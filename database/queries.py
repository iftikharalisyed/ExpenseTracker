from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": dt.strftime("%B %Y"),
    }


def get_summary_stats(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT SUM(amount) AS total, COUNT(*) AS cnt FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    total = row["total"] or 0
    count = row["cnt"] or 0

    top_row = conn.execute(
        "SELECT category FROM expenses WHERE user_id = ? "
        "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()

    return {
        "total_spent": total,
        "transaction_count": count,
        "top_category": top_row["category"] if top_row else "—",
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount "
        "FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category AS name, SUM(amount) AS amount "
        "FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    if not rows:
        return []

    result = [{"name": r["name"], "amount": r["amount"]} for r in rows]
    total = sum(r["amount"] for r in result)
    for r in result:
        r["pct"] = round(r["amount"] / total * 100)
    remainder = 100 - sum(r["pct"] for r in result)
    result[0]["pct"] += remainder
    return result

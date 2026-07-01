from database.queries import (get_category_breakdown, get_recent_transactions,
                               get_summary_stats, get_user_by_id)


def test_get_user_by_id_valid(seed_user_id):
    user = get_user_by_id(seed_user_id)
    assert user is not None
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert "member_since" in user
    assert user["member_since"] != ""


def test_get_user_by_id_nonexistent():
    assert get_user_by_id(999999) is None


def test_get_summary_stats_with_expenses(seed_user_id):
    stats = get_summary_stats(seed_user_id)
    assert abs(stats["total_spent"] - 346.24) < 0.01
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(empty_user_id):
    stats = get_summary_stats(empty_user_id)
    assert stats["total_spent"] == 0
    assert stats["transaction_count"] == 0
    assert stats["top_category"] == "—"


def test_get_recent_transactions_with_expenses(seed_user_id):
    txs = get_recent_transactions(seed_user_id)
    assert len(txs) == 8
    assert txs[0]["date"] == "2026-06-22"
    for tx in txs:
        assert "date" in tx
        assert "description" in tx
        assert "category" in tx
        assert "amount" in tx


def test_get_recent_transactions_no_expenses(empty_user_id):
    assert get_recent_transactions(empty_user_id) == []


def test_get_category_breakdown_with_expenses(seed_user_id):
    cats = get_category_breakdown(seed_user_id)
    assert len(cats) == 7
    assert cats[0]["name"] == "Bills"
    assert all(isinstance(c["pct"], int) for c in cats)
    assert sum(c["pct"] for c in cats) == 100


def test_get_category_breakdown_no_expenses(empty_user_id):
    assert get_category_breakdown(empty_user_id) == []


def test_profile_unauthenticated(client):
    r = client.get("/profile")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_profile_authenticated_seed_user(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
    r = client.get("/profile")
    assert r.status_code == 200
    body = r.data.decode()
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "346.24" in body
    assert "Bills" in body

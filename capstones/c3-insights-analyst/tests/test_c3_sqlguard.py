import pytest

PACKAGE = "insights"


@pytest.mark.parametrize("sql", [
    "DELETE FROM transactions",
    "SELECT 1; DROP TABLE transactions",
    "UPDATE transactions SET amount_usd = 0",
    "SELECT * FROM pragma_table_info('accounts')",
    "SELECT name FROM sqlite_master",
    "SELECT * FROM transactions t JOIN salaries s ON 1=1",
    "SELECT * FROM accounts, salaries",
    "SELECT a.account_id FROM accounts a, salaries s WHERE 1=1",
    "ATTACH DATABASE 'x.db' AS x",
    "explain select 1",
    'SELECT * FROM "salaries"',                 # SQLite runs every quoted form below; the guard must not
    "SELECT * FROM `salaries`",
    "SELECT * FROM [salaries]",
    "SELECT * FROM 'salaries'",
    'SELECT * FROM"salaries"',
    'SELECT name FROM "sqlite_master"',
    "SELECT * FROM accounts, 'salaries'",
    'SELECT * FROM accounts a JOIN "salaries" s ON 1=1',
])
def test_blocks(cap, sql):
    with pytest.raises(cap.UnsafeSQL):
        cap.guard_sql(sql)


def test_allows_and_limits(cap):
    out = cap.guard_sql("SELECT * FROM transactions;")
    assert out.endswith("LIMIT 1000") and ";" not in out
    assert cap.guard_sql("select * from accounts limit 5").endswith("limit 5")
    assert cap.guard_sql("SELECT * FROM accounts LIMIT 50000").endswith("LIMIT 1000")
    cte = "WITH chen AS (SELECT account_id FROM accounts) SELECT * FROM monthly_spend WHERE account_id IN (SELECT account_id FROM chen)"
    assert cap.guard_sql(cte).startswith("WITH chen")
    quoted_text = "SELECT * FROM accounts WHERE customer_name = 'say \"hi\" [x]'"   # quotes inside a literal are data
    assert cap.guard_sql(quoted_text).startswith(quoted_text)


def test_comments_cannot_smuggle(cap):
    assert cap.guard_sql("SELECT 1 FROM accounts -- ; DROP TABLE accounts").startswith("SELECT 1 FROM accounts")
    with pytest.raises(cap.UnsafeSQL):
        cap.guard_sql("SELECT 1 /* harmless */ ; DELETE FROM accounts")


def test_error_messages_are_actionable(cap):
    with pytest.raises(cap.UnsafeSQL) as e:
        cap.guard_sql("SELECT * FROM salaries")
    assert "salaries" in str(e.value) and "transactions" in str(e.value)

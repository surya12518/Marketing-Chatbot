import sqlite3

def create_db():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    # Drop tables if exist
    cursor.execute("DROP TABLE IF EXISTS campaigns")
    cursor.execute("DROP TABLE IF EXISTS transactions")

    # Campaigns table
    cursor.execute("""
    CREATE TABLE campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        budget REAL,
        spend REAL,
        revenue REAL,
        start_date TEXT,
        end_date TEXT
    )
    """)

    # Transactions table
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        customer_name TEXT,
        amount REAL,
        date TEXT,
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
    )
    """)

    # Insert campaigns
    campaigns = [
        ("Facebook Ads", 10000, 8000, 15000, "2024-01-01", "2024-06-30"),
        ("Google Ads", 20000, 15000, 25000, "2024-02-01", "2024-07-31"),
        ("LinkedIn Ads", 15000, 12000, 17000, "2024-03-01", "2024-08-31"),
    ]
    cursor.executemany("INSERT INTO campaigns (name, budget, spend, revenue, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)", campaigns)

    # Insert transactions
    transactions = [
        (1, "Alice", 200, "2024-03-10"),
        (1, "Bob", 350, "2024-04-15"),
        (2, "Charlie", 500, "2024-05-05"),
        (3, "David", 700, "2024-06-20"),
    ]
    cursor.executemany("INSERT INTO transactions (campaign_id, customer_name, amount, date) VALUES (?, ?, ?, ?)", transactions)

    conn.commit()
    conn.close()
    print("✅ portfolio.db created with sample data")

if __name__ == "__main__":
    create_db()

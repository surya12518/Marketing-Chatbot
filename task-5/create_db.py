# create_db.py
import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
DB_PATH = "portfolio.db"

def create_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS leads;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS campaigns;

    CREATE TABLE campaigns (
        id INTEGER PRIMARY KEY,
        client TEXT,
        name TEXT,
        start_date TEXT,
        end_date TEXT,
        spend REAL,
        channel TEXT,
        conversions INTEGER,
        roi REAL
    );

    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        region TEXT,
        loyalty_score REAL,
        churn_risk INTEGER
    );

    CREATE TABLE leads (
        id INTEGER PRIMARY KEY,
        campaign_id INTEGER,
        status TEXT,
        conversion_probability REAL,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
    );
    """)
    conn.commit()

def seed_data(conn):
    cur = conn.cursor()
    channels = ['email', 'social', 'search', 'display', 'affiliate']
    regions = ['North', 'South', 'East', 'West', 'Urban', 'Rural']

    campaign_ids = []
    for i in range(1, 21):
        client = fake.company()
        name = f"{client.split()[0]} Campaign {i}"
        start = fake.date_between(start_date='-1y', end_date='today')
        end = start + timedelta(days=random.randint(10, 90))
        spend = round(random.uniform(5000, 200000), 2)
        channel = random.choice(channels)
        conversions = random.randint(10, 5000)
        roi = round(random.uniform(0.5, 8.0), 2)
        cur.execute(
            "INSERT INTO campaigns (client,name,start_date,end_date,spend,channel,conversions,roi) VALUES (?,?,?,?,?,?,?,?)",
            (client, name, start.isoformat(), end.isoformat(), spend, channel, conversions, roi)
        )
        campaign_ids.append(cur.lastrowid)

    for i in range(1, 61):
        name = fake.name()
        age = random.randint(18, 70)
        region = random.choice(regions)
        loyalty_score = round(random.uniform(0, 100), 2)
        churn_risk = random.randint(0, 100)
        cur.execute(
            "INSERT INTO customers (name,age,region,loyalty_score,churn_risk) VALUES (?,?,?,?,?)",
            (name, age, region, loyalty_score, churn_risk)
        )

    statuses = ['open', 'contacted', 'converted', 'lost']
    for i in range(1, 101):
        campaign_id = random.choice(campaign_ids)
        status = random.choice(statuses)
        conversion_probability = round(random.uniform(0, 1), 3)
        cur.execute(
            "INSERT INTO leads (campaign_id,status,conversion_probability) VALUES (?,?,?)",
            (campaign_id, status, conversion_probability)
        )
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    seed_data(conn)
    conn.close()
    print(f"Created {DB_PATH} with sample data")

if __name__ == "__main__":
    main()

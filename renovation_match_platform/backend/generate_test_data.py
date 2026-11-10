"""Generate a large, realistic test dataset for system testing and the live demo.

Creates a SEPARATE database file (demo_data.db) so the team's renovation_match.db is not touched.

Run from the backend folder:
    py generate_test_data.py
Run the app on the generated data (PowerShell):
    $env:RENOVATION_DB = "demo_data.db"; py -m app.main
"""
import random
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.services.database import db
from app.controller.create_user_account_controller import CreateUserAccountController

SEED = 314                      # fixed seed: every run produces the same data
DAYS_SINCE_LAUNCH = 90          # activity is spread over the last 90 days
PASSWORD = "Test1234!"          # every generated account uses this password
EMAIL_DOMAIN = "testdata.example.com"
ROLE_COUNTS = {"USER_ADMIN": 5, "INTERIOR_DESIGNER": 30, "CUSTOMER": 80, "PLATFORM_MANAGER": 5}
SUSPENDED = 6
FAVOURITES = 200
VIEWS = 600

FIRST_NAMES = ["Mei", "Arjun", "Siti", "Wei Jie", "Priya", "Daniel", "Aisyah", "Ryan", "Hui Min", "Kumar",
               "Nurul", "Marcus", "Jia Hui", "Farhan", "Chloe", "Ravi", "Shu Fen", "Iskandar", "Grace", "Zhi Hao"]
LAST_NAMES = ["Tan", "Lim", "Kumar", "Ng", "Wong", "Rahman", "Lee", "Chua", "Singh", "Goh",
              "Ong", "Ismail", "Teo", "Pillai", "Koh"]
LOCATIONS = ["Tampines", "Jurong West", "Woodlands", "Bishan", "Punggol", "Clementi", "Bedok", "Toa Payoh"]


def stamp(moment):
    return moment.isoformat(timespec="seconds")


def random_between(start, end):
    return start + timedelta(seconds=random.randint(0, max(0, int((end - start).total_seconds()))))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "demo_data.db"
    random.seed(SEED)
    now = datetime.now().replace(microsecond=0)
    launch = now - timedelta(days=DAYS_SINCE_LAUNCH)

    db.configure(str(out))
    db.init()                   # tables + the team's demo seed (4 users, 100 companies, categories, IDPs)
    conn = sqlite3.connect(out)
    if conn.execute("SELECT 1 FROM users WHERE email LIKE ?", (f"%@{EMAIL_DOMAIN}",)).fetchone():
        print(f"{out.name} already has generated data. Delete it to generate again.")
        return

    # 1. The platform "launched" 90 days ago: base records start then, IDPs are added over time.
    conn.execute("UPDATE users SET created_at=?", (stamp(launch),))
    conn.execute("UPDATE companies SET created_at=?, updated_at=?", (stamp(launch), stamp(launch)))
    conn.execute("UPDATE categories SET created_at=?", (stamp(launch),))
    project_created = {}
    for (project_id,) in conn.execute("SELECT id FROM projects").fetchall():
        created = random_between(launch, now - timedelta(days=1))
        project_created[project_id] = created
        conn.execute("UPDATE projects SET created_at=?, updated_at=?, views=0 WHERE id=?",
                     (stamp(created), stamp(created), project_id))
    conn.commit()

    # 2. User accounts, created through the real controller (hashed password + profile), then backdated.
    admin_id = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()[0]
    customers = {conn.execute("SELECT id FROM users WHERE username='customer'").fetchone()[0]: launch}
    generated = []
    used = set()
    controller = CreateUserAccountController()
    print("Creating user accounts...")
    for role, count in ROLE_COUNTS.items():
        for _ in range(count):
            while True:
                first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
                username = f"{first}.{last}{random.randint(1, 99)}".lower().replace(" ", "")
                if username not in used:
                    used.add(username)
                    break
            ok, user_id = controller.create_user_account(admin_id, {
                "username": username,
                "email": f"{username}@{EMAIL_DOMAIN}",
                "password": PASSWORD,
                "role": role,
                "full_name": f"{first} {last}",
            })
            if not ok:
                raise RuntimeError(user_id)
            generated.append((user_id, role, username))

    for user_id, role, _ in generated:
        created = random_between(launch, now)
        conn.execute("UPDATE users SET created_at=? WHERE id=?", (stamp(created), user_id))
        conn.execute("UPDATE activity_events SET occurred_at=? WHERE event_type='USER_CREATED' AND entity_id=?",
                     (stamp(created), user_id))
        conn.execute("UPDATE profiles SET phone=?, location=?, bio=?, updated_at=? WHERE user_id=?",
                     (f"9{random.randint(1000000, 9999999)}", random.choice(LOCATIONS),
                      f"{role.replace('_', ' ').title()} on the platform.", stamp(created), user_id))
        if role == "CUSTOMER":
            customers[user_id] = created
    for user_id, _, _ in random.sample(generated, SUSPENDED):
        conn.execute("UPDATE users SET status='SUSPENDED' WHERE id=?", (user_id,))
    conn.commit()

    # 3. Favourites: unique customer-IDP pairs, saved after both the customer and the IDP existed.
    pairs = set()
    while len(pairs) < FAVOURITES:
        pairs.add((random.choice(list(customers)), random.choice(list(project_created))))
    for customer_id, project_id in pairs:
        saved = random_between(max(customers[customer_id], project_created[project_id]), now)
        conn.execute("INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)",
                     (customer_id, project_id, stamp(saved)))
        conn.execute("""INSERT INTO activity_events(actor_id,event_type,entity_type,entity_id,occurred_at)
                        VALUES(?,?,?,?,?)""", (customer_id, "PROJECT_SHORTLISTED", "project", project_id, stamp(saved)))

    # 4. Views: one event per view, after the IDP was created; each IDP's view counter matches its events.
    for _ in range(VIEWS):
        project_id = random.choice(list(project_created))
        viewed = random_between(project_created[project_id], now)
        viewers = [cid for cid, joined in customers.items() if joined <= viewed]
        actor = random.choice(viewers) if viewers and random.random() < 0.7 else None
        conn.execute("""INSERT INTO activity_events(actor_id,event_type,entity_type,entity_id,occurred_at)
                        VALUES(?,?,?,?,?)""", (actor, "PROJECT_VIEWED", "project", project_id, stamp(viewed)))
        conn.execute("UPDATE projects SET views=views+1 WHERE id=?", (project_id,))
    conn.commit()

    # 5. Summary for the report.
    def count(sql, params=()):
        return conn.execute(sql, params).fetchone()[0]

    rows = [("User accounts", count("SELECT COUNT(*) FROM users"))]
    for role in ROLE_COUNTS:
        rows.append(("  " + role, count("SELECT COUNT(*) FROM users WHERE role=?", (role,))))
    rows += [
        ("  (suspended)", count("SELECT COUNT(*) FROM users WHERE status='SUSPENDED'")),
        ("Profiles", count("SELECT COUNT(*) FROM profiles")),
        ("Companies", count("SELECT COUNT(*) FROM companies")),
        ("Categories", count("SELECT COUNT(*) FROM categories")),
        ("IDPs (projects)", count("SELECT COUNT(*) FROM projects")),
        ("Favourites", count("SELECT COUNT(*) FROM favourites")),
        ("View events", count("SELECT COUNT(*) FROM activity_events WHERE event_type='PROJECT_VIEWED'")),
        ("All activity events", count("SELECT COUNT(*) FROM activity_events")),
    ]
    print(f"\nTest data generated in {out.name} (seed {SEED}, activity over the last {DAYS_SINCE_LAUNCH} days)")
    for label, value in rows:
        print(f"  {label:<24}{value:>6}")
    print(f"\nDemo logins (password {PASSWORD}):")
    for role in ROLE_COUNTS:
        username = conn.execute("""SELECT username FROM users WHERE role=? AND status='ACTIVE' AND email LIKE ?
                                   ORDER BY id LIMIT 1""", (role, f"%@{EMAIL_DOMAIN}")).fetchone()[0]
        print(f"  {role:<20}{username}")
    conn.close()


if __name__ == "__main__":
    main()
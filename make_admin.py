
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "portal.db"

email = "sanikabirharunskh@gmail.com"

with sqlite3.connect(DB_PATH) as con:
    cur = con.execute(
        "UPDATE users SET is_admin = 1 WHERE email = ?",
        (email,)
    )
    con.commit()

    if cur.rowcount:
        print("Success! Your account is now an Admin.")
    else:
        print("Account not found. Check the registered email.")

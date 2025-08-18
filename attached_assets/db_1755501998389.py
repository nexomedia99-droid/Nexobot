import sqlite3

DB_FILE = "database.db"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        # Table member/user
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            whatsapp TEXT,
            telegram TEXT,
            payment_method TEXT,
            payment_number TEXT,
            owner_name TEXT,
            referrer TEXT,
            points INTEGER DEFAULT 0
        )
        """)
        # Table job
        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            fee TEXT,
            desc TEXT,
            status TEXT
        )
        """)
        # Table applicants
        cur.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            job_id INTEGER,
            user_id TEXT,
            PRIMARY KEY (job_id, user_id)
        )
        """)
        conn.commit()
        # Table achievements (badge system)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            badge_name TEXT,
            awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


# ==== USER FUNGSI ====
def add_user(user_id, data):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO users (user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            data['username'],
            data['whatsapp'],
            data['telegram'],
            data['payment_method'],
            data['payment_number'],
            data['owner_name'],
            data.get('referrer', None),  # Allow referrer to be optional
            data.get('points', 0)      # Default points to 0
        ))
        conn.commit()

def get_user_by_id(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            keys = ["user_id", "username", "whatsapp", "telegram", "payment_method", "payment_number", "owner_name", "referrer", "points"]
            return dict(zip(keys, row))
        return None

def get_user_by_username(username):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            keys = ["user_id", "username", "whatsapp", "telegram", "payment_method", "payment_number", "owner_name", "referrer", "points"]
            return dict(zip(keys, row))
        return None

def get_all_users():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points FROM users")
        rows = cur.fetchall()
        keys = ["user_id", "username", "whatsapp", "telegram", "payment_method", "payment_number", "owner_name", "referrer", "points"]
        return [dict(zip(keys, row)) for row in rows]

def get_users_by_referrer(referrer_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points FROM users WHERE referrer = ?", (referrer_id,))
        rows = cur.fetchall()
        keys = ["user_id", "username", "whatsapp", "telegram", "payment_method", "payment_number", "owner_name", "referrer", "points"]
        return [dict(zip(keys, row)) for row in rows]

def add_points_to_user(user_id, points_to_add):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points_to_add, user_id))
        conn.commit()

def get_referrals_by_username(referrer_username):
    """Get all users who were referred by a specific username"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, whatsapp, telegram, payment_method, payment_number, owner_name, referrer, points FROM users WHERE referrer = ?", (referrer_username,))
        rows = cur.fetchall()
        keys = ["user_id", "username", "whatsapp", "telegram", "payment_method", "payment_number", "owner_name", "referrer", "points"]
        return [dict(zip(keys, row)) for row in rows]

# ==== JOB FUNGSI ====
def add_job(title, fee, desc, status="aktif"):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jobs (title, fee, desc, status) VALUES (?, ?, ?, ?)
        """, (title, fee, desc, status))
        conn.commit()
        return cur.lastrowid

def get_job_by_id(job_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, fee, desc, status FROM jobs WHERE id = ?", (job_id,))
        row = cur.fetchone()
        if row:
            keys = ["id", "title", "fee", "desc", "status"]
            return dict(zip(keys, row))
        return None

def get_all_jobs():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, fee, desc, status FROM jobs")
        rows = cur.fetchall()
        keys = ["id", "title", "fee", "desc", "status"]
        return [dict(zip(keys, row)) for row in rows]

# ==== APPLICANTS ====
def add_applicant(job_id, user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO applicants (job_id, user_id) VALUES (?, ?)", (job_id, user_id))
        conn.commit()

def get_applicants_by_job(job_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM applicants WHERE job_id = ?", (job_id,))
        return [row[0] for row in cur.fetchall()]

def delete_user_by_id(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        # Delete user applications first (foreign key constraint)
        cur.execute("DELETE FROM applicants WHERE user_id = ?", (user_id,))
        # Delete user from users table
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()


# ==========================================
# FUNGSI UNTUK BADGE / ACHIEVEMENTS
# ==========================================

def get_total_applies(user_id: str) -> int:
    """Hitung total job yang pernah di-apply oleh user."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM applicants WHERE user_id = ?", (user_id,))
        return cur.fetchone()[0]


def has_badge(user_id: str, badge_name: str) -> bool:
    """Cek apakah user sudah punya badge tertentu."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM achievements WHERE user_id = ? AND badge_name = ?", (user_id, badge_name))
        return cur.fetchone() is not None


def add_badge_to_user(user_id: str, badge_name: str):
    """Tambah badge ke user kalau belum ada."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM achievements WHERE user_id = ? AND badge_name = ?", (user_id, badge_name))
        if not cur.fetchone():  # hanya tambah kalau belum ada
            cur.execute("INSERT INTO achievements (user_id, badge_name, created_at) VALUES (?, ?, datetime('now'))",
                        (user_id, badge_name))
            conn.commit()


def get_badges(user_id: str):
    """Ambil semua badge user."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT badge_name FROM achievements WHERE user_id = ?", (user_id,))
        return [row[0] for row in cur.fetchall()]



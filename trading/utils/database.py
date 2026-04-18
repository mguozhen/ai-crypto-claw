"""
SQLite database — multi-tenant: users, accounts, trades, configs, command logs.
"""
import sqlite3
import os
import json
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _has_column(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def init_db():
    conn = _conn()
    c = conn.cursor()

    # === Users ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            password_hash TEXT,
            telegram_bot_token_enc TEXT,
            telegram_chat_id TEXT,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === User configs (per-user strategy) ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            config_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # === Accounts (OKX API keys) ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            api_key_enc TEXT NOT NULL,
            secret_enc TEXT NOT NULL,
            passphrase_enc TEXT NOT NULL,
            is_main INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            demo_mode INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === Trades ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            symbol TEXT,
            side TEXT,
            amount REAL,
            price REAL,
            cost REAL,
            status TEXT,
            strategy TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === Grid orders ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS grid_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            symbol TEXT,
            side TEXT,
            grid_level INTEGER,
            price REAL,
            amount REAL,
            status TEXT,
            paired_order_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filled_at TIMESTAMP
        )
    """)

    # === DCA history ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS dca_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            amount_usdt REAL,
            amount_crypto REAL,
            price REAL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === Daily PnL ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_pnl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            starting_balance REAL,
            ending_balance REAL,
            pnl_usdt REAL,
            pnl_pct REAL,
            trade_count INTEGER
        )
    """)

    # === Command logs ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            username TEXT,
            user_id INTEGER,
            command TEXT,
            args TEXT,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === Migrations ===
    for table in ["trades", "grid_orders", "dca_history", "daily_pnl"]:
        if not _has_column(c, table, "account_id"):
            c.execute(f"ALTER TABLE {table} ADD COLUMN account_id INTEGER DEFAULT 1")

    if not _has_column(c, "accounts", "user_id"):
        c.execute("ALTER TABLE accounts ADD COLUMN user_id INTEGER")

    if not _has_column(c, "command_logs", "user_id"):
        c.execute("ALTER TABLE command_logs ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()


# ==================== Users ====================

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_user(username, password, display_name="", bot_token_enc="", is_admin=0):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (username, display_name, password_hash, telegram_bot_token_enc, is_admin)
        VALUES (?, ?, ?, ?, ?)
    """, (username, display_name, _hash_password(password), bot_token_enc, is_admin))
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return uid


def authenticate_user(username, password):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    row = c.fetchone()
    conn.close()
    if row and _check_password(password, row["password_hash"]):
        return dict(row)
    return None


def get_user_by_id(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_active_users():
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY is_admin DESC, id")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_chat_id(user_id, chat_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("UPDATE users SET telegram_chat_id = ? WHERE id = ?", (str(chat_id), user_id))
    conn.commit()
    conn.close()


def deactivate_user(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def ensure_admin_user(username="admin", password="admin123"):
    """Create default admin if none exists."""
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE is_admin = 1")
    if not c.fetchone():
        conn.close()
        return create_user(username, password, "Administrator", "", is_admin=1)
    conn.close()
    return None


# ==================== User Configs ====================

def save_user_config(user_id, config_dict):
    conn = _conn()
    c = conn.cursor()
    config_json = json.dumps(config_dict)
    c.execute("""
        INSERT INTO user_configs (user_id, config_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET config_json = ?, updated_at = ?
    """, (user_id, config_json, datetime.now().isoformat(),
          config_json, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_user_config(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT config_json FROM user_configs WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row["config_json"])
    return None


# ==================== Accounts ====================

def add_account(name, api_key_enc, secret_enc, passphrase_enc, demo_mode=0, user_id=None):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO accounts (name, api_key_enc, secret_enc, passphrase_enc, demo_mode, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, api_key_enc, secret_enc, passphrase_enc, demo_mode, user_id))
    account_id = c.lastrowid
    conn.commit()
    conn.close()
    return account_id


def register_main_account(api_key_enc, secret_enc, passphrase_enc, demo_mode=0):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT id FROM accounts WHERE is_main = 1")
    row = c.fetchone()
    if row:
        c.execute("UPDATE accounts SET api_key_enc=?, secret_enc=?, passphrase_enc=?, demo_mode=? WHERE is_main = 1",
                  (api_key_enc, secret_enc, passphrase_enc, demo_mode))
        account_id = row["id"]
    else:
        c.execute("""
            INSERT INTO accounts (name, api_key_enc, secret_enc, passphrase_enc, is_main, demo_mode)
            VALUES ('Main', ?, ?, ?, 1, ?)
        """, (api_key_enc, secret_enc, passphrase_enc, demo_mode))
        account_id = c.lastrowid
    conn.commit()
    conn.close()
    return account_id


def get_account(account_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_active_accounts():
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE is_active = 1 ORDER BY is_main DESC, id")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_accounts_for_user(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE user_id = ? AND is_active = 1", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_account(account_id):
    conn = _conn()
    c = conn.cursor()
    c.execute("UPDATE accounts SET is_active = 0 WHERE id = ? AND is_main = 0", (account_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ==================== Trade Logging ====================

def log_trade(order_id, symbol, side, amount, price, cost, status, strategy, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO trades (order_id, symbol, side, amount, price, cost, status, strategy, account_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_id, symbol, side, amount, price, cost, status, strategy, account_id))
    conn.commit()
    conn.close()


def log_grid_order(order_id, symbol, side, grid_level, price, amount, status, paired_id=None, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO grid_orders
        (order_id, symbol, side, grid_level, price, amount, status, paired_order_id, account_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_id, symbol, side, grid_level, price, amount, status, paired_id, account_id))
    conn.commit()
    conn.close()


def update_grid_order_status(order_id, status):
    conn = _conn()
    c = conn.cursor()
    filled_at = datetime.now().isoformat() if status == "filled" else None
    c.execute("UPDATE grid_orders SET status = ?, filled_at = ? WHERE order_id = ?",
              (status, filled_at, order_id))
    conn.commit()
    conn.close()


def get_active_grid_orders(symbol, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        SELECT order_id, side, grid_level, price, amount
        FROM grid_orders
        WHERE symbol = ? AND account_id = ? AND status IN ('open', 'partially_filled')
    """, (symbol, account_id))
    rows = c.fetchall()
    conn.close()
    return [(r[0], r[1], r[2], r[3], r[4]) for r in rows]


def log_dca(symbol, amount_usdt, amount_crypto, price, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("INSERT INTO dca_history (symbol, amount_usdt, amount_crypto, price, account_id) VALUES (?, ?, ?, ?, ?)",
              (symbol, amount_usdt, amount_crypto, price, account_id))
    conn.commit()
    conn.close()


def get_last_dca_time(symbol, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT executed_at FROM dca_history WHERE symbol = ? AND account_id = ? ORDER BY executed_at DESC LIMIT 1",
              (symbol, account_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_last_dca_price(symbol, account_id=1):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT price FROM dca_history WHERE symbol = ? AND account_id = ? ORDER BY executed_at DESC LIMIT 1",
              (symbol, account_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_stats(account_id=None):
    conn = _conn()
    c = conn.cursor()
    if account_id:
        c.execute("SELECT COUNT(*) FROM trades WHERE status = 'filled' AND account_id = ?", (account_id,))
        total_trades = c.fetchone()[0]
        c.execute("SELECT SUM(amount_usdt) FROM dca_history WHERE account_id = ?", (account_id,))
        dca_total = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM grid_orders WHERE status = 'filled' AND account_id = ?", (account_id,))
        grid_fills = c.fetchone()[0]
    else:
        c.execute("SELECT COUNT(*) FROM trades WHERE status = 'filled'")
        total_trades = c.fetchone()[0]
        c.execute("SELECT SUM(amount_usdt) FROM dca_history")
        dca_total = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM grid_orders WHERE status = 'filled'")
        grid_fills = c.fetchone()[0]
    conn.close()
    return {"total_trades": total_trades, "dca_total_usdt": dca_total, "grid_fills": grid_fills}


def get_trades(account_id=None, limit=50):
    conn = _conn()
    c = conn.cursor()
    if account_id:
        c.execute("SELECT * FROM trades WHERE account_id = ? ORDER BY created_at DESC LIMIT ?", (account_id, limit))
    else:
        c.execute("SELECT * FROM trades ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==================== Command Logs ====================

def log_command(chat_id, username, command, args="", result="", user_id=None):
    conn = _conn()
    c = conn.cursor()
    c.execute("INSERT INTO command_logs (chat_id, username, user_id, command, args, result) VALUES (?, ?, ?, ?, ?, ?)",
              (str(chat_id), username, user_id, command, args, result))
    conn.commit()
    conn.close()


def get_command_logs(limit=100, user_id=None):
    conn = _conn()
    c = conn.cursor()
    if user_id:
        c.execute("SELECT * FROM command_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    else:
        c.execute("SELECT * FROM command_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

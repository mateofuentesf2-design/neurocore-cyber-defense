import os
import sqlite3
import psycopg2
import psycopg2.pool
from contextlib import contextmanager
from typing import Any, List, Dict, Optional, Tuple
from datetime import datetime

_connection_pool = None
_sqlite_pool = []
DB_TYPE = None

def detect_db_type() -> str:
    global DB_TYPE
    if DB_TYPE:
        return DB_TYPE
    
    if os.getenv("POSTGRES_HOST"):
        DB_TYPE = "postgresql"
    elif os.getenv("USE_POSTGRESQL", "").lower() == "true":
        DB_TYPE = "postgresql"
    else:
        DB_TYPE = "sqlite"
    return DB_TYPE

def get_connection():
    db_type = detect_db_type()
    
    if db_type == "postgresql":
        return get_postgres_connection()
    else:
        return get_sqlite_connection()

def get_postgres_connection():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DB", "neurocore"),
                user=os.getenv("POSTGRES_USER", "neurocore"),
                password=os.getenv("POSTGRES_PASSWORD", "neurocore")
            )
        except psycopg2.OperationalError as e:
            print(f"⚠️ PostgreSQL not available: {e}")
            print("📦 Falling back to SQLite...")
            global DB_TYPE
            DB_TYPE = "sqlite"
            return get_sqlite_connection()
    
    try:
        conn = _connection_pool.getconn()
        if conn.closed:
            _connection_pool.putconn(conn)
            return get_postgres_connection()
        return conn
    except:
        return get_sqlite_connection()

def get_sqlite_connection():
    return sqlite3.connect(
        "neurocore.db",
        check_same_thread=False,
        timeout=30.0
    )

def normalize_query(query: str) -> str:
    db_type = detect_db_type()
    if db_type == "sqlite":
        return query.replace("%s", "?")
    return query

def execute(query: str, params: tuple = None, fetch: bool = True, commit: bool = True) -> Optional[List]:
    query = normalize_query(query)
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
        if fetch:
            return cursor.fetchall()
        return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if detect_db_type() == "postgresql":
            try:
                _connection_pool.putconn(conn)
            except:
                pass
        else:
            try:
                conn.close()
            except:
                pass

def execute_one(query: str, params: tuple = None) -> Optional[Tuple]:
    query = normalize_query(query)
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if detect_db_type() == "postgresql":
            try:
                _connection_pool.putconn(conn)
            except:
                pass
        else:
            try:
                conn.close()
            except:
                pass

def execute_many(query: str, params_list: List[tuple]):
    query = normalize_query(query)
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.executemany(query, params_list)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if detect_db_type() == "postgresql":
            try:
                _connection_pool.putconn(conn)
            except:
                pass
        else:
            try:
                conn.close()
            except:
                pass

@contextmanager
def get_cursor():
    db_type = detect_db_type()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if db_type == "postgresql":
            try:
                _connection_pool.putconn(conn)
            except:
                pass
        else:
            try:
                conn.close()
            except:
                pass

def init_db():
    db_type = detect_db_type()
    conn = get_connection()
    cursor = conn.cursor()
    
    if db_type == "sqlite":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                tenant_id TEXT,
                role_id INTEGER DEFAULT 1,
                email TEXT,
                full_name TEXT,
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                raw TEXT NOT NULL,
                tenant_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                alert TEXT,
                severity TEXT DEFAULT 'info',
                processed INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_text TEXT UNIQUE NOT NULL,
                tenant_id TEXT NOT NULL,
                name TEXT,
                is_active INTEGER DEFAULT 1,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                tenant_id TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                ip TEXT,
                blocked INTEGER DEFAULT 0,
                responded INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                tenant_id TEXT,
                reason TEXT,
                blocked_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                features TEXT NOT NULL,
                label INTEGER NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                tenant_id TEXT,
                action TEXT,
                resource TEXT,
                details TEXT,
                ip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_tenant ON events(tenant_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_tenant ON alerts(tenant_id)
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                tenant_id TEXT,
                role_id INTEGER DEFAULT 1,
                email TEXT,
                full_name TEXT,
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                raw TEXT NOT NULL,
                tenant_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                alert TEXT,
                severity TEXT DEFAULT 'info',
                processed INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key_text TEXT UNIQUE NOT NULL,
                tenant_id TEXT NOT NULL,
                name TEXT,
                is_active INTEGER DEFAULT 1,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                event_id INTEGER,
                tenant_id TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                ip TEXT,
                blocked INTEGER DEFAULT 0,
                responded INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id SERIAL PRIMARY KEY,
                ip TEXT NOT NULL,
                tenant_id TEXT,
                reason TEXT,
                blocked_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_training_data (
                id SERIAL PRIMARY KEY,
                features TEXT NOT NULL,
                label INTEGER NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                tenant_id TEXT,
                action TEXT,
                resource TEXT,
                details TEXT,
                ip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_tenant ON events(tenant_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_tenant ON alerts(tenant_id)
        """)

    conn.commit()
    cursor.close()
    if db_type == "postgresql":
        try:
            _connection_pool.putconn(conn)
        except:
            pass
    else:
        conn.close()

def close_all():
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
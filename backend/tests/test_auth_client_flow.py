import os
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("TEST_DB_PATH", str(ROOT / "backend" / "tests" / "test_cirujano.db")))

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["JWT_REFRESH_SECRET"] = "test-refresh-secret"
os.environ["SKIP_MIGRATIONS"] = "1"

from fastapi.testclient import TestClient
import sqlite3

from app.main import app


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _ensure_min_schema():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            permissions TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            hashed_password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            avatar_url TEXT,
            role_id INTEGER NOT NULL DEFAULT 3,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires DATETIME,
            created_at DATETIME,
            updated_at DATETIME,
            last_login DATETIME,
            FOREIGN KEY(role_id) REFERENCES user_roles(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            phone_alt TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            country TEXT,
            preferred_contact TEXT,
            notes TEXT,
            total_repairs INTEGER DEFAULT 0,
            total_spent FLOAT DEFAULT 0,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            device_type_id INTEGER NOT NULL,
            brand_id INTEGER,
            brand_other TEXT,
            model TEXT NOT NULL,
            serial_number TEXT,
            year_manufactured INTEGER,
            description TEXT,
            condition_notes TEXT,
            photos TEXT,
            total_repairs INTEGER DEFAULT 0,
            first_repair_date DATE,
            last_repair_date DATE,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(device_type_id) REFERENCES device_types(id),
            FOREIGN KEY(brand_id) REFERENCES device_brands(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT,
            sort_order INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            device_id INTEGER,
            status TEXT,
            total_cost FLOAT,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repair_number TEXT UNIQUE NOT NULL,
            device_id INTEGER NOT NULL,
            quote_id INTEGER,
            status_id INTEGER NOT NULL DEFAULT 1,
            assigned_to INTEGER,
            intake_date DATETIME,
            diagnosis_date DATETIME,
            approval_date DATETIME,
            start_date DATETIME,
            completion_date DATETIME,
            delivery_date DATETIME,
            problem_reported TEXT NOT NULL,
            diagnosis TEXT,
            work_performed TEXT,
            parts_cost FLOAT DEFAULT 0,
            labor_cost FLOAT DEFAULT 0,
            additional_cost FLOAT DEFAULT 0,
            discount FLOAT DEFAULT 0,
            total_cost FLOAT DEFAULT 0,
            payment_status TEXT,
            payment_method TEXT,
            paid_amount FLOAT DEFAULT 0,
            warranty_days INTEGER DEFAULT 90,
            warranty_until DATE,
            priority INTEGER DEFAULT 2,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(device_id) REFERENCES devices(id),
            FOREIGN KEY(quote_id) REFERENCES quotes(id),
            FOREIGN KEY(status_id) REFERENCES repair_statuses(id),
            FOREIGN KEY(assigned_to) REFERENCES users(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id INTEGER,
            ip_address TEXT,
            details TEXT,
            message TEXT,
            created_at DATETIME
        )
    """)
    cur.execute("INSERT OR IGNORE INTO user_roles (id, name) VALUES (1, 'admin')")
    cur.execute("INSERT OR IGNORE INTO user_roles (id, name) VALUES (2, 'technician')")
    cur.execute("INSERT OR IGNORE INTO user_roles (id, name) VALUES (3, 'client')")
    cur.execute("INSERT OR IGNORE INTO repair_statuses (id, code, name) VALUES (1, 'pending_quote', 'Pendiente Cotizacion')")
    conn.commit()
    conn.close()


def test_auth_and_client_flow():
    _ensure_min_schema()
    with TestClient(app) as client:
        # Register
        unique = uuid.uuid4().hex[:8]
        email = f"testuser_{unique}@example.com"
        username = f"testuser_{unique}"
        register_payload = {
            "email": email,
            "username": username,
            "full_name": "Test User",
            "password": "testpass123",
            "phone": "+56911111111"
        }
        register = client.post("/api/v1/auth/register", json=register_payload)
        assert register.status_code == 201, register.text

        # Login
        login = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "testpass123"
        })
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        refresh_token = login.json()["refresh_token"]

        # Refresh token
        refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh.status_code == 200, refresh.text
        new_token = refresh.json()["access_token"]
        assert new_token

        # Client dashboard + repairs
        dashboard = client.get("/api/v1/client/dashboard", headers=_auth_headers(token))
        assert dashboard.status_code == 200, dashboard.text

        repairs = client.get("/api/v1/client/repairs", headers=_auth_headers(token))
        assert repairs.status_code == 200, repairs.text

        # Forgot/reset password
        forgot = client.post("/api/v1/auth/forgot-password", json={"email": email})
        assert forgot.status_code == 200, forgot.text
        reset_token = forgot.json().get("reset_token")
        assert reset_token

        reset = client.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": "newpass123"
        })
        assert reset.status_code == 200, reset.text

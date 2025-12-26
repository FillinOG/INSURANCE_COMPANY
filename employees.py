import re
import hashlib
from db.connection import get_connection
from utils.security import verify_password

NAME_RE = re.compile(r'^[А-Яа-яЁё -]+$')
PHONE_RE = re.compile(r'^\+7\d{10}$')
ROLE_RE = re.compile(r'^(admin|employee)$')


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate(login: str, password: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT "ID_сотрудника", "password_hash", "role"
        FROM "Сотрудник"
        WHERE "login" = %s
    """, (login,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    emp_id, password_hash, role = row

    if verify_password(password, password_hash):
        return {"employee_id": emp_id, "role": role}
    return None


def get_employees(current_user):
    conn = get_connection()
    cur = conn.cursor()

    if current_user["role"] == "admin":
        cur.execute("""
            SELECT
                "ID_сотрудника",
                "Фамилия",
                "Имя",
                "Отчество",
                "Номер_телефона",
                "login",
                "role"
            FROM "Сотрудник"
            ORDER BY "ID_сотрудника"
        """)
    else:
        cur.execute("""
            SELECT
                "ID_сотрудника",
                "Фамилия",
                "Имя",
                "Отчество",
                "Номер_телефона",
                "login",
                "role"
            FROM "Сотрудник"
            WHERE "ID_сотрудника" = %s
        """, (current_user["employee_id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def validate_employee(data, require_password=False):
    if not NAME_RE.match(data["Фамилия"]):
        raise ValueError("Некорректная фамилия")

    if not NAME_RE.match(data["Имя"]):
        raise ValueError("Некорректное имя")

    if data["Отчество"] and not NAME_RE.match(data["Отчество"]):
        raise ValueError("Некорректное отчество")

    if not PHONE_RE.match(data["Номер_телефона"]):
        raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")

    if not data["login"]:
        raise ValueError("Логин обязателен")

    if require_password and not data.get("password"):
        raise ValueError("Пароль обязателен")

    if not ROLE_RE.match(data["role"]):
        raise ValueError("Некорректная роль")


def add_employee(data):
    validate_employee(data, require_password=True)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO "Сотрудник"
        ("Фамилия", "Имя", "Отчество",
         "Номер_телефона", "login", "password_hash", "role")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data["Фамилия"],
        data["Имя"],
        data["Отчество"] or None,
        data["Номер_телефона"],
        data["login"],
        hash_password(data["password"]),
        data["role"]
    ))

    conn.commit()
    cur.close()
    conn.close()


def update_employee(emp_id, data):
    validate_employee(data, require_password=False)

    conn = get_connection()
    cur = conn.cursor()

    if data.get("password"):
        cur.execute("""
            UPDATE "Сотрудник"
            SET
                "Фамилия" = %s,
                "Имя" = %s,
                "Отчество" = %s,
                "Номер_телефона" = %s,
                "login" = %s,
                "password_hash" = %s,
                "role" = %s
            WHERE "ID_сотрудника" = %s
        """, (
            data["Фамилия"],
            data["Имя"],
            data["Отчество"] or None,
            data["Номер_телефона"],
            data["login"],
            hash_password(data["password"]),
            data["role"],
            emp_id
        ))
    else:
        cur.execute("""
            UPDATE "Сотрудник"
            SET
                "Фамилия" = %s,
                "Имя" = %s,
                "Отчество" = %s,
                "Номер_телефона" = %s,
                "login" = %s,
                "role" = %s
            WHERE "ID_сотрудника" = %s
        """, (
            data["Фамилия"],
            data["Имя"],
            data["Отчество"] or None,
            data["Номер_телефона"],
            data["login"],
            data["role"],
            emp_id
        ))

    conn.commit()
    cur.close()
    conn.close()


def delete_employee(emp_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM "Сотрудник"
        WHERE "ID_сотрудника" = %s
    """, (emp_id,))

    conn.commit()
    cur.close()
    conn.close()

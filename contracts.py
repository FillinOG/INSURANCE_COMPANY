from datetime import datetime
from db.connection import get_connection


def parse_date(value: str):
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Дата должна быть в формате ДД.ММ.ГГГГ")


def get_all_contracts(current_user):
    conn = get_connection()
    cur = conn.cursor()

    base_sql = """
        SELECT
            d."№_договора",
            c."Фамилия" || ' ' || c."Имя" ||
                COALESCE(' ' || c."Отчество", '') AS client_fio,
            o."Объект_страхования",
            s."Фамилия" || ' ' || s."Имя" ||
                COALESCE(' ' || s."Отчество", '') AS employee_fio,
            d."Стоимость",
            d."Дата_начала",
            d."Дата_окончания"
        FROM "Договор страхования" d
        JOIN "Клиент" c ON d."ID_клиента" = c."ID_клиента"
        JOIN "Сотрудник" s ON d."ID_сотрудника" = s."ID_сотрудника"
        JOIN "Застрахованный объект" o ON d."ID_объекта" = o."ID_объекта"
    """

    if current_user["role"] == "admin":
        cur.execute(base_sql + ' ORDER BY d."№_договора"')
    else:
        cur.execute(
            base_sql + ' WHERE d."ID_сотрудника" = %s ORDER BY d."№_договора"',
            (current_user["employee_id"],)
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_contract(employee_id, client_id, object_id, cost, start_date, end_date):
    if cost <= 0:
        raise ValueError("Стоимость должна быть больше 0")
    if end_date <= start_date:
        raise ValueError("Дата окончания должна быть позже даты начала")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO "Договор страхования"
        ("ID_сотрудника", "ID_клиента", "ID_объекта",
         "Стоимость", "Дата_начала", "Дата_окончания")
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        employee_id,
        client_id,
        object_id,
        cost,
        start_date,
        end_date
    ))

    conn.commit()
    cur.close()
    conn.close()
()

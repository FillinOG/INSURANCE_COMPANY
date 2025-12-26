from db.connection import get_connection


def get_all_clients():
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            "ID_клиента",
            "Фамилия",
            "Имя",
            "Отчество",
            "Серия_паспорта",
            "Номер_паспорта",
            "Номер_телефона"
        FROM "Клиент"
        ORDER BY "ID_клиента"
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def add_client(lastname, firstname, patronymic,
               passport_series, passport_number, phone):
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO "Клиент"
        ("Фамилия", "Имя", "Отчество",
         "Серия_паспорта", "Номер_паспорта", "Номер_телефона")
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (lastname, firstname, patronymic,
         passport_series, passport_number, phone)
    )

    conn.commit()
    conn.close()
    return True

def update_client(
    client_id,
    lastname,
    firstname,
    patronymic,
    series,
    number,
    phone
):
    from db.connection import get_connection

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE "Клиент"
            SET
                "Фамилия" = %s,
                "Имя" = %s,
                "Отчество" = %s,
                "Серия_паспорта" = %s,
                "Номер_паспорта" = %s,
                "Номер_телефона" = %s
            WHERE "ID_клиента" = %s
        """, (
            lastname,
            firstname,
            patronymic,
            series,
            number,
            phone,
            client_id
        ))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("Ошибка обновления клиента:", e)
        return False
    
def delete_client(client_id):
    from db.connection import get_connection

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            'DELETE FROM "Клиент" WHERE "ID_клиента" = %s',
            (client_id,)
        )

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("Ошибка удаления клиента:", e)
        return False

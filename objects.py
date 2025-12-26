from db.connection import get_connection


def get_all_objects():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            o."ID_объекта",
            o."Объект_страхования",
            o."ФИО_страхователя",
            o."№_договора"
        FROM "Застрахованный объект" o
        ORDER BY o."ID_объекта"
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_object(client_id, object_name):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # получаем ФИО клиента
        cur.execute("""
            SELECT "Фамилия", "Имя", "Отчество"
            FROM "Клиент"
            WHERE "ID_клиента" = %s
        """, (client_id,))

        client = cur.fetchone()
        fio = f"{client[0]} {client[1]}" + (f" {client[2]}" if client[2] else "")

        cur.execute("""
            INSERT INTO "Застрахованный объект"
            ("Объект_страхования", "ФИО_страхователя", "№_договора", "ID_клиента")
            VALUES (%s, %s, %s, %s)
        """, (
            object_name,
            fio,
            None,
            client_id
        ))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("Ошибка добавления объекта:", e)
        return False


def update_object(object_id, object_name):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE "Застрахованный объект"
            SET "Объект_страхования" = %s
            WHERE "ID_объекта" = %s
        """, (object_name, object_id))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("Ошибка обновления объекта:", e)
        return False


def delete_object(object_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM "Застрахованный объект"
            WHERE "ID_объекта" = %s
        """, (object_id,))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print("Ошибка удаления объекта:", e)
        return False

import tkinter as tk
from tkinter import ttk, messagebox
import re

from services.clients import get_all_clients, add_client, update_client, delete_client



class ClientsWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.tree = ttk.Treeview(
            self,
            columns=(
                "id", "lastname", "firstname", "patronymic",
                "series", "number", "phone"
            ),
            show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("lastname", text="Фамилия")
        self.tree.heading("firstname", text="Имя")
        self.tree.heading("patronymic", text="Отчество")
        self.tree.heading("series", text="Серия")
        self.tree.heading("number", text="Номер")
        self.tree.heading("phone", text="Телефон")

        self.tree.pack(fill="both", expand=True, pady=10)

        ttk.Button(self, text="Добавить клиента", command=self.open_add_window)\
            .pack(pady=5)
        
        ttk.Button(self, text="Редактировать клиента", command=self.open_edit_window)\
            .pack(pady=5)
        
        ttk.Button(self, text="Удалить клиента", command=self.delete_selected_client)\
            .pack(pady=5)



        self.load_clients()

    # ---------- ЗАГРУЗКА КЛИЕНТОВ ----------
    def load_clients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for client in get_all_clients():
            self.tree.insert("", "end", values=client)

    # ---------- ОКНО ДОБАВЛЕНИЯ ----------
    def open_add_window(self):
        window = tk.Toplevel(self)
        window.title("Добавить клиента")
        window.grab_set()

        fields = [
            ("Фамилия*", "lastname"),
            ("Имя*", "firstname"),
            ("Отчество", "patronymic"),
            ("Серия паспорта*", "series"),
            ("Номер паспорта*", "number"),
            ("Телефон (+7XXXXXXXXXX)*", "phone")
        ]

        entries = {}

        # ===== ВАЛИДАТОРЫ ВВОДА =====

        # ФИО: только русские буквы, пробел, дефис
        def name_validator(value):
            if value == "":
                return True
            return bool(re.fullmatch(r"[А-Яа-яЁё\s\-]+", value))

        vcmd_name = (window.register(name_validator), "%P")

        # Серия: до 4 цифр
        vcmd_series = (window.register(
            lambda s: s.isdigit() and len(s) <= 4 or s == ""
        ), "%P")

        # Номер: до 6 цифр
        vcmd_number = (window.register(
            lambda s: s.isdigit() and len(s) <= 6 or s == ""
        ), "%P")

        # Телефон: строго +7XXXXXXXXXX
        def phone_validator(value):
            if value == "+7":
                return True
            if not value.startswith("+7"):
                return False
            if not value[2:].isdigit():
                return False
            return len(value) <= 12

        vcmd_phone = (window.register(phone_validator), "%P")

        # ===== СОЗДАНИЕ ПОЛЕЙ =====

        for i, (label, key) in enumerate(fields):
            tk.Label(window, text=label).grid(
                row=i, column=0, pady=5, padx=5, sticky="e"
            )

            if key in ("lastname", "firstname", "patronymic"):
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_name)

            elif key == "series":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_series)

            elif key == "number":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_number)

            elif key == "phone":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_phone)
                entry.insert(0, "+7")

            else:
                entry = tk.Entry(window)

            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[key] = entry

        # ===== СОХРАНЕНИЕ =====

        def save():
            lastname = entries["lastname"].get().strip()
            firstname = entries["firstname"].get().strip()
            patronymic = entries["patronymic"].get().strip() or None
            series = entries["series"].get()
            number = entries["number"].get()
            phone = entries["phone"].get()

            fio_pattern = r"^[А-Яа-яЁё\s\-]+$"

            # --- ОБЯЗАТЕЛЬНЫЕ ПОЛЯ ---
            if not lastname or not firstname:
                messagebox.showerror(
                    "Ошибка",
                    "Фамилия и имя являются обязательными"
                )
                return

            # --- ФИО ---
            if not re.fullmatch(fio_pattern, lastname):
                messagebox.showerror(
                    "Ошибка",
                    "Фамилия может содержать только русские буквы, пробел и дефис"
                )
                return

            if not re.fullmatch(fio_pattern, firstname):
                messagebox.showerror(
                    "Ошибка",
                    "Имя может содержать только русские буквы, пробел и дефис"
                )
                return

            if patronymic and not re.fullmatch(fio_pattern, patronymic):
                messagebox.showerror(
                    "Ошибка",
                    "Отчество может содержать только русские буквы, пробел и дефис"
                )
                return

            # --- ПАСПОРТ ---
            if len(series) != 4:
                messagebox.showerror(
                    "Ошибка",
                    "Серия паспорта должна состоять из 4 цифр"
                )
                return

            if len(number) != 6:
                messagebox.showerror(
                    "Ошибка",
                    "Номер паспорта должен состоять из 6 цифр"
                )
                return

            # --- ТЕЛЕФОН ---
            if not phone.startswith("+7") or len(phone) != 12:
                messagebox.showerror(
                    "Ошибка",
                    "Телефон должен быть в формате +7XXXXXXXXXX"
                )
                return

            # --- СОХРАНЕНИЕ В БД ---
            if add_client(
                lastname,
                firstname,
                patronymic,
                series,
                number,
                phone
            ):
                self.load_clients()
                messagebox.showinfo("Успех", "Клиент успешно добавлен")
                window.destroy()
            else:
                messagebox.showerror(
                    "Ошибка",
                    "Не удалось добавить клиента"
                )

        tk.Button(
            window, text="Сохранить", command=save
        ).grid(row=len(fields), column=0, columnspan=2, pady=10)


    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования")
            return

        values = self.tree.item(selected[0], "values")

        client_id = values[0]

        window = tk.Toplevel(self)
        window.title("Редактировать клиента")
        window.grab_set()

        fields = [
            ("Фамилия*", "lastname", values[1]),
            ("Имя*", "firstname", values[2]),
            ("Отчество", "patronymic", values[3]),
            ("Серия паспорта*", "series", values[4]),
            ("Номер паспорта*", "number", values[5]),
            ("Телефон (+7XXXXXXXXXX)*", "phone", values[6])
        ]

        entries = {}

        # ===== ВАЛИДАТОРЫ (ТЕ ЖЕ!) =====

        def name_validator(value):
            if value == "":
                return True
            return bool(re.fullmatch(r"[А-Яа-яЁё\s\-]+", value))

        vcmd_name = (window.register(name_validator), "%P")

        vcmd_series = (window.register(
            lambda s: s.isdigit() and len(s) <= 4 or s == ""
        ), "%P")

        vcmd_number = (window.register(
            lambda s: s.isdigit() and len(s) <= 6 or s == ""
        ), "%P")

        def phone_validator(value):
            if value == "+7":
                return True
            if not value.startswith("+7"):
                return False
            if not value[2:].isdigit():
                return False
            return len(value) <= 12

        vcmd_phone = (window.register(phone_validator), "%P")

        # ===== ПОЛЯ =====

        for i, (label, key, value) in enumerate(fields):
            tk.Label(window, text=label).grid(row=i, column=0, pady=5, padx=5, sticky="e")

            if key in ("lastname", "firstname", "patronymic"):
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_name)
            elif key == "series":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_series)
            elif key == "number":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_number)
            elif key == "phone":
                entry = tk.Entry(window, validate="key", validatecommand=vcmd_phone)
            else:
                entry = tk.Entry(window)

            entry.insert(0, value)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[key] = entry

        # ===== СОХРАНЕНИЕ =====

        def save():
            lastname = entries["lastname"].get().strip()
            firstname = entries["firstname"].get().strip()
            patronymic = entries["patronymic"].get().strip() or None
            series = entries["series"].get()
            number = entries["number"].get()
            phone = entries["phone"].get()

            fio_pattern = r"^[А-Яа-яЁё\s\-]+$"

            if not lastname or not firstname:
                messagebox.showerror("Ошибка", "Фамилия и имя обязательны")
                return

            if not re.fullmatch(fio_pattern, lastname):
                messagebox.showerror("Ошибка", "Некорректная фамилия")
                return

            if not re.fullmatch(fio_pattern, firstname):
                messagebox.showerror("Ошибка", "Некорректное имя")
                return

            if patronymic and not re.fullmatch(fio_pattern, patronymic):
                messagebox.showerror("Ошибка", "Некорректное отчество")
                return

            if len(series) != 4 or len(number) != 6:
                messagebox.showerror("Ошибка", "Некорректные паспортные данные")
                return

            if not phone.startswith("+7") or len(phone) != 12:
                messagebox.showerror("Ошибка", "Телефон должен быть +7XXXXXXXXXX")
                return

            if update_client(
                client_id,
                lastname,
                firstname,
                patronymic,
                series,
                number,
                phone
            ):
                self.load_clients()
                messagebox.showinfo("Успех", "Данные клиента обновлены")
                window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить клиента")

        tk.Button(window, text="Сохранить", command=save)\
            .grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_selected_client(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showerror("Ошибка", "Выберите клиента для удаления")
            return

        values = self.tree.item(selected[0], "values")
        client_id = values[0]
        fio = f"{values[1]} {values[2]}"

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы действительно хотите удалить клиента:\n{fio}?\n\n"
            "⚠️ Операция необратима!"
        )

        if not confirm:
            return

        if delete_client(client_id):
            self.load_clients()
            messagebox.showinfo("Успех", "Клиент успешно удалён")
        else:
            messagebox.showerror(
                "Ошибка",
                "Невозможно удалить клиента.\n"
                "Возможно, у него есть связанные договоры."
            )

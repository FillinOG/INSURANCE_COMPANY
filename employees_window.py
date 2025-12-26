import tkinter as tk
from tkinter import ttk, messagebox
from services.employees import (
    get_employees,
    add_employee,
    update_employee,
    delete_employee
)


class EmployeesWindow(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user

        self.tree = ttk.Treeview(
            self,
            columns=("id", "lastname", "firstname",
                     "patronymic", "phone", "login", "role"),
            show="headings"
        )

        headings = [
            ("id", "ID"),
            ("lastname", "Фамилия"),
            ("firstname", "Имя"),
            ("patronymic", "Отчество"),
            ("phone", "Телефон"),
            ("login", "Логин"),
            ("role", "Роль")
        ]

        for col, text in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        if self.user["role"] == "admin":
            btn_frame = ttk.Frame(self)
            btn_frame.pack(pady=5)

            ttk.Button(btn_frame, text="Добавить", command=self.open_add).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Редактировать", command=self.open_edit).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Удалить", command=self.delete_selected).pack(side="left", padx=5)

        self.load_employees()

    def load_employees(self):
        self.tree.delete(*self.tree.get_children())
        for emp in get_employees(self.user):
            self.tree.insert("", "end", values=emp)

    def open_add(self):
        win = tk.Toplevel(self)
        win.title("Добавить сотрудника")
        win.grab_set()

        labels = [
            "Фамилия", "Имя", "Отчество",
            "Телефон", "Логин", "Пароль", "Роль"
        ]

        entries = {}

        for i, label in enumerate(labels):
            ttk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if label == "Роль":
                cb = ttk.Combobox(win, values=["admin", "employee"], state="readonly")
                cb.current(1)
                cb.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = cb
            elif label == "Пароль":
                e = ttk.Entry(win, show="*")
                e.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = e
            else:
                e = ttk.Entry(win)
                e.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = e

        def save():
            try:
                data = {
                    "Фамилия": entries["Фамилия"].get(),
                    "Имя": entries["Имя"].get(),
                    "Отчество": entries["Отчество"].get(),
                    "Номер_телефона": entries["Телефон"].get(),
                    "login": entries["Логин"].get(),
                    "password": entries["Пароль"].get(),
                    "role": entries["Роль"].get()
                }
                add_employee(data)
                self.load_employees()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(win, text="Сохранить", command=save).grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        emp_id = self.tree.item(selected[0])["values"][0]

        if emp_id == self.user["employee_id"]:
            messagebox.showerror("Ошибка", "Нельзя удалить самого себя")
            return

        if messagebox.askyesno("Подтверждение", "Удалить сотрудника?"):
            delete_employee(emp_id)
            self.load_employees()

    def open_edit(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]

        emp_id = values[0]

        win = tk.Toplevel(self)
        win.title("Редактировать сотрудника")
        win.grab_set()

        row = 0

        # ---- ID (НЕ редактируется) ----
        ttk.Label(win, text="ID сотрудника").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(win, text=str(emp_id)).grid(row=row, column=1, padx=5, pady=5, sticky="w")
        row += 1

        fields = [
            ("Фамилия", values[1]),
            ("Имя", values[2]),
            ("Отчество", values[3]),
            ("Телефон", values[4]),
            ("Логин", values[5]),
            ("Пароль", ""),   # пароль вводится ТОЛЬКО если хотят сменить
            ("Роль", values[6])
        ]

        entries = {}

        for label, value in fields:
            ttk.Label(win, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")

            if label == "Роль":
                cb = ttk.Combobox(win, values=["admin", "employee"], state="readonly")
                cb.set(value)
                cb.grid(row=row, column=1, padx=5, pady=5)
                entries[label] = cb

            elif label == "Пароль":
                e = ttk.Entry(win, show="*")
                e.grid(row=row, column=1, padx=5, pady=5)
                entries[label] = e

            else:
                e = ttk.Entry(win)
                e.insert(0, value if value else "")
                e.grid(row=row, column=1, padx=5, pady=5)
                entries[label] = e

            row += 1

        def save():
            try:
                data = {
                    "Фамилия": entries["Фамилия"].get(),
                    "Имя": entries["Имя"].get(),
                    "Отчество": entries["Отчество"].get(),
                    "Номер_телефона": entries["Телефон"].get(),
                    "login": entries["Логин"].get(),
                    "role": entries["Роль"].get()
                }

                password = entries["Пароль"].get()
                if password:
                    data["password"] = password

                update_employee(emp_id, data)
                self.load_employees()
                win.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(win, text="Сохранить", command=save).grid(
            row=row, column=0, columnspan=2, pady=10
        )


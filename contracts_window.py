import tkinter as tk
from tkinter import ttk, messagebox
from services.contracts import get_all_contracts, add_contract, parse_date
from services.clients import get_all_clients
from services.objects import get_all_objects
from services.employees import get_employees


class ContractsWindow(ttk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user

        self.tree = ttk.Treeview(
            self,
            columns=("id", "client", "object", "employee",
                     "cost", "period"),
            show="headings"
        )

        self.tree.heading("id", text="№ договора")
        self.tree.heading("client", text="Клиент")
        self.tree.heading("object", text="Объект")
        self.tree.heading("employee", text="Сотрудник")
        self.tree.heading("cost", text="Стоимость")
        self.tree.heading("period", text="Срок действия")

        self.tree.pack(fill="both", expand=True, pady=10)

        ttk.Button(self, text="Добавить договор", command=self.open_add).pack(pady=5)

        self.load_contracts()

    def load_contracts(self):
        self.tree.delete(*self.tree.get_children())
        for row in get_all_contracts(self.user):
            period = f'{row[5].strftime("%d.%m.%Y")} – {row[6].strftime("%d.%m.%Y")}'
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4], period
            ))

    def open_add(self):
        win = tk.Toplevel(self)
        win.title("Добавить договор")
        win.grab_set()

        clients = get_all_clients()
        objects = get_all_objects()

        def build_map(data):
            return {row[1]: row[0] for row in data}

        client_map = build_map(clients)
        object_map = build_map(objects)

        row_i = 0

        ttk.Label(win, text="Клиент").grid(row=row_i, column=0)
        client_cb = ttk.Combobox(win, values=list(client_map.keys()), state="readonly")
        client_cb.grid(row=row_i, column=1)
        row_i += 1

        if self.user["role"] == "admin":
            employees = get_employees(self.user)
            employee_map = {f"{e[1]} {e[2]}": e[0] for e in employees}

            ttk.Label(win, text="Сотрудник").grid(row=row_i, column=0)
            employee_cb = ttk.Combobox(
                win, values=list(employee_map.keys()), state="readonly"
            )
            employee_cb.grid(row=row_i, column=1)
            row_i += 1
        else:
            employee_map = None

        ttk.Label(win, text="Объект").grid(row=row_i, column=0)
        object_cb = ttk.Combobox(win, values=list(object_map.keys()), state="readonly")
        object_cb.grid(row=row_i, column=1)
        row_i += 1

        ttk.Label(win, text="Стоимость").grid(row=row_i, column=0)
        cost_entry = ttk.Entry(win)
        cost_entry.grid(row=row_i, column=1)
        row_i += 1

        ttk.Label(win, text="Дата начала (ДД.ММ.ГГГГ)").grid(row=row_i, column=0)
        start_entry = ttk.Entry(win)
        start_entry.grid(row=row_i, column=1)
        row_i += 1

        ttk.Label(win, text="Дата окончания (ДД.ММ.ГГГГ)").grid(row=row_i, column=0)
        end_entry = ttk.Entry(win)
        end_entry.grid(row=row_i, column=1)
        row_i += 1

        def save():
            try:
                cost = float(cost_entry.get())
                start_date = parse_date(start_entry.get())
                end_date = parse_date(end_entry.get())

                employee_id = (
                    employee_map[employee_cb.get()]
                    if self.user["role"] == "admin"
                    else self.user["employee_id"]
                )

                add_contract(
                    employee_id,
                    client_map[client_cb.get()],
                    object_map[object_cb.get()],
                    cost,
                    start_date,
                    end_date
                )

                self.load_contracts()
                win.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(win, text="Сохранить", command=save)\
            .grid(row=row_i, column=0, columnspan=2, pady=10)

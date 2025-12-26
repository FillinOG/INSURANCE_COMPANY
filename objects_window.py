import tkinter as tk
from tkinter import ttk, messagebox
from services.objects import (
    get_all_objects,
    add_object,
    update_object,
    delete_object
)
from services.clients import get_all_clients


class ObjectsWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.tree = ttk.Treeview(
            self,
            columns=("id", "object", "fio", "contract"),
            show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("object", text="Объект страхования")
        self.tree.heading("fio", text="Страхователь")
        self.tree.heading("contract", text="№ договора")

        self.tree.pack(fill="both", expand=True, pady=10)

        ttk.Button(self, text="Добавить объект", command=self.open_add).pack(pady=3)
        ttk.Button(self, text="Редактировать объект", command=self.open_edit).pack(pady=3)
        ttk.Button(self, text="Удалить объект", command=self.remove).pack(pady=3)

        self.load_objects()

    def load_objects(self):
        self.tree.delete(*self.tree.get_children())
        for obj in get_all_objects():
            self.tree.insert("", "end", values=obj)

    def open_add(self):
        win = tk.Toplevel(self)
        win.title("Добавить объект")
        win.grab_set()

        tk.Label(win, text="Клиент").grid(row=0, column=0, padx=5, pady=5)

        clients = get_all_clients()
        client_map = {
            f"{c[1]} {c[2]}": c[0] for c in clients
        }

        client_cb = ttk.Combobox(
            win,
            values=list(client_map.keys()),
            state="readonly"
        )
        client_cb.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Объект страхования").grid(row=1, column=0)
        obj_entry = tk.Entry(win)
        obj_entry.grid(row=1, column=1)

        def save():
            if not client_cb.get() or not obj_entry.get():
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            if add_object(
                client_map[client_cb.get()],
                obj_entry.get()
            ):
                self.load_objects()
                win.destroy()

        tk.Button(win, text="Сохранить", command=save).grid(
            row=2, column=0, columnspan=2, pady=10
        )

    def open_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите объект")
            return

        values = self.tree.item(selected[0], "values")
        object_id = values[0]

        win = tk.Toplevel(self)
        win.title("Редактировать объект")
        win.grab_set()

        tk.Label(win, text="Объект страхования").grid(row=0, column=0)
        entry = tk.Entry(win)
        entry.insert(0, values[1])
        entry.grid(row=0, column=1)

        def save():
            if update_object(object_id, entry.get()):
                self.load_objects()
                win.destroy()

        tk.Button(win, text="Сохранить", command=save).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def remove(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите объект")
            return

        object_id = self.tree.item(selected[0], "values")[0]

        if messagebox.askyesno("Подтверждение", "Удалить объект?"):
            if delete_object(object_id):
                self.load_objects()

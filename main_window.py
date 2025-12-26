import tkinter as tk
from tkinter import ttk
from ui.clients_window import ClientsWindow
from ui.objects_window import ObjectsWindow
from ui.contracts_window import ContractsWindow
from ui.employees_window import EmployeesWindow


class MainWindow:
    def __init__(self, root, user):
        self.user = user

        # создаём НОВОЕ окно
        self.window = tk.Toplevel(root)
        self.window.title("Страховая компания")
        self.window.geometry("900x500")

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True)

        clients_tab = ClientsWindow(notebook)
        notebook.add(clients_tab, text="Клиенты")

        objects_tab = ObjectsWindow(notebook)
        notebook.add(objects_tab, text="Объекты страхования")

        contracts_tab = ContractsWindow(notebook, self.user)
        notebook.add(contracts_tab, text="Договоры")

        employees_tab = EmployeesWindow(notebook, self.user)
        notebook.add(employees_tab, text="Сотрудники")


        # если закрыли главное окно — закрываем всё приложение
        self.window.protocol("WM_DELETE_WINDOW", root.quit)

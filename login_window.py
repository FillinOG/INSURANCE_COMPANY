import tkinter as tk
from tkinter import messagebox
from services.employees import authenticate


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Вход в систему")
        self.root.geometry("300x200")

        tk.Label(root, text="Логин").pack(pady=5)
        self.login_entry = tk.Entry(root)
        self.login_entry.pack()

        tk.Label(root, text="Пароль").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Войти", command=self.login).pack(pady=15)

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        user = authenticate(login, password)

        if user:
            from ui.main_window import MainWindow

            self.root.withdraw()   # скрываем окно логина
            MainWindow(self.root, user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

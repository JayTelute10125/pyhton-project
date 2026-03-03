import tkinter as tk
from tkinter import messagebox
import random
import json
import os

DATA_FILE = "hangman_users.json"
DEFAULT_ATTEMPTS = 6

WORD_BANK = {
    "easy": [
        {"word": "cat", "hint": "A small domestic animal"},
        {"word": "tree", "hint": "Grows in forests"},
        {"word": "fish", "hint": "Lives in water"}
    ],
    "medium": [
        {"word": "python", "hint": "Popular programming language"},
        {"word": "planet", "hint": "Orbits a star"},
        {"word": "silver", "hint": "A precious metal"}
    ],
    "hard": [
        {"word": "developer", "hint": "Person who writes code"},
        {"word": "algorithm", "hint": "Step-by-step problem solving method"},
        {"word": "database", "hint": "Stores structured information"}
    ]
}


# ================= USER CLASS =================

class User:
    def __init__(self, username):
        self.username = username
        self.games_played = 0
        self.games_won = 0

    def record_win(self):
        self.games_played += 1
        self.games_won += 1

    def record_loss(self):
        self.games_played += 1

    def win_rate(self):
        if self.games_played == 0:
            return 0.0
        return round((self.games_won / self.games_played) * 100, 2)

    def to_dict(self):
        return {
            "games_played": self.games_played,
            "games_won": self.games_won
        }


# ================= MAIN GAME GUI =================

class HangmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Hangman Game")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")

        self.users = self.load_users()
        self.user = None

        self.create_login_screen()

    # ---------- LOGIN ----------

    def create_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter Username",
                 font=("Arial", 18),
                 bg="#1e1e1e", fg="white").pack(pady=20)

        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=10)

        tk.Button(self.root, text="Start",
                  command=self.login,
                  bg="#4CAF50", fg="white",
                  font=("Arial", 12)).pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        if username in self.users:
            self.user = self.users[username]
        else:
            self.user = User(username)
            self.users[username] = self.user

        self.create_menu_screen()

    # ---------- MENU ----------

    def create_menu_screen(self):
        self.clear_screen()

        tk.Label(self.root, text=f"Welcome, {self.user.username}",
                 font=("Arial", 18),
                 bg="#1e1e1e", fg="cyan").pack(pady=20)

        tk.Button(self.root, text="Play Game",
                  command=self.create_game_screen,
                  bg="#2196F3", fg="white",
                  width=15).pack(pady=10)

        tk.Button(self.root, text="View Stats",
                  command=self.show_stats,
                  bg="#FF9800", fg="white",
                  width=15).pack(pady=10)

        tk.Button(self.root, text="Exit",
                  command=self.root.quit,
                  bg="#f44336", fg="white",
                  width=15).pack(pady=10)

    # ---------- GAME ----------

    def create_game_screen(self):
        self.clear_screen()

        self.difficulty = tk.StringVar(value="easy")

        difficulty_menu = tk.OptionMenu(
            self.root, self.difficulty, *WORD_BANK.keys())
        difficulty_menu.pack(pady=10)

        tk.Button(self.root, text="Start Game",
                  command=self.start_game,
                  bg="#4CAF50", fg="white").pack(pady=10)

    def start_game(self):
        word_data = random.choice(WORD_BANK[self.difficulty.get()])
        self.word = word_data["word"]
        self.hint = word_data["hint"]
        self.guessed_letters = set()
        self.wrong_letters = set()
        self.attempts_left = DEFAULT_ATTEMPTS

        self.clear_screen()

        tk.Label(self.root, text=f"Hint: {self.hint}",
                 font=("Arial", 14),
                 bg="#1e1e1e", fg="yellow").pack(pady=10)

        self.word_label = tk.Label(self.root, text=self.display_word(),
                                   font=("Courier", 28),
                                   bg="#1e1e1e", fg="white")
        self.word_label.pack(pady=20)

        self.info_label = tk.Label(self.root,
                                   text=f"Attempts Left: {self.attempts_left}",
                                   font=("Arial", 12),
                                   bg="#1e1e1e", fg="red")
        self.info_label.pack(pady=10)

        self.create_letter_buttons()

    def create_letter_buttons(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack()

        for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            btn = tk.Button(frame, text=letter.upper(),
                            width=4, height=2,
                            bg="#333", fg="white",
                            command=lambda l=letter: self.guess(l))
            btn.grid(row=i // 9, column=i % 9, padx=5, pady=5)

    def guess(self, letter):
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return

        if letter in self.word:
            self.guessed_letters.add(letter)
        else:
            self.wrong_letters.add(letter)
            self.attempts_left -= 1

        self.word_label.config(text=self.display_word())
        self.info_label.config(
            text=f"Attempts Left: {self.attempts_left}")

        if self.is_won():
            self.user.record_win()
            self.save_users()
            messagebox.showinfo("🎉 You Won!",
                                f"The word was: {self.word}")
            self.create_menu_screen()

        elif self.attempts_left <= 0:
            self.user.record_loss()
            self.save_users()
            messagebox.showerror("💀 You Lost!",
                                 f"The word was: {self.word}")
            self.create_menu_screen()

    def display_word(self):
        return " ".join(
            letter if letter in self.guessed_letters else "_"
            for letter in self.word
        )

    def is_won(self):
        return all(letter in self.guessed_letters for letter in self.word)

    # ---------- STATS ----------

    def show_stats(self):
        messagebox.showinfo(
            "Statistics",
            f"Games Played: {self.user.games_played}\n"
            f"Games Won: {self.user.games_won}\n"
            f"Win Rate: {self.user.win_rate()}%"
        )

    # ---------- UTILITIES ----------

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_users(self):
        if not os.path.exists(DATA_FILE):
            return {}

        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
        except:
            return {}

        users = {}
        for username, stats in data.items():
            user = User(username)
            user.games_played = stats.get("games_played", 0)
            user.games_won = stats.get("games_won", 0)
            users[username] = user
        return users

    def save_users(self):
        data = {username: user.to_dict()
                for username, user in self.users.items()}
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)


# ================= RUN =================

if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanGUI(root)
    root.mainloop()
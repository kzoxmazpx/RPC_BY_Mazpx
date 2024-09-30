import tkinter as tk
from tkinter import ttk, messagebox
from pypresence import Presence
import time
import threading
from ttkbootstrap import Style
import json
import os
import sys
import subprocess
import winreg as reg

CLIENT_ID = '1281631749348003932'  # ID de client fixe
APP_NAME = 'Discord Rich Presence App'  # Nom de l'application pour le registre Windows
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"  # Chemin dans le registre pour le démarrage automatique

class RichPresenceApp:
    def __init__(self, root):
        self.state = tk.StringVar()
        self.details = tk.StringVar()
        self.large_image = tk.StringVar()
        self.large_text = tk.StringVar()
        self.small_image = tk.StringVar()
        self.small_text = tk.StringVar()
        self.button1_label = tk.StringVar()
        self.button1_url = tk.StringVar()
        self.button2_label = tk.StringVar()
        self.button2_url = tk.StringVar()

        self.load_data()  # Charger les données enregistrées au démarrage de l'application

        root.title("Discord Rich Presence | By Mazpx & Kz0x._")

        style = Style(theme='darkly')  # Utilisation du thème sombre 'darkly' de ttkbootstrap
        main_frame = ttk.Frame(root, padding="10", style="Dark.TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")

        def create_label_entry(frame, text, var):
            label = ttk.Label(frame, text=text, style="White.TLabel")  # Utilisation du style White.TLabel pour le texte blanc
            entry = ttk.Entry(frame, textvariable=var, width=40, style="Custom.TEntry")  # Utilisation du style Custom.TEntry pour l'entrée de texte
            label.grid(row=len(frame.grid_slaves()) // 2, column=0, pady=5, sticky='w')
            entry.grid(row=len(frame.grid_slaves()) // 2, column=1, pady=5, padx=10, sticky='ew')
            return label, entry

        # Définition du style personnalisé pour les entrées de texte
        style.configure('Custom.TEntry', background='#303030', foreground='white', fieldbackground='#404040')

        create_label_entry(main_frame, "State ( Titre )", self.state)
        create_label_entry(main_frame, "Details ( Description )", self.details)
        create_label_entry(main_frame, "Large Image Url", self.large_image)
        create_label_entry(main_frame, "Large Image Text", self.large_text)
        create_label_entry(main_frame, "Small Image Url", self.small_image)
        create_label_entry(main_frame, "Small Image Text", self.small_text)
        create_label_entry(main_frame, "Button 1 Text", self.button1_label)
        create_label_entry(main_frame, "Button 1 URL", self.button1_url)
        create_label_entry(main_frame, "Button 2 Text", self.button2_label)
        create_label_entry(main_frame, "Button 2 URL", self.button2_url)

        button_frame = ttk.Frame(root)
        button_frame.grid(row=0, column=1, sticky="ns")

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_rich_presence, style="Dark.TButton")
        self.start_button.pack(pady=10, padx=20, fill='x')

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_rich_presence, state=tk.DISABLED, style="Dark.TButton")
        self.stop_button.pack(pady=10, padx=20, fill='x')

        self.save_button = ttk.Button(button_frame, text="Enregistrer", command=self.save_data, style="Dark.TButton")
        self.save_button.pack(pady=10, padx=20, fill='x')

        self.clear_button = ttk.Button(button_frame, text="Effacer", command=self.clear_data, style="Dark.TButton")
        self.clear_button.pack(pady=10, padx=20, fill='x')

        # Ajout du bouton pour activer/désactiver le démarrage automatique
        self.autostart_var = tk.BooleanVar()
        self.autostart_var.set(self.is_autostart_enabled())
        self.autostart_checkbox = ttk.Checkbutton(button_frame, text="Démarrage automatique au démarrage de Windows", variable=self.autostart_var, command=self.toggle_autostart)
        self.autostart_checkbox.pack(pady=10, padx=20, fill='x')

        root.grid_rowconfigure(0, weight=1)  # Permet au premier cadre de s'étendre avec la fenêtre
        root.grid_columnconfigure(0, weight=1)  # Permet à la colonne principale de s'étendre avec la fenêtre

        self.rpc = None
        self.update_thread = None
        self.running = False

        # Vérifier et démarrer automatiquement la présence si des données sont enregistrées
        if self.is_data_saved():
            self.start_rich_presence_delayed()

    def start_rich_presence_delayed(self):
        # Attendre 3 secondes avant de démarrer la rich presence
        root.after(3000, self.start_rich_presence)

    def start_rich_presence(self):
        self.rpc = Presence(CLIENT_ID)
        self.rpc.connect()

        self.running = True
        self.update_thread = threading.Thread(target=self.update_presence, daemon=True)
        self.update_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def update_presence(self):
        while self.running:
            presence_data = {
                'state': self.state.get(),
                'details': self.details.get(),
                'start': time.time()
            }

            if self.large_image.get():
                presence_data['large_image'] = self.large_image.get()
                presence_data['large_text'] = self.large_text.get()

            if self.small_image.get():
                presence_data['small_image'] = self.small_image.get()
                presence_data['small_text'] = self.small_text.get()

            buttons = []
            if self.button1_label.get() and self.button1_url.get():
                buttons.append({'label': self.button1_label.get(), 'url': self.button1_url.get()})
            if self.button2_label.get() and self.button2_url.get():
                buttons.append({'label': self.button2_label.get(), 'url': self.button2_url.get()})

            if buttons:
                presence_data['buttons'] = buttons

            self.rpc.update(**presence_data)
            time.sleep(15)  # Update every 15 seconds

    def stop_rich_presence(self):
        if self.running:
            self.running = False
            self.rpc.close()
            self.rpc = None

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        else:
            # Afficher un message demandant à mettre la rich presence sur stop
            messagebox.showinfo("Information", "Veuillez mettre la Rich Presence sur stop pour fermer l'application.")

    def save_data(self):
        data = {
            'state': self.state.get(),
            'details': self.details.get(),
            'large_image': self.large_image.get(),
            'large_text': self.large_text.get(),
            'small_image': self.small_image.get(),
            'small_text': self.small_text.get(),
            'button1_label': self.button1_label.get(),
            'button1_url': self.button1_url.get(),
            'button2_label': self.button2_label.get(),
            'button2_url': self.button2_url.get()
        }
        with open('rich_presence_data.json', 'w') as file:
            json.dump(data, file)

    def load_data(self):
        try:
            with open('rich_presence_data.json', 'r') as file:
                data = json.load(file)
                self.state.set(data['state'])
                self.details.set(data['details'])
                self.large_image.set(data['large_image'])
                self.large_text.set(data['large_text'])
                self.small_image.set(data['small_image'])
                self.small_text.set(data['small_text'])
                self.button1_label.set(data['button1_label'])
                self.button1_url.set(data['button1_url'])
                self.button2_label.set(data['button2_label'])
                self.button2_url.set(data['button2_url'])
        except FileNotFoundError:
            pass

    def clear_data(self):
        self.state.set('')
        self.details.set('')
        self.large_image.set('')
        self.large_text.set('')
        self.small_image.set('')
        self.small_text.set('')
        self.button1_label.set('')
        self.button1_url.set('')
        self.button2_label.set('')
        self.button2_url.set('')
        if self.running:
            self.stop_rich_presence()

        # Supprimer le fichier de données
        try:
            os.remove('rich_presence_data.json')
        except FileNotFoundError:
            pass

    def is_data_saved(self):
        # Vérifie si des données sont enregistrées dans le fichier JSON
        try:
            with open('rich_presence_data.json', 'r') as file:
                data = json.load(file)
                return bool(data)
        except FileNotFoundError:
            return False

    def is_autostart_enabled(self):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, REG_PATH, 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, APP_NAME)
            reg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except WindowsError:
            return False

    def toggle_autostart(self):
        if self.autostart_var.get():
            try:
                key = reg.OpenKey(reg.HKEY_CURRENT_USER, REG_PATH, 0, reg.KEY_WRITE)
                reg.SetValueEx(key, APP_NAME, 0, reg.REG_SZ, sys.executable + ' "' + os.path.abspath(__file__) + '"')
                reg.CloseKey(key)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to add to startup: {e}")
                self.autostart_var.set(False)
        else:
            try:
                key = reg.OpenKey(reg.HKEY_CURRENT_USER, REG_PATH, 0, reg.KEY_WRITE)
                reg.DeleteValue(key, APP_NAME)
                reg.CloseKey(key)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to remove from startup: {e}")
                self.autostart_var.set(True)

if __name__ == "__main__":
    root = Style(theme='darkly').master
    app = RichPresenceApp(root)
    root.mainloop()

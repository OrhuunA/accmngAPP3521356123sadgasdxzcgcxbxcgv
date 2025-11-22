
import customtkinter as ctk
import json
import os
import threading
import time
import requests
import sys
import webbrowser
from PIL import Image
from datetime import datetime
from cryptography.fernet import Fernet

# --- AYARLAR ---
DATA_FILE = "accounts_db.json"
CONFIG_FILE = "config.json"
KEY_FILE = "secret.key"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

RANK_ORDER = {
    "CHALLENGER": 9000, "GRANDMASTER": 8000, "MASTER": 7000,
    "DIAMOND": 6000, "EMERALD": 5000, "PLATINUM": 4000,
    "GOLD": 3000, "SILVER": 2000, "BRONZE": 1000, "IRON": 0, "UNRANKED": -1
}

RANK_COLORS = {
    "IRON": "#7a7a7a", "BRONZE": "#8c7853", "SILVER": "#d3d3d3",
    "GOLD": "#DAA520", "PLATINUM": "#00CED1", "EMERALD": "#2ecc71",
    "DIAMOND": "#b9f2ff", "MASTER": "#9b59b6", "GRANDMASTER": "#c0392b",
    "CHALLENGER": "#F1C40F", "UNRANKED": "gray"
}

def resource_path(relative_path):
    """EXE olunca dosyaları geçici klasörde bulur"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_cursor():
    """Mac ve Windows için doğru el işaretini seçer"""
    if sys.platform == "darwin":
        return "pointinghand" # Mac
    else:
        return "hand2" # Windows

# --------------------------

class CipherManager:
    def __init__(self):
        self.key = self.load_key()
        self.cipher = Fernet(self.key)

    def load_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f: return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f: f.write(key)
            return key

    def encrypt(self, text): return self.cipher.encrypt(text.encode()).decode()
    def decrypt(self, encrypted_text):
        try: return self.cipher.decrypt(encrypted_text.encode()).decode()
        except: return encrypted_text

cipher_man = CipherManager()

# --- UI PENCERELERİ ---

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x280")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.my_parent = parent

        ctk.CTkLabel(self, text="SETTINGS", font=("Arial", 18, "bold"), text_color="white").pack(pady=(20, 10))

        ctk.CTkLabel(self, text="Riot API Key:", font=("Arial", 12), text_color="gray").pack(pady=(10, 0))
        
        self.entry_key = ctk.CTkEntry(self, width=300, height=35, placeholder_text="RGAPI-xxxxxxxx-xxxx-xxxx...")
        if self.my_parent.api_key:
            self.entry_key.insert(0, self.my_parent.api_key)
        self.entry_key.pack(pady=5)

        # --- LİNK DÜZELTMESİ ---
        cursor_style = get_cursor() # Windows/Mac uyumlu imleç
        self.link_lbl = ctk.CTkLabel(self, text="Get your key from developer.riotgames.com", font=("Arial", 11, "underline"), text_color="#4ea8de", cursor=cursor_style)
        self.link_lbl.pack(pady=(0, 20))
        self.link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://developer.riotgames.com"))
        self.link_lbl.bind("<Enter>", lambda e: self.link_lbl.configure(text_color="#69b3e7"))
        self.link_lbl.bind("<Leave>", lambda e: self.link_lbl.configure(text_color="#4ea8de"))

        # --- BUTON GARANTİSİ ---
        save_icon = self.my_parent.icons.get('save')
        if save_icon:
            self.save_btn = ctk.CTkButton(self, text="", image=save_icon, width=50, height=50, fg_color="#2ea44f", hover_color="#22863a", command=self.save_settings)
            self.save_btn.image = save_icon
        else:
            self.save_btn = ctk.CTkButton(self, text="SAVE KEY", width=200, height=40, fg_color="#2ea44f", hover_color="#22863a", command=self.save_settings)
        
        self.save_btn.pack(pady=10)

    def save_settings(self):
        new_key = self.entry_key.get().strip()
        self.my_parent.api_key = new_key
        self.my_parent.save_config()
        self.destroy()

class EditAccountWindow(ctk.CTkToplevel):
    def __init__(self, parent, acc):
        super().__init__(parent)
        self.title("Edit")
        self.geometry("350x550")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.my_parent = parent 
        self.acc = acc

        ctk.CTkLabel(self, text="EDIT ACCOUNT", font=("Arial", 18, "bold"), text_color="white").pack(pady=(20, 10))

        self.entry_user = ctk.CTkEntry(self, width=220, height=35)
        self.entry_user.insert(0, acc['login_id'])
        self.entry_user.pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self, width=220, height=35)
        self.entry_pass.insert(0, acc['login_pw'])
        self.entry_pass.pack(pady=5)

        ctk.CTkLabel(self, text="Riot ID", font=("Arial", 11), text_color="gray").pack(pady=(10, 0))
        self.entry_riot = ctk.CTkEntry(self, width=220, height=35)
        self.entry_riot.insert(0, acc['riot_id'])
        self.entry_riot.pack(pady=5)

        ctk.CTkLabel(self, text="Notes", font=("Arial", 11), text_color="gray").pack(pady=(10, 0))
        self.entry_note = ctk.CTkTextbox(self, width=220, height=80)
        self.entry_note.insert("0.0", acc.get('note', ''))
        self.entry_note.pack(pady=5)

        save_icon = self.my_parent.icons.get('save')
        if save_icon:
            self.save_btn = ctk.CTkButton(self, text="", image=save_icon, width=50, height=50, fg_color="#2ea44f", hover_color="#22863a", command=self.save_changes)
            self.save_btn.image = save_icon 
        else:
            self.save_btn = ctk.CTkButton(self, text="UPDATE", width=220, height=40, fg_color="#2ea44f", hover_color="#22863a", command=self.save_changes)
        self.save_btn.pack(pady=20)

    def save_changes(self):
        self.acc['login_id'] = self.entry_user.get().strip()
        self.acc['login_pw'] = self.entry_pass.get().strip()
        self.acc['riot_id'] = self.entry_riot.get().strip()
        self.acc['note'] = self.entry_note.get("0.0", "end").strip()
        self.my_parent.save_data()
        self.my_parent.filter_accounts(None)
        self.destroy()

class AccountDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent, acc):
        super().__init__(parent)
        self.title("Details")
        self.geometry("450x500")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.my_parent = parent 
        self.acc = acc

        ctk.CTkLabel(self, text=acc['riot_id'], font=("Arial", 24, "bold"), text_color="white").pack(pady=(25, 10))

        last_seen = acc.get('last_seen', 'Unknown')
        ctk.CTkLabel(self, text=f"Last Played: {last_seen}", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=40)

        self.create_info_row(info_frame, "User Name:", acc['login_id'])
        self.create_info_row(info_frame, "Password:", acc['login_pw'])

        if acc.get('note'):
            ctk.CTkLabel(self, text="NOTES", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(20, 5))
            note_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=6)
            note_frame.pack(fill="x", padx=40)
            ctk.CTkLabel(note_frame, text=acc['note'], wraplength=350, font=("Arial", 13), text_color="#ddd", justify="left").pack(padx=10, pady=10)

        ctk.CTkFrame(self, height=1, width=300, fg_color="#333").pack(pady=20)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=5)

        edit_icon = self.my_parent.icons.get('edit')
        btn_edit = ctk.CTkButton(action_frame, text="Edit", image=edit_icon, width=32, height=32, fg_color="#d98e04", hover_color="#b57602", command=self.open_edit)
        if edit_icon: 
            btn_edit.configure(text="")
            btn_edit.image = edit_icon
        btn_edit.pack(side="left", padx=8)

        delete_icon = self.my_parent.icons.get('delete')
        btn_delete = ctk.CTkButton(action_frame, text="Del", image=delete_icon, width=32, height=32, fg_color="#801818", hover_color="red", command=self.delete_this_account)
        if delete_icon: 
            btn_delete.configure(text="")
            btn_delete.image = delete_icon
        btn_delete.pack(side="left", padx=8)

    def create_info_row(self, parent_frame, label_text, value_text):
        row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text=label_text, width=85, anchor="w", text_color="gray", font=("Arial", 13)).pack(side="left")
        entry_val = ctk.CTkEntry(row, width=140, height=28, show="*", font=("Arial", 14))
        entry_val.insert(0, value_text)
        entry_val.configure(state="readonly")
        entry_val.pack(side="left", padx=5)

        copy_icon = self.my_parent.icons.get('copy')
        btn_copy = ctk.CTkButton(row, text="C", image=copy_icon, width=25, height=25, fg_color="#333", hover_color="#555")
        if copy_icon: 
            btn_copy.configure(text="")
            btn_copy.image = copy_icon
        btn_copy.configure(command=lambda b=btn_copy, t=value_text: self.my_parent.copy_to_clipboard(t, b))
        btn_copy.pack(side="right")

        show_icon = self.my_parent.icons.get('show')
        btn_reveal = ctk.CTkButton(row, text="S", image=show_icon, width=25, height=25, fg_color="#333", hover_color="#555")
        if show_icon: 
            btn_reveal.configure(text="")
            btn_reveal.image = show_icon
        btn_reveal.configure(command=lambda e=entry_val, b=btn_reveal: self.toggle_reveal(e, b))
        btn_reveal.pack(side="right", padx=(0, 4))

    def toggle_reveal(self, entry_widget, btn_widget):
        hide_icon = self.my_parent.icons.get('hide')
        show_icon = self.my_parent.icons.get('show')
        if entry_widget.cget("show") == "*":
            entry_widget.configure(show="")
            if hide_icon: 
                btn_widget.configure(image=hide_icon)
                btn_widget.image = hide_icon
        else:
            entry_widget.configure(show="*")
            if show_icon: 
                btn_widget.configure(image=show_icon)
                btn_widget.image = show_icon

    def open_edit(self):
        self.destroy()
        EditAccountWindow(self.my_parent, self.acc)

    def delete_this_account(self):
        self.my_parent.delete_account(self.acc)
        self.destroy()

class AddAccountWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New")
        self.geometry("350x550")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.my_parent = parent

        ctk.CTkLabel(self, text="NEW ACCOUNT", font=("Arial", 18, "bold"), text_color="white").pack(pady=(20, 10))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username", width=220, height=35)
        self.entry_user.pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=220, height=35)
        self.entry_pass.pack(pady=5)

        ctk.CTkLabel(self, text="Riot ID", font=("Arial", 11), text_color="gray").pack(pady=(10, 0))
        self.entry_riot = ctk.CTkEntry(self, placeholder_text="e.g. Faker#T1", width=220, height=35)
        self.entry_riot.pack(pady=5)
        ctk.CTkLabel(self, text="Format: Name#Tag (No spaces)", font=("Arial", 10), text_color="gray").pack(pady=(0, 5))

        ctk.CTkLabel(self, text="Notes (Optional)", font=("Arial", 11), text_color="gray").pack(pady=(5, 0))
        self.entry_note = ctk.CTkTextbox(self, width=220, height=80)
        self.entry_note.pack(pady=5)

        save_icon = self.my_parent.icons.get('save')
        if save_icon:
            self.save_btn = ctk.CTkButton(self, text="", image=save_icon, width=50, height=50, fg_color="#2ea44f", hover_color="#22863a", command=self.save_action)
            self.save_btn.image = save_icon 
        else:
            self.save_btn = ctk.CTkButton(self, text="SAVE", width=220, height=40, fg_color="#2ea44f", hover_color="#22863a", font=("Arial", 13, "bold"), command=self.save_action)
        self.save_btn.pack(pady=20)

    def save_action(self):
        u_id = self.entry_user.get()
        u_pw = self.entry_pass.get()
        r_id = self.entry_riot.get()

        if not u_id or not u_pw or not r_id:
            print("Missing info!")
            return

        new_acc = {
            "login_id": u_id.strip(),
            "login_pw": u_pw.strip(),
            "riot_id": r_id.strip(),
            "server": self.my_parent.server_var.get(),
            "rank_tier": "UNRANKED", "rank_div": "", "lp": 0,
            "note": self.entry_note.get("0.0", "end").strip(),
            "last_seen": "Unknown"
        }
        self.my_parent.add_account_to_db(new_acc)
        self.destroy()

class LolManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("League ACC Manager v27.0")
        self.geometry("1000x700")
        
        self.api_key = self.load_config()
        self.accounts = self.load_data()
        self.sort_descending = True
        
        self.load_icons()
        self.load_rank_images()

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="League ACC\nManager", font=ctk.CTkFont(size=22, weight="bold")).pack(padx=20, pady=(30, 10))

        ctk.CTkLabel(self.sidebar, text="Server:", text_color="gray").pack(padx=20, pady=(10, 5))
        self.server_var = ctk.StringVar(value="EUW1")
        self.server_menu = ctk.CTkOptionMenu(self.sidebar, variable=self.server_var, values=["TR1", "EUW1", "EUN1", "NA1"], command=self.filter_accounts, width=180)
        self.server_menu.pack(padx=20, pady=5)

        self.sort_btn = ctk.CTkButton(self.sidebar, text="⬇️ Rank: High to Low", command=self.toggle_sort, fg_color="#444", hover_color="#555", width=180)
        self.sort_btn.pack(padx=20, pady=10)

        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)

        self.add_btn = ctk.CTkButton(self.sidebar, text="+ ADD ACCOUNT", command=self.open_add_window, fg_color="#2ea44f", hover_color="#22863a", height=40, font=("Arial", 13, "bold"))
        self.add_btn.pack(padx=20, pady=(10, 10))

        self.refresh_btn = ctk.CTkButton(self.sidebar, text="UPDATE RANKS (API)", command=self.update_ranks_from_api, fg_color="#0366d6", hover_color="#0256b4", height=40, font=("Arial", 13, "bold"))
        self.refresh_btn.pack(padx=20, pady=10)

        self.settings_btn = ctk.CTkButton(self.sidebar, text="⚙️ Settings", command=self.open_settings, fg_color="transparent", border_width=1, border_color="gray", text_color="gray")
        self.settings_btn.pack(side="bottom", pady=20, padx=20)

        self.main_area = ctk.CTkScrollableFrame(self, label_text="Accounts List")
        self.main_area.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.filter_accounts(None)
    
    def load_icons(self):
        self.icons = {}
        assets_dir = resource_path("assets")
        
        def get_img(filename, size):
            path = os.path.join(assets_dir, filename)
            if not os.path.exists(path): 
                path = os.path.join(os.path.abspath("."), "assets", filename) 

            if os.path.exists(path):
                return ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=size)
            return None

        s = (14, 14)
        self.icons['edit'] = get_img("edit.png", s)
        self.icons['delete'] = get_img("delete.png", s)
        self.icons['copy'] = get_img("copy.png", s)
        self.icons['show'] = get_img("show.png", s)
        self.icons['hide'] = get_img("hide.png", s)
        self.icons['save'] = get_img("save.png", (24, 24))

    def load_rank_images(self):
        self.rank_icons = {}
        rank_dir = resource_path(os.path.join("assets", "ranks"))
        size = (45, 45)
        tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER", "UNRANKED"]
        
        for tier in tiers:
            path = os.path.join(rank_dir, f"{tier}.png")
            if not os.path.exists(path): 
                path = os.path.join(os.path.abspath("."), "assets", "ranks", f"{tier}.png")

            if os.path.exists(path):
                self.rank_icons[tier] = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=size)
            else:
                self.rank_icons[tier] = None

    def load_data(self):
        if not os.path.exists(DATA_FILE): return []
        with open(DATA_FILE, "r") as f: 
            data = json.load(f)
            for acc in data: acc['login_pw'] = cipher_man.decrypt(acc['login_pw'])
            return data

    def save_data(self):
        data_to_save = []
        for acc in self.accounts:
            safe_acc = acc.copy()
            safe_acc['login_pw'] = cipher_man.encrypt(acc['login_pw'])
            data_to_save.append(safe_acc)
        with open(DATA_FILE, "w") as f: json.dump(data_to_save, f, indent=4)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: return json.load(f).get("api_key", "")
        return ""

    def save_config(self):
        with open(CONFIG_FILE, "w") as f: json.dump({"api_key": self.api_key}, f, indent=4)

    def open_settings(self): SettingsWindow(self)
    def open_add_window(self): AddAccountWindow(self)
    def open_details_window(self, acc): AccountDetailsWindow(self, acc)
    def add_account_to_db(self, new_acc): 
        self.accounts.append(new_acc)
        self.save_data()
        self.filter_accounts(None)
    def delete_account(self, acc):
        if acc in self.accounts: self.accounts.remove(acc)
        self.save_data()
        self.filter_accounts(None)
    def copy_to_clipboard(self, text, btn):
        self.clipboard_clear(); self.clipboard_append(text); self.update()
        orig_fg = btn.cget("fg_color"); btn.configure(fg_color="green"); self.after(1000, lambda: btn.configure(fg_color=orig_fg))
    def get_rank_score(self, acc):
        tier = acc.get("rank_tier", "UNRANKED"); base = RANK_ORDER.get(tier, -1)
        div = {"I": 300, "II": 200, "III": 100, "IV": 0}.get(acc.get("rank_div", "IV"), 0)
        return base + div + acc.get("lp", 0)
    def toggle_sort(self):
        self.sort_descending = not self.sort_descending
        self.sort_btn.configure(text="⬇️ Rank: High to Low" if self.sort_descending else "⬆️ Rank: Low to High")
        self.filter_accounts(None)
    
    def filter_accounts(self, choice):
        for w in self.main_area.winfo_children(): w.destroy()
        selected = self.server_var.get()
        filtered = [acc for acc in self.accounts if acc["server"] == selected]
        filtered.sort(key=self.get_rank_score, reverse=self.sort_descending)
        if not filtered: ctk.CTkLabel(self.main_area, text=f"No accounts in {selected}", font=("Arial", 14)).pack(pady=20)
        for acc in filtered: self.create_card(acc)

    def create_card(self, acc):
        card = ctk.CTkFrame(self.main_area, border_width=1, border_color="#404040", fg_color="#2b2b2b")
        card.pack(fill="x", padx=5, pady=8)
        card.bind("<Button-1>", lambda event, a=acc: self.open_details_window(a))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        content.bind("<Button-1>", lambda event, a=acc: self.open_details_window(a))
        
        rank_img = self.rank_icons.get(acc.get('rank_tier', 'UNRANKED'))
        if rank_img:
            lbl_img = ctk.CTkLabel(content, text="", image=rank_img)
            lbl_img.pack(side="left", padx=(0, 15))
            lbl_img.bind("<Button-1>", lambda event, a=acc: self.open_details_window(a))
        
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", anchor="w")
        info_frame.bind("<Button-1>", lambda event, a=acc: self.open_details_window(a))
        ctk.CTkLabel(info_frame, text=acc['riot_id'], font=("Arial", 18, "bold"), text_color="white").pack(anchor="w")
        if 'winrate' in acc:
            wr_color = "#2ecc71" if any(x in acc['winrate'] for x in "56789") else "#e74c3c"
            ctk.CTkLabel(info_frame, text=acc['winrate'], font=("Arial", 11), text_color=wr_color).pack(anchor="w")
        
        rank_txt = f"{acc.get('rank_tier', 'UNRANKED')} {acc.get('rank_div', '')}"
        lbl_rank = ctk.CTkLabel(content, text=f"{rank_txt} ({acc.get('lp', 0)} LP)", font=("Arial", 14, "bold"), text_color=RANK_COLORS.get(acc.get('rank_tier', 'UNRANKED'), "gray"))
        lbl_rank.pack(side="right")
        lbl_rank.bind("<Button-1>", lambda event, a=acc: self.open_details_window(a))

    def calculate_time_ago(self, ms):
        if not ms: return "Unknown"
        try:
            diff = datetime.now() - datetime.fromtimestamp(ms / 1000)
            if diff.days == 0: return "Today"
            if diff.days == 1: return "Yesterday"
            return f"{diff.days} days ago"
        except: return "Unknown"

    def update_ranks_from_api(self):
        if not self.api_key:
            print("⚠️ NO API KEY! Open Settings.")
            self.open_settings()
            return

        def fetch():
            self.refresh_btn.configure(state="disabled", text="UPDATING...")
            headers = {"X-Riot-Token": self.api_key}
            for acc in self.accounts:
                try:
                    if "#" not in acc["riot_id"]: continue
                    name, tag = [x.strip() for x in acc["riot_id"].split("#")]
                    server = acc["server"].lower()
                    region = "americas" if server in ["na1", "br1", "la1"] else "europe"
                    
                    print(f"Querying: {name}#{tag}...")
                    r1 = requests.get(f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}", headers=headers)
                    if r1.status_code == 200:
                        puuid = r1.json()['puuid']
                        try:
                            r_matches = requests.get(f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1", headers=headers)
                            if r_matches.status_code == 200 and r_matches.json():
                                r_detail = requests.get(f"https://{region}.api.riotgames.com/lol/match/v5/matches/{r_matches.json()[0]}", headers=headers)
                                if r_detail.status_code == 200: acc['last_seen'] = self.calculate_time_ago(r_detail.json()['info']['gameEndTimestamp'])
                        except: pass
                        
                        r3 = requests.get(f"https://{server}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}", headers=headers)
                        if r3.status_code == 200:
                            found = False
                            for q in r3.json():
                                if q['queueType'] == 'RANKED_SOLO_5x5':
                                    acc.update({"rank_tier": q['tier'], "rank_div": q['rank'], "lp": q['leaguePoints']})
                                    w, l = q['wins'], q['losses']
                                    acc['winrate'] = f"{w}W {l}L ({int(w/(w+l)*100) if w+l>0 else 0}%)"
                                    found = True; break
                            if not found: acc.update({"rank_tier": "UNRANKED", "rank_div": "", "lp": 0, "winrate": ""})
                    elif r1.status_code == 403:
                        print("❌ API Key Expired/Invalid!")
                        self.after(0, lambda: self.refresh_btn.configure(text="INVALID KEY"))
                        return
                except Exception as e: print(e)
                time.sleep(1.2)
            self.save_data()
            self.after(0, lambda: self.filter_accounts(None))
            self.after(0, lambda: self.refresh_btn.configure(state="normal", text="UPDATE RANKS (API)"))
        threading.Thread(target=fetch).start()

if __name__ == "__main__":
    app = LolManagerApp()
    app.mainloop()

# 🏆 League ACC Manager (LoL Rank Tracker)

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Fernet%20Encryption-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

> **[TR]** League of Legends hesaplarınızı tek bir merkezden yönetin, liglerini takip edin ve istatistiklerini görüntüleyin.
>
> **[EN]** Manage your League of Legends accounts from a single hub, track their ranks, and view statistics.

---

## 📸 Screenshots / Ekran Görüntüleri

<div align="center">
  <img src="screenshots/main_ui.png" alt="Main Interface" width="800"/>
</div>
<br/>

| **Add Account / Hesap Ekleme** | **Settings / Ayarlar** | **Edit & Details / Düzenleme** |
|:---:|:---:|:---:|
| <img src="screenshots/add_account.png" width="250"/> | <img src="screenshots/settings.png" width="250"/> | <img src="screenshots/edit_account.png" width="250"/> |

---

## 🇹🇷 TÜRKÇE (Turkish)

### 🌟 Özellikler
* **📊 Rank & LP Takibi:** Riot API üzerinden anlık Lig, Aşama ve LP bilgisini çeker.
* **🎨 Dinamik Arayüz:** Hesabın ligine göre (Gold, Diamond, Challenger vb.) kartların rengi otomatik değişir.
* **📈 Winrate Analizi:** Sezonluk kazanma oranını ve toplam maç sayısını gösterir.
* **🟢 Aktiflik Durumu:** Hesabın en son ne zaman maç attığını analiz eder (Örn: "Bugün", "3 gün önce").
* **🔐 Yüksek Güvenlik:** Şifreleriniz `Fernet` algoritması ile şifrelenerek **sadece sizin bilgisayarınızda** saklanır.
* **📝 Not Sistemi:** Her hesap için "Smurf", "Main", "RP Var" gibi özel notlar alabilirsiniz.
* **⚡ Hızlı Filtreleme:** Hesapları lig sırasına göre (Yüksekten düşüğe) otomatik dizer.

### 🚀 Kurulum

1.  GitHub sayfasının sağ tarafındaki **"Releases"** kısmından en son sürümü (`.zip`) indirin.
2.  ZIP dosyasını klasöre çıkartın.
3.  `app.exe` (Windows) veya `app` (macOS) dosyasını çalıştırın.

### ⚙️ İlk Ayarlar (API Key)
Uygulamanın çalışması için kendi Riot API anahtarınızı girmelisiniz:
1.  Uygulamada sol alttaki **"⚙️ Settings"** butonuna tıklayın.
2.  [developer.riotgames.com](https://developer.riotgames.com) adresinden aldığınız **Personal API Key**'i yapıştırın ve kaydedin.

---

## 🇬🇧 ENGLISH

### 🌟 Features
* **📊 Rank & LP Tracking:** Fetches instant Rank, Tier, and LP info via Riot API.
* **🎨 Dynamic UI:** Card borders change color automatically based on the account's rank (Gold, Diamond, Challenger, etc.).
* **📈 Winrate Analysis:** Displays seasonal winrate and total win/loss counts.
* **🟢 Activity Status:** Shows when the last match was played (e.g., "Today", "3 days ago").
* **🔐 Secure Storage:** Credentials are encrypted locally using `Fernet` encryption.
* **📝 Notes System:** Add custom notes for each account (e.g., "Smurf", "Main").
* **⚡ Smart Sorting:** Automatically sorts accounts by rank (High to Low).

### 🚀 Installation

1.  Download the latest `.zip` from the **"Releases"** section on the right.
2.  Extract the ZIP file.
3.  Run `app.exe` (Windows) or `app` (macOS).

### ⚙️ Configuration (API Key)
You need your own Riot API Key for the app to fetch data:
1.  Click the **"⚙️ Settings"** button at the bottom left.
2.  Paste your **Personal API Key** obtained from [developer.riotgames.com](https://developer.riotgames.com) and save.

---

## 🛠️ For Developers / Geliştiriciler İçin

If you want to run or modify the source code:

```bash
# 1. Clone the repo
git clone [https://github.com/KullaniciAdin/RepoAdin.git](https://github.com/KullaniciAdin/RepoAdin.git)

# 2. Install dependencies
pip install customtkinter requests pillow cryptography

# 3. Run the app
python app.py

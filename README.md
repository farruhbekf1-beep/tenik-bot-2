# 🤖 TECH MAX / JARVIS Telegram Bot (GitHub & Server)

Ushbu loyiha **TECH MAX / JARVIS** xizmatlar markazining Telegram bot kodi bo'lib, GitHub va istalgan bepul yoki pullik bulutli serverlarda (VPS, Railway, Render, Heroku) 24/7 rejimida muammosiz ishlaydi.

---

## 🚀 GitHub'ga Yuklash Va Serverga Joylash Yo'riqnomasi

### 1-Qadam: GitHub Repository Yaratish
1. [GitHub.com](https://github.com) sahifasiga kiring.
2. **`New Repository`** tugmasini bosing.
3. Repozitoriyga nom bering: masalan `techmax-telegram-bot`.
4. Repozitoriyni **Public** yoki **Private** tanlab, **`Create Repository`** tugmasini bosing.
5. Ushbu papkadagi barcha fayllarni (`bot.py`, `requirements.txt`, `Procfile`, `README.md`) GitHub repozitoriyangizga yuklang (Upload files).

---

### 2-Qadam: Serverda Ishga Tushirish (Railway / Render / Heroku / VPS)

#### 🔹 Railway / Render / Heroku orqali (Tavsiya etiladi - Bepul 24/7):
1. [Railway.app](https://railway.app) yoki [Render.com](https://render.com) sahifasiga kiring va GitHub orqali ro'yxatdan o'ting.
2. **`New Project`** -> **`Deploy from GitHub repo`** tanlang va yaratgan `techmax-telegram-bot` repozitoriyangizni ulaysiz.
3. **Environment Variables (Muhit o'zgaruvchilari)** bo'limida quyidagi qiymatlarni kiriting:

| Kalit Nom (Key) | Qiymat (Value) |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather bergan bot tokeni (masalan: `123456:ABC...`) |
| `TECHMAX_ADMIN_USERNAME` | `FARRUHBEKK1` |
| `TECHMAX_ADMIN_PHONE` | `+998943528488` |

4. **Deploy** tugmasini bosing. Bot bir necha soniya ichida avtomatik ishga tushadi! 🚀

---

#### 🔹 VPS Linux Serverda (Ubuntu / Debian):
```bash
# 1. Repozitoriyni ko'chirib olish:
git clone https://github.com/USERNAME/techmax-telegram-bot.git
cd techmax-telegram-bot

# 2. Tokenni o'rnatish va fon rejimida ishga tushirish:
export TELEGRAM_BOT_TOKEN="BOT_TOKENINGIZNI_YOZING"
nohup python3 bot.py &
```

---

## 🛠 Bot Imkoniyatlari
* ⚡ 16 ta Xizmat Sohasi & Aniq Yo'nalishlar
* 📅 Avtomatik Ish Vaqtini Band Qilish (Slots)
* 🛡 To'liq Admin Panel (@FARRUHBEKK1)
* 📢 Barcha Foydalanuvchilarga Reklama Yuborish (Broadcast)
* 📊 Real-vaqt Statistika va Buyurtmalarni Boshqarish
* 🔗 JARVIS Android Ilovasi Bilan Integratsiya (HTTP Bridge API)

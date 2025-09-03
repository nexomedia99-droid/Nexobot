
# NexoBot - Comprehensive Telegram Bot for NexoBuzz Community

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-v20.7-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

NexoBot adalah bot Telegram yang komprehensif untuk platform komunitas NexoBuzz. Bot ini memfasilitasi aplikasi pekerjaan untuk buzzer dan influencer, mengelola registrasi pengguna, menyediakan asisten AI, dan memelihara leaderboard komunitas dengan fitur gamifikasi.

## 🚀 Fitur Utama

### 👥 Manajemen Pengguna
- **Registrasi Multi-step**: Proses pendaftaran lengkap dengan validasi data
- **Edit Profil**: Pengguna dapat mengubah informasi pribadi mereka
- **Sistem Referral**: Program rujukan dengan reward points
- **Validasi Data**: Validasi nomor telepon dan informasi pembayaran

### 💼 Sistem Job & Aplikasi
- **Posting Job**: Admin dapat memposting lowongan buzzer/influencer
- **Aplikasi Job**: Pengguna dapat melamar pekerjaan yang tersedia
- **Tracking Aplikasi**: Monitoring status aplikasi dan pelamar
- **Management Job**: Update dan reset job oleh admin

### 🎮 Gamifikasi & Points
- **Sistem Points**: Earn points melalui berbagai aktivitas
- **Leaderboard**: Ranking pengguna berdasarkan points
- **Badge System**: Achievement badges untuk milestone tertentu
- **Activity Rewards**: Points untuk partisipasi grup dan interaksi

### 📢 Fitur Promosi
- **Promosi Standar**: Post promosi dengan biaya 10 points
- **Promosi Spesial**: Post promosi premium dengan pin (15 points)
- **Auto-delete**: Promosi otomatis terhapus setelah 24 jam
- **Tracking Followers**: Monitor yang mengklik promosi

### 🤖 AI Assistant
- **Google Gemini Integration**: AI chatbot dengan Gemini 2.5 Flash
- **Context Preservation**: Menyimpan konteks percakapan
- **Group Summary**: Rangkuman aktivitas grup
- **Interactive Mode**: Mode chat interaktif di private message

### 📊 Web Dashboard
- **Real-time Monitoring**: Dashboard web untuk statistik bot
- **Analytics**: Grafik dan metrics pengguna
- **Theme Support**: Dark/light theme toggle
- **API Endpoints**: RESTful API untuk data access

### 🔐 Security & Admin
- **Role-based Access**: Kontrol akses berbasis peran
- **Admin Commands**: Command khusus untuk admin
- **Input Validation**: Sanitasi input untuk mencegah serangan
- **Error Handling**: Penanganan error yang robust

## 🛠️ Teknologi Yang Digunakan

- **Python 3.11+**: Bahasa pemrograman utama
- **python-telegram-bot 20.7**: Framework Telegram bot
- **Flask 3.1.1**: Web framework untuk dashboard
- **SQLite**: Database embedded untuk penyimpanan data
- **Google Gemini AI**: AI chatbot integration
- **Chart.js**: Visualisasi data dashboard
- **Bootstrap**: UI framework untuk responsive design

## 📋 Prasyarat

- Python 3.11 atau lebih tinggi
- Telegram Bot Token (dari @BotFather)
- Google Gemini API Key
- Akses ke grup Telegram untuk deploy

## ⚙️ Instalasi & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd nexobot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Buat file `.env` atau set environment variables:

```bash
export BOT_TOKEN="your_telegram_bot_token"
export GEMINI_API_KEY="your_gemini_api_key"
export OWNER_ID="your_telegram_user_id"
export GROUP_ID="your_telegram_group_id"
export GEMINI_MODEL="gemini-2.5-flash"
```

### 4. Inisialisasi Database
Database SQLite akan otomatis dibuat saat pertama kali menjalankan bot.

### 5. Jalankan Bot
```bash
python main.py
```

Bot akan berjalan dengan:
- **Bot Telegram**: Menangani semua command dan interaksi
- **Dashboard Web**: http://0.0.0.0:5000
- **Health Check**: http://0.0.0.0:8080/health

## 📖 Dokumentasi Command

### User Commands
- `/start` - Memulai bot dan menampilkan menu utama
- `/register` - Mendaftar sebagai member (private chat only)
- `/myinfo` - Lihat informasi profil pribadi
- `/editinfo` - Edit informasi profil
- `/myreferral` - Lihat daftar referral
- `/points` - Cek saldo points
- `/leaderboard` - Lihat ranking komunitas
- `/listjob` - Lihat daftar job tersedia
- `/infojob <id>` - Detail informasi job
- `/promote <link>` - Post promosi standar (10 points)
- `/promote_special <link>` - Post promosi spesial (15 points)
- `/cek_followers <promo_id>` - Cek pengklik promosi
- `/help` - Bantuan penggunaan bot

### AI Commands
- `/startai` - Aktifkan mode AI interaktif
- `/stopai` - Nonaktifkan mode AI
- `/ai <text>` - Chat dengan AI (grup)
- `/summary` - Rangkuman aktivitas grup

### Admin Commands
- `/listmember` - Daftar semua member
- `/memberinfo <user_id>` - Info detail member
- `/paymentinfo <user_id>` - Info pembayaran member
- `/delete <user_id>` - Hapus member
- `/addpoint <user_id> <amount>` - Tambah points
- `/resetpoint <user_id>` - Reset points ke 0
- `/addbadge <user_id> <badge_name>` - Tambah badge
- `/resetbadge <user_id>` - Reset semua badge
- `/postjob` - Post job baru
- `/updatejob <id>` - Update job
- `/resetjob <id>` - Reset aplikan job
- `/pelamarjob <id>` - Lihat pelamar job

## 🏗️ Struktur Project

```
nexobot/
├── main.py              # Entry point aplikasi
├── db.py                # Database operations
├── utils.py             # Utility functions
├── dashboard.py         # Web dashboard Flask
├── keep_alive.py        # Health check server
├── start.py             # Start command & menu
├── register.py          # User registration system
├── promote.py           # Promotion system
├── jobs.py              # Job management system
├── ai.py                # AI chatbot integration
├── admin.py             # Admin commands
├── leaderboard.py       # Points & ranking system
├── help.py              # Help system
├── security.py          # Security utilities
├── error_handler.py     # Error handling
├── validators.py        # Input validation
├── decorators.py        # Function decorators
├── static/              # Static files (CSS, JS)
├── templates/           # HTML templates
└── database.db          # SQLite database
```

## 🔧 Konfigurasi

### Database Schema
Bot menggunakan SQLite dengan tabel-tabel:
- `users` - Data pengguna dan profil
- `jobs` - Informasi lowongan pekerjaan
- `applications` - Aplikasi job dari pengguna
- `badges` - System achievement badges
- `promotions` - Data promosi pengguna
- `ai_sessions` - Session AI chat
- `group_messages` - Pesan grup untuk summary

### Topics & Groups
Bot dikonfigurasi untuk bekerja dengan topic-topic tertentu:
- `BUZZER_TOPIC_ID = 3` - Topic untuk job buzzer
- `INFLUENCER_TOPIC_ID = 4` - Topic untuk job influencer
- `PAYMENT_TOPIC_ID = 5` - Topic untuk konfirmasi payment
- `PROMOTE_TOPIC_ID = 11` - Topic untuk promosi

## 🚀 Deployment

### Replit (Recommended)
1. Fork repository ke Replit
2. Set environment variables di Secrets
3. Klik tombol Run

### Manual Deployment
1. Setup server dengan Python 3.11+
2. Install dependencies
3. Set environment variables
4. Jalankan dengan `python main.py`
5. Setup reverse proxy untuk production

## 📊 Monitoring & Analytics

### Web Dashboard
Akses dashboard di http://0.0.0.0:5000 untuk:
- Statistik real-time pengguna
- Grafik aktivitas AI
- Monitor aplikasi job
- System uptime & performance

### Health Checks
- **Health**: http://0.0.0.0:8080/health
- **Status**: http://0.0.0.0:8080/status
- **Ping**: http://0.0.0.0:8080/ping

## 🔒 Keamanan

- Input sanitization untuk mencegah injection
- Role-based access control
- Rate limiting untuk AI requests
- Secure environment variable handling
- Private chat only untuk data sensitif

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request

## 📝 License

Project ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

## 🆘 Support

Untuk bantuan dan support:
- Hubungi admin bot melalui Telegram
- Buat issue di GitHub repository
- Check dashboard untuk monitoring status

## 🔄 Changelog

### v2.0.0
- Added AI integration with Google Gemini
- Web dashboard with real-time analytics
- Enhanced promotion system
- Improved security and validation
- Better error handling and logging

---

**NexoBot** - Powering NexoBuzz Community 🚀

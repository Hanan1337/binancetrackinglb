```markdown
# Binance Leaderboard Tracker

## Deskripsi
Binance Leaderboard Tracker adalah bot Python yang dirancang untuk memantau posisi trading di Binance Futures Leaderboard. Bot ini melacak posisi baru, posisi tertutup, dan posisi saat ini untuk daftar pengguna (encrypted UIDs) yang ditentukan, lalu mengirimkan notifikasi ke Telegram. Bot ini menggunakan API Binance untuk mengambil data posisi dan mendukung fitur seperti mode maintenance untuk pembaruan kode tanpa menghentikan bot.

## Fitur
- Memantau posisi trading (LONG/SHORT) dari pengguna tertentu di Binance Futures Leaderboard.
- Notifikasi real-time ke Telegram untuk posisi baru, tertutup, dan saat ini.
- Perintah Telegram: `/add`, `/remove`, `/list`, `/maintenance`.
- Mode maintenance untuk menjeda pemantauan posisi tanpa menghentikan bot.
- Logging lengkap untuk debugging dan monitoring.

## Prasyarat
Sebelum menjalankan bot, pastikan Anda memiliki:
- **Python 3.8+**: Versi Python yang mendukung `asyncio` dan dependensi lainnya.
- **Dependensi Python**:
  - `aiohttp`: Untuk permintaan HTTP asinkronus ke Binance dan Telegram.
  - `pandas`: Untuk memproses data posisi dalam DataFrame.
- **Akun Telegram**: Untuk membuat bot dan mendapatkan token.
- **Chat ID Telegram**: Untuk mengirim notifikasi.
- **Akses ke Binance Leaderboard**: Pastikan Anda memiliki encrypted UIDs yang valid untuk dimonitor.

## Instalasi

### 1. Clone Repository (Opsional)
Jika kode berada di repository Git, clone ke mesin lokal Anda:
```bash
git clone https://github.com/username/binance-leaderboard-tracker.git
cd binance-leaderboard-tracker
```
Jika tidak, salin semua file ke direktori proyek Anda (misalnya `/home/hanan/binancetrackinglb`).

### 2. Buat Virtual Environment (Opsional tapi Direkomendasikan)
Untuk mengisolasi dependensi:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instal Dependensi
Instal paket Python yang diperlukan:
```bash
pip install aiohttp pandas
```

### 4. Siapkan Struktur Direktori
Pastikan direktori proyek Anda memiliki file berikut:
```
/home/hanan/binancetrackinglb/
├── main.py              # File utama untuk menjalankan bot
├── position_tracker.py  # Logika pemantauan posisi (kode di atas)
├── message.py           # Penanganan perintah Telegram
├── binance.py           # Fungsi untuk mengambil data dari Binance
├── notifier.py          # Pengiriman notifikasi ke Telegram
├── shared.py            # Variabel global
├── constants.py         # Definisi konstan (PositionType, Emoji)
├── maintenance.py       # Mode maintenance (opsional)
├── config.ini           # File konfigurasi
├── user_addresses.json  # Daftar UID yang dipantau
└── bot.log              # File log (dibuat saat bot berjalan)
```

## Konfigurasi

### 1. Buat File `config.ini`
Buat file `config.ini` di direktori proyek dengan isi berikut:
```ini
[general]
polling_interval = 30
account_info_url_template = https://www.binance.com/en/futures-activity/leaderboard/user/um?encryptedUid={}

[telegram]
bottoken = YOUR_TELEGRAM_BOT_TOKEN
chatid = YOUR_CHAT_ID
admins = YOUR_ADMIN_CHAT_ID

[telegram_messages]
new_position_template = ⚠️ 【<b>{nickName}</b>】\n❇️ New position opened\n\n<u><b>Position: {symbol} {position} {leverage}X</b></u>\n\nBase currency - USDT\n━━━━━━━━━━━━━━━━\n🎯 <b>Entry Price:</b> {entry_price}\n💰 <b>Est. Entry Size:</b> {position_value:.5f}\n{pnl_emoji} <b>PnL:</b> {pnl}\n━━━━━━━━━━━━━━━━\n\n<b>Last Update:</b>\n{update_time}\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>
closed_position_template = ⚠️ 【<b>{nickName}</b>】\n⛔️ <u><b>Position closed</b></u>\n\n<b>Position:</b> {symbol} {position} {leverage}X\n\n💵 <b>Current Price:</b> {current_price} USDT\n<b>Last Update:</b>\n{update_time}\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>
current_positions_template = ⚠️ 【<b>{nickName}</b>】\n💎 Current positions:\n\n<b><u>Position: {symbol} {position} {leverage}X</u></b>\n\nBase currency - USDT\n━━━━━━━━━━━━━━━━━\n🎯 <b>Entry Price:</b> {entry_price}\n💰 <b>Est. Entry Size:</b> {position_value:.5f}\n{pnl_emoji} <b>PnL:</b> {pnl}\n━━━━━━━━━━━━━━━━━\n\n<b>Last Update:</b>\n{update_time}\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>
```
Ganti:
- `YOUR_TELEGRAM_BOT_TOKEN`: Dapatkan dari BotFather di Telegram.
- `YOUR_CHAT_ID`: ID chat tempat notifikasi dikirim (gunakan bot seperti @userinfobot untuk mendapatkannya).
- `YOUR_ADMIN_CHAT_ID`: ID admin yang diizinkan mengendalikan bot (pisahkan dengan koma jika lebih dari satu, misalnya `-123456789,987654321`).

### 2. Inisialisasi `user_addresses.json`
Buat file `user_addresses.json` untuk menyimpan daftar encrypted UIDs yang akan dipantau:
```json
[]
```
Tambahkan UID nanti melalui perintah Telegram `/add`.

## Cara Menjalankan

### 1. Pastikan Semua File Siap
Verifikasi bahwa semua file ada di direktori proyek dan `config.ini` sudah dikonfigurasi.

### 2. Jalankan Bot
Dari terminal, jalankan:
```bash
python /home/hanan/binancetrackinglb/main.py
```
Bot akan mulai memantau posisi dan mendengarkan perintah Telegram. Log akan ditulis ke `bot.log` di direktori yang sama.

### 3. Gunakan Perintah Telegram
Kirim perintah ke bot Telegram Anda:
- `/add <encryptedUid>`: Tambahkan UID ke daftar pemantauan (contoh: `/add 782DDDD51145467F6B3C3844C4D9F78F`).
- `/list`: Tampilkan daftar UID yang dipantau.
- `/remove <index>`: Hapus UID berdasarkan indeks dari daftar (contoh: `/remove 0`).
- `/maintenance`: Toggle mode maintenance untuk menjeda pemantauan posisi.

## Struktur File
- `main.py`: Titik masuk utama, mengatur pemantauan posisi dan polling Telegram.
- `position_tracker.py`: Memantau dan memproses posisi trading dari Binance.
- `message.py`: Menangani perintah Telegram dan pembaruan UID.
- `binance.py`: Berisi fungsi untuk mengambil data dari Binance Leaderboard.
- `notifier.py`: Mengirim notifikasi ke Telegram.
- `shared.py`: Menyimpan variabel global seperti `TARGETED_USER_ADDRESSES` dan `USER_NICKNAMES`.
- `constants.py`: Definisi konstan seperti `PositionType` (LONG/SHORT) dan Emoji (PROFIT/LOSS).
- `maintenance.py`: Mengelola mode maintenance (opsional).
- `config.ini`: Konfigurasi bot (token, chat ID, template pesan).
- `user_addresses.json`: Daftar UID yang dipantau.
- `bot.log`: File log untuk debugging.

## Contoh Output di Telegram
```
⚠️ 【<b>mason会发财</b>】
💎 Current positions:

<u><b>Position: ETHUSDT LONG 20X</b></u>

Base currency - USDT
━━━━━━━━━━━━━━━━━
🎯 <b>Entry Price:</b> 2095.299181115
💰 <b>Est. Entry Size:</b> 1496536.95627
🔴 <b>PnL:</b> -4994.24759786
━━━━━━━━━━━━━━━━━

<b>Last Update:</b>
2025-03-04 08:31:34
<b><a href='https://www.binance.com/en/futures-activity/leaderboard/user/um?encryptedUid=782DDDD51145467F6B3C3844C4D9F78F'>VIEW PROFILE ON BINANCE</a></b>
```
**Catatan:** Waktu ditampilkan apa adanya dari Binance (UTC) karena konversi ke UTC+7 dihapus.

## Troubleshooting

### Bot Tidak Berjalan
- **Periksa Log**: Buka `bot.log` untuk melihat error (contoh: `/home/hanan/binancetrackinglb/bot.log`).
- **Dependensi Hilang**: Pastikan `aiohttp` dan `pandas` terinstal (`pip list`).
- **Konfigurasi Salah**: Verifikasi `config.ini` memiliki token dan chat ID yang benar.

### Error 'PositionTracker' object has no attribute 'track_positions'
- Pastikan `position_tracker.py` adalah versi terbaru dengan metode `track_positions`.
- Bersihkan cache:
  ```bash
  rm -rf /home/hanan/binancetrackinglb/__pycache__
  ```
- Periksa impor di `main.py`:
  ```python
  from position_tracker import PositionTracker
  ```

### Waktu Tidak Sesuai
Karena konversi waktu dihapus, waktu akan ditampilkan dalam UTC (misalnya 08:31:34 untuk 2025-03-04 08:31:34 UTC). Jika Anda ingin WIB (UTC+7), beri tahu saya untuk mengembalikan konversi.

### Notifikasi Tidak Terkirim
- Pastikan `bottoken` dan `chatid` di `config.ini` valid.
- Uji koneksi Telegram:
  ```bash
  curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
  ```

## Kontribusi
Jika Anda ingin menambahkan fitur atau memperbaiki bug:
1. Fork repository (jika ada).
2. Buat branch baru (`git checkout -b feature/nama-fitur`).
3. Commit perubahan (`git commit -m "Menambahkan fitur X"`).
4. Push ke branch (`git push origin feature/nama-fitur`).
5. Buat pull request.

## Lisensi
Proyek ini bersifat open-source di bawah lisensi MIT (atau sesuaikan dengan preferensi Anda).
```

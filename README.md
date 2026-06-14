[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4SHtB1vz)

# Final Project: CipherTalk

## Anggota Kelompok D-11
| Name           | NRP        | Kelas     |
| ---            | ---        | ---|
| Yasmina Fitri Azizah | 5025241039 | Pemrograman Jaringan D |
| Kinanti Ayu Caesandria | 5025241047 | Pemrograman Jaringan D |

## [Link Demo](https://drive.google.com/file/d/1TLTMeEb8boF2cVXbT1GEc15iXC7foJet/view?usp=sharing)

## server.py
  Kode `server.py` berguna untuk meneruskan pesan (broadcast & whisper), menyimpan list forum & histori broadcast, membuat & memverifikasi kode OTP, dan menerapkan
  mekanisme anti-spam (limit karakter, limit bubble chat, limit pembuatan forum). Untuk mengimplementasikan hal-hal tadi, `server.py` memiliki berbagai _function_ yaitu :
### load_database()
```
db_lock = threading.Lock() #global
with db_lock:
```
berguna untuk memastikan hanya 1 thread yang mengakses database
```
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
```
akan membuka file dalam mode read dan melakukan konversi datanya ke dalam dictionary python
```            
            limit_date = datetime.now() - timedelta(days=7)
            cleaned_rooms = {}
            
            for room_name, chat_history in data.get("rooms", {}).items():
                valid_chats = []
                for chat in chat_history:
                    # Cek timestamp tiap chat
                    chat_time = datetime.strptime(chat['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if chat_time > limit_date:
                        valid_chats.append(chat)
                cleaned_rooms[room_name] = valid_chats
            
            return {"rooms": cleaned_rooms}
```
akan mengecek chat yang masih belum lewat `limit_date` dan menyimpannya ke dalam `valid_chat`

### save_database()
```
with db_lock:
```
berguna untuk memastikan hanya 1 thread yang mengakses database dalam 1 waktu, sehingga tidak ada race condition dengan load_database
```
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
```
akan membuka file dalam mode read dan melakukan konversi dictionary python ke JSON

### generate_alias()
```
FIRST = ["Melon", "Jeruk", "Apel", "Mangga", "Anggur", "Nanas", "Pepaya", "Berry", "Semangka", "Kiwi", "Durian", "Sirsak", "Lemon", "Ceri", "Alpukat", "Jambu"]
STRINGS = string.ascii_uppercase + string.digits
...
    alias = f"{random.choice(FIRST)}{random.choice(STRINGS)}{random.choice(STRINGS)}{random.choice(STRINGS)}"
```
mengkonstruksikan format alias, yaitu nama buah + 3 karakter alfanumerik
```
while True:
    ...
    if all(info["alias"] != alias for info in clients.values()):
        return alias
```
mengiterasikan alias generation hingga nilainya unik/tidak sama dengan user lain

### broadcast_to_room()
```
packet = (json.dumps(message_dict) + "\n").encode('utf-8')
```
melakukan encoding pesan dalam dictionary ke dalam JSON dengan `\n` sebagai delimiter
```
for client_socket in rooms_sockets.get(room_name, []):
    if client_socket != sender_socket:
        try:
            client_socket.sendall(packet)
```
akan mencari ruangan forum yang sesuai dan mengirim paket tersebut ke semua user di dalam forum kecuali kepada pengirim pesan
```
        except Exception as e:
            print(f"Broadcast error: {e}")
            handle_disconnect(client_socket)
```
untuk menghandle apabila suatu user tidak dapat menerima pesan. Server akan menganggap terdapat masalah pada koneksi user
dan melakukan diskoneksi

### handle_disconnect()
```
if client_socket in clients:
    user_info = clients[client_socket]
    alias = user_info["alias"]
    nrp = user_info["nrp"]
    room = user_info["current_room"]
```
untuk memastikan user yang ingin diputus koneksinya benar-benar masih terhubung
``` 
    if room in rooms_sockets and client_socket in rooms_sockets[room]:
        rooms_sockets[room].remove(client_socket)
```
untuk menghapus user tersebut dari daftar user di suatu ruangan
```
    exit_notification = {
        "status": "info",
        "sender_alias": "SISTEM",
        "timestamp": "INFO",
        "message": f"Pengguna [{alias}] telah keluar dari forum."
    }
    broadcast_to_room(room, client_socket, exit_notification)
```
memberi notifikasi ke user lain di ruangan bahwa user tersebut keluar
```
    del clients[client_socket]
    try:
        client_socket.close()
    except:
        pass
```
menghapus user dari online list dan menutup koneksi
```
    log_msg = f"NRP {nrp} ({alias}) terputus dari jaringan."
    print(f"[DISCONNECT] {log_msg}")
    logging.info(log_msg)
```
menulis log

### handle_client()
Fungsi ini dapat dibagi menjadi dua fase, yaitu sebelum dan sesuda user ter-autentikasi
- fase 1 
```
if command == "login":
    ...
    if not re.match(r"^\d{10}$", input_nrp):
      ...
    elif any(info["nrp"] == input_nrp for info in clients.values()):
      ...
    elif input_nrp in locked_accounts:
      ...
```
melakukan validasi format nrp dan memastikan nrp tersebut belum login dan masih memiliki kesempatan untuk meminta kode nrp untuk waktu itu
```
    else:
        otp = str(secrets.randbelow(900000) + 100000)
        pending_logins[input_nrp] = {
            "otp_hash": hashlib.sha256(otp.encode()).hexdigest(),
            "expires_at": datetime.now() + timedelta(minutes=5),
            "attempts": 0
        }

        email = f"{input_nrp}@student.its.ac.id"
        # TODO: kirim OTP ke email its
        print(f"[OTP DEBUG] OTP untuk {email}: {otp}")
        ...
```
men-generate OTP untuk login
```
elif command == "verify_otp":
    ...
    if input_nrp not in pending_logins:
        ...
    else:
        ...
        if datetime.now() > record["expires_at"]:
            ...
        elif record["attempts"] >= 5:
            ...
        elif hashlib.sha256(input_otp.encode()).hexdigest() != record["otp_hash"]:
            ...
        else:
            ...
```
memverifikasi apakah OTP masih berlaku, belum melewati batas percobaan, dan sesuai dengan yang dibuat/dikirim server

- fase 2
```
if command == "broadcast":
  ...
elif command == "create":
  ...
elif command == "join":
  ...
elif command == "whisper":
  ...
elif command == "leave":
  ...
elif command == "list":
  ...
elif command == "online":
  ...
```
handling fitur-fitur yang dapat digunakan user saat terkoneksi dan terautentikasi

### start_server()
```
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
koneksi menggunakan TCP dengan IPv4
```
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```
jika server di restart, maka port yang sama dapat dipakai kembali tanpa menunggu expired
```
server.bind((HOST, PORT))
server.listen()
print(f"[START] Server CipherTalk aktif mendengarkan di {HOST}:{PORT}")
logging.info(f"Server CipherTalk diaktifkan pada {HOST}:{PORT}")
```
server akan mendengarkan pesan masuk dari HOST=localhost dan PORT=7002
```
while True:
    client_socket, client_address = server.accept()
    print(f"[CONNECTION] Koneksi fisik masuk dari {client_address}")
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    ...
    thread.start()
```
mengalokasikan 1 thread untuk setiap 1 koneksi user dan 
```
    thread.daemon = True
```
memastikan worker thread akan mati apabila proses utama server mati 

## gui.py

### Fitur Utama Antarmuka
* **Dynamic Screen Transition:** Sistem satu jendela (*single-window*) yang membersihkan kontainer secara dinamis untuk berpindah modul layar (Login $\rightarrow$ OTP $\rightarrow$ Chat Room).
* **Asynchronous Server Listening:** Memanfaatkan *worker thread* terpisah untuk mendengarkan paket data masuk dari server tanpa memblokir (*freezing*) responsivitas GUI.
* **Input Constraint & Live Counter:** Pembatasan masukan teks maksimal 100 karakter yang divalidasi langsung melalui komponen *live character counter*.
* **One-Click Emoji Toolbar:** Aksesibilitas cepat untuk menyisipkan emoji ke dalam kolom obrolan dengan satu klik mouse.


### Alur dan Logika Modul Kode

#### 1. Inisialisasi dan Manajemen Jendela
Saat kelas `CipherTalkClientGUI` diinstansiasi, sistem mengonfigurasi dimensi dasar jendela sebesar **800x600** piksel dan menyiapkan sebuah komponen `tk.Frame` utama sebagai kontainer induk.
* `clear_container()`: Fungsi utilitas krusial yang mendeteksi seluruh komponen anak (*widgets*) di dalam kontainer menggunakan properti `.winfo_children()`, lalu menghancurkannya (`widget.destroy()`). Metode ini memastikan efisiensi penggunaan memori RAM saat aplikasi melakukan transisi halaman.

#### 2. Alur Autentikasi
Proses masuk jaringan dibagi menjadi dua tahap sekuensial yang aman:
* **Fase NRP**: Mengharuskan masukan berupa 10 digit numerik murni. Jika valid, soket TCP diinisialisasi (`socket.SOCK_STREAM`) dan melakukan jabat tangan awal ke server dengan mengirimkan paket instruksi berbentuk JSON:
  ```
  {"command": "login", "payload": "50252410XX"}
  ```

* **Fase OTP**: Jika server membalas dengan status `otp_sent`, kontainer beralih ke layar kode OTP. Masukan disamarkan menggunakan parameter `show="*"`. Kode dikirim kembali dalam format:
  ```
  {"command": "verify_otp", "nrp": "50252410XX", "payload": "XXXXXX"}
  ```

#### 3. Jendela Utama Obrolan & Panel Kontrol

Setelah otorisasi sukses, layar obrolan dibangun menggunakan konfigurasi tata letak grid (`columnconfigure`) yang membagi area menjadi dua segmen utama:

* **Sisi Kiri (Area Komunikasi):** Mengintegrasikan komponen *scrolled-text* yang dikunci dalam mode `tk.DISABLED` agar riwayat chat bersifat *read-only* dan tidak dapat dimodifikasi secara tidak sengaja oleh pengguna. Kunci dibuka sementara hanya lewat fungsi `append_chat()` saat ada string data pesan baru masuk.
* **Sisi Kanan (Panel Kontrol Grafis):**
Bertindak sebagai abstraksi perintah teks soket. Setiap tombol mengikat fungsi `send_action_packet()` atau memicu dialog pop-up untuk membungkus perintah ke dalam skema JSON terstruktur sebelum dilempar ke jaringan:
* **Daftar Forum**: `{"command": "list"}`
* **Buat Forum**: `{"command": "create", "payload": "<nama_room>"}`
* **Masuk Forum**: `{"command": "join", "payload": "<nama_room>"}`
* **Cek User Online**: `{"command": "online"}`
* **Chat Privat (Whisper)**: `{"command": "whisper", "target": "<alias_target>", "payload": "<pesan>"}`


### Mekanisme Konkurensi & Manajemen Paket Data

#### Asynchronous Threading 

Apabila proses login berhasil, GUI akan langsung memicu sebuah komponen *background thread* independen melalui perintah:

```python
threading.Thread(target=self.listen_from_server, daemon=True).start()

```

Properti `daemon=True` menjamin bahwa ketika jendela aplikasi GUI utama ditutup oleh pengguna, *thread* latar belakang ini akan langsung ikut mati secara otomatis, mencegah terjadinya proses menggantung di sistem operasi.

* Worker thread ini berjalan di dalam perulangan `while self.is_running:` untuk terus menangkap data streaming dari jaringan.
* Karena TCP bersifat *stream-based*, fungsi ini memanfaatkan mekanisme penyangga buffer string untuk menampung serpihan paket data. Pemisahan paket dilakukan secara akurat berbasis pemisah baris baru (`\n`) sebelum diurai kembali menjadi kamus data objek via `json.loads(line)`.
* Jika koneksi ke server terputus mendadak, *catch block* akan menangkap kegagalan tersebut dan mengarahkan antarmuka untuk memicu fungsi `disable_inputs()`, yang bertugas mengunci kolom entri dan tombol kirim agar pengguna tidak dapat mengirimkan pesan kosong (pesan hantu).


### Detail Interaktivitas & Aksesibilitas UI

* **Live Character Counter**: Fungsi ini terikat dengan aksi pengetikan di keyboard (<KeyRelease>). Jika panjang teks melewati ambang 100 karakter, label indikator akan otomatis berubah warna menjadi merah sebagai pembatas visual bagi pengguna.
* **Emoji Insertion Control**: Ketika salah satu tombol emoji ditekan, fungsi ini akan menyisipkan karakter Unicode emoji ke titik kursor aktif saat ini berada (`tk.INSERT`), memperbarui jumlah karakter secara real-time, dan mengembalikan fokus pengetikan kembali ke kolom teks utama (`self.msg_entry.focus_set()`) agar alur mengetik pengguna tidak terputus.

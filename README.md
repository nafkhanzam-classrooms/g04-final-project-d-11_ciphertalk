[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4SHtB1vz)

# Final Project: CipherTalk

## Anggota Kelompok D-11
| Name           | NRP        | Kelas     |
| ---            | ---        | ---|
| Yasmina Fitri Azizah | 5025241039 | Pemrograman Jaringan D |
| Kinanti Ayu Caesandria | 5025241047 | Pemrograman Jaringan D |

## [Link Demo](https://drive.google.com/file/d/1TLTMeEb8boF2cVXbT1GEc15iXC7foJet/view?usp=sharing)

## server.py

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

* **Sisi Kiri (Area Komunikasi):** Mengintegrasikan komponen `scrolledtext.ScrolledText` yang dikunci dalam mode `tk.DISABLED` agar riwayat chat bersifat *read-only* dan tidak dapat dimodifikasi secara tidak sengaja oleh pengguna. Kunci dibuka sementara hanya lewat fungsi `append_chat()` saat ada string data pesan baru masuk.
* **Sisi Kanan (Panel Kontrol Grafis):**
Bertindak sebagai abstraksi perintah teks soket. Setiap tombol mengikat fungsi `send_action_packet()` atau memicu dialog pop-up (`simpledialog.askstring`) untuk membungkus perintah ke dalam skema JSON terstruktur sebelum dilempar ke jaringan:
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

Properti `daemon=True` menjamin bahwa ketika jendela aplikasi GUI utama ditutup oleh pengguna, *thread* latar belakang ini akan langsung ikut mati secara otomatis, mencegah terjadinya proses menggantung (*zombie process*) di sistem operasi.

* Worker thread ini berjalan di dalam perulangan `while self.is_running:` untuk terus menangkap data streaming dari jaringan.
* Karena TCP bersifat *stream-based*, fungsi ini memanfaatkan mekanisme penyangga `buffer` string untuk menampung serpihan paket data. Pemisahan paket dilakukan secara akurat berbasis pemisah baris baru (`\n`) sebelum diurai kembali menjadi kamus data objek via `json.loads(line)`.
* Jika koneksi ke server terputus mendadak, *catch block* akan menangkap kegagalan tersebut dan mengarahkan antarmuka untuk memicu fungsi `disable_inputs()`, yang bertugas mengunci kolom entri dan tombol kirim agar pengguna tidak dapat mengirimkan pesan hantu (*ghost messages*).


### Detail Interaktivitas & Aksesibilitas UI

* **Live Character Counter**: Fungsi ini terikat dengan aksi pengetikan di keyboard (`<KeyRelease>`). Jika panjang teks di dalam komponen `msg_entry` melewati ambang 100 karakter, label indikator akan otomatis berubah warna menjadi merah (`fg="red"`) sebagai pembatas visual (*constraint warning*) bagi pengguna.
* **Emoji Insertion Control**: Ketika salah satu tombol emoji ditekan, fungsi ini akan menyisipkan karakter Unicode emoji ke titik kursor aktif saat ini berada (`tk.INSERT`), memperbarui jumlah karakter secara real-time, dan mengembalikan fokus pengetikan kembali ke kolom teks utama (`self.msg_entry.focus_set()`) agar alur mengetik pengguna tidak terputus.

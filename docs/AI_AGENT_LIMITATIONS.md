# Penanganan Error & Batasan Agen AI Eksternal (vs IDE Built-in)

Dokumen ini mencatat beberapa batasan teknis saat bekerja menggunakan agen AI eksternal dibandingkan dengan agen AI yang terintegrasi langsung ke dalam IDE Anda (seperti Windsurf, Cursor, atau GitHub Copilot).

## 1. Konflik Tarik-Menarik dengan Auto-Formatter IDE (Prettier, Beautify, dll.)

**Deskripsi Masalah:**
Agen AI eksternal mengedit file dengan cara membaca dan menulis teks mentah secara langsung ke sistem (File System). Ketika file disimpan, fitur **Auto-Format on Save** yang aktif di text editor/IDE Anda akan langsung memproses ulang file tersebut. 

Terkadang, formatter IDE secara agresif akan memecah baris kode yang dianggap "terlalu panjang". Pada file berjenis template seperti Django HTML, hal ini bisa mengakibatkan tag khusus seperti `{% if %}` terpotong menjadi dua baris `{% \n if %}`, yang akan memicu `TemplateSyntaxError`. Agen eksternal tidak memiliki akses untuk "mematikan sementara" formatter di IDE Anda.

**Kapan Sebaiknya Beralih ke Windsurf / Cursor:**
* Apabila Anda terjebak dalam masalah `TemplateSyntaxError` (tag terputus) atau *syntax error* serupa yang tak kunjung selesai.
* Apabila indentasi atau pelurusan elemen HTML terus kembali berantakan setiap kali agen eksternal selesai mengedit.
* AI built-in IDE beroperasi langsung di dalam _buffer memory_ editor, sehingga bisa mem-_bypass_ atau bekerja selaras dengan formatter.

## 2. Modifikasi Kode yang Belum Disimpan (Unsaved Changes) & Linter

**Deskripsi Masalah:**
Agen eksternal hanya bisa membaca kode yang sudah tersimpan di *hard drive* (disk). Jika Anda sedang mengetik sesuatu di layar dan belum menekan `Ctrl+S`, agen eksternal tidak mengetahuinya. Ia juga tidak bisa "melihat" peringatan garis bergelombang merah (*diagnostic linter errors*) yang muncul langsung dari ekstensi IDE Anda.

**Kapan Sebaiknya Beralih ke Windsurf / Cursor:**
* Jika Anda ingin memblok (highlight) beberapa baris kode yang belum di-save dan bertanya "Tolong betulkan bagian yang kublok ini".
* Jika menyelesaikan masalah linter instan yang muncul seketika di layar Anda.

## 3. Interaksi Terminal yang Kompleks (Interactive Shells)

**Deskripsi Masalah:**
Meskipun agen eksternal sangat ahli menjalankan skrip shell, perintah Docker, pencarian file, dan membaca log, ia bisa kesulitan jika sebuah perintah membutuhkan interaksi antarmuka (UI) keyboard yang spesifik secara langsung (seperti memilih opsi dengan tombol panah pada CLI interaktif).

---

### 💡 Kesimpulan Penggunaan:

* **Gunakan Agen AI Eksternal Untuk:** Pekerjaan otonom, *heavy lifting* dan terstruktur. Mengaudit arsitektur database, memperbaiki logika backend kompleks, mengatur *deployment scripting*, merombak beberapa file sekaligus secara buta, serta investigasi error dari akses log Docker container.
* **Gunakan Windsurf / Cursor IDE Untuk:** Koreksi mikro (*micro-edits*), perbaikan *layout/UI* HTML yang sangat dipengaruhi oleh pemformatan otomatis (auto-formatter), menanyakan baris kode spesifik yang sedang Anda kelola di layar, atau koreksi sintaks instan berbasis linter IDE.

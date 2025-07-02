
# Proyek Grafika Komputer Interaktif: PyOpenGL & Web Control Panel 2D

[![Python Version](https://img.shields.io/badge/Python-3.x%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-green.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Graphics API](https://img.shields.io/badge/Graphics%20API-PyOpenGL-orange.svg?style=for-the-badge&logo=opengl&logoColor=white)](http://pyopengl.sourceforge.net/)
[![UI/UX](https://img.shields.io/badge/UI%2FUX-HTML%2FCSS%2FJS-red.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)


---

Selamat datang di Proyek Grafika Komputer Interaktif! Aplikasi inovatif ini membawa konsep-konsep grafika 2D ke level selanjutnya dengan kombinasi PyOpenGL yang kuat dan panel kontrol berbasis web yang cantik serta intuitif. Dibuat khusus untuk memenuhi persyaratan tugas besar mata kuliah Grafika Komputer, proyek ini adalah bukti nyata sinergi antara aplikasi desktop grafis berkinerja tinggi dan antarmuka pengguna web modern.

## Daftar Isi

* [Gambaran Umum Proyek](#gambaran-umum-proyek)
* [Fitur Unggulan](#fitur-unggulan)
* [Teknologi yang Digunakan](#teknologi-yang-digunakan)
* [Struktur Proyek](#struktur-proyek)
* [Persyaratan Sistem](#persyaratan-sistem)
* [Panduan Instalasi](#panduan-instalasi)
* [Cara Menjalankan Program](#cara-menjalankan-program)
* [Panduan Penggunaan](#panduan-penggunaan)
* [Potensi Pengembangan Lanjutan](#potensi-pengembangan-lanjutan)

---

## Gambaran Umum Proyek

Proyek ini mendefinisikan ulang interaksi dalam aplikasi grafika komputer. Alih-alih antarmuka tradisional, kami memisahkan rendering grafis berkinerja tinggi (dihandle oleh PyOpenGL sebagai aplikasi desktop native) dari pengalaman pengguna (disajikan melalui panel kontrol berbasis web yang ramah pengguna). Komunikasi real-time antara kedua dunia ini diwujudkan melalui server Python Flask yang efisien dan komunikasi socket yang cepat.

Pendekatan arsitektur *hybrid* ini tidak hanya memenuhi standar akademis tetapi juga membuka pintu bagi pengalaman pengguna yang lebih fleksibel, modern, dan demonstrasi konsep grafika yang lebih interaktif.

## Fitur Unggulan

### A. Objek 2D Dasar & Pengaturan Visual

* **Menggambar Primitif:** Buat Titik, Garis, Segitiga, Elips, dan Persegi dengan mudah melalui klik mouse langsung di jendela grafis.
* **Kustomisasi Visual:** Atur **Warna** objek (RGB) dan **Ketebalan Garis** (atau ukuran titik) menggunakan slider dan pemilih warna yang responsif di panel web. Perubahan dapat diterapkan pada objek baru atau objek yang sedang terpilih!
* **Input Mouse:** Semua operasi gambar dan interaksi dikendalikan secara intuitif melalui klik mouse.

### B. Transformasi Geometris Interaktif

* **Translasi (Pergeseran):** Pindahkan objek terpilih di sepanjang sumbu X dan Y menggunakan slider di panel web.
* **Rotasi:** Putar objek terpilih menggunakan slider sudut rotasi.
* **Skala (Perubahan Ukuran):** Sesuaikan ukuran objek terpilih secara independen di sumbu X dan Y menggunakan slider skala.
* **Reset Cepat:** Satu tombol untuk mengembalikan semua transformasi objek yang terpilih ke kondisi awalnya (posisi asli, rotasi 0, skala 100%).

### C. Windowing & Clipping Canggih

* **Definisi Jendela Clipping:** Tentukan area tampilan aktif dengan dua klik mouse di jendela OpenGL. Batas jendela terlihat jelas dengan *outline* cyan.
* **Algoritma Cerdas:**
    * **Cohen-Sutherland:** Digunakan untuk memotong garis dan segmen elips.
    * **Sutherland-Hodgman:** Digunakan untuk memotong poligon (segitiga dan persegi), memastikan hanya bagian yang terlihat yang dirender.
* **Kontrol Toggle:** Aktifkan atau nonaktifkan fitur clipping dengan mudah dari panel web.
* **Geser Jendela Clipping:** Pindahkan jendela clipping secara halus dengan *drag-and-drop* mouse, memberikan kontrol dinamis atas area pandang.

### D. Integrasi & Interaktivitas Seamless

* **Pemilihan Objek Intuitif:** Klik objek di jendela grafis (dalam mode seleksi) untuk memilihnya. Objek yang terpilih akan ditandai dengan **highlight kuning** yang jelas.
* **Panel Kontrol Web Modern:** Antarmuka pengguna yang *user-friendly* dan responsif, dirancang dengan HTML, CSS, dan JavaScript, memungkinkan Anda mengendalikan semua fitur dengan mudah dari browser Anda.
* **Komunikasi Real-time:** Berkat arsitektur Flask dan socket, setiap penyesuaian di panel web langsung tercermin di jendela grafis PyOpenGL Anda, menciptakan pengalaman yang *live* dan interaktif.
* **Penghapusan Objek Individual:** Hapus objek yang sedang terpilih dengan mudah melalui tombol di panel kontrol web.

---

## Teknologi yang Digunakan

* **Python 3.x:** Tulang punggung proyek.
    * `PyOpenGL`: Jembatan ke dunia grafika OpenGL.
    * `Flask`: Micro-framework web ringan untuk API dan panel kontrol.
    * `Flask-Cors`: Memastikan komunikasi web lintas-origin berjalan lancar.
    * `Pygame` / `FreeGLUT`: Digunakan oleh PyOpenGL untuk manajemen jendela dan penanganan event dasar.
* **HTML5:** Struktur dasar antarmuka pengguna web.
* **CSS3:** Styling modern untuk panel kontrol web yang estetis.
* **JavaScript:** Memberikan interaktivitas dinamis di sisi klien (browser).

## Struktur Proyek

Organisasi kode yang bersih dan modular untuk navigasi yang mudah:

```

my\_graphics\_project/
├── main.py                 \# Logika inti aplikasi (PyOpenGL + Flask backend)
└── static/                 \# Folder untuk aset web statis (HTML, CSS, JS)
   ├── index.html          \# Halaman utama panel kontrol web
   ├── style.css           \# Styling khusus untuk panel kontrol
   └── script.js           \# Logika interaktif sisi klien untuk panel kontrol

````

## Persyaratan Sistem

Untuk menjalankan aplikasi ini dengan lancar, pastikan Anda memiliki:

* **Sistem Operasi:** Windows 10/11, macOS, atau distribusi Linux yang kompatibel.
* **Python:** Python 3.x terinstal (disarankan versi terbaru untuk performa dan keamanan).
* **Koneksi Internet:** Diperlukan untuk mengunduh dependensi awal.
* **Browser Web Modern:** Google Chrome, Mozilla Firefox, Microsoft Edge, dll., untuk mengakses panel kontrol.

## Panduan Instalasi

Ikuti langkah-langkah mudah ini untuk menyiapkan dan menjalankan proyek di lingkungan lokal Anda:

1.  **Unduh atau Kloning Repositori:**
    ```bash
    git clone [https://github.com/USERNAME_ANDA/NAMA_REPO_ANDA.git](https://github.com/USERNAME_ANDA/NAMA_REPO_ANDA.git) # Ganti dengan URL repo Anda
    cd NAMA_REPO_ANDA # Atau nama folder jika Anda mengunduh ZIP
    ```
    *(Jika Anda mengunduh file ZIP, pastikan struktur folder `my_graphics_project/main.py` dan `my_graphics_project/static/` sudah benar.)*

2.  **Instal Dependensi Python:**
    Buka Terminal atau Command Prompt Anda. **Pastikan `python` dan `pip` dikenali di PATH sistem Anda.** (Jika tidak, Anda mungkin perlu menambahkan Python ke PATH secara manual atau menggunakan `python -m pip install...`).

    Navigasikan ke direktori proyek Anda (`my_graphics_project`):
    ```bash
    cd path/to/my_graphics_project
    ```
    Jalankan perintah instalasi dependensi:
    ```bash
    pip install pygame PyOpenGL PyOpenGL_accelerate Flask Flask-Cors
    ```
    *(Jika `pip` tidak dikenali, coba `python -m pip install ...` atau `py -m pip install ...`)*

## Cara Menjalankan Program

Setelah instalasi selesai, meluncurkan aplikasi sangat sederhana:

1.  **Buka Terminal/Command Prompt:**
    * Pastikan Anda berada di direktori proyek (`my_graphics_project`).

2.  **Jalankan Aplikasi Python:**
    ```bash
    python main.py
    ```
    * Aplikasi ini akan memulai **dua komponen esensial**:
        1.  Sebuah jendela aplikasi grafis PyOpenGL akan muncul di desktop Anda. Ini adalah kanvas visual Anda.
        2.  Server web Flask akan mulai berjalan di latar belakang, bertindak sebagai *API gateway* dan penyedia panel kontrol.
    * Di terminal, Anda akan melihat pesan log yang mengindikasikan server telah dimulai, termasuk alamat URL untuk panel kontrol web:
        ```
        INFO - Aplikasi PyOpenGL siap. Silakan buka panel kontrol web Anda di browser.
        INFO - Memulai Web Control Panel Flask...
        INFO - Panel Kontrol Web dapat diakses di: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
        ```
    * **Penting:** Biarkan terminal ini tetap terbuka selama Anda menggunakan aplikasi. Menutupnya akan menghentikan kedua bagian program.

3.  **Akses Panel Kontrol Web:**
    * Buka browser web favorit Anda.
    * Di bilah alamat (URL bar), ketik alamat yang Anda lihat di log terminal (misalnya: `http://127.0.0.1:5000/`).
    * Tekan `Enter`.

Selamat! Anda kini siap untuk *berinteraksi* dengan grafika 2D Anda secara dinamis!

## Panduan Penggunaan

Panel kontrol web dirancang agar sangat intuitif. Berikut adalah cara memaksimalkan pengalaman Anda:

* **Menggambar Objek:**
    * Di bagian "Mode Gambar", pilih jenis primitif (Titik, Garis, Segitiga, Elips, Persegi).
    * **Klik kiri** pada jendela PyOpenGL untuk menggambar. (Perhatikan: Garis, Segitiga, Elips, dan Persegi memerlukan beberapa klik untuk didefinisikan.)
* **Mengubah Warna & Ketebalan:**
    * Gunakan slider dan pemilih warna di "Pengaturan Gambar Global".
    * Klik "Perbarui Pengaturan". Perubahan ini akan memengaruhi **objek yang sedang terpilih**, atau objek **baru** jika tidak ada yang terpilih.
* **Memilih Objek:**
    * Pilih mode `Seleksi/Nonaktif` dari bagian "Mode Gambar".
    * **Klik kiri** pada objek di jendela PyOpenGL. Objek yang terpilih akan disorot dengan **highlight kuning** yang jelas.
* **Transformasi (Objek Terpilih):**
    * Setelah memilih objek, gunakan slider di bagian "Transformasi Objek" untuk **Translasi**, **Rotasi**, dan **Skala**.
    * Klik "Terapkan Translasi/Rotasi/Skala" setelah menyesuaikan slider.
    * **Reset Transformasi:** Klik tombol `Reset Transformasi` untuk mengembalikan objek yang terpilih ke posisi, rotasi, dan ukuran aslinya.
* **Kontrol Clipping:**
    * **Atur Jendela Clipping:** Klik tombol `Atur Jendela Clipping`. Kemudian, **klik dua titik** di jendela PyOpenGL untuk mendefinisikan area jendela clipping.
    * **Aktifkan/Nonaktifkan:** Gunakan tombol `Aktifkan Clipping` atau `Nonaktifkan Clipping` untuk melihat efek pemotongan pada objek yang melewati batas jendela.
    * **Geser Jendela:** Pastikan clipping aktif dan Anda dalam mode `Seleksi/Nonaktif`. Kemudian, **klik dan seret (drag-and-drop)** mouse di dalam jendela clipping di jendela PyOpenGL untuk memindahkannya.
* **Menghapus Objek:**
    * **Hapus Objek Terpilih:** Pastikan Anda telah memilih objek (ditandai kuning). Kemudian, klik tombol `Hapus Objek Terpilih` di panel kontrol web.
    * **Hapus Semua Objek:** Klik tombol `Hapus Semua Objek` untuk membersihkan seluruh kanvas.

## Potensi Pengembangan Lanjutan

Proyek ini adalah fondasi yang kokoh untuk eksplorasi lebih lanjut di bidang grafika komputer. Beberapa ide untuk penyempurnaan dan fitur tambahan meliputi:

* **UI/UX:**
    * Feedback visual yang lebih kaya di panel web (misal, menampilkan properti objek yang sedang dipilih).
    * Menampilkan mode gambar aktif secara lebih jelas di jendela PyOpenGL (selain highlight tombol).
    * Fungsionalitas "undo/redo" untuk operasi gambar dan transformasi.
* **Grafika:**
    * Implementasi alternatif algoritma clipping (misal, Liang-Barsky) dan perbandingannya.
    * Rotasi dan skala objek di sekitar *pusat objeknya sendiri* untuk interaksi yang lebih alami dan akurat.
    * Dukungan untuk kurva Bézier atau Spline.
    * Pengembangan menjadi grafika 3D yang lebih kompleks.
* **Interaksi:**
    * Peningkatan akurasi pemilihan objek dengan metode canggih (misal, Color Picking atau Selection Buffer OpenGL).
    * Shortcut keyboard tambahan untuk semua fungsi.
    * Fitur "mengubah ukuran" jendela clipping dengan *drag* dari sisi/sudutnya.



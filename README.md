Proyek Grafika Komputer Interaktif dengan PyOpenGL dan Web Control Panel



 (Opsional: jika Anda ingin menyertakan lisensi)

Selamat datang di Proyek Grafika Komputer Interaktif! Aplikasi ini adalah implementasi canggih dari konsep-konsep grafika 2D menggunakan PyOpenGL, dilengkapi dengan panel kontrol berbasis web yang intuitif dan responsif. Dirancang untuk memenuhi persyaratan tugas besar mata kuliah Grafika Komputer, proyek ini menunjukkan sinergi antara aplikasi desktop grafis berkinerja tinggi dan antarmuka pengguna modern berbasis web.

Daftar Isi
Gambaran Umum Proyek

Fitur Utama

Teknologi yang Digunakan

Struktur Proyek

Persyaratan Sistem

Panduan Instalasi

Cara Menjalankan Program

Panduan Penggunaan

Penyempurnaan Lanjutan (Potensi Pengembangan)

Kontribusi

Lisensi

Kontak

Gambaran Umum Proyek
Proyek ini adalah aplikasi grafika komputer yang memungkinkan pengguna untuk membuat, memanipulasi, dan melihat objek 2D secara interaktif. Berbeda dari aplikasi grafis tradisional, proyek ini memisahkan logika rendering grafis (yang dihandle oleh PyOpenGL sebagai aplikasi desktop) dari antarmuka pengguna (yang disajikan melalui browser web). Komunikasi antara keduanya difasilitasi oleh server Python Flask dan komunikasi socket real-time.

Pendekatan ini tidak hanya menunjukkan pemahaman mendalam tentang pipeline grafika, tetapi juga kemampuan untuk mengintegrasikan teknologi desktop dan web untuk pengalaman pengguna yang lebih fleksibel dan modern.

Fitur Utama
A. Objek 2D Dasar
Gambar Titik: Tambahkan titik dengan klik mouse.

Gambar Garis: Buat segmen garis dengan dua klik mouse.

Gambar Segitiga: Bentuk segitiga dengan tiga klik mouse.

Gambar Elips: Gambar elips terisi (saat clipping nonaktif) atau outline (saat clipping aktif) dengan dua klik (pusat dan titik radius).

Gambar Persegi: Buat persegi terisi (saat clipping nonaktif) atau outline (saat clipping aktif) dengan dua klik (sudut berlawanan).

Input Mouse Interaktif: Semua objek digambar dan dikelola melalui interaksi klik mouse langsung pada jendela OpenGL.

B. Pengaturan Warna & Ketebalan
Pilihan Warna RGB: Sesuaikan warna objek yang akan digambar atau warna objek yang sedang terpilih melalui pemilih warna di panel web.

Pilihan Ketebalan Garis/Ukuran Titik: Atur ketebalan garis atau ukuran titik menggunakan slider. Perubahan dapat diterapkan pada objek baru atau objek yang sedang terpilih.

C. Transformasi Geometris Interaktif
Translasi (Pergeseran): Geser objek yang terpilih di sepanjang sumbu X dan Y menggunakan slider di panel web.

Rotasi: Putar objek yang terpilih menggunakan slider sudut rotasi.

Skala (Perubahan Ukuran): Ubah ukuran objek yang terpilih di sepanjang sumbu X dan Y menggunakan slider skala.

Reset Transformasi: Tombol praktis untuk mengembalikan semua transformasi (translasi, rotasi, skala) objek yang terpilih ke kondisi awalnya.

D. Windowing & Clipping
Definisi Jendela Clipping: Tentukan area persegi panjang aktif untuk clipping dengan dua klik mouse pada jendela OpenGL. Batas jendela ditampilkan secara visual (outline cyan).

Algoritma Clipping Garis (Cohen-Sutherland): Potong garis dan segmen elips yang melampaui batas jendela clipping.

Algoritma Clipping Poligon (Sutherland-Hodgman): Potong segitiga dan persegi yang melampaui batas jendela clipping, menghasilkan poligon baru yang sesuai.

Aktifkan/Nonaktifkan Clipping: Kontrol on/off untuk fungsionalitas clipping dari panel web.

Geser Jendela Clipping: Geser jendela clipping secara halus dengan fitur drag-and-drop mouse langsung di jendela OpenGL (saat clipping aktif dan mode seleksi).

E. Integrasi & Interaktivitas Lanjutan
Pemilihan Objek: Pilih objek yang sudah ada dengan mengklik di jendela OpenGL (saat mode "Seleksi/Nonaktif" aktif). Objek yang terpilih akan ditandai dengan highlight kuning.

Panel Kontrol Berbasis Web: Antarmuka pengguna yang modern dan responsif dibangun dengan HTML, CSS, dan JavaScript, memungkinkan kontrol penuh atas aplikasi grafis.

Komunikasi Real-time: Penggunaan Flask sebagai backend web dan komunikasi socket untuk interaksi instan antara panel web dan jendela grafis PyOpenGL.

Teknologi yang Digunakan
Python 3.x: Bahasa pemrograman utama.

PyOpenGL: Binding Python untuk OpenGL, digunakan untuk rendering grafis 2D.

Flask: Micro-framework web Python, digunakan sebagai backend untuk melayani panel kontrol web dan API komunikasi.

Flask-Cors: Ekstensi Flask untuk menangani Cross-Origin Resource Sharing.

Pygame / FreeGLUT: Digunakan oleh PyOpenGL untuk manajemen jendela dan penanganan event dasar.

HTML5: Struktur dasar untuk antarmuka pengguna web.

CSS3: Styling untuk panel kontrol web yang menarik dan responsif.

JavaScript: Logika interaktif di sisi klien (browser) untuk panel kontrol.

Struktur Proyek
my_graphics_project/
├── main.py                 # Kode Python utama (PyOpenGL app + Flask backend)
└── static/                 # Folder untuk aset web (HTML, CSS, JS)
    ├── index.html          # Halaman panel kontrol web
    ├── style.css           # Styling untuk panel kontrol
    └── script.js           # Logika interaktif panel kontrol
Persyaratan Sistem
Sistem Operasi: Windows 10/11, macOS, atau Linux

Python 3.x terinstal

Koneksi internet (untuk mengunduh dependensi awal)

Browser Web modern (Chrome, Firefox, Edge, dll.)

Panduan Instalasi
Ikuti langkah-langkah di bawah ini untuk menyiapkan dan menjalankan proyek di lingkungan lokal Anda:

Unduh atau Kloning Repositori:

Bash

git clone [URL_REPO_ANDA] # Jika ini dari GitHub/GitLab
cd my_graphics_project
Atau, jika Anda hanya memiliki file-file, pastikan struktur folder my_graphics_project/main.py dan my_graphics_project/static/ sudah benar.

Instal Dependensi Python:
Buka Terminal atau Command Prompt (di Windows, pastikan python dan pip dikenali. Jika tidak, tambahkan Python ke PATH lingkungan sistem Anda atau gunakan py -m pip).

Navigasikan ke direktori proyek Anda (my_graphics_project):

Bash

cd path/to/my_graphics_project
Jalankan perintah instalasi dependensi:

Bash

pip install pygame PyOpenGL PyOpenGL_accelerate Flask Flask-Cors
(Jika pip tidak dikenali, coba python -m pip install ... atau py -m pip install ...)

Cara Menjalankan Program
Setelah instalasi selesai, ikuti langkah-langkah ini untuk menjalankan aplikasi:

Buka Terminal/Command Prompt:

Pastikan Anda berada di direktori proyek my_graphics_project.

Jalankan Aplikasi Python:

Bash

python main.py
Aplikasi ini akan memulai dua komponen: jendela aplikasi grafis PyOpenGL (aplikasi desktop) dan server web Flask (backend).

Jendela grafis PyOpenGL akan muncul di desktop Anda.

Di terminal, Anda akan melihat pesan log yang mengindikasikan bahwa server telah dimulai, termasuk alamat URL untuk panel kontrol web:

INFO - Aplikasi PyOpenGL siap. Silakan buka panel kontrol web Anda di browser.
INFO - Panel Kontrol Web dapat diakses di: http://127.0.0.1:5000/
Penting: Biarkan terminal ini tetap terbuka selama Anda menggunakan aplikasi.

Akses Panel Kontrol Web:

Buka browser web favorit Anda.

Di bilah alamat (URL bar), ketik alamat yang Anda lihat di log terminal (biasanya http://127.0.0.1:5000/).

Tekan Enter.

Sekarang Anda siap untuk berinteraksi dengan aplikasi grafis Anda!

Panduan Penggunaan
Panel kontrol web dirancang agar intuitif. Berikut adalah cara menggunakannya:

Mode Gambar:

Pilih mode Gambar Titik, Garis, Segitiga, Elips, atau Persegi dari bagian "Mode Gambar".

Klik kiri pada jendela PyOpenGL untuk menggambar. Beberapa objek (garis, segitiga, elips, persegi) memerlukan beberapa klik untuk didefinisikan.

Perhatikan bahwa tombol mode yang aktif akan memiliki highlight visual.

Pengaturan Gambar Global:

Gunakan slider Ketebalan Garis/Ukuran Titik dan pemilih Warna Gambar untuk mengatur properti objek yang akan digambar.

Klik "Perbarui Pengaturan" untuk menerapkan perubahan.

Catatan: Jika ada objek yang terpilih, perubahan warna/ketebalan akan diterapkan pada objek terpilih tersebut. Jika tidak ada objek terpilih, perubahan akan menjadi pengaturan default untuk objek yang baru digambar.

Transformasi Objek:

Pilih Objek: Aktifkan mode Seleksi/Nonaktif (tombol paling kanan di bagian "Mode Gambar"). Kemudian, klik kiri pada objek di jendela PyOpenGL. Objek yang terpilih akan ditandai dengan highlight kuning.

Gunakan slider Translasi X/Y, Rotasi, dan Skala X/Y untuk memanipulasi objek yang terpilih.

Klik "Terapkan Translasi/Rotasi/Skala" setelah menyesuaikan slider.

Reset Transformasi: Klik tombol "Reset Transformasi" untuk mengembalikan objek yang terpilih ke posisi, rotasi, dan ukuran aslinya.

Windowing & Clipping:

Atur Jendela Clipping: Klik "Atur Jendela Clipping (2 Klik)". Kemudian, klik dua titik di jendela PyOpenGL untuk mendefinisikan area jendela clipping.

Aktifkan/Nonaktifkan Clipping: Gunakan tombol "Aktifkan Clipping" dan "Nonaktifkan Clipping" untuk melihat efek pemotongan pada objek yang melewati batas jendela.

Geser Jendela Clipping: Pastikan clipping aktif dan Anda dalam mode Seleksi/Nonaktif. Kemudian, klik dan seret (drag-and-drop) mouse di dalam jendela clipping di jendela PyOpenGL untuk memindahkannya.

Umum:

Hapus Semua Objek: Klik tombol "Hapus Semua Objek" untuk membersihkan semua objek dari kanvas.

Penyempurnaan Lanjutan (Potensi Pengembangan)
Proyek ini telah mengimplementasikan fitur-fitur inti. Namun, ada banyak ruang untuk penyempurnaan dan fitur tambahan:

UI/UX:

Feedback visual di panel web saat objek terpilih (misalnya, menampilkan properti objek terpilih).

Indikator visual di jendela OpenGL saat mode gambar aktif (selain highlight tombol).

Fungsionalitas "undo/redo" untuk operasi gambar dan transformasi.

Grafika:

Clipping elips terisi (memerlukan algoritma yang lebih canggih dari clipping poligon).

Rotasi dan skala objek di sekitar pusat objeknya sendiri, bukan origin global.

Implementasi algoritma clipping Liang-Barsky sebagai alternatif Cohen-Sutherland.

Tambahan objek 2D lainnya (misalnya, poligon umum dengan N sisi).

Fungsionalitas "undo/redo" untuk operasi gambar dan transformasi.

Fitur "mengubah ukuran" window clipping dengan drag dari sisi/sudutnya.

Interaksi:

Peningkatan akurasi picking objek (misalnya, menggunakan color-picking atau selection buffer OpenGL).

Shortcut keyboard untuk mode gambar dan transformasi.

Kontribusi
Kontribusi untuk proyek ini sangat disambut baik! Jika Anda memiliki ide atau perbaikan, silakan:

Fork repositori ini.

Buat branch baru (git checkout -b feature/nama-fitur-baru).

Lakukan perubahan dan commit (git commit -m 'Tambahkan fitur baru').

Push ke branch Anda (git push origin feature/nama-fitur-baru).

Buat Pull Request.

Lisensi
Proyek ini dilisensikan di bawah Lisensi MIT. Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini untuk tujuan pribadi atau komersial.

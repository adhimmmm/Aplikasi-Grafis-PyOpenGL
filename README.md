#  Aplikasi Grafis Interaktif PyOpenGL & Web

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyOpenGL](https://img.shields.io/badge/PyOpenGL-blue?style=for-the-badge&logo=opengl&logoColor=white)](http://pyopengl.sourceforge.net/)
[![Pygame](https://img.shields.io/badge/Pygame-FF1C1C?style=for-the-badge&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Flask-SocketIO](https://img.shields.io/badge/Flask--SocketIO-000000?style=for-the-badge&logo=socket.io&logoColor=white)](https://flask-socketio.readthedocs.io/en/latest/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Three.js](https://img.shields.io/badge/Three.js-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=for-the-badge&logo=socket.io&logoColor=white)](https://socket.io/)

Ini adalah proyek aplikasi grafis yang terbagi menjadi dua bagian utama: aplikasi grafis 2D interaktif dan aplikasi grafis 3D, keduanya dibangun menggunakan PyOpenGL untuk rendering grafis dan diintegrasikan dengan teknologi web (Flask dan JavaScript) untuk antarmuka kontrol yang intuitif.

## Fitur Utama

### 1\. Aplikasi Grafis 2D Interaktif

Aplikasi 2D memungkinkan pengguna untuk menggambar berbagai primitif grafis dan menerapkan transformasi secara real-time melalui panel kontrol web.

  * **Gambar Primitif:** Dukungan untuk menggambar titik, garis, segitiga, elips, dan persegi.
  * **Transformasi Objek:** Terapkan translasi (geser), rotasi, dan skala pada objek yang dipilih.
  * **Pengaturan Gambar:** Sesuaikan ketebalan garis/ukuran titik dan warna gambar.
  * **Windowing & Clipping:** Tentukan jendela clipping khusus dan aktifkan/nonaktifkan clipping menggunakan algoritma Cohen-Sutherland (untuk garis) dan Sutherland-Hodgman (untuk poligon).
  * **Interaksi Mouse:** Gambar objek dengan klik mouse, pilih objek dengan mengklik, dan geser jendela clipping.
  * **Komunikasi Real-time:** Kontrol aplikasi PyOpenGL melalui antarmuka web Flask yang berkomunikasi melalui soket TCP/IP.

### 2\. Aplikasi Grafis 3D Interaktif

Aplikasi 3D menyediakan visualisasi objek 3D dengan kontrol kamera, pencahayaan Phong, dan kemampuan memuat model OBJ, juga melalui panel kontrol web.

  * **Visualisasi Objek 3D:** Render dan manipulasi kubus, piramida, dan sphere.
  * **Load File OBJ:** Impor model 3D eksternal dalam format `.obj`.
  * **Transformasi Objek:** Kontrol rotasi (X, Y, Z), skala, dan posisi (X, Y, Z) objek 3D.
  * **Pencahayaan Phong:** Atur komponen cahaya ambient, diffuse, dan specular untuk model shading yang realistis.
  * **Kontrol Kamera:** Sesuaikan posisi kamera menggunakan parameter `gluLookAt` dan ubah mode proyeksi antara perspektif (`gluPerspective`) dan ortografis.
  * **Mode Rendering:** Alihkan antara mode wireframe dan mode terisi.
  * **Animasi Otomatis:** Opsi untuk mengaktifkan rotasi objek otomatis.
  * **Kontrol Mouse 3D:** Interaksi mouse untuk rotasi kamera, zoom, dan pan di jendela Pygame/OpenGL.
  * **Komunikasi Real-time:** Panel kontrol web menggunakan Three.js untuk visualisasi di browser dan Socket.IO untuk mengirim perintah ke backend PyOpenGL.

## Teknologi yang Digunakan

  * **Backend (PyOpenGL Applications):**

      * **Python:** Bahasa pemrograman utama.
      * **PyOpenGL:** Binding Python untuk OpenGL (untuk rendering 2D & 3D).
      * **Pygame:** Digunakan untuk mengelola jendela OpenGL dan event input.
      * **Flask:** Microframework web Python untuk melayani panel kontrol 2D dan 3D.
      * **Flask-SocketIO:** Ekstensi Flask untuk komunikasi WebSocket (digunakan di aplikasi 3D).
      * **Socket (Python Built-in):** Digunakan untuk komunikasi antara Flask dan PyOpenGL di aplikasi 2D.
      * **NumPy:** Untuk operasi matematika, khususnya dalam perhitungan normal di aplikasi 3D.
      * **Threading:** Untuk menjalankan server OpenGL dan Flask secara bersamaan.

  * **Frontend (Web Control Panels):**

      * **HTML5:** Struktur dasar antarmuka web.
      * **CSS3:** Styling untuk tampilan yang menarik dan responsif.
      * **JavaScript:** Logika interaktif di sisi klien.
      * **Three.js:** Pustaka JavaScript untuk rendering 3D di browser (digunakan di panel kontrol 3D untuk *visualisasi sendiri di browser*, sekaligus sebagai kontrol untuk aplikasi PyOpenGL backend).
      * **Socket.IO (Client-side):** Untuk komunikasi real-time antara browser dan Flask-SocketIO server (aplikasi 3D).
      * **Fetch API:** Untuk komunikasi antara browser dan Flask server (aplikasi 2D).

## Struktur Proyek

```
.
├── Grafkom/
│   ├── 2D/
│   │   ├── main.py               # Backend PyOpenGL 2D dan server Flask
│   │   └── static/
│   │       ├── index.html        # Frontend HTML untuk kontrol 2D
│   │       ├── script.js         # Logika JavaScript untuk kontrol 2D
│   │       └── style.css         # Styling CSS untuk kontrol 2D
│   └── 3D/
│       ├── app.py                # Backend PyOpenGL 3D dan server Flask-SocketIO
│       └── 3d.html               # Frontend HTML untuk kontrol 3D (dengan Three.js)
```

## Instalasi

Pastikan Anda memiliki Python 3 terinstal di sistem Anda. Kemudian, ikuti langkah-langkah di bawah ini:

1.  **Clone Repository (jika ada):**

    ```bash
    git clone <URL_REPOSITORY_ANDA>
    cd <NAMA_FOLDER_PROYEK>
    ```

2.  **Instal Dependensi:**
    Navigasikan ke direktori utama proyek (`Grafkom/` jika Anda memiliki struktur yang sama) dan instal semua pustaka Python yang diperlukan:

    ```bash
    pip install Flask Flask-SocketIO PyOpenGL pygame numpy
    ```

    Jika Anda mengalami masalah dengan `PyOpenGL` atau `pygame`, pastikan Anda memiliki build tools yang diperlukan untuk mengompilasi paket-paket ini.

## Cara Menjalankan Aplikasi

Anda dapat menjalankan aplikasi 2D atau 3D secara terpisah.

### Menjalankan Aplikasi Grafis 2D

1.  **Navigasi ke Direktori 2D:**

    ```bash
    cd Grafkom/2D
    ```

2.  **Jalankan Aplikasi Python:**

    ```bash
    python main.py
    ```

    Ini akan memulai jendela PyOpenGL 2D dan server web Flask untuk panel kontrol.

3.  **Buka Panel Kontrol Web:**
    Buka browser web Anda dan navigasikan ke:
    [http://127.0.0.1:5000/](https://www.google.com/search?q=http://127.0.0.1:5000/)

    Anda akan melihat panel kontrol tempat Anda dapat berinteraksi dengan aplikasi grafis 2D.

### Menjalankan Aplikasi Grafis 3D

1.  **Navigasi ke Direktori 3D:**

    ```bash
    cd Grafkom/3D
    ```

2.  **Jalankan Aplikasi Python:**

    ```bash
    python app.py
    ```

    Ini akan memulai jendela Pygame/PyOpenGL 3D dan server web Flask-SocketIO untuk panel kontrol. Skrip juga akan secara otomatis mencoba membuka panel kontrol di browser Anda.

3.  **Buka Panel Kontrol Web:**
    Buka browser web Anda dan navigasikan ke:
    [http://localhost:5000/](https://www.google.com/search?q=http://localhost:5000/)

    Anda akan melihat panel kontrol dengan visualisasi 3D (dibuat dengan Three.js) yang juga mengontrol jendela PyOpenGL 3D.

## Penggunaan

Setelah aplikasi PyOpenGL (2D atau 3D) dan panel kontrol web yang sesuai berjalan:

  * **Panel Kontrol Web:** Gunakan slider, tombol, dan kotak centang di antarmuka web untuk mengubah mode gambar, menerapkan transformasi, menyesuaikan pengaturan pencahayaan, mengontrol kamera, dan banyak lagi. Perubahan akan segera tercermin di jendela PyOpenGL.
  * **Jendela PyOpenGL:**
      * **2D:** Klik di jendela untuk menggambar objek sesuai mode yang dipilih. Untuk objek yang membutuhkan lebih dari satu titik (garis, segitiga, elips, persegi, jendela clipping), klik titik-titik yang diperlukan. Dalam mode seleksi, klik objek untuk memilihnya dan terapkan transformasi.
      * **3D:** Anda dapat merotasi kamera dengan drag mouse (klik kiri + drag), melakukan pan dengan klik kanan + drag, dan zoom in/out dengan scroll mouse.

Selamat mencoba aplikasi grafis interaktif Anda\!

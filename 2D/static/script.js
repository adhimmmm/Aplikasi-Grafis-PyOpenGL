document.addEventListener("DOMContentLoaded", () => {
  // Mendapatkan elemen DOM untuk menampilkan status pesan di UI web.
  const statusMessage = document.getElementById("status-message");

  // --- Pembaruan Tampilan Nilai Slider ---
  // Fungsi ini membuat slider interaktif dengan menampilkan nilai saat digeser.
  // Memudahkan pengguna melihat nilai numerik dari slider.
  function setupSlider(inputId, valueDisplayId, unit = "") {
    const inputElement = document.getElementById(inputId);
    const valueDisplayElement = document.getElementById(valueDisplayId);
    if (inputElement && valueDisplayElement) {
      inputElement.addEventListener("input", () => {
        valueDisplayElement.textContent = inputElement.value + unit;
      });
      // Atur nilai awal saat halaman dimuat agar tampilan konsisten.
      valueDisplayElement.textContent = inputElement.value + unit;
    }
  }

  // Panggil setupSlider untuk setiap slider yang ada di HTML.
  setupSlider("translateX", "translateXValue");
  setupSlider("translateY", "translateYValue");
  setupSlider("rotateAngle", "rotateAngleValue", "°"); // Tambahkan satuan derajat.
  setupSlider("scaleX", "scaleXValue", "%");
  setupSlider("scaleY", "scaleYValue", "%");
  setupSlider("lineThickness", "lineThicknessValue");

  // --- Fungsi Komunikasi dengan Backend Flask ---
  // Fungsi asinkron untuk mengirim perintah ke backend Flask (server Python).
  async function sendMessageToBackend(endpoint, data) {
    statusMessage.textContent = "Mengirim perintah...";
    statusMessage.className = "status-box"; // Reset class untuk gaya status (misal, hapus success/error).

    try {
      // Menggunakan Fetch API untuk mengirim permintaan POST dengan data JSON.
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Memberitahu server bahwa body adalah JSON.
        },
        body: JSON.stringify(data), // Mengkonversi objek JavaScript ke string JSON.
      });

      // Memastikan respons adalah JSON dan menguraikannya.
      const result = await response.json();

      // Memperbarui pesan status di UI web berdasarkan respons dari backend.
      if (result.status === "success") {
        statusMessage.textContent = `BERHASIL: ${result.message}`;
        statusMessage.classList.add("success"); // Tambahkan kelas gaya sukses (dari CSS).
      } else {
        statusMessage.textContent = `GAGAL: ${result.message.replace(/["']/g, "")}`; // Hapus quote dari pesan error
        statusMessage.classList.add("error"); // Tambahkan kelas gaya error (dari CSS).
      }
      console.log("Respons Backend:", result); // Log respons lengkap ke konsol browser untuk debugging.
      return result;
    } catch (error) {
      // Menangani kesalahan koneksi atau kesalahan lain yang terjadi saat komunikasi (misal, backend tidak jalan).
      statusMessage.textContent = `ERROR KONEKSI: ${error.message}. Pastikan backend dan PyOpenGL berjalan.`;
      statusMessage.classList.add("error");
      console.error("Error saat berkomunikasi dengan backend:", error);
      return { status: "error", message: error.message };
    }
  }

  // --- Fungsi Mengelola Kelas Aktif Tombol Mode Gambar ---
  // Fungsi ini menambahkan kelas CSS 'active-tool-button' ke tombol yang sedang dipilih
  // dan menghapusnya dari tombol lain, memberikan umpan balik visual kepada pengguna.
  function setActiveDrawingToolButton(activeButtonId) {
    // Dapatkan referensi ke semua tombol mode gambar.
    const drawingToolButtons = [
      document.getElementById("drawPointTool"),
      document.getElementById("drawLineTool"),
      document.getElementById("drawTriangleTool"),
      document.getElementById("drawEllipseTool"),
      document.getElementById("drawRectangleTool"),
      document.getElementById("selectNoneTool"),
    ];

    // Hapus kelas 'active-tool-button' dari semua tombol mode gambar lainnya.
    drawingToolButtons.forEach((button) => {
      if (button) {
        // Pastikan tombol ada (tidak null) sebelum mencoba memanipulasinya.
        button.classList.remove("active-tool-button");
      }
    });

    // Tambahkan kelas 'active-tool-button' ke tombol yang sedang aktif.
    const activeBtn = document.getElementById(activeButtonId);
    if (activeBtn) {
      activeBtn.classList.add("active-tool-button");
    }
  }

  // --- Event Listener untuk Kontrol Transformasi ---
  // Tombol "Terapkan Translasi"
  document.getElementById("applyTranslate").addEventListener("click", () => {
    const tx = parseFloat(document.getElementById("translateX").value); // Mengambil nilai slider X sebagai float.
    const ty = parseFloat(document.getElementById("translateY").value); // Mengambil nilai slider Y sebagai float.
    // Mengirim perintah translasi ke backend.
    sendMessageToBackend("/api/transform", { type: "transform", action: "translate", x: tx, y: ty });
  });

  // Tombol "Terapkan Rotasi"
  document.getElementById("applyRotate").addEventListener("click", () => {
    const angle = parseFloat(document.getElementById("rotateAngle").value); // Mengambil nilai slider sudut rotasi.
    // Mengirim perintah rotasi ke backend.
    sendMessageToBackend("/api/transform", { type: "transform", action: "rotate", angle: angle });
  });

  // Tombol "Terapkan Skala"
  document.getElementById("applyScale").addEventListener("click", () => {
    const scale_x = parseFloat(document.getElementById("scaleX").value) / 100.0; // Konversi persen ke faktor skala (misal 100% -> 1.0).
    const scale_y = parseFloat(document.getElementById("scaleY").value) / 100.0;
    // Mengirim perintah skala ke backend.
    sendMessageToBackend("/api/transform", { type: "transform", action: "scale", scale_x: scale_x, scale_y: scale_y });
  });

  // Tombol "Reset Transformasi"
  document.getElementById("resetTransform").addEventListener("click", () => {
    sendMessageToBackend("/api/transform", { type: "transform", action: "reset_transforms" });
    // Setel ulang slider transformasi ke nilai default di UI setelah reset berhasil dikirim
    document.getElementById("translateX").value = 0;
    document.getElementById("translateY").value = 0;
    document.getElementById("rotateAngle").value = 0;
    document.getElementById("scaleX").value = 100;
    document.getElementById("scaleY").value = 100;
    // Panggil setupSlider lagi untuk memperbarui tampilan nilai di sebelah slider
    setupSlider("translateX", "translateXValue");
    setupSlider("translateY", "translateYValue");
    setupSlider("rotateAngle", "rotateAngleValue", "°");
    setupSlider("scaleX", "scaleXValue", "%");
    setupSlider("scaleY", "scaleYValue", "%");
  });

  // --- Event Listener untuk Kontrol Mode Gambar ---
  // Setiap tombol mode gambar akan mengirim perintah ke backend untuk mengubah mode,
  // dan juga memperbarui tampilan visual tombol aktif.
  document.getElementById("drawPointTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "point" });
    setActiveDrawingToolButton("drawPointTool");
  });
  document.getElementById("drawLineTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "line" });
    setActiveDrawingToolButton("drawLineTool");
  });
  document.getElementById("drawTriangleTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "triangle" });
    setActiveDrawingToolButton("drawTriangleTool");
  });
  document.getElementById("drawEllipseTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "ellipse" });
    setActiveDrawingToolButton("drawEllipseTool");
  });
  document.getElementById("drawRectangleTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "rectangle" });
    setActiveDrawingToolButton("drawRectangleTool");
  });
  document.getElementById("selectNoneTool").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "none" });
    setActiveDrawingToolButton("selectNoneTool");
  });

  // --- Event Listener untuk Pengaturan Gambar Global ---
  document.getElementById("applyDrawSettings").addEventListener("click", () => {
    const thickness = parseFloat(document.getElementById("lineThickness").value);
    const color = document.getElementById("drawColor").value; // Mengambil nilai warna hex (misal #FF0000).
    // Mengirim perintah pengaturan gambar ke backend.
    sendMessageToBackend("/api/draw_settings", { thickness: thickness, color: color });
  });

  // --- Event Listener untuk Kontrol Windowing & Clipping ---
  document.getElementById("setClipWindow").addEventListener("click", () => {
    sendMessageToBackend("/api/clipping", { action: "set_window_mode" });
    // Catatan: Anda mungkin ingin menambahkan logika visual aktif khusus untuk tombol ini
    // jika pengguna sedang dalam mode mengatur jendela clipping.
  });
  document.getElementById("enableClipping").addEventListener("click", () => {
    sendMessageToBackend("/api/clipping", { action: "enable" });
    // Menambahkan gaya aktif ke tombol "Aktifkan Clipping", menghapus dari "Nonaktifkan Clipping".
    document.getElementById("enableClipping").classList.add("active-tool-button");
    document.getElementById("disableClipping").classList.remove("active-tool-button");
  });
  document.getElementById("disableClipping").addEventListener("click", () => {
    sendMessageToBackend("/api/clipping", { action: "disable" });
    // Menambahkan gaya aktif ke tombol "Nonaktifkan Clipping", menghapus dari "Aktifkan Clipping".
    document.getElementById("disableClipping").classList.add("active-tool-button");
    document.getElementById("enableClipping").classList.remove("active-tool-button");
  });

  // --- Event Listener untuk Kontrol Umum ---
  document.getElementById("clearAllObjects").addEventListener("click", () => {
    sendMessageToBackend("/api/draw_mode", { mode: "clear_all" });
    // Saat menghapus semua objek, secara visual kembali ke mode 'none'.
    setActiveDrawingToolButton("selectNoneTool");
  });

  // --- Inisialisasi awal saat halaman dimuat ---
  // Atur mode default saat halaman pertama kali dibuka (misal, mode 'none' aktif secara visual).
  setActiveDrawingToolButton("selectNoneTool");
});

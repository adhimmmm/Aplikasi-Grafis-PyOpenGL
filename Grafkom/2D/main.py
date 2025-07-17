import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import threading
import socket
import json
import logging
import time
import math

# --- Konfigurasi Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Konfigurasi Komunikasi ---
PYOPENGL_APP_HOST = '127.0.0.1'
PYOPENGL_APP_PORT = 12345
FLASK_WEB_PORT = 5000

# --- Status Aplikasi PyOpenGL (Variabel Global) ---
current_line_thickness = 1.0
current_draw_color = [1.0, 0.0, 0.0] # Default: Merah (RGB 0.0-1.0)

# Definisi mode gambar.
DRAW_MODE_NONE = 0
DRAW_MODE_POINT = 1
DRAW_MODE_LINE = 2
DRAW_MODE_TRIANGLE = 3
DRAW_MODE_ELLIPSE = 4
DRAW_MODE_RECTANGLE = 5 # <--- BARU: Mode gambar persegi
DRAW_MODE_CLIP_WINDOW = 6 # <--- Urutan berubah, jadi ini jadi 6

current_draw_mode = DRAW_MODE_NONE
drawing_points = []

# Struktur untuk menyimpan semua objek yang sudah digambar
# Setiap objek adalah dictionary dengan propertinya:
# 'type': jenis objek (DRAW_MODE_POINT, etc.)
# 'points': list of lists untuk koordinat verteks
# 'color': list [R, G, B]
# 'thickness': ketebalan garis atau ukuran titik
# 'transformations': dictionary untuk transformasi spesifik objek {'translate': [tx,ty], 'rotate': angle, 'scale': [sx,sy]}
drawn_objects = []

# Variabel untuk clipping window
clipping_window_coords = {'x_min': -0.7, 'y_min': -0.7, 'x_max': 0.7, 'y_max': 0.7}
clipping_enabled = False

selected_object_index = -1 # Index objek yang sedang dipilih, -1 jika tidak ada.

# Variabel untuk fitur drag jendela clipping
is_dragging_clipping_window = False
drag_start_x = 0.0 # Posisi X awal klik saat memulai drag
drag_start_y = 0.0 # Posisi Y awal klik saat memulai drag
# Offset dari titik klik ke sudut kiri bawah jendela clipping
drag_offset_x = 0.0
drag_offset_y = 0.0


# --- Kelas Server Perintah PyOpenGL ---
class PyOpenGLCommandServer:
    def __init__(self, host, port, command_callback):
        self.host = host
        self.port = port
        self.command_callback = command_callback
        self.server_socket = None
        self.running = False
        self.thread = None

    def start(self):
        """Memulai server soket di thread terpisah."""
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logging.info(f"PyOpenGL Command Server dimulai di {self.host}:{self.port}")

    def _run_server(self):
        """Loop utama server soket untuk menerima koneksi dan perintah."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            while self.running:
                conn, addr = self.server_socket.accept()
                with conn:
                    logging.info(f"Koneksi diterima dari {addr}")
                    data = conn.recv(1024).decode('utf-8')
                    if not data:
                        continue
                    
                    logging.info(f"Perintah diterima: {data}")
                    response = self._process_command(data)
                    conn.sendall(response.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error di server soket PyOpenGL: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            logging.info("PyOpenGL Command Server dihentikan.")

    def _process_command(self, command_string):
        """
        Menguraikan string perintah (diharapkan dalam format JSON) dan memanggil fungsi callback.
        Callback akan bertanggung jawab untuk memodifikasi state grafis.
        """
        try:
            command_data = json.loads(command_string) 
            if self.command_callback:
                self.command_callback(command_data) 
                return json.dumps({"status": "success", "message": "Perintah dieksekusi"})
        except json.JSONDecodeError:
            logging.warning(f"Perintah non-JSON diterima: {command_string}. Mengabaikan.")
            return json.dumps({"status": "error", "message": "Perintah diterima dalam format tidak valid (bukan JSON)."})
        except Exception as e:
            logging.error(f"Error memproses perintah: {e}")
            return json.dumps({"status": "error", "message": f"Gagal memproses perintah: {e}"})
        
        return json.dumps({"status": "error", "message": "Perintah tidak dikenali atau callback tidak ada"})

    def stop(self):
        """Menghentikan server soket dengan aman."""
        self.running = False
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        except ConnectionRefusedError:
            pass
        if self.thread:
            self.thread.join(timeout=1)

# --- Fungsi Gambar Primitif OpenGL ---
def draw_point(x, y, color, size):
    """Menggambar sebuah titik."""
    glPointSize(size)
    glColor3fv(color)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_line(p1, p2, color, thickness):
    """Menggambar sebuah garis."""
    glLineWidth(thickness)
    glColor3fv(color)
    glBegin(GL_LINES)
    glVertex2f(p1[0], p1[1])
    glVertex2f(p2[0], p2[1])
    glEnd()

def draw_triangle(p1, p2, p3, color):
    """Menggambar sebuah segitiga."""
    glColor3fv(color)
    glBegin(GL_TRIANGLES)
    glVertex2f(p1[0], p1[1])
    glVertex2f(p2[0], p2[1])
    glVertex2f(p3[0], p3[1])
    glEnd()

def draw_ellipse(center_x, center_y, radius_x, radius_y, color, segments=100, filled=True, thickness=1.0):
    """
    Menggambar sebuah elips.
    Jika filled=True, menggunakan GL_TRIANGLE_FAN untuk mengisi elips.
    Jika filled=False, mengembalikan daftar segmen garis untuk outline (untuk clipping).
    Ditambahkan parameter 'thickness' agar bisa diteruskan ke segmen yang di-clip.
    """
    glColor3fv(color)
    if filled:
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * float(i) / float(segments)
            dx = radius_x * math.cos(angle)
            dy = radius_y * math.sin(angle)
            glVertex2f(center_x + dx, center_y + dy)
        glEnd()
        return None
    else:
        segments_list = []
        for i in range(segments):
            angle1 = 2.0 * math.pi * float(i) / float(segments)
            angle2 = 2.0 * math.pi * float(i + 1) / float(segments)
            
            p1_x = center_x + radius_x * math.cos(angle1)
            p1_y = center_y + radius_y * math.sin(angle1)
            p2_x = center_x + radius_x * math.cos(angle2)
            p2_y = center_y + radius_y * math.sin(angle2)
            segments_list.append([[p1_x, p1_y], [p2_x, p2_y]])
        return segments_list

def draw_rectangle(p1, p2, color, filled=True, thickness=1.0):
    """
    Menggambar sebuah persegi panjang.
    p1: [x1, y1] (sudut pertama)
    p2: [x2, y2] (sudut kedua)
    """
    x1, y1 = p1
    x2, y2 = p2

    glColor3fv(color)
    glLineWidth(thickness)

    if filled:
        glBegin(GL_QUADS) # Untuk persegi terisi
    else:
        glBegin(GL_LINE_LOOP) # Untuk outline persegi

    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()


# --- Fungsi Transformasi Titik ---
def apply_object_transform_to_point(point, transformations):
    """
    Menerapkan transformasi (translasi, rotasi, skala) ke satu titik.
    Mengembalikan titik yang sudah ditransformasi.
    Ini penting agar clipping bekerja pada posisi objek yang benar setelah transformasi.
    """
    x, y = point
    
    # Skala
    if 'scale' in transformations:
        sx, sy = transformations['scale']
        x *= sx
        y *= sy
    
    # Rotasi (rotasi sederhana di sekitar origin 0,0)
    # Untuk rotasi di sekitar pusat objek, perlu terjemahan sebelum/sesudah.
    if 'rotate' in transformations:
        angle_rad = math.radians(transformations['rotate'])
        new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        x, y = new_x, new_y
        
    # Translasi
    if 'translate' in transformations:
        tx, ty = transformations['translate']
        x += tx
        y += ty
        
    return [x, y]


# --- Fungsi Clipping (Cohen-Sutherland & Sutherland-Hodgman) ---
# Cohen-Sutherland untuk Garis
INSIDE = 0  # 0000 -> Titik di dalam window
LEFT = 1    # 0001 -> Titik di kiri window
RIGHT = 2   # 0010 -> Titik di kanan window
BOTTOM = 4  # 0100 -> Titik di bawah window
TOP = 8     # 1000 -> Titik di atas window

def compute_outcode(x, y, x_min, y_min, x_max, y_max):
    """Menghitung outcode (kode region) untuk sebuah titik."""
    code = INSIDE
    if x < x_min: code |= LEFT
    elif x > x_max: code |= RIGHT
    if y < y_min: code |= BOTTOM
    elif y > y_max: code |= TOP
    return code

def cohen_sutherland_clip(p1, p2, window_coords):
    """
    Mengimplementasikan algoritma clipping Cohen-Sutherland untuk garis.
    Mengembalikan koordinat garis yang sudah di-clip ([x1,y1], [x2,y2]) atau None jika garis sepenuhnya di-clip.
    """
    x1, y1 = p1
    x2, y2 = p2
    x_min, y_min, x_max, y_max = window_coords['x_min'], window_coords['y_min'], window_coords['x_max'], window_coords['y_max']

    code1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)
    
    accept = False

    while True:
        if (code1 == 0 and code2 == 0): # Kedua titik akhir berada di dalam jendela
            accept = True
            break
        elif (code1 & code2) != 0: # Kedua titik akhir berada di luar dan di sisi yang sama
            break
        else:
            x, y = 0.0, 0.0
            code_out = code1 if code1 != 0 else code2

            if code_out & TOP:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min 

            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                code2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)
    
    if accept:
        return [x1, y1], [x2, y2]
    else:
        return None

# Sutherland-Hodgman untuk Poligon (Dasar Konveks)
def sutherland_hodgman_clip(polygon_vertices, window_coords):
    """
    Mengimplementasikan algoritma clipping Sutherland-Hodgman untuk poligon konveks.
    Ini adalah implementasi dasar yang berfungsi untuk poligon konveks (seperti segitiga).
    """
    clipped_polygon = list(polygon_vertices)

    x_min, y_min, x_max, y_max = window_coords['x_min'], window_coords['y_min'], window_coords['x_max'], window_coords['y_max']

    def clip_against_edge(input_polygon, edge_type, edge_value):
        output_polygon = []
        if not input_polygon: return output_polygon

        for i in range(len(input_polygon)):
            p1 = input_polygon[i]
            p2 = input_polygon[(i + 1) % len(input_polygon)]

            def is_inside(point):
                if edge_type == 'left': return point[0] >= edge_value
                if edge_type == 'right': return point[0] <= edge_value
                if edge_type == 'bottom': return point[1] >= edge_value
                if edge_type == 'top': return point[1] <= edge_value

            def intersect(p_start, p_end):
                if edge_type == 'left' or edge_type == 'right':
                    denom = (p_end[0] - p_start[0])
                    if denom == 0:
                        return [edge_value, p_start[1]]
                    t = (edge_value - p_start[0]) / denom
                    return [edge_value, p_start[1] + t * (p_end[1] - p_start[1])]
                elif edge_type == 'bottom' or edge_type == 'top':
                    denom = (p_end[1] - p_start[1])
                    if denom == 0:
                        return [p_start[0], edge_value]
                    t = (edge_value - p_start[1]) / denom
                    return [p_start[0] + t * (p_end[0] - p_start[0]), edge_value]
                return []

            p1_inside = is_inside(p1)
            p2_inside = is_inside(p2)

            if p1_inside and p2_inside:
                output_polygon.append(p2)
            elif p1_inside and not p2_inside:
                output_polygon.append(intersect(p1, p2))
            elif not p1_inside and p2_inside:
                output_polygon.append(intersect(p1, p2))
                output_polygon.append(p2)

        return output_polygon
    
    # Clip against each edge of the window
    clipped_polygon = clip_against_edge(clipped_polygon, 'left', x_min)
    if not clipped_polygon: return []
    clipped_polygon = clip_against_edge(clipped_polygon, 'right', x_max)
    if not clipped_polygon: return []
    clipped_polygon = clip_against_edge(clipped_polygon, 'bottom', y_min)
    if not clipped_polygon: return []
    clipped_polygon = clip_against_edge(clipped_polygon, 'top', y_max)

    return clipped_polygon if clipped_polygon else []

# --- Fungsi Utama Rendering OpenGL ---
def display():
    """
    Fungsi ini dipanggil setiap kali jendela OpenGL perlu digambar ulang.
    Ini adalah tempat semua logika rendering grafis berada.
    """
    global redraw_needed, current_draw_mode, selected_object_index

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluOrtho2D(-1.0, 1.0, -1.0, 1.0) 

    # Menggambar objek-objek yang sudah disimpan.
    for i, obj in enumerate(drawn_objects):
        # Dapatkan transformasi objek saat ini (default ke dictionary kosong jika tidak ada)
        current_obj_transforms = obj.get('transformations', {})

        # --- Bagian CLIPPING ---
        if clipping_enabled:
            # KLIPING TITIK
            if obj['type'] == DRAW_MODE_POINT:
                transformed_point = apply_object_transform_to_point(obj['points'][0], current_obj_transforms)
                if (clipping_window_coords['x_min'] <= transformed_point[0] <= clipping_window_coords['x_max'] and
                    clipping_window_coords['y_min'] <= transformed_point[1] <= clipping_window_coords['y_max']):
                    draw_point(transformed_point[0], transformed_point[1], obj['color'], obj['thickness'])
            # KLIPING GARIS
            elif obj['type'] == DRAW_MODE_LINE:
                # Transformasi kedua titik garis sebelum clipping
                transformed_p1 = apply_object_transform_to_point(obj['points'][0], current_obj_transforms)
                transformed_p2 = apply_object_transform_to_point(obj['points'][1], current_obj_transforms)
                
                clipped_line_coords = cohen_sutherland_clip(transformed_p1, transformed_p2, clipping_window_coords)
                if clipped_line_coords: 
                    draw_line(clipped_line_coords[0], clipped_line_coords[1], obj['color'], obj['thickness'])
            # KLIPING SEGITIGA
            elif obj['type'] == DRAW_MODE_TRIANGLE:
                # Transformasi semua verteks segitiga sebelum clipping
                transformed_vertices = [apply_object_transform_to_point(p, current_obj_transforms) for p in obj['points']]
                
                clipped_triangle_vertices = sutherland_hodgman_clip(transformed_vertices, clipping_window_coords)
                if clipped_triangle_vertices:
                    glColor3fv(obj['color'])
                    glBegin(GL_POLYGON)
                    for vertex in clipped_triangle_vertices:
                        glVertex2f(vertex[0], vertex[1])
                    glEnd()
            # KLIPING ELIPS (outline)
            elif obj['type'] == DRAW_MODE_ELLIPSE:
                # Transformasi pusat elips dan skala radiusnya.
                transformed_center = apply_object_transform_to_point(obj['points'][0], current_obj_transforms)
                original_radius_x, original_radius_y = obj['points'][1]
                transformed_radius_x, transformed_radius_y = original_radius_x, original_radius_y
                if 'scale' in current_obj_transforms:
                    transformed_radius_x *= current_obj_transforms['scale'][0]
                    transformed_radius_y *= current_obj_transforms['scale'][1]
                
                # Mendapatkan segmen garis yang membentuk outline elips yang sudah ditransformasi secara logis.
                ellipse_segments = draw_ellipse(transformed_center[0], transformed_center[1],
                                                transformed_radius_x, transformed_radius_y,
                                                obj['color'], filled=False, thickness=obj['thickness'])
                
                if ellipse_segments:
                    for segment in ellipse_segments:
                        # Setiap segmen elips yang sudah "ditransformasi secara logis"
                        # sekarang di-clip menggunakan Cohen-Sutherland.
                        clipped_segment = cohen_sutherland_clip(segment[0], segment[1], clipping_window_coords)
                        if clipped_segment:
                            draw_line(clipped_segment[0], clipped_segment[1], obj['color'], obj['thickness'])
            # KLIPING PERSEGI (outline)
            elif obj['type'] == DRAW_MODE_RECTANGLE:
                x1_orig, y1_orig = obj['points'][0]
                x2_orig, y2_orig = obj['points'][1]
                rect_vertices = [
                    [x1_orig, y1_orig],
                    [x2_orig, y1_orig],
                    [x2_orig, y2_orig],
                    [x1_orig, y2_orig]
                ]
                # Transformasi verteks persegi
                transformed_vertices = [apply_object_transform_to_point(p, current_obj_transforms) for p in rect_vertices]

                clipped_rect_vertices = sutherland_hodgman_clip(transformed_vertices, clipping_window_coords)
                if clipped_rect_vertices:
                    glColor3fv(obj['color'])
                    glBegin(GL_POLYGON) # Gunakan GL_POLYGON untuk menggambar poligon umum
                    for vertex in clipped_rect_vertices:
                        glVertex2f(vertex[0], vertex[1])
                    glEnd()
        else: # Clipping dinonaktifkan, gambar objek seperti biasa (tanpa pemotongan).
            # Terapkan transformasi OpenGL di sini untuk rendering tanpa clipping.
            glPushMatrix() # Simpan matriks sebelum transformasi.
            if 'translate' in current_obj_transforms:
                tx, ty = current_obj_transforms['translate']
                glTranslatef(tx, ty, 0.0)
            if 'rotate' in current_obj_transforms:
                angle = current_obj_transforms['rotate']
                glRotatef(angle, 0.0, 0.0, 1.0) 
            if 'scale' in current_obj_transforms:
                sx, sy = current_obj_transforms['scale']
                glScalef(sx, sy, 1.0)

            if obj['type'] == DRAW_MODE_POINT:
                draw_point(obj['points'][0][0], obj['points'][0][1], obj['color'], obj['thickness'])
            elif obj['type'] == DRAW_MODE_LINE:
                draw_line(obj['points'][0], obj['points'][1], obj['color'], obj['thickness'])
            elif obj['type'] == DRAW_MODE_TRIANGLE:
                draw_triangle(obj['points'][0], obj['points'][1], obj['points'][2], obj['color'])
            elif obj['type'] == DRAW_MODE_ELLIPSE:
                draw_ellipse(obj['points'][0][0], obj['points'][0][1], obj['points'][1][0], obj['points'][1][1], obj['color'], filled=True, thickness=obj['thickness'])
            elif obj['type'] == DRAW_MODE_RECTANGLE:
                draw_rectangle(obj['points'][0], obj['points'][1], obj['color'], filled=True, thickness=obj['thickness'])
            glPopMatrix()


        # --- Menarik Highlight untuk Objek yang Dipilih ---
        if i == selected_object_index:
            glColor3f(1.0, 1.0, 0.0) # Warna kuning untuk highlight.
            glLineWidth(3.0) # Ketebalan garis highlight.

            # Untuk menggambar highlight, kita perlu menerapkan transformasi objek
            # dan kemudian menggambar bentuk highlight.
            glPushMatrix()
            current_obj_transforms = obj.get('transformations', {})
            if 'translate' in current_obj_transforms:
                tx, ty = current_obj_transforms['translate']
                glTranslatef(tx, ty, 0.0)
            if 'rotate' in current_obj_transforms:
                angle = current_obj_transforms['rotate']
                glRotatef(angle, 0.0, 0.0, 1.0)
            if 'scale' in current_obj_transforms:
                sx, sy = current_obj_transforms['scale']
                glScalef(sx, sy, 1.0)

            # Gambar bentuk highlight berdasarkan tipe objek.
            if obj['type'] == DRAW_MODE_POINT:
                x, y = obj['points'][0]
                glBegin(GL_LINE_LOOP)
                glVertex2f(x - 0.03, y - 0.03) # Ukuran kotak highlight.
                glVertex2f(x + 0.03, y - 0.03)
                glVertex2f(x + 0.03, y + 0.03)
                glVertex2f(x - 0.03, y + 0.03)
                glEnd()
            elif obj['type'] == DRAW_MODE_LINE:
                draw_line(obj['points'][0], obj['points'][1], color=[1.0,1.0,0.0], thickness=obj['thickness']+2)
            elif obj['type'] == DRAW_MODE_TRIANGLE:
                glBegin(GL_LINE_LOOP)
                for p in obj['points']:
                    glVertex2f(p[0], p[1])
                glEnd()
            elif obj['type'] == DRAW_MODE_ELLIPSE:
                center_x, center_y = obj['points'][0]
                radius_x, radius_y = obj['points'][1]
                ellipse_segments = draw_ellipse(center_x, center_y, radius_x, radius_y, color=[1.0,1.0,0.0], filled=False, thickness=3.0)
                if ellipse_segments:
                    for segment in ellipse_segments:
                        draw_line(segment[0], segment[1], color=[1.0,1.0,0.0], thickness=3.0)
            elif obj['type'] == DRAW_MODE_RECTANGLE:
                draw_rectangle(obj['points'][0], obj['points'][1], color=[1.0,1.0,0.0], filled=False, thickness=3.0)
            glPopMatrix()


    # Menggambar jendela clipping (garis batas) di atas semua objek.
    glColor3f(0.0, 1.0, 1.0) # Warna cyan.
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(clipping_window_coords['x_min'], clipping_window_coords['y_min'])
    glVertex2f(clipping_window_coords['x_max'], clipping_window_coords['y_min'])
    glVertex2f(clipping_window_coords['x_max'], clipping_window_coords['y_max'])
    glVertex2f(clipping_window_coords['x_min'], clipping_window_coords['y_max'])
    glEnd()

    # Menggambar titik-titik sementara yang sedang diinput oleh mouse.
    if current_draw_mode in [DRAW_MODE_LINE, DRAW_MODE_TRIANGLE, DRAW_MODE_ELLIPSE, DRAW_MODE_RECTANGLE, DRAW_MODE_CLIP_WINDOW] and drawing_points:
        glPointSize(8.0)
        glColor3f(1.0, 1.0, 0.0) # Kuning.
        glBegin(GL_POINTS)
        for p in drawing_points:
            glVertex2f(p[0], p[1])
        glEnd()

    glutSwapBuffers()
    redraw_needed = False

def idle():
    """Fungsi idle dipanggil oleh GLUT saat tidak ada event lain yang menunggu."""
    global redraw_needed
    if redraw_needed:
        glutPostRedisplay()
    time.sleep(0.01)

# --- Penanganan Input Mouse OpenGL ---
def mouse_handler(button, state, x, y):
    """Fungsi callback untuk event klik mouse di jendela OpenGL."""
    global current_draw_mode, drawing_points, drawn_objects, clipping_window_coords, redraw_needed, selected_object_index, \
           is_dragging_clipping_window, drag_start_x, drag_start_y, drag_offset_x, drag_offset_y

    # Konversi koordinat layar (piksel) ke koordinat dunia OpenGL (-1.0 ke 1.0).
    gl_x = (x / (glutGet(GLUT_WINDOW_WIDTH) / 2.0)) - 1.0
    gl_y = 1.0 - (y / (glutGet(GLUT_WINDOW_HEIGHT) / 2.0)) # Sumbu Y terbalik: layar Y+ ke bawah, OpenGL Y+ ke atas.

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_draw_mode == DRAW_MODE_POINT:
            drawn_objects.append({
                'type': DRAW_MODE_POINT,
                'points': [[gl_x, gl_y]],
                'color': list(current_draw_color),
                'thickness': current_line_thickness,
                'transformations': {}
            })
            logging.info(f"Titik digambar di ({gl_x:.2f}, {gl_y:.2f})")
            redraw_needed = True

        elif current_draw_mode == DRAW_MODE_LINE:
            drawing_points.append([gl_x, gl_y])
            if len(drawing_points) == 2:
                drawn_objects.append({
                    'type': DRAW_MODE_LINE,
                    'points': [drawing_points[0], drawing_points[1]],
                    'color': list(current_draw_color),
                    'thickness': current_line_thickness,
                    'transformations': {}
                })
                logging.info(f"Garis digambar dari {drawing_points[0]} ke {drawing_points[1]}")
                drawing_points.clear()
                redraw_needed = True

        elif current_draw_mode == DRAW_MODE_TRIANGLE:
            drawing_points.append([gl_x, gl_y])
            if len(drawing_points) == 3:
                drawn_objects.append({
                    'type': DRAW_MODE_TRIANGLE,
                    'points': [drawing_points[0], drawing_points[1], drawing_points[2]],
                    'color': list(current_draw_color),
                    'thickness': current_line_thickness,
                    'transformations': {}
                })
                logging.info(f"Segitiga digambar dengan verteks: {drawing_points}")
                drawing_points.clear()
                redraw_needed = True

        elif current_draw_mode == DRAW_MODE_ELLIPSE:
            drawing_points.append([gl_x, gl_y])
            if len(drawing_points) == 2:
                center_x, center_y = drawing_points[0]
                radius_x = abs(gl_x - center_x)
                radius_y = abs(gl_y - center_y)
                if radius_x == 0: radius_x = 0.01
                if radius_y == 0: radius_y = 0.01

                drawn_objects.append({
                    'type': DRAW_MODE_ELLIPSE,
                    'points': [[center_x, center_y], [radius_x, radius_y]],
                    'color': list(current_draw_color),
                    'thickness': current_line_thickness,
                    'transformations': {}
                })
                logging.info(f"Elips digambar di tengah ({center_x:.2f}, {center_y:.2f}) dengan radius ({radius_x:.2f}, {radius_y:.2f})")
                drawing_points.clear()
                redraw_needed = True

        elif current_draw_mode == DRAW_MODE_RECTANGLE:
            drawing_points.append([gl_x, gl_y])
            if len(drawing_points) == 2:
                drawn_objects.append({
                    'type': DRAW_MODE_RECTANGLE,
                    'points': [drawing_points[0], drawing_points[1]],
                    'color': list(current_draw_color),
                    'thickness': current_line_thickness,
                    'transformations': {}
                })
                logging.info(f"Persegi digambar dari {drawing_points[0]} ke {drawing_points[1]}")
                drawing_points.clear()
                redraw_needed = True

        elif current_draw_mode == DRAW_MODE_CLIP_WINDOW:
            drawing_points.append([gl_x, gl_y])
            if len(drawing_points) == 2:
                x1, y1 = drawing_points[0]
                x2, y2 = drawing_points[1]
                clipping_window_coords['x_min'] = min(x1, x2)
                clipping_window_coords['y_min'] = min(y1, y2)
                clipping_window_coords['x_max'] = max(x1, x2)
                clipping_window_coords['y_max'] = max(y1, y2)
                logging.info(f"Jendela clipping diatur ke: {clipping_window_coords}")
                drawing_points.clear()
                redraw_needed = True
                current_draw_mode = DRAW_MODE_NONE

        elif current_draw_mode == DRAW_MODE_NONE: # Mode seleksi objek atau drag window.
            selected_object_index = -1 # Reset pilihan sebelumnya.
            
            # --- Cek apakah klik berada di dalam jendela clipping (untuk memulai drag) ---
            if (clipping_window_coords['x_min'] <= gl_x <= clipping_window_coords['x_max'] and
                clipping_window_coords['y_min'] <= gl_y <= clipping_window_coords['y_max'] and
                clipping_enabled):
                
                is_dragging_clipping_window = True
                drag_start_x = gl_x
                drag_start_y = gl_y
                drag_offset_x = gl_x - clipping_window_coords['x_min']
                drag_offset_y = gl_y - clipping_window_coords['y_min']
                logging.info("Memulai drag jendela clipping.")
            else: # Jika tidak drag window, coba pilih objek.
                for i in range(len(drawn_objects) - 1, -1, -1):
                    obj = drawn_objects[i]
                    
                    # Dapatkan koordinat objek setelah transformasi untuk cek klik yang lebih akurat
                    transformed_object_points = [apply_object_transform_to_point(p, obj.get('transformations', {})) for p in obj['points']]
                    
                    is_clicked = False

                    if obj['type'] == DRAW_MODE_POINT:
                        p = transformed_object_points[0]
                        if (gl_x - p[0])**2 + (gl_y - p[1])**2 < 0.03**2:
                            is_clicked = True
                    elif obj['type'] == DRAW_MODE_LINE:
                        p1, p2 = transformed_object_points[0], transformed_object_points[1]
                        if ((gl_x - p1[0])**2 + (gl_y - p1[1])**2 < 0.03**2 or
                            (gl_x - p2[0])**2 + (gl_y - p2[1])**2 < 0.03**2):
                            is_clicked = True
                    elif obj['type'] == DRAW_MODE_TRIANGLE:
                        for p in transformed_object_points:
                            if (gl_x - p[0])**2 + (gl_y - p[1])**2 < 0.03**2:
                                is_clicked = True
                                break
                    elif obj['type'] == DRAW_MODE_ELLIPSE:
                        center_x, center_y = transformed_object_points[0]
                        radius_x, radius_y = obj['points'][1][0], obj['points'][1][1]
                        if 'scale' in obj.get('transformations', {}):
                            radius_x *= obj['transformations']['scale'][0]
                            radius_y *= obj['transformations']['scale'][1]

                        if radius_x > 0 and radius_y > 0 and \
                           ((gl_x - center_x)**2 / radius_x**2 + (gl_y - center_y)**2 / radius_y**2) <= 1.05**2:
                            is_clicked = True
                    elif obj['type'] == DRAW_MODE_RECTANGLE:
                        x1, y1 = transformed_object_points[0]
                        x2, y2 = transformed_object_points[1]
                        
                        min_x = min(x1, x2)
                        max_x = max(x1, x2)
                        min_y = min(y1, y2)
                        max_y = max(y1, y2)

                        if min_x <= gl_x <= max_x and min_y <= gl_y <= max_y:
                            is_clicked = True

                    if is_clicked:
                        selected_object_index = i
                        logging.info(f"Objek type {obj['type']} di indeks {selected_object_index} dipilih.")
                        break
                
                if selected_object_index == -1 and not is_dragging_clipping_window:
                    logging.info("Tidak ada objek yang dipilih.")
            redraw_needed = True


    # Penanganan mouse lepas (mengakhiri drag)
    if button == GLUT_LEFT_BUTTON and state == GLUT_UP:
        if is_dragging_clipping_window:
            is_dragging_clipping_window = False
            logging.info("Mengakhiri drag jendela clipping.")
            redraw_needed = True

    # Penanganan klik kanan mouse (contoh: untuk menghapus semua objek)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        drawn_objects.clear()
        drawing_points.clear()
        selected_object_index = -1
        logging.info("Semua objek dihapus.")
        redraw_needed = True

# --- Tambahan: Mouse Motion Handler untuk Dragging ---
def mouse_motion_handler(x, y):
    """
    Fungsi callback untuk event gerakan mouse.
    Digunakan untuk menggeser jendela clipping saat sedang di-drag.
    """
    global is_dragging_clipping_window, drag_offset_x, drag_offset_y, clipping_window_coords, redraw_needed

    if is_dragging_clipping_window:
        # Konversi koordinat layar ke OpenGL
        gl_x = (x / (glutGet(GLUT_WINDOW_WIDTH) / 2.0)) - 1.0
        gl_y = 1.0 - (y / (glutGet(GLUT_WINDOW_HEIGHT) / 2.0))

        # Hitung posisi baru sudut kiri bawah window
        new_x_min = gl_x - drag_offset_x
        new_y_min = gl_y - drag_offset_y

        # Hitung delta pergerakan
        delta_x = new_x_min - clipping_window_coords['x_min']
        delta_y = new_y_min - clipping_window_coords['y_min']

        # Geser seluruh window
        clipping_window_coords['x_min'] += delta_x
        clipping_window_coords['y_min'] += delta_y
        clipping_window_coords['x_max'] += delta_x
        clipping_window_coords['y_max'] += delta_y

        redraw_needed = True # Minta redraw untuk update visual yang halus
        glutPostRedisplay() # Perlu segera di-redraw untuk animasi halus


# --- Handler Perintah dari Socket (untuk Komunikasi Flask -> PyOpenGL) ---
def handle_incoming_command(command_data):
    global current_line_thickness, current_draw_color, redraw_needed, \
           current_draw_mode, drawn_objects, clipping_window_coords, clipping_enabled, \
           selected_object_index

    command_type = command_data.get("type")
    action = command_data.get("action")
    
    if command_type == "transform":
        if selected_object_index != -1 and selected_object_index < len(drawn_objects):
            obj = drawn_objects[selected_object_index]
            if 'transformations' not in obj: obj['transformations'] = {}

            if action == "translate":
                tx = command_data.get("x", 0) / 100.0
                ty = command_data.get("y", 0) / 100.0
                obj['transformations']['translate'] = [
                    obj['transformations'].get('translate', [0.0, 0.0])[0] + tx,
                    obj['transformations'].get('translate', [0.0, 0.0])[1] + ty
                ]
                logging.info(f"Translasi diterapkan pada objek indeks {selected_object_index}.")
            elif action == "rotate":
                angle_delta = command_data.get("angle", 0)
                obj['transformations']['rotate'] = obj['transformations'].get('rotate', 0) + angle_delta
                logging.info(f"Rotasi {angle_delta} derajat diterapkan pada objek indeks {selected_object_index}.")
            elif action == "scale":
                scale_x = command_data.get("scale_x", 1.0)
                scale_y = command_data.get("scale_y", 1.0)
                obj['transformations']['scale'] = [
                    obj['transformations'].get('scale', [1.0, 1.0])[0] * scale_x,
                    obj['transformations'].get('scale', [1.0, 1.0])[1] * scale_y
                ]
                logging.info(f"Skala ({scale_x:.2f}, {scale_y:.2f}) diterapkan pada objek indeks {selected_object_index}.")
            elif action == "reset_transforms":
                obj['transformations'] = {}
                logging.info(f"Transformasi objek indeks {selected_object_index} direset.")
            redraw_needed = True
        else:
            logging.info("Tidak ada objek yang dipilih untuk transformasi.")

    elif command_type == "draw_settings":
        # Jika ada objek yang dipilih, terapkan perubahan warna/ketebalan padanya.
        if selected_object_index != -1 and selected_object_index < len(drawn_objects):
            obj = drawn_objects[selected_object_index]
            if "thickness" in command_data:
                obj['thickness'] = float(command_data["thickness"])
            if "color" in command_data:
                hex_color = command_data["color"].lstrip('#')
                rgb_tuple = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                obj['color'] = list(rgb_tuple)
            logging.info(f"Pengaturan warna/ketebalan diperbarui untuk objek indeks {selected_object_index}.")
            redraw_needed = True
        else: # Jika tidak ada objek yang dipilih, setel current_draw_color/thickness untuk objek baru.
            if "thickness" in command_data:
                current_line_thickness = float(command_data["thickness"])
            if "color" in command_data:
                hex_color = command_data["color"].lstrip('#')
                rgb_tuple = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                current_draw_color = list(rgb_tuple)
            logging.info(f"Pengaturan gambar diperbarui untuk objek baru: ketebalan={current_line_thickness}, warna={current_draw_color}")
            redraw_needed = True

    elif command_type == "draw_mode":
        mode_str = command_data.get("mode")
        drawing_points.clear()
        selected_object_index = -1
        if mode_str == "point": current_draw_mode = DRAW_MODE_POINT
        elif mode_str == "line": current_draw_mode = DRAW_MODE_LINE
        elif mode_str == "triangle": current_draw_mode = DRAW_MODE_TRIANGLE
        elif mode_str == "ellipse": current_draw_mode = DRAW_MODE_ELLIPSE
        elif mode_str == "rectangle": current_draw_mode = DRAW_MODE_RECTANGLE
        elif mode_str == "none": current_draw_mode = DRAW_MODE_NONE
        elif mode_str == "clear_all":
            drawn_objects.clear()
            current_draw_mode = DRAW_MODE_NONE
            selected_object_index = -1
            logging.info("Semua objek dihapus.")
        logging.info(f"Mode gambar diatur ke: {mode_str}")
        redraw_needed = True

    elif command_type == "clipping":
        action = command_data.get("action")
        if action == "enable":
            clipping_enabled = True
            logging.info("Clipping diaktifkan.")
        elif action == "disable":
            clipping_enabled = False
            logging.info("Clipping dinonaktifkan.")
        elif action == "set_window_mode":
            current_draw_mode = DRAW_MODE_CLIP_WINDOW
            drawing_points.clear()
            selected_object_index = -1
            logging.info("Mode set window clipping diaktifkan. Klik 2 titik di jendela OpenGL.")
        
        redraw_needed = True

# --- Kelas Aplikasi Flask (untuk Web Panel) ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

class WebControlPanelApp:
    def __init__(self, host, port, pyopengl_host, pyopengl_port):
        self.app = Flask(__name__, static_folder='static', static_url_path='')
        CORS(self.app)
        self.host = host
        self.port = port
        self.pyopengl_host = pyopengl_host
        self.pyopengl_port = pyopengl_port
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return send_from_directory(self.app.static_folder, 'index.html')

        @self.app.route('/api/transform', methods=['POST'])
        def transform_object_api():
            data = request.json
            if not all(k in data for k in ['type', 'action']): 
                return jsonify({"status": "error", "message": "Data transformasi tidak lengkap."}), 400
            
            result = self._send_command_to_pyopengl(data) 
            return jsonify(result)

        @self.app.route('/api/draw_settings', methods=['POST'])
        def update_draw_settings_api():
            data = request.json
            if not all(k in data for k in ['thickness', 'color']):
                return jsonify({"status": "error", "message": "Data pengaturan gambar tidak lengkap."}), 400
            
            command_to_send = {"type": "draw_settings", "thickness": float(data['thickness']), "color": data['color']}
            result = self._send_command_to_pyopengl(command_to_send)
            return jsonify(result)

        @self.app.route('/api/draw_mode', methods=['POST'])
        def set_draw_mode_api():
            data = request.json
            if 'mode' not in data:
                return jsonify({"status": "error", "message": "Mode gambar tidak ditentukan."}), 400
            
            command_to_send = {"type": "draw_mode", "mode": data['mode']}
            result = self._send_command_to_pyopengl(command_to_send)
            return jsonify(result)

        @self.app.route('/api/clipping', methods=['POST'])
        def handle_clipping_api():
            data = request.json
            if 'action' not in data:
                return jsonify({"status": "error", "message": "Aksi clipping tidak ditentukan."}), 400
            
            command_to_send = {"type": "clipping", "action": data['action']}
            result = self._send_command_to_pyopengl(command_to_send)
            return jsonify(result)

    def _send_command_to_pyopengl(self, command_data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((self.pyopengl_host, self.pyopengl_port))
                s.sendall(json.dumps(command_data).encode('utf-8'))
                response_json = s.recv(1024).decode('utf-8')
                return json.loads(response_json)
        except ConnectionRefusedError:
            logging.error("Koneksi ditolak: Pastikan aplikasi PyOpenGL berjalan dan server perintah aktif.")
            return {"status": "error", "message": "Aplikasi PyOpenGL tidak berjalan atau koneksi ditolak."}
        except socket.timeout:
            logging.error("Timeout koneksi ke aplikasi PyOpenGL.")
            return {"status": "error", "message": "Timeout saat berkomunikasi dengan aplikasi PyOpenGL."}
        except json.JSONDecodeError:
            logging.error(f"Gagal menguraikan respon JSON dari PyOpenGL: {response_json}")
            return {"status": "error", "message": "Respon tidak valid dari PyOpenGL."}
        except Exception as e:
            logging.error(f"Kesalahan tak terduga saat mengirim perintah: {e}")
            return {"status": "error", "message": f"Kesalahan internal: {e}"}

    def run_flask_app(self):
        self.app.run(debug=False, port=self.port, use_reloader=False)

# --- Main Execution Block ---
if __name__ == '__main__':
    logging.info("Memulai Aplikasi Grafis PyOpenGL...")
    
    pyopengl_command_server_instance = PyOpenGLCommandServer(
        host=PYOPENGL_APP_HOST, 
        port=PYOPENGL_APP_PORT, 
        command_callback=handle_incoming_command
    )
    pyopengl_command_server_instance.start()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Aplikasi Grafis PyOpenGL Interaktif")

    glClearColor(0.2, 0.2, 0.2, 1.0)
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMouseFunc(mouse_handler)
    glutMotionFunc(mouse_motion_handler)
    
    logging.info("Aplikasi PyOpenGL siap. Silakan buka panel kontrol web Anda di browser.")
    
    logging.info("Memulai Web Control Panel Flask...")
    
    web_panel_app_instance = WebControlPanelApp(
        host=PYOPENGL_APP_HOST, 
        port=FLASK_WEB_PORT,
        pyopengl_host=PYOPENGL_APP_HOST, 
        pyopengl_port=PYOPENGL_APP_PORT
    )
    flask_thread = threading.Thread(
        target=web_panel_app_instance.run_flask_app, 
        daemon=True
    )
    flask_thread.start()
    logging.info(f"Panel Kontrol Web dapat diakses di: http://{PYOPENGL_APP_HOST}:{FLASK_WEB_PORT}/")

    glutMainLoop() 

    pyopengl_command_server_instance.stop()
    logging.info("Aplikasi ditutup dengan bersih.")
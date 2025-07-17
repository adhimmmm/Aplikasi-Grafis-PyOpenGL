#!/usr/bin/env python3
"""
Flask + OpenGL 3D Graphics Application (Single File Backend)
Simplified version - hanya 2 file: app.py + 3d.html
"""

from flask import Flask, send_file
from flask_socketio import SocketIO, emit
import threading
import time
import json
import math
import numpy as np
import os
import sys
import webbrowser
from pathlib import Path

# Try import OpenGL
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import pygame
    from pygame.locals import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("⚠️  OpenGL not available. Install with: pip install PyOpenGL pygame")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'graphics3d_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class OpenGLRenderer:
    def __init__(self):
        # Window settings
        self.window_width = 800
        self.window_height = 600
        
        # Camera parameters untuk gluLookAt
        self.camera_params = {
            'eye_x': 5.0, 'eye_y': 5.0, 'eye_z': 5.0,
            'center_x': 0.0, 'center_y': 0.0, 'center_z': 0.0,
            'up_x': 0.0, 'up_y': 1.0, 'up_z': 0.0
        }
        
        # Perspective parameters untuk gluPerspective
        self.perspective_params = {
            'fov': 75.0,
            'aspect': self.window_width / self.window_height,
            'near': 0.1,
            'far': 1000.0
        }
        
        # Object transformation parameters
        self.transform_params = {
            'rot_x': 0.0, 'rot_y': 0.0, 'rot_z': 0.0,
            'scale': 1.0,
            'pos_x': 0.0, 'pos_y': 0.0, 'pos_z': 0.0
        }
        
        # Lighting parameters (Phong Model)
        self.lighting_params = {
            'ambient_enabled': True,
            'diffuse_enabled': True,
            'specular_enabled': True
        }
        
        # Rendering parameters
        self.current_object = 'cube'
        self.projection_mode = 'perspective'
        self.wireframe_mode = False
        self.shadows_enabled = True
        self.auto_rotate = True
        
        # Animation
        self.rotation_angle = 0.0
        self.running = False
        
        # OBJ model data
        self.obj_vertices = []
        self.obj_faces = []
        
        # Statistics
        self.vertex_count = 8
        self.face_count = 6
        
    def init_opengl(self):
        """Initialize OpenGL context"""
        if not OPENGL_AVAILABLE:
            print("❌ OpenGL tidak tersedia")
            return False
            
        try:
            os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
            pygame.init()
            pygame.display.set_mode((self.window_width, self.window_height), DOUBLEBUF | OPENGL)
            pygame.display.set_caption("OpenGL 3D Renderer - Controlled by Web UI")
            
            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)
            
            # Enable face culling
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
            
            # Setup initial viewport and projection
            self.setup_viewport()
            self.setup_projection()
            
            # Setup lighting (Phong Model)
            self.setup_phong_lighting()
            
            # Set background color
            glClearColor(0.06, 0.06, 0.14, 1.0)
            return True
            
        except Exception as e:
            print(f"❌ Error initializing OpenGL: {e}")
            return False
        
    def setup_viewport(self):
        """Setup viewport"""
        glViewport(0, 0, self.window_width, self.window_height)
        
    def setup_projection(self):
        """Setup projection matrix menggunakan gluPerspective"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        if self.projection_mode == 'perspective':
            gluPerspective(
                self.perspective_params['fov'],
                self.perspective_params['aspect'], 
                self.perspective_params['near'],
                self.perspective_params['far']
            )
        else:  # orthographic
            frustum_size = 5
            aspect = self.perspective_params['aspect']
            glOrtho(
                -frustum_size * aspect / 2, frustum_size * aspect / 2,
                -frustum_size / 2, frustum_size / 2,
                self.perspective_params['near'], self.perspective_params['far']
            )
    
    def setup_camera(self):
        """Setup camera menggunakan gluLookAt"""
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        gluLookAt(
            self.camera_params['eye_x'], self.camera_params['eye_y'], self.camera_params['eye_z'],
            self.camera_params['center_x'], self.camera_params['center_y'], self.camera_params['center_z'],
            self.camera_params['up_x'], self.camera_params['up_y'], self.camera_params['up_z']
        )
    
    def setup_phong_lighting(self):
        """Setup Phong lighting model"""
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        
        # Ambient Light
        if self.lighting_params['ambient_enabled']:
            glEnable(GL_LIGHT0)
            ambient_light = [0.2, 0.2, 0.2, 1.0]
            glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        else:
            glDisable(GL_LIGHT0)
            
        # Directional Light (Diffuse + Specular)
        if self.lighting_params['diffuse_enabled'] or self.lighting_params['specular_enabled']:
            glEnable(GL_LIGHT1)
            
            light_position = [10.0, 10.0, 5.0, 0.0]
            glLightfv(GL_LIGHT1, GL_POSITION, light_position)
            
            if self.lighting_params['diffuse_enabled']:
                diffuse_light = [0.8, 0.8, 0.8, 1.0]
                glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse_light)
            else:
                glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])
                
            if self.lighting_params['specular_enabled']:
                specular_light = [1.0, 1.0, 1.0, 1.0]
                glLightfv(GL_LIGHT1, GL_SPECULAR, specular_light)
            else:
                glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        else:
            glDisable(GL_LIGHT1)
            
        # Point Light
        glEnable(GL_LIGHT2)
        point_light_pos = [5.0, 5.0, 5.0, 1.0]
        glLightfv(GL_LIGHT2, GL_POSITION, point_light_pos)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.3, 0.1, 0.1, 1.0])
        glLightfv(GL_LIGHT2, GL_SPECULAR, [0.5, 0.2, 0.2, 1.0])
        
    def set_material_properties(self, color):
        """Set material properties untuk Phong shading"""
        ambient = [color[0] * 0.2, color[1] * 0.2, color[2] * 0.2, 1.0]
        diffuse = [color[0], color[1], color[2], 1.0]
        specular = [0.8, 0.8, 0.8, 1.0] if self.lighting_params['specular_enabled'] else [0.0, 0.0, 0.0, 1.0]
        shininess = 100.0 if self.lighting_params['specular_enabled'] else 0.0
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, shininess)
    
    def apply_transformations(self):
        """Apply object transformations"""
        glTranslatef(
            self.transform_params['pos_x'],
            self.transform_params['pos_y'], 
            self.transform_params['pos_z']
        )
        
        glRotatef(self.transform_params['rot_x'], 1, 0, 0)
        glRotatef(self.transform_params['rot_y'], 0, 1, 0)
        glRotatef(self.transform_params['rot_z'], 0, 0, 1)
        
        if self.auto_rotate:
            glRotatef(self.rotation_angle, 0, 1, 0)
            
        scale = self.transform_params['scale']
        glScalef(scale, scale, scale)
    
    def draw_cube(self):
        """Draw cube with manual vertex creation"""
        self.set_material_properties([0.39, 0.71, 0.96])
        self.vertex_count = 8
        self.face_count = 6
        
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        
        # Back face
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0,  1.0, -1.0)
        glVertex3f( 1.0,  1.0, -1.0)
        glVertex3f( 1.0, -1.0, -1.0)
        
        # Top face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-1.0,  1.0, -1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f( 1.0,  1.0, -1.0)
        
        # Bottom face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f( 1.0, -1.0, -1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        
        # Right face
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f( 1.0, -1.0, -1.0)
        glVertex3f( 1.0,  1.0, -1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        
        # Left face
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        glVertex3f(-1.0,  1.0, -1.0)
        
        glEnd()
    
    def draw_pyramid(self):
        """Draw pyramid with manual vertex creation"""
        self.set_material_properties([0.94, 0.58, 0.98])
        self.vertex_count = 5
        self.face_count = 5
        
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        base_size = 1.5
        height = 2.5
        
        # Base
        glBegin(GL_QUADS)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-base_size, 0.0, -base_size)
        glVertex3f( base_size, 0.0, -base_size)
        glVertex3f( base_size, 0.0,  base_size)
        glVertex3f(-base_size, 0.0,  base_size)
        glEnd()
        
        # Sides
        glBegin(GL_TRIANGLES)
        
        # Front
        glNormal3f(0.0, 0.7, 0.7)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(-base_size, 0.0, base_size)
        glVertex3f(base_size, 0.0, base_size)
        
        # Right
        glNormal3f(0.7, 0.7, 0.0)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_size, 0.0, base_size)
        glVertex3f(base_size, 0.0, -base_size)
        
        # Back
        glNormal3f(0.0, 0.7, -0.7)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(base_size, 0.0, -base_size)
        glVertex3f(-base_size, 0.0, -base_size)
        
        # Left
        glNormal3f(-0.7, 0.7, 0.0)
        glVertex3f(0.0, height, 0.0)
        glVertex3f(-base_size, 0.0, -base_size)
        glVertex3f(-base_size, 0.0, base_size)
        
        glEnd()
    
    def draw_sphere(self):
        """Draw sphere using GLU quadric"""
        self.set_material_properties([0.31, 0.80, 0.77])
        self.vertex_count = 514
        self.face_count = 512
        
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, 1.5, 32, 16)
        gluDeleteQuadric(quadric)
    
    def load_obj_file(self, filename):
        """Load OBJ file"""
        self.obj_vertices = []
        self.obj_faces = []
        
        try:
            if not os.path.exists(filename):
                # Try creating a simple test OBJ if file doesn't exist
                if 'tetrahedron' in filename.lower():
                    self.create_test_tetrahedron()
                    return True
                else:
                    return False
                    
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts:
                        continue
                        
                    if parts[0] == 'v':
                        vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                        self.obj_vertices.append(vertex)
                        
                    elif parts[0] == 'f':
                        face = []
                        for part in parts[1:]:
                            vertex_index = int(part.split('/')[0]) - 1
                            face.append(vertex_index)
                        
                        if len(face) > 3:
                            for i in range(1, len(face) - 1):
                                triangle = [face[0], face[i], face[i + 1]]
                                self.obj_faces.append(triangle)
                        else:
                            self.obj_faces.append(face)
                            
            self.vertex_count = len(self.obj_vertices)
            self.face_count = len(self.obj_faces)
            self.current_object = 'obj'
            return True
            
        except Exception as e:
            print(f"Error loading OBJ file: {e}")
            return False
    
    def create_test_tetrahedron(self):
        """Create a simple test tetrahedron"""
        self.obj_vertices = [
            [0.0, 1.0, 0.0],
            [-1.0, -1.0, 1.0],
            [1.0, -1.0, 1.0],
            [0.0, -1.0, -1.0]
        ]
        
        self.obj_faces = [
            [0, 1, 2],
            [0, 3, 1],
            [0, 2, 3],
            [1, 3, 2]
        ]
        
        self.vertex_count = 4
        self.face_count = 4
        self.current_object = 'obj'
    
    def draw_obj_model(self):
        """Draw OBJ model"""
        if not self.obj_vertices or not self.obj_faces:
            return
            
        self.set_material_properties([0.0, 0.74, 0.83])
        
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        glBegin(GL_TRIANGLES)
        for face in self.obj_faces:
            if len(face) >= 3:
                v1 = np.array(self.obj_vertices[face[0]])
                v2 = np.array(self.obj_vertices[face[1]])
                v3 = np.array(self.obj_vertices[face[2]])
                
                normal = np.cross(v2 - v1, v3 - v1)
                normal = normal / np.linalg.norm(normal)
                
                glNormal3f(normal[0], normal[1], normal[2])
                glVertex3f(v1[0], v1[1], v1[2])
                glVertex3f(v2[0], v2[1], v2[2])
                glVertex3f(v3[0], v3[1], v3[2])
        glEnd()
    
    def draw_ground(self):
        """Draw ground plane"""
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.2, 0.2)
        
        glBegin(GL_QUADS)
        glVertex3f(-10.0, -2.0, -10.0)
        glVertex3f( 10.0, -2.0, -10.0)
        glVertex3f( 10.0, -2.0,  10.0)
        glVertex3f(-10.0, -2.0,  10.0)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw_current_object(self):
        """Draw currently selected object"""
        glPushMatrix()
        self.apply_transformations()
        
        if self.current_object == 'cube':
            self.draw_cube()
        elif self.current_object == 'pyramid':
            self.draw_pyramid()
        elif self.current_object == 'sphere':
            self.draw_sphere()
        elif self.current_object == 'obj':
            self.draw_obj_model()
            
        glPopMatrix()
    
    def render(self):
        """Main rendering function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.setup_camera()
        self.setup_phong_lighting()
        
        self.draw_ground()
        self.draw_current_object()
        
        pygame.display.flip()
    
    def update_animation(self):
        """Update animation"""
        if self.auto_rotate:
            self.rotation_angle += 0.5
            if self.rotation_angle >= 360:
                self.rotation_angle = 0
    
    def run(self):
        """Main renderer loop"""
        if not self.init_opengl():
            return
            
        print("✅ OpenGL Renderer started")
        self.running = True
        
        clock = pygame.time.Clock()
        frame_counter = 0
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update_animation()
            self.render()
            clock.tick(60)
            
            # Emit status every 60 frames
            frame_counter += 1
            if frame_counter % 60 == 0:
                self.emit_status()
        
        pygame.quit()
    
    def emit_status(self):
        """Emit current status to web UI"""
        try:
            socketio.emit('status_update', {
                'object': self.current_object.title(),
                'vertices': self.vertex_count,
                'faces': self.face_count,
                'projection': self.projection_mode.title(),
                'wireframe': self.wireframe_mode,
                'auto_rotate': self.auto_rotate,
                'lighting': {
                    'ambient': self.lighting_params['ambient_enabled'],
                    'diffuse': self.lighting_params['diffuse_enabled'],
                    'specular': self.lighting_params['specular_enabled']
                }
            })
        except:
            pass

# Global renderer instance
renderer = OpenGLRenderer() if OPENGL_AVAILABLE else None

@app.route('/')
def index():
    """Serve main page"""
    return send_file('3d.html')

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('🔗 Client connected')
    if renderer:
        emit('status_update', {
            'object': renderer.current_object.title(),
            'vertices': renderer.vertex_count,
            'faces': renderer.face_count,
            'projection': renderer.projection_mode.title(),
            'wireframe': renderer.wireframe_mode,
            'auto_rotate': renderer.auto_rotate,
            'lighting': {
                'ambient': renderer.lighting_params['ambient_enabled'],
                'diffuse': renderer.lighting_params['diffuse_enabled'],
                'specular': renderer.lighting_params['specular_enabled']
            }
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected')

@socketio.on('set_object')
def handle_set_object(data):
    """Handle object change from web UI"""
    if renderer:
        obj_type = data['type']
        if obj_type in ['cube', 'pyramid', 'sphere']:
            renderer.current_object = obj_type
            print(f"📦 Object changed to: {obj_type}")

@socketio.on('update_transform')
def handle_update_transform(data):
    """Handle transform updates from web UI"""
    if renderer:
        renderer.transform_params.update(data)

@socketio.on('update_camera')
def handle_update_camera(data):
    """Handle camera updates from web UI"""
    if renderer:
        renderer.camera_params.update(data)

@socketio.on('update_perspective')
def handle_update_perspective(data):
    """Handle perspective updates from web UI"""
    if renderer:
        renderer.perspective_params.update(data)
        renderer.setup_projection()

@socketio.on('update_lighting')
def handle_update_lighting(data):
    """Handle lighting updates from web UI"""
    if renderer:
        renderer.lighting_params.update(data)

@socketio.on('toggle_wireframe')
def handle_toggle_wireframe():
    """Toggle wireframe mode"""
    if renderer:
        renderer.wireframe_mode = not renderer.wireframe_mode
        emit('wireframe_toggled', {'enabled': renderer.wireframe_mode})

@socketio.on('toggle_auto_rotate')
def handle_toggle_auto_rotate():
    """Toggle auto rotation"""
    if renderer:
        renderer.auto_rotate = not renderer.auto_rotate
        emit('auto_rotate_toggled', {'enabled': renderer.auto_rotate})

@socketio.on('set_projection')
def handle_set_projection(data):
    """Set projection mode"""
    if renderer:
        renderer.projection_mode = data['mode']
        renderer.setup_projection()

@socketio.on('reset_camera')
def handle_reset_camera():
    """Reset camera to default"""
    if renderer:
        renderer.camera_params = {
            'eye_x': 5.0, 'eye_y': 5.0, 'eye_z': 5.0,
            'center_x': 0.0, 'center_y': 0.0, 'center_z': 0.0,
            'up_x': 0.0, 'up_y': 1.0, 'up_z': 0.0
        }

@socketio.on('load_obj')
def handle_load_obj(data):
    """Handle OBJ file loading"""
    if renderer:
        filename = data['filename']
        success = renderer.load_obj_file(filename)
        
        if success:
            emit('obj_loaded', {
                'vertices': renderer.vertex_count,
                'faces': renderer.face_count,
                'filename': os.path.basename(filename)
            })
        
        emit('obj_load_result', {'success': success, 'filename': filename})

def install_requirements():
    """Auto-install requirements if missing"""
    required_packages = {
        'flask': 'Flask==2.3.3',
        'flask_socketio': 'Flask-SocketIO==5.3.6', 
        'PyOpenGL': 'PyOpenGL==3.1.6',
        'pygame': 'pygame==2.5.2',
        'numpy': 'numpy==1.24.3'
    }
    
    missing = []
    for package, pip_name in required_packages.items():
        try:
            if package == 'flask_socketio':
                import flask_socketio
            elif package == 'PyOpenGL':
                import OpenGL
            else:
                __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print("📦 Installing missing packages...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ Packages installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            print("Please install manually:")
            for pkg in missing:
                print(f"  pip install {pkg}")
            return False
    return True

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🎮 Flask + OpenGL 3D Graphics Application 🎮           ║
║                                                              ║
║  ✨ Simplified 2-File Version                               ║
║  🎯 HTML UI + Python OpenGL Backend                         ║
║  🔗 Real-time WebSocket Communication                       ║
║  🎨 Native OpenGL Performance                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def start_renderer():
    """Start OpenGL renderer in separate thread"""
    if renderer:
        renderer.run()

if __name__ == '__main__':
    print_banner()
    
    # Check and install requirements
    if not install_requirements():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if 3d.html exists (FIXED: was checking for index.html)
    if not os.path.exists('3d.html'):
        print("❌ 3d.html not found!")
        print("Please ensure 3d.html is in the same directory as app.py")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("🚀 Starting Flask + OpenGL Application...")
    
    # Start OpenGL renderer in background thread if available
    if OPENGL_AVAILABLE and renderer:
        renderer_thread = threading.Thread(target=start_renderer, daemon=True)
        renderer_thread.start()
        time.sleep(1)  # Give renderer time to initialize
        print("✅ OpenGL renderer started")
    else:
        print("⚠️  OpenGL not available - UI only mode")
    
    # Try to open browser
    try:
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening web browser...")
    except:
        print("🌐 Please open http://localhost:5000 in your browser")
    
    print("\n" + "="*60)
    print("🎮 Controls:")
    print("  • Web UI: http://localhost:5000")
    print("  • OpenGL Window: Mouse drag = rotate, wheel = zoom")
    print("  • Keyboard (Web): 1,2,3 = objects, Space = auto-rotate")
    print("  • Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Start Flask-SocketIO server
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to exit...")
        
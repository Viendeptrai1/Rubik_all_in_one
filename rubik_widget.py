from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from rubik_3x3 import RubikCube
from rubik_2x2 import RubikCube2x2

class RubikWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubik = RubikCube()
        self.cube = self.rubik  # Thêm alias để truy cập trực tiếp đến đối tượng Rubik
        self.last_pos = QPoint()
        self.zoom = -10
        self.move_queue = []

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.8, 0.9, 1.0, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Cập nhật animation
        animation_completed = self.rubik.update_animation()
        
        # Nếu animation đã hoàn thành, cập nhật hiển thị trạng thái
        if animation_completed:
            # Thông báo cho controls widget cập nhật hiển thị trạng thái
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                window = self.parent().parent()
                if hasattr(window, 'controls'):
                    window.controls.update_state_display()
            
            # Nếu có nước đi tiếp theo trong hàng đợi
            if self.move_queue and not self.rubik.animating:
                face, clockwise = self.move_queue.pop(0)
                # Áp dụng nước đi kế tiếp
                self.rubik.rotate_face(face, clockwise)
                
        # Hoặc nếu không có animation đang chạy và có nước đi trong hàng đợi
        elif not self.rubik.animating and self.move_queue:
            face, clockwise = self.move_queue.pop(0)
            # Áp dụng nước đi kế tiếp
            self.rubik.rotate_face(face, clockwise)
        
        # Vẽ khối Rubik
        self.rubik.draw_cube()
        
        # Kích hoạt vẽ lại để tiếp tục animation
        self.update()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        if event.buttons() & Qt.LeftButton:
            self.rubik.rotate_cube(dx * 0.5, dy * 0.5)
        self.last_pos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom += delta
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        self.update()


class RubikWidget2x2(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubik = RubikCube2x2()
        self.cube = self.rubik  # Thêm alias để truy cập trực tiếp đến đối tượng Rubik
        self.last_pos = QPoint()
        self.zoom = -5  # Khởi tạo gần hơn vì rubik 2x2 nhỏ hơn
        self.move_queue = []

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.8, 0.9, 1.0, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Cập nhật animation
        animation_completed = self.rubik.update_animation()
        
        # Nếu animation đã hoàn thành, cập nhật hiển thị trạng thái
        if animation_completed:
            # Thông báo cho controls widget cập nhật hiển thị trạng thái
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                window = self.parent().parent()
                if hasattr(window, 'controls'):
                    window.controls.update_state_display()
            
            # Nếu có nước đi tiếp theo trong hàng đợi
            if self.move_queue and not self.rubik.animating:
                face, clockwise = self.move_queue.pop(0)
                # Áp dụng nước đi kế tiếp
                self.rubik.rotate_face(face, clockwise)
                
        # Hoặc nếu không có animation đang chạy và có nước đi trong hàng đợi
        elif not self.rubik.animating and self.move_queue:
            face, clockwise = self.move_queue.pop(0)
            # Áp dụng nước đi kế tiếp
            self.rubik.rotate_face(face, clockwise)
        
        # Vẽ khối Rubik
        self.rubik.draw_cube()
        
        # Kích hoạt vẽ lại để tiếp tục animation
        self.update()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        if event.buttons() & Qt.LeftButton:
            self.rubik.rotate_cube(dx * 0.5, dy * 0.5)
        self.last_pos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom += delta
        self.update()

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from rubik import RubikCube

class RubikWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubik = RubikCube()
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
        if self.rubik.update_animation():
            # Animation completed, check queue
            if self.move_queue and not self.rubik.animating:
                face, clockwise = self.move_queue.pop(0)
                self.rubik.rotate_face(face, clockwise)
        self.rubik.draw_cube()
        self.update()  # Trigger repaint for animations

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

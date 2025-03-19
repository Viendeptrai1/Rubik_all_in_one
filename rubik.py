import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Piece:
    """
    Lớp đại diện cho một khối nhỏ trong Rubik
    Mỗi khối có vị trí (x, y, z) và màu sắc cho mỗi mặt
    """
    def __init__(self, position, colors):
        """
        Khởi tạo một khối Rubik
        :param position: Tuple (x, y, z) chỉ vị trí ban đầu của khối
        :param colors: Dict chứa màu của các mặt {'F': color, 'B': color, ...}
        """
        self.position = np.array(position)  # Vị trí trong không gian 3D
        self.colors = colors.copy()
        
        # Các đỉnh của khối
        self.vertices = {
            'F': [(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5)],
            'B': [(0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)],
            'L': [(-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5)],
            'R': [(0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)],
            'U': [(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)],
            'D': [(0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)]
        }
    
    def draw(self):
        """Vẽ khối với OpenGL"""
        glPushMatrix()
        
        # Di chuyển đến vị trí hiện tại
        glTranslatef(self.position[0] - 1.0,
                    self.position[1] - 1.0,
                    self.position[2] - 1.0)
        
        # Vẽ từng mặt của khối
        for face, vertices in self.vertices.items():
            if face in self.colors:
                # Vẽ viền đen
                glLineWidth(3.0)
                for offset in [(0, 0, 0), (0.008, 0.008, 0.008), (-0.008, -0.008, -0.008)]:
                    glBegin(GL_LINE_LOOP)
                    glColor3f(0, 0, 0)
                    for v in vertices:
                        glVertex3f(v[0] + offset[0], v[1] + offset[1], v[2] + offset[2])
                    glEnd()
                
                # Vẽ mặt với màu tương ứng
                glBegin(GL_QUADS)
                glColor3f(*self.colors[face])
                for v in vertices:
                    glVertex3f(*v)
                glEnd()
        
        glPopMatrix()
    
    def rotate(self, axis, angle):
        """
        Xoay khối quanh một trục
        :param axis: Trục xoay ('x', 'y', 'z')
        :param angle: Góc xoay (độ)
        """
        # Chuyển đổi góc sang radian
        rad = np.radians(angle)
        cos_a = np.cos(rad)
        sin_a = np.sin(rad)
        
        # Ma trận xoay
        if axis == 'x':
            rot_matrix = np.array([
                [1, 0, 0],
                [0, cos_a, -sin_a],
                [0, sin_a, cos_a]
            ])
            face_map = {'U': 'F', 'F': 'D', 'D': 'B', 'B': 'U'} if angle > 0 else {'U': 'B', 'B': 'D', 'D': 'F', 'F': 'U'}
        elif axis == 'y':
            rot_matrix = np.array([
                [cos_a, 0, sin_a],
                [0, 1, 0],
                [-sin_a, 0, cos_a]
            ])
            face_map = {'F': 'R', 'R': 'B', 'B': 'L', 'L': 'F'} if angle > 0 else {'F': 'L', 'L': 'B', 'B': 'R', 'R': 'F'}
        else:
            rot_matrix = np.array([
                [cos_a, -sin_a, 0],
                [sin_a, cos_a, 0],
                [0, 0, 1]
            ])
            face_map = {'U': 'L', 'L': 'D', 'D': 'R', 'R': 'U'} if angle > 0 else {'U': 'R', 'R': 'D', 'D': 'L', 'L': 'U'}
        
        # Xoay tọa độ
        center = np.array([1, 1, 1])  # Tâm xoay là điểm giữa của khối Rubik
        pos = self.position - center  # Dịch về gốc tọa độ
        new_pos = np.dot(rot_matrix, pos)  # Xoay
        self.position = np.round(new_pos + center).astype(int)  # Dịch về vị trí cũ
        
        # Cập nhật màu sắc
        new_colors = {face: self.colors[face] for face in self.colors}  # Giữ nguyên màu sắc
        for old_face, new_face in face_map.items():
            if old_face in self.colors:
                new_colors[new_face] = self.colors[old_face]
        self.colors = new_colors

class RubikCube:
    """
    Lớp quản lý trạng thái và hiển thị Rubik Cube
    """
    # Màu sắc cho các mặt (White, Yellow, Red, Orange, Green, Blue)
    COLORS = {
        'W': (1.0, 1.0, 1.0),  # White - Up
        'Y': (1.0, 1.0, 0.0),  # Yellow - Down
        'R': (1.0, 0.0, 0.0),  # Red - Front
        'O': (1.0, 0.5, 0.0),  # Orange - Back
        'G': (0.0, 1.0, 0.0),  # Green - Left
        'B': (0.0, 0.0, 1.0)   # Blue - Right
    }

    # Định nghĩa các phép xoay chuẩn cho mỗi mặt
    FACE_ROTATIONS = {
        'F': {'axis': 'z', 'pos': 2},  # Mặt trước (z=2)
        'B': {'axis': 'z', 'pos': 0},  # Mặt sau (z=0)
        'L': {'axis': 'x', 'pos': 0},  # Mặt trái (x=0)
        'R': {'axis': 'x', 'pos': 2},  # Mặt phải (x=2)
        'U': {'axis': 'y', 'pos': 2},  # Mặt trên (y=2)
        'D': {'axis': 'y', 'pos': 0}   # Mặt dưới (y=0)
    }

    def __init__(self, size=3):
        """
        Khởi tạo Rubik Cube
        :param size: Kích thước của cube (2 hoặc 3)
        """
        self.size = size
        self.rotation_x = 0  # Góc xoay quanh trục x
        self.rotation_y = 0  # Góc xoay quanh trục y
        
        # Khởi tạo các khối
        self.pieces = []
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    # Xác định màu cho từng mặt của khối
                    colors = {}
                    
                    # Mặt trước (Front) - Đỏ (z = size-1)
                    if z == size-1:
                        colors['F'] = self.COLORS['R']
                    # Mặt sau (Back) - Cam (z = 0)
                    if z == 0:
                        colors['B'] = self.COLORS['O']
                    # Mặt trái (Left) - Xanh lá (x = 0)
                    if x == 0:
                        colors['L'] = self.COLORS['G']
                    # Mặt phải (Right) - Xanh dương (x = size-1)
                    if x == size-1:
                        colors['R'] = self.COLORS['B']
                    # Mặt trên (Up) - Trắng (y = size-1)
                    if y == size-1:
                        colors['U'] = self.COLORS['W']
                    # Mặt dưới (Down) - Vàng (y = 0)
                    if y == 0:
                        colors['D'] = self.COLORS['Y']
                    
                    # Chỉ thêm các khối có ít nhất 1 mặt có màu (các khối nằm ở mặt ngoài)
                    if colors:
                        self.pieces.append(Piece((x, y, z), colors))
        
        # Thông số animation
        self.animating = False
        self.animation_face = None
        self.animation_angle = 0
        self.animation_target = 0
        self.animation_speed = 5  # Độ nhanh của animation (độ/frame)
        self.animation_clockwise = True

    def _get_rotation_matrix(self, axis, angle_deg):
        """Tạo ma trận xoay cho một trục và góc cho trước"""
        angle = np.radians(angle_deg)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        if axis == 'x':
            return np.array([
                [1, 0, 0],
                [0, cos_a, -sin_a],
                [0, sin_a, cos_a]
            ])
        elif axis == 'y':
            return np.array([
                [cos_a, 0, sin_a],
                [0, 1, 0],
                [-sin_a, 0, cos_a]
            ])
        else:  # z
            return np.array([
                [cos_a, -sin_a, 0],
                [sin_a, cos_a, 0],
                [0, 0, 1]
            ])

    def draw_cube(self):
        """Vẽ toàn bộ Rubik Cube"""
        glPushMatrix()
        
        # Áp dụng phép xoay toàn cục
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Vẽ từng khối
        for piece in self.pieces:
            if self.animating:
                is_rotating = self._is_piece_on_face(piece, self.animation_face)
                if is_rotating:
                    glPushMatrix()
                    # Áp dụng xoay animation theo định nghĩa trong FACE_ROTATIONS
                    rot = self.FACE_ROTATIONS[self.animation_face]
                    if rot['axis'] == 'x':
                        glRotatef(self.animation_angle, 1, 0, 0)
                    elif rot['axis'] == 'y':
                        glRotatef(self.animation_angle, 0, 1, 0)
                    else:  # z
                        glRotatef(self.animation_angle, 0, 0, 1)
                    piece.draw()
                    glPopMatrix()
                else:
                    piece.draw()
            else:
                piece.draw()
        
        glPopMatrix()

    def _is_piece_on_face(self, piece, face):
        """Kiểm tra xem một khối có thuộc mặt đang xoay không"""
        pos = piece.position
        if face == 'F': return pos[2] == self.size-1
        if face == 'B': return pos[2] == 0
        if face == 'L': return pos[0] == 0
        if face == 'R': return pos[0] == self.size-1
        if face == 'U': return pos[1] == self.size-1
        if face == 'D': return pos[1] == 0
        return False

    def rotate_face(self, face, clockwise=True):
        """Bắt đầu xoay một mặt"""
        if self.animating:
            return
            
        self.animating = True
        self.animation_face = face
        self.animation_clockwise = clockwise
        self.animation_angle = 0
        self.animation_target = 90 if clockwise else -90

    def _update_adjacent_faces(self, face, clockwise):
        """Cập nhật các mặt liên quan khi xoay một mặt"""
        # Không cần cập nhật các mặt liên quan vì đã được xử lý trong piece.rotate()
        pass

    def scramble(self, num_moves=20):
        """Xáo trộn Rubik ngẫu nhiên"""
        if self.animating:  # Nếu đang có animation, không thực hiện
            return
            
        import random
        faces = ['F', 'B', 'L', 'R', 'U', 'D']
        moves = []
        
        last_face = None
        for _ in range(num_moves):
            # Tránh lặp lại mặt vừa xoay
            available_faces = [f for f in faces if f != last_face]
            face = random.choice(available_faces)
            last_face = face
            
            clockwise = random.choice([True, False])
            moves.append((face, clockwise))
        
        # Thực hiện move đầu tiên
        if moves:
            face, clockwise = moves.pop(0)
            self.rotate_face(face, clockwise)
            
            # Lưu các moves còn lại vào queue
            self._scramble_queue = moves

    def rotate_cube(self, dx, dy):
        
        self.rotation_y += dx
        self.rotation_x += dy

    def update_animation(self):
        """Cập nhật trạng thái animation

        :return: True nếu animation đã hoàn thành.
        """
        if not self.animating:
            # Nếu có moves trong scramble queue, thực hiện move tiếp theo
            if hasattr(self, '_scramble_queue') and self._scramble_queue:
                face, clockwise = self._scramble_queue.pop(0)
                self.rotate_face(face, clockwise)
            return False

        target = self.animation_target
        current = self.animation_angle
        speed = self.animation_speed

        remaining = target - current
        step = remaining * 0.2

        if abs(step) > speed:
            step = speed if step > 0 else -speed

        self.animation_angle += step

        if abs(target - self.animation_angle) < 0.1:
            self.animation_angle = target
            self._complete_rotation()
            return True

        return False

    def _get_face_pieces(self, face):
        """Lấy tất cả các mảnh thuộc một mặt theo thứ tự: góc và cạnh"""
        rot_info = self.FACE_ROTATIONS[face]
        axis = rot_info['axis']
        pos = rot_info['pos']
        
        face_pieces = []
        for piece in self.pieces:
            if axis == 'x' and piece.position[0] == pos:
                face_pieces.append(piece)
            elif axis == 'y' and piece.position[1] == pos:
                face_pieces.append(piece)
            elif axis == 'z' and piece.position[2] == pos:
                face_pieces.append(piece)
        
        # Sắp xếp các mảnh theo thứ tự góc trước, cạnh sau
        corners = [p for p in face_pieces if self._is_corner_piece(p)]
        edges = [p for p in face_pieces if self._is_edge_piece(p)]
        return corners + edges

    def _is_corner_piece(self, piece):
        """Kiểm tra xem một mảnh có phải là góc không"""
        return len(piece.colors) == 3

    def _is_edge_piece(self, piece):
        """Kiểm tra xem một mảnh có phải là cạnh không"""
        return len(piece.colors) == 2

    def _rotate_colors(self, piece, axis, clockwise):
        """Xoay màu sắc của một mảnh theo trục và chiều xoay"""
        new_colors = {}
        
        if axis == 'x':
            if clockwise:
                color_map = {'U': 'F', 'F': 'D', 'D': 'B', 'B': 'U'}
            else:
                color_map = {'U': 'B', 'B': 'D', 'D': 'F', 'F': 'U'}
        elif axis == 'y':
            if clockwise:
                color_map = {'F': 'R', 'R': 'B', 'B': 'L', 'L': 'F'}
            else:
                color_map = {'F': 'L', 'L': 'B', 'B': 'R', 'R': 'F'}
        else:  # z
            if clockwise:
                color_map = {'U': 'L', 'L': 'D', 'D': 'R', 'R': 'U'}
            else:
                color_map = {'U': 'R', 'R': 'D', 'D': 'L', 'L': 'U'}

        # Áp dụng color map cho các mặt bị ảnh hưởng
        for old_face, color in piece.colors.items():
            if old_face in color_map:
                new_colors[color_map[old_face]] = color
            else:
                new_colors[old_face] = color

        return new_colors

    def _complete_rotation(self):
        """Hoàn thành phép xoay một mặt"""
        if not self.animation_face:
            return

        face = self.animation_face
        rot_info = self.FACE_ROTATIONS[face]
        clockwise = self.animation_clockwise
        
        # Lấy tất cả các mảnh trên mặt đang xoay
        face_pieces = self._get_face_pieces(face)
        
        # Tính toán ma trận xoay
        angle = 90 if clockwise else -90
        rot_matrix = self._get_rotation_matrix(rot_info['axis'], angle)
        
        # Xoay từng mảnh
        center = np.array([1, 1, 1])
        for piece in face_pieces:
            # Cập nhật vị trí
            pos = piece.position - center
            new_pos = np.dot(rot_matrix, pos)
            piece.position = np.round(new_pos + center).astype(int)
            
            # Cập nhật màu sắc
            piece.colors = self._rotate_colors(piece, rot_info['axis'], clockwise)
        
        # Reset trạng thái animation
        self.animating = False
        self.animation_face = None
        self.animation_angle = 0
        self.animation_target = 0

    def __eq__(self, other):
        """Compare two RubikCube instances for equality"""
        if not isinstance(other, RubikCube):
            return False
        
        # Compare pieces based on positions and colors
        if len(self.pieces) != len(other.pieces):
            return False
            
        # Sort pieces by position for consistent comparison
        self_pieces = sorted(self.pieces, key=lambda p: tuple(p.position))
        other_pieces = sorted(other.pieces, key=lambda p: tuple(p.position))
        
        for p1, p2 in zip(self_pieces, other_pieces):
            if tuple(p1.position) != tuple(p2.position) or p1.colors != p2.colors:
                return False
        return True
    
    def __lt__(self, other):
        """Less than comparison - required for some algorithms"""
        # In this case, less than doesn't make semantic sense for cubes
        # We'll use a stable fallback based on object id
        return id(self) < id(other)

# Các phương thức khác để quản lý Rubik sẽ được thêm vào sau
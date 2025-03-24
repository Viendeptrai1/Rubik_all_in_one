import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from RubikState.rubik_chen import RubikState, SOLVED_STATE as SOLVED_STATE_3X3
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE as SOLVED_STATE_2X2

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

class Piece2x2:
    """
    Lớp đại diện cho một khối nhỏ trong Rubik 2x2
    Điều chỉnh để khớp với hệ tọa độ trung tâm (-0.5 đến 0.5)
    """
    def __init__(self, position, colors):
        """
        Khởi tạo một khối Rubik 2x2
        :param position: Tuple (x, y, z) chỉ vị trí ban đầu của khối
        :param colors: Dict chứa màu của các mặt {'F': color, 'B': color, ...}
        """
        self.position = np.array(position)  # Vị trí trong không gian 3D
        self.colors = colors.copy()
        self.size = 0.5  # Kích thước nửa cạnh của khối
        
        # Các đỉnh của khối (điều chỉnh cho hệ tọa độ trung tâm)
        self.vertices = {
            'F': [
                (self.size, self.size, self.size), 
                (-self.size, self.size, self.size), 
                (-self.size, -self.size, self.size), 
                (self.size, -self.size, self.size)
            ],
            'B': [
                (self.size, self.size, -self.size), 
                (-self.size, self.size, -self.size), 
                (-self.size, -self.size, -self.size), 
                (self.size, -self.size, -self.size)
            ],
            'L': [
                (-self.size, self.size, self.size), 
                (-self.size, self.size, -self.size), 
                (-self.size, -self.size, -self.size), 
                (-self.size, -self.size, self.size)
            ],
            'R': [
                (self.size, self.size, self.size), 
                (self.size, self.size, -self.size), 
                (self.size, -self.size, -self.size), 
                (self.size, -self.size, self.size)
            ],
            'U': [
                (self.size, self.size, self.size), 
                (-self.size, self.size, self.size), 
                (-self.size, self.size, -self.size), 
                (self.size, self.size, -self.size)
            ],
            'D': [
                (self.size, -self.size, self.size), 
                (-self.size, -self.size, self.size), 
                (-self.size, -self.size, -self.size), 
                (self.size, -self.size, -self.size)
            ]
        }
    
    def draw(self):
        """Vẽ khối với OpenGL"""
        glPushMatrix()
        
        # Di chuyển đến vị trí hiện tại (không cần điều chỉnh vì đã dùng hệ tọa độ trung tâm)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
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
    # - Tất cả các mặt sẽ xoay theo chiều kim đồng hồ nhìn từ mặt đó khi clockwise=True
    # - Mặt LBD cần đảo ngược hướng khi áp dụng vào ma trận xoay
    FACE_ROTATIONS = {
        # Mặt trước (Front - z=max)
        'F': {
            'axis': 'z',  # Xoay quanh trục z
            'pos': 2,     # Vị trí của mặt 
            'invert': False  # Không cần đảo ngược hướng
        },
        # Mặt sau (Back - z=0)
        'B': {
            'axis': 'z',
            'pos': 0,
            'invert': True  # Cần đảo ngược hướng
        },
        # Mặt trái (Left - x=0)
        'L': {
            'axis': 'x',
            'pos': 0,
            'invert': True  # Cần đảo ngược hướng
        },
        # Mặt phải (Right - x=max)
        'R': {
            'axis': 'x',
            'pos': 2,
            'invert': False  # Không cần đảo ngược hướng
        },
        # Mặt trên (Up - y=max)
        'U': {
            'axis': 'y',
            'pos': 2,
            'invert': False  # Không cần đảo ngược hướng
        },
        # Mặt dưới (Down - y=0)
        'D': {
            'axis': 'y',
            'pos': 0,
            'invert': True  # Cần đảo ngược hướng
        }
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
        
        # Lưu góc xoay thực để cập nhật vị trí và màu
        self.actual_rotation_angle = 0

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
                    
                    # Tính toán góc hiển thị animation
                    # Đảo chiều nếu mặt cần đảo ngược
                    display_angle = self.animation_angle
                    if rot['invert']:
                        display_angle = -display_angle
                        
                    # Áp dụng phép xoay cho animation
                    if rot['axis'] == 'x':
                        glRotatef(display_angle, 1, 0, 0)
                    elif rot['axis'] == 'y':
                        glRotatef(display_angle, 0, 1, 0)
                    else:  # z
                        glRotatef(display_angle, 0, 0, 1)
                    
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
        epsilon = 0.1  # Dung sai cho phép
        
        if face == 'F': return pos[2] > 0.5 - epsilon
        if face == 'B': return pos[2] < -0.5 + epsilon
        if face == 'L': return pos[0] < -0.5 + epsilon
        if face == 'R': return pos[0] > 0.5 - epsilon
        if face == 'U': return pos[1] > 0.5 - epsilon
        if face == 'D': return pos[1] < -0.5 + epsilon
        return False

    def rotate_face(self, face, clockwise=True):
        """Bắt đầu xoay một mặt"""
        if self.animating:
            return
            
        self.animating = True
        self.animation_face = face
        
        # Đảo ngược clockwise để khớp với quy ước của RubikState
        # Lưu ý: Chúng ta không cần đảo ngược thêm cho các mặt 'invert' ở đây
        # vì animation sẽ được hiển thị trực tiếp
        clockwise = not clockwise
        
        self.animation_clockwise = clockwise
        self.animation_angle = 0
        self.animation_target = 90 if clockwise else -90
        
    def _complete_rotation(self):
        """Hoàn thành phép xoay một mặt"""
        if not self.animation_face:
            return

        face = self.animation_face
        rot_info = self.FACE_ROTATIONS[face]
        clockwise = self.animation_clockwise
        
        # Tính góc xoay thực sự trong logic 3D
        # Đảo ngược chiều xoay nếu cần thiết cho các mặt L, B, D
        actual_clockwise = clockwise
        if rot_info['invert']:
            actual_clockwise = not clockwise
            
        # Tính toán góc xoay trong không gian 3D
        angle = 90 if actual_clockwise else -90
        
        # Lấy tất cả các mảnh trên mặt đang xoay
        face_pieces = self._get_face_pieces(face)
        
        # Áp dụng ma trận xoay 
        rot_matrix = self._get_rotation_matrix(rot_info['axis'], angle)
        
        # Xoay từng mảnh
        center = np.array([1, 1, 1])
        for piece in face_pieces:
            # Cập nhật vị trí
            pos = piece.position - center
            new_pos = np.dot(rot_matrix, pos)
            piece.position = np.round(new_pos + center).astype(int)
            
            # Cập nhật màu sắc - clockwise đã được điều chỉnh ở trên
            piece.colors = self._rotate_colors(piece, rot_info['axis'], angle)
        
        # Reset trạng thái animation
        self.animating = False
        self.animation_face = None
        self.animation_angle = 0
        self.animation_target = 0

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
        """Xoay toàn bộ khối Rubik"""
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
        """Lấy tất cả các mảnh thuộc một mặt"""
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
        
        return face_pieces

    def _is_corner_piece(self, piece):
        """Kiểm tra xem một mảnh có phải là góc không"""
        return len(piece.colors) == 3

    def _is_edge_piece(self, piece):
        """Kiểm tra xem một mảnh có phải là cạnh không"""
        return len(piece.colors) == 2

    def _rotate_colors(self, piece, axis, angle):
        """Xoay màu sắc của một mảnh theo trục và góc xoay"""
        new_colors = {}
        
        # Góc xoay đã được hiệu chỉnh, xử lý hướng xoay và ánh xạ màu sắc
        # Góc dương (>0) sẽ xoay theo chiều kim đồng hồ nhìn từ hướng dương
        # Góc âm (<0) sẽ xoay ngược chiều kim đồng hồ nhìn từ hướng dương
        clockwise = angle > 0
        
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

    def get_state(self):
        """Trả về trạng thái hiện tại của Rubik dựa trên vị trí và màu sắc của các khối"""
        # Khởi tạo trạng thái mặc định
        cp = [0] * 8  # Hoán vị góc
        co = [0] * 8  # Định hướng góc
        ep = [0] * 12  # Hoán vị cạnh
        eo = [0] * 12  # Định hướng cạnh
        
        # Tạo bản đồ vị trí đến indexing cho góc
        corner_pos_map = {
            (2, 2, 2): 0,  # URF
            (0, 2, 2): 1,  # ULF
            (0, 2, 0): 2,  # ULB
            (2, 2, 0): 3,  # URB
            (2, 0, 2): 4,  # DRF
            (0, 0, 2): 5,  # DLF
            (0, 0, 0): 6,  # DLB
            (2, 0, 0): 7,  # DRB
        }
        
        # Tạo bản đồ vị trí đến indexing cho cạnh
        edge_pos_map = {
            (2, 2, 1): 0,  # UR
            (1, 2, 2): 1,  # UF
            (0, 2, 1): 2,  # UL
            (1, 2, 0): 3,  # UB
            (2, 0, 1): 4,  # DR
            (1, 0, 2): 5,  # DF
            (0, 0, 1): 6,  # DL
            (1, 0, 0): 7,  # DB
            (2, 1, 2): 8,  # FR
            (0, 1, 2): 9,  # FL
            (0, 1, 0): 10, # BL
            (2, 1, 0): 11, # BR
        }
        
        # Bản đồ màu để xác định góc và cạnh
        # Mỗi góc và cạnh có một kết hợp màu duy nhất
        corner_color_map = {
            ('W', 'B', 'O'): 3,  # URB
            ('W', 'G', 'O'): 2,  # ULB
            ('W', 'G', 'R'): 1,  # ULF
            ('W', 'B', 'R'): 0,  # URF
            ('Y', 'B', 'O'): 7,  # DRB
            ('Y', 'G', 'O'): 6,  # DLB
            ('Y', 'G', 'R'): 5,  # DLF
            ('Y', 'B', 'R'): 4,  # DRF
        }
        
        edge_color_map = {
            ('W', 'B'): 0,   # UR
            ('W', 'R'): 1,   # UF
            ('W', 'G'): 2,   # UL
            ('W', 'O'): 3,   # UB
            ('Y', 'B'): 4,   # DR
            ('Y', 'R'): 5,   # DF
            ('Y', 'G'): 6,   # DL
            ('Y', 'O'): 7,   # DB
            ('B', 'R'): 8,   # FR
            ('G', 'R'): 9,   # FL
            ('G', 'O'): 10,  # BL
            ('B', 'O'): 11,  # BR
        }
        
        # Xử lý góc - xác định vị trí và định hướng
        for piece in self.pieces:
            pos = tuple(piece.position)
            
            # Chỉ xử lý khối góc (có 3 màu)
            if len(piece.colors) == 3 and pos in corner_pos_map:
                pos_idx = corner_pos_map[pos]
                
                # Lấy màu cho mỗi mặt
                colors = []
                for face, color_tuple in piece.colors.items():
                    # Chuyển đổi màu RGB thành chữ cái
                    if color_tuple == self.COLORS['W']: colors.append('W')
                    elif color_tuple == self.COLORS['Y']: colors.append('Y')
                    elif color_tuple == self.COLORS['R']: colors.append('R')
                    elif color_tuple == self.COLORS['O']: colors.append('O')
                    elif color_tuple == self.COLORS['G']: colors.append('G')
                    elif color_tuple == self.COLORS['B']: colors.append('B')
                
                # Sắp xếp màu để khớp với bản đồ
                colors = tuple(sorted(colors))
                
                if colors in corner_color_map:
                    # Xác định góc nào đang ở vị trí này
                    corner_idx = corner_color_map[colors]
                    cp[pos_idx] = corner_idx
                    
                    # TODO: Xác định định hướng (phức tạp hơn, cần kiểm tra màu cụ thể trên mỗi mặt)
                    # Hiện tại giả sử định hướng là 0 cho tất cả
            
            # Xử lý cạnh (có 2 màu)
            elif len(piece.colors) == 2 and pos in edge_pos_map:
                pos_idx = edge_pos_map[pos]
                
                # Lấy màu cho mỗi mặt
                colors = []
                for face, color_tuple in piece.colors.items():
                    # Chuyển đổi màu RGB thành chữ cái
                    if color_tuple == self.COLORS['W']: colors.append('W')
                    elif color_tuple == self.COLORS['Y']: colors.append('Y')
                    elif color_tuple == self.COLORS['R']: colors.append('R')
                    elif color_tuple == self.COLORS['O']: colors.append('O')
                    elif color_tuple == self.COLORS['G']: colors.append('G')
                    elif color_tuple == self.COLORS['B']: colors.append('B')
                
                # Sắp xếp màu để khớp với bản đồ
                colors = tuple(sorted(colors))
                
                if colors in edge_color_map:
                    # Xác định cạnh nào đang ở vị trí này
                    edge_idx = edge_color_map[colors]
                    ep[pos_idx] = edge_idx
                    
                    # TODO: Xác định định hướng (phức tạp hơn, cần kiểm tra màu cụ thể trên mỗi mặt)
                    # Hiện tại giả sử định hướng là 0 cho tất cả
        
        # Trả về đối tượng RubikState
        return RubikState(cp, co, ep, eo)

class RubikCube2x2:
    """
    Lớp quản lý trạng thái và hiển thị Rubik Cube 2x2
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
        'F': {'axis': 'z', 'invert': False}, # Mặt trước (Front)
        'B': {'axis': 'z', 'invert': True},  # Mặt sau (Back)
        'L': {'axis': 'x', 'invert': True},  # Mặt trái (Left)
        'R': {'axis': 'x', 'invert': False}, # Mặt phải (Right)
        'U': {'axis': 'y', 'invert': False}, # Mặt trên (Up)
        'D': {'axis': 'y', 'invert': True}   # Mặt dưới (Down)
    }

    # Ánh xạ góc vào vị trí thực tế trong không gian 3D
    # Hệ tọa độ dùng trục gốc tại tâm khối (giữa khối)
    CORNER_MAP = {
        0: (0.5, 0.5, 0.5),    # URF (0) - Top-Right-Front
        1: (-0.5, 0.5, 0.5),   # ULF (1) - Top-Left-Front 
        2: (-0.5, 0.5, -0.5),  # ULB (2) - Top-Left-Back
        3: (0.5, 0.5, -0.5),   # URB (3) - Top-Right-Back
        4: (0.5, -0.5, 0.5),   # DRF (4) - Bottom-Right-Front
        5: (-0.5, -0.5, 0.5),  # DLF (5) - Bottom-Left-Front
        6: (-0.5, -0.5, -0.5), # DLB (6) - Bottom-Left-Back
        7: (0.5, -0.5, -0.5),  # DRB (7) - Bottom-Right-Back
    }

    def __init__(self):
        """Khởi tạo Rubik Cube 2x2"""
        # Góc xoay và hiển thị
        self.rotation_x = 30
        self.rotation_y = 30
        
        # Khởi tạo trạng thái Rubik 2x2
        self.state = SOLVED_STATE_2X2.copy()
        
        # Thông số animation
        self.animating = False
        self.animation_face = None
        self.animation_angle = 0
        self.animation_target = 0
        self.animation_speed = 5  # Độ nhanh của animation (độ/frame)
        self.animation_clockwise = True
        
        # Khởi tạo các khối
        self.pieces = []
        self._initialize_pieces()
        
        # Queue cho các nước đi
        self.move_queue = []

    def _initialize_pieces(self):
        """Khởi tạo các khối theo trạng thái hiện tại"""
        self.pieces = []
        
        # Khởi tạo 8 khối góc dựa trên trạng thái hiện tại
        for i in range(8):
            # Lấy vị trí thực tế của góc dựa trên hoán vị
            corner_index = self.state.cp[i]
            pos = self.CORNER_MAP[corner_index]
            
            # Tính toán màu dựa trên định hướng và vị trí
            colors = self._get_corner_colors(i, self.state.co[i])
            
            # Tạo khối
            self.pieces.append(Piece2x2(pos, colors))

    def _get_corner_colors(self, corner_idx, orientation):
        """Lấy màu cho một khối góc dựa trên định hướng"""
        colors = {}
        
        # Màu cố định cho mỗi góc trong trạng thái đã giải
        corner_colors = {
            0: {'U': 'W', 'R': 'B', 'F': 'R'},  # URF (0)
            1: {'U': 'W', 'L': 'G', 'F': 'R'},  # ULF (1)
            2: {'U': 'W', 'L': 'G', 'B': 'O'},  # ULB (2)
            3: {'U': 'W', 'R': 'B', 'B': 'O'},  # URB (3)
            4: {'D': 'Y', 'R': 'B', 'F': 'R'},  # DRF (4) 
            5: {'D': 'Y', 'L': 'G', 'F': 'R'},  # DLF (5)
            6: {'D': 'Y', 'L': 'G', 'B': 'O'},  # DLB (6)
            7: {'D': 'Y', 'R': 'B', 'B': 'O'},  # DRB (7)
        }
        
        # Lấy thông tin màu góc 
        original_colors = corner_colors[corner_idx]
        
        # Khởi tạo mapping xoay dựa trên định hướng
        # URF, ULF, ULB, URB có trục xoay UP, DRF, DLF, DLB, DRB có trục xoay DOWN
        if corner_idx in [0, 1, 2, 3]:  # Góc trên (U)
            cycle = ['U', 'R' if corner_idx in [0, 3] else 'L', 'F' if corner_idx in [0, 1] else 'B']
        else:  # Góc dưới (D)
            cycle = ['D', 'R' if corner_idx in [4, 7] else 'L', 'F' if corner_idx in [4, 5] else 'B']
        
        # Áp dụng định hướng
        if orientation == 0:
            # Không xoay
            for face, color in original_colors.items():
                colors[face] = self.COLORS[color]
        elif orientation == 1:
            # Xoay 1 lần theo chiều kim đồng hồ
            colors[cycle[0]] = self.COLORS[original_colors[cycle[2]]]
            colors[cycle[1]] = self.COLORS[original_colors[cycle[0]]]
            colors[cycle[2]] = self.COLORS[original_colors[cycle[1]]]
        elif orientation == 2:
            # Xoay 2 lần theo chiều kim đồng hồ
            colors[cycle[0]] = self.COLORS[original_colors[cycle[1]]]
            colors[cycle[1]] = self.COLORS[original_colors[cycle[0]]]
            colors[cycle[2]] = self.COLORS[original_colors[cycle[2]]]
            
        return colors

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

    def _is_piece_on_face(self, piece, face):
        """Kiểm tra xem một khối có thuộc mặt đang xoay không"""
        pos = piece.position
        epsilon = 0.1  # Dung sai cho phép
        
        if face == 'F': return pos[2] > 0.5 - epsilon
        if face == 'B': return pos[2] < -0.5 + epsilon
        if face == 'L': return pos[0] < -0.5 + epsilon
        if face == 'R': return pos[0] > 0.5 - epsilon
        if face == 'U': return pos[1] > 0.5 - epsilon
        if face == 'D': return pos[1] < -0.5 + epsilon
        return False

    def rotate_face(self, face, clockwise=True):
        """Bắt đầu xoay một mặt"""
        if self.animating:
            return
            
        self.animating = True
        self.animation_face = face
        
        # Đảo ngược clockwise để khớp với quy ước của RubikState
        clockwise = not clockwise
        
        self.animation_clockwise = clockwise
        self.animation_angle = 0
        self.animation_target = 90 if clockwise else -90
        
    def _complete_rotation(self):
        """Hoàn thành phép xoay một mặt"""
        if not self.animation_face:
            return
            
        face = self.animation_face
        rot_info = self.FACE_ROTATIONS[face]
        clockwise = self.animation_clockwise
        
        # Tính góc xoay thực sự trong logic 3D
        # Đảo ngược chiều xoay nếu cần thiết cho các mặt L, B, D
        actual_clockwise = clockwise
        if rot_info['invert']:
            actual_clockwise = not clockwise
            
        # Tính toán góc xoay trong không gian 3D
        angle = 90 if actual_clockwise else -90
        
        # Lấy tất cả các mảnh trên mặt đang xoay
        face_pieces = self._get_face_pieces(face)
        
        # Áp dụng ma trận xoay 
        rot_matrix = self._get_rotation_matrix(rot_info['axis'], angle)
        
        # Xoay từng mảnh
        center = np.array([0, 0, 0])  # Tâm xoay ở giữa Rubik 2x2
        for piece in face_pieces:
            # Cập nhật vị trí
            pos = piece.position - center
            new_pos = np.dot(rot_matrix, pos)
            piece.position = np.round(new_pos + center, 2)  # Làm tròn với 2 chữ số thập phân
            
            # Cập nhật màu sắc - clockwise đã được điều chỉnh ở trên
            piece.colors = self._rotate_colors(piece, rot_info['axis'], angle)
        
        # Cập nhật trạng thái logic
        move = face
        if not clockwise:
            move = f"{face}'"
            
        # Cập nhật trạng thái trong RubikState
        from RubikState.rubik_2x2 import MOVES as MOVES_2X2
        self.state = self.state.apply_move(move, MOVES_2X2)
        
        # Reset trạng thái animation
        self.animating = False
        self.animation_face = None
        self.animation_angle = 0
        self.animation_target = 0

    def draw_cube(self):
        """Vẽ toàn bộ Rubik Cube 2x2"""
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
                    # Áp dụng xoay animation
                    rot = self.FACE_ROTATIONS[self.animation_face]
                    
                    # Tính toán góc hiển thị animation
                    # Đảo ngược góc hiển thị cho các mặt 'invert'
                    display_angle = self.animation_angle
                    if rot['invert']:
                        display_angle = -display_angle
                    
                    # Áp dụng phép xoay
                    if rot['axis'] == 'x':
                        glRotatef(display_angle, 1, 0, 0)
                    elif rot['axis'] == 'y':
                        glRotatef(display_angle, 0, 1, 0)
                    else:  # z
                        glRotatef(display_angle, 0, 0, 1)
                    
                    piece.draw()
                    glPopMatrix()
                else:
                    piece.draw()
            else:
                piece.draw()
        
        glPopMatrix()

    def rotate_cube(self, dx, dy):
        """Xoay toàn bộ khối Rubik"""
        self.rotation_y += dx
        self.rotation_x += dy

    def update_animation(self):
        """Cập nhật trạng thái animation"""
        if not self.animating:
            # Nếu có moves trong queue, thực hiện move tiếp theo
            if self.move_queue:
                face, clockwise = self.move_queue.pop(0)
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
            self.move_queue = moves
            
    def get_state(self):
        """Trả về trạng thái hiện tại của Rubik 2x2 dựa trên vị trí và màu sắc của các khối"""
        # Khởi tạo trạng thái mặc định
        cp = [0] * 8  # Hoán vị góc
        co = [0] * 8  # Định hướng góc
        
        # Tạo bản đồ vị trí đến indexing cho góc
        corner_pos_map = {
            (0.5, 0.5, 0.5): 0,    # URF (0) - Top-Right-Front
            (-0.5, 0.5, 0.5): 1,   # ULF (1) - Top-Left-Front 
            (-0.5, 0.5, -0.5): 2,  # ULB (2) - Top-Left-Back
            (0.5, 0.5, -0.5): 3,   # URB (3) - Top-Right-Back
            (0.5, -0.5, 0.5): 4,   # DRF (4) - Bottom-Right-Front
            (-0.5, -0.5, 0.5): 5,  # DLF (5) - Bottom-Left-Front
            (-0.5, -0.5, -0.5): 6, # DLB (6) - Bottom-Left-Back
            (0.5, -0.5, -0.5): 7,  # DRB (7) - Bottom-Right-Back
        }
        
        # Bản đồ màu để xác định góc
        # Mỗi góc có một kết hợp màu duy nhất
        corner_color_map = {
            ('W', 'B', 'O'): 3,  # URB
            ('W', 'G', 'O'): 2,  # ULB
            ('W', 'G', 'R'): 1,  # ULF
            ('W', 'B', 'R'): 0,  # URF
            ('Y', 'B', 'O'): 7,  # DRB
            ('Y', 'G', 'O'): 6,  # DLB
            ('Y', 'G', 'R'): 5,  # DLF
            ('Y', 'B', 'R'): 4,  # DRF
        }
        
        # Màu mặt chuẩn để xác định định hướng
        standard_colors = {
            0: {'U': 'W', 'R': 'B', 'F': 'R'},  # URF (0)
            1: {'U': 'W', 'L': 'G', 'F': 'R'},  # ULF (1)
            2: {'U': 'W', 'L': 'G', 'B': 'O'},  # ULB (2)
            3: {'U': 'W', 'R': 'B', 'B': 'O'},  # URB (3)
            4: {'D': 'Y', 'R': 'B', 'F': 'R'},  # DRF (4) 
            5: {'D': 'Y', 'L': 'G', 'F': 'R'},  # DLF (5)
            6: {'D': 'Y', 'L': 'G', 'B': 'O'},  # DLB (6)
            7: {'D': 'Y', 'R': 'B', 'B': 'O'},  # DRB (7)
        }
        
        # Xử lý góc - xác định vị trí và định hướng
        for piece in self.pieces:
            pos = tuple(piece.position)
            
            if pos in corner_pos_map:
                pos_idx = corner_pos_map[pos]
                
                # Lấy màu cho mỗi mặt
                color_map = {}  # map face -> color
                for face, color_tuple in piece.colors.items():
                    # Chuyển đổi màu RGB thành chữ cái
                    if color_tuple == self.COLORS['W']: color_map[face] = 'W'
                    elif color_tuple == self.COLORS['Y']: color_map[face] = 'Y'
                    elif color_tuple == self.COLORS['R']: color_map[face] = 'R'
                    elif color_tuple == self.COLORS['O']: color_map[face] = 'O'
                    elif color_tuple == self.COLORS['G']: color_map[face] = 'G'
                    elif color_tuple == self.COLORS['B']: color_map[face] = 'B'
                
                # Tập hợp các màu để xác định khối góc
                colors = tuple(sorted(color_map.values()))
                
                if colors in corner_color_map:
                    # Xác định góc nào đang ở vị trí này
                    corner_idx = corner_color_map[colors]
                    cp[pos_idx] = corner_idx
                    
                    # Xác định định hướng dựa trên vị trí của màu U/D
                    standard = standard_colors[corner_idx]
                    reference_face = 'U' if 'U' in standard else 'D'
                    reference_color = standard[reference_face]
                    
                    # Tìm mặt hiện tại chứa màu tham chiếu (U/D)
                    current_face = None
                    for face, color in color_map.items():
                        if color == reference_color:
                            current_face = face
                            break
                    
                    # Xác định định hướng
                    if current_face == reference_face:
                        co[pos_idx] = 0  # Không xoay
                    elif current_face in ['F', 'B']:
                        co[pos_idx] = 1  # Xoay 1 lần
                    elif current_face in ['R', 'L']:
                        co[pos_idx] = 2  # Xoay 2 lần
        
        # Trả về đối tượng Rubik2x2State
        return Rubik2x2State(cp, co)

    def _get_face_pieces(self, face):
        """Lấy tất cả các mảnh thuộc một mặt"""
        face_pieces = []
        for piece in self.pieces:
            if self._is_piece_on_face(piece, face):
                face_pieces.append(piece)
        return face_pieces
        
    def _rotate_colors(self, piece, axis, angle):
        """Xoay màu sắc của một mảnh theo trục và góc xoay"""
        new_colors = {}
        
        # Góc xoay đã được hiệu chỉnh, xử lý hướng xoay và ánh xạ màu sắc
        # Góc dương (>0) sẽ xoay theo chiều kim đồng hồ nhìn từ hướng dương
        # Góc âm (<0) sẽ xoay ngược chiều kim đồng hồ nhìn từ hướng dương
        clockwise = angle > 0
        
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
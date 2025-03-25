import numpy as np
from rubik_state import RubikState, SOLVED_STATE

# Định nghĩa mapping giữa vị trí khối và chỉ số trong biểu diễn hoán vị
# Các góc (corners) được đánh số 0-7 theo thứ tự:
# 0: URF, 1: UFL, 2: ULB, 3: UBR, 4: DFR, 5: DLF, 6: DBL, 7: DRB
# Các cạnh (edges) được đánh số 0-11 theo thứ tự:
# 0: UR, 1: UF, 2: UL, 3: UB, 4: DR, 5: DF, 6: DL, 7: DB, 8: FR, 9: FL, 10: BL, 11: BR

# Map vị trí 3D của góc sang chỉ số trong biểu diễn hoán vị
CORNER_POSITION_MAP = {
    (2, 2, 2): 0,  # URF
    (0, 2, 2): 1,  # UFL
    (0, 2, 0): 2,  # ULB
    (2, 2, 0): 3,  # UBR
    (2, 0, 2): 4,  # DFR
    (0, 0, 2): 5,  # DLF
    (0, 0, 0): 6,  # DBL
    (2, 0, 0): 7   # DRB
}

# Map vị trí 3D của cạnh sang chỉ số trong biểu diễn hoán vị
EDGE_POSITION_MAP = {
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
    (2, 1, 0): 11  # BR
}

# Map vị trí và màu để tính định hướng 
# Định hướng góc (0: đúng, 1: xoay thuận, 2: xoay ngược)
# Định hướng cạnh (0: đúng, 1: lật)

# Map mặt tham chiếu cho định hướng góc
CORNER_ORIENTATION_REFERENCE = {
    0: 'U',  # Mặt U hoặc D là mặt tham chiếu
    1: 'U', 
    2: 'U',
    3: 'U',
    4: 'D',
    5: 'D',
    6: 'D',
    7: 'D'
}

# Map mặt tham chiếu cho định hướng cạnh
EDGE_ORIENTATION_REFERENCE = {
    0: 'U',  # Mặt U hoặc D là mặt tham chiếu cho cạnh hàng U/D
    1: 'U',
    2: 'U', 
    3: 'U',
    4: 'D',
    5: 'D',
    6: 'D',
    7: 'D',
    8: 'F',  # Mặt F hoặc B là mặt tham chiếu cho cạnh hàng E
    9: 'F',
    10: 'B',
    11: 'B'
}

def cube_to_state(rubik_cube):
    """Chuyển đổi từ mô hình RubikCube 3D sang RubikState (hoán vị, định hướng)"""
    # Khởi tạo các mảng hoán vị và định hướng
    cp = [-1] * 8  # Hoán vị góc (corner permutation)
    co = [-1] * 8  # Định hướng góc (corner orientation)
    ep = [-1] * 12  # Hoán vị cạnh (edge permutation)
    eo = [-1] * 12  # Định hướng cạnh (edge orientation)
    
    # Duyệt qua từng khối góc và xác định hoán vị và định hướng
    corner_pieces = [piece for piece in rubik_cube.pieces if len(piece.colors) == 3]  # Các khối góc có 3 màu
    for piece in corner_pieces:
        # Lấy vị trí góc trong không gian 3D
        position = tuple(piece.position)
        if position not in CORNER_POSITION_MAP:
            continue
            
        pos_idx = CORNER_POSITION_MAP[position]  # Chỉ số vị trí hiện tại
        
        # Xác định hoán vị (khối góc này thuộc về vị trí nào trong trạng thái đã giải)
        # Điều này đòi hỏi phân tích các màu trên khối
        colors = piece.colors
        
        # Lấy các màu và mặt tương ứng
        color_faces = {}
        for face, color in colors.items():
            color_name = get_color_name(color, rubik_cube.COLORS)
            color_faces[color_name] = face
            
        # Xác định khối góc này thuộc vị trí nào trong trạng thái đã giải
        correct_pos = determine_corner_position(color_faces)
        cp[pos_idx] = correct_pos
        
        # Xác định định hướng của góc
        # Mặt tham chiếu (U/D) có màu đúng ở mặt U/D của khối?
        ref_face = CORNER_ORIENTATION_REFERENCE[correct_pos]
        ref_color = get_reference_color(ref_face, rubik_cube.COLORS)
        
        orientation = determine_corner_orientation(color_faces, ref_face, ref_color)
        co[pos_idx] = orientation
    
    # Duyệt qua từng khối cạnh và xác định hoán vị và định hướng
    edge_pieces = [piece for piece in rubik_cube.pieces if len(piece.colors) == 2]  # Các khối cạnh có 2 màu
    for piece in edge_pieces:
        # Lấy vị trí cạnh trong không gian 3D
        position = tuple(piece.position)
        if position not in EDGE_POSITION_MAP:
            continue
            
        pos_idx = EDGE_POSITION_MAP[position]  # Chỉ số vị trí hiện tại
        
        # Xác định hoán vị
        colors = piece.colors
        
        # Lấy các màu và mặt tương ứng
        color_faces = {}
        for face, color in colors.items():
            color_name = get_color_name(color, rubik_cube.COLORS)
            color_faces[color_name] = face
            
        # Xác định khối cạnh này thuộc vị trí nào trong trạng thái đã giải
        correct_pos = determine_edge_position(color_faces)
        ep[pos_idx] = correct_pos
        
        # Xác định định hướng của cạnh
        ref_face = EDGE_ORIENTATION_REFERENCE[correct_pos]
        ref_color = get_reference_color(ref_face, rubik_cube.COLORS)
        
        orientation = determine_edge_orientation(color_faces, ref_face, ref_color)
        eo[pos_idx] = orientation
    
    # Trả về trạng thái Rubik
    return RubikState(cp, co, ep, eo)

def state_to_cube(state, rubik_cube):
    """Chuyển đổi từ RubikState (hoán vị, định hướng) sang mô hình RubikCube 3D"""
    # Sao lưu lại trạng thái ban đầu để tránh mất tham chiếu
    original_pieces = [piece.copy() for piece in rubik_cube.pieces]
    
    # Duyệt qua các khối góc
    for pos_idx, current_idx in enumerate(state.cp):
        orientation = state.co[pos_idx]
        
        # Tìm vị trí 3D của góc này
        position_3d = get_corner_position_3d(pos_idx)
        
        # Tìm khối góc tương ứng với vị trí này
        for i, piece in enumerate(rubik_cube.pieces):
            if tuple(piece.position) == position_3d and len(piece.colors) == 3:
                # Lấy màu của khối góc đúng (khối thuộc về vị trí current_idx)
                correct_colors = get_corner_colors(current_idx, orientation, rubik_cube.COLORS)
                
                # Cập nhật màu cho khối hiện tại
                for face, color in correct_colors.items():
                    if face in piece.colors:
                        piece.colors[face] = color
                break
    
    # Duyệt qua các khối cạnh
    for pos_idx, current_idx in enumerate(state.ep):
        orientation = state.eo[pos_idx]
        
        # Tìm vị trí 3D của cạnh này
        position_3d = get_edge_position_3d(pos_idx)
        
        # Tìm khối cạnh tương ứng với vị trí này
        for i, piece in enumerate(rubik_cube.pieces):
            if tuple(piece.position) == position_3d and len(piece.colors) == 2:
                # Lấy màu của khối cạnh đúng (khối thuộc về vị trí current_idx)
                correct_colors = get_edge_colors(current_idx, orientation, rubik_cube.COLORS)
                
                # Cập nhật màu cho khối hiện tại
                for face, color in correct_colors.items():
                    if face in piece.colors:
                        piece.colors[face] = color
                break
    
    return rubik_cube

# Các hàm hỗ trợ
def get_color_name(color, color_map):
    """Lấy tên màu từ giá trị RGB"""
    for name, rgb in color_map.items():
        if np.array_equal(color, rgb):
            return name
    return None

def determine_corner_position(color_faces):
    """Xác định vị trí đúng của khối góc dựa trên màu sắc"""
    # Ánh xạ các màu sắc góc với vị trí trong trạng thái đã giải
    corner_colors = {
        frozenset(['W', 'R', 'B']): 0,  # URF: White-Red-Blue
        frozenset(['W', 'G', 'R']): 1,  # UFL: White-Green-Red
        frozenset(['W', 'O', 'G']): 2,  # ULB: White-Orange-Green
        frozenset(['W', 'B', 'O']): 3,  # UBR: White-Blue-Orange
        frozenset(['Y', 'R', 'B']): 4,  # DFR: Yellow-Red-Blue
        frozenset(['Y', 'G', 'R']): 5,  # DLF: Yellow-Green-Red
        frozenset(['Y', 'O', 'G']): 6,  # DBL: Yellow-Orange-Green
        frozenset(['Y', 'B', 'O']): 7   # DRB: Yellow-Blue-Orange
    }
    
    # Tạo tập hợp các màu của góc hiện tại
    colors_set = frozenset(color_faces.keys())
    
    # Trả về vị trí tương ứng với màu sắc
    if colors_set in corner_colors:
        return corner_colors[colors_set]
    
    # Nếu không tìm thấy, có thể là lỗi màu sắc
    print(f"Warning: Could not determine corner position for colors: {colors_set}")
    return 0  # Default to URF

def determine_edge_position(color_faces):
    """Xác định vị trí đúng của khối cạnh dựa trên màu sắc"""
    # Ánh xạ các màu sắc cạnh với vị trí trong trạng thái đã giải
    edge_colors = {
        frozenset(['W', 'B']): 0,   # UR: White-Blue
        frozenset(['W', 'R']): 1,   # UF: White-Red
        frozenset(['W', 'G']): 2,   # UL: White-Green
        frozenset(['W', 'O']): 3,   # UB: White-Orange
        frozenset(['Y', 'B']): 4,   # DR: Yellow-Blue
        frozenset(['Y', 'R']): 5,   # DF: Yellow-Red
        frozenset(['Y', 'G']): 6,   # DL: Yellow-Green
        frozenset(['Y', 'O']): 7,   # DB: Yellow-Orange
        frozenset(['R', 'B']): 8,   # FR: Red-Blue
        frozenset(['R', 'G']): 9,   # FL: Red-Green
        frozenset(['O', 'G']): 10,  # BL: Orange-Green
        frozenset(['O', 'B']): 11   # BR: Orange-Blue
    }
    
    # Tạo tập hợp các màu của cạnh hiện tại
    colors_set = frozenset(color_faces.keys())
    
    # Trả về vị trí tương ứng với màu sắc
    if colors_set in edge_colors:
        return edge_colors[colors_set]
    
    # Nếu không tìm thấy, có thể là lỗi màu sắc
    print(f"Warning: Could not determine edge position for colors: {colors_set}")
    return 0  # Default to UR

def determine_corner_orientation(color_faces, ref_face, ref_color):
    """Xác định định hướng của góc"""
    # Lấy mặt của màu tham chiếu (màu U hoặc D)
    ref_color_name = get_color_name(ref_color, {'W': np.array([255, 255, 255]), 'Y': np.array([255, 255, 0])})
    
    # Tìm mặt chứa màu tham chiếu
    ref_face_actual = None
    for color, face in color_faces.items():
        if color == ref_color_name:
            ref_face_actual = face
            break
    
    if not ref_face_actual:
        print(f"Warning: Reference color {ref_color_name} not found on corner piece")
        return 0
    
    # Định hướng phụ thuộc vào vị trí mặt tham chiếu
    # 0: Mặt tham chiếu trùng với mặt U/D thực tế
    # 1: Mặt tham chiếu xoay thuận (120 độ)
    # 2: Mặt tham chiếu xoay ngược (240 độ)
    
    if ref_face_actual in ['U', 'D']:
        return 0  # Đúng định hướng
    
    # Định hướng phụ thuộc vào vị trí của góc
    # Xác định các mặt lân cận của góc
    adjacent_faces = list(color_faces.values())
    adjacent_faces.remove(ref_face_actual)
    
    # Căn cứ vào các mặt lân cận để xác định định hướng
    # Đây là một thuật toán đơn giản, có thể cần điều chỉnh theo cấu trúc cụ thể
    if 'F' in adjacent_faces or 'R' in adjacent_faces:
        return 1  # Xoay thuận
    else:
        return 2  # Xoay ngược
    
    return 0  # Mặc định

def determine_edge_orientation(color_faces, ref_face, ref_color):
    """Xác định định hướng của cạnh"""
    # Lấy màu tham chiếu
    ref_color_name = None
    if ref_face in ['U', 'D']:
        ref_color_name = 'W' if ref_face == 'U' else 'Y'
    elif ref_face in ['F', 'B']:
        ref_color_name = 'R' if ref_face == 'F' else 'O'
    
    # Tìm mặt chứa màu tham chiếu
    ref_face_actual = None
    for color, face in color_faces.items():
        if color == ref_color_name:
            ref_face_actual = face
            break
    
    if not ref_face_actual:
        print(f"Warning: Reference color {ref_color_name} not found on edge piece")
        return 0
    
    # Định hướng phụ thuộc vào vị trí mặt tham chiếu
    # 0: Đúng định hướng, 1: Lật ngược
    
    # Đối với cạnh ở tầng U/D
    if ref_face in ['U', 'D']:
        if ref_face_actual in ['U', 'D']:
            return 0  # Đúng định hướng
        else:
            return 1  # Lật ngược
    
    # Đối với cạnh ở tầng E (các cạnh giữa)
    if ref_face in ['F', 'B']:
        if ref_face_actual in ['F', 'B']:
            return 0  # Đúng định hướng
        else:
            return 1  # Lật ngược
    
    return 0  # Mặc định

def get_reference_color(face, color_map):
    """Lấy màu tham chiếu cho mặt"""
    if face == 'U':
        return color_map['W']  # White for Up
    elif face == 'D':
        return color_map['Y']  # Yellow for Down
    elif face == 'F':
        return color_map['R']  # Red for Front
    elif face == 'B':
        return color_map['O']  # Orange for Back
    elif face == 'L':
        return color_map['G']  # Green for Left
    elif face == 'R':
        return color_map['B']  # Blue for Right
    return None

def get_corner_position_3d(idx):
    """Lấy vị trí 3D tương ứng với chỉ số góc"""
    for pos, i in CORNER_POSITION_MAP.items():
        if i == idx:
            return pos
    return None

def get_edge_position_3d(idx):
    """Lấy vị trí 3D tương ứng với chỉ số cạnh"""
    for pos, i in EDGE_POSITION_MAP.items():
        if i == idx:
            return pos
    return None

def get_corner_colors(idx, orientation, color_map):
    """Lấy màu sắc của khối góc dựa trên chỉ số và định hướng"""
    # Map góc với màu (theo thứ tự U/D, F/B, L/R)
    corner_colors = {
        0: {'U': 'W', 'F': 'R', 'R': 'B'},  # URF
        1: {'U': 'W', 'L': 'G', 'F': 'R'},  # UFL
        2: {'U': 'W', 'B': 'O', 'L': 'G'},  # ULB
        3: {'U': 'W', 'R': 'B', 'B': 'O'},  # UBR
        4: {'D': 'Y', 'F': 'R', 'R': 'B'},  # DFR
        5: {'D': 'Y', 'L': 'G', 'F': 'R'},  # DLF
        6: {'D': 'Y', 'B': 'O', 'L': 'G'},  # DBL
        7: {'D': 'Y', 'R': 'B', 'B': 'O'}   # DRB
    }
    
    # Lấy màu cơ bản của góc
    colors = corner_colors[idx].copy()
    faces = list(colors.keys())
    
    # Áp dụng định hướng
    if orientation == 1:  # Xoay thuận (120 độ)
        # Hoán đổi màu: U/D -> F/B -> L/R -> U/D
        ud_face = next(f for f in faces if f in ['U', 'D'])
        fb_face = next(f for f in faces if f in ['F', 'B'])
        lr_face = next(f for f in faces if f in ['L', 'R'])
        
        ud_color = colors[ud_face]
        fb_color = colors[fb_face]
        lr_color = colors[lr_face]
        
        colors[ud_face] = lr_color
        colors[fb_face] = ud_color
        colors[lr_face] = fb_color
        
    elif orientation == 2:  # Xoay ngược (240 độ)
        # Hoán đổi màu: U/D -> L/R -> F/B -> U/D
        ud_face = next(f for f in faces if f in ['U', 'D'])
        fb_face = next(f for f in faces if f in ['F', 'B'])
        lr_face = next(f for f in faces if f in ['L', 'R'])
        
        ud_color = colors[ud_face]
        fb_color = colors[fb_face]
        lr_color = colors[lr_face]
        
        colors[ud_face] = fb_color
        colors[fb_face] = lr_color
        colors[lr_face] = ud_color
    
    # Chuyển đổi tên màu sang RGB
    result = {}
    for face, color_name in colors.items():
        result[face] = color_map[color_name]
    
    return result

def get_edge_colors(idx, orientation, color_map):
    """Lấy màu sắc của khối cạnh dựa trên chỉ số và định hướng"""
    # Map cạnh với màu (theo thứ tự tầng, mặt)
    edge_colors = {
        0: {'U': 'W', 'R': 'B'},   # UR
        1: {'U': 'W', 'F': 'R'},   # UF
        2: {'U': 'W', 'L': 'G'},   # UL
        3: {'U': 'W', 'B': 'O'},   # UB
        4: {'D': 'Y', 'R': 'B'},   # DR
        5: {'D': 'Y', 'F': 'R'},   # DF
        6: {'D': 'Y', 'L': 'G'},   # DL
        7: {'D': 'Y', 'B': 'O'},   # DB
        8: {'F': 'R', 'R': 'B'},   # FR
        9: {'F': 'R', 'L': 'G'},   # FL
        10: {'B': 'O', 'L': 'G'},  # BL
        11: {'B': 'O', 'R': 'B'}   # BR
    }
    
    # Lấy màu cơ bản của cạnh
    colors = edge_colors[idx].copy()
    faces = list(colors.keys())
    
    # Áp dụng định hướng
    if orientation == 1:  # Lật ngược
        # Hoán đổi màu giữa hai mặt
        colors[faces[0]], colors[faces[1]] = colors[faces[1]], colors[faces[0]]
    
    # Chuyển đổi tên màu sang RGB
    result = {}
    for face, color_name in colors.items():
        result[face] = color_map[color_name]
    
    return result 
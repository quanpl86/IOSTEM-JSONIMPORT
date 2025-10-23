# src/utils/geometry.py

from typing import Tuple

# Định nghĩa kiểu dữ liệu cho tọa độ 3D để sử dụng trong type hints.
Vector3 = Tuple[int, int, int]

def add_vectors(v1: Vector3, v2: Vector3) -> Vector3:
    """
    Cộng hai vector 3D (hoặc tọa độ).

    Args:
        v1 (Vector3): Vector thứ nhất.
        v2 (Vector3): Vector thứ hai.

    Returns:
        Vector3: Vector kết quả của phép cộng.
        
    Example:
        >>> add_vectors((1, 2, 3), (4, 5, 6))
        (5, 7, 9)
    """
    return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])

def subtract_vectors(v1: Vector3, v2: Vector3) -> Vector3:
    """
    Trừ hai vector 3D (v1 - v2).

    Args:
        v1 (Vector3): Vector bị trừ.
        v2 (Vector3): Vector trừ.

    Returns:
        Vector3: Vector kết quả của phép trừ.

    Example:
        >>> subtract_vectors((5, 7, 9), (1, 2, 3))
        (4, 5, 6)
    """
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])

def scale_vector(v: Vector3, scalar: int) -> Vector3:
    """
    Nhân một vector với một số vô hướng (scalar).

    Args:
        v (Vector3): Vector cần nhân.
        scalar (int): Số vô hướng.

    Returns:
        Vector3: Vector đã được nhân.

    Example:
        >>> scale_vector((1, 2, 3), 3)
        (3, 6, 9)
    """
    return (v[0] * scalar, v[1] * scalar, v[2] * scalar)

def manhattan_distance(p1: Vector3, p2: Vector3) -> int:
    """
    Tính khoảng cách Manhattan (khoảng cách trên lưới) giữa hai điểm 3D.
    Đây là tổng chênh lệch tuyệt đối của các tọa độ.

    Args:
        p1 (Vector3): Điểm thứ nhất.
        p2 (Vector3): Điểm thứ hai.

    Returns:
        int: Khoảng cách Manhattan.

    Example:
        >>> manhattan_distance((1, 1, 1), (4, 3, 2))
        6
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])

# --- Các vector hằng số tiện ích ---
# Định nghĩa sẵn các vector chỉ hướng cơ bản.
# Điều này giúp code dễ đọc và tránh lỗi gõ nhầm số.
# Ví dụ: thay vì viết (1, 0, 0) ở nhiều nơi, ta viết FORWARD_X.

FORWARD_X = (1, 0, 0)
BACKWARD_X = (-1, 0, 0)
FORWARD_Z = (0, 0, 1)
BACKWARD_Z = (0, 0, -1)
UP_Y = (0, 1, 0)
DOWN_Y = (0, -1, 0)

DIRECTIONS_2D = [FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z]
# src/map_generator/topologies/complex_maze.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class ComplexMazeTopology(BaseTopology):
    """
    Tạo ra một mê cung phức tạp bằng thuật toán Randomized Depth-First Search.
    Mê cung này đảm bảo có một lối đi duy nhất từ điểm đầu đến mọi điểm khác.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Hiện thực hóa thuật toán sinh mê cung.

        Returns:
            PathInfo: Một đối tượng chứa vị trí bắt đầu, đích và một danh sách
                      dài các tọa độ của tường tạo nên mê cung.
        """
        print("    LOG: Generating 'complex_maze' topology using Randomized DFS...")

        # --- (CẢI TIẾN) Đọc và ngẫu nhiên hóa kích thước mê cung từ params ---
        width_param = params.get('maze_width', [9, 13])
        depth_param = params.get('maze_depth', [9, 13])

        req_width = random.randint(*width_param) if isinstance(width_param, list) else width_param
        req_depth = random.randint(*depth_param) if isinstance(depth_param, list) else depth_param

        # Mê cung sẽ được tạo trên lưới 2D (XZ), với chiều cao Y cố định là 0.
        # Để thuật toán hoạt động tốt, lưới phải có kích thước lẻ.
        width = req_width if req_width % 2 != 0 else req_width - 1
        depth = req_depth if req_depth % 2 != 0 else req_depth - 1
        
        # Tạo một lưới ban đầu chứa đầy tường.
        # Giá trị '1' đại diện cho tường (wall), '0' đại diện cho đường đi (path).
        grid = [[1 for _ in range(depth)] for _ in range(width)]

        # Chọn một điểm bắt đầu ngẫu nhiên cho thuật toán "đào hầm".
        # Điểm này phải có tọa độ lẻ để nằm giữa các "bức tường" của lưới.
        start_x = random.randrange(1, width, 2)
        start_z = random.randrange(1, depth, 2)
        
        # Sử dụng một stack (ngăn xếp) để theo dõi đường đi của thuật toán DFS.
        stack = [(start_x, start_z)]
        grid[start_x][start_z] = 0  # Đánh dấu điểm bắt đầu là đường đi.

        while stack:
            cx, cz = stack[-1]  # Lấy ô hiện tại (peek).

            # Tìm các "hàng xóm" cách 2 ô mà chưa được ghé thăm (vẫn là tường).
            neighbors = []
            # (dx, dz) là các vector di chuyển tới hàng xóm.
            for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                nx, nz = cx + dx, cz + dz
                # Kiểm tra xem hàng xóm có nằm trong biên của lưới không.
                if 0 <= nx < width and 0 <= nz < depth and grid[nx][nz] == 1:
                    neighbors.append((nx, nz))

            if neighbors:
                # Nếu có hàng xóm hợp lệ, chọn ngẫu nhiên một trong số chúng.
                nx, nz = random.choice(neighbors)
                
                # "Đục tường" nằm giữa ô hiện tại và hàng xóm đã chọn.
                wall_x, wall_z = (cx + nx) // 2, (cz + nz) // 2
                grid[wall_x][wall_z] = 0
                
                # Đánh dấu ô hàng xóm là đường đi.
                grid[nx][nz] = 0
                
                # Thêm hàng xóm vào stack để tiếp tục khám phá từ vị trí mới này.
                stack.append((nx, nz))
            else:
                # Nếu không còn hàng xóm (ngõ cụt), quay lui (backtrack).
                stack.pop()

        # Chuyển đổi lưới 2D (chứa 0 và 1) thành danh sách chướng ngại vật 3D.
        obstacles = []
        for x in range(width):
            for z in range(depth):
                if grid[x][z] == 1:
                    # [SỬA] Định nghĩa rõ ràng "Tường" của mê cung sử dụng modelKey 'wall.stone01'.
                    # Điều này phân biệt nó với các "Vật cản" có thể nhảy qua.
                    obstacles.append({"type": "wall", "modelKey": "wall.stone01", "pos": (x, 0, z)})

        # Xác định vị trí bắt đầu và kết thúc của màn chơi.
        # Chúng ta thường chọn hai góc đối diện để tạo ra thử thách dài nhất.
        start_pos: Coord = (1, 0, 1)
        target_pos: Coord = (width - 2, 0, depth - 2)
        
        # Đảm bảo điểm bắt đầu và kết thúc chắc chắn là đường đi.
        # (Hiếm khi cần thiết với thuật toán này, nhưng là một bước an toàn).
        obstacles = [obs for obs in obstacles if obs["pos"] not in [start_pos, target_pos]]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=[],  # Không có đường đi định trước cho mê cung, người chơi phải tự tìm.
            obstacles=obstacles
        )
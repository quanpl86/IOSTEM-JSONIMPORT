# src/map_generator/placements/variable_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class VariablePlacer(BasePlacer):
    """
    Đặt các vật phẩm và chướng ngại vật để khuyến khích người chơi sử dụng Biến.
    
    Logic chính là tạo ra một nhiệm vụ "thu thập" và một "bài kiểm tra" ở cuối,
    buộc người chơi phải theo dõi một trạng thái (số lượng vật phẩm) trong suốt màn chơi.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường và đặt các vật phẩm để đếm, cùng với một "cổng logic"
        ở cuối để kiểm tra kết quả.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology.
            params (dict): Các tham số bổ sung.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'variable' logic...")

        # --- Bước 1: Đặt các vật phẩm để được đếm ---
        # Đối với các bài toán về biến, chúng ta thường muốn có một số lượng
        # vật phẩm đáng kể để việc đếm trở nên có ý nghĩa.
        # Chúng ta có thể chọn đặt ở tất cả các điểm hoặc một phần.
        # Để đơn giản, ta đặt ở tất cả các điểm mà Topology đã cung cấp.
        # (SỬA LỖI) Không đặt vật phẩm ở vị trí sẽ đặt cổng logic (target_pos).
        # Điều này áp dụng cho các map như SpiralPath.
        items_to_collect = [{"type": "crystal", "pos": pos} for pos in path_info.path_coords if pos != path_info.target_pos]
        
        # --- Bước 2: Tạo "Cổng logic" ---
        # Đây là một chướng ngại vật đặc biệt. Game engine sẽ hiểu rằng
        # người chơi chỉ có thể đi qua nó nếu họ đã thu thập đủ số lượng
        # vật phẩm yêu cầu.
        
        # Vị trí của cổng sẽ nằm ở vị trí đích ban đầu của con đường.
        gate_pos = path_info.target_pos
        
        # Vị trí đích MỚI của màn chơi sẽ là ô ngay sau cổng.
        # Giả sử di chuyển theo trục X để đơn giản hóa.
        # Một hệ thống hoàn thiện hơn sẽ cần kiểm tra hướng đi cuối cùng.
        final_target_pos = (gate_pos[0] + 1, gate_pos[1], gate_pos[2])

        # Tạo đối tượng chướng ngại vật "cổng"
        obstacles = [{
            "type": "logic_gate", 
            "pos": gate_pos,
            # Thêm metadata cho game engine biết điều kiện để vượt qua
            "condition": {
                "item_type": "crystal",
                "required_count": len(items_to_collect)
            }
        }]

        return {
            "start_pos": path_info.start_pos,
            "target_pos": final_target_pos, # Đích đã được dời ra sau cổng
            "items": items_to_collect,
            "obstacles": obstacles
        }
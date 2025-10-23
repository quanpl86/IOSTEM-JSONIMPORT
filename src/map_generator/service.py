# src/map_generator/service.py

from .models.map_data import MapData
from .models.path_info import PathInfo
from .topologies.simple_path import SimplePathTopology
from .topologies.straight_line import StraightLineTopology
from .topologies.staircase import StaircaseTopology
from .topologies.square import SquareTopology
from .topologies.plowing_field import PlowingFieldTopology
from .topologies.grid import GridTopology
from .topologies.symmetrical_islands import SymmetricalIslandsTopology
from .topologies.spiral import SpiralTopology
from .topologies.interspersed_path import InterspersedPathTopology
from .topologies.complex_maze import ComplexMazeTopology
from .placements.sequencing_placer import SequencingPlacer
from .placements.obstacle_placer import ObstaclePlacer # THÊM MỚI
from .placements.for_loop_placer import ForLoopPlacer
from .placements.function_placer import FunctionPlacer
from .placements.variable_placer import VariablePlacer
from .placements.while_if_placer import WhileIfPlacer
from .placements.algorithm_placer import AlgorithmPlacer

class MapGeneratorService:
    def __init__(self):
        print("⚙️  Khởi tạo MapGeneratorService...")
        self.topologies = {
            'simple_path': SimplePathTopology(),
            'straight_line': StraightLineTopology(),
            'staircase': StaircaseTopology(),
            'square_shape': SquareTopology(),
            'plowing_field': PlowingFieldTopology(),
            'grid': GridTopology(),
            'symmetrical_islands': SymmetricalIslandsTopology(),
            'spiral_path': SpiralTopology(),
            'interspersed_path': InterspersedPathTopology(),
            'complex_maze_2d': ComplexMazeTopology(),
            'variable_length_sides': StraightLineTopology(),
            'item_counting_path': StraightLineTopology(),
            'unknown_length_hallway': StraightLineTopology(),
            'unknown_height_tower': StaircaseTopology(),
            'variable_size_rectangles': PlowingFieldTopology(),
        }
        self.placements = {
            'sequencing': SequencingPlacer(),
            'obstacle': ObstaclePlacer(), # THÊM MỚI
            'function_definition': FunctionPlacer(),
            'function_decomposition': FunctionPlacer(),
            'function_with_params': FunctionPlacer(),
            'function_with_multi_params': FunctionPlacer(),
            'for_loop_simple': ForLoopPlacer(),
            'for_loop_complex': ForLoopPlacer(),
            'nested_for_loop': ForLoopPlacer(),
            # Các placer cho Topic 4 (Biến & Toán học)
            'variable_loop': VariablePlacer(),
            'variable_counter': VariablePlacer(),
            'variable_update': VariablePlacer(),
            'variable_control_loop': VariablePlacer(),
            'coordinate_math': VariablePlacer(),
            'math_basic': VariablePlacer(),
            'math_complex': VariablePlacer(),
            'math_expression_loop': VariablePlacer(),
            'config_driven_execution': VariablePlacer(),
            'math_puzzle': VariablePlacer(),
            'if_else_logic': WhileIfPlacer(),
            'if_elseif_logic': WhileIfPlacer(),
            'logical_operators': WhileIfPlacer(),
            'while_loop': WhileIfPlacer(),
            'algorithm_design': AlgorithmPlacer(),
            'advanced_algorithm': AlgorithmPlacer(),
        }
        print("👍 Đã đăng ký thành công tất cả các chiến lược.")

    def generate_map(self, map_type: str, logic_type: str, params: dict) -> MapData:
        
        # --- DEBUG POINT B ---
        print(f"    DEBUG (B): Service nhận được params: {params}")
        
        print(f"\n--- Bắt đầu sinh map: [Topology: '{map_type}', Placer: '{logic_type}'] ---")
        
        topology_strategy = self.topologies.get(map_type)
        if not topology_strategy:
            raise ValueError(f"Không tìm thấy chiến lược topology nào có tên '{map_type}' đã được đăng ký.")
            
        # (CẢI TIẾN) Tăng kích thước lưới để có không gian cho các map lớn hơn
        grid_size = (14, 14, 14)

        # [SỬA LỖI] Một số Topology (ví dụ: GridTopology) có thể truyền toàn bộ params vào PathInfo,
        # gây ra lỗi "unexpected keyword argument" nếu params chứa các key không mong muốn (như 'map_type').
        # Tạo một bản sao của params và loại bỏ các key không liên quan đến topology để đảm bảo an toàn.
        topology_params = params.copy()
        topology_params.pop('map_type', None) # Xóa 'map_type' nếu có
        path_info: PathInfo = topology_strategy.generate_path_info(grid_size=grid_size, params=topology_params)
        
        placement_strategy = self.placements.get(logic_type)
        if not placement_strategy:
            raise ValueError(f"Không tìm thấy chiến lược placement nào có tên '{logic_type}' đã được đăng ký.")
            
        final_layout: dict = placement_strategy.place_items(path_info, params=params)
        
        map_data = MapData(
            grid_size=grid_size,
            start_pos=final_layout.get('start_pos'),
            target_pos=final_layout.get('target_pos'),
            items=final_layout.get('items', []),
            obstacles=final_layout.get('obstacles', []),
            path_coords=path_info.path_coords, # (SỬA LỖI) Truyền path_coords vào MapData
            map_type=map_type,
            logic_type=logic_type
        )
        
        print(f"--- Hoàn thành sinh map: '{map_type}' ---")
        return map_data
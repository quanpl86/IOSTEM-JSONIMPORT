# src/bug_generator/service.py
from typing import Dict, Any, Type

# --- SECTION 1: Import các chiến lược tạo lỗi ---
# Import các lớp chiến lược đã được tổ chức lại
from .strategies.base_strategy import BaseBugStrategy
from .strategies.main_thread_bugs import (
    MisplacedBlocksBug,
    MissingBlockBug,
    IncorrectLoopCountBug,
    IncorrectParameterBug,
    RedundantBlocksBug,
    # Thêm các lớp khác khi bạn tạo chúng, ví dụ:
    # IncorrectInitialValueBug,
    # IncorrectMathOperatorBug,
)
# from .strategies.function_bugs import (
#     IncorrectFunctionLogicBug,
#     MissingFunctionCallBug,
# )

# --- SECTION 2: Nhà máy tạo lỗi (Bug Strategy Factory) ---
# Ánh xạ bug_type tới lớp chiến lược tương ứng.
# Cấu trúc này tuân theo bản phân loại chi tiết của bạn.
BUG_STRATEGIES: Dict[str, Type[BaseBugStrategy]] = {
    # Nhóm 1.1: Lỗi Tuần Tự và Cấu Trúc Cơ Bản
    'sequence_error': MisplacedBlocksBug,
    'missing_block': MissingBlockBug,
    # 'misplaced_control_structure': # Sẽ thêm lớp này sau
    
    # Nhóm 1.2: Lỗi Cấu Hình Khối Điều Khiển
    'incorrect_loop_count': IncorrectLoopCountBug,
    'incorrect_parameter': IncorrectParameterBug, # Ví dụ: sai hướng rẽ
    # 'incorrect_loop_condition': # Sẽ thêm lớp này sau
    
    # Nhóm 1.3: Lỗi Dữ Liệu và Tính Toán
    # 'incorrect_initial_value': IncorrectInitialValueBug,
    # 'missing_variable_update': MissingBlockBug, # Có thể dùng lại MissingBlockBug để xóa khối 'change'
    # 'incorrect_math_operator': IncorrectMathOperatorBug,
    
    # Nhóm 1.4: Lỗi Tối Ưu Hóa
    'optimization': RedundantBlocksBug,
    
    # Nhóm 2.1: Lỗi Bên Trong Hàm
    # 'incorrect_logic_in_function': IncorrectFunctionLogicBug,
    
    # Nhóm 2.2: Lỗi Gọi Hàm
    'incorrect_function_call_order': MisplacedBlocksBug, # Dùng lại logic hoán đổi khối
    # 'missing_function_call': MissingBlockBug, # Dùng lại logic xóa khối
}

# --- SECTION 3: Hàm điều phối chính (Dispatcher) ---
def create_bug(bug_type: str, data: Any, config: Dict = None) -> Any:
    """
    Hàm điều phối chính. Tìm chiến lược phù hợp, khởi tạo và áp dụng nó.
    """
    config = config or {}
    strategy_class = BUG_STRATEGIES.get(bug_type)

    if strategy_class:
        print(f"    LOG: Đang tạo lỗi loại '{bug_type}'.")
        # Tạo một bản sao để tránh thay đổi dữ liệu gốc
        data_copy = list(data) if isinstance(data, list) else str(data)
        
        # Khởi tạo và áp dụng chiến lược
        strategy_instance = strategy_class()
        return strategy_instance.apply(data_copy, config)
    else:
        print(f"    - ⚠️ Cảnh báo: Không tìm thấy chiến lược tạo lỗi cho loại '{bug_type}'. Trả về dữ liệu gốc.")
        return data
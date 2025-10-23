# src/bug_generator/strategies/main_thread_bugs.py
import random
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from .base_strategy import BaseBugStrategy

class MisplacedBlocksBug(BaseBugStrategy):
    """
    1.1. Lỗi Tuần Tự: Sai Thứ Tự Khối Lệnh (Sequence Error)
    Hoán đổi vị trí của hai khối lệnh ngẫu nhiên trong chương trình chính.
    """
    def apply(self, xml_string: str, config: Dict) -> str:
        if not xml_string: return ""
        try:
            root = ET.fromstring(f"<root>{xml_string}</root>")
            maze_start_block = root.find(".//block[@type='maze_start']")
            if maze_start_block is None: return xml_string

            statement_do = maze_start_block.find("./statement[@name='DO']")
            if statement_do is None or not list(statement_do): return xml_string

            top_level_blocks = []
            current_block = statement_do.find("./block")
            while current_block is not None:
                next_block = current_block.find("./next/block")
                next_element = current_block.find("./next")
                if next_element is not None:
                    current_block.remove(next_element)
                top_level_blocks.append(current_block)
                current_block = next_block
            
            if len(top_level_blocks) >= 2:
                idx1, idx2 = random.sample(range(len(top_level_blocks)), 2)
                top_level_blocks[idx1], top_level_blocks[idx2] = top_level_blocks[idx2], top_level_blocks[idx1]
                print(f"      -> Bug 'misplaced_blocks': Hoán đổi khối lệnh ở vị trí {idx1} và {idx2}.")

                for child in list(statement_do): statement_do.remove(child)
                for i in range(len(top_level_blocks) - 1):
                    ET.SubElement(top_level_blocks[i], 'next').append(top_level_blocks[i+1])
                statement_do.append(top_level_blocks[0])

            return "".join(ET.tostring(child, encoding='unicode') for child in root)
        except Exception as e:
            print(f"   - ⚠️ Lỗi khi tạo lỗi misplaced_blocks: {e}. Trả về chuỗi gốc.")
        return xml_string

class MissingBlockBug(BaseBugStrategy):
    """
    1.1. Lỗi Tuần Tự: Thiếu Khối Lệnh (Missing Block Error)
    Xóa một khối lệnh ngẫu nhiên.
    """
    def apply(self, data: Any, config: Dict) -> Any:
        if not isinstance(data, str): return data
        try:
            root = ET.fromstring(f"<root>{data}</root>")
            possible_parents = root.findall(".//statement/..")
            target_parent = random.choice(possible_parents) if possible_parents else root
            target_statement = target_parent.find("./statement")
            
            if target_statement is not None and len(list(target_statement)) > 1:
                blocks_in_statement = list(target_statement)
                simple_blocks_indices = [
                    i for i, b in enumerate(blocks_in_statement) 
                    if b.get('type') not in ['procedures_callnoreturn', 'maze_repeat', 'variables_set']
                ]
                
                remove_idx = random.choice(simple_blocks_indices) if simple_blocks_indices else random.randint(0, len(blocks_in_statement) - 1)
                removed_block = blocks_in_statement.pop(remove_idx)
                
                for child in list(target_statement): target_statement.remove(child)
                if blocks_in_statement:
                    for i in range(len(blocks_in_statement) - 1):
                        ET.SubElement(blocks_in_statement[i], 'next').append(blocks_in_statement[i+1])
                    target_statement.append(blocks_in_statement[0])
                print(f"      -> Bug 'missing_block': Đã xóa khối '{removed_block.get('type')}'")
                return "".join(ET.tostring(child, encoding='unicode') for child in root)
        except Exception as e:
            print(f"   - ⚠️ Lỗi khi tạo lỗi missing_block: {e}. Trả về chuỗi gốc.")
        return data

class IncorrectLoopCountBug(BaseBugStrategy):
    """
    1.2. Lỗi Cấu Hình: Sai Số Lần Lặp (Incorrect Loop Count)
    """
    def apply(self, xml_string: str, config: Dict) -> str:
        if not xml_string: return ""
        try:
            root = ET.fromstring(f"<root>{xml_string}</root>")
            repeat_fields = root.findall(".//block[@type='maze_repeat']//field[@name='NUM']")
            if repeat_fields:
                target_field = random.choice(repeat_fields)
                original_num = int(target_field.text or 1)
                bugged_num = original_num + 1 if original_num > 2 else original_num - 1
                if bugged_num <= 0: bugged_num = 1
                target_field.text = str(bugged_num)
                print(f"      -> Bug 'incorrect_loop_count': Thay đổi số lần lặp từ {original_num} thành {bugged_num}.")
                return "".join(ET.tostring(child, encoding='unicode') for child in root)
        except ET.ParseError as e:
            print(f"   - ⚠️ Lỗi khi phân tích XML để tạo lỗi incorrect_loop_count: {e}.")
        print(f"   - ⚠️ Không tìm thấy khối 'maze_repeat' để tạo lỗi. Trả về chuỗi gốc.")
        return xml_string

class IncorrectParameterBug(BaseBugStrategy):
    """
    1.2. Lỗi Cấu Hình: Sai Tham Số (Incorrect Parameter)
    Ví dụ: rẽ sai hướng.
    """
    def apply(self, xml_string: str, config: Dict) -> str:
        if not xml_string: return ""
        try:
            root = ET.fromstring(f"<root>{xml_string}</root>")
            turn_fields = root.findall(".//block[@type='maze_turn']/field[@name='DIR']")
            if turn_fields:
                target_field = random.choice(turn_fields)
                original_dir = target_field.text
                bugged_dir = "turnRight" if original_dir == "turnLeft" else "turnLeft"
                target_field.text = bugged_dir
                print(f"      -> Bug 'incorrect_parameter': Thay đổi hướng rẽ từ {original_dir} thành {bugged_dir}.")
                return "".join(ET.tostring(child, encoding='unicode') for child in root)
        except ET.ParseError as e:
            print(f"   - ⚠️ Lỗi khi phân tích XML để tạo lỗi incorrect_parameter: {e}.")
        print(f"   - ⚠️ Không tìm thấy khối 'maze_turn' để tạo lỗi incorrect_parameter.")
        return xml_string

# ... Bạn có thể thêm các lớp khác cho Nhóm 1 ở đây ...
# Ví dụ: IncorrectInitialValueBug, MissingVariableUpdateBug, IncorrectMathOperatorBug

class RedundantBlocksBug(BaseBugStrategy):
    """
    1.4. Lỗi Tối Ưu Hóa: Thừa Khối Lệnh (Redundant Blocks)
    """
    def apply(self, actions: List[str], config: Dict) -> List[str]:
        if not actions: return actions
        insert_idx = random.randint(0, len(actions))
        actions.insert(insert_idx, 'turnRight')
        actions.insert(insert_idx, 'turnLeft')
        print(f"      -> Bug 'optimization': Chèn cặp lệnh rẽ thừa ở vị trí {insert_idx}.")
        return actions

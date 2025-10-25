# scripts/calculate_lines.py
import json
import re
import sys
from typing import List

# --- HÀM TÍNH LLOC CHÍNH XÁC (ĐÃ SỬA LỖI repeat, function, if...) ---
def calculate_logical_lines_py(code: str) -> int:
    """
    Tính số dòng code logic (LLOC) từ chuỗi JavaScript.
    ĐÃ SỬA: Không tính nhầm dòng điều khiển + { thành 2 dòng.
    """
    if not code:
        return 0

    # 1. Loại bỏ comment
    code = re.sub(r'/\*[\s\S]*?\*/|//.*', '', code)

    # 2. Tách thành dòng
    lines = code.split('\n')
    logical_lines = 0
    i = 0

    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()

        # Bỏ dòng trống
        if not line:
            i += 1
            continue

        # Bỏ qua { hoặc } đơn lẻ
        if line in ['{', '}']:
            i += 1
            continue

        # --- XỬ LÝ CÁC CÂU LỆNH ĐIỀU KHIỂN + { TRONG CÙNG DÒNG ---
        # Ví dụ: for (...) {  → chỉ tính 1 dòng
        if re.match(r'^\s*(for|while|if|else\s+if|function|switch|catch|try|finally|class)\b', line):
            # Kiểm tra dòng tiếp theo
            next_line_stripped = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if next_line_stripped == '{' or next_line_stripped.startswith('{'):
                # Ghép: for (...) { → 1 LLOC
                logical_lines += 1
                i += 2  # Bỏ qua dòng { tiếp theo
                continue
            elif line.endswith('{'):
                # Trường hợp: if (...) { → đã gộp
                logical_lines += 1
                i += 1
                continue

        # --- XỬ LÝ CÂU LỆNH ĐƠN GIẢN ---
        if line.endswith(';') or line.endswith('()') or re.match(r'^\w+\s*\(', line):
            logical_lines += 1

        i += 1

    return logical_lines


# --- HÀM CHUYỂN structuredSolution → JavaScript (giữ nguyên, đã tốt) ---
def translate_structured_solution_to_js(structured_solution: List[str], raw_actions: List[str]) -> str:
    """
    Chuyển đổi structuredSolution → JavaScript.
    Dùng raw_actions để ánh xạ maze_turn.
    """
    js_code_lines = []
    indent_str = '  '
    procedure_map = {}
    turn_actions = [a for a in raw_actions if a in ['turnLeft', 'turnRight']]
    maze_turn_idx = 0

    indent_stack = [0]
    loop_var_stack = []

    i = 0
    while i < len(structured_solution):
        raw_line = structured_solution[i]
        trimmed = raw_line.strip()
        actual_indent = (len(raw_line) - len(raw_line.lstrip())) // len(indent_str)

        # Đóng khối nếu thụt lề giảm
        while actual_indent < indent_stack[-1] and len(indent_stack) > 1:
            indent_stack.pop()
            js_code_lines.append(f"{indent_str * indent_stack[-1]}}}")
            if loop_var_stack:
                loop_var_stack.pop()

        current_indent = indent_stack[-1]

        if not trimmed:
            i += 1
            continue

        if trimmed.startswith('DEFINE PROCEDURE_'):
            proc_key = trimmed.split(' ')[1][:-1]
            proc_name = f"procedure{len(procedure_map) + 1}"
            procedure_map[proc_key] = proc_name
            js_code_lines.append(f"{indent_str * current_indent}function {proc_name}() {{")
            indent_stack.append(current_indent + 1)

        elif trimmed.startswith('repeat ('):
            match = re.match(r'repeat \((\d+)\) do:', trimmed)
            if match:
                count = match.group(1)
                var = 'i' * (len(loop_var_stack) + 1)
                loop_var_stack.append(var)
                js_code_lines.append(f"{indent_str * current_indent}for (let {var} = 0; {var} < {count}; {var}++) {{")
                indent_stack.append(current_indent + 1)

        elif trimmed.startswith('MAIN PROGRAM:'):
            while len(indent_stack) > 1:
                indent_stack.pop()
                js_code_lines.append(f"{indent_str * indent_stack[-1]}}}")
                if loop_var_stack:
                    loop_var_stack.pop()
            current_indent = 0

        elif trimmed.startswith('CALL PROCEDURE_'):
            proc_key = trimmed.split(' ')[1]
            proc_name = procedure_map.get(proc_key, 'unknown_proc')
            js_code_lines.append(f"{indent_str * current_indent}{proc_name}();")

        elif trimmed == 'moveForward':
            js_code_lines.append(f"{indent_str * current_indent}moveForward();")
        elif trimmed == 'collect':
            js_code_lines.append(f"{indent_str * current_indent}collectItem();")
        elif trimmed == 'turnRight':
            js_code_lines.append(f"{indent_str * current_indent}turnRight();")
        elif trimmed == 'turnLeft':
            js_code_lines.append(f"{indent_str * current_indent}turnLeft();")
        elif trimmed.startswith('maze_turn'):
            turn = turn_actions[maze_turn_idx] if maze_turn_idx < len(turn_actions) else 'turnRight'
            js_code_lines.append(f"{indent_str * current_indent}{turn}();")
            maze_turn_idx += 1

        i += 1

    # Đóng các khối còn lại
    while len(indent_stack) > 1:
        indent_stack.pop()
        js_code_lines.append(f"{indent_str * indent_stack[-1]}}}")
        if loop_var_stack:
            loop_var_stack.pop()

    return "\n".join(js_code_lines)


# --- HÀM CHUYỂN rawActions → JavaScript (tùy chọn) ---
def translate_raw_actions_to_js(raw_actions: List[str]) -> str:
    lines = []
    for a in raw_actions:
        if a == 'moveForward':
            lines.append("moveForward();")
        elif a in ['collect', 'collectItem']:
            lines.append("collectItem();")
        elif a == 'turnLeft':
            lines.append("turnLeft();")
        elif a == 'turnRight':
            lines.append("turnRight();")
        elif a == 'maze_turn':
            lines.append("turnRight(); // default")
        else:
            lines.append(f"// Unknown: {a}")
    return "\n".join(lines)


# --- MAIN ---
def main():
    if len(sys.argv) != 2:
        print("Usage: python calculate_lines.py <path_to_solution.json>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_actions = data.get("rawActions", [])
        structured = data.get("structuredSolution", [])

        # Lấy danh sách turn để ánh xạ maze_turn
        turn_actions = [a for a in raw_actions if a in ['turnLeft', 'turnRight']]

        # Sinh JS từ structuredSolution
        js_code = translate_structured_solution_to_js(structured, turn_actions)

        # Tính LLOC
        lloc = calculate_logical_lines_py(js_code)

        # In kết quả
        print(lloc)

        # === DEBUG (bỏ comment nếu cần) ===
        # print("\n--- JS Code ---", file=sys.stderr)
        # print(js_code, file=sys.stderr)
        # print(f"\nLLOC: {lloc}", file=sys.stderr)
        # print(f"Raw LLOC: {calculate_logical_lines_py(translate_raw_actions_to_js(raw_actions))}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
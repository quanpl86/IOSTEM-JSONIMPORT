# scripts/calculate_lines.py
import json
import re
import sys
from typing import List

# ===================================================================
# HÀM TÍNH LLOC TỪ JS (DỰ PHÒNG – DÙNG TRONG generate_all_maps.py)
# ===================================================================
def calculate_logical_lines_py(js_code: str) -> int:
    """
    Tính LLOC từ chuỗi JavaScript sinh ra
    """
    if not js_code:
        return 0
    code = re.sub(r'/\*[\s\S]*?\*/|//.*', '', js_code)
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    logical_lines = 0
    for line in lines:
        if line in ['{', '}']:
            continue
        if (line.endswith(';') or line.endswith('()') or 
            line.startswith('for (') or line.startswith('if (') or 
            line.startswith('while (') or line.startswith('function ') or 
            line.startswith('} else {') or re.match(r'^\w+\s*\(', line)):
            logical_lines += 1
    return logical_lines


# ===================================================================
# HÀM TÍNH LLOC CHỈ TỪ structuredSolution (CHÍNH XÁC 100%)
# ===================================================================
def calculate_optimal_lines_from_structured(structured_solution: List[str]) -> int:
    lloc = 0
    in_main = False
    in_procedure = False
    variables = set()  # Theo dõi biến đã khai báo
    in_repeat_scope = False  # Đang trong khối repeat?

    i = 0
    while i < len(structured_solution):
        line = structured_solution[i]
        trimmed = line.strip()
        if not trimmed:
            i += 1
            continue

        # === CHUYỂN TRẠNG THÁI ===
        if trimmed == "MAIN PROGRAM:":
            in_main = True
            in_procedure = False
            i += 1
            continue
        if trimmed.startswith("DEFINE PROCEDURE_"):
            in_procedure = True
            in_main  = False
            lloc += 1  # function procedureX() {
            i += 1
            continue
        if trimmed in {"On start:", "On start."}:
            i += 1
            continue

        if not (in_main or in_procedure):
            i += 1
            continue

        # === BIẾN ===
        if trimmed == "variables_set":
            lloc += 2  # var steps; steps = 5;
            variables.add("steps")
        elif trimmed.startswith("variables_set_to "):
            parts = trimmed.split(" ", 3)
            var_name = parts[2]
            if var_name not in variables:
                lloc += 1  # var x;
                variables.add(var_name)
            lloc += 1  # x = ...

        # === VÒNG LẶP ===
        elif trimmed == "maze_repeat_variable":
            lloc += 1  # for (var count0 = 0; count0 < steps; ...)
            in_repeat_scope = True

        elif trimmed.startswith("repeat ("):
            match = re.match(r"repeat \((.+?)\) do:", trimmed)
            if match:
                repeat_arg = match.group(1).strip()
                # Nếu là số → tạo for mới
                if re.match(r"^\d+$", repeat_arg):
                    lloc += 1
                    in_repeat_scope = True
                # Nếu là biến → KHÔNG tạo for mới nếu đang trong repeat scope
                elif repeat_arg in variables:
                    if not in_repeat_scope:
                        lloc += 1
                        in_repeat_scope = True
                    # else: dùng chung vòng lặp → KHÔNG +1
                else:
                    lloc += 1
                    in_repeat_scope = True
            else:
                lloc += 1
                in_repeat_scope = True

        # === LỆNH CƠ BẢN ===
        elif trimmed in {"moveForward", "collect", "jump", "maze_turn"}:
            lloc += 1
        elif trimmed.startswith("CALL PROCEDURE_"):
            lloc += 1
        elif re.match(r"^\w+ [+*/-]?= .+", trimmed):
            lloc += 1
        elif trimmed.startswith("if ") or trimmed == "else":
            lloc += 1

        i += 1

    return lloc


# ===================================================================
# HÀM CHUYỂN structuredSolution → JS
# ===================================================================
def translate_structured_solution_to_js(structured_solution: List[str], raw_actions: List[str] = None) -> str:
    if raw_actions is None:
        raw_actions = []
    turn_actions = [a for a in raw_actions if a in ['turnLeft', 'turnRight']]
    turn_idx = 0

    js_lines = []
    indent = 0
    variables = set()
    loop_counter = 0
    in_procedure = False

    i = 0
    while i < len(structured_solution):
        line = structured_solution[i]
        trimmed = line.strip()
        current_indent = (len(line) - len(line.lstrip())) // 2

        while indent > current_indent:
            js_lines.append("  " * indent + "}")
            indent -= 1

        if not trimmed:
            i += 1
            continue

        if trimmed == "MAIN PROGRAM:":
            in_procedure = False
            i += 1
            continue
        if trimmed.startswith("DEFINE PROCEDURE_"):
            proc_name = "procedure" + trimmed.split("_")[1].rstrip(":")
            js_lines.append(f"function {proc_name}() {{")
            indent += 1
            in_procedure = True
            i += 1
            continue
        if trimmed in {"On start:", "On start."}:
            i += 1
            continue

        if trimmed == "variables_set":
            js_lines.append("  " * indent + "var steps;")
            js_lines.append("  " * indent + "steps = 5;")
        elif trimmed.startswith("variables_set_to "):
            parts = trimmed.split(" ", 3)
            var_name = parts[2]
            value = parts[3] if len(parts) > 3 else "0"
            if var_name not in variables:
                js_lines.append("  " * indent + f"var {var_name};")
                variables.add(var_name)
            js_lines.append("  " * indent + f"{var_name} = {value};")
        elif trimmed == "maze_repeat_variable":
            var = f"count{loop_counter}"
            loop_counter += 1
            js_lines.append("  " * indent + f"for (var {var} = 0; {var} < steps; {var}++) {{")
            indent += 1
        elif trimmed.startswith("repeat ("):
            n = re.search(r"\d+", trimmed).group()
            var = f"count{loop_counter}"
            loop_counter += 1
            js_lines.append("  " * indent + f"for (var {var} = 0; {var} < {n}; {var}++) {{")
            indent += 1
        elif trimmed.startswith("while "):
            cond = trimmed.split(" ", 1)[1]
            js_lines.append("  " * indent + f"while ({cond}) {{")
            indent += 1
        elif trimmed.startswith("for "):
            js_lines.append("  " * indent + trimmed.replace("for ", "for (") + ") {")
            indent += 1
        elif trimmed.startswith("if "):
            cond = trimmed.split(" ", 1)[1]
            js_lines.append("  " * indent + f"if ({cond}) {{")
            indent += 1
        elif trimmed == "else":
            indent -= 1
            js_lines.append("  " * indent + "} else {")
            indent += 1
        elif trimmed.startswith("CALL PROCEDURE_"):
            proc = "procedure" + trimmed.split("_")[1]
            js_lines.append("  " * indent + f"{proc}();")
        elif trimmed in {"moveForward", "collect", "jump"}:
            func = {"moveForward": "moveForward", "collect": "collectItem", "jump": "jump"}[trimmed]
            js_lines.append("  " * indent + f"{func}();")
        elif trimmed.startswith("maze_turn"):
            turn = turn_actions[turn_idx] if turn_idx < len(turn_actions) else "turnRight"
            js_lines.append("  " * indent + f"{turn}();")
            turn_idx += 1
        elif re.match(r"^\w+ = .+", trimmed):
            js_lines.append("  " * indent + trimmed + ";")
        elif re.match(r"^\w+ [+*/-]= .+", trimmed):
            js_lines.append("  " * indent + trimmed + ";")
        elif trimmed.startswith("math_"):
            js_lines.append("  " * indent + trimmed.replace("math_", "Math.") + ";")
        elif trimmed.startswith("logic_"):
            js_lines.append("  " * indent + trimmed.replace("logic_", "") + ";")

        i += 1

    while indent > 0:
        js_lines.append("  " * indent + "}")
        indent -= 1

    return "\n".join(js_lines)


# ===================================================================
# MAIN: CHẠY ĐỘC LẬP
# ===================================================================
def main():
    if len(sys.argv) != 2:
        print("Usage: python calculate_lines.py <path_to_solution.json>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        structured = data.get("structuredSolution", [])
        raw_actions = data.get("rawActions", [])

        # Tính LLOC từ structuredSolution (ưu tiên)
        lloc = calculate_optimal_lines_from_structured(structured)
        print("=== optimalLines (từ structuredSolution) ===")
        print(lloc)

        # (Tùy chọn) Tính từ JS
        js_code = translate_structured_solution_to_js(structured, raw_actions)
        lloc_js = calculate_logical_lines_py(js_code)
        print("\n=== LLOC từ JS (để kiểm tra) ===")
        print(lloc_js)

        print("\n=== JS SINH RA ===")
        print(js_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
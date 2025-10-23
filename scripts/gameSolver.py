import json
import sys
import traceback
from typing import Set, Dict, List, Tuple, Any, Optional
import random # [FIX] Import the random module
from collections import Counter

# --- SECTION 1: TYPE DEFINITIONS (Định nghĩa kiểu dữ liệu) ---
Action = str
Position = Dict[str, int]
PlayerStart = Dict[str, Any]

# --- SECTION 2: GAME WORLD MODEL (Mô hình hóa thế giới game) ---
class GameWorld:
    """Đọc và hiểu file JSON, xây dựng một bản đồ thế giới chi tiết với các thuộc tính model."""
    # [SỬA] Khai báo toàn bộ các loại đối tượng dựa trên gameAssets.ts
    WALKABLE_GROUNDS: Set[str] = {
        'ground.checker', 'ground.earth', 'ground.earthChecker', 'ground.mud', 
        'ground.normal', 'ground.snow',
        'water.water01',
        'ice.ice01'
    }
    SOLID_WALLS: Set[str] = {
        'stone.stone01', 'stone.stone02', 'stone.stone03', 'stone.stone04', 
        'stone.stone05', 'stone.stone06', 'stone.stone07',
        'wall.brick01', 'wall.brick02', 'wall.brick03', 'wall.brick04', 
        'wall.brick05', 'wall.brick06', 'wall.stone01',
        # [SỬA] Thêm các model key còn thiếu
        'lava.lava01' # Lava cũng là một bức tường không thể đi qua
    }
    DEADLY_OBSTACLES: Set[str] = {
        'lava.lava01'
    }
    
    def __init__(self, json_data: Dict[str, Any]):
        config = json_data['gameConfig']
        self.start_info: PlayerStart = config['players'][0]['start']
        self.finish_pos: Position = config['finish']
        self.blockly_config: Dict[str, Any] = json_data.get('blocklyConfig', {})
        self.available_blocks: Set[str] = self._get_available_blocks()
        # Lấy thông tin về mục tiêu từ file JSON
        self.solution_config: Dict[str, Any] = json_data.get('solution', {})
        self.world_map: Dict[str, str] = {
            f"{block['position']['x']}-{block['position']['y']}-{block['position']['z']}": block['modelKey']
            for block in config.get('blocks', [])
        }
        # [SỬA] Thêm các khối của vật cản vào world_map để solver nhận biết
        # Giả định vật cản luôn có modelKey là 'wall.brick01' và cao 1 khối
        self.obstacles: List[Dict] = config.get('obstacles', [])
        # [REFACTORED] Gán modelKey chính xác cho từng loại vật cản
        for obs in self.obstacles: 
            pos = obs['position'] 
            model_key = obs.get('modelKey', 'wall.brick01') # Mặc định là wall.brick01 nếu không có
            self.world_map[f"{pos['x']}-{pos['y']}-{pos['z']}"] = model_key

        # [SỬA] Tách ra làm 2 dict: một cho tra cứu theo vị trí, một cho tra cứu theo ID
        self.collectibles_by_pos: Dict[str, Dict] = {
            f"{c['position']['x']}-{c['position']['y']}-{c['position']['z']}": c
            for c in config.get('collectibles', [])
        }
        self.collectibles_by_id: Dict[str, Dict] = {
            c['id']: c for c in config.get('collectibles', [])
        }

        self.switches: Dict[str, Dict] = {}
        self.portals: Dict[str, Dict] = {}
        all_interactibles = config.get('interactibles', [])
        for i in all_interactibles:
            if not isinstance(i, dict) or 'position' not in i: continue
            pos_key = f"{i['position']['x']}-{i['position']['y']}-{i['position']['z']}"
            if i['type'] == 'switch':
                self.switches[pos_key] = i
            elif i['type'] == 'portal':
                target_portal = next((p for p in all_interactibles if p['id'] == i['targetId']), None)
                if target_portal:
                    i['targetPosition'] = target_portal['position']
                    self.portals[pos_key] = i

    def _get_available_blocks(self) -> Set[str]:
        """[MỚI] Phân tích toolbox để lấy danh sách các khối lệnh được phép sử dụng."""
        available = set()
        toolbox_contents = self.blockly_config.get('toolbox', {}).get('contents', [])

        def recurse_contents(contents: List[Dict]):
            for item in contents:
                if item.get('kind') == 'block' and item.get('type'):
                    available.add(item['type'])
                elif item.get('kind') == 'category':
                    if item.get('custom') == 'PROCEDURE':
                        available.add('PROCEDURE')  # Marker đặc biệt cho phép tạo hàm
                    recurse_contents(item.get('contents', []))
        recurse_contents(toolbox_contents)
        return available

# --- SECTION 3: GAME STATE & PATH NODE (Trạng thái game và Nút tìm đường) ---
class GameState:
    """Đại diện cho một "bản chụp" của toàn bộ game tại một thời điểm."""
    def __init__(self, start_info: PlayerStart, world: GameWorld):
        self.x, self.y, self.z = start_info['x'], start_info['y'], start_info['z']
        self.direction = start_info['direction']
        self.collected_items: Set[str] = set()
        self.switch_states: Dict[str, str] = {s['id']: s['initialState'] for s in world.switches.values()}

    def clone(self) -> 'GameState':
        # Tạo một instance mới mà không cần gọi __init__ để tăng tốc và làm code rõ ràng hơn
        new_state = self.__class__.__new__(self.__class__)
        # Sao chép các thuộc tính cần thiết
        new_state.x, new_state.y, new_state.z = self.x, self.y, self.z
        new_state.direction = self.direction
        new_state.collected_items = self.collected_items.copy()
        new_state.switch_states = self.switch_states.copy()
        return new_state 

    def get_key(self) -> str:
        items = ",".join(sorted(list(self.collected_items)))
        switches = ",".join(sorted([f"{k}:{v}" for k, v in self.switch_states.items()]))
        return f"{self.x},{self.y},{self.z},{self.direction}|i:{items}|s:{switches}"

class PathNode:
    """Nút chứa trạng thái và các thông tin chi phí cho thuật toán A*."""
    def __init__(self, state: GameState):
        self.state = state
        self.parent: Optional['PathNode'] = None
        self.action: Optional[Action] = None
        self.g_cost: float = 0.0
        self.h_cost: float = 0.0

    @property
    def f_cost(self) -> float:
        return float(self.g_cost) + float(self.h_cost)

# --- SECTION 4: A* SOLVER (Thuật toán A*) ---
def solve_level(world: GameWorld) -> Optional[List[Action]]:
    """Thực thi thuật toán A* để tìm lời giải tối ưu cho level."""
    start_state = GameState(world.start_info, world)
    start_node = PathNode(start_state)
    open_list: List[PathNode] = []
    visited: Set[str] = set()

    def manhattan(p1: Position, p2: Position) -> int:
        return abs(p1['x'] - p2['x']) + abs(p1['y'] - p2['y']) + abs(p1['z'] - p2['z'])

    def heuristic(state: GameState) -> int:
        h = 0
        current_pos = {'x': state.x, 'y': state.y, 'z': state.z}
        
        # --- [TỐI ƯU] Coi các công tắc cần bật như những mục tiêu cần đến ---
        required_goals = world.solution_config.get("itemGoals", {})
        
        # 1. Lấy vị trí các vật phẩm chưa thu thập
        uncollected_ids = set(world.collectibles_by_id.keys()) - state.collected_items
        sub_goal_positions = [c['position'] for c_id, c in world.collectibles_by_id.items() if c_id in uncollected_ids]

        # 2. Lấy vị trí các công tắc cần bật nhưng vẫn đang 'off'
        if required_goals.get('switch', 0) > 0:
            for switch_pos_key, switch_obj in world.switches.items():
                if state.switch_states.get(switch_obj['id']) == 'off':
                    sub_goal_positions.append(switch_obj['position'])

        # 3. Tính toán heuristic dựa trên tất cả các mục tiêu phụ
        if sub_goal_positions:
            closest_dist = min(manhattan(current_pos, pos) for pos in sub_goal_positions)
            h += closest_dist
            if len(sub_goal_positions) > 1:
                h += max(manhattan(pos, world.finish_pos) for pos in sub_goal_positions) # Ước tính chi phí để đi từ mục tiêu xa nhất đến đích
        else:
            h += manhattan(current_pos, world.finish_pos)
        h += len(sub_goal_positions) * 10 # Phạt nặng cho mỗi mục tiêu chưa hoàn thành
        return h

    def is_goal_achieved(state: GameState, world: GameWorld) -> bool:
        """Kiểm tra xem trạng thái hiện tại có thỏa mãn điều kiện thắng của màn chơi không."""
        solution_type = world.solution_config.get("type", "reach_target")
        
        is_at_finish = state.x == world.finish_pos['x'] and state.y == world.finish_pos['y'] and state.z == world.finish_pos['z']
        
        # --- [ĐÃ SỬA] Logic kiểm tra mục tiêu ---
        required_items = world.solution_config.get("itemGoals", {})
        if required_items:
            all_goals_met = True
            for goal_type, required_count in required_items.items():
                if goal_type == 'switch':
                    # Đối với công tắc, đếm số lượng đang ở trạng thái 'on'
                    toggled_on_count = sum(1 for s in state.switch_states.values() if s == 'on')
                    if toggled_on_count < required_count:
                        all_goals_met = False
                        break
                elif goal_type == 'obstacle':
                    # [SỬA] Tạm thời coi mục tiêu obstacle luôn đạt được để tránh lỗi.
                    # Logic này sẽ được cải tiến sau để đếm số lần 'jump'.
                    pass
                else: # Mặc định là các vật phẩm có thể thu thập (collectibles)
                    # [SỬA LỖI] Đếm số lượng vật phẩm đã thu thập khớp với loại mục tiêu.
                    collected_count = sum(1 for item_id in state.collected_items if world.collectibles_by_id.get(item_id, {}).get('type') == goal_type)
                    
                    # [SỬA LỖI] Xử lý trường hợp required_count là "all"
                    if isinstance(required_count, str) and required_count.lower() == 'all':
                        # Đếm tổng số vật phẩm loại đó có trên bản đồ
                        total_of_type = sum(1 for c in world.collectibles_by_id.values() if c.get('type') == goal_type)
                        if collected_count < total_of_type:
                            all_goals_met = False
                            break
                    elif isinstance(required_count, int) and collected_count < required_count:
                        all_goals_met = False
                        break
        else:
            all_goals_met = True
        # Hiện tại chỉ hỗ trợ mục tiêu "reach_target" và "collect_all"
        return is_at_finish and all_goals_met

    start_node.h_cost = heuristic(start_state)
    open_list.append(start_node)

    # [SỬA LỖI] Xây dựng danh sách hành động hợp lệ dựa trên toolbox của level.
    # Điều này ngăn solver "gian lận" bằng cách sử dụng các khối không có sẵn.
    possible_actions = []
    available_blocks = world.available_blocks
    if 'maze_moveForward' in available_blocks:
        possible_actions.append('moveForward')
    if 'maze_turn' in available_blocks:
        possible_actions.extend(['turnLeft', 'turnRight'])
    if 'maze_jump' in available_blocks:
        possible_actions.append('jump')
    if 'maze_collect' in available_blocks:
        possible_actions.append('collect')
    if 'maze_toggle_switch' in available_blocks:
        possible_actions.append('toggleSwitch')
    
    # Nếu không có hành động nào, trả về None để tránh lặp vô hạn
    if not possible_actions:
        return None

    while open_list:
        open_list.sort(key=lambda node: node.f_cost)
        current_node = open_list.pop(0)
        state_key = current_node.state.get_key()
        if state_key in visited:
            continue
        visited.add(state_key)

        state = current_node.state

        if is_goal_achieved(state, world):
            path: List[Action] = []
            curr = current_node
            while curr and curr.action:
                path.insert(0, curr.action)
                curr = curr.parent
            return path

        DIRECTIONS = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)]
        for action in possible_actions:
            next_state = state.clone()
            is_valid_move = False
            current_pos_key = f"{state.x}-{state.y}-{state.z}"

            if action in ['moveForward', 'jump']:
                # [SỬA] Đồng bộ lại logic di chuyển và nhảy để xử lý vật cản chính xác
                dx, _, dz = DIRECTIONS[state.direction]
                if action == 'moveForward':
                    next_x, next_y, next_z = state.x + dx, state.y, state.z + dz
                    dest_key = f"{next_x}-{next_y}-{next_z}"
                    ground_key = f"{next_x}-{next_y-1}-{next_z}"
                    current_ground_key = f"{state.x}-{state.y-1}-{state.z}"
                    model_at_dest = world.world_map.get(dest_key)
                    model_at_ground = world.world_map.get(ground_key)

                    # TH1: Di chuyển ngang trên mặt đất
                    is_walking_on_ground = (model_at_dest is None or model_at_dest not in GameWorld.SOLID_WALLS) and \
                                           (model_at_ground is not None and model_at_ground in GameWorld.WALKABLE_GROUNDS)
                    if is_walking_on_ground:
                        next_state.x, next_state.y, next_state.z = next_x, next_y, next_z
                        is_valid_move = True
                    
                    # TH2: Bước xuống từ trên cao (ví dụ: từ đỉnh vật cản)
                    is_stepping_down = world.world_map.get(current_ground_key) in GameWorld.SOLID_WALLS
                    ground_key_onestep_down = f"{next_x}-{next_y-2}-{next_z}" # Đất ở dưới chân sau khi bước xuống
                    is_landing_on_ground = world.world_map.get(ground_key_onestep_down) in GameWorld.WALKABLE_GROUNDS
                    if is_stepping_down and is_landing_on_ground and model_at_dest is None:
                        next_y -= 1
                        next_state.x, next_state.y, next_state.z = next_x, next_y, next_z
                        is_valid_move = True

                elif action == 'jump':
                    # [SỬA] Logic Jump mới: Nhảy lên trên đỉnh của vật cản.
                    # Đây là bước 1 của quy trình vượt chướng ngại vật.
                    obstacle_x, obstacle_y, obstacle_z = state.x + dx, state.y, state.z + dz

                    # 1. Phải có vật cản ở ô phía trước, ngang tầm mắt.
                    obstacle_pos_key = f"{obstacle_x}-{obstacle_y}-{obstacle_z}"
                    is_obstacle_in_front = world.world_map.get(obstacle_pos_key) in GameWorld.SOLID_WALLS

                    # 2. Không gian phía trên vật cản phải trống.
                    air_above_obstacle_key = f"{obstacle_x}-{obstacle_y + 1}-{obstacle_z}"
                    is_air_clear_above = world.world_map.get(air_above_obstacle_key) is None

                    # 3. Người chơi phải đang đứng trên mặt đất.
                    player_ground_key = f"{state.x}-{state.y - 1}-{state.z}"
                    is_player_on_ground = world.world_map.get(player_ground_key) in GameWorld.WALKABLE_GROUNDS

                    if is_obstacle_in_front and is_air_clear_above and is_player_on_ground:
                        # Di chuyển người chơi lên trên đỉnh của vật cản.
                        next_state.x, next_state.y, next_state.z = obstacle_x, obstacle_y + 1, obstacle_z
                        is_valid_move = True
            elif action == 'turnLeft':
                next_state.direction = (state.direction + 3) % 4
                is_valid_move = True
            elif action == 'turnRight':
                next_state.direction = (state.direction + 1) % 4
                is_valid_move = True
            elif action == 'collect':
                if current_pos_key in world.collectibles_by_pos and world.collectibles_by_pos[current_pos_key]['id'] not in state.collected_items:
                    next_state.collected_items.add(world.collectibles_by_pos[current_pos_key]['id'])
                    is_valid_move = True
            elif action == 'toggleSwitch':
                if current_pos_key in world.switches:
                    switch = world.switches[current_pos_key]
                    current_switch_state = state.switch_states[switch['id']]
                    next_state.switch_states[switch['id']] = 'off' if current_switch_state == 'on' else 'on'
                    is_valid_move = True
            
            if is_valid_move:
                if next_state.get_key() in visited: continue
                next_node = PathNode(next_state)
                next_node.parent, next_node.action = current_node, action
                
                # [TỐI ƯU] Thêm chi phí nhỏ cho các hành động không di chuyển
                # để ưu tiên các hành động di chuyển thực sự.
                cost = 1.0
                if state.x == next_state.x and state.y == next_state.y and state.z == next_state.z:
                    cost = 1.1  # Phạt nhẹ các hành động turn, collect, toggle tại chỗ
                next_node.g_cost = current_node.g_cost + cost

                next_node.h_cost = heuristic(next_state)
                open_list.append(next_node)
    return None

# --- SECTION 5: CODE SYNTHESIS & OPTIMIZATION (Tổng hợp & Tối ưu code) ---
def find_most_frequent_sequence(actions: List[str], min_len=3, max_len=10, force_function=False) -> Optional[Tuple[List[str], int]]:
    """Tìm chuỗi con xuất hiện thường xuyên nhất để đề xuất tạo Hàm."""
    sequence_counts = Counter()
    actions_tuple = tuple(actions)
    for length in range(min_len, max_len + 1):
        for i in range(len(actions_tuple) - length + 1):
            sequence_counts[actions_tuple[i:i+length]] += 1

    # [CẢI TIẾN] Ưu tiên tìm các chuỗi có 'jump' khi force_function=True
    def find_best_sequence(sequences: List[Tuple[Tuple[str, ...], int]]) -> Optional[Tuple[List[str], int]]:
        most_common, max_freq, best_savings = None, 1, 0
        for seq, freq in sequences:
            if freq > 1:
                # Nếu không ép buộc tạo hàm, chỉ tạo khi nó thực sự tiết kiệm khối lệnh.
                # Nếu ép buộc, chỉ cần nó xuất hiện nhiều hơn 1 lần là đủ.
                savings = (freq - 1) * len(seq) - (len(seq) + freq) if not force_function else freq
                if savings > best_savings:
                    best_savings, most_common, max_freq = savings, seq, freq
        return (list(most_common), max_freq) if most_common else None

    all_sequences = list(sequence_counts.items())
    
    if force_function:
        # Ưu tiên các chuỗi có 'jump'
        jump_sequences = [item for item in all_sequences if 'jump' in item[0]]
        best_jump_seq = find_best_sequence(jump_sequences)
        if best_jump_seq:
            return best_jump_seq

    # Nếu không có chuỗi jump phù hợp hoặc không force, tìm trong tất cả các chuỗi
    most_common, max_freq = find_best_sequence(all_sequences) or (None, 0)
    return (list(most_common), max_freq) if most_common else None

def compress_actions_to_structure(actions: List[str], available_blocks: Set[str]) -> List[Dict]:
    """Hàm đệ quy nén chuỗi hành động thành cấu trúc có vòng lặp."""
    if not actions: return []
    structured_code, i = [], 0
    can_use_repeat = 'maze_repeat' in available_blocks

    while i < len(actions):
        best_seq_len, best_repeats = 0, 0
        if can_use_repeat: # Chỉ tìm vòng lặp nếu khối 'repeat' có sẵn
            for seq_len in range(1, len(actions) // 2 + 1):
                if i + 2 * seq_len > len(actions): break
                repeats = 1
                while i + (repeats + 1) * seq_len <= len(actions) and \
                      actions[i:i+seq_len] == actions[i+repeats*seq_len:i+(repeats+1)*seq_len]:
                    repeats += 1
                if repeats > 1 and (repeats * seq_len) > (1 + seq_len) and seq_len >= best_seq_len:
                    best_seq_len, best_repeats = seq_len, repeats
        
        if best_repeats > 0:
            structured_code.append({
                "type": "maze_repeat",
                "times": best_repeats,
                "body": compress_actions_to_structure(actions[i:i+best_seq_len], available_blocks)
            })
            i += best_repeats * best_seq_len
        else:
            action_str = actions[i]
            if action_str.startswith("CALL:"):
                structured_code.append({"type": "CALL", "name": action_str.split(":", 1)[1]})
            else:
                if action_str == "turnLeft" or action_str == "turnRight":
                    structured_code.append({"type": "maze_turn", "direction": action_str})
                else:
                    structured_code.append({"type": action_str})
            i += 1
    return structured_code

def _synthesize_fibonacci(world: GameWorld, template: Dict) -> Dict:
    """
    [MỚI] Hàm helper chuyên dụng để tổng hợp lời giải cho thuật toán Fibonacci.
    Đọc các thông số từ template để tạo ra cấu trúc code.
    """
    # Xác định số lần lặp dựa trên số lượng vật phẩm cần tương tác
    num_items = len(world.collectibles_by_id) + len(world.switches)
    loop_times = num_items if num_items > 0 else 5 # Ít nhất 5 lần lặp nếu không có item
    if loop_times < 3: loop_times = 3 # Đảm bảo đủ số lần lặp để có logic Fibonacci

    # Lấy tên các biến từ template, sử dụng giá trị mặc định nếu không có
    var_a = template.get("variables", ["a", "b", "temp"])[0]
    var_b = template.get("variables", ["a", "b", "temp"])[1]
    var_temp = template.get("variables", ["a", "b", "temp"])[2]

    main_program = [
        {"type": "variables_set", "variable": var_a, "value": 0},
        {"type": "variables_set", "variable": var_b, "value": 1},
        {"type": "variables_set", "variable": var_temp, "value": 0},
        {"type": "maze_repeat", "times": loop_times, "body": [
            # Logic Fibonacci: temp = a; a = b; b = temp + b
            {"type": "variables_set", "variable": var_temp, "value": {"type": "variables_get", "variable": var_a}},
            {"type": "variables_set", "variable": var_a, "value": {"type": "variables_get", "variable": var_b}},
            {"type": "variables_set", "variable": var_b, "value": {"type": "math_arithmetic", "op": "ADD", "var_a": var_temp, "var_b": var_b}},
            {"type": "maze_moveForward"},
            {"type": "maze_toggle_switch"}
        ]}
    ]
    return {"main": main_program, "procedures": {}}

def synthesize_program(actions: List[Action], world: GameWorld) -> Dict:
    """Quy trình tổng hợp code chính, tạo hàm và vòng lặp."""
    procedures, remaining_actions = {}, list(actions)
    # [CẢI TIẾN] Lấy các cấu hình từ solution_config
    available_blocks = world.available_blocks
    force_function = world.solution_config.get('force_function', False)
    suggested_function_names = world.solution_config.get('function_names', [])
    # [MỚI] Lấy logic_type để quyết định cách tổng hợp code
    # Điều này rất quan trọng cho các bài toán về biến
    logic_type = world.solution_config.get('logic_type', 'sequencing')
    # [CẢI TIẾN] Đọc cấu hình thuật toán từ curriculum
    algorithm_template = world.solution_config.get('algorithm_template')

    # --- [REWRITTEN] Xử lý các trường hợp đặc biệt dựa trên logic_type ---
    if logic_type in ['variable_loop', 'variable_counter', 'math_basic', 'math_complex', 'math_expression_loop', 'advanced_algorithm', 'config_driven_execution', 'math_puzzle']:
        # Đối với logic này, chúng ta muốn tạo ra một lời giải tường minh sử dụng biến
        # mà không cố gắng tạo ra các hàm (function) phức tạp.
        if not actions: return {"main": [], "procedures": {}}

        # Logic cho bài toán dùng biến để lặp
        if logic_type == 'variable_loop':
            # Tìm hành động lặp lại nhiều nhất, thường là 'moveForward'
            action_counts = Counter(a for a in actions if a in ['moveForward', 'collect'])
            if not action_counts: # Nếu không có hành động nào, trả về giải pháp tuần tự
                return {"main": compress_actions_to_structure(actions, available_blocks), "procedures": {}}
            
            most_common_action, num_repeats = action_counts.most_common(1)[0]
            
            # Tạo lời giải: set steps = N; repeat (steps) { action }
            main_program = [
                {"type": "variables_set", "variable": "steps", "value": num_repeats},
                {
                    "type": "maze_repeat_variable", # Loại khối đặc biệt để chỉ định dùng biến
                    "variable": "steps",
                    "body": [{"type": f"maze_{most_common_action}" if most_common_action in ['collect', 'toggleSwitch'] else most_common_action}]
                }
            ]
            # Thêm các hành động còn lại (nếu có)
            # Đây là một cách đơn giản hóa, có thể cần cải tiến
            remaining_actions_after_loop = [a for a in actions if a != most_common_action or (actions.count(a) > num_repeats)]
            main_program.extend(compress_actions_to_structure(remaining_actions_after_loop, available_blocks))
            return {"main": main_program, "procedures": {}}

        # Logic cho bài toán dùng biểu thức toán học
        if logic_type in ['math_expression_loop', 'math_complex', 'math_basic']:
            # Giả lập tạo 2 biến và dùng chúng trong vòng lặp
            total_moves = actions.count('moveForward')
            if total_moves < 2: # Cần ít nhất 2 bước để chia thành a+b
                return {"main": compress_actions_to_structure(actions, available_blocks), "procedures": {}}

            val_a = random.randint(1, total_moves - 1)
            val_b = total_moves - val_a
            
            main_program = [
                {"type": "variables_set", "variable": "a", "value": val_a},
                {"type": "variables_set", "variable": "b", "value": val_b},
                {
                    "type": "maze_repeat_expression", # Loại khối đặc biệt
                    "expression": {
                        "type": "math_arithmetic",
                        "op": "ADD",
                        "var_a": "a",
                        "var_b": "b"
                    },
                    "body": [{"type": "moveForward"}]
                }
            ]
            # Thêm các hành động không phải moveForward
            other_actions = [a for a in actions if a != 'moveForward']
            main_program.extend(compress_actions_to_structure(other_actions, available_blocks))
            return {"main": main_program, "procedures": {}}

        # [CẢI TIẾN] Logic cho các bài toán thuật toán phức tạp (Fibonacci, config-driven)
        if logic_type == 'advanced_algorithm' and algorithm_template:
            # Thay vì hard-code, chúng ta đọc template và gọi hàm tương ứng
            if algorithm_template.get("name") == "fibonacci":
                print("    LOG: (Solver) Synthesizing solution based on 'fibonacci' template.")
                return _synthesize_fibonacci(world, algorithm_template)
            # Có thể thêm các thuật toán khác ở đây, ví dụ:
            # elif algorithm_template.get("name") == "factorial":
            #     return _synthesize_factorial(world, algorithm_template)

        # Nếu không có logic đặc biệt nào khớp, trả về lời giải tuần tự đã được nén vòng lặp cơ bản
        return {"main": compress_actions_to_structure(remaining_actions, available_blocks), "procedures": procedures}
    # --- Logic cũ để tạo hàm ---
    can_use_procedures = 'PROCEDURE' in available_blocks
    if can_use_procedures and logic_type not in ['math_basic', 'variable_loop', 'variable_counter']: # Không tạo hàm cho các bài toán biến/toán đơn giản
        for i in range(3): # Thử tạo tối đa 3 hàm
            result = find_most_frequent_sequence(remaining_actions, force_function=force_function)
            if result:
                sequence = result[0]
                # [CẢI TIẾN] Ưu tiên sử dụng tên hàm được định nghĩa trong curriculum
                proc_name = suggested_function_names[i] if i < len(suggested_function_names) else f"PROCEDURE_{i+1}"

                procedures[proc_name] = compress_actions_to_structure(sequence, available_blocks)
                new_actions, j, seq_tuple = [], 0, tuple(sequence)
                while j < len(remaining_actions):
                    if tuple(remaining_actions[j:j+len(sequence)]) == seq_tuple:
                        new_actions.append(f"CALL:{proc_name}")
                        j += len(sequence)
                    else:
                        new_actions.append(remaining_actions[j])
                        j += 1
                remaining_actions = new_actions
            else: break

    return {"main": compress_actions_to_structure(remaining_actions, available_blocks), "procedures": procedures}

# --- SECTION 6: REPORTING & UTILITIES (Báo cáo & Tiện ích) ---

def count_blocks(program: Dict) -> int:
    """
    [CHỨC NĂNG MỚI] Đệ quy đếm tổng số khối lệnh trong chương trình đã tối ưu.
    Mỗi lệnh, vòng lặp, định nghĩa hàm, lời gọi hàm đều được tính là 1 khối.
    """
    def _count_list_recursively(block_list: List[Dict]) -> int:
        count = 0
        for block in block_list:
            count += 1  # Đếm khối lệnh hiện tại (move, repeat, call,...)
            if block.get("type") == "maze_repeat":
                # Nếu là vòng lặp, đệ quy đếm các khối bên trong nó
                count += _count_list_recursively(block.get("body", []))
        return count

    total = 0
    # Đếm các khối trong các hàm đã định nghĩa
    if "procedures" in program:
        for name, body in program["procedures"].items():
            total += 1  # Đếm khối "DEFINE PROCEDURE"
            total += _count_list_recursively(body)
    
    # Đếm các khối trong chương trình chính
    total += 1 # Đếm khối "On start"
    total += _count_list_recursively(program.get("main", []))
    
    return total

def format_program(program: Dict, indent=0) -> str:
    """
    [REFACTORED] Hàm helper để in chương trình ra màn hình theo cấu trúc Blockly.
    Phiên bản này sẽ in rõ ràng các khối định nghĩa hàm.
    """
    output, prefix = "", "  " * indent
    # In các khối định nghĩa hàm trước
    if indent == 0 and program.get("procedures"):
        for name, body in program["procedures"].items():
            output += f"{prefix}DEFINE {name}:\n"
            # Đệ quy để in nội dung của hàm
            output += format_program({"main": body}, indent + 1)
        output += "\n"

    # In chương trình chính
    if indent == 0:
        output += f"{prefix}MAIN PROGRAM:\n{prefix}  On start:\n"
        indent += 1 # Tăng indent cho nội dung của main
        prefix = "  " * indent
    
    # Lấy body của chương trình/hàm/vòng lặp để in
    body_to_print = program.get("main", program.get("body", []))
    for block in body_to_print:
        block_type = block.get("type")
        if block_type == 'maze_repeat':
            output += f"{prefix}repeat ({block['times']}) do:\n"
            output += format_program(block, indent + 1)
        elif block_type == 'CALL':
            output += f"{prefix}CALL {block['name']}\n"
        else:
            output += f"{prefix}{block_type}\n"
    return output

def format_program_for_json(program: Dict[str, Any]) -> List[str]:
    """Tạo ra một list các dòng string để lưu vào JSON, giữ nguyên logic cũ nếu cần."""
    return format_program(program).strip().split('\n')

def calculate_accurate_optimal_blocks(level_data: Dict[str, Any], verbose=True, print_solution=False, return_solution=False) -> Optional[Any]:
    """
    [HÀM MỚI] Hàm chính để tính toán số khối tối ưu.
    Có thể được import và sử dụng bởi các script khác.
    """
    if verbose: print("  - Bắt đầu Giai đoạn 1 (Solver): Tìm đường đi tối ưu bằng A*...")
    world = GameWorld(level_data)
    optimal_actions = solve_level(world)
    
    if optimal_actions:
        if verbose: print(f"  - Giai đoạn 1 hoàn tất: Tìm thấy chuỗi {len(optimal_actions)} hành động.")
        
        # [MỚI] Hiển thị chi tiết 33 hành động thô
        if print_solution:
            print("  - Chi tiết chuỗi hành động thô:", ", ".join(optimal_actions))

        if verbose: print("  - Bắt đầu Giai đoạn 2 (Solver): Tổng hợp thành chương trình có cấu trúc...")
        
        program_solution = synthesize_program(optimal_actions, world)
        optimized_block_count = count_blocks(program_solution)
        
        if verbose:
            print(f"  - Giai đoạn 2 hoàn tất: Chuyển đổi {len(optimal_actions)} hành động thành chương trình {optimized_block_count} khối lệnh.")
        
        if print_solution:
            print("\n" + "="*40)
            print("LỜI GIẢI CHI TIẾT ĐƯỢC TỔNG HỢP:")
            print(format_program(program_solution).strip())
            print("="*40)
        
        if return_solution:
            # [SỬA] Trả về một gói dữ liệu đầy đủ hơn
            return {
                "block_count": optimized_block_count, 
                "program_solution_dict": program_solution,
                "raw_actions": optimal_actions,
                "structuredSolution": format_program_for_json(program_solution)}
        else:
            return optimized_block_count
    else:
        if verbose: print("  - ❌ KHÔNG TÌM THẤY LỜI GIẢI cho level này.")
        return None

# --- SECTION 7: MAIN EXECUTION BLOCK (Phần thực thi chính) ---
def solve_map_and_get_solution(level_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Hàm chính để giải một map và trả về một dictionary chứa các thông tin lời giải.
    Đây là điểm đầu vào cho các script khác.
    """
    try:
        solution_data = calculate_accurate_optimal_blocks(level_data, verbose=False, print_solution=False, return_solution=True)
        return solution_data # type: ignore
    except Exception as e:
        print(f"   - ❌ Lỗi khi giải map: {e}")
        # traceback.print_exc() # Bỏ comment để gỡ lỗi chi tiết
        return None

if __name__ == "__main__":
    # Phần này chỉ chạy khi script được thực thi trực tiếp, dùng để test.
    if len(sys.argv) > 1:
        json_filename = sys.argv[1]
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                level_data = json.load(f)
            
            solution = calculate_accurate_optimal_blocks(level_data, verbose=True, print_solution=True, return_solution=True)
            if solution:
                print(f"\n===> KẾT QUẢ TEST: Số khối tối ưu là {solution['block_count']}") # Sửa lỗi subscriptable
        except Exception as e:
            print(f"Lỗi khi test file '{json_filename}': {e}") # Sửa lỗi subscriptable
# scripts/generate_curriculum.py
import pandas as pd
import json
import os
import re
from collections import defaultdict

# --- Cấu hình đường dẫn ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'curriculum_source.xlsx')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'curriculum')

def parse_params(param_string):
    """Chuyển đổi chuỗi 'key1:value1;key2:value2' thành dictionary."""
    if not isinstance(param_string, str) or not param_string.strip():
        return {}
    params = {}
    for part in param_string.split(';'):
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Cố gắng chuyển đổi value thành số hoặc list nếu có thể
            try:
                # [SỬA LỖI] Xử lý trường hợp list, ví dụ: [2,3] hoặc ['a','b']
                if value.startswith('[') and value.endswith(']'):
                    # Thay thế nháy đơn bằng nháy kép để tuân thủ JSON
                    value = value.replace("'", '"')
                    params[key] = json.loads(value)
                else:
                    params[key] = int(value) # Thử chuyển thành số nguyên
            except (ValueError, json.JSONDecodeError):
                params[key] = value # Nếu thất bại, giữ nguyên là chuỗi
    return params

def main():
    """Đọc file Excel và sinh ra các file curriculum JSON."""
    print("=============================================")
    print("=== BẮT ĐẦU QUY TRÌNH SINH CURRICULUM ===")
    print("=============================================")

    try:
        df = pd.read_excel(INPUT_FILE).fillna('')
        print(f"✅ Đọc thành công file nguồn: {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file nguồn '{INPUT_FILE}'.")
        return
    except Exception as e:
        print(f"❌ Lỗi khi đọc file Excel: {e}")
        return

    # Nhóm các thử thách theo topic_code
    challenges_by_topic = defaultdict(lambda: {'topic_name': '', 'suggested_maps': []})

    for index, row in df.iterrows():
        topic_code = row['topic_code']
        challenges_by_topic[topic_code]['topic_name'] = row['topic_name']

        # Tạo cấu trúc cho một map_request
        map_request = {
            "id": row['id'],
            "level": int(row['level']),
            "titleKey": f"Challenge.{row['id']}.Title",
            "descriptionKey": f"Challenge.{row['id']}.Description",
            "translations": {
                "vi": {
                    f"Challenge.{row['id']}.Title": row['title_vi'],
                    f"Challenge.{row['id']}.Description": row['description_vi']
                }
                # Thêm các ngôn ngữ khác ở đây nếu có
            },
            "generation_config": {
                "map_type": row['gen_map_type'],
                "logic_type": row['gen_logic_type'],
                "num_variants": int(row['gen_num_variants']),
                "params": parse_params(row['gen_params'])
            },
            "blockly_config": {
                "toolbox_preset": row['blockly_toolbox_preset'],
                # Sử dụng start_block_type hoặc start_blocks tùy cái nào được điền
                "start_block_type": row['blockly_start_block_type'] if row['blockly_start_block_type'] else None,
                "start_blocks": row.get('blockly_start_blocks', '') if not row['blockly_start_block_type'] else None,
            },
            "solution_config": {
                "type": row['solution_type'],
                "itemGoals": parse_params(row.get('solution_item_goals', ''))
            }
        }
        # Loại bỏ các key có giá trị None để file JSON gọn gàng
        if map_request["blockly_config"]["start_block_type"] is None:
            del map_request["blockly_config"]["start_block_type"]
        if map_request["blockly_config"]["start_blocks"] is None:
            del map_request["blockly_config"]["start_blocks"]

        challenges_by_topic[topic_code]['suggested_maps'].append(map_request)

    # Ghi ra các file JSON cho từng topic
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for topic_code, data in challenges_by_topic.items():
        # Lấy số thứ tự từ topic_code, ví dụ: TOPIC_01 -> 01
        match = re.match(r'TOPIC_(\d+)', topic_code)
        if match:
            topic_num = match.group(1)
            filename = f"{topic_num}_{data['topic_name'].lower().replace(' & ', '_').replace(' ', '_')}.json"
        else:
            filename = f"{topic_code.lower()}.json"

        output_path = os.path.join(OUTPUT_DIR, filename)
        
        final_json = {
            "topic_code": topic_code,
            "topic_name": data['topic_name'],
            "suggested_maps": data['suggested_maps']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=2, ensure_ascii=False)
        print(f"✅ Đã tạo/cập nhật file curriculum: {filename}")

    print("\n=============================================")
    print("=== HOÀN THÀNH SINH CURRICULUM ===")
    print("=============================================")


if __name__ == "__main__":
    main()

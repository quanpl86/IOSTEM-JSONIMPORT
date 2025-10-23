# main.py

# Import hàm main từ các script nghiệp vụ.
# Đổi tên để tránh nhầm lẫn với hàm 'main' của chính file này.
from scripts.generate_curriculum import main as generate_curriculum_main
from scripts.generate_all_maps import main as generate_all_maps_main

def main():
    """
    Hàm chính của chương trình, đóng vai trò là điểm khởi chạy.
    Nó điều phối một chuỗi các tác vụ:
    1. Sinh file curriculum từ file Excel.
    2. Sinh các file game level cuối cùng từ curriculum.
    """
    print("============================================")
    print("=== KHỞI CHẠY TỪ ĐIỂM ĐẦU VÀO CHÍNH (main.py) ===")
    print("============================================")
    
    # Bước 1: Chạy script để sinh/cập nhật các file curriculum từ nguồn (Excel)
    generate_curriculum_main()
    
    # In một dòng ngăn cách để dễ đọc log
    print("\n" + "="*50 + "\n")

    # Bước 2: Chạy script để sinh tất cả các map game từ curriculum đã được tạo
    generate_all_maps_main()
    
    print("\n============================================")
    print("=== KẾT THÚC TOÀN BỘ TÁC VỤ TỪ main.py ===")
    print("============================================")


if __name__ == "__main__":
    # Dòng này đảm bảo rằng hàm main() chỉ được chạy khi file này
    # được thực thi trực tiếp, không phải khi nó được import bởi một file khác.
    main()
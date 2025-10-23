# src/bug_generator/strategies/base_strategy.py
from abc import ABC, abstractmethod
from typing import Any, Dict
import xml.etree.ElementTree as ET

class BaseBugStrategy(ABC):
    """
    Lớp cơ sở trừu tượng (Interface) cho tất cả các chiến lược tạo lỗi.
    Mỗi lớp con kế thừa từ đây phải hiện thực hóa phương thức apply().
    """

    @abstractmethod
    def apply(self, data: Any, config: Dict) -> Any:
        """
        Áp dụng logic tạo lỗi vào dữ liệu đầu vào (XML string hoặc list actions).

        Args:
            data: Dữ liệu đầu vào (thường là chuỗi XML của Blockly).
            config: Cấu hình chi tiết cho việc tạo lỗi.
        """
        pass

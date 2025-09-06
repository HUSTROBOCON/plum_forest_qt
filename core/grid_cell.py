"""网格单元格模块"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush


class GridCell(QPushButton):
    """网格单元格类 - 扩展支持路径显示和外围区域"""
    
    def __init__(self, position, cell_type, is_clickable=True):
        super().__init__()
        self.position = position
        self.cell_type = cell_type
        self.is_clickable = is_clickable
        self.block_type = None
        self.is_path = False  # 是否为路径
        self.path_order = -1  # 路径顺序
        self.is_collected = False  # 是否被收集
        self.setFixedSize(120, 120)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet(self.get_style())
        if self.is_clickable:
            # 使用新的编号系统
            from utils.constants import POSITION_NUMBERS
            display_number = POSITION_NUMBERS.get(self.position, self.position + 1)
            self.setText(str(display_number))
        else:
            # 外围区域也显示编号
            from utils.constants import POSITION_NUMBERS
            display_number = POSITION_NUMBERS.get(self.position, "")
            self.setText(str(display_number) if display_number else "")
        self.setFont(QFont("Arial", 16, QFont.Bold))
        
    def get_style(self):
        """获取样式"""
        base_style = """
            QPushButton {
                border: 2px solid #333;
                font-weight: bold;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                border: 3px solid #007acc;
            }
        """
        
        if self.cell_type == 'medium':
            return base_style + "QPushButton { background-color: #2A7138; }"
        elif self.cell_type == 'low':
            return base_style + "QPushButton { background-color: #295210; }"
        elif self.cell_type == 'high':
            return base_style + "QPushButton { background-color: #98A650; }"
        elif self.cell_type == 'outer':
            return base_style + "QPushButton { background-color: #87CEEB; }"  # 淡蓝色
        else:
            return base_style + "QPushButton { background-color: #2A7138; }"
    
    def set_path(self, is_path, order=-1):
        """设置路径状态"""
        self.is_path = is_path
        self.path_order = order
        self.update()
    
    def set_collected(self, is_collected):
        """设置收集状态"""
        self.is_collected = is_collected
        self.update()
    
    def set_block(self, block_type):
        """设置方块类型"""
        self.block_type = block_type
        self.is_collected = False
        if block_type:
            # 使用新的编号系统
            from utils.constants import POSITION_NUMBERS
            display_number = POSITION_NUMBERS.get(self.position, self.position + 1)
            self.setText(str(display_number))
        else:
            # 恢复原始显示
            if self.is_clickable:
                from utils.constants import POSITION_NUMBERS
                display_number = POSITION_NUMBERS.get(self.position, self.position + 1)
                self.setText(str(display_number))
            else:
                from utils.constants import POSITION_NUMBERS
                display_number = POSITION_NUMBERS.get(self.position, "")
                self.setText(str(display_number) if display_number else "")
        
        self.setStyleSheet(self.get_style() + "QPushButton { color: black; }")
        self.update()
    
    def clear_block(self):
        """清除方块"""
        self.set_block(None)
        self.is_collected = False
    
    def paintEvent(self, event):
        """重写绘制事件，绘制方块和路径"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制高度标识（在右上角，仅对绿色区域）
        if self.cell_type in ['low', 'medium', 'high']:
            height_text = ""
            if self.cell_type == 'low':
                height_text = "L(200)"
            elif self.cell_type == 'medium':
                height_text = "M(400)"
            elif self.cell_type == 'high':
                height_text = "H(600)"
            
            if height_text:
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(self.rect().adjusted(0, 5, -5, 0), Qt.AlignRight | Qt.AlignTop, height_text)
        
        # 绘制路径（如果有）
        if self.is_path:
            painter.setBrush(QBrush(QColor(255, 255, 0, 150)))  # 半透明黄色
            painter.setPen(QPen(QColor(255, 165, 0), 3))  # 橙色边框
            painter.drawRect(self.rect())
            
            # 绘制路径顺序
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, str(self.path_order + 1))
        
        # 绘制方块（如果有）
        if self.block_type:
            if self.block_type == 'R1':
                color = QColor(255, 0, 0)
            elif self.block_type == 'R2':
                if self.is_collected:
                    color = QColor(100, 100, 255)  # 被收集的R2方块变浅蓝色
                else:
                    color = QColor(0, 0, 255)
            elif self.block_type == 'F':
                color = QColor(128, 0, 128)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            
            button_rect = self.rect()
            square_size = 40
            x = (button_rect.width() - square_size) // 2
            y = (button_rect.height() - square_size) // 2 + 10
            
            painter.drawRect(x, y, square_size, square_size)
            
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            
            text = self.block_type
            if self.block_type == 'R2' and self.is_collected:
                text = "✓"  # 显示收集标记
            
            text_rect = painter.fontMetrics().boundingRect(text)
            text_x = x + (square_size - text_rect.width()) // 2
            text_y = y + (square_size + text_rect.height()) // 2 - 2
            
            painter.drawText(text_x, text_y, text)
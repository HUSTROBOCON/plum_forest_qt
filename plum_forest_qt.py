import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QCheckBox, 
                             QLabel, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush

class GridCell(QPushButton):
    """网格单元格类"""
    def __init__(self, position, cell_type):
        super().__init__()
        self.position = position  # 0-11的位置编号
        self.cell_type = cell_type  # 'entrance', 'exit', 'corridor', 'normal'
        self.block_type = None  # 'R1', 'R2', 'F', None
        self.setFixedSize(120, 120)  # 进一步增大单元格尺寸
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet(self.get_style())
        self.setText(str(self.position + 1))  # 显示位置编号
        self.setFont(QFont("Arial", 16, QFont.Bold))  # 进一步增大字体
        
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
        
        if self.cell_type == 'entrance':
            return base_style + "QPushButton { background-color: #2A7138; }"  # 42-113-56
        elif self.cell_type == 'exit':
            return base_style + "QPushButton { background-color: #295210; }"  # 41-82-16
        elif self.cell_type == 'corridor':
            return base_style + "QPushButton { background-color: #98A650; }"  # 152-166-80
        else:
            return base_style + "QPushButton { background-color: #2A7138; }"  # 42-113-56
    
    def set_block(self, block_type):
        """设置方块类型"""
        self.block_type = block_type
        if block_type:
            # 只显示位置编号，方块通过paintEvent绘制
            self.setText(str(self.position + 1))
        else:
            self.setText(str(self.position + 1))
        
        # 更新样式
        self.setStyleSheet(self.get_style() + "QPushButton { color: black; }")
        self.update()  # 触发重绘
    
    def clear_block(self):
        """清除方块"""
        self.set_block(None)
    
    def paintEvent(self, event):
        """重写绘制事件，绘制方块"""
        super().paintEvent(event)
        
        if self.block_type:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 设置方块颜色
            if self.block_type == 'R1':
                color = QColor(255, 0, 0)  # 红色
            elif self.block_type == 'R2':
                color = QColor(0, 0, 255)  # 蓝色
            elif self.block_type == 'F':
                color = QColor(128, 0, 128)  # 紫色
            
            # 绘制方块
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))  # 黑色边框
            
            # 计算方块位置（在按钮中央）
            button_rect = self.rect()
            square_size = 40  # 方块大小
            x = (button_rect.width() - square_size) // 2
            y = (button_rect.height() - square_size) // 2 + 10  # 稍微向下偏移，避免与文字重叠
            
            painter.drawRect(x, y, square_size, square_size)
            
            # 在方块上绘制文字
            painter.setPen(QPen(QColor(255, 255, 255), 1))  # 白色文字
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            
            # 计算文字位置（方块中央）
            text_rect = painter.fontMetrics().boundingRect(self.block_type)
            text_x = x + (square_size - text_rect.width()) // 2
            text_y = y + (square_size + text_rect.height()) // 2 - 2
            
            painter.drawText(text_x, text_y, self.block_type)

class PlumForestQT(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_constraints()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("梅花林布局优化 - 交互式QT程序")
        self.setGeometry(50, 50, 1200, 900)  # 增加窗口高度以容纳新区域
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(30)  # 增加间距
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 右侧网格区域
        grid_widget = self.create_grid_widget()
        main_layout.addWidget(grid_widget)
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setFixedWidth(280)  # 进一步增大控制面板宽度
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("控制面板")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 方块类型选择
        layout.addWidget(QLabel("选择方块类型:"))
        
        self.r1_checkbox = QCheckBox("R1 (最多3个)")
        self.r2_checkbox = QCheckBox("R2 (最多4个)")
        self.fake_checkbox = QCheckBox("Fake (最多1个)")
        
        # 设置字体大小
        font = QFont("Arial", 14)
        self.r1_checkbox.setFont(font)
        self.r2_checkbox.setFont(font)
        self.fake_checkbox.setFont(font)
        
        # 连接信号 - 修复bug：使用stateChanged而不是clicked
        self.r1_checkbox.stateChanged.connect(self.on_r1_changed)
        self.r2_checkbox.stateChanged.connect(self.on_r2_changed)
        self.fake_checkbox.stateChanged.connect(self.on_fake_changed)
        
        layout.addWidget(self.r1_checkbox)
        layout.addWidget(self.r2_checkbox)
        layout.addWidget(self.fake_checkbox)
        
        # 分隔线
        layout.addWidget(QLabel("─" * 30))
        
        # 功能按钮
        random_btn = QPushButton("随机放置")
        random_btn.setFont(QFont("Arial", 14))
        random_btn.setFixedHeight(50)
        random_btn.clicked.connect(self.random_placement)
        layout.addWidget(random_btn)
        
        clear_btn = QPushButton("一键清除")
        clear_btn.setFont(QFont("Arial", 14))
        clear_btn.setFixedHeight(50)
        clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(clear_btn)
        
        # 分隔线
        layout.addWidget(QLabel("─" * 30))
        
        # 状态显示
        self.status_label = QLabel("状态: 准备就绪")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)
        
        # 计数显示
        self.count_label = QLabel("R1: 0/3, R2: 0/4, F: 0/1")
        self.count_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.count_label)
        
        # 约束说明
        constraints_text = """
约束条件:
• R1只能放在外围，不能放在走廊中间
• R2至少1个在入口
• F不能放在入口位置（1/2/3）
• 点击已放置的方块可清除
        """
        constraints_label = QLabel(constraints_text)
        constraints_label.setFont(QFont("Arial", 11))
        constraints_label.setWordWrap(True)
        layout.addWidget(constraints_label)
        
        layout.addStretch()
        return panel
    
    def create_grid_widget(self):
        """创建网格widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("梅花林布局软件")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建完整的大矩形容器
        main_container = QFrame()
        main_container.setFrameStyle(QFrame.StyledPanel)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #333;
            }
        """)
        
        # 主容器布局
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 一区 - 上方白色区域
        area1_label = QLabel("一区")
        area1_label.setAlignment(Qt.AlignCenter)
        area1_label.setFont(QFont("Arial", 18, QFont.Bold))
        area1_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: none;
                color: black;
                border-bottom: 1px solid #ccc;
            }
        """)
        area1_label.setFixedHeight(80)  # 高度为2 * 120
        main_layout.addWidget(area1_label)
        
        # 二区 - 中间的3×4网格
        area2_container = QFrame()
        area2_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-bottom: 1px solid #ccc;
            }
        """)
        area2_layout = QVBoxLayout(area2_container)
        area2_layout.setSpacing(0)
        area2_layout.setContentsMargins(0, 0, 0, 0)
        
        # 二区标题
        # area2_title = QLabel("二区")
        # area2_title.setFont(QFont("Arial", 16, QFont.Bold))
        # area2_title.setAlignment(Qt.AlignCenter)
        # area2_title.setStyleSheet("""
        #     QLabel {
        #         background-color: #f0f0f0;
        #         border: none;
        #         border-bottom: 1px solid #ccc;
        #         padding: 5px;
        #     }
        # """)
        # area2_layout.addWidget(area2_title)
        
        # 网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)  # 移除网格间距，让单元格紧贴
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建网格单元格
        self.cells = []
        for i in range(4):  # 4行
            row = []
            for j in range(3):  # 3列
                position = i * 3 + j
                
                # 根据位置确定单元格类型和颜色
                if position in [1, 3, 9, 11]:  # 位置2,4,10,12 (0-based: 1,3,9,11)
                    cell_type = 'exit'  # 使用深绿色 #295210 (41-82-16)
                elif position in [5, 7]:  # 位置6,8 (0-based: 5,7)
                    cell_type = 'corridor'  # 使用黄绿色 #98A650 (152-166-80)
                else:  # 位置1,3,5,7,9,11 (0-based: 0,2,4,6,8,10)
                    cell_type = 'entrance'  # 使用绿色 #2A7138 (42-113-56)
                
                cell = GridCell(position, cell_type)
                cell.clicked.connect(lambda checked, pos=position: self.on_cell_clicked(pos))
                row.append(cell)
                grid_layout.addWidget(cell, i, j)
            
            self.cells.append(row)
        
        area2_layout.addLayout(grid_layout)
        main_layout.addWidget(area2_container)
        
        # 三区 - 下方白色区域
        area3_label = QLabel("三区")
        area3_label.setAlignment(Qt.AlignCenter)
        area3_label.setFont(QFont("Arial", 18, QFont.Bold))
        area3_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: none;
                color: black;
            }
        """)
        area3_label.setFixedHeight(80)  # 高度为2.7 * 120
        main_layout.addWidget(area3_label)
        
        layout.addWidget(main_container, alignment=Qt.AlignCenter)
        layout.addStretch()
        return widget
    
    def setup_constraints(self):
        """设置约束条件"""
        self.current_selection = None
        self.block_counts = {'R1': 0, 'R2': 0, 'F': 0}
        
        # 定义外围位置（不包括走廊和位置12）
        self.outer_positions = [0, 1, 2, 3, 5, 6, 8, 9, 10, 11]  # 位置1-11，排除走廊4,7,10
        self.entrance_positions = [0, 1, 2]  # 位置1,2,3
        self.corridor_positions = [4, 7, 10]  # 位置5,8,11（注意：这里用的是0-based索引）
        self.forbidden_f_positions = [0, 1, 2]  # F不能放在位置1,2,3 (0-based: 0,1,2)
        self.forbidden_r1_positions = [11]  # R1不能放在位置12 (0-based: 11)
    
    def on_r1_changed(self, state):
        """R1复选框状态改变"""
        if state == Qt.Checked:
            self.r2_checkbox.setChecked(False)
            self.fake_checkbox.setChecked(False)
            self.current_selection = 'R1'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_r2_changed(self, state):
        """R2复选框状态改变"""
        if state == Qt.Checked:
            self.r1_checkbox.setChecked(False)
            self.fake_checkbox.setChecked(False)
            self.current_selection = 'R2'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_fake_changed(self, state):
        """Fake复选框状态改变"""
        if state == Qt.Checked:
            self.r1_checkbox.setChecked(False)
            self.r2_checkbox.setChecked(False)
            self.current_selection = 'F'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_cell_clicked(self, position):
        """单元格被点击"""
        row, col = position // 3, position % 3
        cell = self.cells[row][col]
        
        # 如果已经有方块，清除它
        if cell.block_type:
            self.remove_block(position)
            return
        
        # 如果没有选择方块类型，提示用户
        if self.current_selection is None:
            QMessageBox.warning(self, "警告", "请先选择要放置的方块类型！")
            return
        
        # 检查约束条件
        if not self.check_constraints(position, self.current_selection):
            return
        
        # 放置新方块
        self.place_block(position, self.current_selection)
        
        # 保持当前选择，不自动取消
        self.update_status()
    
    def check_constraints(self, position, block_type):
        """检查约束条件"""
        # 检查数量限制
        if block_type == 'R1' and self.block_counts['R1'] >= 3:
            QMessageBox.warning(self, "约束违反", "R1方块最多只能放置3个！")
            return False
        elif block_type == 'R2' and self.block_counts['R2'] >= 4:
            QMessageBox.warning(self, "约束违反", "R2方块最多只能放置4个！")
            return False
        elif block_type == 'F' and self.block_counts['F'] >= 1:
            QMessageBox.warning(self, "约束违反", "Fake方块最多只能放置1个！")
            return False
        
        # 检查R1只能放在外围
        if block_type == 'R1' and position not in self.outer_positions:
            QMessageBox.warning(self, "约束违反", "R1方块只能放在外围位置，不能放在走廊中间！")
            return False
        
        # 检查F不能放在位置1、2、3
        if block_type == 'F' and position in self.forbidden_f_positions:
            QMessageBox.warning(self, "约束违反", "F不能放在入口位置（1/2/3）！")
            return False
        
        return True
    
    def place_block(self, position, block_type):
        """放置方块"""
        row, col = position // 3, position % 3
        cell = self.cells[row][col]
        cell.set_block(block_type)
        self.block_counts[block_type] += 1
        self.update_count_display()
    
    def remove_block(self, position):
        """移除方块"""
        row, col = position // 3, position % 3
        cell = self.cells[row][col]
        if cell.block_type:
            self.block_counts[cell.block_type] -= 1
            cell.clear_block()
            self.update_count_display()
    
    def clear_all(self):
        """清除所有方块"""
        for row in self.cells:
            for cell in row:
                cell.clear_block()
        
        self.block_counts = {'R1': 0, 'R2': 0, 'F': 0}
        self.update_count_display()
        self.update_status()
        # 移除弹窗提示
    
    def random_placement(self):
        """随机放置方块"""
        # 先清除所有方块
        self.clear_all()
        
        # 生成随机布局
        positions = list(range(12))
        
        # 优先处理：至少1个R2在入口位置（1/2/3）
        entrance_available = [pos for pos in self.entrance_positions if pos in positions]
        if entrance_available:
            # 至少放1个R2在入口
            entrance_r2 = random.choice(entrance_available)
            self.place_block(entrance_r2, 'R2')
            positions.remove(entrance_r2)
        
        # 随机选择F位置（1个，不能放在位置1、2、3）
        available_f_positions = [pos for pos in positions if pos not in self.forbidden_f_positions]
        if available_f_positions:
            f_position = random.choice(available_f_positions)
            self.place_block(f_position, 'F')
            positions.remove(f_position)
        
        # 随机选择R1位置（外围，最多3个，不包括位置12）
        # 从剩余位置中选择外围位置
        available_r1_positions = [pos for pos in positions if pos in self.outer_positions]
        if len(available_r1_positions) >= 3:
            r1_positions = random.sample(available_r1_positions, 3)
        else:
            r1_positions = available_r1_positions  # 如果不够3个，就全选
        
        for pos in r1_positions:
            self.place_block(pos, 'R1')
            positions.remove(pos)
        
        # 剩余位置全部放R2（确保总共4个R2）
        remaining_r2_count = 4 - 1  # 已经放了1个R2在入口
        if len(positions) >= remaining_r2_count:
            remaining_r2_positions = random.sample(positions, remaining_r2_count)
        else:
            remaining_r2_positions = positions  # 如果不够，就全选
        
        for pos in remaining_r2_positions:
            self.place_block(pos, 'R2')
        
        self.update_status()
        # QMessageBox.information(self, "随机放置完成", "已按照约束条件随机放置所有方块！")
    
    def update_count_display(self):
        """更新计数显示"""
        count_text = f"R1: {self.block_counts['R1']}/3, R2: {self.block_counts['R2']}/4, F: {self.block_counts['F']}/1"
        self.count_label.setText(count_text)
    
    def update_status(self):
        """更新状态显示"""
        if self.current_selection:
            self.status_label.setText(f"状态: 已选择 {self.current_selection} (可连续放置)")
        else:
            self.status_label.setText("状态: 准备就绪")

def main():
    app = QApplication(sys.argv)
    window = PlumForestQT()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
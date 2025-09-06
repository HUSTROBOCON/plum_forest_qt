"""控制面板模块"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton,
                             QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.constants import (
    DEFAULT_COST_UP_200, DEFAULT_COST_DOWN_200, DEFAULT_COST_UP_400,
    DEFAULT_COST_DOWN_400, DEFAULT_PICKUP_COST, DEFAULT_REQUIRED_R2_COUNT,
    DEFAULT_OUTER_ZONE_MOVE_COST
)


class ControlPanel(QScrollArea):
    """控制面板类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFixedWidth(450)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 创建面板
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("控制面板")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 方块类型选择
        self.setup_block_selection(layout)
        
        # 路径规划控制
        self.setup_path_controls(layout)
        
        # 功能按钮
        self.setup_function_buttons(layout)
        
        # 状态信息组
        self.setup_status_info(layout)
        
        # 路径信息显示
        self.setup_path_info(layout)
        
        # 约束说明
        self.setup_constraints_info(layout)
        
        # 设置滚动区域
        self.setWidget(panel)
    
    def setup_block_selection(self, layout):
        """设置方块类型选择"""
        block_group = QFrame()
        block_group.setFrameStyle(QFrame.Box)
        block_layout = QVBoxLayout(block_group)
        block_layout.setSpacing(5)
        
        block_layout.addWidget(QLabel("选择方块类型:"))
        
        self.r1_checkbox = QCheckBox("R1 (最多3个)")
        self.r2_checkbox = QCheckBox("R2 (最多4个)")
        self.fake_checkbox = QCheckBox("Fake (最多1个)")
        
        font = QFont("Arial", 12)
        self.r1_checkbox.setFont(font)
        self.r2_checkbox.setFont(font)
        self.fake_checkbox.setFont(font)
        
        block_layout.addWidget(self.r1_checkbox)
        block_layout.addWidget(self.r2_checkbox)
        block_layout.addWidget(self.fake_checkbox)
        
        layout.addWidget(block_group)
    
    def setup_path_controls(self, layout):
        """设置路径规划控制"""
        path_group = QFrame()
        path_group.setFrameStyle(QFrame.Box)
        path_layout = QVBoxLayout(path_group)
        path_layout.setSpacing(5)
        
        path_layout.addWidget(QLabel("路径规划设置:"))

        # R2构型
        r2_cfg_row = QHBoxLayout()
        r2_cfg_row.addWidget(QLabel("R2构型:"))
        self.r2_config_combo = QComboBox()
        self.r2_config_combo.addItems(["仅200台阶", "200与400台阶"])
        self.r2_config_combo.setCurrentIndex(1)  # 默认允许400，与当前一致
        self.r2_config_combo.setFont(QFont("Arial", 11))
        r2_cfg_row.addWidget(self.r2_config_combo)
        path_layout.addLayout(r2_cfg_row)
        
        # 移动代价设置
        self.setup_cost_controls(path_layout)
        
        # R2收集任务设置
        self.setup_task_controls(path_layout)
        
        # 高度说明
        height_info = QLabel("高度: 入口/出口=0, L=200, M=400, H=600")
        height_info.setFont(QFont("Arial", 9))
        height_info.setWordWrap(True)
        path_layout.addWidget(height_info)
        
        # 算法选择
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Dijkstra算法"])
        self.algorithm_combo.setFont(QFont("Arial", 11))
        path_layout.addWidget(self.algorithm_combo)
        
        # 路径规划按钮
        self.setup_path_buttons(path_layout)
        
        layout.addWidget(path_group)
    
    def setup_cost_controls(self, path_layout):
        """设置代价控制"""
        cost_grid = QGridLayout()
        cost_grid.setSpacing(3)
        
        # 标题
        cost_grid.addWidget(QLabel("高度变化"), 0, 0)
        cost_grid.addWidget(QLabel("上升"), 0, 1)
        cost_grid.addWidget(QLabel("下降"), 0, 2)
        
        # +200/-200高度的代价
        cost_grid.addWidget(QLabel("200:"), 1, 0)
        
        self.cost_up_200_spinbox = QSpinBox()
        self.cost_up_200_spinbox.setMinimum(0)
        self.cost_up_200_spinbox.setMaximum(100)
        self.cost_up_200_spinbox.setValue(DEFAULT_COST_UP_200)
        self.cost_up_200_spinbox.setFixedWidth(60)
        cost_grid.addWidget(self.cost_up_200_spinbox, 1, 1)
        
        self.cost_down_200_spinbox = QSpinBox()
        self.cost_down_200_spinbox.setMinimum(0)
        self.cost_down_200_spinbox.setMaximum(100)
        self.cost_down_200_spinbox.setValue(DEFAULT_COST_DOWN_200)
        self.cost_down_200_spinbox.setFixedWidth(60)
        cost_grid.addWidget(self.cost_down_200_spinbox, 1, 2)
        
        # +400/-400高度的代价
        cost_grid.addWidget(QLabel("400:"), 2, 0)
        
        self.cost_up_400_spinbox = QSpinBox()
        self.cost_up_400_spinbox.setMinimum(0)
        self.cost_up_400_spinbox.setMaximum(100)
        self.cost_up_400_spinbox.setValue(DEFAULT_COST_UP_400)
        self.cost_up_400_spinbox.setFixedWidth(60)
        cost_grid.addWidget(self.cost_up_400_spinbox, 2, 1)
        
        self.cost_down_400_spinbox = QSpinBox()
        self.cost_down_400_spinbox.setMinimum(0)
        self.cost_down_400_spinbox.setMaximum(100)
        self.cost_down_400_spinbox.setValue(DEFAULT_COST_DOWN_400)
        self.cost_down_400_spinbox.setFixedWidth(60)
        cost_grid.addWidget(self.cost_down_400_spinbox, 2, 2)
        
        # 外围区域移动代价
        cost_grid.addWidget(QLabel("R2外围移动代价:"), 3, 0)
        
        self.outer_zone_cost_spinbox = QSpinBox()
        self.outer_zone_cost_spinbox.setMinimum(0)
        self.outer_zone_cost_spinbox.setMaximum(100)
        self.outer_zone_cost_spinbox.setValue(DEFAULT_OUTER_ZONE_MOVE_COST)
        self.outer_zone_cost_spinbox.setFixedWidth(60)
        cost_grid.addWidget(self.outer_zone_cost_spinbox, 3, 1)
        
        cost_grid.addWidget(QLabel("移动"), 3, 2)
        
        path_layout.addLayout(cost_grid)
    
    def setup_task_controls(self, path_layout):
        """设置任务控制"""
        task_grid = QGridLayout()
        task_grid.setSpacing(3)
        
        task_grid.addWidget(QLabel("拾取代价:"), 0, 0)
        self.pickup_cost_spinbox = QSpinBox()
        self.pickup_cost_spinbox.setMinimum(0)
        self.pickup_cost_spinbox.setMaximum(100)
        self.pickup_cost_spinbox.setValue(DEFAULT_PICKUP_COST)
        self.pickup_cost_spinbox.setFixedWidth(60)
        task_grid.addWidget(self.pickup_cost_spinbox, 0, 1)
        
        task_grid.addWidget(QLabel("必须收集:"), 1, 0)
        self.required_r2_spinbox = QSpinBox()
        self.required_r2_spinbox.setMinimum(2)
        self.required_r2_spinbox.setMaximum(4)
        self.required_r2_spinbox.setValue(DEFAULT_REQUIRED_R2_COUNT)
        self.required_r2_spinbox.setFixedWidth(60)
        task_grid.addWidget(self.required_r2_spinbox, 1, 1)
        
        task_grid.addWidget(QLabel("个R2块"), 1, 2)
        
        path_layout.addLayout(task_grid)
    
    def setup_path_buttons(self, path_layout):
        """设置路径按钮"""
        button_layout = QHBoxLayout()
        
        self.plan_btn = QPushButton("计算路径")
        self.plan_btn.setFont(QFont("Arial", 12))
        self.plan_btn.setFixedHeight(35)
        button_layout.addWidget(self.plan_btn)
        
        self.clear_path_btn = QPushButton("清除路径")
        self.clear_path_btn.setFont(QFont("Arial", 12))
        self.clear_path_btn.setFixedHeight(35)
        button_layout.addWidget(self.clear_path_btn)
        
        # 添加视频生成按钮
        self.generate_video_btn = QPushButton("生成视频")
        self.generate_video_btn.setFont(QFont("Arial", 12))
        self.generate_video_btn.setFixedHeight(35)
        self.generate_video_btn.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.generate_video_btn)
        
        path_layout.addLayout(button_layout)
    
    def setup_function_buttons(self, layout):
        """设置功能按钮"""
        func_layout = QHBoxLayout()
        
        self.random_btn = QPushButton("随机放置")
        self.random_btn.setFont(QFont("Arial", 12))
        self.random_btn.setFixedHeight(35)
        func_layout.addWidget(self.random_btn)
        
        self.clear_btn = QPushButton("一键清除")
        self.clear_btn.setFont(QFont("Arial", 12))
        self.clear_btn.setFixedHeight(35)
        func_layout.addWidget(self.clear_btn)
        
        layout.addLayout(func_layout)
    
    def setup_status_info(self, layout):
        """设置状态信息"""
        status_group = QFrame()
        status_group.setFrameStyle(QFrame.Box)
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(3)
        
        # 状态显示
        self.status_label = QLabel("状态: 准备就绪")
        self.status_label.setFont(QFont("Arial", 11))
        status_layout.addWidget(self.status_label)
        
        # 计数显示
        self.count_label = QLabel("R1: 0/3, R2: 0/4, F: 0/1")
        self.count_label.setFont(QFont("Arial", 11))
        status_layout.addWidget(self.count_label)
        
        layout.addWidget(status_group)
    
    def setup_path_info(self, layout):
        """设置路径信息"""
        path_info_group = QFrame()
        path_info_group.setFrameStyle(QFrame.Box)
        path_info_layout = QVBoxLayout(path_info_group)
        path_info_layout.setSpacing(3)
        
        path_info_layout.addWidget(QLabel("路径信息:"))
        
        self.path_info_text = QTextEdit()
        self.path_info_text.setReadOnly(True)
        self.path_info_text.setFont(QFont("Consolas", 9))
        self.path_info_text.setMinimumHeight(200)
        self.path_info_text.setMaximumHeight(300)
        self.path_info_text.setText("路径信息: 未计算")
        
        path_info_layout.addWidget(self.path_info_text)
        
        layout.addWidget(path_info_group)
    
    def setup_constraints_info(self, layout):
        """设置约束说明"""
        constraints_group = QFrame()
        constraints_group.setFrameStyle(QFrame.Box)
        constraints_layout = QVBoxLayout(constraints_group)
        
        constraints_text = """约束条件:
• R1只能放在外围
• R2至少1个在入口
• F不能放在入口位置
• R2机器人必须收集指定数量R2块
• 只能收集前后左右相邻的R2块
• 对于收集R2块数量为2的情况在R2取2个块走的策略中，如果R2被R2块堵住了路，那么它可以多取一个块来开路"""
        
        constraints_label = QLabel(constraints_text)
        constraints_label.setFont(QFont("Arial", 9))
        constraints_label.setWordWrap(True)
        constraints_layout.addWidget(constraints_label)
        
        layout.addWidget(constraints_group)
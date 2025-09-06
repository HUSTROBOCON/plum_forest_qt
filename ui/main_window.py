"""主窗口模块"""

import random
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.path_planner import PathPlanner
from core.grid_cell import GridCell
from ui.control_panel import ControlPanel
from utils.constants import (
    EXTENDED_GRID_WIDTH, EXTENDED_GRID_HEIGHT, EXTENDED_GREEN_POSITIONS,
    ENTRY_ZONE_POSITIONS, EXIT_ZONE_POSITIONS, TRUE_START_POSITION,
    GREEN_AREA_START_ROW, GREEN_AREA_START_COL, ORIGINAL_GRID_WIDTH, ORIGINAL_GRID_HEIGHT, ORIGINAL_GRID_SIZE,
    LOW_POSITIONS, HIGH_POSITIONS, MEDIUM_POSITIONS, POSITION_NUMBERS,
    OUTER_POSITIONS, ENTRANCE_POSITIONS, FORBIDDEN_F_POSITIONS,
    MAX_R1_COUNT, MAX_R2_COUNT, MAX_F_COUNT
)
from core.video_generator import VideoGenerator
from PyQt5.QtWidgets import QFileDialog, QProgressDialog
from PyQt5.QtCore import QThread, pyqtSignal
import os

class VideoGenerationThread(QThread):
    """视频生成线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, video_generator, path_with_states, cells_data, output_path, fps, duration_per_step):
        super().__init__()
        self.video_generator = video_generator
        self.path_with_states = path_with_states
        self.cells_data = cells_data
        self.output_path = output_path
        self.fps = fps
        self.duration_per_step = duration_per_step
    
    def run(self):
        try:
            success = self.video_generator.generate_video(
                self.path_with_states, 
                self.cells_data, 
                self.output_path, 
                self.fps, 
                self.duration_per_step
            )
            self.finished.emit(success, self.output_path)
        except Exception as e:
            self.finished.emit(False, str(e))

class PlumForestQT(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.path_planner = PathPlanner(EXTENDED_GRID_WIDTH, EXTENDED_GRID_HEIGHT)
        self.video_generator = VideoGenerator(EXTENDED_GRID_WIDTH, EXTENDED_GRID_HEIGHT)
        self.current_path = None
        self.collected_r2_positions = set()
        self.init_ui()
        self.setup_constraints()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("梅花林布局优化 - R2收集任务版 (扩展外围区域)")
        self.setGeometry(50, 50, 1800, 1000)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # 左侧控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # 右侧网格区域
        grid_widget = self.create_grid_widget()
        main_layout.addWidget(grid_widget)
        
    def create_grid_widget(self):
        """创建网格widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        title = QLabel("梅花林布局软件 - R2收集任务版 (扩展外围区域)")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        main_container = QFrame()
        main_container.setFrameStyle(QFrame.StyledPanel)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #333;
            }
        """)
        
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
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
        area1_label.setFixedHeight(80)
        main_layout.addWidget(area1_label)
        
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
        
        # 创建5x6网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
        self.cells = []
        for i in range(EXTENDED_GRID_HEIGHT):
            row = []
            for j in range(EXTENDED_GRID_WIDTH):
                position = i * EXTENDED_GRID_WIDTH + j
                
                # 确定单元格类型
                if position in EXTENDED_GREEN_POSITIONS:
                    # 绿色区域
                    original_pos = self.get_original_position(position)
                    if original_pos in LOW_POSITIONS:
                        cell_type = 'low'
                    elif original_pos in HIGH_POSITIONS:
                        cell_type = 'high'
                    else:
                        cell_type = 'medium'
                    is_clickable = True
                elif position in ENTRY_ZONE_POSITIONS or position in EXIT_ZONE_POSITIONS:
                    # 可通行的外围区域
                    cell_type = 'outer'
                    is_clickable = False
                else:
                    # 不可通行的外围区域
                    cell_type = 'outer'
                    is_clickable = False
                
                cell = GridCell(position, cell_type, is_clickable)
                if is_clickable:
                    cell.clicked.connect(lambda checked, pos=position: self.on_cell_clicked(pos))
                row.append(cell)
                grid_layout.addWidget(cell, i, j)
            
            self.cells.append(row)
        
        area2_layout.addLayout(grid_layout)
        main_layout.addWidget(area2_container)
        
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
        area3_label.setFixedHeight(80)
        main_layout.addWidget(area3_label)
        
        layout.addWidget(main_container, alignment=Qt.AlignCenter)
        layout.addStretch()
        return widget
    
    def get_original_position(self, extended_position):
        """将扩展网格中的位置转换为原始位置"""
        row = extended_position // EXTENDED_GRID_WIDTH
        col = extended_position % EXTENDED_GRID_WIDTH
        
        # 检查是否在绿色区域内
        if (GREEN_AREA_START_ROW <= row < GREEN_AREA_START_ROW + ORIGINAL_GRID_HEIGHT and
            GREEN_AREA_START_COL <= col < GREEN_AREA_START_COL + ORIGINAL_GRID_WIDTH):
            relative_row = row - GREEN_AREA_START_ROW
            relative_col = col - GREEN_AREA_START_COL
            return relative_row * ORIGINAL_GRID_WIDTH + relative_col
        return -1  # 不在绿色区域内
    
    def get_extended_position(self, original_pos):
        """将原始位置转换为扩展网格中的位置"""
        row = original_pos // ORIGINAL_GRID_WIDTH
        col = original_pos % ORIGINAL_GRID_WIDTH
        extended_row = GREEN_AREA_START_ROW + row
        extended_col = GREEN_AREA_START_COL + col
        return extended_row * EXTENDED_GRID_WIDTH + extended_col
    
    def get_display_number(self, position):
        """获取位置的显示编号"""
        return POSITION_NUMBERS.get(position, position + 1)
    
    def setup_constraints(self):
        """设置约束条件"""
        self.current_selection = None
        self.block_counts = {'R1': 0, 'R2': 0, 'F': 0}
        
        # 基于原始位置的约束
        self.outer_positions = OUTER_POSITIONS
        self.entrance_positions = ENTRANCE_POSITIONS
        self.corridor_positions = [4, 7, 10]
        self.forbidden_f_positions = FORBIDDEN_F_POSITIONS
        self.forbidden_r1_positions = [11]
    
    def connect_signals(self):
        """连接信号"""
        # 方块类型选择
        self.control_panel.r1_checkbox.stateChanged.connect(self.on_r1_changed)
        self.control_panel.r2_checkbox.stateChanged.connect(self.on_r2_changed)
        self.control_panel.fake_checkbox.stateChanged.connect(self.on_fake_changed)
        
        # 按钮
        self.control_panel.plan_btn.clicked.connect(self.calculate_path)
        self.control_panel.clear_path_btn.clicked.connect(self.clear_path)
        self.control_panel.random_btn.clicked.connect(self.random_placement)
        self.control_panel.clear_btn.clicked.connect(self.clear_all)
        
        # 视频生成按钮
        self.control_panel.generate_video_btn.clicked.connect(self.generate_video)
    
    def calculate_path(self):
        """计算最优路径"""
        # 更新路径规划器的参数
        cost_up_200 = self.control_panel.cost_up_200_spinbox.value()
        cost_down_200 = self.control_panel.cost_down_200_spinbox.value()
        cost_up_400 = self.control_panel.cost_up_400_spinbox.value()
        cost_down_400 = self.control_panel.cost_down_400_spinbox.value()
        pickup_cost = self.control_panel.pickup_cost_spinbox.value()
        required_r2_count = self.control_panel.required_r2_spinbox.value()
        outer_zone_cost = self.control_panel.outer_zone_cost_spinbox.value()

        # R2构型
        r2_cfg_text = self.control_panel.r2_config_combo.currentText()
        allow_400 = (r2_cfg_text == "200与400台阶")
        self.path_planner.set_r2_config(allow_400)

        self.path_planner.set_costs(cost_up_200, cost_down_200, cost_up_400, cost_down_400, 
                                   pickup_cost, required_r2_count, outer_zone_cost)
        
        # 获取障碍物和R2方块位置（基于扩展网格）
        obstacles = set()
        r2_positions = set()
        
        for row in self.cells:
            for cell in row:
                if cell.block_type:
                    obstacles.add(cell.position)
                    if cell.block_type == 'R2':
                        r2_positions.add(cell.position)
        
        # 检查R2方块数量是否足够
        if len(r2_positions) < required_r2_count:
            QMessageBox.warning(self, "任务无法完成", 
                              f"场上只有{len(r2_positions)}个R2方块，无法收集{required_r2_count}个！")
            return
        
        # 定义起始和目标位置（基于扩展网格）
        # 起始位置：蓝色区域（位置14、15、16）
        start_positions = ENTRY_ZONE_POSITIONS
        # 目标位置：绿色区域的底部（位置10、11、12）
        end_positions = [self.get_extended_position(pos) for pos in [9, 10, 11]]
        
        # 执行路径规划
        path_with_states = self.path_planner.dijkstra_with_collection(
            start_positions, end_positions, obstacles, r2_positions)
        
        if path_with_states:
            self.current_path = path_with_states
            self.display_path_with_collection(path_with_states)
            
            # 启用视频生成按钮
            self.control_panel.generate_video_btn.setEnabled(True)
            
            
            # 计算路径总代价
            total_cost = self.path_planner.calculate_path_cost_with_collection(path_with_states)
            
            # 构建详细路径信息
            path_details = self.build_path_details(path_with_states)

            # 实际收集数量
            final_collected = path_with_states[-1][1]
            actual_collected_count = len(final_collected) if hasattr(final_collected, '__len__') else 0
            
            # 显示路径信息
            positions_only = [pos for pos, _ in path_with_states if pos not in [-1, self.path_planner.grid_size]]
            path_str = " → ".join([str(self.get_display_number(p)) for p in positions_only])
            
            path_info = f"""路径: {path_str}
总代价: {total_cost}
移动步数: {len(positions_only)}
收集R2块: {actual_collected_count}个 (目标≥{required_r2_count if required_r2_count==2 else required_r2_count})
R2构型: {'200与400台阶' if allow_400 else '仅200台阶'}
算法: Dijkstra算法
代价设置: ↑200={cost_up_200}, ↓200={cost_down_200}, ↑400={cost_up_400}, ↓400={cost_down_400}, 拾取={pickup_cost}, 外围={outer_zone_cost}

详细步骤:
{chr(10).join(path_details)}"""
            
            self.control_panel.path_info_text.setText(path_info)
            self.control_panel.status_label.setText(f"状态: 路径计算完成 (总代价: {total_cost})")
        else:
            # 禁用视频生成按钮
            self.control_panel.generate_video_btn.setEnabled(False)

            QMessageBox.warning(self, "路径规划", "无法找到满足收集任务的路径！")
            self.control_panel.path_info_text.setText("路径信息: 无可行路径")
            self.control_panel.status_label.setText("状态: 路径计算失败")
    
    def build_path_details(self, path_with_states):
        """构建详细的路径信息"""
        details = []

        for i in range(len(path_with_states) - 1):
            current_pos, current_collected = path_with_states[i]
            next_pos, next_collected = path_with_states[i + 1]

            # 收集
            if current_pos == next_pos and current_collected != next_collected:
                newly_collected = next_collected - current_collected
                collected_pos = list(newly_collected)[0]
                details.append(f"在位置{self.get_display_number(current_pos)}收集R2块{self.get_display_number(collected_pos)} [代价:{self.path_planner.pickup_cost}]")
                continue

            # 普通移动（包含从10/11/12到25/24/23的下到蓝区、以及蓝区到22的行走）
            if current_pos != next_pos:
                current_height = self.path_planner.position_heights.get(current_pos, 0)
                next_height = self.path_planner.position_heights.get(next_pos, 0)
                height_change = next_height - current_height
                cost = self.path_planner.get_edge_cost(current_pos, next_pos)
                arrow = "↑" if height_change > 0 else "↓" if height_change < 0 else "→"
                details.append(
                    f"{self.get_display_number(current_pos)}({current_height}) {arrow} "
                    f"{self.get_display_number(next_pos)}({next_height}) "
                    f"[{'+' if height_change > 0 else ''}{height_change}, 代价:{cost}]"
                )

        return details
    
    def generate_video(self):
        """生成路径规划视频"""
        if not self.current_path:
            QMessageBox.warning(self, "警告", "请先计算路径！")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存视频", "path_planning.mp4", "MP4视频文件 (*.mp4)"
        )
        
        if not output_path:
            return
        
        # 创建单元格数据
        cells_data = self.video_generator.create_cells_data_from_ui(self.cells)
        
        # 创建进度对话框
        progress = QProgressDialog("正在生成视频...", "取消", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # 创建并启动视频生成线程
        self.video_thread = VideoGenerationThread(
            self.video_generator,
            self.current_path,
            cells_data,
            output_path,
            fps=2,
            duration_per_step=1.0
        )
        
        self.video_thread.finished.connect(
            lambda success, message: self.on_video_generation_finished(success, message, progress)
        )
        self.video_thread.start()

    def on_video_generation_finished(self, success, message, progress):
        """视频生成完成回调"""
        progress.close()
        
        if success:
            QMessageBox.information(self, "成功", f"视频已保存到: {message}")
        else:
            QMessageBox.critical(self, "错误", f"视频生成失败: {message}")
    

    def display_path_with_collection(self, path_with_states):
        """显示带收集任务的路径"""
        # 清除之前的路径和收集状态
        self.clear_path_display()
        self.clear_collected_display()
        
        # 记录所有被收集的R2方块
        all_collected = set()
        if path_with_states:
            final_collected = path_with_states[-1][1]
            # 将frozenset转换为普通set
            all_collected = set(final_collected) if isinstance(final_collected, frozenset) else final_collected
        
        # 显示路径
        positions_only = []
        for pos, collected in path_with_states:
            if pos not in [-1, self.path_planner.grid_size]:
                positions_only.append(pos)
        
        for i, pos in enumerate(positions_only):
            row, col = pos // EXTENDED_GRID_WIDTH, pos % EXTENDED_GRID_WIDTH
            cell = self.cells[row][col]
            cell.set_path(True, i)
        
        # 显示收集的R2方块
        for pos in all_collected:
            row, col = pos // EXTENDED_GRID_WIDTH, pos % EXTENDED_GRID_WIDTH
            cell = self.cells[row][col]
            cell.set_collected(True)
        
        # 确保存储为普通set
        self.collected_r2_positions = set(all_collected)
    
    def clear_path_display(self):
        """清除路径显示"""
        for row in self.cells:
            for cell in row:
                cell.set_path(False)
    
    def clear_collected_display(self):
        """清除收集状态显示"""
        for row in self.cells:
            for cell in row:
                cell.set_collected(False)
        # 确保是普通set，才能调用clear()
        if hasattr(self.collected_r2_positions, 'clear'):
            self.collected_r2_positions.clear()
        else:
            self.collected_r2_positions = set()
    
    def clear_path(self):
        """清除路径"""
        self.clear_path_display()
        self.clear_collected_display()
        self.current_path = None
        self.control_panel.generate_video_btn.setEnabled(False)  # 禁用视频生成按钮
        self.control_panel.path_info_text.setText("路径信息: 未计算")
        self.control_panel.status_label.setText("状态: 路径已清除")
    
    def clear_all(self):
        """清除所有方块和路径"""
        for row in self.cells:
            for cell in row:
                cell.clear_block()
                cell.set_path(False)
        
        self.block_counts = {'R1': 0, 'R2': 0, 'F': 0}
        self.current_path = None
        self.control_panel.generate_video_btn.setEnabled(False)  # 禁用视频生成按钮
        # 确保重置为普通set
        self.collected_r2_positions = set()
        self.update_count_display()
        self.update_status()
        self.control_panel.path_info_text.setText("路径信息: 未计算")

    
    def on_r1_changed(self, state):
        if state == Qt.Checked:
            self.control_panel.r2_checkbox.setChecked(False)
            self.control_panel.fake_checkbox.setChecked(False)
            self.current_selection = 'R1'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_r2_changed(self, state):
        if state == Qt.Checked:
            self.control_panel.r1_checkbox.setChecked(False)
            self.control_panel.fake_checkbox.setChecked(False)
            self.current_selection = 'R2'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_fake_changed(self, state):
        if state == Qt.Checked:
            self.control_panel.r1_checkbox.setChecked(False)
            self.control_panel.r2_checkbox.setChecked(False)
            self.current_selection = 'F'
        else:
            self.current_selection = None
        self.update_status()
    
    def on_cell_clicked(self, position):
        row, col = position // EXTENDED_GRID_WIDTH, position % EXTENDED_GRID_WIDTH
        cell = self.cells[row][col]
        
        if cell.block_type:
            self.remove_block(position)
            return
        
        if self.current_selection is None:
            QMessageBox.warning(self, "警告", "请先选择要放置的方块类型！")
            return
        
        # 检查是否在绿色区域内
        original_pos = self.get_original_position(position)
        if original_pos == -1:
            QMessageBox.warning(self, "警告", "只能在外围区域放置方块！")
            return
        
        if not self.check_constraints(original_pos, self.current_selection):
            return
        
        self.place_block(position, self.current_selection)
        self.update_status()
    
    def check_constraints(self, original_position, block_type):
        if block_type == 'R1' and self.block_counts['R1'] >= MAX_R1_COUNT:
            QMessageBox.warning(self, "约束违反", "R1方块最多只能放置3个！")
            return False
        elif block_type == 'R2' and self.block_counts['R2'] >= MAX_R2_COUNT:
            QMessageBox.warning(self, "约束违反", "R2方块最多只能放置4个！")
            return False
        elif block_type == 'F' and self.block_counts['F'] >= MAX_F_COUNT:
            QMessageBox.warning(self, "约束违反", "Fake方块最多只能放置1个！")
            return False
        
        if block_type == 'R1' and original_position not in self.outer_positions:
            QMessageBox.warning(self, "约束违反", "R1方块只能放在外围位置，不能放在走廊中间！")
            return False
        
        if block_type == 'F' and original_position in self.forbidden_f_positions:
            QMessageBox.warning(self, "约束违反", "F不能放在入口位置（1/2/3）！")
            return False
        
        return True
    
    def place_block(self, position, block_type):
        row, col = position // EXTENDED_GRID_WIDTH, position % EXTENDED_GRID_WIDTH
        cell = self.cells[row][col]
        cell.set_block(block_type)
        self.block_counts[block_type] += 1
        self.update_count_display()
    
    def remove_block(self, position):
        row, col = position // EXTENDED_GRID_WIDTH, position % EXTENDED_GRID_WIDTH
        cell = self.cells[row][col]
        if cell.block_type:
            self.block_counts[cell.block_type] -= 1
            cell.clear_block()
            self.update_count_display()
    
    def random_placement(self):
        self.clear_all()
        
        # 获取所有绿色区域位置
        green_positions = [self.get_extended_position(pos) for pos in range(ORIGINAL_GRID_SIZE)]
        
        entrance_available = [self.get_extended_position(pos) for pos in self.entrance_positions]
        if entrance_available:
            entrance_r2 = random.choice(entrance_available)
            self.place_block(entrance_r2, 'R2')
            green_positions.remove(entrance_r2)
        
        available_f_positions = [pos for pos in green_positions 
                               if self.get_original_position(pos) not in self.forbidden_f_positions]
        if available_f_positions:
            f_position = random.choice(available_f_positions)
            self.place_block(f_position, 'F')
            green_positions.remove(f_position)
        
        available_r1_positions = [pos for pos in green_positions 
                                if self.get_original_position(pos) in self.outer_positions]
        if len(available_r1_positions) >= MAX_R1_COUNT:
            r1_positions = random.sample(available_r1_positions, MAX_R1_COUNT)
        else:
            r1_positions = available_r1_positions
        
        for pos in r1_positions:
            self.place_block(pos, 'R1')
            green_positions.remove(pos)
        
        remaining_r2_count = MAX_R2_COUNT - 1
        if len(green_positions) >= remaining_r2_count:
            remaining_r2_positions = random.sample(green_positions, remaining_r2_count)
        else:
            remaining_r2_positions = green_positions
        
        for pos in remaining_r2_positions:
            self.place_block(pos, 'R2')
        
        self.update_status()
    
    def update_count_display(self):
        count_text = f"R1: {self.block_counts['R1']}/{MAX_R1_COUNT}, R2: {self.block_counts['R2']}/{MAX_R2_COUNT}, F: {self.block_counts['F']}/{MAX_F_COUNT}"
        self.control_panel.count_label.setText(count_text)
    
    def update_status(self):
        if self.current_selection:
            self.control_panel.status_label.setText(f"状态: 已选择 {self.current_selection} (可连续放置)")
        else:
            self.control_panel.status_label.setText("状态: 准备就绪")
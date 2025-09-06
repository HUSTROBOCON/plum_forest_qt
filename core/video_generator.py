"""视频生成模块"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QPixmap
from utils.constants import (
    EXTENDED_GRID_WIDTH, EXTENDED_GRID_HEIGHT, POSITION_NUMBERS, 
    POSITION_HEIGHTS, EXTENDED_GREEN_POSITIONS, ALL_OUTER_POSITIONS
)


class VideoGenerator:
    """路径规划视频生成器"""
    
    def __init__(self, grid_width=EXTENDED_GRID_WIDTH, grid_height=EXTENDED_GRID_HEIGHT):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = 120
        self.margin = 50
        self.video_width = self.grid_width * self.cell_size + 2 * self.margin
        self.video_height = self.grid_height * self.cell_size + 2 * self.margin + 100  # 额外空间用于信息显示
        
        # 颜色定义
        self.colors = {
            'background': (255, 255, 255),
            'grid_line': (100, 100, 100),
            'low_area': (41, 82, 16),      # 深绿色
            'medium_area': (42, 113, 56),    # 绿色
            'high_area': (152, 166, 80),     # 浅绿色
            'outer_area': (135, 206, 235),   # 淡蓝色
            'path': (255, 255, 0, 150),      # 黄色路径
            'path_border': (255, 165, 0),    # 橙色边框
            'current_pos': (255, 0, 0),      # 红色当前位置
            'r1_block': (255, 0, 0),         # 红色R1
            'r2_block': (0, 0, 255),         # 蓝色R2
            'r2_collected': (100, 100, 255), # 浅蓝色已收集R2
            'f_block': (128, 0, 128),        # 紫色F
            'text': (0, 0, 0),               # 黑色文字
            'info_bg': (240, 240, 240)       # 信息背景
        }
    
    def create_frame(self, cells_data, current_pos=None, collected_r2=None, step_info=""):
        """创建单帧图像"""
        # 创建画布
        img = Image.new('RGB', (self.video_width, self.video_height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 绘制网格
        self._draw_grid(draw, cells_data, current_pos, collected_r2)
        
        # 绘制信息
        self._draw_info(draw, step_info)
        
        return img
    
    def _draw_grid(self, draw, cells_data, current_pos=None, collected_r2=None):
        """绘制网格"""
        if collected_r2 is None:
            collected_r2 = set()
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                position = row * self.grid_width + col
                
                # 获取单元格信息
                cell_info = cells_data.get(position, {})
                cell_type = cell_info.get('type', 'outer')
                block_type = cell_info.get('block_type')
                is_path = cell_info.get('is_path', False)
                path_order = cell_info.get('path_order', -1)
                
                # 绘制单元格背景
                self._draw_cell_background(draw, x, y, cell_type, is_path, path_order)
                
                # 绘制方块
                if block_type:
                    self._draw_block(draw, x, y, block_type, position in collected_r2)
                
                # 绘制当前位置
                if current_pos == position:
                    self._draw_current_position(draw, x, y)
                
                # 绘制位置编号
                self._draw_position_number(draw, x, y, position)
                
                # 绘制高度标识
                self._draw_height_label(draw, x, y, position)
    
    def _draw_cell_background(self, draw, x, y, cell_type, is_path, path_order):
        """绘制单元格背景"""
        # 基础背景色
        if cell_type == 'low':
            color = self.colors['low_area']
        elif cell_type == 'medium':
            color = self.colors['medium_area']
        elif cell_type == 'high':
            color = self.colors['high_area']
        else:  # outer
            color = self.colors['outer_area']
        
        # 绘制背景
        draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
        
        # 绘制路径高亮
        if is_path:
            # 半透明黄色覆盖
            overlay = Image.new('RGBA', (self.cell_size, self.cell_size), self.colors['path'])
            img = Image.new('RGBA', (self.cell_size, self.cell_size), (0, 0, 0, 0))
            img.paste(overlay, (0, 0))
            
            # 创建临时图像进行合成
            temp_img = Image.new('RGBA', (self.video_width, self.video_height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], fill=color)
            temp_img.paste(img, (x, y), img)
            
            # 绘制路径边框
            draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                          outline=self.colors['path_border'], width=3)
            
            # 绘制路径顺序
            if path_order >= 0:
                text = str(path_order + 1)
                bbox = draw.textbbox((0, 0), text, font=self._get_font(14))
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x + (self.cell_size - text_width) // 2
                text_y = y + (self.cell_size - text_height) // 2
                draw.text((text_x, text_y), text, fill=self.colors['text'], font=self._get_font(14, bold=True))
        
        # 绘制网格线
        draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                      outline=self.colors['grid_line'], width=2)
    
    def _draw_block(self, draw, x, y, block_type, is_collected=False):
        """绘制方块"""
        square_size = 40
        square_x = x + (self.cell_size - square_size) // 2
        square_y = y + (self.cell_size - square_size) // 2 + 10
        
        if block_type == 'R1':
            color = self.colors['r1_block']
            text = 'R1'
        elif block_type == 'R2':
            if is_collected:
                color = self.colors['r2_collected']
                text = 'OK'
            else:
                color = self.colors['r2_block']
                text = 'R2'
        elif block_type == 'F':
            color = self.colors['f_block']
            text = 'F'
        else:
            return
        
        # 绘制方块
        draw.rectangle([square_x, square_y, square_x + square_size, square_y + square_size], 
                      fill=color, outline=self.colors['text'], width=2)
        
        # 绘制方块文字
        bbox = draw.textbbox((0, 0), text, font=self._get_font(12))
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = square_x + (square_size - text_width) // 2
        text_y = square_y + (square_size - text_height) // 2 - 2
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=self._get_font(12, bold=True))
    
    def _draw_current_position(self, draw, x, y):
        """绘制当前位置指示器"""
        # 绘制红色圆圈
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2
        radius = 15
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], 
                    fill=self.colors['current_pos'], outline=(255, 255, 255), width=3)
    
    def _draw_position_number(self, draw, x, y, position):
        """绘制位置编号"""
        display_number = POSITION_NUMBERS.get(position, "")
        if display_number:
            text = str(display_number)
            bbox = draw.textbbox((0, 0), text, font=self._get_font(16))
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (self.cell_size - text_width) // 2
            text_y = y + 10
            draw.text((text_x, text_y), text, fill=self.colors['text'], font=self._get_font(16, bold=True))
    
    def _draw_height_label(self, draw, x, y, position):
        """绘制高度标识"""
        if position in POSITION_HEIGHTS:
            height = POSITION_HEIGHTS[position]
            if height > 0:
                height_text = f"{height}"
                bbox = draw.textbbox((0, 0), height_text, font=self._get_font(9))
                text_width = bbox[2] - bbox[0]
                text_x = x + self.cell_size - text_width - 5
                text_y = y + 5
                draw.text((text_x, text_y), height_text, fill=(100, 100, 100), font=self._get_font(9))
    
    def _draw_info(self, draw, step_info):
        """绘制步骤信息"""
        info_y = self.margin + self.grid_height * self.cell_size + 10
        
        # 绘制信息背景
        draw.rectangle([self.margin, info_y, self.video_width - self.margin, info_y + 80], 
                      fill=self.colors['info_bg'], outline=self.colors['grid_line'])
        
        # 绘制信息文字
        if step_info:
            lines = step_info.split('\n')
            for i, line in enumerate(lines):
                y_pos = info_y + 10 + i * 20
                draw.text((self.margin + 10, y_pos), line, fill=self.colors['text'], font=self._get_font(12))
    
    def _get_font(self, size, bold=False):
        """获取字体"""
        try:
            if bold:
                return ImageFont.truetype("arial.ttf", size)
            else:
                return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def generate_video(self, path_with_states, cells_data, output_path, fps=2, duration_per_step=1.0):
        """生成路径规划视频"""
        if not path_with_states:
            return False
        
        # 准备视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (self.video_width, self.video_height))
        
        try:
            # 生成每一帧
            for i, (pos, collected) in enumerate(path_with_states):
                # 创建步骤信息
                step_info = f"step: {i+1}/{len(path_with_states)}\n"
                step_info += f"pos: {POSITION_NUMBERS.get(pos, pos)}\n"
                step_info += f"collected R2: {len(collected)}"
                
                # 更新cells_data以显示当前路径状态
                current_cells_data = self._prepare_cells_data(cells_data, path_with_states[:i+1])
                
                # 创建帧
                frame = self.create_frame(current_cells_data, pos, collected, step_info)
                
                # 转换为OpenCV格式
                frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                
                # 写入多帧以控制播放速度
                for _ in range(int(fps * duration_per_step)):
                    video_writer.write(frame_cv)
            
            return True
            
        except Exception as e:
            print(f"视频生成错误: {e}")
            return False
        finally:
            video_writer.release()
    
    def _prepare_cells_data(self, original_cells_data, path_states):
        """准备单元格数据，包含路径信息"""
        cells_data = original_cells_data.copy()
        
        # 标记路径
        for i, (pos, _) in enumerate(path_states):
            if pos in cells_data:
                cells_data[pos]['is_path'] = True
                cells_data[pos]['path_order'] = i
        
        return cells_data
    
    def create_cells_data_from_ui(self, cells):
        """从UI单元格创建数据"""
        cells_data = {}
        for row in cells:
            for cell in row:
                cells_data[cell.position] = {
                    'type': cell.cell_type,
                    'block_type': cell.block_type,
                    'is_path': cell.is_path,
                    'path_order': cell.path_order
                }
        return cells_data
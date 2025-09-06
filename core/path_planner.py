"""路径规划器模块"""

import heapq
from utils.constants import (
    EXTENDED_GRID_WIDTH, EXTENDED_GRID_HEIGHT, EXTENDED_GRID_SIZE,
    EXTENDED_GREEN_POSITIONS, ENTRY_ZONE_POSITIONS, EXIT_ZONE_POSITIONS,
    TRUE_START_POSITION, ALL_OUTER_POSITIONS, POSITION_HEIGHTS,
    DEFAULT_COST_UP_200, DEFAULT_COST_DOWN_200, DEFAULT_COST_UP_400,
    DEFAULT_COST_DOWN_400, DEFAULT_PICKUP_COST, DEFAULT_REQUIRED_R2_COUNT,
    DEFAULT_OUTER_ZONE_MOVE_COST, ENTRANCE_MAPPING, EXIT_MAPPING, FINAL_OUTER_TARGET
)


class PathPlanner:
    """路径规划器类 - 扩展支持R2方块收集任务和外围区域"""
    
    def __init__(self, grid_width=EXTENDED_GRID_WIDTH, grid_height=EXTENDED_GRID_HEIGHT):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_size = grid_width * grid_height
        
        # 默认移动代价
        self.cost_up_200 = DEFAULT_COST_UP_200
        self.cost_down_200 = DEFAULT_COST_DOWN_200
        self.cost_up_400 = DEFAULT_COST_UP_400
        self.cost_down_400 = DEFAULT_COST_DOWN_400
        self.pickup_cost = DEFAULT_PICKUP_COST
        self.required_r2_count = DEFAULT_REQUIRED_R2_COUNT
        self.outer_zone_move_cost = DEFAULT_OUTER_ZONE_MOVE_COST
        
        # 位置高度映射
        self.position_heights = POSITION_HEIGHTS.copy()

        # R2构型：是否允许400台阶（默认允许）
        self.allow_400 = True
    
    def set_costs(self, cost_up_200, cost_down_200, cost_up_400, cost_down_400, 
                  pickup_cost, required_r2_count, outer_zone_move_cost=None):
        """设置移动代价和任务参数"""
        self.cost_up_200 = cost_up_200
        self.cost_down_200 = cost_down_200
        self.cost_up_400 = cost_up_400
        self.cost_down_400 = cost_down_400
        self.pickup_cost = pickup_cost
        self.required_r2_count = required_r2_count
        if outer_zone_move_cost is not None:
            self.outer_zone_move_cost = outer_zone_move_cost

    def set_r2_config(self, allow_400: bool):
        """设置R2构型：是否允许400台阶"""
        self.allow_400 = allow_400
        
    def is_valid_position(self, position):
        """检查位置是否在有效范围内"""
        return 0 <= position < self.grid_size
    
    def is_green_area(self, position):
        """检查位置是否在绿色区域"""
        return position in EXTENDED_GREEN_POSITIONS
    
    def is_outer_zone(self, position):
        """检查位置是否在外围区域"""
        return position in ALL_OUTER_POSITIONS
    
    def get_neighbors(self, position):
        """获取相邻位置"""
        if not self.is_valid_position(position):
            return []
            
        row, col = position // self.grid_width, position % self.grid_width
        neighbors = []
        
        # 四个方向：上、下、左、右
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.grid_height and 0 <= new_col < self.grid_width:
                new_pos = new_row * self.grid_width + new_col
                neighbors.append(new_pos)
        
        return neighbors
    
    def get_valid_neighbors(self, position):
        """获取有效相邻位置（考虑外围区域限制）"""
        neighbors = self.get_neighbors(position)
        valid_neighbors = []
        
        for neighbor in neighbors:
            # 如果在绿色区域，可以移动到任何相邻位置
            if self.is_green_area(position):
                valid_neighbors.append(neighbor)
            # 如果在外围区域，只能移动到其他外围区域或绿色区域
            elif self.is_outer_zone(position):
                if self.is_outer_zone(neighbor) or self.is_green_area(neighbor):
                    valid_neighbors.append(neighbor)
        
        return valid_neighbors
    
    def get_edge_cost(self, pos1, pos2, is_from_start=False, is_to_end=False):
        """获取两个位置之间的边代价"""
        # 外围之间移动
        if self.is_outer_zone(pos1) and self.is_outer_zone(pos2):
            return self.outer_zone_move_cost

        # 出口区到虚拟终点
        if is_to_end and self.is_outer_zone(pos1):
            return self.outer_zone_move_cost

        # 按高度差计算（绿色区或外圈->绿色）
        height1 = self.position_heights.get(pos1, 0)
        height2 = self.position_heights.get(pos2, 0)
        height_diff = height2 - height1

        if height_diff == 200:
            return self.cost_up_200
        elif height_diff == -200:
            return self.cost_down_200
        elif height_diff == 400:
            return self.cost_up_400
        elif height_diff == -400:
            return self.cost_down_400
        else:
            return 0

    def is_transition_allowed(self, pos1, pos2):
        """根据R2构型与出口/入口规则判断移动是否允许"""
        # 外围之间总是允许
        if self.is_outer_zone(pos1) and self.is_outer_zone(pos2):
            return True

        h1 = self.position_heights.get(pos1, 0)
        h2 = self.position_heights.get(pos2, 0)
        diff = abs(h2 - h1)

        # “仅200台阶”时禁止任何±400的高度变化
        if diff == 400 and not self.allow_400:
            return False

        # 绿↔蓝的边只允许通过合法的入口或出口配对
        g, b = (pos1, pos2) if self.is_green_area(pos1) and self.is_outer_zone(pos2) else \
               (pos2, pos1) if self.is_outer_zone(pos1) and self.is_green_area(pos2) else (None, None)
        if g is None:
            return True  # 绿↔绿 或 外↔外 已处理

        # 合法入口或出口配对才允许
        if ENTRANCE_MAPPING.get(g) == b or EXIT_MAPPING.get(g) == b:
            return True
        return False
        
    def get_adjacent_r2_blocks(self, position, r2_positions):
        """获取位置相邻的R2方块"""
        adjacent_r2 = []
        neighbors = self.get_valid_neighbors(position)
        for neighbor in neighbors:
            if neighbor in r2_positions:
                adjacent_r2.append(neighbor)
        return adjacent_r2
    
    def get_entrance_adjacent_r2_blocks(self, start_positions, r2_positions):
        """获取入口位置相邻的R2方块（从入口外部可以收集的）"""
        entrance_adjacent_r2 = []
        for start_pos in start_positions:
            if start_pos in r2_positions:
                entrance_adjacent_r2.append(start_pos)
        return entrance_adjacent_r2
    
    def dijkstra_with_collection(self, start_positions, end_positions, obstacles, r2_positions):
        """
        带收集任务的Dijkstra算法 - 支持外围区域
        状态表示：(position, collected_r2_frozenset)
        """
        # 不再使用“虚拟终点传送”，直接把外围22作为真实终点
        initial_collected = frozenset()
        distances = {}
        predecessors = {}
        pq = []

        # 特殊策略：当要求为2时，允许“≥2”并可继续拾取更多（由总代价决定是否更优）
        allow_extra_when_two = (self.required_r2_count == 2)

        # 真实起点：外圈14
        start_state = (TRUE_START_POSITION, initial_collected)
        distances[start_state] = 0
        predecessors[start_state] = None
        heapq.heappush(pq, (0, TRUE_START_POSITION, initial_collected))

        while pq:
            current_dist, current_pos, collected_r2 = heapq.heappop(pq)
            current_state = (current_pos, collected_r2)

            # 终止条件：到达外围终点22并满足收集要求
            collected_cnt = len(collected_r2)
            meets_requirement = (collected_cnt >= self.required_r2_count) if allow_extra_when_two else (collected_cnt == self.required_r2_count)
            if current_pos == FINAL_OUTER_TARGET and meets_requirement:
                return self.reconstruct_path_with_collection(predecessors, current_state)

            if current_state in distances and current_dist > distances[current_state]:
                continue

            # 普通位置之间的扩展
            if 0 <= current_pos < self.grid_size:
                # 有效障碍：排除已收集的R2
                current_obstacles = obstacles - collected_r2

                # 可收集相邻R2（当要求为2时，允许继续多取，由总代价自行选择）
                adjacent_r2 = self.get_adjacent_r2_blocks(current_pos, r2_positions - collected_r2)
                for r2_pos in adjacent_r2:
                    if len(collected_r2) < self.required_r2_count or allow_extra_when_two:
                        new_collected = collected_r2 | {r2_pos}
                        new_dist = current_dist + self.pickup_cost
                        new_state = (current_pos, new_collected)
                        if new_state not in distances or new_dist < distances[new_state]:
                            distances[new_state] = new_dist
                            predecessors[new_state] = current_state
                            heapq.heappush(pq, (new_dist, current_pos, new_collected))

                # 移动到相邻位置（外→外、外↔绿、绿→绿；按构型与合法口过滤）
                for neighbor_pos in self.get_valid_neighbors(current_pos):
                    if neighbor_pos not in current_obstacles:
                        if not self.is_transition_allowed(current_pos, neighbor_pos):
                            continue
                        move_cost = self.get_edge_cost(current_pos, neighbor_pos)
                        new_dist = current_dist + move_cost
                        new_state = (neighbor_pos, collected_r2)
                        if new_state not in distances or new_dist < distances[new_state]:
                            distances[new_state] = new_dist
                            predecessors[new_state] = current_state
                            heapq.heappush(pq, (new_dist, neighbor_pos, collected_r2))

        return None

    def calculate_path_cost_with_collection(self, path_with_states):
        """计算带收集任务的路径总代价"""
        if not path_with_states or len(path_with_states) < 2:
            return 0

        total_cost = 0
        for i in range(len(path_with_states) - 1):
            current_pos, current_collected = path_with_states[i]
            next_pos, next_collected = path_with_states[i + 1]

            # 收集
            if current_pos == next_pos and current_collected != next_collected:
                total_cost += self.pickup_cost
            # 移动
            elif current_pos != next_pos:
                total_cost += self.get_edge_cost(current_pos, next_pos)

        return total_cost
    
    def reconstruct_path_with_collection(self, predecessors, end_state):
        """重建带收集任务的路径"""
        path = []
        current_state = end_state
        
        while current_state is not None:
            path.append(current_state)
            current_state = predecessors.get(current_state)
        
        return path[::-1]
    

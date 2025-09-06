"""常量定义"""

# 网格配置 - 扩展为5x6
EXTENDED_GRID_WIDTH = 5
EXTENDED_GRID_HEIGHT = 6
EXTENDED_GRID_SIZE = EXTENDED_GRID_WIDTH * EXTENDED_GRID_HEIGHT

# 原始绿色区域配置（保持3x4）
ORIGINAL_GRID_WIDTH = 3
ORIGINAL_GRID_HEIGHT = 4
ORIGINAL_GRID_SIZE = ORIGINAL_GRID_WIDTH * ORIGINAL_GRID_HEIGHT

# 绿色区域在5x6网格中的起始位置（左上角）
GREEN_AREA_START_ROW = 1
GREEN_AREA_START_COL = 1

# 位置类型（基于原始12个位置）
LOW_POSITIONS = [1, 3, 9, 11]  # 200高度
HIGH_POSITIONS = [5, 7]        # 600高度
MEDIUM_POSITIONS = [0, 2, 4, 6, 8, 10]  # 400高度

# 扩展网格中的位置映射
# 将原始12个位置映射到5x6网格中的实际位置
def get_extended_position(original_pos):
    """将原始位置转换为扩展网格中的位置"""
    row = original_pos // ORIGINAL_GRID_WIDTH
    col = original_pos % ORIGINAL_GRID_WIDTH
    extended_row = GREEN_AREA_START_ROW + row
    extended_col = GREEN_AREA_START_COL + col
    return extended_row * EXTENDED_GRID_WIDTH + extended_col

# 扩展网格中的绿色区域位置
EXTENDED_GREEN_POSITIONS = [get_extended_position(i) for i in range(ORIGINAL_GRID_SIZE)]

# 外围区域定义 - 蓝色格子编号从13开始
# 入口区：3个蓝色地块，位于绿色地块1,2,3的正上方（注意：row 应该是 GREEN_AREA_START_ROW - 1）
ENTRY_ZONE_POSITIONS = [
    (GREEN_AREA_START_ROW - 1) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL,      # 位置1上方 → 显示编号14
    (GREEN_AREA_START_ROW - 1) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL + 1,  # 位置2上方 → 显示编号15
    (GREEN_AREA_START_ROW - 1) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL + 2   # 位置3上方 → 显示编号16
]

# 出口区：3个合法出口口 + 终点所在行的右下角（用于沿外围行走）
EXIT_ZONE_POSITIONS = [
    (GREEN_AREA_START_ROW + ORIGINAL_GRID_HEIGHT) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL,      # 位置10下方 → 显示25
    (GREEN_AREA_START_ROW + ORIGINAL_GRID_HEIGHT) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL + 1,  # 位置11下方 → 显示24
    (GREEN_AREA_START_ROW + ORIGINAL_GRID_HEIGHT) * EXTENDED_GRID_WIDTH + GREEN_AREA_START_COL + 2,  # 位置12下方 → 显示23
    EXTENDED_GRID_SIZE - 1  # 最右下角（外围编号22）
]

# 真实起始位置：外圈14
TRUE_START_POSITION = ENTRY_ZONE_POSITIONS[0]

# 绿↔蓝允许的入口映射（1→14、2→15、3→16）
ENTRANCE_MAPPING = {
    get_extended_position(0): ENTRY_ZONE_POSITIONS[0],
    get_extended_position(1): ENTRY_ZONE_POSITIONS[1],
    get_extended_position(2): ENTRY_ZONE_POSITIONS[2],
}

# 绿↔蓝允许的出口映射（10→25、11→24、12→23）
EXIT_MAPPING = {
    get_extended_position(9):  EXIT_ZONE_POSITIONS[0],
    get_extended_position(10): EXIT_ZONE_POSITIONS[1],
    get_extended_position(11): EXIT_ZONE_POSITIONS[2],
}

# 外围终点：必须到达的蓝色格子（显示编号22）
FINAL_OUTER_TARGET = EXTENDED_GRID_SIZE - 1

# 所有可通行的外围位置
ALL_OUTER_POSITIONS = ENTRY_ZONE_POSITIONS + EXIT_ZONE_POSITIONS

# 位置编号映射 - 绿色格子1-12，蓝色格子13-18
POSITION_NUMBERS = {}

# 绿色区域编号1-12
for i, pos in enumerate(EXTENDED_GREEN_POSITIONS):
    POSITION_NUMBERS[pos] = i + 1

# 蓝色区域编号13-18（绕一圈）
blue_positions = []
# 上边（从左到右）
for col in range(EXTENDED_GRID_WIDTH):
    pos = 0 * EXTENDED_GRID_WIDTH + col
    if pos not in EXTENDED_GREEN_POSITIONS:
        blue_positions.append(pos)
# 右边（从上到下）
for row in range(1, EXTENDED_GRID_HEIGHT - 1):
    pos = row * EXTENDED_GRID_WIDTH + (EXTENDED_GRID_WIDTH - 1)
    if pos not in EXTENDED_GREEN_POSITIONS:
        blue_positions.append(pos)
# 下边（从右到左）
for col in range(EXTENDED_GRID_WIDTH - 1, -1, -1):
    pos = (EXTENDED_GRID_HEIGHT - 1) * EXTENDED_GRID_WIDTH + col
    if pos not in EXTENDED_GREEN_POSITIONS:
        blue_positions.append(pos)
# 左边（从下到上）
for row in range(EXTENDED_GRID_HEIGHT - 2, 0, -1):
    pos = row * EXTENDED_GRID_WIDTH + 0
    if pos not in EXTENDED_GREEN_POSITIONS:
        blue_positions.append(pos)

# 给蓝色位置分配编号13-18
for i, pos in enumerate(blue_positions):
    POSITION_NUMBERS[pos] = 13 + i

# 位置高度映射（扩展到5x6网格）
POSITION_HEIGHTS = {}
# 绿色区域保持原有高度
for i, pos in enumerate(EXTENDED_GREEN_POSITIONS):
    if i in LOW_POSITIONS:
        POSITION_HEIGHTS[pos] = 200
    elif i in HIGH_POSITIONS:
        POSITION_HEIGHTS[pos] = 600
    else:
        POSITION_HEIGHTS[pos] = 400

# 外围区域高度为0
for pos in ALL_OUTER_POSITIONS:
    POSITION_HEIGHTS[pos] = 0

# 约束条件（基于原始位置）
OUTER_POSITIONS = [0, 1, 2, 3, 5, 6, 8, 9, 10, 11]
ENTRANCE_POSITIONS = [0, 1, 2]
CORRIDOR_POSITIONS = [4, 7, 10]
FORBIDDEN_F_POSITIONS = [0, 1, 2]
FORBIDDEN_R1_POSITIONS = [11]

# 方块限制
MAX_R1_COUNT = 3
MAX_R2_COUNT = 4
MAX_F_COUNT = 1

# 默认代价
DEFAULT_COST_UP_200 = 2
DEFAULT_COST_DOWN_200 = 2
DEFAULT_COST_UP_400 = 4
DEFAULT_COST_DOWN_400 = 4
DEFAULT_PICKUP_COST = 1
DEFAULT_REQUIRED_R2_COUNT = 3
DEFAULT_OUTER_ZONE_MOVE_COST = 1  # 新增：外围区域移动代价
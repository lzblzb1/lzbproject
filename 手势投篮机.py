import mediapipe as mp
import cv2
import numpy as np
import pygame
import math
import time
# 初始化pygame

pygame.init()

# 游戏窗口的尺寸
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30  # 帧率
# 加载背景图片
background = pygame.image.load("C:/Users/ZhuanZ/Desktop/tp/bas.jpg")  # 替换为你的背景图片路径
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))  # 调整图片大小以适应窗口

# 设置窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("手势投篮游戏")

# 加载支持中文的字体文件
font_path = "C:/Windows/Fonts/msyh.ttc"  # Windows 微软雅黑字体
font = pygame.font.Font(font_path, 30)  # 设置字体大小为30

# 初始化mediapipe手势识别模块
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# 进度条的参数
max_power = 100  # 最大蓄力
current_power = 0  # 当前蓄力
is_shooting = False  # 是否开始投篮
a=0
# 球的参数
ball_radius = 25
ball_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100]  # 球的位置
ball_velocity = [0, 0]  # 球的速度

# 篮筐的参数
hoop_radius = 40
hoop_pos = [WINDOW_WIDTH // 2, 130]  # 篮筐的位置

# 加载篮球图片
original_ball_image = pygame.image.load("C:/Users/ZhuanZ/Desktop/tp/3w.jpg")  # 替换为你的篮球图片路径
original_ball_image = pygame.transform.scale(original_ball_image, (ball_radius * 2, ball_radius * 2))  # 调整图片大小

# 裁剪图片为圆形
def crop_image_to_circle(image, radius):
    cropped_image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(cropped_image, (255, 255, 255, 255), (radius, radius), radius*0.8)
    image = pygame.transform.scale(image, (radius * 2, radius * 2))
    cropped_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return cropped_image

ball_image = crop_image_to_circle(original_ball_image, ball_radius)

# 计算两向量之间的夹角
def calculate_angle(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    cos_angle = dot_product / (norm_v1 * norm_v2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    return np.degrees(angle)

# 手势检测函数：通过手腕位置和中指指尖的高低判断手势状态
def detect_wrist_position(frame):
    global current_power, is_shooting

    # 转换帧为 RGB 格式（Mediapipe 需要 RGB 格式）
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # 如果检测到手势
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 获取手腕和中指指尖的位置
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]  # 手腕
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]  # 中指指尖
            middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]  # 中指 MCP 关节
            #print(f"中指指尖 Y: {middle_tip.y}, 中指 MCP Y: {middle_mcp.y}")
            # 判断中指指尖和手腕的高低
            if middle_tip.y > middle_mcp.y:  # 中指指尖低于手腕 -> 投篮动作
                if not is_shooting:
                    is_shooting = True
                return "投篮动作"
            elif middle_tip.y < wrist.y:  # 中指指尖高于手腕 -> 蓄力中
                current_power = min(current_power + 5, max_power)  # 增加蓄力值
                is_shooting = False
                return "蓄力中"


    # 如果未检测到手势
    return "未检测到手势"

#截取篮球的圆
def crop_image_to_circle(image, radius):
    cropped_image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(cropped_image, (255, 255, 255, 255), (radius, radius), radius)
    image = pygame.transform.scale(image, (radius * 2, radius * 2))
    cropped_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return cropped_image

def draw_basket_net():
    global ball_pos, hoop_pos, hoop_radius

    # 定义篮网的参数
    net_top_left = (hoop_pos[0] - hoop_radius // 2, hoop_pos[1] + 5)  # 篮网左上角
    net_top_right = (hoop_pos[0] + hoop_radius // 2, hoop_pos[1] + 5)  # 篮网右上角
    net_bottom_left = (hoop_pos[0] - hoop_radius // 3, hoop_pos[1] + 50)  # 篮网左下角
    net_bottom_right = (hoop_pos[0] + hoop_radius // 3, hoop_pos[1] + 50)  # 篮网右下角
    # 检测是否球进入篮筐
    if current_power > 60 and current_power < 90 and ball_pos[1] < 200:
        net_top_left = (net_bottom_left[0] - 10, net_bottom_left[1] + 10)  # 左下角摆动
        net_top_right = (net_bottom_right[0] + 10, net_bottom_right[1] + 10)  # 右下角摆动
    # 绘制轮廓线
    pygame.draw.line(screen, (255, 255, 255), net_top_left, net_bottom_left, 2)  # 左侧边线
    pygame.draw.line(screen, (255, 255, 255), net_top_right, net_bottom_right, 2)  # 右侧边线
    pygame.draw.line(screen, (255, 255, 255), net_top_left, net_top_right, 2)  # 顶部边线

    # 绘制中间对称线
    mid_left = ((net_top_left[0] + net_bottom_left[0]) // 2, (net_top_left[1] + net_bottom_left[1]) // 2)
    mid_right = ((net_top_right[0] + net_bottom_right[0]) // 2, (net_top_right[1] + net_bottom_right[1]) // 2)

    line_left = ((net_top_left[0] + net_bottom_left[0]) // 2, (net_top_left[1] + net_bottom_left[1]) // 1.9)
    line_right = ((net_top_right[0] + net_bottom_right[0]) // 2, (net_top_right[1] + net_bottom_right[1]) // 1.9)

    # 绘制中间对称线
    mid_top = ((net_top_left[0] + net_bottom_left[0]) // 2, (net_top_left[1] + net_bottom_left[1]) // 2)
    mid_top1 = ((net_top_right[0] + net_bottom_right[0]) // 2, (net_top_right[1] + net_bottom_right[1]) // 2)
    # 左斜线

    pygame.draw.line(screen, (255, 255, 255), mid_left, mid_right, 2)
    # 右斜线
    pygame.draw.line(screen, (255, 255, 255), line_left, line_right, 2)


# 绘制进度条
def draw_progress_bar():
    pygame.draw.rect(screen, (0, 255, 0), (50, WINDOW_HEIGHT - 50, 700, 30))
    pygame.draw.rect(screen, (255, 0, 0), (50, WINDOW_HEIGHT - 50, 7 * current_power, 30))  # 增加进度条的速度
    pygame.draw.rect(screen, (0, 0,255 ), (470, WINDOW_HEIGHT - 50, 210, 30))  # 增加进度条的速度

# 绘制篮球和篮筐
def draw_basketball_and_hoop():
    #pygame.draw.circle(screen, (255, 0, 0), hoop_pos, hoop_radius, 5)  # 篮筐
    # 绘制裁剪后的篮球图片
    screen.blit(ball_image, (ball_pos[0] - ball_radius, ball_pos[1] - ball_radius))  # 图片中心与球位置对齐
    # 绘制篮网
    draw_basket_net()
# 更新篮球的位置
def update_ball():
    global ball_pos, ball_velocity, is_shooting, current_power,a

    if is_shooting:
        # 增大球的初速度，使篮球向上移动得更快
        ball_velocity[1] = -current_power / 3  # 投篮的初速度（向上）- 降低除数增大速度
        ball_velocity[0] = (ball_pos[0] - hoop_pos[0]) / 50  # 增大篮筐方向的速度，增加水平移动速度

    # 更新球的位置
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    # 模拟重力，加大重力使球下落得更快
    ball_velocity[1] += 1.0  # 重力影响，增加值使下落更快
    if current_power > 60 and current_power < 90:
        a = 1  # 进球
        # 显示信息
        progress_text = font.render(f"{message}: {wrist_position}, 蓄力: {current_power}/{max_power}", True,
                                    (0, 0, 0))
        # 将渲染后的文字绘制到屏幕上
        screen.blit(progress_text, (50, WINDOW_HEIGHT - 100))  # 设置显示位置
    else:
        a = 0
    # 如果篮球飞出屏幕或进篮筐，重置
    if ball_pos[1] > WINDOW_HEIGHT or (math.hypot(ball_pos[0] - hoop_pos[0], ball_pos[1] - hoop_pos[1]) < hoop_radius):
        if ball_pos[1] > WINDOW_HEIGHT:  # 球掉出屏幕
            ball_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100]
            ball_velocity = [0, 0]
        elif math.hypot(ball_pos[0] - hoop_pos[0], ball_pos[1] - hoop_pos[1]) < hoop_radius:
            #print("投篮成功!")
            ball_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100]
            ball_velocity = [0, 0]
            current_power = 0  # 重置蓄力
            is_shooting = False

# 主循环
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 检测手势状态
    wrist_position = detect_wrist_position(frame)

    screen.blit(background, (0, 0))  # 绘制背景图片

    # 绘制进度条
    draw_progress_bar()

    # 绘制篮球和篮筐
    draw_basketball_and_hoop()

    # 更新并绘制球的位置
    update_ball()

    # 根据 a 的值更新显示信息
    if a == 1:
        message = "球进啦牛逼"
        a=0
    else:
        message = "球没进"

    # # 显示信息
    # progress_text = font.render(f"{message}: {wrist_position}, 蓄力: {current_power}/{max_power}", True, (0, 0, 0))
    #
    # # 将渲染后的文字绘制到屏幕上
    # screen.blit(progress_text, (50, WINDOW_HEIGHT - 100))  # 设置显示位置

    # 更新显示
    pygame.display.update()

    # 退出条件：按下 "q" 键退出
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            exit()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

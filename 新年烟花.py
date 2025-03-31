import os
import sys
import pygame
import random
import math

# 初始化pygame
pygame.init()
# 初始化音效
pygame.mixer.init()  # 初始化音频系统
# 设置窗口大小
WIDTH, HEIGHT = 1500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("新年烟花")

# 获取资源路径
def resource_path(relative_path):
    """获取资源文件的路径，兼容开发环境和打包后的exe文件"""
    if getattr(sys, 'frozen', False):  # 如果是打包后的exe程序
        base_path = sys._MEIPASS
    else:  # 如果是开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 定义颜色列表
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 128, 0), (128, 0, 255), (0, 128, 255),
    (255, 20, 147), (50, 205, 50), (218, 165, 32)
]

# 尝试加载底图
try:
    # 使用 resource_path 来加载图片
    background = pygame.image.load(resource_path("6u5gfyxh.png"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error:
    print("底图加载失败，将使用黑色背景。")
    background = None
# 加载音效
firework_sound = pygame.mixer.Sound(resource_path("yanhua.mp3"))  # 加载音效文件
# 设置文字，使用支持中文的字体
font = pygame.font.Font(None, 60)  # 确保 simhei.ttf 存在，或者指定完整路径
text = font.render("", True, (255, 255, 255))
text_rect = text.get_rect(center=(WIDTH // 1.5, HEIGHT // 1.5))

# 创建“点火”按钮
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
button_color = (255, 165, 0)  # 按钮的颜色（橙色）
button_text = font.render("fire", True, (0, 0, 0))
button_text_rect = button_text.get_rect(center=button_rect.center)

# 创建“自动放烟花”按钮
auto_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 160, 200, 50)
auto_button_color = (0, 255, 0)  # 按钮的颜色（绿色）
auto_button_text = font.render("Auto Fire", True, (0, 0, 0))
auto_button_text_rect = auto_button_text.get_rect(center=auto_button_rect.center)

class Particle:
    def __init__(self, x, y, color, speed, angle, life_decay=0.1):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed * 2
        self.angle = angle
        self.lifetime = random.randint(12, 15)
        self.life_decay = life_decay
        self.size = random.randint(1, 3)  # 随机粒子大小
        self.remove = False
        self.length =5
        self.width = 8
    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.speed *= 0.9
        self.lifetime -= self.life_decay
        if self.lifetime <= 0 or self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.remove = True

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int((self.lifetime / 40) * 255)
            s = pygame.Surface((self.length*2,self.width*2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), (1, 1, self.length, self.width))  # 绘制长条形矩形
            screen.blit(s, (int(self.x - self.length / 2), int(self.y - self.width / 2)))  # 绘制到屏幕上


class Firework:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT
        self.color = random.choice(COLORS)
        self.speed = random.randint(9, 13)
        self.exploded = False
        self.particles = []
        self.trail = []
        self.trail_length = 8
        self.remove = False
        self.explode_time = random.randint(50, 70)  # 延迟爆炸

    def update(self):
        if not self.exploded:
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
            self.y -= self.speed
            self.speed -= 0.1
            self.explode_time -= 1
            if self.explode_time <= 0:
                self.explode()
                firework_sound.play()  # 播放烟花爆炸音效
            elif self.y < 0:
                self.remove = True
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.remove:
                    self.particles.remove(particle)
            if len(self.particles) == 0:
                self.remove = True

    def explode(self):
        self.exploded = True
        num_particles = random.randint(300, 500)  # 增加粒子数量
        num_directions = 36
        direction_angle = 10

        for i in range(num_particles):
            # 计算每个粒子的发射角度（均匀分布在圆周上）
            base_angle = i * direction_angle
            # 随机加入小幅度的偏差，使得粒子不会严格对齐
            angle_variation = random.uniform(-math.pi / 12, math.pi / 12)
            angle = base_angle + angle_variation
            speed = random.uniform(3, 7)
            color = random.choice(COLORS)
            particle = Particle(self.x, self.y, color, speed, base_angle)
            self.particles.append(particle)

    def draw(self, screen):
        if not self.exploded:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int((i + 1) / len(self.trail) * 255)
                s = pygame.Surface((2, 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha), (1, 1), 1)
                screen.blit(s, (int(tx - 1), int(ty - 1)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)
        else:
            for particle in self.particles:
                particle.draw(screen)


# 创建烟花列表
fireworks = []
# 按钮状态变量
firing = False
firework_count = 0
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查鼠标点击是否在按钮区域内
            if button_rect.collidepoint(event.pos):
                # 点火按钮点击后，连续发送五个烟花
                firing = True
                firework_count = 1

    # 每帧有一定概率生成新的烟花
    if firing and firework_count > 0:
        fireworks.append(Firework())
        firework_count -= 1
        if firework_count == 0:
            firing = False

    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((0, 0, 0))

    # 绘制按钮
    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_text, button_text_rect)  # 绘制按钮文字

    screen.blit(text, text_rect)  # 绘制文字

    for firework in fireworks[:]:
        firework.update()
        firework.draw(screen)
        if firework.remove:
            fireworks.remove(firework)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


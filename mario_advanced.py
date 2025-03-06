import pygame
import sys
import os
import random

# 初始化 Pygame
pygame.init()
pygame.mixer.init()  # 初始化音频

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("超级马里奥")

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# 创建资源文件夹
if not os.path.exists('resources'):
    os.makedirs('resources')
    os.makedirs('resources/images')
    os.makedirs('resources/sounds')

# 加载图像函数
def load_image(name, colorkey=None, scale=1):
    image = pygame.Surface((30, 30))
    image.fill(colorkey if colorkey else BLACK)
    if name == 'player':
        pygame.draw.rect(image, BLUE, (0, 0, 30, 30))
    elif name == 'enemy':
        pygame.draw.rect(image, RED, (0, 0, 30, 30))
    elif name == 'coin':
        pygame.draw.circle(image, YELLOW, (15, 15), 10)
    elif name == 'platform':
        pygame.draw.rect(image, BROWN, (0, 0, 30, 10))
    
    if colorkey:
        image.set_colorkey(colorkey)
    
    return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

# 加载音效函数
def load_sound(name):
    # 由于没有实际音效文件，我们只创建一个空的Sound对象
    return pygame.mixer.Sound(os.path.join('resources/sounds', f"{name}.wav")) if os.path.exists(os.path.join('resources/sounds', f"{name}.wav")) else None

# 游戏状态
class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.win = False

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('player', BLACK, 1.5)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = WINDOW_HEIGHT - self.rect.height - 10
        self.vel_y = 0
        self.vel_x = 0
        self.jumping = False
        self.speed = 5
        self.direction = "right"
        self.jump_sound = load_sound('jump')

    def update(self):
        keys = pygame.key.get_pressed()
        
        # 左右移动
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.direction = "right"
            
        # 跳跃
        if keys[pygame.K_SPACE] and not self.jumping:
            self.vel_y = -15
            self.jumping = True
            if self.jump_sound:
                self.jump_sound.play()
            
        # 重力
        self.vel_y += 0.8
        
        # 更新位置
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # 地面碰撞检测
        if self.rect.y > WINDOW_HEIGHT - self.rect.height - 10:
            self.rect.y = WINDOW_HEIGHT - self.rect.height - 10
            self.vel_y = 0
            self.jumping = False
            
        # 边界限制
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WINDOW_WIDTH - self.rect.width:
            self.rect.x = WINDOW_WIDTH - self.rect.width

# 平台类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 20))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('enemy', BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1  # 1 表示向右，-1 表示向左
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        
        # 改变方向
        if self.rect.right > WINDOW_WIDTH or self.rect.left < 0:
            self.direction *= -1

# 金币类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('coin', BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.value = 10

# 游戏管理器
class Game:
    def __init__(self):
        self.state = GameState()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 创建平台
        self.create_level(self.state.level)
        
        # 加载音效
        self.coin_sound = load_sound('coin')
        self.death_sound = load_sound('death')
        
        # 字体
        self.font = pygame.font.SysFont(None, 36)
    
    def create_level(self, level):
        # 清空所有精灵组
        self.platforms.empty()
        self.enemies.empty()
        self.coins.empty()
        
        # 根据关卡创建平台
        if level == 1:
            platforms_data = [
                (0, WINDOW_HEIGHT - 10, WINDOW_WIDTH),  # 地面
                (300, 400, 200),
                (100, 300, 200),
                (500, 200, 200),
            ]
            
            for x, y, width in platforms_data:
                platform = Platform(x, y, width)
                self.platforms.add(platform)
                self.all_sprites.add(platform)
            
            # 创建敌人
            enemies_data = [(400, 370), (150, 270)]
            for x, y in enemies_data:
                enemy = Enemy(x, y)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            
            # 创建金币
            coins_data = [(350, 350), (150, 250), (550, 150), (700, 500)]
            for x, y in coins_data:
                coin = Coin(x, y)
                self.coins.add(coin)
                self.all_sprites.add(coin)
    
    def update(self):
        if not self.state.game_over and not self.state.win:
            # 更新所有精灵
            self.all_sprites.update()
            
            # 检测玩家与平台的碰撞
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            for platform in hits:
                # 只有从上方碰撞才停止下落
                if self.player.vel_y > 0 and self.player.rect.bottom <= platform.rect.top + 10:
                    self.player.rect.bottom = platform.rect.top
                    self.player.vel_y = 0
                    self.player.jumping = False
            
            # 检测玩家与敌人的碰撞
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in enemy_hits:
                # 如果玩家从上方跳到敌人头上
                if self.player.vel_y > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                    enemy.kill()
                    self.player.vel_y = -10  # 弹跳
                    self.state.score += 20
                else:
                    # 玩家受伤
                    self.state.lives -= 1
                    if self.death_sound:
                        self.death_sound.play()
                    
                    # 重置玩家位置
                    self.player.rect.x = 50
                    self.player.rect.y = WINDOW_HEIGHT - self.player.rect.height - 10
                    
                    if self.state.lives <= 0:
                        self.state.game_over = True
            
            # 检测玩家与金币的碰撞
            coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
            for coin in coin_hits:
                self.state.score += coin.value
                if self.coin_sound:
                    self.coin_sound.play()
            
            # 检查是否通关（收集所有金币）
            if len(self.coins) == 0:
                self.state.win = True
    
    def draw(self, screen):
        # 绘制背景
        screen.fill(WHITE)
        
        # 绘制所有精灵
        self.all_sprites.draw(screen)
        
        # 绘制得分和生命值
        score_text = self.font.render(f"得分: {self.state.score}", True, BLACK)
        lives_text = self.font.render(f"生命: {self.state.lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        # 绘制游戏结束或胜利信息
        if self.state.game_over:
            game_over_text = self.font.render("游戏结束! 按R键重新开始", True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        
        if self.state.win:
            win_text = self.font.render("恭喜通关! 按R键重新开始", True, GREEN)
            screen.blit(win_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))

# 创建游戏实例
game = Game()

# 游戏主循环
clock = pygame.time.Clock()

while True:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # 重新开始游戏
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game.state.game_over or game.state.win):
                game = Game()

    # 更新游戏
    game.update()
    
    # 绘制
    game.draw(screen)
    
    # 更新显示
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)
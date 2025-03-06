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
pygame.display.set_caption("超级马里奥增强版")

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# 游戏常量
GRAVITY = 0.8
JUMP_SPEED = -15
PLAYER_SPEED = 5
ENEMY_SPEED = 2

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
    elif name == 'mushroom':
        pygame.draw.rect(image, RED, (0, 0, 30, 30))
        pygame.draw.circle(image, WHITE, (15, 10), 10)
    elif name == 'star':
        points = [(15, 0), (18, 10), (28, 10), (20, 16),
                 (23, 28), (15, 20), (7, 28), (10, 16),
                 (2, 10), (12, 10)]
        pygame.draw.polygon(image, YELLOW, points)
    elif name == 'brick':
        pygame.draw.rect(image, BROWN, (0, 0, 30, 30))
        pygame.draw.line(image, BLACK, (0, 15), (30, 15), 2)
        pygame.draw.line(image, BLACK, (15, 0), (15, 30), 2)
    
    if colorkey:
        image.set_colorkey(colorkey)
    
    return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

# 加载音效函数
def load_sound(name):
    return pygame.mixer.Sound(os.path.join('resources/sounds', f"{name}.wav")) if os.path.exists(os.path.join('resources/sounds', f"{name}.wav")) else None

# 游戏状态
class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.win = False
        self.time_left = 300  # 关卡时间限制（秒）
        self.start_time = pygame.time.get_ticks()

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
        self.speed = PLAYER_SPEED
        self.direction = "right"
        self.is_big = False  # 是否处于变大状态
        self.is_invincible = False  # 是否处于无敌状态
        self.invincible_timer = 0
        self.jump_sound = load_sound('jump')

    def power_up(self, power_type):
        if power_type == 'mushroom':
            self.is_big = True
            self.image = load_image('player', BLACK, 2.0)
            self.rect.y -= 15  # 调整位置以适应新大小
        elif power_type == 'star':
            self.is_invincible = True
            self.invincible_timer = pygame.time.get_ticks()

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
            self.vel_y = JUMP_SPEED
            self.jumping = True
            if self.jump_sound:
                self.jump_sound.play()
        
        # 更新无敌状态
        if self.is_invincible:
            if pygame.time.get_ticks() - self.invincible_timer > 10000:  # 10秒无敌时间
                self.is_invincible = False
            
        # 重力
        self.vel_y += GRAVITY
        
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

# 砖块类
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('brick', BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.has_item = random.choice([True, False])  # 随机决定是否包含道具

# 道具类
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.type = power_type
        self.image = load_image(power_type, BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.vel_x = 2

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x

        # 地面碰撞检测
        if self.rect.y > WINDOW_HEIGHT - self.rect.height - 10:
            self.rect.y = WINDOW_HEIGHT - self.rect.height - 10
            self.vel_y = 0

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('enemy', BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed * self.direction
        
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
        self.bricks = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 创建关卡
        self.create_level(self.state.level)
        
        # 加载音效
        self.coin_sound = load_sound('coin')
        self.death_sound = load_sound('death')
        self.powerup_sound = load_sound('powerup')
        
        # 字体
        self.font = pygame.font.SysFont(None, 36)
    
    def create_level(self, level):
        # 清空所有精灵组
        self.platforms.empty()
        self.enemies.empty()
        self.coins.empty()
        self.bricks.empty()
        self.powerups.empty()
        
        # 根据关卡创建游戏元素
        if level == 1:
            # 创建平台
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
            
            # 创建砖块
            bricks_data = [(350, 300), (400, 300), (450, 300)]
            for x, y in bricks_data:
                brick = Brick(x, y)
                self.bricks.add(brick)
                self.all_sprites.add(brick)
            
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
            # 更新时间
            elapsed_time = (pygame.time.get_ticks() - self.state.start_time) // 1000
            self.state.time_left = max(0, 300 - elapsed_time)
            
            if self.state.time_left == 0:
                self.state.game_over = True
            
            # 更新所有精灵
            self.all_sprites.update()
            
            # 检测玩家与平台的碰撞
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            for platform in hits:
                if self.player.vel_y > 0 and self.player.rect.bottom <= platform.rect.top + 10:
                    self.player.rect.bottom = platform.rect.top
                    self.player.vel_y = 0
                    self.player.jumping = False
            
            # 检测玩家与砖块的碰撞
            brick_hits = pygame.sprite.spritecollide(self.player, self.bricks, False)
            for brick in brick_hits:
                if self.player.vel_y < 0:  # 从下方撞击
                    if brick.has_item:
                        power_type = random.choice(['mushroom', 'star'])
                        powerup = PowerUp(brick.rect.x, brick.rect.y - 30, power_type)
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)
                        brick.has_item = False
                    brick.kill()
            
            # 检测玩家与道具的碰撞
            powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in powerup_hits:
                self.player.power_up(powerup.type)
                if self.powerup_sound:
                    self.powerup_sound.play()
            
            # 检测玩家与敌人的碰撞
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in enemy_hits:
                # 如果玩家处于无敌状态，直接消灭敌人
                if self.player.is_invincible:
                    enemy.kill()
                    self.state.score += 20
                    continue
                    
                # 如果玩家从上方跳到敌人头上
                if self.player.vel_y > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                    enemy.kill()
                    self.player.vel_y = -10  # 弹跳
                    self.state.score += 20
                else:
                    # 玩家受伤
                    if self.player.is_big:
                        # 如果是大马里奥，变小但不死
                        self.player.is_big = False
                        self.player.image = load_image('player', BLACK, 1.5)
                        # 短暂无敌时间
                        self.player.is_invincible = True
                        self.player.invincible_timer = pygame.time.get_ticks()
                    else:
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
        
        # 绘制得分、生命值和时间
        score_text = self.font.render(f"得分: {self.state.score}", True, BLACK)
        lives_text = self.font.render(f"生命: {self.state.lives}", True, BLACK)
        time_text = self.font.render(f"时间: {self.state.time_left}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(time_text, (WINDOW_WIDTH - 150, 10))
        
        # 如果玩家处于无敌状态，显示闪烁效果
        if self.player.is_invincible and (pygame.time.get_ticks() // 200) % 2 == 0:
            pygame.draw.rect(screen, YELLOW, self.player.rect, 2)
        
        # 绘制游戏结束或胜利信息
        if self.state.game_over:
            game_over_text = self.font.render("游戏结束! 按R键重新开始", True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        
        if self.state.win:
            win_text = self.font.render("恭喜通关! 按N键进入下一关，按R键重新开始", True, GREEN)
            screen.blit(win_text, (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2))

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
        
        # 重新开始游戏或进入下一关
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game.state.game_over or game.state.win):
                game = Game()
            elif event.key == pygame.K_n and game.state.win:
                game.state.level += 1
                game.state.win = False
                game.state.start_time = pygame.time.get_ticks()
                game.create_level(game.state.level)

    # 更新游戏
    game.update()
    
    # 绘制
    game.draw(screen)
    
    # 更新显示
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)
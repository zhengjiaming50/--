import pygame
import sys

# 初始化Pygame
pygame.init()

# 游戏窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyMario")

# 颜色定义
BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT - 100))
        
        # 移动属性
        self.speed = 5
        self.jump_force = -15
        self.gravity = 0.8
        self.direction = pygame.math.Vector2(0, 0)
        self.on_ground = False

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        if self.on_ground:
            self.direction.y = self.jump_force
            self.on_ground = False

    def update(self):
        keys = pygame.key.get_pressed()
        
        # 水平移动
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # 跳跃
        if keys[pygame.K_SPACE]:
            self.jump()

        # 应用重力
        self.apply_gravity()

        # 边界限制
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True

# 平台类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.speed = 3

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

# 金币类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

# 创建游戏组
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

# 创建玩家
player = Player()
all_sprites.add(player)

# 创建平台
platform1 = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
platform2 = Platform(300, SCREEN_HEIGHT - 150, 200, 20)
platforms.add(platform1, platform2)
all_sprites.add(platform1, platform2)

# 创建敌人
enemy1 = Enemy(500, SCREEN_HEIGHT - 70)
enemies.add(enemy1)
all_sprites.add(enemy1)

# 创建金币
coin1 = Coin(400, SCREEN_HEIGHT - 180)
coins.add(coin1)
all_sprites.add(coin1)

# 游戏循环
clock = pygame.time.Clock()
running = True
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 碰撞检测：平台
    for platform in platforms:
        if player.rect.colliderect(platform.rect):
            if player.direction.y > 0:
                player.rect.bottom = platform.rect.top
                player.on_ground = True
                player.direction.y = 0

    # 碰撞检测：敌人
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    if enemy_hits:
        # 简单死亡处理
        print("Game Over!")
        running = False

    # 碰撞检测：金币
    coin_hits = pygame.sprite.spritecollide(player, coins, True)
    for coin in coin_hits:
        score += 10
        print(f"Score: {score}")

    # 更新
    all_sprites.update()

    # 绘制
    screen.fill(BLUE)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

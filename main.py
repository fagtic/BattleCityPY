import pygame
import random
import sys
import os

# Инициализация Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Константы игры
TILE_SIZE = 16
GAME_WIDTH = 416
GAME_HEIGHT = 416
SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT + 80  # Добавляем место для интерфейса

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (76, 175, 80)
RED = (255, 82, 82)
YELLOW = (255, 204, 0)
BROWN = (139, 69, 19)
GRAY = (85, 85, 85)
DARK_GREEN = (34, 139, 34)
BLUE = (30, 144, 255)

class Tank:
    def __init__(self, x, y, is_player=False):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 1.5
        self.height = TILE_SIZE * 1.5
        self.speed = 2 if is_player else 1
        self.direction = 0  # 0: вверх, 1: вправо, 2: вниз, 3: влево
        self.is_player = is_player
        self.color = GREEN if is_player else RED
        
        self.image = pygame.image.load('assets/tank.png')
        self.has_image = True


    def draw(self, screen):
        if self.has_image and self.image:
                sprite_width = self.image.get_width() // 4
                sprite_height = self.image.get_height()
                
                # Определяем область спрайта в зависимости от направления
                if self.direction == 0:  # вверх
                    sx = sprite_width * 2
                elif self.direction == 1:  # вправо
                    sx = sprite_width * 0
                elif self.direction == 2:  # вниз
                    sx = sprite_width * 3
                else:  # влево
                    sx = sprite_width * 1
                
                # Создаем поверхность для спрайта
                sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                # Исправленный blit - убираем лишние скобки
                sprite_surface.blit(self.image, (-sx, 0))
                
                # Масштабируем и рисуем
                scaled_sprite = pygame.transform.scale(sprite_surface, (int(self.width), int(self.height)))
                screen.blit(scaled_sprite, (self.x, self.y))
                return
        
        # Fallback отрисовка - упрощенная версия
        tank_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Корпус танка
        pygame.draw.rect(screen, self.color, tank_rect)
        
        # Пушка (в зависимости от направления)
        if self.direction == 0:  # вверх
            pygame.draw.rect(screen, (51, 51, 51), 
                           (self.x + self.width // 2 - 2, self.y - 8, 4, 12))
        elif self.direction == 1:  # вправо
            pygame.draw.rect(screen, (51, 51, 51), 
                           (self.x + self.width, self.y + self.height // 2 - 2, 12, 4))
        elif self.direction == 2:  # вниз
            pygame.draw.rect(screen, (51, 51, 51), 
                           (self.x + self.width // 2 - 2, self.y + self.height, 4, 12))
        else:  # влево
            pygame.draw.rect(screen, (51, 51, 51), 
                           (self.x - 12, self.y + self.height // 2 - 2, 12, 4))

    def move(self):
        old_x, old_y = self.x, self.y
        
        if self.direction == 0:  # вверх
            self.y -= self.speed
        elif self.direction == 1:  # вправо
            self.x += self.speed
        elif self.direction == 2:  # вниз
            self.y += self.speed
        elif self.direction == 3:  # влево
            self.x -= self.speed
        
        # Ограничение движения в пределах экрана
        self.x = max(0, min(GAME_WIDTH - self.width, self.x))
        self.y = max(0, min(GAME_HEIGHT - self.height, self.y))
        
        return old_x, old_y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())

class Bullet:
    def __init__(self, x, y, direction, is_player):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 6
        self.speed = 5
        self.direction = direction
        self.is_player = is_player
        self.active = True

    def update(self):
        if self.direction == 0:  # вверх
            self.y -= self.speed
        elif self.direction == 1:  # вправо
            self.x += self.speed
        elif self.direction == 2:  # вниз
            self.y += self.speed
        elif self.direction == 3:  # влево
            self.x -= self.speed
        
        # Деактивация при выходе за границы
        if (self.x < 0 or self.x > GAME_WIDTH or 
            self.y < 0 or self.y > GAME_HEIGHT):
            self.active = False

    def draw(self, screen):
        color = YELLOW if self.is_player else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())

class Wall:
    def __init__(self, x, y, wall_type='brick'):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.type = wall_type
        
        # Загрузка изображения стены
        try:
            image_path = f'assets/{wall_type}.png'
            if os.path.exists(image_path):
                self.image = pygame.image.load(image_path)
                self.has_image = True
            else:
                self.has_image = False
        except Exception as e:
            self.has_image = False

    def draw(self, screen):
        if self.has_image and self.image:
            try:
                screen.blit(self.image, (self.x, self.y))
                return
            except Exception as e:
                print(f"Ошибка отрисовки {self.type}: {e}")
        
        # Fallback отрисовка
        if self.type == 'brick':
            color = BROWN
        elif self.type == 'steel':
            color = GRAY
        elif self.type == 'forest':
            color = DARK_GREEN
        elif self.type == 'water':
            color = BLUE
        else:
            color = BROWN
            
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides_with_tank(self, tank):
        if self.type == 'forest':
            return False
        return self.get_rect().colliderect(tank.get_rect())

    def collides_with_bullet(self, bullet):
        if self.type in ['water', 'forest']:
            return False
        return self.get_rect().colliderect(bullet.get_rect())

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle City - PyGame")
        self.clock = pygame.time.Clock()
        
        # Создаем шрифт
        self.font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 24)
        
        self.score = 0
        self.player_lives = 3
        self.game_over = False
        self.game_won = False
        
        self.player = None
        self.enemies = []
        self.walls = []
        self.player_bullets = []
        self.enemy_bullets = []
        
        self.keys = {
            'w': False,
            'a': False,
            's': False,
            'd': False,
            'space': False
        }
        
        self.init_game()

    def init_game(self):
        self.score = 0
        self.player_lives = 3
        self.game_over = False
        self.game_won = False
        
        # Создаем игрока
        self.player = Tank(12 * TILE_SIZE, 22 * TILE_SIZE, True)
        
        # Создаем врагов
        self.enemies = [
            Tank(3 * TILE_SIZE, 3 * TILE_SIZE),
            Tank(22 * TILE_SIZE, 3 * TILE_SIZE),
            Tank(3 * TILE_SIZE, 22 * TILE_SIZE),
            Tank(22 * TILE_SIZE, 22 * TILE_SIZE)
        ]
        
        self.walls = []
        self.player_bullets = []
        self.enemy_bullets = []
        
        # Границы уровня
        for i in range(26):
            self.walls.append(Wall(i * TILE_SIZE, 0, 'steel'))
            self.walls.append(Wall(i * TILE_SIZE, 25 * TILE_SIZE, 'steel'))
        
        for i in range(1, 25):
            self.walls.append(Wall(0, i * TILE_SIZE, 'steel'))
            self.walls.append(Wall(25 * TILE_SIZE, i * TILE_SIZE, 'steel'))
        
        # Внутренние стены
        wall_positions = [
            # Кирпичные стены в центре
            [10, 5, 'brick'], [11, 5, 'brick'], [12, 5, 'brick'], [13, 5, 'brick'], [14, 5, 'brick'],
            [10, 6, 'brick'], [14, 6, 'brick'],
            [10, 7, 'brick'], [14, 7, 'brick'],
            [10, 8, 'brick'], [11, 8, 'brick'], [12, 8, 'brick'], [13, 8, 'brick'], [14, 8, 'brick'],
            
            # Стальные стены
            [5, 10, 'steel'], [6, 10, 'steel'], [7, 10, 'steel'],
            [5, 11, 'steel'], [7, 11, 'steel'],
            [5, 12, 'steel'], [6, 12, 'steel'], [7, 12, 'steel'],
            
            [18, 10, 'steel'], [19, 10, 'steel'], [20, 10, 'steel'],
            [18, 11, 'steel'], [20, 11, 'steel'],
            [18, 12, 'steel'], [19, 12, 'steel'], [20, 12, 'steel'],
            
            # Лес
            [8, 15, 'forest'], [9, 15, 'forest'], [10, 15, 'forest'], [11, 15, 'forest'],
            [8, 16, 'forest'], [9, 16, 'forest'], [10, 16, 'forest'], [11, 16, 'forest'],
            [8, 17, 'forest'], [9, 17, 'forest'], [10, 17, 'forest'], [11, 17, 'forest'],
            
            # Вода
            [14, 15, 'water'], [15, 15, 'water'], [16, 15, 'water'], [17, 15, 'water'],
            [14, 16, 'water'], [15, 16, 'water'], [16, 16, 'water'], [17, 16, 'water'],
            [14, 17, 'water'], [15, 17, 'water'], [16, 17, 'water'], [17, 17, 'water']
        ]
        
        for pos in wall_positions:
            self.walls.append(Wall(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, pos[2]))
        

    def check_tank_wall_collision(self, tank):
        for wall in self.walls:
            if wall.collides_with_tank(tank):
                return True
        return False

    def check_tank_tank_collision(self, tank, other_tanks):
        for other_tank in other_tanks:
            if other_tank != tank and tank.collides_with(other_tank):
                return True
        return False

    def shoot_bullet(self, shooter, is_player):
        if shooter.direction == 0:  # вверх
            bullet_x = shooter.x + shooter.width // 2 - 3
            bullet_y = shooter.y - 6
        elif shooter.direction == 1:  # вправо
            bullet_x = shooter.x + shooter.width
            bullet_y = shooter.y + shooter.height // 2 - 3
        elif shooter.direction == 2:  # вниз
            bullet_x = shooter.x + shooter.width // 2 - 3
            bullet_y = shooter.y + shooter.height
        else:  # влево
            bullet_x = shooter.x - 6
            bullet_y = shooter.y + shooter.height // 2 - 3
        
        bullet = Bullet(bullet_x, bullet_y, shooter.direction, is_player)
        
        if is_player:
            self.player_bullets.append(bullet)
        else:
            self.enemy_bullets.append(bullet)

    def check_collisions(self):
        # Пули игрока с врагами
        for bullet in self.player_bullets[:]:
            if not bullet.active:
                self.player_bullets.remove(bullet)
                continue
                
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    bullet.active = False
                    self.enemies.remove(enemy)
                    self.score += 100
                    if len(self.enemies) == 0:
                        self.game_won = True
                    break
        
        # Пули врагов с игроком
        for bullet in self.enemy_bullets[:]:
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
                continue
                
            if bullet.collides_with(self.player):
                bullet.active = False
                self.player_lives -= 1
                if self.player_lives <= 0:
                    self.game_over = True
        
        # Пули со стенами
        all_bullets = self.player_bullets + self.enemy_bullets
        for bullet in all_bullets[:]:
            if not bullet.active:
                if bullet in self.player_bullets:
                    self.player_bullets.remove(bullet)
                else:
                    self.enemy_bullets.remove(bullet)
                continue
                
            for wall in self.walls[:]:
                if wall.collides_with_bullet(bullet):
                    bullet.active = False
                    if wall.type == 'brick':
                        self.walls.remove(wall)
                    break

    def update_enemies(self):
        for enemy in self.enemies:
            old_x, old_y = enemy.move()
            
            collided = (self.check_tank_wall_collision(enemy) or 
                       self.check_tank_tank_collision(enemy, self.enemies) or 
                       enemy.collides_with(self.player))
            
            if collided:
                enemy.x, enemy.y = old_x, old_y
                enemy.direction = random.randint(0, 3)
            else:
                if random.random() < 0.01:
                    enemy.direction = random.randint(0, 3)
            
            if random.random() < 0.01:
                self.shoot_bullet(enemy, False)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.keys['w'] = True
                    self.player.direction = 0
                elif event.key == pygame.K_a:
                    self.keys['a'] = True
                    self.player.direction = 3
                elif event.key == pygame.K_s:
                    self.keys['s'] = True
                    self.player.direction = 2
                elif event.key == pygame.K_d:
                    self.keys['d'] = True
                    self.player.direction = 1
                elif event.key == pygame.K_SPACE:
                    if not self.keys['space'] and not self.game_over and not self.game_won:
                        self.keys['space'] = True
                        self.shoot_bullet(self.player, True)
                elif event.key == pygame.K_r:
                    self.init_game()
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.keys['w'] = False
                elif event.key == pygame.K_a:
                    self.keys['a'] = False
                elif event.key == pygame.K_s:
                    self.keys['s'] = False
                elif event.key == pygame.K_d:
                    self.keys['d'] = False
                elif event.key == pygame.K_SPACE:
                    self.keys['space'] = False
        
        return True

    def update(self):
        if self.game_over or self.game_won:
            return
        
        # Движение игрока
        if any([self.keys['w'], self.keys['a'], self.keys['s'], self.keys['d']]):
            old_x, old_y = self.player.move()
            
            if (self.check_tank_wall_collision(self.player) or 
                self.check_tank_tank_collision(self.player, self.enemies)):
                self.player.x, self.player.y = old_x, old_y
        
        # Обновление врагов
        self.update_enemies()
        
        # Обновление пуль
        for bullet in self.player_bullets:
            bullet.update()
        for bullet in self.enemy_bullets:
            bullet.update()
        
        # Проверка столкновений
        self.check_collisions()

    def draw(self):
        # Очистка экрана
        self.screen.fill(BLACK)
        
        # Отрисовка игрового поля
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        game_surface.fill(BLACK)
        
        # Отрисовка стен
        for wall in self.walls:
            wall.draw(game_surface)
        
        # Отрисовка пуль
        for bullet in self.player_bullets:
            if bullet.active:
                bullet.draw(game_surface)
        for bullet in self.enemy_bullets:
            if bullet.active:
                bullet.draw(game_surface)
        
        # Отрисовка танков
        self.player.draw(game_surface)
        for enemy in self.enemies:
            enemy.draw(game_surface)
        
        # Отображаем игровое поле на основном экране
        self.screen.blit(game_surface, (0, 50))
        
        # Отрисовка интерфейса
        pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, 50))
        
        # Счет и жизни
        score_text = self.font.render(f'Очки: {self.score}', True, WHITE)
        lives_text = self.font.render(f'Жизни: {self.player_lives}', True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        
        # Управление
        controls_text = self.small_font.render('Управление: WASD - движение, ПРОБЕЛ - стрельба, R - перезапуск', True, WHITE)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, GAME_HEIGHT + 55))
        
        # Сообщения о конце игры
        if self.game_over:
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 50))
            
            game_over_text = self.font.render('ИГРА ОКОНЧЕНА', True, RED)
            score_text = self.font.render(f'Счет: {self.score}', True, WHITE)
            restart_text = self.small_font.render('Нажми R для перезапуска', True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, GAME_HEIGHT // 2 - 20 + 50))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, GAME_HEIGHT // 2 + 20 + 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, GAME_HEIGHT // 2 + 60 + 50))
        
        elif self.game_won:
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 50))
            
            win_text = self.font.render('ПОБЕДА!', True, GREEN)
            score_text = self.font.render(f'Счет: {self.score}', True, WHITE)
            restart_text = self.small_font.render('Нажми R для перезапуска', True, WHITE)
            
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, GAME_HEIGHT // 2 - 20 + 50))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, GAME_HEIGHT // 2 + 20 + 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, GAME_HEIGHT // 2 + 60 + 50))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    # Создаем папку assets если её нет
    if not os.path.exists('assets'):
        os.makedirs('assets')
        print("Создана папка assets. Добавьте туда файлы: tank.png, brick.png, steel.png, forest.png, water.png")
        print("Игра будет использовать fallback-отрисовку")
    
    game = Game()
    game.run()
import pygame
import math

class Player:
    def __init__(self, x, y):
        # Загрузка спрайт-листа персонажа
        self.sprite_sheet = pygame.image.load("image/player_sprites.png").convert_alpha()
        
        # Размеры кадра персонажа
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height() // 4

        # Масштабированные размеры (увеличиваем в 2 раза)
        self.scaled_width = self.frame_width * 2
        self.scaled_height = self.frame_height * 2

        # Словарь для хранения кадров анимации персонажа
        self.frames = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }

        # Извлечение кадров из спрайт-листа персонажа
        directions = ["down", "up", "left", "right"]
        for row, direction in enumerate(directions):
            for col in range(4):
                frame = self.sprite_sheet.subsurface((col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
                self.frames[direction].append(scaled_frame)

        # Отображение направлений для коррекции анимаций
        self.direction_mapping = {
            "up": "right",
            "left": "up",
            "right": "left",
            "down": "down"
        }

        # Начальные параметры
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.2
        self.frame_timer = 0
        self.rect = self.frames["down"][0].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.moving = False

        # Характеристики игрока
        self.health = 100  # Здоровье
        self.max_health = 100
        self.attack_damage = 10  # Урон от атаки

        # Загрузка и разделение спрайт-листа HP-бара //////////////
        self.hp_bar_sheet = pygame.image.load("image/hp_bar.png").convert_alpha()
        self.hp_frame_count = 5  # 5 кадров в спрайт-листе
        self.hp_frame_height = self.hp_bar_sheet.get_height() // self.hp_frame_count  # Вертикальное расположение
        self.hp_frame_width = self.hp_bar_sheet.get_width()
        self.hp_frames = []
    
        # Масштабируем HP-бар (увеличиваем размер, например, ширина 200 пикселей)
        hp_bar_scaled_width = 200  # Увеличили с 100 до 200
        hp_bar_scaled_height = int(self.hp_frame_height * (hp_bar_scaled_width / self.hp_frame_width))  # Пропорционально
    
        for i in range(self.hp_frame_count):
            frame = self.hp_bar_sheet.subsurface((0, i * self.hp_frame_height, self.hp_frame_width, self.hp_frame_height))
            scaled_frame = pygame.transform.scale(frame, (hp_bar_scaled_width, hp_bar_scaled_height))
            self.hp_frames.append(scaled_frame)
    
        # Фиксированная позиция HP-бара (слева сверху)
        self.hp_bar_x = 15  # Отступ от левого края
        self.hp_bar_y = 15  # Отступ от верхнего края

        # Параметры атаки
        self.attack_cooldown = 0  # Счётчик перезарядки атаки
        self.attack_cooldown_time = 30  # Перезарядка атаки (0.5 секунды при 60 FPS)
        self.attack_radius = 50  # Радиус атаки
        self.attacking = False  # Флаг атаки
        self.has_damaged = False  # Флаг, был ли нанесён урон в текущей атаке
        self.attack_frame = 0  # Текущий кадр анимации атаки
        self.attack_frames = []  # Список кадров анимации атаки
        self.attack_animation_speed = 0.3  # Скорость анимации атаки
        self.attack_frame_timer = 0  # Таймер для анимации атаки

        # Параметры рывка
        self.dashing = False  # Флаг рывка
        self.dash_speed = 5*3  # Скорость рывка (в n*5 раза быстрее обычной)
        self.dash_distance = 150  # Дистанция рывка в пикселях
        self.dash_duration = 10  # Длительность рывка в кадрах (примерно 0.17 сек при 60 FPS)
        self.dash_animation_speed = 0.4
        self.dash_timer = 0  # Текущий таймер рывка
        self.dash_cooldown = 0  # Перезарядка рывка
        self.dash_cooldown_time = 60  # Перезарядка рывка (1 секунда при 60 FPS)
        self.dash_start_x = 0  # Начальная позиция X для рывка
        self.dash_start_y = 0  # Начальная позиция Y для рывка

        # Загрузка и разделение спрайт-листа атаки
        try:
            attack_sprite_sheet = pygame.image.load("image/attack_sprite.png").convert_alpha()
            attack_frame_width = attack_sprite_sheet.get_width() // 6  # 6 кадров в спрайт-листе
            attack_frame_height = attack_sprite_sheet.get_height()
            for i in range(6):
                frame = attack_sprite_sheet.subsurface((i * attack_frame_width, 0, attack_frame_width, attack_frame_height))
                scaled_frame = pygame.transform.scale(frame, (self.attack_radius * 2, self.attack_radius * 2))
                self.attack_frames.append(scaled_frame)
        except FileNotFoundError:
            # Создаём временный спрайт для отладки (красный круг)
            for i in range(6):
                temp_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (255, 0, 0, 128), (self.attack_radius, self.attack_radius), self.attack_radius)
                self.attack_frames.append(temp_surface)

    def move(self, keys):
        self.moving = False
        dx, dy = 0, 0  # Изменения по осям X и Y

        if not self.dashing: # Если не в рывке
            # Проверяем нажатия клавиш
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= self.speed
                self.moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += self.speed
                self.moving = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= self.speed
                self.moving = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += self.speed
                self.moving = True

        # Если есть движение по обеим осям (диагональ), нормализуем скорость
        if dx != 0 and dy != 0:
            length = math.sqrt(dx**2 + dy**2)
            dx = (dx / length) * self.speed
            dy = (dy / length) * self.speed

        # Применяем движение
        self.rect.x += dx
        self.rect.y += dy

        # Определяем направление для анимации
        if dx > 0:
            if dy > 0:
                self.current_direction = "down"  # Вправо-вниз
            elif dy < 0:
                self.current_direction = "up"  # Вправо-вверх
            else:
                self.current_direction = "right"  # Только вправо
        elif dx < 0:
            if dy > 0:
                self.current_direction = "down"  # Влево-вниз
            elif dy < 0:
                self.current_direction = "up"  # Влево-вверх
            else:
                self.current_direction = "left"  # Только влево
        elif dy > 0:
            self.current_direction = "down"  # Только вниз
        elif dy < 0:
            self.current_direction = "up"  # Только вверх

        # Ограничение движения в пределах экрана
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        # Обновление анимации с учетом рывка
        if self.moving or self.dashing:
            current_speed = self.dash_animation_speed if self.dashing else self.animation_speed
            self.frame_timer += current_speed
            if self.frame_timer >= 1:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
        else:
            self.current_frame = 0
    
    def dash(self):
        # Рывок возможен только если нет атаки, рывка и перезарядка завершена
        if not self.attacking and not self.dashing and self.dash_cooldown <= 0:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown = self.dash_cooldown_time
            self.dash_start_x = self.rect.x
            self.dash_start_y = self.rect.y
            return True
        return False

    def attack(self):
        # Атака возможна только если нет текущей анимации атаки и перезарядка завершена
        if not self.dash and not self.attacking and self.attack_cooldown <= 0:
            self.attacking = True
            self.has_damaged = False  # Сбрасываем флаг урона
            self.attack_cooldown = self.attack_cooldown_time
            self.attack_frame = 0  # Сбрасываем кадр анимации
            self.attack_frame_timer = 0
            return True  # Указываем, что атака произошла
        return False

    def get_attack_rect(self):
        # Определяем область атаки
        attack_rect = pygame.Rect(0, 0, self.attack_radius * 2, self.attack_radius * 2)
        attack_rect.center = self.rect.center
        if self.current_direction == "up":
            attack_rect.y -= self.rect.height // 2
        elif self.current_direction == "down":
            attack_rect.y += self.rect.height // 2
        elif self.current_direction == "left":
            attack_rect.x -= self.rect.width // 2
        elif self.current_direction == "right":
            attack_rect.x += self.rect.width // 2
        return attack_rect
    def take_damage(self, damage):
    
        if not self.dashing:  # Нельзя получить урон во время рывка (неуязвимость)
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                # Здесь можно добавить логику смерти игрока
                print("Игрок умер!")
            return True  # Урон успешно нанесён
        return False  # Урон не нанесён (игрок в рывке)
        
    # Получение урона
    def take_damage(self, damage):
        if not self.dashing:  # Неуязвимость во время рывка
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                print("Игрок умер!")
            elif self.health > self.max_health:
                self.health = self.max_health  # Ограничение сверху
            return True
        return False

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Обновление анимации атаки
        if self.attacking:
            self.attack_frame_timer += self.attack_animation_speed
            if self.attack_frame_timer >= 1:
                self.attack_frame_timer = 0
                self.attack_frame += 1
                if self.attack_frame >= len(self.attack_frames):
                    self.attack_frame = 0
                    self.attacking = False  # Завершаем атаку после полной анимации
                    self.has_damaged = False  # Сбрасываем флаг урона

        #Обновление рывка
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
            else:
                # Вычисляем прогресс рывка (от 1 до 0)
                progress = self.dash_timer / self.dash_duration
                distance_left = self.dash_distance * (1 - progress)
                
                # Перемещаем персонажа в зависимости от направления
                if self.current_direction == "up":
                    self.rect.y = self.dash_start_y - distance_left
                elif self.current_direction == "down":
                    self.rect.y = self.dash_start_y + distance_left
                elif self.current_direction == "left":
                    self.rect.x = self.dash_start_x - distance_left
                elif self.current_direction == "right":
                    self.rect.x = self.dash_start_x + distance_left

        # Обновление перезарядки рывка
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1


    def draw(self, screen, camera_x=0, camera_y=0):
        mapped_direction = self.direction_mapping[self.current_direction]
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        draw_rect.y -= camera_y

        # Отрисовка персонажа
        current_sprite = self.frames[mapped_direction][self.current_frame]
        if self.dashing:
            # Увеличиваем размер персонажа во время рывка
            dash_scale = 0.9  # Увеличение на 20%
            dash_sprite = pygame.transform.scale(current_sprite, 
                (int(self.scaled_width * dash_scale), int(self.scaled_height * dash_scale)))
            dash_sprite.fill((255, 0, 0, 200), special_flags=pygame.BLEND_RGBA_MULT)  # Легкий голубой оттенок
            dash_rect = dash_sprite.get_rect(center=draw_rect.center)
            screen.blit(dash_sprite, dash_rect)
        else:
            screen.blit(current_sprite, draw_rect)
        
        # Отрисовка HP-бара (фиксированная позиция)
        health_percent = self.health / self.max_health  # Процент оставшегося здоровья
        frame_index = max(0, min(self.hp_frame_count - 1, int((1 - health_percent) * self.hp_frame_count)))  # Выбираем кадр
        hp_bar_sprite = self.hp_frames[frame_index]
        screen.blit(hp_bar_sprite, (self.hp_bar_x, self.hp_bar_y))  # Фиксированные координаты

        # Отрисовка атаки
        if self.attacking:
            attack_rect = self.get_attack_rect()
            attack_rect.x -= camera_x
            attack_rect.y -= camera_y

            # Поворачиваем спрайт атаки в зависимости от направления
            attack_sprite = self.attack_frames[self.attack_frame]
            if self.current_direction == "up":
                attack_sprite = pygame.transform.rotate(attack_sprite, 90)
            elif self.current_direction == "down":
                attack_sprite = pygame.transform.rotate(attack_sprite, 270)
            elif self.current_direction == "left":
                attack_sprite = pygame.transform.rotate(attack_sprite, 180)
            # Для "right" поворот не нужен, так как спрайт уже ориентирован вправо

            # Корректируем позицию после поворота (центрируем)
            sprite_rect = attack_sprite.get_rect(center=(attack_rect.centerx, attack_rect.centery))
            screen.blit(attack_sprite, (sprite_rect.x, sprite_rect.y))
        
        # Анимация рывка: несколько следов
        if self.dashing:
            for i in range(2):  # Два следа
                trail_sprite = current_sprite.copy()
                trail_sprite.set_alpha(100 - i * 40)  # Уменьшаем прозрачность для дальних следов
                trail_rect = draw_rect.copy()
                offset = 15 * (i + 1)  # Увеличиваем смещение для каждого следа
                if self.current_direction == "up":
                    trail_rect.y += offset
                elif self.current_direction == "down":
                    trail_rect.y -= offset
                elif self.current_direction == "left":
                    trail_rect.x += offset
                elif self.current_direction == "right":
                    trail_rect.x -= offset
                screen.blit(trail_sprite, trail_rect)
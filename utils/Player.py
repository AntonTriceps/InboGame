# utils/Player.py
import pygame

class Player:
    def __init__(self, x, y, map_width, map_height, inventory=None):
        # Загрузка спрайта
        self.sprite_path = "data/image/Player/PlayerMain_sprites.png"
        try:
            self.sprite_sheet = pygame.image.load(self.sprite_path).convert_alpha()
        except Exception as e:
            print(f"Ошибка загрузки спрайта игрока: {e}")
            self.sprite_sheet = pygame.Surface((24, 32))  # Заглушка на случай ошибки

        # Размеры кадра персонажа (предполагаем 4 кадра в ширину и 4 в высоту спрайт-листа)
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height() // 4

        # Масштабированные размеры (увеличиваем в 2 раза)
        self.scaled_width = self.frame_width * 2
        self.scaled_height = self.frame_height * 2

        # Словарь для хранения кадров анимации персонажа
        self.frames = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }

        # Извлечение кадров из спрайт-листа персонажа
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(4):
                frame = self.sprite_sheet.subsurface((col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
                self.frames[direction].append(scaled_frame)

        # Начальные параметры
        self.direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.2
        self.frame_timer = 0
        self.image = self.frames["down"][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.moving = False

        # Характеристики игрока
        self.health = 100  # Здоровье
        self.max_health = 100
        
        # Параметры атаки
        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 15  # Длительность атаки в кадрах (0.25 сек при 60 FPS)
        self.attack_cooldown = 0
        self.attack_cooldown_time = 30  # Перезарядка атаки (0.5 сек при 60 FPS)
        self.inventory = inventory  # Ссылка на инвентарь для доступа к мечу

        # Загрузка и разделение спрайт-листа HP-бара //////////////
        self.hp_bar_sheet = pygame.image.load("data/image/UI/hp_bar.png").convert_alpha()
        self.hp_frame_count = 5  # 5 кадров в спрайт-листе
        self.hp_frame_height = self.hp_bar_sheet.get_height() // self.hp_frame_count  # Вертикальное расположение
        self.hp_frame_width = self.hp_bar_sheet.get_width()
        self.hp_frames = []
    
        # Масштабируем HP-бар (увеличиваем размер, например, ширина 200 пикселей)
        hp_bar_scaled_width = 230  # Увеличили с 100 до 200
        hp_bar_scaled_height = int(self.hp_frame_height * (hp_bar_scaled_width / self.hp_frame_width))  # Пропорционально
    
        for i in range(self.hp_frame_count):
            frame = self.hp_bar_sheet.subsurface((0, i * self.hp_frame_height, self.hp_frame_width, self.hp_frame_height))
            scaled_frame = pygame.transform.scale(frame, (hp_bar_scaled_width, hp_bar_scaled_height))
            self.hp_frames.append(scaled_frame)
    
        # Фиксированная позиция HP-бара (слева сверху)
        self.hp_bar_x = 20  # Отступ от левого края
        self.hp_bar_y = 20  # Отступ от верхнего края

        # Параметры рывка
        self.dashing = False  # Флаг рывка
        self.dash_speed = 5*3  # Скорость рывка (в n*5 раза быстрее обычной)
        self.dash_distance = 150  # Дистанция рывка в пикселях
        self.dash_duration = 10  # Длительность рывка в кадрах 0.34
        self.dash_animation_speed = 0.4
        self.dash_count = 2  # Количество доступных рывков (2 подряд)
        self.max_dash_count = 2  # Максимальное количество рывков
        self.dash_timer = 0  # Текущий таймер рывка
        self.dash_cooldown = 0  # Перезарядка рывка
        self.dash_delay_time = 15  # Задержка в кадрах (0.17 сек при 60 FPS)
        self.dash_delay = 0
        self.dash_cooldown_time = 60  # Перезарядка рывка (1 секунда при 60 FPS)
        self.dash_start_x = 0  # Начальная позиция X для рывка
        self.dash_start_y = 0  # Начальная позиция Y для рывка

        # Размеры карты
        self.map_width = map_width
        self.map_height = map_height

    def update(self):
        self.moving = False
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if not self.dashing:
            # Движение по горизонтали (Стрелки и WASD)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= self.speed
                self.direction = "left"
                self.moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += self.speed
                self.direction = "right"
                self.moving = True
            
            if (keys[pygame.K_LSHIFT]) and not self.dashing and self.dash_delay <= 0:
                self.dash()
            if keys[pygame.K_SPACE] and self.attack_cooldown <= 0:  # Атака по пробелу
                self.attack()

            # Движение по вертикали (Стрелки и WASD)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= self.speed
                self.direction = "up"
                self.moving = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += self.speed
                self.direction = "down"
                self.moving = True

        # Расчет новых координат, но пока не применяем их
        new_rect_x = self.rect.x + dx
        new_rect_y = self.rect.y + dy

        # Проверка границ карты перед обновлением позиции
        if new_rect_x >= 0 and new_rect_x <= self.map_width - self.rect.width:
            self.rect.x = new_rect_x
        if new_rect_y >= 0 and new_rect_y <= self.map_height - self.rect.height:
            self.rect.y = new_rect_y

        # Анимация
        if self.moving:
            self.frame_timer += self.animation_speed
            if self.frame_timer >= 1:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
            self.image = self.frames[self.direction][self.current_frame]
        else:
            self.current_frame = 0
            self.image = self.frames[self.direction][self.current_frame]

        # Обновление атаки
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False

        #Обновление рывка
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
            else:
                # Вычисляем прогресс рывка (от 1 до 0)
                progress = self.dash_timer / self.dash_duration
                distance_left = self.dash_distance * (1 - progress)
                
                if self.direction == "up":
                    new_y = self.dash_start_y - distance_left
                    self.rect.y = max(0, min(new_y, self.map_height - self.rect.height))
                elif self.direction == "down":
                    new_y = self.dash_start_y + distance_left
                    self.rect.y = max(0, min(new_y, self.map_height - self.rect.height))
                elif self.direction == "left":
                    new_x = self.dash_start_x - distance_left
                    self.rect.x = max(0, min(new_x, self.map_width - self.rect.width))
                elif self.direction == "right":
                    new_x = self.dash_start_x + distance_left
                    self.rect.x = max(0, min(new_x, self.map_width - self.rect.width))
        # Обновление перезарядки между рывками подряд
        if self.dash_delay > 0:
            self.dash_delay -= 1
        # Обновление перезарядки рывков
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            if self.dash_cooldown <= 0 and self.dash_count < self.max_dash_count:
                # Восстанавливаем все рывки после перезарядки
                self.dash_count = self.max_dash_count
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1  # Перенесли сюда

    def dash(self):
        # Рывок возможен, если есть доступные рывки и нет текущего рывка
        if not self.dashing and self.dash_count > 0:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_count -= 1  # Уменьшаем количество доступных рывков
            if self.dash_count == 0:
                self.dash_cooldown = self.dash_cooldown_time  # Запускаем перезарядку после второго рывка
            if self.dash_count > 0:
                self.dash_delay = self.dash_delay_time
            self.dash_start_x = self.rect.x
            self.dash_start_y = self.rect.y
            return True
        return False

    def attack(self):
        if not self.attacking and self.attack_cooldown <= 0 and self.inventory and self.inventory.items:
            self.attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown = self.attack_cooldown_time
            # Начальный и конечный угол для анимации взмаха (в градусах)
            self.start_angle = 60  # Начальный угол (сверху)
            self.end_angle = -60  # Конечный угол (снизу)
            return True
        return False


    def draw(self, surface):
        current_sprite = self.frames[self.direction][self.current_frame]

        # Отрисовка HP-бара (фиксированная позиция)
        health_percent = self.health / self.max_health  # Процент оставшегося здоровья
        frame_index = max(0, min(self.hp_frame_count - 1, int((1 - health_percent) * self.hp_frame_count)))  # Выбираем кадр
        hp_bar_sprite = self.hp_frames[frame_index]
        surface.blit(hp_bar_sprite, (self.hp_bar_x, self.hp_bar_y))  # Фиксированные координаты

        if self.dashing:
           for i in range(4):  # Четыре следа
            trail_sprite = current_sprite.copy()
            trail_sprite.set_alpha(100 - i * 20)  # Уменьшаем прозрачность для дальних следов
            # Накладываем цвет на след (например, синий: 0, 0, 255)
            trail_sprite.fill((128, 0, 128, 200), special_flags=pygame.BLEND_RGBA_MULT)
            trail_rect = self.rect.copy()
            offset = 12 * (i + 1)  # Увеличиваем смещение для каждого следа
            if self.direction == "up":
                trail_rect.y += offset
            elif self.direction == "down":
                trail_rect.y -= offset
            elif self.direction == "left":
                trail_rect.x += offset
            elif self.direction == "right":
                trail_rect.x -= offset
            surface.blit(trail_sprite, trail_rect)

            # Увеличиваем размер персонажа во время рывка
            dash_scale = 0.9  # Уменьшение модели
            dash_sprite = pygame.transform.scale(
                current_sprite,
                (int(self.scaled_width * dash_scale), int(self.scaled_height * dash_scale))
            )
            dash_sprite.fill((255, 0, 0, 200), special_flags=pygame.BLEND_RGBA_MULT)  # Красный оттенок для рывка
            dash_rect = dash_sprite.get_rect(center=self.rect.center)
            surface.blit(dash_sprite, dash_rect)
        else:
            surface.blit(current_sprite, self.rect)

        # Отрисовка атаки мечом с анимацией взмаха
        if self.attacking and self.inventory and self.inventory.items:
            sword = self.inventory.items[0]
            sword_sprite = sword.sprite
            sword_scale = 2.0  # Коэффициент увеличения
            scaled_sword = pygame.transform.scale(
                sword_sprite,
                (int(sword_sprite.get_width() * sword_scale), int(sword_sprite.get_height() * sword_scale))
            )

            # Вычисление прогресса анимации (от 1 до 0)
            attack_progress = self.attack_timer / self.attack_duration
            # Интерполяция угла от начального к конечному
            current_angle = self.start_angle + (self.end_angle - self.start_angle) * (1 - attack_progress)

            # Поворот спрайта меча
            rotated_sword = pygame.transform.rotate(scaled_sword, current_angle)
            sword_rect = rotated_sword.get_rect()

            # Позиционирование меча относительно игрока
            sword_offset = 40
            if self.direction == "up":
                sword_pos = (self.rect.centerx - sword_rect.width // 2, self.rect.top - sword_offset)
            elif self.direction == "down":
                sword_pos = (self.rect.centerx - sword_rect.width // 2, self.rect.bottom + sword_offset - sword_rect.height)
            elif self.direction == "left":
                sword_pos = (self.rect.left - sword_offset, self.rect.centery - sword_rect.height // 2)
            elif self.direction == "right":
                sword_pos = (self.rect.right + sword_offset - sword_rect.width, self.rect.centery - sword_rect.height // 2)

            # Корректировка позиции для учета поворота
            sword_rect.topleft = sword_pos
            surface.blit(rotated_sword, sword_rect)

    def set_direction(self, direction):
        """Установить направление игрока."""
        self.direction = direction
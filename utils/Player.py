# utils/Player.py
import pygame

class Player:
    def __init__(self, x, y, map_width, map_height):
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

        # Размеры карты
        self.map_width = map_width
        self.map_height = map_height

    def update(self):
        self.moving = False
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Движение по горизонтали (Стрелки и WASD)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.direction = "left"
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.direction = "right"
            self.moving = True

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_direction(self, direction):
        """Установить направление игрока."""
        self.direction = direction
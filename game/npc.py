import pygame
import random

class NPC:
    def __init__(self, x, y, level_width, level_height, level_name):
        # Загрузка спрайт-листа в зависимости от уровня
        sprite_path = "/Users/anton/Downloads/InboGame/image/location/{level_name}_npc_sprites.png"
        try:
            self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        except FileNotFoundError:
            # Если файл для уровня не найден, используем дефолтный спрайт
            self.sprite_sheet = pygame.image.load("image/npc_sprites.png").convert_alpha()
        
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height() // 4

        # Масштабированные размеры (увеличиваем в 2 раза)
        self.scaled_width = self.frame_width * 2
        self.scaled_height = self.frame_height * 2

        self.frames = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }

        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(4):
                frame = self.sprite_sheet.subsurface((col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
                self.frames[direction].append(scaled_frame)

        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.1
        self.frame_timer = 0
        self.rect = self.frames["down"][0].get_rect()
        self.rect.x = x
        self.rect.y = y

        # Параметры движения
        self.speed = 2
        self.steps_left = 0
        self.pause_timer = 0
        self.moving = False
        self.level_width = level_width
        self.level_height = level_height

        # Характеристики NPC
        self.health = 50  # Здоровье NPC (5 ударов по 10 урона)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # NPC "умирает"
        return False

    def update(self, collidables, dialogue_active, player_pos):
        # Обновление анимации
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % 4

        # Если диалог активен, NPC не двигается и смотрит на игрока
        if dialogue_active:
            self.moving = False
            self.current_frame = 0  # Сбрасываем анимацию
            # Определяем направление взгляда на игрока
            dx = player_pos[0] - self.rect.x
            dy = player_pos[1] - self.rect.y
            if abs(dx) > abs(dy):
                self.current_direction = "right" if dx > 0 else "left"
            else:
                self.current_direction = "down" if dy > 0 else "up"
            return

        # Логика движения
        if self.pause_timer > 0:
            self.pause_timer -= 1
            self.moving = False
            self.current_frame = 0
        elif self.steps_left > 0:
            self.moving = True
            old_x, old_y = self.rect.x, self.rect.y

            if self.current_direction == "up":
                self.rect.y -= self.speed
            elif self.current_direction == "down":
                self.rect.y += self.speed
            elif self.current_direction == "left":
                self.rect.x -= self.speed
            elif self.current_direction == "right":
                self.rect.x += self.speed

            if self.rect.x < 0:
                self.rect.x = 0
                self.steps_left = 0
            elif self.rect.x > self.level_width - self.rect.width:
                self.rect.x = self.level_width - self.rect.width
                self.steps_left = 0
            if self.rect.y < 0:
                self.rect.y = 0
                self.steps_left = 0
            elif self.rect.y > self.level_height - self.rect.height:
                self.rect.y = self.level_height - self.rect.height
                self.steps_left = 0

            for collidable in collidables:
                if self.rect.colliderect(collidable):
                    self.rect.x, self.rect.y = old_x, old_y
                    self.steps_left = 0
                    break

            self.steps_left -= 1
            if self.steps_left == 0:
                self.pause_timer = 300  # 5 секунд
        else:
            self.steps_left = 100  # 100 шагов
            self.current_direction = random.choice(["up", "down", "left", "right"])

    def draw(self, screen):
        screen.blit(self.frames[self.current_direction][self.current_frame], self.rect)
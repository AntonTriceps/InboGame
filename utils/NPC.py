# utils/NPC.py
import pygame
import random
import json

class NPC:
    def __init__(self, x, y, map_width, map_height, dialogue_file_path="data/dialogues/dialogues_level1.json", dialogue_id="npc_dialogue_1"):
        # Загрузка спрайта NPC
        self.sprite_path = "data/image/NPC/NPC_level1_sprites.png"
        try:
            self.sprite_sheet = pygame.image.load(self.sprite_path).convert_alpha()
        except Exception as e:
            print(f"Ошибка загрузки спрайта NPC: {e}")
            self.sprite_sheet = pygame.Surface((24, 32))

        # Размеры кадра
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height() // 4

        # Масштабированные размеры
        self.scaled_width = self.frame_width * 2
        self.scaled_height = self.frame_height * 2

        # Анимации
        self.frames = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(4):
                frame = self.sprite_sheet.subsurface((col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, (self.scaled_width, self.scaled_height))
                self.frames[direction].append(scaled_frame)

        # Начальные параметры
        self.direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.frame_timer = 0
        self.image = self.frames["down"][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1
        self.moving = False

        # Размеры карты
        self.map_width = map_width
        self.map_height = map_height

        # Параметры для случайного движения по карте
        self.movement_state = "idle"
        self.idle_duration = 1500
        self.move_duration = 2000
        self.timer = pygame.time.get_ticks()
        self.current_move_direction = "down"

        # Параметры для взаимодействия
        self.interaction_distance = 70
        self.talking_to_npc = False

        # Загрузка диалогов
        self.dialogue_file_path = dialogue_file_path
        self.dialogue_id = dialogue_id
        self.dialogues_data = self.load_dialogues(dialogue_file_path)
        self.current_dialogue_node_id = "start"
        self.current_dialogue = None

        # Параметры для плавающего текста
        self.floating_text = "Эй, путник! Подойди ко мне!"
        self.show_floating_text = False
        self.floating_text_interval = 5000
        self.floating_text_duration = 2000
        self.floating_text_timer = pygame.time.get_ticks()
        self.floating_text_visible_until = 0

        # Шрифт для текста
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)

        # Для плавного текста
        self.dialogue_text = ""
        self.displayed_text = ""
        self.text_index = 0
        self.text_speed = 3
        self.text_timer = 0

    def load_dialogues(self, file_path):
        """Загрузка диалогов из JSON файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл диалогов не найден: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка декодирования JSON в файле: {file_path}")
            return {}

    def get_frame(self, x, y):
        """Получение кадра из спрайт-листа."""
        frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (x * self.frame_width, y * self.frame_height, self.frame_width, self.frame_height))
        return frame

    def update(self):
        """Обновление состояния NPC."""
        if self.talking_to_npc:
            self.moving = False
            return
        else:
            self.moving = False
            dx = 0
            dy = 0
            current_time = pygame.time.get_ticks()

            if self.movement_state == "idle":
                if current_time - self.timer >= self.idle_duration:
                    self.movement_state = "moving"
                    self.timer = current_time
                    possible_directions = ["up", "down", "left", "right"]
                    self.current_move_direction = random.choice(possible_directions)
            elif self.movement_state == "moving":
                if current_time - self.timer >= self.move_duration:
                    self.movement_state = "idle"
                    self.timer = current_time
                    self.idle_duration = random.randint(1000, 2500)

                if self.current_move_direction == "left":
                    dx -= self.speed
                    self.direction = "left"
                    self.moving = True
                elif self.current_move_direction == "right":
                    dx += self.speed
                    self.direction = "right"
                    self.moving = True
                elif self.current_move_direction == "up":
                    dy -= self.speed
                    self.direction = "up"
                    self.moving = True
                elif self.current_move_direction == "down":
                    dy += self.speed
                    self.direction = "down"
                    self.moving = True

            new_rect_x = self.rect.x + dx
            new_rect_y = self.rect.y + dy

            # Проверка границ карты
            if new_rect_x < 0:
                new_rect_x = 0
                self.movement_state = "idle"
            elif new_rect_x > self.map_width - self.rect.width:
                new_rect_x = self.map_width - self.rect.width
                self.movement_state = "idle"
            if new_rect_y < 0:
                new_rect_y = 0
                self.movement_state = "idle"
            elif new_rect_y > self.map_height - self.rect.height:
                new_rect_y = self.map_height - self.rect.height
                self.movement_state = "idle"

            self.rect.x = new_rect_x
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

        # Обновление плавающего текста
        current_time_float_text = pygame.time.get_ticks()
        if current_time_float_text - self.floating_text_timer >= self.floating_text_interval:
            self.show_floating_text = True
            self.floating_text_visible_until = current_time_float_text + self.floating_text_duration
            self.floating_text_timer = current_time_float_text
        if current_time_float_text > self.floating_text_visible_until:
            self.show_floating_text = False

    def draw(self, surface):
        """Отрисовка NPC и интерфейса диалога."""
        surface.blit(self.image, self.rect)
        if self.talking_to_npc:
            self.draw_dialogue_ui(surface)
        else:
            self.draw_floating_text(surface)

    def draw_floating_text(self, surface):
        """Отрисовка плавающего текста над NPC с ограничением в пределах карты."""
        if self.show_floating_text:
            text_surface = self.font.render(self.floating_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top - 10))

            # Ограничение текста в пределах карты
            if text_rect.left < 0:
                text_rect.left = 0
            if text_rect.right > self.map_width:
                text_rect.right = self.map_width
            if text_rect.top < 0:
                text_rect.top = 0
            if text_rect.bottom > self.map_height:
                text_rect.bottom = self.map_height - (self.rect.top - text_rect.top)  # Сдвигаем текст вверх

            surface.blit(text_surface, text_rect)

    def draw_dialogue_ui(self, surface):
        """Отрисовка интерфейса диалога NPC с динамическим размером окна."""
        if not self.talking_to_npc or not self.current_dialogue:
            return

        current_node = self.current_dialogue.get(self.current_dialogue_node_id)
        if not current_node:
            self.end_dialogue()
            return

        npc_text = current_node.get("npc_text", "...")
        player_options = current_node.get("player_options", [])

        # Обновление текста для плавного отображения
        if self.dialogue_text != npc_text:
            self.dialogue_text = npc_text
            self.displayed_text = ""
            self.text_index = 0
            self.text_timer = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if current_time - self.text_timer > 1000 // (self.text_speed * 60):
            if self.text_index < len(self.dialogue_text):
                self.displayed_text += self.dialogue_text[self.text_index]
                self.text_index += 1
                self.text_timer = current_time

        # Разбиение текста на строки
        text_start_x = 50 + 20  # Отступ от края экрана + внутренний отступ
        max_text_width = surface.get_width() - 100 - 40  # Ширина экрана минус отступы
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            text_surface_test = self.font.render(test_line, True, (255, 255, 255))
            if text_surface_test.get_width() > max_text_width:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line.strip())

        # Подсчёт высоты окна: текст NPC + варианты игрока
        line_height = 25
        padding = 20  # Внутренние отступы сверху и снизу
        npc_lines_height = len(lines) * line_height
        options_height = len(player_options) * line_height
        total_height = npc_lines_height + options_height + padding * 2  # Учитываем отступы

        # Ограничение минимальной и максимальной высоты окна
        min_height = 100
        max_height = surface.get_height() // 2  # Не больше половины экрана
        dialogue_height = max(min_height, min(total_height, max_height))

        # Определение прямоугольника окна диалога
        dialogue_window_rect = pygame.Rect(
            50, surface.get_height() - dialogue_height - 50,
            surface.get_width() - 100, dialogue_height
        )
        pygame.draw.rect(surface, (50, 50, 50), dialogue_window_rect)
        pygame.draw.rect(surface, (255, 255, 255), dialogue_window_rect, 2)

        # Отрисовка текста NPC
        text_start_y = dialogue_window_rect.y + padding
        for i, line in enumerate(lines):
            npc_text_surface = self.font.render(line, True, (255, 255, 255))
            npc_text_rect = npc_text_surface.get_rect(topleft=(text_start_x, text_start_y + i * line_height))
            surface.blit(npc_text_surface, npc_text_rect)

        # Отрисовка вариантов ответа игрока
        option_start_y = text_start_y + npc_lines_height + padding // 2
        for i, option in enumerate(player_options):
            option_text = f"{i+1}. {option['text']}"
            option_surface = self.font.render(option_text, True, (200, 200, 200))
            option_rect = option_surface.get_rect(topleft=(text_start_x, option_start_y + i * line_height))
            surface.blit(option_surface, option_rect)

    def handle_input(self, event):
        """Обработка ввода игрока во время диалога."""
        if not self.talking_to_npc or not self.current_dialogue:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end_dialogue()
            elif event.key == pygame.K_1:
                self.process_player_choice(0)
            elif event.key == pygame.K_2:
                self.process_player_choice(1)
            elif event.key == pygame.K_3:
                self.process_player_choice(2)

    def process_player_choice(self, option_index):
        """Обработка выбора игрока в диалоге."""
        current_node = self.current_dialogue.get(self.current_dialogue_node_id)
        if not current_node:
            return

        player_options = current_node.get("player_options", [])
        if 0 <= option_index < len(player_options):
            selected_option = player_options[option_index]
            next_node_id = selected_option.get("next_node_id")
            if next_node_id:
                self.current_dialogue_node_id = next_node_id
                if next_node_id == "end":
                    self.end_dialogue()
            else:
                print("Ошибка: 'next_node_id' не найден в выбранной опции.")
        else:
            print(f"Неверный индекс опции: {option_index}")

    def start_dialogue(self):
        """Начать разговор с NPC."""
        self.talking_to_npc = True
        self.current_dialogue = self.dialogues_data["dialogues"].get(self.dialogue_id)
        if self.current_dialogue:
            self.current_dialogue_node_id = "start"
            print(f"Начало диалога с NPC: {self.dialogue_id}")
        else:
            print(f"Диалог с ID '{self.dialogue_id}' не найден.")
            self.talking_to_npc = False

    def end_dialogue(self):
        """Завершить разговор с NPC."""
        self.talking_to_npc = False
        self.current_dialogue_node_id = "start"
        self.current_dialogue = None
        print("Конец разговора с NPC.")

    def set_direction(self, direction):
        """Установить направление NPC."""
        self.direction = direction

    def is_close_to_player(self, player_rect):
        """Проверка близости игрока."""
        distance_to_player = pygame.math.Vector2(player_rect.center).distance_to(self.rect.center)
        return distance_to_player <= self.interaction_distance
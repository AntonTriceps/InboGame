import pygame

class Dialogue:
    def __init__(self, messages, font_size=30):
        self.messages = messages
        self.current_message = 0
        self.active = False
        self.font = pygame.font.Font(None, font_size)
        self.choice = None
        self.text_progress = 0  # Прогресс отображения текста
        self.text_speed = 2  # Скорость появления текста (символы за кадр)

    def start(self):
        self.active = True
        self.current_message = 0
        self.choice = None
        self.text_progress = 0

    def next(self):
        if self.current_message < len(self.messages) - 1:
            self.current_message += 1
            self.text_progress = 0
        else:
            self.active = False

    def set_choice(self, choice):
        self.choice = choice
        self.active = False

    def update(self):
        if self.active and self.text_progress < len(self.messages[self.current_message]):
            self.text_progress += self.text_speed
            if self.text_progress > len(self.messages[self.current_message]):
                self.text_progress = len(self.messages[self.current_message])

    def draw(self, screen):
        if not self.active:
            return

        # Отрисовка фона диалогового окна
        dialogue_box = pygame.Rect(50, 400, 700, 150)
        pygame.draw.rect(screen, (0, 0, 0), dialogue_box)
        pygame.draw.rect(screen, (255, 255, 255), dialogue_box, 2)

        # Постепенное отображение текста
        current_text = self.messages[self.current_message][:int(self.text_progress)]
        text = self.font.render(current_text, True, (255, 255, 255))
        screen.blit(text, (60, 410))

        # Отображение выбора, если это последнее сообщение
        if self.current_message == len(self.messages) - 1 and self.choice is None:
            choice_text = self.font.render("1. Да    2. Нет", True, (255, 255, 255))
            screen.blit(choice_text, (60, 450))
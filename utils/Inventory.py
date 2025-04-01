import pygame

class Inventory:
    def __init__(self):
        self.items = []  # Список предметов
        self.active = False  # Открыт ли инвентарь
        self.font = pygame.font.Font(None, 30)

    def add_item(self, item):
        self.items.append(item)

    def toggle(self):
        self.active = not self.active

    def draw(self, screen):
        if not self.active:
            return

        # Отрисовка фона инвентаря
        inventory_box = pygame.Rect(50, 50, 700, 500)
        pygame.draw.rect(screen, (0, 0, 0), inventory_box)  # Чёрный фон
        pygame.draw.rect(screen, (255, 255, 255), inventory_box, 2)  # Белая рамка

        # Отрисовка предметов
        for i, item in enumerate(self.items):
            text = self.font.render(f"{i+1}. {item}", True, (255, 255, 255))
            screen.blit(text, (60, 60 + i * 30))
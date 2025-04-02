import pygame
from utils.Item import Item

class Inventory:
    def __init__(self):
        self.items = []  # Список предметов
        self.active = False  # Открыт ли инвентарь
        self.font = pygame.font.Font(None, 24)

    def add_item(self, item):
        """Добавление предмета в инвентарь."""
        if isinstance(item, Item):  # Проверяем, что добавляем объект Item
            self.items.append(item)
        else:
            print(f"Ошибка: предмет должен быть объектом класса Item, получен {type(item)}")

    def toggle(self):
        self.active = not self.active

    def draw(self, screen):
        if not self.active:
            return

        # Отрисовка фона инвентаря
        inventory_box = pygame.Rect(70, 70, 700, 500)
        pygame.draw.rect(screen, (0, 0, 0), inventory_box)  # Чёрный фон
        pygame.draw.rect(screen, (255, 255, 255), inventory_box, 2)  # Белая рамка

        # Отрисовка предметов
        for i, item in enumerate(self.items):
            # Отрисовка спрайта предмета
            item.draw(screen, 80, 80 + i * 40)  # 40 пикселей между предметами для читаемости
            # Отрисовка названия рядом со спрайтом
            text = self.font.render(f"{i+1}. {item}", True, (255, 255, 255))
            screen.blit(text, (80, 110 + i * 40))  # Смещение текста
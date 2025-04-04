import pygame
from utils.Item import Item

class Inventory:
    def __init__(self):
        self.items = []  # Список предметов
        self.active = False  # Открыт ли инвентарь
        self.font = pygame.font.Font(None, 24)
        # Загрузка спрайта инвентаря
        self.background_path = "data/sprites/inventory/inventory_inactive.png"
        try:
            self.background = pygame.image.load(self.background_path).convert_alpha()
            # Масштабируем фон, если нужно (например, до 700x500, как было в оригинале)
            self.background = pygame.transform.scale(self.background, (700, 500))
        except Exception as e:
            print(f"Ошибка загрузки фона инвентаря: {e}")
            # Заглушка: чёрный прямоугольник на случай ошибки
            self.background = pygame.Surface((700, 500))
            self.background.fill((0, 0, 0))

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
        
        inventory_pos = (130, 70)  # Позиция инвентаря на экране
        screen.blit(self.background, inventory_pos)

        # Отрисовка предметов
        for i, item in enumerate(self.items):
            # Отрисовка спрайта предмета
            item.draw(screen, 160, 190 + i * 40)  # 40 пикселей между предметами для читаемости
            # Отрисовка названия рядом со спрайтом
            text = self.font.render(f"{i+1}. {item}", True, (255, 255, 255))
            screen.blit(text, (80, 110 + i * 40))  # Смещение текста
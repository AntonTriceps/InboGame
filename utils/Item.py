import pygame

class Item:
    def __init__(self, name, sprite_path):
        self.name = name  # Название предмета
    
        self.sprite_path = sprite_path  # Путь к файлу спрайта
        try:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()  # Загрузка спрайта
            # Масштабируем спрайт до нужного размера, например, 32x32 пикселя
            self.sprite = pygame.transform.scale(self.sprite, (32, 32))
        except Exception as e:
            print(f"Ошибка загрузки спрайта предмета '{name}': {e}")
            # Заглушка на случай ошибки: красный квадрат 32x32
            self.sprite = pygame.Surface((32, 32))
            self.sprite.fill((255, 0, 0))
            

    def draw(self, surface, x, y, scale_factor = 1.5):
        """Отрисовка спрайта предмета на указанных координатах."""
        scaled_sprite = pygame.transform.scale(
            self.sprite,
            (int(self.sprite.get_width() * scale_factor), int(self.sprite.get_height() * scale_factor))
        )
        surface.blit(scaled_sprite, (x, y))

    def __str__(self):
        """Строковое представление предмета для отображения в инвентаре."""
        return self.name
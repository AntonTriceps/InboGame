import pygame
import pytmx

class CollisionDetectorTMX:
    def __init__(self, tmx_data):
        self.tmx_data = tmx_data
        self.collision_layers_names = ["Sloy 2", "Sloy 3", "Sloy 4"] # Имена слоев коллизий
        self.collision_layers = []

        for layer in self.tmx_data.layers:
            if layer.name in self.collision_layers_names and isinstance(layer, pytmx.TiledTileLayer):
                self.collision_layers.append(layer)

        if not self.collision_layers:
            print(f"Не найдены слои коллизий с именами: {self.collision_layers_names}")

    def check_collision(self, player_rect, dx, dy):
        """
        Проверяет, произойдет ли коллизия при перемещении игрока на dx, dy.
        *** ВРЕМЕННО ОТКЛЮЧЕНА КОЛЛИЗИЯ - ВСЕГДА ВОЗВРАЩАЕТ FALSE ***

        Args:
            player_rect: pygame.Rect - прямоугольник игрока.
            dx: int - изменение по оси X.
            dy: int - изменение по оси Y.

        Returns:
            bool: True, если коллизия произойдет, False - если нет.
        """
        return False  # *** ВРЕМЕННО ОТКЛЮЧЕНО - ВСЕГДА ВОЗВРАЩАЕТ FALSE ***
        #  Следующий код закомментирован, чтобы временно отключить коллизию
        # new_rect = player_rect.move(dx, dy) # Создаем прямоугольник будущей позиции
        #
        # for layer in self.collision_layers:
        #     for x, y, gid in layer:
        #         if gid != 0: # Предполагаем, что gid=0 - пустой тайл, не коллизия
        #             tile = self.tmx_data.get_tile_image_by_gid(gid) # Получаем тайл (хотя он тут не используется, можно убрать)
        #             if tile: # Проверка на tile существует, хотя она всегда True, если gid != 0
        #                 tile_rect = pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
        #                                          self.tmx_data.tilewidth, self.tmx_data.tileheight)
        #                 if new_rect.colliderect(tile_rect):
        #                     return True # Коллизия обнаружена
        #
        # return False # Коллизия не обнаружена
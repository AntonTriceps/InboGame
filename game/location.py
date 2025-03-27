import pygame
import pytmx

class Location:
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

    def draw(self, screen, camera_x=0, camera_y=0):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    screen.blit(image, (x * self.tmx_data.tilewidth - camera_x, y * self.tmx_data.tileheight - camera_y))

    def get_collidable_objects(self):
        collidables = []
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'type') and obj.type == "collidable":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                collidables.append(rect)
        return collidables

    def get_interactable_objects(self):
        interactables = []
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'type') and obj.type == "chest":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                interactables.append({"rect": rect, "type": obj.type})
        return interactables
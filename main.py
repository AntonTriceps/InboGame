# main.py
import pygame
import pytmx
import sys
from utils.Inventory import Inventory
from utils.Item import Item

# Импорт класса Player, NPC из utils
try:
    from utils.Player import Player
    from utils.NPC import NPC
except ImportError:
    print("Ошибка импорта файлов из utils. Убедитесь, что папка utils существует и файлы Player.py, NPC.py находятся в ней.")
    sys.exit()

# Инициализация PyGame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Novella INBO-22-23")

# Пути к файлам игры
LEVEL_1_PATH = "data/level/level1/1level.tmx"

# Класс для загрузки и отрисовки TMX карты
class TiledMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

    def render(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmx_data.tilewidth,
                                         y * self.tmx_data.tileheight))

# Загрузка карты
try:
    level_map = TiledMap(LEVEL_1_PATH)
except Exception as e:
    print(f"Ошибка загрузки карты: {e}")
    pygame.quit()
    exit()

# Calculate center spawn position for NPC
npc_spawn_x = level_map.width // 2 - 24  # Adjust 24 if NPC scaled width is different
npc_spawn_y = level_map.height // 2 - 32 # Adjust 32 if NPC scaled height is different

# Настройки инвентаря
inventory = Inventory()
# Добавляем тестовый предмет "Меч" с его спрайтом
inventory.add_item(Item("Меч", "data/image/Items/sword sprite.png"))

# Создание экземпляра игрока
player = Player(100, 100, level_map.width, level_map.height, inventory=inventory)

# Создание экземпляра NPC для level1.tmx, спавн в центре карты
npc_level1 = NPC(npc_spawn_x, npc_spawn_y, level_map.width, level_map.height)

# Основной игровой цикл
running = True
clock = pygame.time.Clock()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка ввода NPC (для диалогов)
        npc_level1.handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:  # Открытие инвентаря
                inventory.toggle()
            if event.key == pygame.K_SPACE and not inventory.active:  # Атака // dash dobavit potom
                player.attack()  # Запускаем атаку
            if event.key == pygame.K_e: # Кнопка взаимодействия 'E'
                if npc_level1.is_close_to_player(player.rect):
                    npc_level1.start_dialogue()

                    # Set directions for player and NPC to face each other during dialogue
                    player_center = pygame.math.Vector2(player.rect.center)
                    npc_center = pygame.math.Vector2(npc_level1.rect.center)
                    direction_vector = npc_center - player_center

                    distance_offset = 50 # Distance to separate characters

                    if abs(direction_vector.x) > abs(direction_vector.y): # More horizontal difference
                        if direction_vector.x > 0: # NPC to the right of player
                            player.set_direction("right")
                            npc_level1.set_direction("left")
                        else: # NPC to the left of player
                            player.set_direction("left")
                            npc_level1.set_direction("right")
                    else: # More vertical difference or equal
                        if direction_vector.y > 0: # NPC below player
                            player.set_direction("down")
                            npc_level1.set_direction("up")
                            player.rect.y -= distance_offset # Move player up
                            npc_level1.rect.y += distance_offset # Move NPC down
                        else: # NPC above player
                            player.set_direction("up")
                            npc_level1.set_direction("down")
                            player.rect.y += distance_offset # Move player down
                            npc_level1.rect.y -= distance_offset # Move NPC up

    # Обновление игрока (только если не в диалоге)
    if not npc_level1.talking_to_npc:
        player.update()
    npc_level1.update() # Обновление NPC - delta_time argument removed

    # Отрисовка
    screen.fill((0, 0, 0))  # Черный фон
    level_map.render(screen)  # Отрисовка карты
    npc_level1.draw(screen) # Отрисовка NPC
    player.draw(screen)      # Отрисовка игрока поверх карты
    npc_level1.draw_dialogue_ui(screen) # Отрисовка интерфейса диалога NPC
    inventory.draw(screen)  # Отрисовка инвентаря (ПЕРЕД flip)
    ## Сюда ставить следующие отрисовки иначе не будут поверх персонажа
    # 
    ## Отрисовка HP-бара из класса Player
    health_percent = player.health / player.max_health
    frame_index = max(0, min(player.hp_frame_count - 1, int((1 - health_percent) * player.hp_frame_count)))
    hp_bar_sprite = player.hp_frames[frame_index]
    screen.blit(hp_bar_sprite, (player.hp_bar_x, player.hp_bar_y))
        
    pygame.display.flip()  # Обновление экрана

    

    clock.tick(60) # delta_time calculation removed from main.py

# Завершение работы
pygame.quit()
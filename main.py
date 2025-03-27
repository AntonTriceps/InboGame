import pygame
import random
from game.player import Player
from game.npc import NPC
from game.location import Location
from game.dialogue import Dialogue
from game.inventory import Inventory
from dialogues import DIALOGUES

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 609
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Novella INBO-22-23")

# Шрифт для характеристик
font = pygame.font.Font(None, 36)

# Функция для загрузки уровня
def load_level(level_name):
    location = Location("image/location/level1.tmx")
    collidables = location.get_collidable_objects()
    interactables = location.get_interactable_objects()
    return location, collidables, interactables

# Функция для размещения NPC в случайной точке
def place_npc_randomly(level_width, level_height, collidables):
    while True:
        x = random.randint(0, level_width - 64)
        y = random.randint(0, level_height - 64)
        npc_rect = pygame.Rect(x, y, 64, 64)
        collision = False
        for collidable in collidables:
            if npc_rect.colliderect(collidable):
                collision = True
                break
        if not collision:
            return x, y

# Начальный уровень
current_level = "level1"
location, collidables, interactables = load_level(current_level)

# Создание объектов
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
npc_x, npc_y = place_npc_randomly(location.width, location.height, collidables)
npc = NPC(npc_x, npc_y, location.width, location.height, current_level)

# Настройки диалога
dialogue = Dialogue(DIALOGUES[current_level])

# Настройки инвентаря
inventory = Inventory()
# Добавим тестовый предмет для проверки
inventory.add_item("Меч")

# Настройки камеры
camera_x, camera_y = 0, 0
level_width = location.width
level_height = location.height

# Основной игровой цикл
running = True
clock = pygame.time.Clock()

while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:  # Открытие инвентаря
                inventory.toggle()
            if event.key == pygame.K_SPACE and not dialogue.active and not inventory.active:  # Атака
                player.attack()  # Запускаем атаку
            if event.key == pygame.K_LSHIFT and not dialogue.active and not inventory.active:  # Атака
                player.dash()  # Запускаем атаку
            if event.key == pygame.K_0 and not dialogue.active and not inventory.active:  # Атака
                player.take_damage(20)  # Запускаем атаку    
            if dialogue.active:
                if event.key == pygame.K_RETURN:
                    dialogue.next()
                elif dialogue.current_message == len(DIALOGUES[current_level]) - 1 and dialogue.choice is None:
                    if event.key == pygame.K_1:  # Выбор "Да"
                        dialogue.set_choice("yes")
                        if current_level == "level1":
                            current_level = "level2"
                            location, collidables, interactables = load_level(current_level)
                            level_width = location.width
                            level_height = location.height
                            player.rect.x, player.rect.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                            npc_x, npc_y = place_npc_randomly(level_width, level_height, collidables)
                            npc = NPC(npc_x, npc_y, level_width, level_height, current_level)
                            dialogue = Dialogue(DIALOGUES[current_level])
                            inventory.add_item("Ключ от второго уровня")
                    elif event.key == pygame.K_2:  # Выбор "Нет"
                        dialogue.set_choice("no")

    # Получение состояния клавиш
    keys = pygame.key.get_pressed()

    # Движение игрока
    if not dialogue.active and not inventory.active:
        old_x, old_y = player.rect.x, player.rect.y
        player.move(keys)

        # Проверка коллизий игрока
        for collidable in collidables:
            if player.rect.colliderect(collidable):
                player.rect.x, player.rect.y = old_x, old_y
                if player.dashing:
                    player.dashing = False  # Останавливаем рывок при столкновении
                break

    # Проверка взаимодействия с NPC
    if keys[pygame.K_e] and not dialogue.active and not inventory.active:
        npc_rect = npc.rect.inflate(20, 20)
        if player.rect.colliderect(npc_rect):
            dialogue.start()

    # Проверка взаимодействия с другими объектами
    if keys[pygame.K_e] and not dialogue.active and not inventory.active:
        for interactable in interactables:
            if player.rect.colliderect(interactable["rect"]):
                print(f"Взаимодействие с {interactable['type']}!")

    # Проверка атаки
    if player.attacking and not player.has_damaged:
        attack_rect = player.get_attack_rect()
        if attack_rect.colliderect(npc.rect):
            player.has_damaged = True  # Устанавливаем флаг, чтобы урон наносился только один раз
            if npc.take_damage(player.attack_damage):
                # NPC "умер", перемещаем его в новую точку
                npc_x, npc_y = place_npc_randomly(level_width, level_height, collidables)
                npc = NPC(npc_x, npc_y, level_width, level_height, current_level)

    # Обновление объектов
    player.update()
    npc.update(collidables, dialogue.active, (player.rect.x, player.rect.y))
    dialogue.update()

    # Обновление камеры
    camera_x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, level_width - SCREEN_WIDTH))
    camera_y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, level_height - SCREEN_HEIGHT))

    # Отрисовка
    screen.fill((0, 0, 0))
    location.draw(screen, camera_x, camera_y)

    player_rect = player.rect.copy()
    player_rect.x -= camera_x
    player_rect.y -= camera_y
    player.draw(screen, camera_x, camera_y)
 
    npc_rect = npc.rect.copy()
    npc_rect.x -= camera_x
    npc_rect.y -= camera_y
    npc.draw(screen)

    ## Отрисовка HP-бара из класса Player
    health_percent = player.health / player.max_health
    frame_index = max(0, min(player.hp_frame_count - 1, int((1 - health_percent) * player.hp_frame_count)))
    hp_bar_sprite = player.hp_frames[frame_index]
    screen.blit(hp_bar_sprite, (player.hp_bar_x, player.hp_bar_y))

    # Атака игрока
    #player_attack_text = font.render(f"Атака: {player.attack_damage}", True, (20, 230, 20))  # Зелёный текст
    #screen.blit(player_attack_text, (20, 50))

    # Отрисовка диалога и инвентаря
    dialogue.draw(screen)
    inventory.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Завершение игры
pygame.quit()
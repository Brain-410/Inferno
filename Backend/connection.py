import pygame
import Backend.general as general
import json
import random

with open("Backend\\Media\\test.json", "r") as file:
    data = json.load(file)
    object_list = data["layers"][0]["data"]
    TILE_WIDTH = data["tilewidth"]
    TILE_HEIGHT = data["tileheight"]
    map_rows = data["height"]
    map_col = data["width"]
file.close()

character = general.Player(2)
general_object = general.Object()
entity_list = []
attack_objects = []

def attacks(screen, dt):
    for obj in attack_objects:
        obj.display(screen)
        obj.dt = dt
        if obj.move():
            attack_objects.remove(obj)

def player_data(dt):
    character.dt = dt
    character.move()
    do_attack = character.attack()
    match do_attack[0]:
        case False:
            pass
        case True:
            attack_objects.append(general.Attack(*do_attack[1]))
    return character.velocity, character.real_position # data needed for rendering motion

def player_render(screen):
    character.display(screen)
    character.attack()
    return character.damage_data


def entities(screen, dt, player_attributes, damage_data): # Demons, Bosses, etc. NPCs with movement
    for entity in entity_list:
        entity.display(screen)
        entity.move(player_attributes[0])
        entity.dt = dt
        

def summon_entity():
    if random.randint(0, 99) == 1:
        match random.randint(1, 4):
            case 1: # Top
                position = pygame.Vector2(random.randint(0, 1280), -20)
            case 2: # Left
                position = pygame.Vector2(-20, random.randint(0, 800))
            case 3: # Right
                position = pygame.Vector2(1300, random.randint(0, 800))
            case 4: # Bottom
                position = pygame.Vector2(random.randint(0, 1280), 820)
        entity_list.append(general.Entity(position, 50, 30, 200, 50))

def objects(screen, player_attributes): #Floor, Walls, etc. NPCs without movement
    camera_pos = pygame.Vector2(player_attributes[1].x - screen.get_width()//2, player_attributes[1].y - screen.get_height()//2)
    
    # Calculate which tiles are on the screen. Reduces lag, no need to render every tile
    start_col = max(0, int(camera_pos.x // TILE_WIDTH))
    end_col = min(map_col, int((camera_pos.x + screen.get_width()) // TILE_WIDTH + 1))

    start_row = max(0, int(camera_pos.y // TILE_HEIGHT))
    end_row = min(map_rows, int((camera_pos.y + screen.get_height()) // TILE_HEIGHT + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            index = row * map_col + col # Determines what index it is in the tilemap

            position_x, position_y = col * TILE_WIDTH - camera_pos.x, row * TILE_HEIGHT - camera_pos.y  # Tile Position
            
            
            general_object.display(screen, object_list[index], (position_x, position_y))

def background(screen):
    screen.fill("black")
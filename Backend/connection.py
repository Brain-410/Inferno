import pygame
import Backend.general as general
import json
import random, datetime

MAX_ENEMIES = 1

with open("Backend\\Media\\test.json", "r") as file:
    data = json.load(file)
    object_list = data["layers"][0]["data"]
    TILE_WIDTH = data["tilewidth"]
    TILE_HEIGHT = data["tileheight"]
    map_rows = data["height"]
    map_col = data["width"]
file.close()


character = general.Player(2, pygame.rect.Rect(0, 0, 32, 48))
general_object = general.Object()
entity_list = []
alive_entities = 0
entities_num = 0
attack_objects = []

def attacks(screen, dt):
    for obj in attack_objects:
        obj.display(screen)
        obj.dt = dt
        if obj.move():
            attack_objects.remove(obj)
    

def player_data(screen, dt):
    character.dt = dt
    character.move()
    character.calculate_real_data(screen)
    do_attack = character.attack()
    if do_attack[0] == True:
        attack_objects.append(general.Attack(*do_attack[1]))

    return character.velocity, character.rect_data, character.real_data  # data needed for rendering motion

def player_render(screen):
    character.display(screen)
    character.attack()


def entities(screen, dt, player_attributes): # Demons, Bosses, etc. NPCs with movement
    global data
    for i in range(entities_num):
        entity = entity_list[i]
        entity.display(screen)
        entity.move(player_attributes)
        for attack in attack_objects:
            if entity.take_damage(attack.rect_data, attack.damage):
                alive_entities -= 1
        entity.dt = dt

        for other_entity in range(i+1, entities_num):
            entity_2 = entity_list[other_entity]
            if entity_2.rect_data.left > entity.rect_data.right:
                break

            difference = entity.position - entity_2.position
            if difference.magnitude_squared() <= (entity.rect_data.width / 2)**2 :
                force = difference.normalize()
                entity.position += force
                entity.position_change += force
                entity_2.position -= force
                entity_2.position_change -= force
        
        
        entity.collide(data)




def summon_entity(player_true_data):
    global alive_entities, entities_num
    if random.randint(0, 99) == 1 and alive_entities < MAX_ENEMIES:
        match random.randint(2, 2):
            case 1: # Top
                position_x = random.randint(0, 1280)
                position_y = -20
            case 2: # Left
                position_x = -20
                position_y = random.randint(0, 800)
            case 3: # Right
                position_x = 1300
                position_y = random.randint(0, 800)
            case 4: # Bottom
                position_x = random.randint(0, 1280)
                position_y = 820
        entity_list.append(general.Entity(pygame.rect.Rect(300, 300, 32, 32), 50, 30, 1000, 50, player_true_data))
        alive_entities += 1
        entities_num += 1
        entity_list.sort(key=lambda x:  x.rect_data.left)

def objects(screen, player_attributes): #Floor, Walls, etc. NPCs without movement
    camera_pos = pygame.Vector2(player_attributes[1].left - screen.get_width()//2, player_attributes[1].top - screen.get_height()//2)
    # Calculate which tiles are on the screen. Reduces lag, no need to render every tile
    start_col = max(0, int(camera_pos.x // TILE_WIDTH - 1))
    end_col = min(map_col, int((camera_pos.x + screen.get_width()) // TILE_WIDTH + 1))

    start_row = max(0, int(camera_pos.y // TILE_HEIGHT - 1))
    end_row = min(map_rows, int((camera_pos.y + screen.get_height()) // TILE_HEIGHT + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):

            index = row * map_col + col # Determines what index it is in the tilemap

            position_x, position_y = col * TILE_WIDTH - camera_pos.x, row * TILE_HEIGHT - camera_pos.y  # Tile Position
            obj_rect = pygame.rect.Rect(position_x, position_y, TILE_WIDTH, TILE_HEIGHT)
            #print(obj_rect)
            
            general_object.display(screen, object_list[index], obj_rect)

def clear(screen):
    screen.fill("black")
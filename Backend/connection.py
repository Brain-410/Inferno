import pygame
import Backend.general as general
import json
import random, datetime

MAX_ENEMIES = 5

with open("Backend\\Media\\test.json", "r") as file:
    data = json.load(file)
    object_list = data["layers"][0]["data"]
    TILE_WIDTH = data["tilewidth"]
    TILE_HEIGHT = data["tileheight"]
    map_rows = data["height"]
    map_col = data["width"]
file.close()


character = None
general_object = general.Object()
entity_list = []
attack_objects = []
collision_object_data = []


def attacks(dt):
    for obj in attack_objects:
        obj.display()
        obj.dt = dt
        match obj.type:
            case "Mace":
                if obj.move():
                    attack_objects.remove(obj)
            case "Holy Ray":
                obj.extend()
                obj.display()
                obj.do_damage(entity_list)
                if obj.end():
                    attack_objects.remove(obj)
        

def player_data(screen, dt):
    global character
    if character == None:
        character = general.Player(2, pygame.rect.Rect(96, 96, 48, 48), screen, (TILE_WIDTH, TILE_HEIGHT))
    character.dt = dt
    character.move()
    character.collide(data)
    attack_data = character.attack()
    if attack_data[0] == "Mace":
        attack_objects.append(general.Mace(screen, *attack_data[1]))
    elif attack_data[0] == "Holy_Ray":
        attack_objects.append(general.Holy_Ray(screen, *attack_data[1])) 
    
    return character.velocity, character.rect_data, character.visual_data, character.camera_pos  # data needed for rendering motion

def player_render():
    character.display()
    character.attack()

def entities(screen, dt, player_attributes): # Demons, Bosses, etc. NPCs with movement
    for entity in entity_list:
        if entity.delete:
            entity_list.remove(entity)
    entities_num = len(entity_list)
    
    for i in range(entities_num):

        entity = entity_list[i]
        entity.dt = dt
        entity.display(screen)
        entity.move(player_attributes)
        entity.collide(data, player_attributes)
        for attack in attack_objects:
            if attack.type == "Mace":
                entity.take_damage(attack.rect_data, attack.damage)
            

        #entity-entity collision
        if entities_num > i:
            for other_entity in range(i+1, entities_num):
                entity_2 = entity_list[other_entity]
                if entity_2.rect_data.left > entity.rect_data.right:
                    break

                difference = entity.position - entity_2.position
                if difference.magnitude_squared() <= (entity.rect_data.width / 2)**2 :
                    force = difference.normalize()
                    entity.position += force
                    entity.true_data[0] += force.x
                    entity.true_data[1] += force.y

                    entity_2.position -= force
                    entity_2.true_data[0] -= force.x
                    entity_2.true_data[1] -= force.y




def summon_entity(player_true_data):
    if random.randint(0, 99) == 1 and len(entity_list) < MAX_ENEMIES:
        match random.randint(1, 1):
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
        entity_list.append(general.Entity(pygame.rect.Rect(position_x, position_y, 48, 48), 50, 30, 1000, 50, player_true_data, entity_list))
        entity_list.sort(key=lambda x:  x.rect_data.left)

def objects(screen, player_attributes): #Floor, Walls, etc. NPCs without movement
    camera_pos = player_attributes[3]

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
            
            general_object.display(screen, object_list[index], obj_rect, 255)


def clear(screen):
    screen.fill("black")
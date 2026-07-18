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
user_interface_object = None
general_object = general.Object()
enemy_list = []
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
                obj.do_damage(enemy_list)
                if obj.end():
                    attack_objects.remove(obj)
        

def player_data(screen, dt):
    global character
    if character == None:
        character = general.Player(2, pygame.rect.Rect(96, 96, 48, 48), screen, 100, 100, 15, 30, (TILE_WIDTH, TILE_HEIGHT), 5, 10, 0)
    character.dt = dt
    character.move()
    character.collide(data)
    character.restore()
    attack_data = character.ability()

    if attack_data[0] == "Mace":
        attack_objects.append(general.Mace(screen, *attack_data[1]))
    elif attack_data[0] == "Holy_Ray":
        attack_objects.append(general.Holy_Ray(screen, *attack_data[1])) 
    
    return character.export_data()

def player_render():
    character.display()

def enemies(screen, dt, player_attributes): # Demons, Bosses, etc. NPCs with movement
    for enemy in enemy_list:
        if enemy.delete:
            enemy_list.remove(enemy)
            character.gain_exp(enemy.reward_exp)
    enemy_num = len(enemy_list)
    
    for i in range(enemy_num):

        enemy = enemy_list[i]
        enemy.dt = dt
        enemy.display(screen)
        enemy.move(player_attributes)
        enemy.collide(data, player_attributes)
        for attack in attack_objects:
            if attack.type == "Mace":
                enemy.take_damage(attack.rect_data, attack.damage)
            

        #entity-entity collision
        if enemy_num > i:
            for other_enemy in range(i+1, enemy_num):
                enemy_2 = enemy_list[other_enemy]
                if enemy_2.visual_data.left > enemy.visual_data.right:
                    break

                difference = enemy.position - enemy_2.position
                if difference.magnitude_squared() <= (enemy.visual_data.width / 2)**2 :
                    force = difference.normalize()
                    enemy.position += force
                    enemy.true_data[0] += force.x
                    enemy.true_data[1] += force.y

                    enemy_2.position -= force
                    enemy_2.true_data[0] -= force.x
                    enemy_2.true_data[1] -= force.y




def summon_enemy(player_true_data):
    if random.randint(0, 99) == 1 and len(enemy_list) < MAX_ENEMIES:
        match random.randint(1, 4):
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
        enemy_list.append(general.Enemy(pygame.rect.Rect(position_x, position_y, 48, 48), 50, 30, 1000, 50, 50, 30, player_true_data, enemy_list, 20, character))
        enemy_list.sort(key=lambda x:  x.visual_data.left)

def objects(screen, player_attributes): #Floor, Walls, etc. NPCs without movement
    camera_pos = player_attributes["camera position"]

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

def user_interface(screen, player_variables):
    global user_interface_object
    if user_interface_object == None:
        user_interface_object = general.UI(screen)
    user_interface_object.update_data(player_variables)
    user_interface_object.health_bar()
    user_interface_object.mana_bar()
    user_interface_object.exp_bar()
    user_interface_object.level()
    user_interface_object.minimap()
    user_interface_object.settings()
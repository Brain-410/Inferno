import pygame, copy, random, json, datetime
import Backend.general as general, Backend.screens as screens, Backend.Media.asset_library as asset_library

MAX_ENEMIES = 5

level_data = [{}, {}, {}, {}]


levels = {
    1: "Limbo",
    2: "Gluttony",
    3: "Heresy",
    4: "Treachery"
}

for level in levels:
    with open(f"Backend\\Media\\Level_Data\\level{level}.json", "r") as file:
        level_data[level-1]["data"] = json.load(file)
        level_data[level-1]["object_list"] =  level_data[level-1]["data"]["layers"][0]["data"]
        level_data[level-1]["TILE_WIDTH"] =  level_data[level-1]["data"]["tilewidth"]
        level_data[level-1]["TILE_HEIGHT"] =  level_data[level-1]["data"]["tileheight"]
        level_data[level-1]["map_rows"] =  level_data[level-1]["data"]["height"]
        level_data[level-1]["map_col"] =  level_data[level-1]["data"]["width"]
    file.close()

character = None
user_interface_object = None
general_object = general.Tile()
enemy_list = []
attack_objects = []
level = 1
title_screen = None
connecting_screen = None
death_screen = None
victory_screen = None
recent_enemy_spawn_time = datetime.datetime.now()

character_info_base = [100, 100, 2, 15, 15, 0.6, 0, 1]
character_info = [100, 100, 2, 15, 15, 0.6, 0, 1]

current_screen = "Title"

def run_screen(screen):
    global title_screen, connecting_screen, current_screen, death_screen, victory_screen
    match current_screen:
        case "Title":
            if title_screen == None:
                title_screen = screens.Title_Screen(screen, 255, 9)
            title_screen.display()
            title_screen.buttons()
            if title_screen.fade():
                current_screen = "Connecting"
                title_screen = None
        case "Connecting":
            if connecting_screen == None:
                connecting_screen = screens.Connector_Screen(screen, 0, 9, level, levels[level])
            connecting_screen.display()
            if connecting_screen.fade():
                current_screen = "Play"
                connecting_screen = None
        case "Death":
            if death_screen == None:
                death_screen = screens.Death_Screen(screen, 0, 9)
            death_screen.display()
            if death_screen.fade():
                current_screen = "Title"
                death_screen = None
        case "Victory":
            if victory_screen == None:
                victory_screen = screens.Victory_Screen(screen, 0, 9)
            victory_screen.display()
            if victory_screen.fade() == True:
                current_screen = "Title"
                victory_screen = None


def attacks(dt):
    global current_screen
    if current_screen != "Play":
        return
    for obj in attack_objects:
        obj.display()
        obj.dt = dt
        match obj.type:
            case "Force":
                if obj.move():
                    attack_objects.remove(obj)
            case "Holy Ray":
                obj.extend()
                obj.display()
                obj.do_damage(enemy_list)
                if obj.end():
                    attack_objects.remove(obj)
        

def player_data(screen, dt):
    global character, current_screen, character_info, level, enemy_list
    if current_screen != "Play":
        return
    if character == None:
        character = general.Player(2, pygame.rect.Rect(1000, 300, 48, 48), screen, 15, 30, (level_data[level-1]["TILE_WIDTH"], level_data[level-1]["TILE_HEIGHT"]), 5, 10, character_info)
    if character.opacity <= 0:
        character = None
        enemy_list.clear()
        current_screen = "Title"
        character_info = None        
        return
    if character.hp <= 0:
        enemy_list.clear()
        character = None
        character_info = copy.copy(character_info_base)
        level = 1
        current_screen = "Death"
        return

 

    character.dt = dt
    character.move()
    character.collide(level_data[level-1]["data"])
    character.restore()
    attack_data = character.ability()

    if attack_data[0] == "Force":
        attack_objects.append(general.Force(screen, *attack_data[1]))
    elif attack_data[0] == "Holy_Ray":
        attack_objects.append(general.Holy_Ray(screen, *attack_data[1])) 
    
    if character.new_level:
        character_info = character.change_level()
        character = None
        level += 1
        if level == 10:
            current_screen = "Victory"
        else:
            current_screen = "Connecting"
        enemy_list.clear()
        return

    return character.export_data()

def player_render(player_data):
    global current_screen, level, enemy_list

    if current_screen != "Play":
        return
    character.display()

def enemies(screen, dt, player_attributes): # Demons, Bosses, etc. NPCs with movement
    global current_screen
    if current_screen != "Play":
        return
    for enemy in enemy_list:
        if enemy.delete:
            enemy_list.remove(enemy)
            character.gain_exp(enemy.reward_exp)
    enemy_num = len(enemy_list)
    
    if player_attributes["alert"]:
        detection_range = 600
    else:
        detection_range = 400
    for i in range(enemy_num):

        enemy = enemy_list[i]
        enemy.dt = dt
        enemy.detection_range_squared = detection_range**2
        enemy.display(screen)
        enemy.move(player_attributes)
        enemy.collide(level_data[level-1]["data"], player_attributes)
        for attack in attack_objects:
            if attack.type == "Force":
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
    global current_screen, recent_enemy_spawn_time
    if current_screen != "Play":
        return
    if len(enemy_list) < MAX_ENEMIES and (datetime.datetime.now() - recent_enemy_spawn_time).total_seconds() > 1:
        recent_enemy_spawn_time = datetime.datetime.now()
        match random.randint(1, 4):
            case 1: # Top
                position_x = random.randint(0, 720)
                position_y = -50
            case 2: # Left
                position_x = -50
                position_y = random.randint(0, 448)
            case 3: # Right
                position_x = 1220
                position_y = random.randint(0, 448)
            case 4: # Bottom
                position_x = random.randint(0, 720)
                position_y = 500

        if random.randint(0, 5) == 1 and (level == 2 or level == 3) or level == 4:
            enemy_list.append(general.Enemy(pygame.rect.Rect(position_x, position_y, 48, 48), 80, 30, 500, 65 + 20 * level, 65 + 20*level, 50 + 10*level, player_true_data, enemy_list, 8 + 5*level, character, -3.1))
        else:
            enemy_list.append(general.Enemy(pygame.rect.Rect(position_x, position_y, 48, 48), 50, 30, 500, 25 + 10 * level, 25 + 10 * level, 20 + 10*level, player_true_data, enemy_list, 5 + 3*level, character, -2.1))
        enemy_list.sort(key=lambda x:  x.visual_data.left)

def objects(screen, player_attributes): #Floor, Walls, etc. NPCs without movement
    global current_screen
    if current_screen != "Play":
        return
    camera_pos = player_attributes["camera position"]

    tile_width = level_data[level-1]["TILE_WIDTH"]
    tile_height = level_data[level-1]["TILE_HEIGHT"]
    map_col = level_data[level-1]["map_col"]
    map_rows = level_data[level-1]["map_rows"]

    # Calculate which tiles are on the screen. Reduces lag, no need to render every tile
    start_col = max(0, int(camera_pos.x // tile_width - 1))
    end_col = min(map_col, int((camera_pos.x + screen.get_width()) // tile_width + 1))

    start_row = max(0, int(camera_pos.y // tile_height - 1))
    end_row = min(map_rows, int((camera_pos.y + screen.get_height()) // tile_height + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):

            index = row * map_col + col # Determines what index it is in the tilemap

            position_x, position_y = col * tile_width - camera_pos.x, row * tile_height - camera_pos.y  # Tile Position
            obj_rect = pygame.rect.Rect(position_x, position_y, tile_width, tile_height)
            
            general_object.display(screen, level_data[level-1]["object_list"][index], obj_rect, 255)

def clear(screen):
    screen.fill("black")


def user_interface(screen, player_variables):
    global current_screen
    if current_screen != "Play":
        return
    global user_interface_object
    if user_interface_object == None:
        user_interface_object = general.UI(screen)
    user_interface_object.update_data(player_variables)
    user_interface_object.health_bar()
    user_interface_object.mana_bar()
    user_interface_object.exp_bar()
    user_interface_object.level()
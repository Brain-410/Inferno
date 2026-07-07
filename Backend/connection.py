import pygame
import Backend.general as general

character = general.Player(2)
general_object = general.Object()
object_list = [[1, 1, 1], [1, 0, 1], [0, 1, 0]]
entity_list = []



def player(screen, dt):
    character.dt = dt
    character.display(screen)
    character.move()
    return character.velocity, character.real_position

def entities(screen, dt, player_attributes): # Demons, Bosses, etc. NPCs with movement
    for entity in entity_list:
        entity.display(screen)
        entity.move(player_attributes[0])
        entity.dt = dt

def objects(screen, player_attributes): #Background, Walls, etc. NPCs without movement
    camera_pos = pygame.Vector2(player_attributes[1].x - screen.get_width()//2, player_attributes[1].y - screen.get_height()//2)
    
    start_col = max(0, camera_pos.x // 32)
    end_col = min(len(object_list), (camera_pos.x + screen.get_width()) // 32 + 1)
    start_row = max(0, camera_pos.y // 32)
    end_row = min(len(object_list), (camera_pos.y + screen.get_height()) // 32 + 1)

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            tile_id = object_list[row][col]
            general_object.display(screen, object_list[row][col], ((col * 32) - camera_pos.x, (row * 32) - camera_pos.y))           

   

def background(screen, dt):
    screen.fill("red")

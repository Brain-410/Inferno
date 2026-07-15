import pygame
import Backend.Media.asset_library as asset_library
import datetime, copy

class Object:
    def display(self, screen, type, data):
        screen.blit(pygame.transform.scale(asset_library.asset_library[type], (data.width, data.height)), tuple(data.topleft))

    def move(self, velocity: pygame.Vector2):
        self.position -= velocity

class Attack(Object):
    def __init__(self, data, destination, time: float, damage: int, extend: bool):
        self.dt = 0.016
        self.rect_data = data
        self.position = self.rect_data.center

        self.damage = damage
        self.__destination = pygame.Vector2(destination.x + self.rect_data.width//2, destination.y + self.rect_data.height//2)
        self.__time = time
        self.__speed = (self.rect_data.center - self.__destination).magnitude() / self.__time
        self.__dx = (self.__destination - self.rect_data.center).normalize()

    def display(self, screen):
        Object.display(self, screen, -3, self.rect_data)
    def move(self):
        if (self.__destination - self.rect_data.center).magnitude() <= 5:
            return True
        self.position += self.__dx * self.dt * self.__speed
        self.rect_data.center = self.position


class Entity(Object):
    def __init__(self, data, max_speed, max_distance, detection_range, hp, player_data):
        self.dt = 0.016
        self.rect_data = data
        self.position = self.rect_data.center
        self.__player_data = player_data
        self.__true_data = [data.left - (player_data[2].right - player_data[1].left), data.top - (player_data[2].bottom - player_data[1].top), data.width, data.height]
        #self.__true_data = [data.left - 640, data.top - 400, data.width, data.height]
        
        self.__knockback_velocity = pygame.Vector2(0, 0)
        self.__stunned = False
        self.__max_speed = max_speed
        self.__max_distance_squared = max_distance**2
        self.__detection_range_squared = detection_range**2
        self.__aggro = False
        self.hp = hp
        self.__last_took_damage = datetime.datetime.now()

    def display(self, screen):
        Object.display(self, screen, -2, self.rect_data)

    def move(self, data):
        
        Object.move(self, data[0]) #Player movement offset
        self.frame_start_position = copy.copy(self.position)
        self.frame_start_position_true = copy.copy(self.__true_data)
        # Player targeting movement
        distance = (pygame.Vector2(640, 400) - self.rect_data.center).magnitude_squared()
        self.__dx = (pygame.Vector2(640, 400) - self.rect_data.center).normalize()

        if distance > 2.25 * self.__detection_range_squared: 
            self.__aggro = False
        elif distance < self.__detection_range_squared:
            self.__aggro = True

        if self.__aggro and self.__stunned == False and self.hp > 0:
            if distance > self.__max_distance_squared:
                self.position += self.__dx * self.__max_speed * self.dt
                self.__true_data[0] += self.__dx.x * self.__max_speed * self.dt
                self.__true_data[1] += self.__dx.y * self.__max_speed * self.dt
            else:
                self.position -= self.__dx * self.__max_speed * 0.5 * self.dt
                self.__true_data[0] -= self.__dx.x * self.__max_speed * 0.5 * self.dt
                self.__true_data[1] -= self.__dx.y * self.__max_speed * 0.5 * self.dt
        

        #entity-entity collision
        new_pos = pygame.rect.Rect(data[2].left + data[2].width//2 - self.rect_data.width//2, 
                                   data[2].top + data[2].height//2 - self.rect_data.height//2, 
                                   data[2].width, data[2].height)
        while self.rect_data.colliderect(new_pos):
            self.position -= self.__dx * 0.01
            self.__true_data[0] -= self.__dx.x * 0.01
            self.__true_data[1] -= self.__dx.y * 0.01
            self.rect_data.center = self.position
        
        
                    

        #attack knockback/stun
        self.position -= self.__knockback_velocity
        self.__true_data[0] -= self.__knockback_velocity.x
        self.__true_data[1] -= self.__knockback_velocity.y
        self.__knockback_velocity *= 0.9
        if self.__knockback_velocity.magnitude_squared() <= 1:
            self.__knockback_velocity = pygame.Vector2(0, 0)
        if (datetime.datetime.now() - self.__last_took_damage).total_seconds() > 1:
            self.__stunned = False

        #final update
        self.velocity = self.position - self.frame_start_position
        self.rect_data.center = self.position



    def take_damage(self, attack_data, amount):
        if self.rect_data.colliderect(attack_data) and (datetime.datetime.now() - self.__last_took_damage).total_seconds() > 0.5:
            self.__last_took_damage = datetime.datetime.now()
            self.hp -= amount
            self.__knockback_velocity = self.__dx * amount / 4
            self.__stunned = True
    

    def collide(self, tile_data, player_data):
        #entity-tilemap collision
        tile_width = tile_data["tilewidth"]
        tile_height = tile_data["tileheight"]
        object_list = tile_data["layers"][0]["data"]
        map_columns = tile_data["width"]

        start_col = int(self.__true_data[0] // tile_width )
        end_col = int((self.__true_data[0] + self.__true_data[2]) // tile_width + 1)
        start_row = int(self.__true_data[1] // tile_height)
        end_row = int((self.__true_data[1] + self.__true_data[3]) // tile_height + 1)

        if (start_col or end_col or start_row or end_row) < 0: # tilemap only includes positive regions, so this would break at be looking at the wrong numbers
            return

        camera_pos = player_data[3] # standardising the camera position variable
        
        for row in range(start_row, end_row):   
            for column in range(start_col, end_col):

                index = (row * map_columns) + column

                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)
                    dx = min(abs(self.rect_data.right - object_rect.left), abs(self.rect_data.left - object_rect.right))
                    dy = min(abs(self.rect_data.bottom - object_rect.top), abs(self.rect_data.top - object_rect.bottom))
                    # horizontal/vertical intersection with the object - how much the entity is moving into the object per direction

                    index = (row * map_columns) + column
                    object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                    if abs(dx) < abs(dy): # if the movement into the object is primarily vertical
                        while self.rect_data.colliderect(object_rect):
                            self.position.x -= self.velocity.x
                            self.__true_data[0] -= self.velocity.x 
                            self.rect_data.center = self.position
                    else: # if the movement into the object is primarily horizontal
                        while self.rect_data.colliderect(object_rect):
                            self.position.y -= self.velocity.y
                            self.__true_data[1] -= self.velocity.y
                            self.rect_data.center = self.position
                    if (self.position - self.frame_start_position).magnitude_squared() > (self.__max_speed + 1)**2: # prevents occasional clipping between corners
                        offset = self.velocity
                        self.position = self.frame_start_position + offset
                        self.__true_data[0], self.__true_data[1] = self.frame_start_position_true[0] + offset.x, self.frame_start_position_true[1] + offset.y
                    self.rect_data.center = self.position

class Player(Object):
    def __init__(self, max_speed, data, screen, tile_data):
        self.rect_data = data
        self.rect_data.center += pygame.Vector2(tile_data[0], tile_data[1])
        self.screen = screen
        
        self.tile_width = tile_data[0]
        self.tile_height = tile_data[1]
        x_real = self.screen.get_width() // 2 - self.rect_data.width
        y_real = self.screen.get_height() // 2 - self.rect_data.height
        self.visual_data = pygame.rect.Rect(x_real, y_real, self.rect_data.width, self.rect_data.height)

        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.__type = -1.1
        self.__time_of_last_attack = datetime.datetime.now()
        self.damage_data = None
    
    def display(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: # Forward
            if abs(self.velocity.y) < abs(self.velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__type = -1.1
        if keys[pygame.K_a]: # Left
            if abs(self.velocity.x) < abs(self.velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__type = -1.2
        if keys[pygame.K_s]: # Down
            if abs(self.velocity.y) < abs(self.velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__type = -1.3
        if keys[pygame.K_d]: # Right
            if abs(self.velocity.x) < abs(self.velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__type = -1.4
        # Checks to see what keys are being held to determine which one is most recently pressed.
        # From this it determines what direction the player should be facing.
        # It also works so if you stop pressing anything the character still faces the same direction.


        Object.display(self, self.screen, self.__type, self.visual_data)
    
    def attack(self):
        #Holy laser beam
        if pygame.mouse.get_pressed()[0] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 3: # Left mouse button, 3s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
        
        #Mace
        elif pygame.mouse.get_pressed()[2] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 0.7: # Right mouse button, 0.5s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            width = self.visual_data.width//2
            height = self.visual_data.height//2
           
            match self.__type:
                case -1.1:
                    pos_x = self.visual_data.left - self.visual_data.width // 8
                    pos_y = self.visual_data.top - self.visual_data.height // 4

                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x + 2.25*width, pos_y), 0.4, 40, False]]
                case -1.2:
                    pos_x = self.visual_data.left - self.visual_data.width // 4
                    pos_y = self.visual_data.bottom + self.visual_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y - 2.25*height), 0.4, 40, False]]
                case -1.3:
                    pos_x = self.visual_data.right + self.visual_data.width // 8
                    pos_y = self.visual_data.bottom + self.visual_data.height // 4
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x - 2.25*width, pos_y), 0.4, 40, False]]
                case -1.4:
                    pos_x = self.visual_data.right + self.visual_data.width // 4
                    pos_y = self.visual_data.top - self.visual_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y + 2.25*height), 0.4, 40, False]]
        
        return [False]

# 1280 x 800
# (640, 400)

    def move(self):
        keys = pygame.key.get_pressed()
        #horizontal motion
        if keys[pygame.K_a]:
            self.velocity.x -= self.__acceleration * self.dt
            if abs(self.velocity.x) >= self.__max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.__max_speed
        if keys[pygame.K_d]:
            self.velocity.x += self.__acceleration * self.dt
            if abs(self.velocity.x) >= self.__max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.__max_speed
        if not(keys[pygame.K_a] or keys[pygame.K_d]):
            if self.velocity.x <= 0.5 and self.velocity.x >= -0.5:
                self.velocity.x = 0
            else:
                self.velocity.x *= 0.85
        #vertical motion
        if keys[pygame.K_w]:
            self.velocity.y -= self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.__max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.__max_speed
        if keys[pygame.K_s]:
            self.velocity.y += self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.__max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.__max_speed
        if not(keys[pygame.K_w] or keys[pygame.K_s]):
            if self.velocity.y <= 0.5 and self.velocity.y >= -0.5:
                self.velocity.y = 0
            else:
                self.velocity.y *= 0.85
        self.rect_data.center += self.velocity
        self.camera_pos = self.rect_data.topleft - pygame.Vector2(self.screen.get_width(), self.screen.get_height())//2


    def collide(self, tile_data):

        #entity-tilemap collision
        tile_width = tile_data["tilewidth"]
        tile_height = tile_data["tileheight"]
        object_list = tile_data["layers"][0]["data"]
        map_rows = tile_data["height"]
        map_columns = tile_data["width"]


        start_col = int(self.rect_data.left // tile_width - 1)
        end_col = int(self.rect_data.right // tile_width)
        start_row = int(self.rect_data.top // tile_height - 1)
        end_row = int(self.rect_data.bottom // tile_height)

        #Checking all tiles the entity is touching
        for row in range(start_row, end_row):  
            for column in range(start_col, end_col):
                print()

                index = (row * map_columns) + column
                object_rect = pygame.rect.Rect(column * tile_width - self.camera_pos.x, row * tile_height - self.camera_pos.y, tile_width, tile_height)

                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    
                    dx = min(abs(self.visual_data.right - object_rect.left), abs(self.visual_data.left - object_rect.right))
                    dy = min(abs(self.visual_data.bottom - object_rect.top), abs(self.visual_data.top - object_rect.bottom))

                    print(dx, dy)
                    if self.visual_data.colliderect(object_rect):
                        if dx < dy:
                            self.rect_data.centerx -= self.velocity.x
                            self.velocity.x = 0
                        else:
                            self.rect_data.centery -= self.velocity.y
                            self.velocity.y = 0
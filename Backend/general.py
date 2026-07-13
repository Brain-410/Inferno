import pygame
import Backend.Media.asset_library as asset_library
import datetime

class Object:
    def display(self, screen, type, data):
        screen.blit(pygame.transform.scale(asset_library.asset_library[type], (data.width, data.height)), tuple(data.center))

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
        self.rect_data.center = self.position

    def take_damage(self, attack_data, amount):
        if self.rect_data.colliderect(attack_data) and (datetime.datetime.now() - self.__last_took_damage).total_seconds() > 0.5:
            self.__last_took_damage = datetime.datetime.now()
            self.hp -= amount
            self.__knockback_velocity = self.__dx * amount / 4
            self.__stunned = True
    

    def collide(self, tile_data):
        #entity-tilemap collision
        tile_width = tile_data["tilewidth"]
        tile_height = tile_data["tileheight"]
        object_list = tile_data["layers"][0]["data"]
        map_rows = tile_data["height"]
        map_columns = tile_data["width"]



        start_col = int(self.__true_data[0] // tile_width )
        end_col = int((self.__true_data[0] + self.__true_data[2]) // tile_width + 1)
        start_row = int(self.__true_data[1] // tile_height)
        end_row = int((self.__true_data[1] + self.__true_data[3]) // tile_height + 1)


        print(start_col, end_col, start_row, end_row)

        if (start_col or end_col or start_row or end_row) < 0:
            print("Out of bounds")
            return
        camera_pos = pygame.Vector2(self.__player_data[1].left - 640, self.__player_data[1].top - 400)

        #Checking all tiles the entity is touching
        for row in range(start_row, end_row):   
            for column in range(start_col, end_col):
                #print("HIIIII")

                index = (row * map_columns) + column
                object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                #print(object_list[index])
                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    print(object_rect)
                    print(self.rect_data)

                    dx, dy = 0, 0
                    #from left
                    if abs(self.rect_data.right - object_rect.left) < abs(object_rect.right - self.rect_data.left):
                        dx = self.rect_data.right - object_rect.left
                        print(f"1, {dx}")
                    else: #from right
                        dx = self.rect_data.left - object_rect.right
                        print(f'2, {dx}')
                    #from bottom
                    if abs(self.rect_data.bottom - object_rect.top) < abs(object_rect.bottom - self.rect_data.top):
                        dy = self.rect_data.bottom - object_rect.top
                        print(f"3, {dy}")
                    else: #from top
                        dy = self.rect_data.top - object_rect.bottom
                        print(f"4, {dy}")   

                    print(max(dx, dy))
                    
                    
                    self.rect_data.center = self.position
        #print("\n\n\n")


class Player(Object):
    def __init__(self, max_speed, data):
        self.rect_data = data

        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.__type = -1.1
        self.__time_of_last_attack = datetime.datetime.now()
        self.damage_data = None

    def calculate_real_data(self, screen):
        x_real = screen.get_width() // 2  - self.rect_data.width
        y_real = screen.get_height() // 2  - self.rect_data.height
        self.real_data = pygame.rect.Rect(x_real, y_real, self.rect_data.width, self.rect_data.height)
    
    def display(self, screen):
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


        Object.display(self, screen, self.__type, self.real_data)
    
    def attack(self):
        #Holy laser beam
        if pygame.mouse.get_pressed()[0] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 3: # Left mouse button, 3s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
        
        #Mace
        elif pygame.mouse.get_pressed()[2] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 0.7: # Right mouse button, 0.5s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            width = self.real_data.width//2
            height = self.real_data.height//2
           
            match self.__type:
                case -1.1:
                    pos_x = self.real_data.left - self.real_data.width // 8
                    pos_y = self.real_data.top - self.real_data.height // 4

                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x + 2.25*width, pos_y), 0.4, 40, False]]
                case -1.2:
                    pos_x = self.real_data.left - self.real_data.width // 4
                    pos_y = self.real_data.bottom + self.real_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y - 2.25*height), 0.4, 40, False]]
                case -1.3:
                    pos_x = self.real_data.right + self.real_data.width // 8
                    pos_y = self.real_data.bottom + self.real_data.height // 4
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x - 2.25*width, pos_y), 0.4, 40, False]]
                case -1.4:
                    pos_x = self.real_data.right + self.real_data.width // 4
                    pos_y = self.real_data.top - self.real_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y + 2.25*height), 0.4, 40, False]]
        
        return [False]

# 1280 x 800
# (640, 400)

    def move(self):
        keys = pygame.key.get_pressed()
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
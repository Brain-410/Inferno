import pygame
import Backend.Media.asset_library as asset_library
import datetime, copy, math

class Object:
    def display(self, screen, asset_index, data, opacity):
        image = asset_library.asset_library[asset_index]
        image.set_alpha(opacity)
        screen.blit(pygame.transform.scale(image, (data.width, data.height)), tuple(data.topleft))

    def move(self, velocity: pygame.Vector2):
        self.position -= velocity

class Attack(Object):
    def __init__(self, screen, object_data, time: float, damage: int, asset_index):
        self.dt = 0.016
        self.rect_data = object_data
        self.position = self.rect_data.center

        self.damage = damage
        self.time = time
        self.__asset_index = asset_index
        self.__screen = screen
        self.__opacity = 255

    def display(self):
        Object.display(self, self.__screen, self.__asset_index, self.rect_data, self.__opacity)
    

class Mace(Attack):
    def __init__(self, screen, object_data, time, damage, asset_index, destination):
        super().__init__(screen, object_data, time, damage, asset_index)
        self.__destination = pygame.Vector2(destination.x + self.rect_data.width//2, destination.y + self.rect_data.height//2)
        self.__speed = (self.rect_data.center - self.__destination).magnitude() / self.time
        self.__dx = (self.__destination - self.rect_data.center).normalize()
 
    def display(self):
        super().display()
    def move(self):
        if (self.__destination - self.rect_data.center).magnitude() <= 5:
            return True
        self.position += self.__dx * self.dt * self.__speed
        self.rect_data.center = self.position

class Holy_Ray(Attack):
    def __init__(self, screen, object_data, time, damage, asset_index, angle):
        super().__init__(screen, object_data, time, damage, asset_index)
        self.__angle = angle
    def display(self):
        super().display()
    def extend(self):
        pass


class Entity(Object):
    def __init__(self, data, max_speed, max_distance, detection_range, hp, player_data, entity_list):
        self.dt = 0.016
        self.rect_data = data
        self.position = self.rect_data.center
        self.__player_data = player_data
        self.true_data = [data.left - (player_data[2].right - player_data[1].left), data.top - (player_data[2].bottom - player_data[1].top), data.width, data.height]
        #self.true_data = [data.left - 640, data.top - 400, data.width, data.height]
        
        self.__knockback_velocity = pygame.Vector2(0, 0)
        self.__stunned = False
        self.__max_speed = max_speed
        self.__max_distance_squared = max_distance**2
        self.__detection_range_squared = detection_range**2
        self.__aggro = False
        self.hp = hp
        self.__last_took_damage = datetime.datetime.now()
        self.__dx = pygame.Vector2(0, 0)
        self.__opacity = 255
        self.is_dead = False
        self.__list = entity_list

    def display(self, screen):
        if self.hp <= 0:
            self.__opacity -= 1
        if self.__opacity <= 0:
            self.is_dead = True

        Object.display(self, screen, -2, self.rect_data, self.__opacity)

    def move(self, data):

        Object.move(self, data[0]) #Player movement offset
        self.frame_start_position = copy.copy(self.position)
        self.frame_start_position_true = copy.copy(self.true_data)
        velocity_offset = pygame.Vector2(0, 0)

        # Player targeting movement
        distance = (pygame.Vector2(640, 400) - self.rect_data.center).magnitude_squared()
        self.__dx = (pygame.Vector2(640, 400) - self.rect_data.center).normalize()

        if distance > 2.25 * self.__detection_range_squared: 
            self.__aggro = False
        elif distance < self.__detection_range_squared:
            self.__aggro = True

        if self.__aggro:
            if distance > self.__max_distance_squared:
                if self.__stunned or self.hp <= 0:
                    velocity_offset += self.__dx * self.__max_speed * self.dt
                else:
                    self.position += self.__dx * self.__max_speed * self.dt
                    self.true_data[0] += self.__dx.x * self.__max_speed * self.dt
                    self.true_data[1] += self.__dx.y * self.__max_speed * self.dt
            else:
                if self.__stunned or self.hp <= 0:
                    velocity_offset += self.__dx * self.__max_speed / 2 * self.dt
                else:
                    self.position -= self.__dx * self.__max_speed * 0.5 * self.dt
                    self.true_data[0] -= self.__dx.x * self.__max_speed * 0.5 * self.dt
                    self.true_data[1] -= self.__dx.y * self.__max_speed * 0.5 * self.dt


        #player-entity collision
        new_pos = pygame.rect.Rect(data[2].left + data[2].width//2 - self.rect_data.width//2, 
                                   data[2].top + data[2].height//2 - self.rect_data.height//2, 
                                   data[2].width, data[2].height)
        while self.rect_data.colliderect(new_pos):
            self.position -= self.__dx * 0.5
            self.true_data[0] -= self.__dx.x * 0.5
            self.true_data[1] -= self.__dx.y * 0.5
            self.rect_data.center = self.position


        #attack knockback/stun
        self.position -= self.__knockback_velocity
        self.true_data[0] -= self.__knockback_velocity.x
        self.true_data[1] -= self.__knockback_velocity.y
        self.__knockback_velocity *= 0.9
        if self.__knockback_velocity.magnitude_squared() <= 1:
            self.__knockback_velocity = pygame.Vector2(0, 0)
        if (datetime.datetime.now() - self.__last_took_damage).total_seconds() > 1:
            self.__stunned = False

        #final update
        self.velocity = self.position - self.frame_start_position + velocity_offset
        self.rect_data.center = self.position




    def take_damage(self, attack_data, amount):
        #print(f"opacity: {self.__opacity}")
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

        start_col = int(self.true_data[0] // tile_width )
        end_col = int((self.true_data[0] + self.true_data[2]) // tile_width + 1)
        start_row = int(self.true_data[1] // tile_height)
        end_row = int((self.true_data[1] + self.true_data[3]) // tile_height + 1)


        if start_col < 0 or end_col < 0 or start_row < 0 or end_row < 0: # tilemap only includes positive regions, so this would exit when looking at an invalid range
            return

        camera_pos = player_data[3] # standardised camera position variable

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
                            self.true_data[0] -= self.velocity.x 
                            self.rect_data.center = self.position
                    else: # if the movement into the object is primarily horizontal
                        while self.rect_data.colliderect(object_rect):
                            self.position.y -= self.velocity.y
                            self.true_data[1] -= self.velocity.y
                            self.rect_data.center = self.position
                    if (self.position - self.frame_start_position).magnitude_squared() > (self.__max_speed + 1)**2: # prevents occasional clipping between corners
                        offset = self.velocity
                        self.position = self.frame_start_position + offset
                        self.true_data[0], self.true_data[1] = self.frame_start_position_true[0] + offset.x, self.frame_start_position_true[1] + offset.y
                    self.rect_data.center = self.position

class Player(Object):
    def __init__(self, max_speed, data, screen, tile_data):
        self.rect_data = data
        self.rect_data.center += pygame.Vector2(tile_data[0] + data.width//2, tile_data[1] + data.height//2)
        self.true_center = self.rect_data.center
        self.screen = screen
        
        self.tile_width = tile_data[0]
        self.tile_height = tile_data[1]
        x_real = self.screen.get_width() // 2 - data.width//2
        y_real = self.screen.get_height() // 2 - data.height//2
        self.visual_data = pygame.rect.Rect(x_real, y_real, data.width, data.height)

        self.camera_pos = data.topleft - pygame.Vector2(self.screen.get_width() + data.width, self.screen.get_height() + data.height)//2


        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.__asset_index = -1.1
        self.__time_of_last_attack = datetime.datetime.now()
        self.damage_data = None
        self.__opacity = 255
    
    def display(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: # Forward
            if abs(self.velocity.y) < abs(self.velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__asset_index = -1.1
        if keys[pygame.K_a]: # Left
            if abs(self.velocity.x) < abs(self.velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__asset_index = -1.2
        if keys[pygame.K_s]: # Down
            if abs(self.velocity.y) < abs(self.velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__asset_index = -1.3
        if keys[pygame.K_d]: # Right
            if abs(self.velocity.x) < abs(self.velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__asset_index = -1.4
        # Checks to see what keys are being held to determine which one is most recently pressed.
        # From this it determines what direction the player should be facing.
        # It also works so if you stop pressing anything the character still faces the same direction.


        Object.display(self, self.screen, self.__asset_index, self.visual_data, self.__opacity)

    def attack(self):
        #Holy laser beam
        if pygame.mouse.get_pressed()[0] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 3: # Left mouse button, 3s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            mouse_pos = pygame.mouse.get_pos()
            angle = math.pi - math.atan2(self.screen.get_height()//2 - mouse_pos[1], self.screen.get_width()//2 - mouse_pos[0])
            time = 0.2
            damage = 30
            asset_index = -3
            object_data = pygame.rect.Rect(self.screen.get_width()//2, self.screen.get_height()//2, 24, 24)
            return ["Holy_Ray", [object_data, time, damage, asset_index, angle]]


        #Mace
        elif pygame.mouse.get_pressed()[2] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 0.7: # Right mouse button, 0.5s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            width = self.visual_data.width//2
            height = self.visual_data.height//2
            time = 0.4
            damage = 40
            asset_index = -3
            
           
            match self.__asset_index:
                case -1.1: # Up

                    start_position_data = pygame.rect.Rect(self.visual_data.left - width, self.visual_data.top - height, width, height)
                    destination = pygame.Vector2(self.visual_data.right, self.visual_data.top - height)

                    return ["Mace", [start_position_data, time, damage, asset_index, destination]]
                case -1.2: # Left
                    start_position_data = pygame.rect.Rect(self.visual_data.left - width, self.visual_data.bottom, width, height)
                    destination = pygame.Vector2(self.visual_data.left - width, self.visual_data.top - height)

                    return ["Mace", [start_position_data, time, damage, asset_index, destination]]
                case -1.3: # Down
                    start_position_data = pygame.rect.Rect(self.visual_data.right, self.visual_data.bottom, width, height)
                    destination = pygame.Vector2(self.visual_data.left - width, self.visual_data.bottom)

                    return ["Mace", [start_position_data, time, damage, asset_index, destination]]
                case -1.4: # Right
                    start_position_data = pygame.rect.Rect(self.visual_data.right, self.visual_data.top - height, width, height)
                    destination = pygame.Vector2(self.visual_data.right, self.visual_data.bottom)
                    return ["Mace", [start_position_data, time, damage, asset_index, destination]]

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

    def collide(self, tile_data):

        #entity-tilemap collision
        tile_width = tile_data["tilewidth"]
        tile_height = tile_data["tileheight"]
        object_list = tile_data["layers"][0]["data"]
        map_columns = tile_data["width"]

        start_col = int(self.rect_data.left // tile_width - 1)
        end_col = int(self.rect_data.right // tile_width)
        start_row = int(self.rect_data.top // tile_height - 1)
        end_row = int(self.rect_data.bottom // tile_height)

        self.original_velocity = copy.copy(self.velocity)
        #Checking all tiles the entity is touching
        for row in range(start_row, end_row):  
            for column in range(start_col, end_col):

                index = (row * map_columns) + column
                object_rect = pygame.rect.Rect(column * tile_width - self.camera_pos.x, row * tile_height - self.camera_pos.y, tile_width, tile_height)

                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    # checking which direction it should be moved (and how much)
                    dx = min(abs(self.visual_data.right - object_rect.left), abs(self.visual_data.left - object_rect.right))
                    dy = min(abs(self.visual_data.bottom - object_rect.top), abs(self.visual_data.top - object_rect.bottom))
                    if self.visual_data.colliderect(object_rect):
                        if dx < dy:
                            if self.original_velocity.x > 0:
                                self.velocity.x = -dx
                            else:
                                self.velocity.x = dx
                        else:
                            if self.original_velocity.y > 0:
                                self.velocity.y = -dy
                            else:
                                self.velocity.y = dy
        self.true_center += self.velocity
        self.rect_data.center = self.true_center
        self.camera_pos += self.velocity

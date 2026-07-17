import pygame
import Backend.Media.asset_library as asset_library
import datetime, copy, math

class Object:
    def display(self, screen, asset_index, data, opacity):
        image = asset_library.asset_library[asset_index]
        image.set_alpha(opacity)
        screen.blit(pygame.transform.scale(image, (data.width, data.height)), tuple(data.topleft))

    def move(variable, velocity: pygame.Vector2):
        variable -= velocity

class Attack(Object):
    def __init__(self, screen, object_data, time: float, damage: int, asset_index):
        self.dt = 0.016
        self.rect_data = object_data
        self.position = self.rect_data.center

        self.damage = damage
        self.time = time
        self.__asset_index = asset_index
        self.screen = screen
        self.__opacity = 255

    def display(self):
        super().display(self.screen, self.__asset_index, self.rect_data, self.__opacity)
    

class Mace(Attack):
    def __init__(self, screen, object_data, time, damage, asset_index, destination):
        super().__init__(screen, object_data, time, damage, asset_index)
        self.__destination = pygame.Vector2(destination.x + self.rect_data.width//2, destination.y + self.rect_data.height//2)
        self.__speed = (self.rect_data.center - self.__destination).magnitude() / self.time
        self.__dx = (self.__destination - self.rect_data.center).normalize()
        self.type = "Mace"
 
    def display(self):
        super().display()
    def move(self):
        if (self.__destination - self.rect_data.center).magnitude() <= 5:
            return True
        self.position += self.__dx * self.dt * self.__speed
        self.rect_data.center = self.position

class Holy_Ray(Attack):
    def __init__(self, screen, object_data, time, damage, asset_index, angle, max_length):
        super().__init__(screen, object_data, time, damage, asset_index)
        self.__angle = angle

        self.type = "Holy Ray"
        self.__reference_image = asset_library.asset_library[asset_index]
        self.__image = self.__reference_image
        self.transformed_data = object_data

        self.__direction = pygame.Vector2(math.cos(self.__angle * math.pi/180), -math.sin(self.__angle * math.pi/180))
        self.__length = 0
        self.__max_length = max_length
        self.__extension_speed = self.__max_length / self.time
        self.__time_of_start = datetime.datetime.now()

        self.__start_position = pygame.Vector2(self.screen.get_width(), self.screen.get_height())//2

    def display(self):
        self.screen.blit(self.__image, (self.transformed_data.x, self.transformed_data.y))

    def extend(self):
        self.__length += self.__extension_speed * self.dt
        self.__image = pygame.transform.scale(self.__reference_image, (self.__length, self.rect_data.width))
        self.__image = pygame.transform.rotate(self.__image, self.__angle)

        self.transformed_data = self.__image.get_rect()
        self.transformed_data.center = self.__start_position + self.__length * self.__direction // 2

    def end(self):
        if self.__length >= self.__max_length:
            self.__extension_speed = 0
        if (datetime.datetime.now() - self.__time_of_start).total_seconds() > self.time + 0.5:
            return True
    
    def do_damage(self, enemies):
        offset = pygame.Vector2(-self.__direction.y, self.__direction.x) * self.rect_data.width / 2
        target = self.__start_position + self.__direction * self.__length

        paths = [
            (self.__start_position, target),
            (self.__start_position + offset, target + offset),
            (self.__start_position - offset, target - offset)
        ]
        for enemy in enemies:
            for start, end in paths:
                if enemy.visual_data.clipline(start, end):
                    enemy.take_damage_laser(self.damage, 1)




class Entity(Object):
    def __init__(self, visual_data, max_speed, hp, max_hp, damage):
        self.dt = 0.016
        self.visual_data = visual_data

        self.max_speed = max_speed
        self.hp = hp
        self.max_hp = max_hp
        self.time_of_last_attack = datetime.datetime.now()
        self.last_took_damage = datetime.datetime.now()
        self.damage = damage

    def display(self, screen, asset_index, data, opacity):
        super().display(screen, asset_index, data, opacity)

    def move(variable, velocity: pygame.Vector2):
        variable -= velocity
    


class Enemy(Entity):
    def __init__(self, data, max_speed, max_distance, detection_range, hp, max_hp, damage, player_data, enemy_list):
        super().__init__(data, max_speed, hp, max_hp, damage)

        self.position = self.visual_data.center
        self.__player_data = player_data
        self.true_data = [data.left - (player_data["visual data"].right - player_data["true data"].left), data.top - (player_data["visual data"].bottom - player_data["true data"].top), data.width, data.height]
        
        self.__knockback_velocity = pygame.Vector2(0, 0)
        self.__stunned = False
        self.__max_distance_squared = max_distance**2
        self.__detection_range_squared = detection_range**2
        self.__aggro = False
        self.__dx = pygame.Vector2(0, 0)
        self.__opacity = 255
        self.delete = False
        self.__list = enemy_list

    def display(self, screen):
        if self.hp <= 0:
            self.__opacity -= 5
        if self.__opacity <= 0:
            self.delete = True

        super().display(screen, -2, self.visual_data, self.__opacity)

    def move(self, data):

        Object.move(self.position, data["velocity"]) #Player movement offset
        self.frame_start_position = copy.copy(self.position)
        self.frame_start_position_true = copy.copy(self.true_data)
        velocity_offset = pygame.Vector2(0, 0)

        # Player targeting movement
        distance = (pygame.Vector2(640, 400) - self.visual_data.center).magnitude_squared()
        self.__dx = (pygame.Vector2(640, 400) - self.visual_data.center).normalize()

        if distance > 2.25 * self.__detection_range_squared: 
            self.__aggro = False
        elif distance < self.__detection_range_squared:
            self.__aggro = True

        if self.__aggro:
            if distance > self.__max_distance_squared:
                if self.__stunned or self.hp <= 0:
                    velocity_offset += self.__dx * self.max_speed * self.dt
                else:
                    self.position += self.__dx * self.max_speed * self.dt
                    self.true_data[0] += self.__dx.x * self.max_speed * self.dt
                    self.true_data[1] += self.__dx.y * self.max_speed * self.dt
            else:
                if self.__stunned or self.hp <= 0:
                    velocity_offset += self.__dx * self.max_speed / 2 * self.dt
                else:
                    self.position -= self.__dx * self.max_speed * 0.5 * self.dt
                    self.true_data[0] -= self.__dx.x * self.max_speed * 0.5 * self.dt
                    self.true_data[1] -= self.__dx.y * self.max_speed * 0.5 * self.dt


        #player-entity collision
        if self.hp > 0:
            new_pos = pygame.rect.Rect(data["visual data"].left + data["visual data"].width//2 - self.visual_data.width//2, 
                                    data["visual data"].top + data["visual data"].height//2 - self.visual_data.height//2, 
                                    data["visual data"].width, data["visual data"].height)
            while self.visual_data.colliderect(new_pos):
                self.position -= self.__dx * 0.5

                self.true_data[0] -= self.__dx.x * 0.5
                self.true_data[1] -= self.__dx.y * 0.5
                self.visual_data.center = self.position

        #attack knockback/stun
        self.position -= self.__knockback_velocity
        self.true_data[0] -= self.__knockback_velocity.x
        self.true_data[1] -= self.__knockback_velocity.y
        self.__knockback_velocity *= 0.9
        if self.__knockback_velocity.magnitude_squared() <= 1:
            self.__knockback_velocity = pygame.Vector2(0, 0)
        if (datetime.datetime.now() - self.last_took_damage).total_seconds() > 1:
            self.__stunned = False

        #final update
        self.velocity = self.position - self.frame_start_position + velocity_offset
        self.visual_data.center = self.position


    def take_damage_laser(self, amount, time_delay):
        if (datetime.datetime.now() - self.last_took_damage).total_seconds() > time_delay and self.hp > 0:
            self.last_took_damage = datetime.datetime.now()
            self.hp -= amount
            #self.__knockback_velocity = self.__dx * amount / 4
            self.__stunned = True

    def take_damage(self, attack_data, amount):
        if self.visual_data.colliderect(attack_data) and (datetime.datetime.now() - self.last_took_damage).total_seconds() > 0.5 and self.hp > 0:
            self.last_took_damage = datetime.datetime.now()
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

        camera_pos = player_data["camera position"] # standardised camera position variable

        for row in range(start_row, end_row):   
            for column in range(start_col, end_col):

                index = (row * map_columns) + column

                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                    dx = min(abs(self.visual_data.right - object_rect.left), abs(self.visual_data.left - object_rect.right))
                    dy = min(abs(self.visual_data.bottom - object_rect.top), abs(self.visual_data.top - object_rect.bottom))
                    # horizontal/vertical intersection with the object - how much the entity is moving into the object per direction

                    index = (row * map_columns) + column
                    object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                    if abs(dx) < abs(dy): # if the movement into the object is primarily vertical
                        while self.visual_data.colliderect(object_rect):
                            self.position.x -= self.velocity.x
                            self.true_data[0] -= self.velocity.x 
                            self.visual_data.center = self.position
                    else: # if the movement into the object is primarily horizontal
                        while self.visual_data.colliderect(object_rect):
                            self.position.y -= self.velocity.y
                            self.true_data[1] -= self.velocity.y
                            self.visual_data.center = self.position
                    if (self.position - self.frame_start_position).magnitude_squared() > (self.max_speed + 1)**2: # prevents occasional clipping between corners
                        offset = self.velocity
                        self.position = self.frame_start_position + offset
                        self.true_data[0], self.true_data[1] = self.frame_start_position_true[0] + offset.x, self.frame_start_position_true[1] + offset.y
                    self.visual_data.center = self.position


#        self.dt = 0.016
#        self.visual_data = visual_data
#        self.max_speed = max_speed
#        self.hp = hp
#        self.time_of_last_attack = datetime.datetime.now()
#        self.last_took_damage = datetime.datetime.now(

class Player(Entity):
    def __init__(self, max_speed, data, screen, hp, max_hp, damage, tile_data):
        
        super().__init__(pygame.rect.Rect((screen.get_width() - data.width)//2, (screen.get_height() - data.height)//2, data.width, data.height), max_speed, hp, max_hp, damage)

        self.rect_data = data
        self.rect_data.center += pygame.Vector2(tile_data[0] + data.width//2, tile_data[1] + data.height//2)
        self.true_center = self.rect_data.center
        self.screen = screen
        
        self.tile_width = tile_data[0]
        self.tile_height = tile_data[1]

        self.camera_pos = data.topleft - pygame.Vector2(self.screen.get_width() + data.width, self.screen.get_height() + data.height)//2


        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.__asset_index = -1.1
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


        super().display(self.screen, self.__asset_index, self.visual_data, self.__opacity)

    def attack(self):
        #Holy laser beam
        if pygame.mouse.get_pressed()[0] and (datetime.datetime.now() - self.time_of_last_attack).total_seconds() > 1.5: # Left mouse button, 3s cooldown
            self.time_of_last_attack = datetime.datetime.now()
            mouse_pos = pygame.mouse.get_pos()
            angle = math.degrees(math.atan2(self.screen.get_height()//2 - mouse_pos[1], mouse_pos[0] - self.screen.get_width()//2))
            time = 0.2
            damage = self.damage
            asset_index = -4
            object_data = pygame.rect.Rect(self.screen.get_width()//2, self.screen.get_height()//2, 24, 24)
            return ["Holy_Ray", [object_data, time, damage, asset_index, angle, 480]]


        #Mace
        elif pygame.mouse.get_pressed()[2] and (datetime.datetime.now() - self.time_of_last_attack).total_seconds() > 0.7: # Right mouse button, 0.5s cooldown
            self.time_of_last_attack = datetime.datetime.now()
            width = self.visual_data.width//2
            height = self.visual_data.height//2
            time = 0.4
            damage = 2 * self.damage
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
            if abs(self.velocity.x) >= self.max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.max_speed
        if keys[pygame.K_d]:
            self.velocity.x += self.__acceleration * self.dt
            if abs(self.velocity.x) >= self.max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.max_speed
        if not(keys[pygame.K_a] or keys[pygame.K_d]):
            if self.velocity.x <= 0.5 and self.velocity.x >= -0.5:
                self.velocity.x = 0
            else:
                self.velocity.x *= 0.85
        #vertical motion
        if keys[pygame.K_w]:
            self.velocity.y -= self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.max_speed
        if keys[pygame.K_s]:
            self.velocity.y += self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.max_speed
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
    
    def export_data(self):
        data = {
            "velocity": self.velocity,
            "visual data": self.visual_data,
            "true data": self.rect_data,
            "camera position": self.camera_pos,
            "hp": self.hp,
            #"mana": self.__mana,
            #"exp": self.__exp
        }
        return data


class UI:
    def __init__(self, screen, player_variables):
        self.__screen = screen       
        self.__player_hp = player_variables["hp"]
        self.__player_mana = player_variables["mana"]
        self.__player_exp = player_variables["exp"]
        self.__player_position = player_variables["true position"] 
    def health_bar(self):
        print(self.__player_hp)
    def mana_bar(self):
        print(self.__player_mana)
    def exp_bar(self):
        print(self.__player_exp)
    def minimap(self):
        pass
    def settings(self):
        pass
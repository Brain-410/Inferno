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

class Tile:
    def display(self, screen, asset_index, data, opacity):
        image = asset_library.tile_assets[asset_index]
        screen.blit(image, tuple(data.topleft))
    def move(variable, velocity: pygame.Vector2):
        variable -= velocity


class Attack(Object):
    def __init__(self, screen, object_data, time, damage, asset_index):
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
    

class Force(Attack):
    def __init__(self, screen, object_data, time, damage, asset_index, destination):
        super().__init__(screen, object_data, time, damage, asset_index)
        self.__destination = pygame.Vector2(destination.x + self.rect_data.width//2, destination.y + self.rect_data.height//2)
        self.__speed = (self.rect_data.center - self.__destination).magnitude() / self.time
        self.__dx = (self.__destination - self.rect_data.center).normalize()
        self.type = "Force"
        self.__image = asset_library.asset_library[asset_index]
 
    def display(self):
        self.screen.blit(self.__image, self.position - pygame.Vector2(12, 12))
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
        self.__transformed_data = object_data

        self.__direction = pygame.Vector2(math.cos(self.__angle * math.pi/180), -math.sin(self.__angle * math.pi/180))
        self.__length = 0
        self.__max_length = max_length
        self.__extension_speed = self.__max_length / self.time
        self.__time_of_start = datetime.datetime.now()

        self.__start_position = pygame.Vector2(self.screen.get_width(), self.screen.get_height())//2

    def display(self):
        self.screen.blit(self.__image, (self.__transformed_data.x, self.__transformed_data.y))

    def extend(self):
        self.__length += self.__extension_speed * self.dt
        self.__image = pygame.transform.scale(self.__reference_image, (self.__length, self.rect_data.width))
        self.__image = pygame.transform.rotate(self.__image, self.__angle)

        self.__transformed_data = self.__image.get_rect()
        self.__transformed_data.center = self.__start_position + self.__length * self.__direction // 2

    def end(self):
        if self.__length >= self.__max_length:
            self.__extension_speed = 0
        if (datetime.datetime.now() - self.__time_of_start).total_seconds() > self.time + 0.5:
            return True
    
    def do_damage(self, enemies):
        offset = pygame.Vector2(-self.__direction.y, self.__direction.x) * self.rect_data.width / 2
        target = self.__start_position + self.__direction * self.__length
        take_damage = False

        paths = [
            (self.__start_position, target),
            (self.__start_position + offset, target + offset),
            (self.__start_position - offset, target - offset)
        ]
        for enemy in enemies:
            for start, end in paths:
                if enemy.visual_data.clipline(start, end):
                    take_damage = True
            if take_damage:
                enemy.take_damage_laser(self.damage)
                take_damage = False
            




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
    def __init__(self, data, max_speed, max_distance, detection_range, hp, max_hp, damage, player_data, enemy_list, reward_exp, player, asset_index):
        super().__init__(data, max_speed, hp, max_hp, damage)


        if asset_index == -3.1:
            self.is_demon = True
        else:
            self.is_demon = False

        self.position = self.visual_data.center
        self.__player_data = player_data
        self.true_data = [data.left - (player_data["visual data"].right - player_data["true data"].left), data.top - (player_data["visual data"].bottom - player_data["true data"].top), data.width, data.height]
        
        self.__knockback_velocity = pygame.Vector2(0, 0)
        self.__stunned = False
        self.__max_distance_squared = max_distance**2
        self.detection_range_squared = detection_range**2
        self.__aggro = True
        self.__dx = pygame.Vector2(0, 0)
        self.__opacity = 255
        self.delete = False
        self.reward_exp = reward_exp
        self.__type = asset_index
        self.__player = player

    def display(self, screen):
        self.hp = round(self.hp)
        if self.hp < 1:
            self.__opacity -= 5
        if self.__opacity <= 0:
            self.delete = True


        self.__outline_bar = pygame.surface.Surface((1, 1))
        self.__outline_bar.fill((0, 0, 0))
        self.__outline_bar_sprite = pygame.transform.scale(self.__outline_bar, (self.visual_data.width, 12))
        self.__outline_bar_sprite.set_alpha(self.__opacity)

        self.__backing_bar = pygame.surface.Surface((1, 1))
        self.__backing_bar.fill((78, 29, 29))

        self.__backing_bar_sprite = pygame.transform.scale(self.__backing_bar, (self.visual_data.width - 4, 8))
        self.__backing_bar_sprite.set_alpha(self.__opacity)

        bar_length = round(max(self.hp / self.max_hp * (self.visual_data.width - 4), 0))
        self.__hp_sprite = pygame.surface.Surface((1, 1))
        self.__hp_sprite.fill((255, 50, 50))
        self.__hp_bar_sprite = pygame.transform.scale(self.__hp_sprite, (bar_length, 8))
        self.__hp_bar_sprite.set_alpha(self.__opacity)


        super().display(screen, self.__type, self.visual_data, self.__opacity)

        screen.blit(self.__outline_bar_sprite, (self.visual_data.left, self.visual_data.top - 5))
        screen.blit(self.__backing_bar_sprite, (self.visual_data.left + 2, self.visual_data.top - 3))
        screen.blit(self.__hp_bar_sprite, (self.visual_data.left + 2, self.visual_data.top - 3))


    def move(self, data):

        Object.move(self.position, data["velocity"]) #Player movement offset
        self.frame_start_position = copy.copy(self.position)
        self.frame_start_position_true = copy.copy(self.true_data)
        velocity_offset = pygame.Vector2(0, 0)

        # Player targeting movement
        distance = (pygame.Vector2(360, 224) - self.visual_data.center).magnitude_squared()
        self.__dx = (pygame.Vector2(360, 224) - self.visual_data.center).normalize()
        if self.is_demon:
            if self.__dx.x > 0:
                self.__type = -3.1
            else:
                self.__type = -3.2

        else:
            if self.__dx.x > 0:
                self.__type = -2.1
            else:
                self.__type = -2.2

        if distance > 800000:
            self.delete = True
            self.reward_exp = 0


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
            if self.visual_data.colliderect(new_pos) and (datetime.datetime.now() - self.time_of_last_attack).total_seconds() > 0.7:
                self.time_of_last_attack = datetime.datetime.now()
                self.__player.take_damage(self.damage, self.__dx)
            while self.visual_data.colliderect(new_pos):
                print("1")
                self.position -= self.__dx

                self.true_data[0] -= self.__dx.x
                self.true_data[1] -= self.__dx.y
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
        self.__velocity = self.position - self.frame_start_position + velocity_offset
        self.visual_data.center = self.position


    def take_damage_laser(self, amount):
        self.hp -= amount * self.dt

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
        map_rows = tile_data["height"]
        map_columns = tile_data["width"]

        start_col = int(self.true_data[0] // tile_width )
        end_col = int((self.true_data[0] + self.true_data[2]) // tile_width + 1)
        start_row = int(self.true_data[1] // tile_height)
        end_row = int((self.true_data[1] + self.true_data[3]) // tile_height + 1)

        if start_row < 0 or end_row > map_rows or start_col < 0 or end_col > map_columns: # tilemap only includes positive regions, so this would exit when looking at an invalid range
            self.delete = True

        camera_pos = player_data["camera position"] # standardised camera position variable

        count = 0
        try:
            for row in range(start_row, end_row):   
                for column in range(start_col, end_col):

                    index = (row * map_columns) + column
                    if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                        count += 1
                        object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                        dx = min(abs(self.visual_data.right - object_rect.left), abs(self.visual_data.left - object_rect.right))
                        dy = min(abs(self.visual_data.bottom - object_rect.top), abs(self.visual_data.top - object_rect.bottom))
                        # horizontal/vertical intersection with the object - how much the entity is moving into the object per direction

                        index = (row * map_columns) + column
                        object_rect = pygame.rect.Rect(column * tile_width - camera_pos.x, row * tile_height - camera_pos.y, tile_width, tile_height)

                        if abs(dx) < abs(dy): # if the movement into the object is primarily vertical
                            while self.visual_data.colliderect(object_rect):
                                if self.__velocity.x == 0:
                                    self.__velocity.x = 1
                                self.position.x -= self.__velocity.x
                                self.true_data[0] -= self.__velocity.x 
                                self.visual_data.center = self.position
                        else: # if the movement into the object is primarily horizontal
                            while self.visual_data.colliderect(object_rect):
                                if self.__velocity.y == 0:
                                    self.__velocity.y = 1
                                self.position.y -= self.__velocity.y
                                self.true_data[1] -= self.__velocity.y
                                self.visual_data.center = self.position
                        if (self.position - self.frame_start_position).magnitude_squared() > (self.max_speed + 1)**2: # prevents occasional clipping between corners
                            offset = self.__velocity
                            self.position = self.frame_start_position + offset
                            self.true_data[0], self.true_data[1] = self.frame_start_position_true[0] + offset.x, self.frame_start_position_true[1] + offset.y
                        self.visual_data.center = self.position
            if count == 4:
                self.delete = True
                self.reward_exp = 0
        except:
            self.delete = True
            self.reward_exp = 0


#        self.dt = 0.016
#        self.visual_data = visual_data
#        self.max_speed = max_speed
#        self.hp = hp
#        self.time_of_last_attack = datetime.datetime.now()
#        self.last_took_damage = datetime.datetime.now(

class Player(Entity):
    def __init__(self, max_speed, data, screen, hp_coefficient, damage, tile_data, mana_coefficient, base_mana, presets):
        

        super().__init__(pygame.rect.Rect((screen.get_width() - data.width)//2, (screen.get_height() - data.height)//2, data.width, data.height), max_speed, presets[0], presets[1], damage)



        self.__rect_data = data
        self.__rect_data.center += pygame.Vector2(tile_data[0] + data.width//2, tile_data[1] + data.height//2)
        self.__true_center = self.__rect_data.center
        self.__start_position = copy.copy(self.__rect_data.center)
        self.screen = screen

        self.__camera_pos = data.topleft - pygame.Vector2(self.screen.get_width() + data.width, self.screen.get_height() + data.height)//2

        self.__mana_coefficient = mana_coefficient
        self.__hp_coefficient = hp_coefficient
        self.__base_mana = base_mana
        self.__exp = presets[6]
        self.__level = presets[7]
        self.__required_exp = 50 +  self.__level * 10


        self.__current_mana = presets[3]
        self.__max_mana = presets[4]
        self.__mana_restore_speed = presets[5]
        self.__hp_restore_speed = presets[2]

        self.__laser_mana = 5
        self.__heal_mana = 5

        self.__time_of_heal = datetime.datetime.now()
        self.__target_hp = self.max_hp
        self.__healing = False

        self.__acceleration = 15
        self.__velocity = pygame.Vector2(0, 0)
        self.__asset_index = -1.1
        self.opacity = 255
        self.alert = False

        self.new_level = False

    def gain_exp(self, amount):
        self.__exp += amount
        while self.__exp >= self.__required_exp:
            self.level_up()

    def level_up(self):
        self.__required_exp += 10
        self.__exp = 0
        self.__level += 1

        self.damage += 5
        self.__max_mana += self.__mana_coefficient
        self.__current_mana += self.__mana_coefficient
        self.max_hp += self.__hp_coefficient
        self.hp += self.__hp_coefficient

        self.__mana_restore_speed += 0.1
        self.__hp_restore_speed += 0.1

    def display(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: # Forward
            if abs(self.__velocity.y) < abs(self.__velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__asset_index = -1.1
        if keys[pygame.K_a]: # Left
            if abs(self.__velocity.x) < abs(self.__velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__asset_index = -1.2

        if keys[pygame.K_s]: # Down
            if abs(self.__velocity.y) < abs(self.__velocity.x) or not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.__asset_index = -1.3

        if keys[pygame.K_d]: # Right
            if abs(self.__velocity.x) < abs(self.__velocity.y) or not(keys[pygame.K_w] or keys[pygame.K_s]):
                self.__asset_index = -1.4
                
        # Checks to see what keys are being held to determine which one is most recently pressed.
        # From this it determines what direction the player should be facing.
        # It also works so if you stop pressing anything the character still faces the same direction.

        super().display(self.screen, self.__asset_index, self.visual_data, self.opacity)

    def restore(self):
        if self.__current_mana < self.__max_mana:
            self.__current_mana += self.__mana_restore_speed * self.dt
        if self.hp < self.max_hp:
            self.hp += self.__hp_restore_speed * self.dt
        
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_TAB] and self.__current_mana >= 0 and (datetime.datetime.now() - self.__time_of_heal).total_seconds() > 3:
            self.__time_of_heal = datetime.datetime.now()
            self.__healing = True
        if self.__healing:
            self.hp += 2 * self.__heal_mana * self.dt
            self.__current_mana -= self.__heal_mana * self.dt
        if (self.hp >= self.max_hp or self.__current_mana <= 0) and self.__healing:
            self.__current_mana = max(0, self.__current_mana)
            self.__healing = False

    def take_damage(self, amount, dx):
        if (datetime.datetime.now() - self.last_took_damage).total_seconds() >= 0.7:
            self.hp -= amount
            self.__velocity = dx.normalize() * self.max_speed * 5

    def ability(self):
        time_difference = (datetime.datetime.now() - self.time_of_last_attack).total_seconds()
        if time_difference > 5:
            self.alert = False
        #Holy laser beam 
        if pygame.mouse.get_pressed()[0] and self.__current_mana >= self.__laser_mana and time_difference > 1.5: # Left mouse button, 3s cooldown
            self.__healing = False
            self.time_of_last_attack = datetime.datetime.now()
            self.__current_mana -= self.__laser_mana
            mouse_pos = pygame.mouse.get_pos()
            angle = math.degrees(math.atan2(self.screen.get_height()//2 - mouse_pos[1], mouse_pos[0] - self.screen.get_width()//2))
            time = 0.2
            damage = self.damage
            asset_index = -4
            object_data = pygame.rect.Rect(self.screen.get_width()//2, self.screen.get_height()//2, 24, 24)
            self.alert = True
            return ["Holy_Ray", [object_data, time, damage, asset_index, angle, 480]]


        #Force
        elif pygame.mouse.get_pressed()[2] and time_difference > 0.7: # Right mouse button, 0.5s cooldown
            self.__current_mana -= 1
            self.__healing = False
            self.time_of_last_attack = datetime.datetime.now()
            width = self.visual_data.width//2
            height = self.visual_data.height//2
            time = 0.4
            damage = self.damage
            asset_index = -5
            self.alert = True
            
           
            match self.__asset_index:
                case -1.1: # Up

                    start_position_data = pygame.rect.Rect(self.visual_data.left - width, self.visual_data.top - height, width, height)
                    destination = pygame.Vector2(self.visual_data.right, self.visual_data.top - height)

                    return ["Force", [start_position_data, time, damage, asset_index, destination]]
                case -1.2: # Left
                    start_position_data = pygame.rect.Rect(self.visual_data.left - width, self.visual_data.bottom, width, height)
                    destination = pygame.Vector2(self.visual_data.left - width, self.visual_data.top - height)

                    return ["Force", [start_position_data, time, damage, asset_index, destination]]
                case -1.3: # Down
                    start_position_data = pygame.rect.Rect(self.visual_data.right, self.visual_data.bottom, width, height)
                    destination = pygame.Vector2(self.visual_data.left - width, self.visual_data.bottom)

                    return ["Force", [start_position_data, time, damage, asset_index, destination]]
                case -1.4: # Right
                    start_position_data = pygame.rect.Rect(self.visual_data.right, self.visual_data.top - height, width, height)
                    destination = pygame.Vector2(self.visual_data.right, self.visual_data.bottom)
                    return ["Force", [start_position_data, time, damage, asset_index, destination]]

        return [False]

# 1280 x 800
# (640, 400)

    def move(self):
        keys = pygame.key.get_pressed()
        #horizontal motion
        if keys[pygame.K_a]:
            self.__healing = False
            self.__velocity.x -= self.__acceleration * self.dt
            if abs(self.__velocity.x) >= self.max_speed:
                self.__velocity.x = self.__velocity.x/abs(self.__velocity.x) * self.max_speed
        if keys[pygame.K_d]:
            self.__healing = False
            self.__velocity.x += self.__acceleration * self.dt
            if abs(self.__velocity.x) >= self.max_speed:
                self.__velocity.x = self.__velocity.x/abs(self.__velocity.x) * self.max_speed
        if not(keys[pygame.K_a] or keys[pygame.K_d]):
            if self.__velocity.x <= 0.5 and self.__velocity.x >= -0.5:
                self.__velocity.x = 0
            else:
                self.__velocity.x *= 0.85
        #vertical motion
        if keys[pygame.K_w]:
            self.__healing = False
            self.__velocity.y -= self.__acceleration * self.dt
            if abs(self.__velocity.y) >= self.max_speed:
                self.__velocity.y = self.__velocity.y/abs(self.__velocity.y) * self.max_speed
        if keys[pygame.K_s]:
            self.__healing = False
            self.__velocity.y += self.__acceleration * self.dt
            if abs(self.__velocity.y) >= self.max_speed:
                self.__velocity.y = self.__velocity.y/abs(self.__velocity.y) * self.max_speed
        if not(keys[pygame.K_w] or keys[pygame.K_s]):
            if self.__velocity.y <= 0.5 and self.__velocity.y >= -0.5:
                self.__velocity.y = 0
            else:
                self.__velocity.y *= 0.85

    def collide(self, tile_data):


        #entity-tilemap collision
        tile_width = tile_data["tilewidth"]
        tile_height = tile_data["tileheight"]
        object_list = tile_data["layers"][0]["data"]
        map_columns = tile_data["width"]
        map_rows = tile_data["height"]

        start_col = int(self.__rect_data.left // tile_width - 1)
        end_col = int(self.__rect_data.right // tile_width)
        start_row = int(self.__rect_data.top // tile_height - 1)
        end_row = int(self.__rect_data.bottom // tile_height)


        self.__original_velocity = copy.copy(self.__velocity)

        if start_row < 0 or end_row > map_rows or start_col < 0 or end_col > map_columns:
            self.__true_center += self.__velocity
            self.__rect_data.center = self.__true_center
            self.__camera_pos += self.__velocity
            return

        #Checking all tiles the entity is touching
        for row in range(start_row, end_row):  
            for column in range(start_col, end_col):

                index = (row * map_columns) + column
                object_rect = pygame.rect.Rect(column * tile_width - self.__camera_pos.x, row * tile_height - self.__camera_pos.y, tile_width, tile_height)

                if object_list[index] in asset_library.collision_tiles: #If object is touching a collision tile
                    # checking which direction it should be moved (and how much)
                    dx = min(abs(self.visual_data.right - object_rect.left), abs(self.visual_data.left - object_rect.right))
                    dy = min(abs(self.visual_data.bottom - object_rect.top), abs(self.visual_data.top - object_rect.bottom))
                    if self.visual_data.colliderect(object_rect):
                        if dx < dy:
                            if self.__original_velocity.x > 0:
                                self.__velocity.x = -dx
                            else:
                                self.__velocity.x = dx
                        else:
                            if self.__original_velocity.y > 0:
                                self.__velocity.y = -dy
                            else:
                                self.__velocity.y = dy
                if object_list[index] in asset_library.level_change_tiles:
                    self.new_level = True
                if object_list[index] in asset_library.damage_tiles:
                    self.hp -= 8
        self.__true_center += self.__velocity
        self.__rect_data.center = self.__true_center
        self.__camera_pos += self.__velocity

    def change_level(self):
        self.__rect_data.center = self.__start_position
        self.__velocity = pygame.Vector2(0, 0)
        self.new_level = False

        return [self.hp, self.max_hp, self.__hp_restore_speed, self.__current_mana, self.__max_mana, self.__mana_restore_speed, self.__exp, self.__level]
    
    def export_data(self):
        
        data = {
            "velocity": self.__velocity,
            "visual data": self.visual_data,
            "true data": self.__rect_data,
            "camera position": self.__camera_pos,

            "hp": self.hp,
            "max hp": self.max_hp,

            "max mana": self.__max_mana,
            "current mana": self.__current_mana,


            "exp": self.__exp,
            "required exp": self.__required_exp,
            "level": self.__level,

            "new level": self.new_level,

            "alert": self.alert
        }
        return data


class UI:
    def __init__(self, screen):
        self.__screen = screen       
    def update_data(self, data):

        self.__large_font = asset_library.fonts["large font"]
        self.__small_font = asset_library.fonts["small font"]
        self.__bar_length = 128

        self.__backing_bar = pygame.surface.Surface((1, 1))
        self.__backing_bar.fill((40, 40, 40))


        self.__hp_sprite = pygame.surface.Surface((1, 1))
        self.__hp_sprite.fill((255, 50, 50))
        self.__player_hp = int(data["hp"])
        self.__player_max_hp = int(data["max hp"])
        self.__hp_bar_length = self.__player_hp / self.__player_max_hp * self.__bar_length
        self.__hp_backing_bar = pygame.surface.Surface((1, 1))
        self.__hp_backing_bar.fill((78, 29, 29))

        
        self.__mana_sprite = pygame.surface.Surface((1, 1))
        self.__mana_sprite.fill((50, 50, 255))
        self.__current_mana = int(data["current mana"])
        self.__max_mana = int(data["max mana"])
        self.__mana_bar_length = self.__current_mana / self.__max_mana * self.__bar_length
        self.__mana_backing_bar = pygame.surface.Surface((1, 1))
        self.__mana_backing_bar.fill((29, 29, 78))


        self.__exp_sprite = pygame.surface.Surface((1, 1))
        self.__exp_sprite.fill((50, 255, 50))
        self.__player_exp = data["exp"]
        self.__required_exp = data["required exp"]
        self.__exp_bar_length = self.__player_exp / self.__required_exp * self.__bar_length
        self.__exp_backing_bar = pygame.surface.Surface((1, 1))
        self.__exp_backing_bar.fill((29, 78, 29))

        self.__player_level = int(data["level"])

        self.__player_position = data["true data"] 

    def health_bar(self):
        self.__screen.blit(pygame.transform.scale(self.__hp_backing_bar, (self.__bar_length, 18)), (70, 20))
        if self.__player_hp >= 0:
            self.__screen.blit(pygame.transform.scale(self.__hp_sprite, (self.__hp_bar_length, 18)), (70, 20))
        text_surface = self.__small_font.render(f"{self.__player_hp} / {self.__player_max_hp}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.right = 65 + self.__bar_length
        text_rect.centery = 31
        self.__screen.blit(text_surface, text_rect)
    def mana_bar(self):
        self.__screen.blit(pygame.transform.scale(self.__mana_backing_bar, (self.__bar_length, 18)), (80, 45))
        if self.__current_mana >= 0:
            self.__screen.blit(pygame.transform.scale(self.__mana_sprite, (self.__mana_bar_length, 18)), (80, 45))
        text_surface = self.__small_font.render(f"{self.__current_mana} / {self.__max_mana}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.right = 75 + self.__bar_length
        text_rect.centery = 56
        self.__screen.blit(text_surface, text_rect)
    def exp_bar(self):
        self.__screen.blit(pygame.transform.scale(self.__exp_backing_bar, (self.__bar_length, 18)), (70, 70))
        self.__screen.blit(pygame.transform.scale(self.__exp_sprite, (self.__exp_bar_length, 18)), (70, 70))
        text_surface = self.__small_font.render(f"{self.__player_exp} / {self.__required_exp}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.right = 65 + self.__bar_length
        text_rect.centery = 81
        self.__screen.blit(text_surface, text_rect)

    def level(self):
        pygame.draw.ellipse(self.__screen, (203, 149, 80), pygame.rect.Rect(15, 5, 70, 90))
        center_ellipse_rect = pygame.rect.Rect(20, 10, 60, 80)
        pygame.draw.ellipse(self.__screen, (200, 200, 200), center_ellipse_rect)

        width = self.__large_font.size(str(self.__player_level))[0] - 3
        height = self.__large_font.get_ascent()

        text_x = center_ellipse_rect.left + (center_ellipse_rect.width - width)//2
        text_y = center_ellipse_rect.top + (center_ellipse_rect.height - height)//2

        self.__screen.blit(self.__large_font.render(f"{self.__player_level}", True, (255, 255, 255)), (text_x, text_y))

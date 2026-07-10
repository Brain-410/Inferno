import pygame
from Backend.Media.asset_library import asset_library
import datetime

class Object:
    def display(self, screen, type, data):
        screen.blit(pygame.transform.scale(asset_library[type], (data.width, data.height)), tuple(data.center))

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
    def __init__(self, data, max_speed, max_distance, detection_range, hp):
        self.dt = 0.016
        self.rect_data = data
        self.position = self.rect_data.center

        self.__max_speed = max_speed
        self.__max_distance_squared = max_distance**2
        self.__detection_range_squared = detection_range**2
        self.__aggro = False
        self.__hp = hp
        self.__last_took_damage = datetime.datetime.now()

    def display(self, screen):
        Object.display(self, screen, -2, self.rect_data)

    def move(self, data):
        Object.move(self, data[0])


        distance = (pygame.Vector2(640, 400) - self.rect_data.center).magnitude_squared()
        dx = (pygame.Vector2(640, 400) - self.rect_data.center).normalize()

        if distance > 2.25 * self.__detection_range_squared:
            self.__aggro = False
        elif distance < self.__detection_range_squared:
            self.__aggro = True

        if self.__aggro:
            if distance > self.__max_distance_squared:
                self.position += dx * self.__max_speed * self.dt
            else:
                self.position -= dx * self.__max_speed * 0.5 * self.dt
        
        new_pos = pygame.rect.Rect(data[2].left + data[2].width//2 - self.rect_data.width//2, 
                                   data[2].top + data[2].height//2 - self.rect_data.height//2, 
                                   data[2].width, data[2].height)
        while self.rect_data.colliderect(new_pos):
            self.position -= dx * 0.01
            self.rect_data.center = self.position
        self.rect_data.center = self.position

    def take_damage(self, attack_data, amount):
        if self.rect_data.colliderect(attack_data) and (datetime.datetime.now() - self.__last_took_damage).total_seconds() > 0.5:
            self.__last_took_damage = datetime.datetime.now()
            self.__hp -= amount
        if self.__hp <= 0:
            return True


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

                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x + 2.25*width, pos_y), 0.4, 20, False]]
                case -1.2:
                    pos_x = self.real_data.left - self.real_data.width // 4
                    pos_y = self.real_data.bottom + self.real_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y - 2.25*height), 0.4, 20, False]]
                case -1.3:
                    pos_x = self.real_data.right + self.real_data.width // 8
                    pos_y = self.real_data.bottom + self.real_data.height // 4
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x - 2.25*width, pos_y), 0.4, 20, False]]
                case -1.4:
                    pos_x = self.real_data.right + self.real_data.width // 4
                    pos_y = self.real_data.top - self.real_data.height // 8
                    return [True, [pygame.rect.Rect(pos_x, pos_y, width, height), pygame.Vector2(pos_x, pos_y + 2.25*height), 0.4, 20, False]]
        
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
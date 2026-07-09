import pygame
from Backend.Media.asset_library import asset_library
import datetime



class Object:
    def display(self, screen, type, position):
        screen.blit(asset_library[type], position)

    def move(self, velocity: pygame.Vector2):
        self.position -= velocity

class Attack(Object):
    def __init__(self, position, destination, time):
        self.__position = position
        self.__destination = destination
        self.__time = time
        self.__speed = (self.__position - self.__destination).magnitude() / self.__time
        self.dt = 0.016
    def display(self, screen):
        Object.display(self, screen, -3, tuple(self.__position))
    def move(self):
        print((self.__destination - self.__position).normalize())
        self.__position += (self.__destination - self.__position).normalize() * self.dt * self.__speed
        if (self.__position - self.__destination).magnitude() < 1:
            return True


class Entity(Object):
    def __init__(self, start_pos, max_speed, distance, detection_range, hp):
        self.position = start_pos
        self.__max_speed = max_speed
        self.__distance = distance
        self.__detection_range = detection_range
        self.__aggro = False
        self.__hp = hp
        self.dt = 0.016
    def display(self, screen):
        Object.display(self, screen, -2, self.position)
    def move(self, velocity):
        Object.move(self, velocity)
        distance = pygame.Vector2(640, 400) - self.position
        if distance.magnitude() > 1.5 * self.__detection_range:
            self.__aggro = False
        elif distance.magnitude() < self.__detection_range:
            self.__aggro = True

        if self.__aggro:
            if distance.magnitude() > self.__distance:
                self.position += distance.normalize() * self.__max_speed * self.dt
            else:
                self.position -= distance.normalize() * self.__max_speed * 0.5 * self.dt
    def collide(self):
        pass

    def take_damage(self, amount):
        self.__hp -= amount
        if self.__hp <= 0:
            print("Ded")

class Objects(Object):
    def display(self, screen, type, position):
        Object.display(screen, type, position)
    def move(self, velocity):
        Object.move(self, velocity)
    def collide(self):
        pass

class Player(Object):
    def __init__(self, max_speed):
        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.real_position = pygame.Vector2(100, 100)
        self.__type = -1.1
        self.__time_of_last_attack = datetime.datetime.now()
        self.damage_data = None

    
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
        Object.display(self, screen, self.__type, (screen.get_width() // 2 - 16, screen.get_height() // 2 - 16))
    
    def attack(self):
        if pygame.mouse.get_pressed()[0] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 5: # Left mouse button, 1s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            # Holy laser beam
        elif pygame.mouse.get_pressed()[2] and (datetime.datetime.now() - self.__time_of_last_attack).total_seconds() > 1: # Right mouse button, 1s cooldown
            self.__time_of_last_attack = datetime.datetime.now()
            # Mace attack
            match self.__type:
                case -1.1:
                    return [True, [pygame.Vector2(600, 370), pygame.Vector2(672, 370), 1]]
                case -1.2:
                    return [True, [pygame.Vector2(600, 400), pygame.Vector2(600, 370), 1]]
                case -1.3:
                    return [True, [pygame.Vector2(600, 400), pygame.Vector2(672, 400), 1]]
                case -1.4:
                    return [True, [pygame.Vector2(600, 370), pygame.Vector2(672, 370), 1]]
        
        return [False]

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
        self.real_position += self.velocity
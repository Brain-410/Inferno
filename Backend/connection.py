import pygame
import Backend.general as general

character = general.Player(pygame.Vector2(600, 300), [30, 30], "blue", 2)
object_list = [general.Object(pygame.Vector2(20, 20), [5, 5], None, "red")]
entity_list = []

def player(screen, dt):
    character.dt = dt
    character.display(screen)
    character.move()
    return character.velocity

def entities(screen, dt, velocity):
    for entity in entity_list:
        entity.display(screen)
        entity.move(velocity)
        entity.dt = dt

def objects(screen, dt, velocity):
    for object in object_list:
        object.display(screen)
        object.move(velocity)
        object.dt = dt

def background(screen, dt):
    screen.fill("Black")

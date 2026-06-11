import pygame

ANCHO = 800
ALTO = 480

BLANCO = (255,255,255)
NEGRO = (0,0,0)
VERDE = (0,255,0)
ROJO = (255,0,0)
GRIS = (50,50,50)



import pygame


def musica_menu():

    pygame.mixer.music.load(
        "sonidos/menu.wav"
    )

    pygame.mixer.music.set_volume(0.5)

    pygame.mixer.music.play(-1)


def musica_batalla():

    pygame.mixer.music.load(
        "sonidos/musica.wav"
    )

    pygame.mixer.music.set_volume(0.5)

    pygame.mixer.music.play(-1)
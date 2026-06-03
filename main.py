import pygame
from batalla import batalla
from batalla import pantalla_victoria
from batalla import pantalla_derrota
from batalla import pantalla_final

pygame.init()

for nivel in [1,2,3]:

    ganado = batalla(nivel)

    if ganado:

        if nivel < 3:
            pantalla_victoria(nivel)

        else:
            pantalla_final()

    else:

        pantalla_derrota(nivel)

pygame.quit()
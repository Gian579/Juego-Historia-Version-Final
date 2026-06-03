import pygame
import sys
import time
import random

from preguntas import obtener_preguntas
from configuracion import *

pygame.init()
pygame.mixer.init()

# ventana

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Historia del Perú RPG")

# fuente(cambiala por la de rojo fuego)

fuente = pygame.font.SysFont("arial", 24)

# musica pokemon

pygame.mixer.music.load("sonidos/musica.wav")
pygame.mixer.music.set_volume(0.3)
#si fuera 0 reproduce solo una vez 
#si es 1 dos veces y asi
pygame.mixer.music.play(-1)

# efectos de sonido meme

correcto_sound = pygame.mixer.Sound("sonidos/correcto.wav")
incorrecto_sound = pygame.mixer.Sound("sonidos/incorrecto.wav")
victoria_sound = pygame.mixer.Sound("sonidos/victoria.wav")
derrota_sound = pygame.mixer.Sound("sonidos/derrota.wav")

# fondo

fondo = pygame.image.load("fondos/aula.png")
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# ASSETS aunque creo que debo cambiar el fondo para que se vean
#ambos sprites


estudiante_normal = pygame.image.load("sprites/estudiante1.png")
estudiante_damage = pygame.image.load("sprites/estudiantedamage1.png")

profesor1 = pygame.image.load("sprites/profesor1.png")
profesor1_damage = pygame.image.load("sprites/profesordamage1.png")

profesor2 = pygame.image.load("sprites/profesor2.png")
profesor2_damage = pygame.image.load("sprites/profesordamage2.png")

profesor3 = pygame.image.load("sprites/profesor3.png")
profesor3_damage = pygame.image.load("sprites/profesordamage3.png")

# las imagenes en una resolucion de 180

estudiante_normal = pygame.transform.scale(estudiante_normal, (170, 170))
estudiante_damage = pygame.transform.scale(estudiante_damage, (170, 170))

profesor1 = pygame.transform.scale(profesor1, (180, 180))
profesor1_damage = pygame.transform.scale(profesor1_damage, (180, 180))

profesor2 = pygame.transform.scale(profesor2, (180, 180))
profesor2_damage = pygame.transform.scale(profesor2_damage, (180, 180))

profesor3 = pygame.transform.scale(profesor3, (180, 180))
profesor3_damage = pygame.transform.scale(profesor3_damage, (180, 180))

# logiCAPCOM

def dibujar_barra(x, y, vida, color):

    pygame.draw.rect(pantalla, GRIS, (x, y, 200, 25))
    pygame.draw.rect(pantalla, color, (x, y, vida * 2, 25))

#texto centrado


def texto(mensaje, x, y, color=BLANCO, centrado=False):

    render = fuente.render(mensaje, True, color)

    if centrado:

        rect = render.get_rect(center=(x, y))
        pantalla.blit(render, rect)

    else:

        pantalla.blit(render, (x, y))




def efecto_golpe(sprite_profesor, sprite_estudiante):

    pantalla.blit(fondo, (0, 0))

    pantalla.blit(sprite_profesor, (540, 50))
    pantalla.blit(sprite_estudiante, (70, 120))

    pygame.display.update()

    time.sleep(0.4)

#Importante

def dibujar_opciones(opciones):

    botones = []

    # caja izquierda

    posiciones_izquierda = [
        (40, 275),
        (40, 325),
        (40, 375)
    ]

    # caja derechap

    posicion_derecha = (420, 325)

    # las 3 de la izq

    for i in range(3):

        rect = pygame.Rect(
            posiciones_izquierda[i][0],
            posiciones_izquierda[i][1],
            300,
            40
        )

        pygame.draw.rect(pantalla, NEGRO, rect)
        pygame.draw.rect(pantalla, BLANCO, rect, 3)

        texto(
            opciones[i],
            posiciones_izquierda[i][0] + 15,
            posiciones_izquierda[i][1] + 8
        )

        botones.append((rect, opciones[i]))

    # derechad

    rect = pygame.Rect(
        posicion_derecha[0],
        posicion_derecha[1],
        300,
        40
    )

    pygame.draw.rect(pantalla, NEGRO, rect)
    pygame.draw.rect(pantalla, BLANCO, rect, 3)

    texto(
        opciones[3],
        posicion_derecha[0] + 15,
        posicion_derecha[1] + 8
    )

    botones.append((rect, opciones[3]))

    return botones


# Victory royale

def pantalla_victoria(nivel):

    victoria_sound.play()

    esperando = True

    while esperando:

        pantalla.fill(NEGRO)

        texto(
            "EXAMEN APROBADO",
            400,
            150,
            BLANCO,
            True
        )

        texto(
            f"Avanzas al examen {nivel + 1}",
            400,
            220,
            BLANCO,
            True
        )

        texto(
            "ENTER para continuar",
            400,
            300,
            BLANCO,
            True
        )

        pygame.display.update()

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_RETURN:
                    esperando = False


# Pantalla derrota :(

def pantalla_derrota(nivel):

    derrota_sound.play()

    mensajes = {

        1: "El profesor cree que no estudiaste.",
        2: "Fuiste enviado al sustitutorio.",
        3: "El examen final destruyó tu promedio."

    }

    esperando = True

    while esperando:

        pantalla.fill(NEGRO)

        texto(
            "DERROTA",
            400,
            140,
            ROJO,
            True
        )

        texto(
            mensajes[nivel],
            400,
            220,
            BLANCO,
            True
        )

        texto(
            "ESC para salir",
            400,
            300,
            BLANCO,
            True
        )

        pygame.display.update()

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# pantalla finalll

def pantalla_final():

    victoria_sound.play()

    esperando = True

    while esperando:

        pantalla.fill(NEGRO)

        texto(
            "FELICITACIONES",
            400,
            120,
            BLANCO,
            True
        )

        texto(
            "APROBASTE HISTORIA DEL PERÚ",
            400,
            200,
            BLANCO,
            True
        )

        texto(
            "Tu promedio ha sido salvado :)",
            400,
            260,
            BLANCO,
            True
        )

        texto(
            "ESC para salir",
            400,
            340,
            BLANCO,
            True
        )

        pygame.display.update()

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# batalla

def batalla(nivel):
    # TIEMPO SEGUN NIVEL

    if nivel == 1:
        tiempo_max = 20

    elif nivel == 2:
        tiempo_max = 15

    else:
        tiempo_max = 10


    vida_profesor = 100
    vida_estudiante = 100

    preguntas = obtener_preguntas(nivel)

    indice = 0

    pregunta_actual = preguntas[indice]

    opciones_mezcladas = pregunta_actual["opciones"].copy()
    random.shuffle(opciones_mezcladas)

    tiempo_inicio = pygame.time.get_ticks()
    profesores_normales = [
        profesor1,
        profesor2,
        profesor3
    ]

    profesores_damage = [
        profesor1_damage,
        profesor2_damage,
        profesor3_damage
    ]

    profesor_normal = profesores_normales[nivel - 1]
    profesor_damage = profesores_damage[nivel - 1]

    sprite_profesor = profesor_normal
    sprite_estudiante = estudiante_normal

    while True:

        tiempo_actual = pygame.time.get_ticks()

        segundos_restantes = tiempo_max - (
        (tiempo_actual - tiempo_inicio) // 1000
            )
            #dibuja sobre otra cosa 
            #el más grande primero
        pantalla.blit(fondo, (0, 0))

        
            #personajes
        pantalla.blit(sprite_profesor, (540, 50))
        pantalla.blit(sprite_estudiante, (70, 120))

        # Barra de vida

        dibujar_barra(540, 30, vida_profesor, ROJO)
        dibujar_barra(40, 30, vida_estudiante, VERDE)

        texto("PROFESOR", 560, 0)
        texto("ESTUDIANTE", 40, 0)
        # CONTADOR DE TIEMPO

        texto(
            f"{max(segundos_restantes,0)}s",
            400,
            60,
            BLANCO,
            True
        )


        # caja de opciones(Como heroe en smash)

        pygame.draw.rect(
            pantalla,
            NEGRO,
            (20, 220, 760, 220)
        )

        pygame.draw.rect(
            pantalla,
            BLANCO,
            (20, 220, 760, 220),
            4
        )

        
        texto(
            pregunta_actual["pregunta"],
            40,
            235,
            BLANCO
        )


        botones = dibujar_opciones(
            opciones_mezcladas
        )

        pygame.display.update()

        if segundos_restantes <= 0:

            incorrecto_sound.play()

            vida_estudiante -= 10

            sprite_estudiante = estudiante_damage

            efecto_golpe(
                sprite_profesor,
                sprite_estudiante
            )

            sprite_estudiante = estudiante_normal

            indice += 1


            tiempo_inicio = pygame.time.get_ticks()

            tiempo_inicio = pygame.time.get_ticks()

            if indice >= len(preguntas):
                preguntas = obtener_preguntas(nivel)
                indice = 0

            if vida_estudiante <= 0:
                return False

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = pygame.mouse.get_pos()

                for boton, opcion in botones:

                    if boton.collidepoint(mouse_pos):

                        # correctou

                        if opcion == pregunta_actual["correcta"]:

                            correcto_sound.play()

                            vida_profesor -= 10

                            sprite_profesor = profesor_damage

                            efecto_golpe(
                                sprite_profesor,
                                sprite_estudiante
                            )

                            sprite_profesor = profesor_normal

                        # incorrectou

                        else:

                            incorrecto_sound.play()

                            vida_estudiante -= 10

                            sprite_estudiante = estudiante_damage

                            efecto_golpe(
                                sprite_profesor,
                                sprite_estudiante
                            )

                            sprite_estudiante = estudiante_normal

                        indice += 1

                        # reiniciar

                        if indice >= len(preguntas):

                            preguntas = obtener_preguntas(nivel)
                            indice = 0
                        pregunta_actual = preguntas[indice]

                        opciones_mezcladas = pregunta_actual["opciones"].copy()
                        random.shuffle(opciones_mezcladas)

                        tiempo_inicio = pygame.time.get_ticks()

                        # ganastep

                        if vida_profesor <= 0:
                            return True

                        # jaja perdistep

                        if vida_estudiante <= 0:
                            return False
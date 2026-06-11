import pygame
import sys
from configuracion import musica_menu
pygame.init()

ANCHO = 800
ALTO = 480

pantalla = pygame.display.set_mode((ANCHO, ALTO))

# ---------- CARGAR IMAGENES ----------

fondo = pygame.image.load(
    "fondos/menu_fondo.png"
)

titulo = pygame.image.load(
    "assets_menu/titulo.png"
)

btn_modo = pygame.image.load(
    "assets_menu/btn_modo.png"
)

btn_modo_hover = pygame.image.load(
    "assets_menu/btn_modo_hover.png"
)

btn_preguntas = pygame.image.load(
    "assets_menu/btn_preguntas.png"
)

btn_preguntas_hover = pygame.image.load(
    "assets_menu/btn_preguntas_hover.png"
)

btn_salir = pygame.image.load(
    "assets_menu/btn_salir.png"
)

btn_salir_hover = pygame.image.load(
    "assets_menu/btn_salir_hover.png"
)

# ---------- ESCALAR ----------

fondo = pygame.transform.scale(
    fondo,
    (800,480)
)

titulo = pygame.transform.scale(
    titulo,
    (400,120)
)

btn_modo = pygame.transform.scale(
    btn_modo,
    (280,50)
)

btn_modo_hover = pygame.transform.scale(
    btn_modo_hover,
    (280,50)
)

btn_preguntas = pygame.transform.scale(
    btn_preguntas,
    (280,50)
)

btn_preguntas_hover = pygame.transform.scale(
    btn_preguntas_hover,
    (280,50)
)

btn_salir = pygame.transform.scale(
    btn_salir,
    (280,50)
)

btn_salir_hover = pygame.transform.scale(
    btn_salir_hover,
    (280,50)
)

# ---------- POSICIONES ----------

titulo_rect = titulo.get_rect(
    center=(400,90)
)

modo_rect = pygame.Rect(
    260,
    180,
    280,
    50
)

preguntas_rect = pygame.Rect(
    260,
    245,
    280,
    50
)

salir_rect = pygame.Rect(
    260,
    310,
    280,
    50
)

# ---------- MENU ----------

def mostrar_menu():

    # Reproducir música del menú una sola vez
    if not pygame.mixer.music.get_busy():

        pygame.mixer.music.load(
            "sonidos/menu.wav"
        )

        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()

    while True:

        mouse = pygame.mouse.get_pos()

        pantalla.blit(fondo, (0, 0))
        pantalla.blit(titulo, titulo_rect)

        # BOTON MODO

        if modo_rect.collidepoint(mouse):

            pantalla.blit(
                btn_modo_hover,
                modo_rect
            )

        else:

            pantalla.blit(
                btn_modo,
                modo_rect
            )

        # BOTON PREGUNTAS

        if preguntas_rect.collidepoint(mouse):

            pantalla.blit(
                btn_preguntas_hover,
                preguntas_rect
            )

        else:

            pantalla.blit(
                btn_preguntas,
                preguntas_rect
            )

        # BOTON SALIR

        if salir_rect.collidepoint(mouse):

            pantalla.blit(
                btn_salir_hover,
                salir_rect
            )

        else:

            pantalla.blit(
                btn_salir,
                salir_rect
            )

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:

                if modo_rect.collidepoint(mouse):

                    return "modo"

                if preguntas_rect.collidepoint(mouse):

                    return "preguntas"

                if salir_rect.collidepoint(mouse):

                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)
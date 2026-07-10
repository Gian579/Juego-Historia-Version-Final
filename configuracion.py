import os
import pygame

os.environ["SDL_VIDEO_CENTERED"] = "1"

# Resolución lógica interna — siempre 800x480
# El escalado a pantalla completa se maneja con _surface_juego
ANCHO = 800
ALTO  = 480

BLANCO = (255, 255, 255)
NEGRO  = (0,   0,   0)
VERDE  = (0,   200, 80)
ROJO   = (220, 50,  50)
GRIS   = (50,  50,  50)

RESOLUCIONES = [
    (800,  480,  "800x480  (Estandar)"),
    (1280, 720,  "1280x720  (HD)"),
    (0,    0,    "Pantalla completa"),
]

# Dificultad
DIFICULTAD_NIVELES = [1, 2, 3]
DIFICULTAD_NOMBRE  = "Facil"

# Modo pantalla completa activo
FULLSCREEN = False

def aplicar_resolucion(ancho, alto):
    """
    Cambia el modo de ventana.
    El juego SIEMPRE dibuja en 800x480 internamente;
    en fullscreen/HD esa superficie se escala a la ventana real.
    ANCHO/ALTO se mantienen en 800x480 para que todo el código
    de posicionamiento no cambie.
    """
    global FULLSCREEN
    if ancho == 0 and alto == 0:
        FULLSCREEN = True
        pygame.display.set_mode((0, 0),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    else:
        FULLSCREEN = False
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.display.set_mode((ancho, alto))

def get_surface_juego():
    """
    Devuelve una Surface 800x480 donde el juego dibuja.
    En fullscreen/HD, esta surface se escala luego a la ventana real.
    """
    return pygame.Surface((ANCHO, ALTO))

def presentar(pantalla_real, surface_juego):
    """
    Escala surface_juego (800x480) a la ventana real y hace flip.
    """
    W, H = pantalla_real.get_size()
    if (W, H) == (ANCHO, ALTO):
        pantalla_real.blit(surface_juego, (0, 0))
    else:
        escalada = pygame.transform.smoothscale(surface_juego, (W, H))
        pantalla_real.blit(escalada, (0, 0))
    pygame.display.flip()

def musica_menu():
    pygame.mixer.music.load("sonidos/menu.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def musica_batalla():
    pygame.mixer.music.load("sonidos/musica.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Preguntas personalizadas (se llena desde menu_preguntas.py)
# {nivel_int: [lista de preguntas]}
PREGUNTAS_CUSTOM = {}

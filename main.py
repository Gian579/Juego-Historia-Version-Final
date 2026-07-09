import pygame
import sys
from menu import mostrar_menu
import configuracion
from configuracion import musica_batalla, musica_menu
from batalla import batalla, pantalla_victoria, pantalla_derrota, pantalla_final
from menu_preguntas import mostrar_editor

def _run_niveles(niveles, preguntas_custom=None):
    """
    Corre la secuencia de niveles.
    Retorna cuando el flujo termina (al menú o al salir).
    """
    errores_por_nivel = {}
    fallos_por_nivel  = {}

    for i, nivel in enumerate(niveles):
        es_ultimo = (i == len(niveles) - 1)
        pregs     = preguntas_custom.get(nivel, None) if preguntas_custom else None

        ganado, errores, total, fallos = batalla(nivel, preguntas_custom=pregs)
        errores_por_nivel[nivel] = (errores, total)
        fallos_por_nivel[nivel]  = fallos

        if ganado:
            if not es_ultimo:
                res = pantalla_victoria(nivel, errores, total, fallos, es_ultimo=False)
                if res == "continuar":
                    musica_batalla()
                    continue          # siguiente nivel
                elif res == "menu":
                    musica_menu(); return
                elif res == "salir":
                    pygame.quit(); sys.exit()
            else:
                res = pantalla_final(errores_por_nivel, fallos_por_nivel)
                if res == "menu":
                    musica_menu(); return
                elif res == "salir":
                    pygame.quit(); sys.exit()
        else:
            res = pantalla_derrota(nivel, errores, total, fallos)
            if res == "menu":
                musica_menu(); return
            elif res == "salir":
                pygame.quit(); sys.exit()

while True:
    opcion = mostrar_menu()

    if opcion == "modo":
        musica_batalla()
        _run_niveles(configuracion.DIFICULTAD_NIVELES)

    elif opcion == "preguntas":
        resultado_editor = mostrar_editor()
        if resultado_editor == "empezar":
            musica_batalla()
            _run_niveles(configuracion.DIFICULTAD_NIVELES,
                         preguntas_custom=configuracion.PREGUNTAS_CUSTOM)
        else:
            musica_menu()

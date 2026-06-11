from menu import mostrar_menu
from batalla import batalla
from configuracion import musica_batalla
from batalla import batalla
from batalla import pantalla_victoria
from batalla import pantalla_derrota
from batalla import pantalla_final

while True:

    opcion = mostrar_menu()

    if opcion == "modo":

        musica_batalla()

        for nivel in [1,2,3]:

            ganado = batalla(nivel)

            if ganado:

                if nivel < 3:
                    pantalla_victoria(nivel)

                else:
                    pantalla_final()

            else:

                pantalla_derrota(nivel)
                break
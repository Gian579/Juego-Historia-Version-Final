import pygame
import sys
import time
import random

from preguntas import obtener_preguntas
import configuracion

pygame.init()
pygame.mixer.init()

W = configuracion.ANCHO   # 800 lógico
H = configuracion.ALTO    # 480 lógico

correcto_sound   = pygame.mixer.Sound("sonidos/correcto.wav")
incorrecto_sound = pygame.mixer.Sound("sonidos/incorrecto.wav")
victoria_sound   = pygame.mixer.Sound("sonidos/victoria.wav")
derrota_sound    = pygame.mixer.Sound("sonidos/derrota.wav")

# ── Assets ────────────────────────────────────────────────────────
_fondo_orig   = pygame.image.load("fondos/aula.png")
_est_n_orig   = pygame.image.load("sprites/estudiante1.png")
_est_d_orig   = pygame.image.load("sprites/estudiantedamage1.png")
_profe_orig   = [pygame.image.load(f"sprites/profesor{i}.png")       for i in range(1,4)]
_profe_d_orig = [pygame.image.load(f"sprites/profesordamage{i}.png") for i in range(1,4)]

def _s(surf, w, h):
    return pygame.transform.smoothscale(surf, (max(1,int(w)), max(1,int(h))))

SP     = 170
_fondo   = _s(_fondo_orig, W, H)
_est_n   = _s(_est_n_orig, SP, SP)
_est_d   = _s(_est_d_orig, SP, SP)
_profe_n = [_s(img, SP+10, SP+10) for img in _profe_orig]
_profe_d = [_s(img, SP+10, SP+10) for img in _profe_d_orig]

POS_EST  = (60,  120)
POS_PROF = (540, 50)

# ── Fuentes ───────────────────────────────────────────────────────
_f22 = pygame.font.SysFont("arial", 22)
_f17 = pygame.font.SysFont("arial", 17)
_f15 = pygame.font.SysFont("arial", 15)
_f28 = pygame.font.SysFont("arial", 28, bold=True)
_f13 = pygame.font.SysFont("arial", 13, bold=True)
_f12 = pygame.font.SysFont("arial", 12)

# ── HUD ──────────────────────────────────────────────────────────
HUD_H      = 44
BAR_W      = 200
BAR_H      = 18
BAR_Y      = 6
LBL_Y      = BAR_Y + BAR_H + 3
BAR_EST_X  = 10
BAR_PROF_X = W - 10 - BAR_W   # 590
MUTE_X     = 455
MUTE_W     = 52
MUTE_H     = 28
MUTE_Y     = (HUD_H - MUTE_H) // 2
MUTE_RECT  = pygame.Rect(MUTE_X, MUTE_Y, MUTE_W, MUTE_H)

def _dibujar_hud(surf, vida_prof, vida_est, segs, silenciado, errores=0, total_preg=0):
    bg = pygame.Surface((W, HUD_H), pygame.SRCALPHA)
    bg.fill((0,0,0,190))
    surf.blit(bg, (0,0))

    # Barra estudiante
    pygame.draw.rect(surf, configuracion.GRIS,  (BAR_EST_X, BAR_Y, BAR_W, BAR_H))
    pygame.draw.rect(surf, configuracion.VERDE,
                     (BAR_EST_X, BAR_Y, int(max(vida_est,0)/100*BAR_W), BAR_H))
    pygame.draw.rect(surf, configuracion.BLANCO, (BAR_EST_X, BAR_Y, BAR_W, BAR_H), 2)
    surf.blit(_f15.render(f"EST  {max(vida_est,0)}%", True, configuracion.BLANCO),
              (BAR_EST_X, LBL_Y))

    # Barra profesor
    pygame.draw.rect(surf, configuracion.GRIS,   (BAR_PROF_X, BAR_Y, BAR_W, BAR_H))
    pygame.draw.rect(surf, configuracion.ROJO,
                     (BAR_PROF_X, BAR_Y, int(max(vida_prof,0)/100*BAR_W), BAR_H))
    pygame.draw.rect(surf, configuracion.BLANCO, (BAR_PROF_X, BAR_Y, BAR_W, BAR_H), 2)
    surf.blit(_f15.render(f"PROF  {max(vida_prof,0)}%", True, configuracion.BLANCO),
              (BAR_PROF_X, LBL_Y))

    # Contador centrado
    if segs is not None:
        color = configuracion.ROJO if segs <= 5 else configuracion.BLANCO
        t = _f28.render(f"{max(segs,0)}s", True, color)
        surf.blit(t, t.get_rect(center=(370, HUD_H//2)))

    # Botón MUTE
    cm = (170,40,40) if silenciado else (40,150,70)
    pygame.draw.rect(surf, cm,                   MUTE_RECT, border_radius=6)
    pygame.draw.rect(surf, configuracion.BLANCO, MUTE_RECT, 2, border_radius=6)
    etiq = _f13.render("MUTE" if not silenciado else " ON ", True, configuracion.BLANCO)
    surf.blit(etiq, (MUTE_RECT.centerx - etiq.get_width()//2,
                     MUTE_RECT.centery - etiq.get_height()//2))

    # Errores (esquina izquierda debajo barra, solo si hay info)
    if total_preg > 0:
        color_err = configuracion.ROJO if errores > 0 else configuracion.VERDE
        err_txt = _f12.render(f"Errores: {errores}", True, color_err)
        surf.blit(err_txt, (BAR_EST_X, LBL_Y + 16))

    return MUTE_RECT.copy()


# ── Caja pregunta + opciones 2×2 ─────────────────────────────────
CAJA_X = 20
CAJA_Y = 230
CAJA_W = 760
CAJA_H = 220
PAD    = 10

def _dibujar_caja(surf, pregunta_txt, opciones, feedback=None):
    pygame.draw.rect(surf, configuracion.NEGRO,  (CAJA_X, CAJA_Y, CAJA_W, CAJA_H))
    pygame.draw.rect(surf, configuracion.BLANCO, (CAJA_X, CAJA_Y, CAJA_W, CAJA_H), 4)

    pq = _f17.render(pregunta_txt, True, configuracion.BLANCO)
    surf.blit(pq, (CAJA_X+PAD, CAJA_Y+PAD))

    sep = CAJA_Y + PAD + pq.get_height() + PAD
    pygame.draw.line(surf, configuracion.GRIS, (CAJA_X+4,sep), (CAJA_X+CAJA_W-4,sep), 1)

    area_y = sep + PAD
    area_h = (CAJA_Y+CAJA_H) - area_y - PAD
    area_w = CAJA_W - PAD*2
    bw = (area_w - PAD) // 2
    bh = (area_h - PAD) // 2

    posiciones = [
        (CAJA_X+PAD,           area_y),
        (CAJA_X+PAD+bw+PAD,    area_y),
        (CAJA_X+PAD,           area_y+bh+PAD),
        (CAJA_X+PAD+bw+PAD,    area_y+bh+PAD),
    ]

    botones = []
    for i, op in enumerate(opciones):
        rx,ry  = posiciones[i]
        rect   = pygame.Rect(rx,ry,bw,bh)
        cfondo = configuracion.NEGRO
        if feedback and op in feedback:
            cfondo = feedback[op]
        pygame.draw.rect(surf, cfondo,              rect, border_radius=6)
        pygame.draw.rect(surf, configuracion.BLANCO, rect, 2, border_radius=6)
        s = _f17.render(op, True, configuracion.BLANCO)
        surf.blit(s, (rx+8, ry+(bh-s.get_height())//2))
        botones.append((rect, op))
    return botones


# ── Frame completo ────────────────────────────────────────────────
def _frame(vida_prof, vida_est, segs, pregunta, opciones,
           silenciado, sp, se, errores=0, total_preg=0, feedback=None):
    surf = configuracion.get_surface_juego()
    surf.blit(_fondo, (0,0))
    surf.blit(sp, POS_PROF)
    surf.blit(se, POS_EST)
    mute_rect = _dibujar_hud(surf, vida_prof, vida_est, segs,
                              silenciado, errores, total_preg)
    bots = _dibujar_caja(surf, pregunta["pregunta"], opciones, feedback)
    configuracion.presentar(pygame.display.get_surface(), surf)
    return bots, mute_rect

def _efecto(vida_prof, vida_est, pregunta, opciones,
            silenciado, sp, se, feedback, errores=0, total_preg=0):
    surf = configuracion.get_surface_juego()
    surf.blit(_fondo, (0,0))
    surf.blit(sp, POS_PROF)
    surf.blit(se, POS_EST)
    _dibujar_hud(surf, vida_prof, vida_est, None, silenciado, errores, total_preg)
    _dibujar_caja(surf, pregunta["pregunta"], opciones, feedback)
    configuracion.presentar(pygame.display.get_surface(), surf)
    time.sleep(0.35)


# ── Pantallas de resultado ────────────────────────────────────────

# Fuentes para pantallas de resultado
_f_res_tit  = pygame.font.SysFont("arial", 26, bold=True)
_f_res_sub  = pygame.font.SysFont("arial", 16, bold=True)
_f_res_item = pygame.font.SysFont("arial", 14)
_f_res_btn  = pygame.font.SysFont("arial", 15, bold=True)

def _btn_resultado(surf, rect, texto, color_bg):
    pygame.draw.rect(surf, color_bg, rect, border_radius=8)
    pygame.draw.rect(surf, configuracion.BLANCO, rect, 2, border_radius=8)
    t = _f_res_btn.render(texto, True, configuracion.BLANCO)
    surf.blit(t, t.get_rect(center=rect.center))

def _pantalla_resultado(sonido, titulo, color_titulo, lineas_info, fallos,
                        mostrar_continuar=False):
    """
    Pantalla rica con:
    - Título (victoria / derrota)
    - Líneas de info (nivel, errores, etc.)
    - Lista scrolleable de fallos [(pregunta, tu_respuesta, correcta)]
    - Botones: Continuar (opcional) | Menú | Salir
    Retorna "continuar", "menu" o "salir"
    """
    pygame.mixer.music.stop()
    sonido.play()
    scroll   = 0
    clock    = pygame.time.Clock()
    ITEM_H   = 52
    LIST_X   = 20
    LIST_Y   = 175
    LIST_W   = W - 40
    VIS      = 4          # items visibles sin scroll

    if mostrar_continuar:
        BTN_CONT  = pygame.Rect(W//2 - 255, H - 44, 155, 34)
        BTN_MENU  = pygame.Rect(W//2 - 78,  H - 44, 155, 34)
        BTN_SALIR = pygame.Rect(W//2 + 99,  H - 44, 155, 34)
    else:
        BTN_CONT  = None
        BTN_MENU  = pygame.Rect(W//2 - 83,  H - 44, 155, 34)
        BTN_SALIR = pygame.Rect(W//2 + 82,  H - 44, 155, 34)

    while True:
        surf = configuracion.get_surface_juego()
        surf.fill((15, 15, 25))

        # Título
        t = _f_res_tit.render(titulo, True, color_titulo)
        surf.blit(t, t.get_rect(center=(W//2, 28)))

        # Líneas de info
        for i, (txt, col) in enumerate(lineas_info):
            r = _f_res_sub.render(txt, True, col)
            surf.blit(r, r.get_rect(center=(W//2, 65 + i*26)))

        # Cabecera lista de fallos
        if fallos:
            cab = _f_res_sub.render(
                f"Preguntas incorrectas ({len(fallos)}):", True, (200,200,100))
            surf.blit(cab, (LIST_X, LIST_Y - 22))

            # Items con scroll
            for vi in range(VIS):
                idx = scroll + vi
                if idx >= len(fallos): break
                preg_txt, elegida, correcta = fallos[idx]
                ry = LIST_Y + vi * (ITEM_H + 4)
                rect_item = pygame.Rect(LIST_X, ry, LIST_W, ITEM_H)

                pygame.draw.rect(surf, (40, 20, 20), rect_item, border_radius=6)
                pygame.draw.rect(surf, (180, 60, 60), rect_item, 2, border_radius=6)

                # Pregunta (truncada)
                preg_show = preg_txt[:68] + ("..." if len(preg_txt)>68 else "")
                surf.blit(_f_res_item.render(
                    f"{idx+1}. {preg_show}", True, configuracion.BLANCO),
                    (LIST_X+10, ry+5))
                # Tu respuesta (rojo) | Correcta (verde)
                surf.blit(_f_res_item.render(
                    f"  Tu respuesta: {elegida}", True, configuracion.ROJO),
                    (LIST_X+10, ry+22))
                surf.blit(_f_res_item.render(
                    f"  Correcta: {correcta}", True, configuracion.VERDE),
                    (LIST_X+10, ry+37))

            # Scroll arrows
            if scroll > 0:
                arr = pygame.Rect(W-38, LIST_Y, 28, 24)
                _btn_resultado(surf, arr, "▲", (60,60,100))
            if scroll + VIS < len(fallos):
                arr = pygame.Rect(W-38, LIST_Y + VIS*(ITEM_H+4) - 28, 28, 24)
                _btn_resultado(surf, arr, "▼", (60,60,100))
        else:
            msg = _f_res_sub.render("Sin errores — respuesta perfecta!", True, configuracion.VERDE)
            surf.blit(msg, msg.get_rect(center=(W//2, 260)))

        # Botones
        if BTN_CONT:
            _btn_resultado(surf, BTN_CONT,  "Continuar ►",      (0, 130, 60))
        _btn_resultado(surf, BTN_MENU,  "← Volver al menú", (50, 80, 160))
        _btn_resultado(surf, BTN_SALIR, "Salir del juego",   (140, 40, 40))

        configuracion.presentar(pygame.display.get_surface(), surf)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "menu"
            if ev.type == pygame.MOUSEBUTTONDOWN:
                rw, rh = pygame.display.get_surface().get_size()
                lx = int(ev.pos[0] * W / rw)
                ly = int(ev.pos[1] * H / rh)
                pos_l = (lx, ly)
                if BTN_CONT and BTN_CONT.collidepoint(pos_l):
                    return "continuar"
                if BTN_MENU.collidepoint(pos_l):
                    return "menu"
                if BTN_SALIR.collidepoint(pos_l):
                    return "salir"
                # Scroll arrows
                if fallos:
                    arr_u = pygame.Rect(W-38, LIST_Y, 28, 24)
                    arr_d = pygame.Rect(W-38, LIST_Y+VIS*(ITEM_H+4)-28, 28, 24)
                    if arr_u.collidepoint(pos_l) and scroll > 0:
                        scroll -= 1
                    if arr_d.collidepoint(pos_l) and scroll+VIS < len(fallos):
                        scroll += 1
            if ev.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - ev.y, max(0, len(fallos)-VIS)))

        clock.tick(60)


def pantalla_victoria(nivel, errores=0, total=0, fallos=None, es_ultimo=False):
    lineas = [
        (f"NIVEL {nivel} APROBADO  —  {errores} errores de {total}",
         configuracion.ROJO if errores > 0 else configuracion.VERDE),
    ]
    return _pantalla_resultado(
        victoria_sound, "EXAMEN APROBADO", configuracion.VERDE,
        lineas, fallos or [],
        mostrar_continuar=not es_ultimo)

def pantalla_derrota(nivel, errores=0, total=0, fallos=None):
    msgs = {1: "El profesor cree que no estudiaste.",
            2: "Fuiste enviado al sustitutorio.",
            3: "El examen final destruyo tu promedio."}
    lineas = [
        (msgs[nivel], configuracion.BLANCO),
        (f"Errores: {errores} de {total} preguntas",
         configuracion.ROJO if errores > 0 else configuracion.VERDE),
    ]
    return _pantalla_resultado(
        derrota_sound, "DERROTA", configuracion.ROJO,
        lineas, fallos or [])

def pantalla_final(errores_por_nivel=None, fallos_por_nivel=None):
    if errores_por_nivel:
        total_e = sum(e for e,_ in errores_por_nivel.values())
        total_p = sum(t for _,t in errores_por_nivel.values())
        lineas = []
        for niv, (e, t) in sorted(errores_por_nivel.items()):
            color_e = configuracion.ROJO if e > 0 else configuracion.VERDE
            lineas.append((f"Nivel {niv}: {e} errores de {t}", color_e))
        color_tot = configuracion.ROJO if total_e > 0 else configuracion.VERDE
        lineas.append((f"Total: {total_e} / {total_p}", color_tot))
    else:
        lineas = [("Juego completado", configuracion.VERDE)]

    # Juntar todos los fallos de todos los niveles
    todos_fallos = []
    if fallos_por_nivel:
        for niv in sorted(fallos_por_nivel.keys()):
            for f in fallos_por_nivel[niv]:
                todos_fallos.append(f)

    return _pantalla_resultado(
        victoria_sound, "FELICITACIONES", configuracion.VERDE,
        lineas, todos_fallos)
    lineas.append(("ENTER para salir", configuracion.BLANCO))
    _pantalla_simple(lineas, victoria_sound)
    pygame.quit(); sys.exit()


# ── Batalla ───────────────────────────────────────────────────────
def batalla(nivel, preguntas_custom=None):
    """
    Juega una batalla.
    preguntas_custom: lista de preguntas ya seleccionadas (modo personalizado).
    Retorna (ganado: bool, errores: int, total_preguntas: int)
    """
    tiempo_max = {1:20, 2:15, 3:10}[nivel]
    silenciado = False
    errores    = 0
    fallos     = []   # [(pregunta_txt, elegida, correcta)]

    prof_n = _profe_n[nivel-1]
    prof_d = _profe_d[nivel-1]

    vida_prof = 100
    vida_est  = 100

    if preguntas_custom:
        preguntas = preguntas_custom.copy()
        random.shuffle(preguntas)
    else:
        preguntas = obtener_preguntas(nivel)

    total_preguntas = len(preguntas)
    respondidas     = 0
    indice  = 0
    pregunta = preguntas[indice]
    opciones = pregunta["opciones"].copy(); random.shuffle(opciones)

    sp = prof_n
    se = _est_n
    t0 = pygame.time.get_ticks()
    clock = pygame.time.Clock()

    while True:
        segs = tiempo_max - (pygame.time.get_ticks()-t0)//1000
        bots, mute_rect = _frame(vida_prof, vida_est, segs,
                                  pregunta, opciones, silenciado, sp, se,
                                  errores, respondidas)
        # Tiempo agotado
        if segs <= 0:
            incorrecto_sound.play()
            errores += 1
            respondidas += 1
            correcta = pregunta["correcta"]
            fallos.append((pregunta["pregunta"], "[Tiempo agotado]", correcta))
            cf = {op:(configuracion.VERDE if op==correcta else configuracion.ROJO)
                  for op in opciones}
            _efecto(vida_prof, vida_est, pregunta, opciones,
                    silenciado, sp, _est_d, cf, errores, respondidas)
            vida_est -= 10
            if vida_est <= 0:
                return False, errores, respondidas, fallos, fallos
            indice = (indice+1) % len(preguntas)
            if indice == 0:
                if preguntas_custom:
                    return vida_prof < vida_est, errores, respondidas, fallos
                preguntas = obtener_preguntas(nivel)
            pregunta = preguntas[indice]
            opciones = pregunta["opciones"].copy(); random.shuffle(opciones)
            t0 = pygame.time.get_ticks()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                        configuracion.aplicar_resolucion(800, 480)

            if ev.type == pygame.MOUSEBUTTONDOWN:
                rw, rh = pygame.display.get_surface().get_size()
                lx = int(ev.pos[0] * W / rw)
                ly = int(ev.pos[1] * H / rh)
                pos_l = (lx, ly)

                if mute_rect.collidepoint(pos_l):
                    silenciado = not silenciado
                    pygame.mixer.music.set_volume(0 if silenciado else 0.5)
                    continue

                for boton, opcion in bots:
                    if boton.collidepoint(pos_l):
                        correcta = pregunta["correcta"]
                        cf = {op:(configuracion.VERDE if op==correcta else configuracion.ROJO)
                              for op in opciones}
                        respondidas += 1
                        if opcion == correcta:
                            correcto_sound.play()
                            _efecto(vida_prof, vida_est, pregunta, opciones,
                                    silenciado, prof_d, se, cf, errores, respondidas)
                            vida_prof -= 10
                        else:
                            incorrecto_sound.play()
                            errores += 1
                            fallos.append((pregunta["pregunta"], opcion, correcta))
                            _efecto(vida_prof, vida_est, pregunta, opciones,
                                    silenciado, sp, _est_d, cf, errores, respondidas)
                            vida_est -= 10

                        if vida_prof <= 0:
                            return True, errores, respondidas, fallos
                        if vida_est  <= 0:
                            return False, errores, respondidas, fallos

                        indice = (indice+1) % len(preguntas)
                        if indice == 0:
                            if preguntas_custom:
                                return vida_prof < vida_est, errores, respondidas, fallos
                            preguntas = obtener_preguntas(nivel)
                        pregunta = preguntas[indice]
                        opciones = pregunta["opciones"].copy(); random.shuffle(opciones)
                        t0 = pygame.time.get_ticks()

        clock.tick(60)

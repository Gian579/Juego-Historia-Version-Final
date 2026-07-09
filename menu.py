import pygame
import sys
import configuracion
from configuracion import RESOLUCIONES

pygame.init()

# Ventana inicial 800x480
_pantalla_real = pygame.display.set_mode((800, 480))
pygame.display.set_caption("Historia del Peru RPG")

# ── Assets originales ─────────────────────────────────────────────
_fondo_orig  = pygame.image.load("fondos/menu_fondo.png")
_titulo_orig = pygame.image.load("assets_menu/titulo.png")
_btn_orig = {
    "modo":  pygame.image.load("assets_menu/btn_modo.png"),
    "modoh": pygame.image.load("assets_menu/btn_modo_hover.png"),
    "preg":  pygame.image.load("assets_menu/btn_preguntas.png"),
    "pregh": pygame.image.load("assets_menu/btn_preguntas_hover.png"),
    "sal":   pygame.image.load("assets_menu/btn_salir.png"),
    "salh":  pygame.image.load("assets_menu/btn_salir_hover.png"),
}

W = configuracion.ANCHO   # siempre 800
H = configuracion.ALTO    # siempre 480

def _smooth(surf, w, h):
    return pygame.transform.smoothscale(surf, (max(1,int(w)), max(1,int(h))))

# Assets escalados a 800x480 (resolución lógica fija)
_fondo  = _smooth(_fondo_orig,  W, H)
_titulo = _smooth(_titulo_orig, W//2, H//4)
_btns = {k: _smooth(v, int(W*0.35), int(H*0.104)) for k,v in _btn_orig.items()}

bw = int(W * 0.35)
bh = int(H * 0.104)
cx = W // 2
titulo_rect    = pygame.Rect(cx - bw, int(H*0.08), bw*2, H//4)
modo_rect      = pygame.Rect(cx - bw//2, int(H*0.375), bw, bh)
preguntas_rect = pygame.Rect(cx - bw//2, int(H*0.51),  bw, bh)
salir_rect     = pygame.Rect(cx - bw//2, int(H*0.645), bw, bh)

# Botón RES — esquina sup derecha
gear_sz   = 36
gear_rect = pygame.Rect(W - gear_sz - 10, 8, gear_sz, gear_sz)

# ── Panel genérico ────────────────────────────────────────────────
def _panel(surf, titulo_txt, opciones, indice_actual, subtextos=None):
    """
    Dibuja panel sobre surf (800x480).
    subtextos: lista opcional de strings secundarios por opción.
    Devuelve (items [(Rect,idx)], close_rect).
    """
    pw = int(W * 0.70)
    ph = int(H * 0.72)
    px = (W - pw) // 2
    py = (H - ph) // 2

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    surf.blit(overlay, (0, 0))

    pygame.draw.rect(surf, (28,28,28),    (px, py, pw, ph), border_radius=12)
    pygame.draw.rect(surf, (200,200,200), (px, py, pw, ph), 3, border_radius=12)

    f_tit = pygame.font.SysFont("arial", 20, bold=True)
    surf.blit(f_tit.render(titulo_txt, True, (255,255,255)), (px+16, py+14))

    pygame.draw.line(surf, (80,80,80), (px+8,py+46), (px+pw-8,py+46), 1)

    f_main = pygame.font.SysFont("arial", 17, bold=True)
    f_sub  = pygame.font.SysFont("arial", 13)
    item_h = 52
    gap    = 8
    items  = []

    for i, label in enumerate(opciones):
        ry = py + 56 + i*(item_h+gap)
        rect_item = pygame.Rect(px+14, ry, pw-28, item_h)
        cfondo = (0,130,60) if i==indice_actual else (55,55,55)
        pygame.draw.rect(surf, cfondo,       rect_item, border_radius=8)
        pygame.draw.rect(surf, (160,160,160), rect_item, 2, border_radius=8)

        txt_m = f_main.render(label, True, (255,255,255))
        if subtextos and i < len(subtextos):
            surf.blit(txt_m, (rect_item.x+14, rect_item.y+8))
            txt_s = f_sub.render(subtextos[i], True, (200,200,200))
            surf.blit(txt_s, (rect_item.x+14, rect_item.y+28))
        else:
            surf.blit(txt_m, (
                rect_item.x+14,
                rect_item.y+(item_h-txt_m.get_height())//2
            ))
        items.append((rect_item, i))

    # Botón cerrar con "X" en Arial (sin Unicode especial)
    f_x        = pygame.font.SysFont("arial", 16, bold=True)
    close_rect = pygame.Rect(px+pw-34, py+7, 26, 26)
    pygame.draw.rect(surf, (160,40,40), close_rect, border_radius=5)
    xt = f_x.render("X", True, (255,255,255))
    surf.blit(xt, (close_rect.centerx-xt.get_width()//2,
                   close_rect.centery-xt.get_height()//2))

    return items, close_rect


# ── Función principal ─────────────────────────────────────────────
def mostrar_menu():
    global _pantalla_real

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("sonidos/menu.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    clock       = pygame.time.Clock()
    panel_res   = False
    panel_dif   = False   # se abre al clickear "Seleccionar Modo"

    DIFICULTADES  = ["Facil", "Medio", "Dificil"]
    SUBTEXTOS_DIF = [
        "Empiezas desde el Profesor 1  (3 batallas)",
        "Empiezas desde el Profesor 2  (2 batallas)",
        "Solo el Profesor 3  (1 batalla)",
    ]
    NIVELES_DIF = {
        "Facil":   [1,2,3],
        "Medio":   [2,3],
        "Dificil": [3],
    }

    def _idx_res():
        flags = pygame.display.get_surface().get_flags()
        if flags & pygame.FULLSCREEN:
            return 2
        return next((i for i,(rw,rh,_) in enumerate(RESOLUCIONES)
                     if rw==800 and rh==480), 0) if not configuracion.FULLSCREEN else 2

    def _idx_dif():
        return DIFICULTADES.index(configuracion.DIFICULTAD_NOMBRE)

    indice_res = _idx_res()
    indice_dif = _idx_dif()

    # dificultad pendiente para iniciar batalla después de confirmar
    _iniciar_batalla = False

    while True:
        # Surface lógica 800x480 donde dibujamos todo
        surf = configuracion.get_surface_juego()

        mouse_real = pygame.mouse.get_pos()
        # Convertir mouse a coordenadas lógicas 800x480
        real_w, real_h = pygame.display.get_surface().get_size()
        sx = W / real_w
        sy = H / real_h
        mouse = (int(mouse_real[0]*sx), int(mouse_real[1]*sy))

        # ── Fondo y botones ───────────────────────────────────────
        surf.blit(_fondo, (0,0))
        surf.blit(_smooth(_titulo_orig, titulo_rect.width, titulo_rect.height), titulo_rect)

        surf.blit(_btns["modoh"] if modo_rect.collidepoint(mouse)      else _btns["modo"],  modo_rect)
        surf.blit(_btns["pregh"] if preguntas_rect.collidepoint(mouse) else _btns["preg"],  preguntas_rect)
        surf.blit(_btns["salh"]  if salir_rect.collidepoint(mouse)     else _btns["sal"],   salir_rect)

        # ── Botón RES ─────────────────────────────────────────────
        gc = (255,215,0) if gear_rect.collidepoint(mouse) else (200,200,200)
        pygame.draw.rect(surf, (35,35,35), gear_rect, border_radius=7)
        pygame.draw.rect(surf, gc,         gear_rect, 2, border_radius=7)
        f_icon = pygame.font.SysFont("arial", 11, bold=True)
        gt = f_icon.render("RES", True, gc)
        surf.blit(gt, (gear_rect.centerx-gt.get_width()//2,
                       gear_rect.centery-gt.get_height()//2))

        # Etiqueta resolución activa
        f_lbl = pygame.font.SysFont("arial", 11)
        lbl   = f_lbl.render(RESOLUCIONES[indice_res][2].split("(")[0].strip(),
                              True, (180,180,180))
        surf.blit(lbl, (gear_rect.x, gear_rect.bottom+2))

        # ── Paneles ───────────────────────────────────────────────
        items_res, close_res = [], None
        items_dif, close_dif = [], None

        if panel_res:
            labels_res = [lb for _,_,lb in RESOLUCIONES]
            items_res, close_res = _panel(surf, "Resolucion de pantalla",
                                          labels_res, indice_res)

        if panel_dif:
            items_dif, close_dif = _panel(surf, "Seleccionar dificultad",
                                          DIFICULTADES, indice_dif,
                                          subtextos=SUBTEXTOS_DIF)

        # Presentar (escala 800x480 → ventana real)
        configuracion.presentar(pygame.display.get_surface(), surf)

        # ── Eventos ───────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN:
                # Convertir click a coordenadas lógicas
                rx, ry = ev.pos
                pos = (int(rx*sx), int(ry*sy))

                # Panel resolución
                if panel_res:
                    if close_res and close_res.collidepoint(pos):
                        panel_res = False; continue
                    for rect_item, idx in items_res:
                        if rect_item.collidepoint(pos):
                            rw,rh,_ = RESOLUCIONES[idx]
                            configuracion.aplicar_resolucion(rw, rh)
                            _pantalla_real = pygame.display.get_surface()
                            real_w, real_h = _pantalla_real.get_size()
                            indice_res = idx
                            panel_res  = False
                    continue

                # Panel dificultad
                if panel_dif:
                    if close_dif and close_dif.collidepoint(pos):
                        panel_dif = False; continue
                    for rect_item, idx in items_dif:
                        if rect_item.collidepoint(pos):
                            configuracion.DIFICULTAD_NOMBRE  = DIFICULTADES[idx]
                            configuracion.DIFICULTAD_NIVELES = NIVELES_DIF[DIFICULTADES[idx]]
                            indice_dif = idx
                            panel_dif  = False
                            return "modo"   # confirmar = iniciar batalla
                    continue

                # Botón RES
                if gear_rect.collidepoint(pos):
                    panel_res = not panel_res
                    panel_dif = False; continue

                # Botones menú
                if modo_rect.collidepoint(pos):
                    # Abrir panel de dificultad antes de empezar
                    panel_dif = True
                    panel_res = False
                    continue
                if preguntas_rect.collidepoint(pos):
                    return "preguntas"
                if salir_rect.collidepoint(pos):
                    pygame.quit(); sys.exit()

        clock.tick(60)

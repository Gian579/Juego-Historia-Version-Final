"""
Menú completo de preguntas personalizadas.
Flujo:
  TAB_AGREGAR  → formulario para agregar preguntas al banco
  TAB_SELECCION → elige qué preguntas tomar de cada nivel (10-15)
                  → botón "Empezar personalizada"
"""
import pygame, sys
import configuracion
import preguntas_custom as pc

W = configuracion.ANCHO   # 800 lógico
H = configuracion.ALTO    # 480 lógico

# ── Paleta ────────────────────────────────────────────────────────
BG       = (18,  18,  28)
PANEL    = (30,  30,  48)
BORDE    = (90,  90, 130)
ACENTO   = (80, 160, 255)
VERDE    = (60, 200, 90)
ROJO     = (220, 60,  60)
AMARILLO = (255, 210,  0)
BLANCO   = (240, 240, 240)
GRIS     = (120, 120, 140)
NEGRO    = (0,   0,   0)

# ── Fuentes ───────────────────────────────────────────────────────
pygame.font.init()
F_TITULO = pygame.font.SysFont("arial", 22, bold=True)
F_BTN    = pygame.font.SysFont("arial", 16, bold=True)
F_NORMAL = pygame.font.SysFont("arial", 15)
F_SMALL  = pygame.font.SysFont("arial", 13)
F_INPUT  = pygame.font.SysFont("arial", 14)

# ── Helpers ───────────────────────────────────────────────────────
def _smooth(surf, w, h):
    return pygame.transform.smoothscale(surf, (max(1,int(w)), max(1,int(h))))

def _rect_btn(surf, rect, texto, color_bg, color_txt=None, radio=7):
    if color_txt is None: color_txt = BLANCO
    pygame.draw.rect(surf, color_bg, rect, border_radius=radio)
    pygame.draw.rect(surf, BLANCO,   rect, 2,  border_radius=radio)
    t = F_BTN.render(texto, True, color_txt)
    surf.blit(t, t.get_rect(center=rect.center))

def _input_box(surf, rect, texto, activo, label=""):
    borde_c = ACENTO if activo else BORDE
    pygame.draw.rect(surf, (22,22,38), rect, border_radius=5)
    pygame.draw.rect(surf, borde_c,    rect, 2,  border_radius=5)
    if label:
        lbl = F_SMALL.render(label, True, GRIS)
        surf.blit(lbl, (rect.x, rect.y - 16))
    # texto con cursor si activo
    mostrar = texto + ("|" if activo and (pygame.time.get_ticks()//500)%2==0 else "")
    t = F_INPUT.render(mostrar, True, BLANCO)
    # clip para no salirse del box
    clip = surf.get_clip()
    surf.set_clip(rect.inflate(-6, -4))
    surf.blit(t, (rect.x+5, rect.y+(rect.height-t.get_height())//2))
    surf.set_clip(clip)

def _mouse_logico(real_pos):
    rw, rh = pygame.display.get_surface().get_size()
    return (int(real_pos[0]*W/rw), int(real_pos[1]*H/rh))

def _presentar(surf):
    configuracion.presentar(pygame.display.get_surface(), surf)


# ── ESTADO COMPARTIDO ─────────────────────────────────────────────
class Estado:
    tab         = 0          # 0=Agregar, 1=Selección
    nivel_form  = 1          # nivel seleccionado en el form
    campo_activo= 0          # 0=pregunta,1=op0,2=op1,3=op2,4=op3
    campos      = ["","","","",""]   # [pregunta, op0, op1, op2, op3]
    correcto_idx= 0          # cuál opción es la correcta (0-3)
    msg         = ""         # mensaje de feedback
    msg_color   = VERDE
    msg_timer   = 0

    # Selección
    nivel_sel   = 1          # nivel activo en pestaña selección
    seleccion   = {1:set(), 2:set(), 3:set()}   # índices seleccionados
    scroll      = {1:0, 2:0, 3:0}              # scroll del banco

    @classmethod
    def set_msg(cls, txt, color=VERDE):
        cls.msg       = txt
        cls.msg_color = color
        cls.msg_timer = pygame.time.get_ticks() + 2500

E = Estado

# ── TAB AGREGAR ──────────────────────────────────────────────────
_LABELS_CAMPO = ["Pregunta:", "Opción A:", "Opción B:", "Opción C:", "Opción D:"]

def _tab_agregar(surf, mouse):
    """Dibuja el formulario. Devuelve lista de Rects clickeables con tag."""
    clicks = []

    # Título
    t = F_TITULO.render("Agregar pregunta al banco", True, BLANCO)
    surf.blit(t, (20, 12))

    # Selector de nivel
    surf.blit(F_SMALL.render("Nivel:", True, GRIS), (20, 46))
    for i, (lbl, col) in enumerate([("1 Fácil",(60,180,60)),
                                     ("2 Medio",(220,170,0)),
                                     ("3 Difícil",(200,60,60))]):
        r = pygame.Rect(70 + i*95, 42, 88, 26)
        activo = (E.nivel_form == i+1)
        bg = col if activo else (45,45,65)
        pygame.draw.rect(surf, bg, r, border_radius=6)
        pygame.draw.rect(surf, BLANCO if activo else BORDE, r, 2, border_radius=6)
        surf.blit(F_SMALL.render(lbl, True, BLANCO), (r.x+8, r.y+6))
        clicks.append((r, f"nivel_{i+1}"))

    # Campos de texto
    FIELD_X = 24
    FIELD_W = 580
    for i in range(5):
        fy = 82 + i*58
        surf.blit(F_SMALL.render(_LABELS_CAMPO[i], True, GRIS), (FIELD_X, fy))
        rect_f = pygame.Rect(FIELD_X, fy+17, FIELD_W, 30)
        _input_box(surf, rect_f, E.campos[i], E.campo_activo==i)
        clicks.append((rect_f, f"campo_{i}"))

    # Radio botones "correcta"
    surf.blit(F_SMALL.render("¿Cuál es la correcta?", True, GRIS), (FIELD_X, 380))
    nombres_op = ["A","B","C","D"]
    for i in range(4):
        r = pygame.Rect(FIELD_X + i*80, 396, 70, 26)
        activo = (E.correcto_idx == i)
        pygame.draw.rect(surf, VERDE if activo else (45,45,65), r, border_radius=6)
        pygame.draw.rect(surf, BLANCO if activo else BORDE, r, 2, border_radius=6)
        surf.blit(F_SMALL.render(f"Op. {nombres_op[i]}", True, BLANCO), (r.x+8, r.y+6))
        clicks.append((r, f"correcta_{i}"))

    # Botones acción
    btn_add  = pygame.Rect(630, 82,  148, 36)
    btn_lim  = pygame.Rect(630, 130, 148, 36)
    btn_ver  = pygame.Rect(630, 178, 148, 36)

    # Contador por nivel
    for i in range(3):
        cnt = len(pc.get_banco(i+1))
        col = VERDE if cnt>=pc.MIN_POR_NIVEL else AMARILLO
        surf.blit(F_SMALL.render(f"Niv {i+1}: {cnt} pregs", True, col),
                  (630, 230+i*22))

    _rect_btn(surf, btn_add, "Agregar", (0,120,60))
    _rect_btn(surf, btn_lim, "Limpiar form", (60,60,100))
    _rect_btn(surf, btn_ver, "Ir a Seleccion", (0,80,160))
    clicks += [(btn_add,"agregar"),(btn_lim,"limpiar"),(btn_ver,"ir_sel")]

    # Mensaje
    if E.msg and pygame.time.get_ticks() < E.msg_timer:
        ms = F_NORMAL.render(E.msg, True, E.msg_color)
        surf.blit(ms, ms.get_rect(center=(W//2, 458)))

    return clicks


# ── TAB SELECCIÓN ─────────────────────────────────────────────────
ITEM_H   = 36
LIST_X   = 18
LIST_Y   = 100
LIST_W   = 640
LIST_VIS = 8    # items visibles a la vez

def _tab_seleccion(surf, mouse):
    clicks = []
    nivel = E.nivel_sel

    # Título
    t = F_TITULO.render("Seleccionar preguntas para jugar", True, BLANCO)
    surf.blit(t, (20, 12))

    # Tabs de nivel
    for i, (lbl,col) in enumerate([("Nivel 1",(60,180,60)),
                                    ("Nivel 2",(220,170,0)),
                                    ("Nivel 3",(200,60,60))]):
        r = pygame.Rect(20+i*115, 44, 108, 30)
        activo = (E.nivel_sel == i+1)
        bg = col if activo else (45,45,65)
        pygame.draw.rect(surf, bg, r, border_radius=6)
        pygame.draw.rect(surf, BLANCO if activo else BORDE, r, 2, border_radius=6)
        surf.blit(F_BTN.render(lbl, True, BLANCO), (r.x+14, r.y+7))
        clicks.append((r, f"tab_nivel_{i+1}"))

    # Contador selección
    n_sel = len(E.seleccion[nivel])
    color_cnt = VERDE if pc.MIN_POR_NIVEL<=n_sel<=pc.MAX_POR_NIVEL else ROJO
    surf.blit(F_SMALL.render(f"Seleccionadas: {n_sel}/{pc.MAX_POR_NIVEL}  (mín {pc.MIN_POR_NIVEL})",
                              True, color_cnt), (400, 50))

    # Lista del banco
    banco = pc.get_banco(nivel)
    scroll = E.scroll[nivel]

    if not banco:
        surf.blit(F_NORMAL.render("No hay preguntas en este nivel aún.", True, GRIS),
                  (LIST_X+10, LIST_Y+20))
    else:
        for vi in range(LIST_VIS):
            idx = scroll + vi
            if idx >= len(banco): break
            q    = banco[idx]
            ry   = LIST_Y + vi*ITEM_H
            rect = pygame.Rect(LIST_X, ry, LIST_W, ITEM_H-3)
            sel  = idx in E.seleccion[nivel]

            bg = (40,90,50) if sel else (35,35,55)
            pygame.draw.rect(surf, bg,    rect, border_radius=5)
            pygame.draw.rect(surf, VERDE if sel else BORDE, rect, 2, border_radius=5)

            # Checkbox: cuadrado con relleno, sin unicode
            cb = pygame.Rect(rect.x+6, rect.centery-9, 18, 18)
            pygame.draw.rect(surf, VERDE if sel else (50,50,75), cb, border_radius=4)
            pygame.draw.rect(surf, BLANCO, cb, 2, border_radius=4)
            if sel:
                # Palomita dibujada con líneas (sin unicode)
                cx, cy = cb.centerx, cb.centery
                pygame.draw.line(surf, BLANCO, (cx-5, cy),    (cx-1, cy+4), 2)
                pygame.draw.line(surf, BLANCO, (cx-1, cy+4),  (cx+5, cy-4), 2)

            # Pregunta — en la fila superior del item
            COLOR_PREG = VERDE if sel else BLANCO
            txt_q = q["pregunta"][:60] + ("..." if len(q["pregunta"])>60 else "")
            # Correcta pegada a la derecha de la pregunta, mismo color
            txt_correcta = f"  [OK: {q['correcta']}]"
            t_preg = F_SMALL.render(f"{idx+1}. {txt_q}", True, COLOR_PREG)
            t_corr = F_SMALL.render(txt_correcta, True, COLOR_PREG)
            texto_x = rect.x + 30
            surf.blit(t_preg, (texto_x, rect.centery - t_preg.get_height()//2))
            surf.blit(t_corr, (texto_x + t_preg.get_width(), rect.centery - t_corr.get_height()//2))

            # Botón eliminar
            del_r = pygame.Rect(rect.right-34, rect.y+6, 28, 22)
            pygame.draw.rect(surf, (140,30,30), del_r, border_radius=4)
            surf.blit(F_SMALL.render("X", True, BLANCO),
                      (del_r.centerx-4, del_r.y+4))
            clicks.append((del_r, f"eliminar_{nivel}_{idx}"))
            clicks.append((rect,  f"toggle_{nivel}_{idx}"))

        # Scroll arrows
        if scroll > 0:
            arr_u = pygame.Rect(LIST_X+LIST_W+8, LIST_Y, 26, 26)
            _rect_btn(surf, arr_u, "▲", (60,60,100))
            clicks.append((arr_u, "scroll_up"))
        if scroll+LIST_VIS < len(banco):
            arr_d = pygame.Rect(LIST_X+LIST_W+8, LIST_Y+LIST_VIS*ITEM_H-30, 26, 26)
            _rect_btn(surf, arr_d, "▼", (60,60,100))
            clicks.append((arr_d, "scroll_down"))

    # Botones inferiores
    btn_todo  = pygame.Rect(20,  442, 120, 30)
    btn_nada  = pygame.Rect(150, 442, 120, 30)
    btn_volver= pygame.Rect(460, 442, 140, 30)
    btn_start = pygame.Rect(610, 430, 172, 42)

    _rect_btn(surf, btn_todo,  "Sel. todos",   (50,80,130))
    _rect_btn(surf, btn_nada,  "Desel. todos", (80,50,50))
    _rect_btn(surf, btn_volver,"← Agregar más",(60,60,100))
    _rect_btn(surf, btn_start, "Empezar personalizada", (0,140,60))
    clicks += [(btn_todo,"sel_todo"),(btn_nada,"sel_nada"),
               (btn_volver,"ir_agregar"),(btn_start,"empezar")]

    # Mensaje
    if E.msg and pygame.time.get_ticks() < E.msg_timer:
        ms = F_NORMAL.render(E.msg, True, E.msg_color)
        surf.blit(ms, ms.get_rect(center=(W//2, 415)))

    return clicks


# ── LÓGICA DE CLICKS ─────────────────────────────────────────────
def _procesar(tag):
    """Procesa la acción del tag clickeado. Devuelve "empezar" o None."""
    # Nivel del formulario
    if tag.startswith("nivel_"):
        E.nivel_form = int(tag[-1]); return

    # Campo de texto
    if tag.startswith("campo_"):
        E.campo_activo = int(tag[-1]); return

    # Opción correcta
    if tag.startswith("correcta_"):
        E.correcto_idx = int(tag[-1]); return

    # Agregar pregunta
    if tag == "agregar":
        preg = E.campos[0].strip()
        ops  = [E.campos[i].strip() for i in range(1,5)]
        if not preg or any(o=="" for o in ops):
            E.set_msg("Completa todos los campos.", ROJO); return
        if len(set(ops)) < 4:
            E.set_msg("Las 4 opciones deben ser distintas.", ROJO); return
        correcta = ops[E.correcto_idx]
        err = pc.agregar_pregunta(E.nivel_form, preg, ops, correcta)
        if err:
            E.set_msg(err, ROJO)
        else:
            E.set_msg(f"Pregunta agregada al nivel {E.nivel_form}.", VERDE)
            E.campos = ["","","","",""]; E.correcto_idx = 0
        return

    # Limpiar
    if tag == "limpiar":
        E.campos = ["","","","",""]; E.correcto_idx = 0; E.msg = ""; return

    # Cambio de tab
    if tag == "ir_sel":   E.tab = 1; E.msg = ""; return
    if tag == "ir_agregar": E.tab = 0; E.msg = ""; return

    # Tab nivel selección
    if tag.startswith("tab_nivel_"):
        E.nivel_sel = int(tag[-1]); return

    # Toggle pregunta
    if tag.startswith("toggle_"):
        _, nivel_s, idx_s = tag.split("_")
        nivel = int(nivel_s); idx = int(idx_s)
        if idx in E.seleccion[nivel]:
            E.seleccion[nivel].discard(idx)
        else:
            if len(E.seleccion[nivel]) >= pc.MAX_POR_NIVEL:
                E.set_msg(f"Máximo {pc.MAX_POR_NIVEL} preguntas por nivel.", ROJO)
            else:
                E.seleccion[nivel].add(idx)
        return

    # Eliminar
    if tag.startswith("eliminar_"):
        parts = tag.split("_")
        nivel = int(parts[1]); idx = int(parts[2])
        pc.eliminar_pregunta(nivel, idx)
        E.seleccion[nivel] = {i if i<idx else i-1 for i in E.seleccion[nivel] if i!=idx}
        E.set_msg("Pregunta eliminada.", AMARILLO); return

    # Scroll
    if tag == "scroll_up":
        if E.scroll[E.nivel_sel]>0: E.scroll[E.nivel_sel]-=1; return
    if tag == "scroll_down":
        banco = pc.get_banco(E.nivel_sel)
        if E.scroll[E.nivel_sel]+LIST_VIS < len(banco):
            E.scroll[E.nivel_sel]+=1; return

    # Sel / Desel todos
    if tag == "sel_todo":
        banco = pc.get_banco(E.nivel_sel)
        E.seleccion[E.nivel_sel] = set(range(min(len(banco), pc.MAX_POR_NIVEL))); return
    if tag == "sel_nada":
        E.seleccion[E.nivel_sel] = set(); return

    # Empezar
    if tag == "empezar":
        # Validar solo los niveles que tienen preguntas seleccionadas
        niveles_activos = {n:sorted(list(s))
                           for n,s in E.seleccion.items() if s}
        if not niveles_activos:
            E.set_msg("Selecciona al menos un nivel con preguntas.", ROJO); return
        for n, idxs in niveles_activos.items():
            if len(idxs) < pc.MIN_POR_NIVEL:
                E.set_msg(f"Nivel {n}: mínimo {pc.MIN_POR_NIVEL} preguntas (tienes {len(idxs)}).", ROJO)
                return
        # Guardar en configuracion para que main.py lo use
        configuracion.PREGUNTAS_CUSTOM = {
            n: pc.get_seleccionadas(n, idxs)
            for n,idxs in niveles_activos.items()
        }
        configuracion.DIFICULTAD_NIVELES = sorted(niveles_activos.keys())
        return "empezar"


# ── TECLADO ──────────────────────────────────────────────────────
def _tecla(ev):
    if E.tab != 0: return
    if E.campo_activo < 0: return
    if ev.key == pygame.K_BACKSPACE:
        E.campos[E.campo_activo] = E.campos[E.campo_activo][:-1]
    elif ev.key == pygame.K_TAB or ev.key == pygame.K_RETURN:
        E.campo_activo = (E.campo_activo+1) % 5
    elif ev.key == pygame.K_ESCAPE:
        E.campo_activo = -1
    else:
        ch = ev.unicode
        if ch and len(E.campos[E.campo_activo]) < 80:
            E.campos[E.campo_activo] += ch


# ── MAIN LOOP ────────────────────────────────────────────────────
def mostrar_editor():
    """
    Muestra el editor de preguntas.
    Devuelve "empezar" si el usuario lanza la partida personalizada,
    o None si presiona ESC/volver.
    """
    # Resetear estado al entrar
    E.tab=0; E.msg=""; E.campos=["","","","",""]
    E.correcto_idx=0; E.campo_activo=0
    E.nivel_form=1; E.nivel_sel=1
    E.seleccion={1:set(),2:set(),3:set()}

    clock = pygame.time.Clock()

    while True:
        surf = configuracion.get_surface_juego()
        surf.fill(BG)
        mouse = _mouse_logico(pygame.mouse.get_pos())

        # Tabs superiores del editor
        for i,(lbl,col) in enumerate([("Agregar preguntas",(0,100,180)),
                                       ("Seleccionar y jugar",(0,140,60))]):
            r = pygame.Rect(0, 0, W//2, 0)   # placeholder, redefino abajo
            # barra de tabs fina arriba — pero lo dibujo como borde inferior
            pass

        # Fondo tab activo
        # (no necesitamos tabs gráficos extra, usamos el botón "Ir a Seleccion")

        clicks = []
        if E.tab == 0:
            clicks = _tab_agregar(surf, mouse)
        else:
            clicks = _tab_seleccion(surf, mouse)

        # Botón VOLVER (siempre visible)
        btn_back = pygame.Rect(W-110, 4, 106, 28)
        _rect_btn(surf, btn_back, "← Menú", (70,40,90))
        clicks.append((btn_back, "volver"))

        _presentar(surf)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                _tecla(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                pos = _mouse_logico(ev.pos)
                for rect, tag in clicks:
                    if rect.collidepoint(pos):
                        if tag == "volver":
                            return None
                        resultado = _procesar(tag)
                        if resultado == "empezar":
                            return "empezar"
                        break

        clock.tick(60)

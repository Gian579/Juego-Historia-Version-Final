"""
Módulo de preguntas personalizadas.
Guarda/carga en preguntas_custom.json al lado del juego.
Estructura JSON:
{
  "1": [ {pregunta, opciones:[4], correcta}, ... ],
  "2": [ ... ],
  "3": [ ... ]
}
"""
import json, os, random

# Guardar en AppData/Local/HistoriaDelPeruRPG para evitar problemas
# con OneDrive, permisos restringidos o carpetas de solo lectura.
# Si falla, cae de vuelta a la carpeta del juego.
def _get_archivo():
    try:
        appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or ""
        if appdata:
            carpeta = os.path.join(appdata, "HistoriaDelPeruRPG")
            os.makedirs(carpeta, exist_ok=True)
            # Prueba que puede escribir ahí
            test = os.path.join(carpeta, ".test_write")
            with open(test, "w") as f: f.write("ok")
            os.remove(test)
            return os.path.join(carpeta, "preguntas_custom.json")
    except Exception:
        pass
    # Fallback: carpeta del juego
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "preguntas_custom.json")

ARCHIVO = _get_archivo()
MIN_POR_NIVEL = 10
MAX_POR_NIVEL = 15

def _cargar_raw():
    if not os.path.exists(ARCHIVO):
        return {"1":[], "2":[], "3":[]}
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        data = json.load(f)
    for k in ["1","2","3"]:
        data.setdefault(k, [])
    return data

def _guardar(data):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_banco(nivel: int) -> list:
    """Devuelve todas las preguntas del nivel (sin mezclar)."""
    return _cargar_raw()[str(nivel)]

def agregar_pregunta(nivel: int, pregunta: str,
                     opciones: list, correcta: str) -> str:
    """
    Agrega una pregunta al banco del nivel.
    Devuelve "" si OK o mensaje de error.
    """
    data = _cargar_raw()
    key  = str(nivel)
    if len(data[key]) >= MAX_POR_NIVEL * 4:   # límite holgado del banco
        return "Banco lleno (max 60 por nivel). Elimina alguna primero."
    entrada = {"pregunta": pregunta, "opciones": opciones, "correcta": correcta}
    data[key].append(entrada)
    _guardar(data)
    return ""

def eliminar_pregunta(nivel: int, indice: int):
    data = _cargar_raw()
    key  = str(nivel)
    if 0 <= indice < len(data[key]):
        data[key].pop(indice)
        _guardar(data)

def get_seleccionadas(nivel: int, indices: list) -> list:
    """Devuelve las preguntas de los índices dados, mezcladas."""
    banco = get_banco(nivel)
    sel   = [banco[i] for i in indices if i < len(banco)]
    random.shuffle(sel)
    return sel

def validar_seleccion(seleccion_por_nivel: dict) -> str:
    """
    seleccion_por_nivel: {1:[idx,...], 2:[...], 3:[...]}
    Devuelve "" si OK, mensaje de error si no.
    """
    for nivel, idxs in seleccion_por_nivel.items():
        n = len(idxs)
        if n < MIN_POR_NIVEL:
            return f"Nivel {nivel}: mínimo {MIN_POR_NIVEL} preguntas (tienes {n})."
        if n > MAX_POR_NIVEL:
            return f"Nivel {nivel}: máximo {MAX_POR_NIVEL} preguntas (tienes {n})."
    return ""

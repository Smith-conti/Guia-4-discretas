import sys
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyArrowPatch

# ============================================================
# DEFINICIÓN DEL DFA
# ============================================================
# Reconocidas longitudes de cadena mayores o iguales a 2
# que comienzan con 'a' y terminan en q4

ESTADO_INICIAL = "q0"
ESTADOS_FINALES = {"q4"}
ALFABETO = {"a", "b"}

ESTADOS = {"q0", "q1", "q2", "q3", "q4"}

TRANSICIONES = {
    ("q0", "a"): "q1",
    ("q1", "a"): "q4",
    ("q1", "b"): "q4",
    ("q2", "a"): "q0",
    ("q2", "b"): "q1",
    ("q3", "b"): "q2",
    ("q4", "a"): "q4",
    ("q4", "b"): "q4",
}

# ============================================================
# CONSTANTES DE VISUALIZACIÓN
# ============================================================
TAM_NODO_ACTIVO = 900
TAM_NODO_NORMAL = 600
GROSOR_BORDE_FINAL = 3
GROSOR_BORDE_NORMAL = 1
SEED_LAYOUT = 7
PAUSA_SEGUNDOS = 1.0
MUTATION_SCALE = 18
SHRINK_ARROW = 6
FONT_SIZE_ARISTA = 11
FONT_SIZE_LOOP = 10
FONT_SIZE_TITULO = 12

# Parámetros para lazos (self-loops)
LOOP_RAD_PAR = 0.5
LOOP_RAD_IMPAR = -0.6
LOOP_DX = 0.08
LOOP_OFFSET_Y_PAR = 0.22
LOOP_OFFSET_Y_IMPAR = -0.22

# Parámetros para aristas normales
RADIO_CURVA_PAR = 0.18
RADIO_CURVA_IMPAR = -0.18
OFFSET_ETIQUETA_PAR = 0.10
OFFSET_ETIQUETA_IMPAR = -0.10


# ============================================================
# SIMULACIÓN
# ============================================================
def ejecutar(cadena: str) -> tuple[list[str], bool]:
    """Simula el DFA sobre la cadena dada.

    Args:
        cadena: Secuencia de símbolos del alfabeto.

    Returns:
        (historial_de_estados, acepta_o_no)
    """
    estado_actual = ESTADO_INICIAL
    historial = [estado_actual]

    for posicion, simbolo in enumerate(cadena):
        clave = (estado_actual, simbolo)
        if clave not in TRANSICIONES:
            raise ValueError(
                f"No hay transición desde {estado_actual} "
                f"con '{simbolo}' en la posición {posicion}"
            )
        estado_actual = TRANSICIONES[clave]
        historial.append(estado_actual)

    return historial, historial[-1] in ESTADOS_FINALES


# ============================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================
def construir_grafo() -> tuple[nx.MultiDiGraph, dict]:
    """Crea el grafo dirigido del DFA y calcula la posición de sus nodos."""
    grafo = nx.MultiDiGraph()
    grafo.add_nodes_from(ESTADOS)

    for (origen, simbolo), destino in TRANSICIONES.items():
        grafo.add_edge(origen, destino, key=simbolo, label=simbolo)

    posiciones = nx.spring_layout(grafo, seed=SEED_LAYOUT)
    return grafo, posiciones


# ============================================================
# DIBUJO
# ============================================================
def _punto_medio_desplazado(
    p1: tuple[float, float],
    p2: tuple[float, float],
    offset: float = 0.10,
) -> tuple[float, float]:
    """Retorna el punto medio entre p1 y p2, desplazado
    perpendicularmente una distancia `offset`."""
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    normal_x, normal_y = -dy, dx
    longitud = (normal_x**2 + normal_y**2) ** 0.5 or 1
    return mx + offset * normal_x / longitud, my + offset * normal_y / longitud


def _dibujar_nodos(grafo, posiciones, estado_actual):
    """Dibuja los nodos: el activo más grande, los finales con borde grueso."""
    tamanos = [
        TAM_NODO_ACTIVO if nodo == estado_actual else TAM_NODO_NORMAL
        for nodo in grafo.nodes()
    ]
    grosores_borde = [
        GROSOR_BORDE_FINAL if nodo in ESTADOS_FINALES else GROSOR_BORDE_NORMAL
        for nodo in grafo.nodes()
    ]
    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=list(grafo.nodes()),
        node_size=tamanos,
        linewidths=grosores_borde,
        edgecolors="black",
    )
    nx.draw_networkx_labels(grafo, posiciones)


def _dibujar_lazos(grafo, posiciones, contador):
    """Dibuja aristas donde origen == destino (self-loops)."""
    for origen, destino, clave, datos in grafo.edges(keys=True, data=True):
        if origen != destino:
            continue

        x, y = posiciones[origen]
        indice = contador.get((origen, origen), 0)
        contador[(origen, origen)] = indice + 1

        es_par = indice % 2 == 0
        radio = LOOP_RAD_PAR if es_par else LOOP_RAD_IMPAR
        offset_y = LOOP_OFFSET_Y_PAR if es_par else LOOP_OFFSET_Y_IMPAR

        loop = FancyArrowPatch(
            (x - LOOP_DX, y),
            (x + LOOP_DX, y),
            connectionstyle=f"arc3,rad={radio}",
            arrowstyle="-|>",
            mutation_scale=MUTATION_SCALE,
            linewidth=1.2,
            shrinkA=SHRINK_ARROW,
            shrinkB=SHRINK_ARROW,
            zorder=5,
            clip_on=False,
        )
        plt.gca().add_patch(loop)
        plt.text(
            x, y + offset_y, datos["label"],
            fontsize=FONT_SIZE_LOOP, ha="center", va="center",
        )


def _dibujar_aristas_normales(grafo, posiciones, contador):
    """Dibuja aristas entre nodos distintos."""
    for origen, destino, clave, datos in grafo.edges(keys=True, data=True):
        if origen == destino:
            continue

        indice = contador.get((origen, destino), 0)
        contador[(origen, destino)] = indice + 1
        es_par = indice % 2 == 0
        radio = RADIO_CURVA_PAR if es_par else RADIO_CURVA_IMPAR

        nx.draw_networkx_edges(
            grafo, posiciones,
            edgelist=[(origen, destino)],
            connectionstyle=f"arc3,rad={radio}",
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
        )

        desplazamiento = OFFSET_ETIQUETA_PAR if es_par else OFFSET_ETIQUETA_IMPAR
        lx, ly = _punto_medio_desplazado(posiciones[origen], posiciones[destino], desplazamiento)
        plt.text(
            lx, ly, datos["label"],
            fontsize=FONT_SIZE_ARISTA, ha="center", va="center",
        )


def dibujar_paso(grafo, posiciones, estado_actual, paso: int, simbolo: str = None):
    """Dibuja el estado completo del autómata en un paso de la simulación.

    Resalta el nodo activo, los estados finales, y las transiciones.
    """
    plt.clf()

    _dibujar_nodos(grafo, posiciones, estado_actual)

    contador = {}
    _dibujar_lazos(grafo, posiciones, contador)
    _dibujar_aristas_normales(grafo, posiciones, contador)

    titulo = f"Paso {paso}: {estado_actual}"
    if simbolo:
        titulo += f" | '{simbolo}'"
    plt.axis("off")
    plt.title(titulo, fontsize=FONT_SIZE_TITULO)
    plt.pause(PAUSA_SEGUNDOS)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    cadena = sys.argv[1] if len(sys.argv) > 1 else input("Cadena (a/b): ").strip()

    try:
        historial, acepta = ejecutar(cadena)
        resultado = "ACEPTA" if acepta else "RECHAZA"
        print(f"{resultado} (estado final: {historial[-1]})")

        grafo, posiciones = construir_grafo()

        plt.ion()
        dibujar_paso(grafo, posiciones, historial[0], 0)

        for indice, simbolo in enumerate(cadena, start=1):
            dibujar_paso(grafo, posiciones, historial[indice], indice, simbolo)

        plt.ioff()
        plt.show()

    except Exception as error:
        print("RECHAZA:", error)

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
TAM_NODO_ACTIVO = 900      # Tamaño del nodo que representa el estado actual
TAM_NODO_NORMAL = 600       # Tamaño del resto de nodos
GROSOR_BORDE_FINAL = 3      # Borde grueso para estados finales
GROSOR_BORDE_NORMAL = 1     # Borde delgado para estados no finales
SEED_LAYOUT = 7             # Semilla para que el layout sea reproducible
PAUSA_SEGUNDOS = 1.0        # Tiempo de pausa entre cada paso de la animación
MUTATION_SCALE = 18         # Tamaño de la punta de flecha
SHRINK_ARROW = 6            # Separación entre la flecha y el borde del nodo
FONT_SIZE_ARISTA = 11       # Tamaño de letra de la etiqueta en aristas
FONT_SIZE_LOOP = 10         # Tamaño de letra de la etiqueta en lazos
FONT_SIZE_TITULO = 12       # Tamaño de letra del título del gráfico

# Parámetros para lazos (self-loops)
LOOP_RAD_PAR = 0.5          # Curvatura del lazo cuando es el primero
LOOP_RAD_IMPAR = -0.6       # Curvatura del lazo cuando es el segundo (evita superposición)
LOOP_DX = 0.08              # separacion horizontal entre los extremos del lazo
LOOP_OFFSET_Y_PAR = 0.22    # Desplazamiento vertical de la etiqueta (primer lazo)
LOOP_OFFSET_Y_IMPAR = -0.22 # Desplazamiento vertical de la etiqueta (segundo lazo)

# Parámetros para aristas normales
RADIO_CURVA_PAR = 0.18      # Curvatura para la primera arista entre dos nodos
RADIO_CURVA_IMPAR = -0.18   # Curvatura para la segunda arista (evita superposición)
OFFSET_ETIQUETA_PAR = 0.10  # Desplazamiento de la etiqueta (primera arista)
OFFSET_ETIQUETA_IMPAR = -0.10 # Desplazamiento de la etiqueta (segunda arista)


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
    # Inicia en el estado inicial y lo guarda como primer paso
    estado_actual = ESTADO_INICIAL
    historial = [estado_actual]

    # Recorre cada caracter de la cadena
    for posicion, simbolo in enumerate(cadena):
        clave = (estado_actual, simbolo)
        # Si no existe transicion definida, la cadena es rechazada
        if clave not in TRANSICIONES:
            raise ValueError(
                f"No hay transición desde {estado_actual} "
                f"con '{simbolo}' en la posición {posicion}"
            )
        # Avanza al siguiente estado segun la funcion de transicion
        estado_actual = TRANSICIONES[clave]
        historial.append(estado_actual)

    # Retorna el historial de estados y si el ultimo estado es final
    return historial, historial[-1] in ESTADOS_FINALES


# ============================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================
def construir_grafo() -> tuple[nx.MultiDiGraph, dict]:
    """Crea el grafo dirigido del DFA y calcula la posición de sus nodos."""
    # Crea un grafo dirigido que permite multiples aristas entre dos nodos
    grafo = nx.MultiDiGraph()
    grafo.add_nodes_from(ESTADOS)

    # Agrega una arista por cada transicion, usando el simbolo como clave
    for (origen, simbolo), destino in TRANSICIONES.items():
        grafo.add_edge(origen, destino, key=simbolo, label=simbolo)

    # Calcula posiciones de los nodos usando el algoritmo spring
    # seed fijo para que el grafo siempre se vea igual
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
    perpendicularmente una distancia `offset`.

    Sirve para separar etiquetas cuando hay dos aristas
    paralelas entre los mismos nodos (una de ida y otra de vuelta).
    """
    # Desempaqueta las coordenadas de cada punto
    (x1, y1), (x2, y2) = p1, p2
    # Calcula el punto medio
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    # Calcula el vector direccion entre ambos puntos
    dx, dy = x2 - x1, y2 - y1
    # Vector perpendicular (rotado 90 grados)
    normal_x, normal_y = -dy, dx
    # Longitud del vector perpendicular (evita division por cero)
    longitud = (normal_x**2 + normal_y**2) ** 0.5 or 1
    # Retorna el punto medio desplazado en la direccion perpendicular
    return mx + offset * normal_x / longitud, my + offset * normal_y / longitud


def _dibujar_nodos(grafo, posiciones, estado_actual):
    """Dibuja los nodos: el activo más grande, los finales con borde grueso."""
    # Asigna tamaño segun si el nodo es el estado actual o no
    tamanos = [
        TAM_NODO_ACTIVO if nodo == estado_actual else TAM_NODO_NORMAL
        for nodo in grafo.nodes()
    ]
    # Asigna borde grueso a los estados finales, delgado al resto
    grosores_borde = [
        GROSOR_BORDE_FINAL if nodo in ESTADOS_FINALES else GROSOR_BORDE_NORMAL
        for nodo in grafo.nodes()
    ]
    # Dibuja los circulos de los nodos con los tamanos y bordes calculados
    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=list(grafo.nodes()),
        node_size=tamanos,
        linewidths=grosores_borde,
        edgecolors="black",
    )
    # Dibuja las etiquetas (q0, q1, ...) dentro de cada nodo
    nx.draw_networkx_labels(grafo, posiciones)


def _dibujar_lazos(grafo, posiciones, contador):
    """Dibuja aristas donde origen == destino (self-loops).

    Usa FancyArrowPatch para dibujar un arco que sale y vuelve al mismo nodo.
    Si hay mas de un lazo en el mismo nodo, alterna la curvatura
    para que no se superpongan.
    """
    # Itera sobre todas las aristas del grafo
    for origen, destino, clave, datos in grafo.edges(keys=True, data=True):
        # Saltea las aristas que no son lazos (origen distinto de destino)
        if origen != destino:
            continue

        # Obtiene las coordenadas del nodo
        x, y = posiciones[origen]
        # Lleva la cuenta de cuantos lazos lleva este nodo
        indice = contador.get((origen, origen), 0)
        contador[(origen, origen)] = indice + 1

        # Alterna curvatura y posicion de etiqueta segun sea par o impar
        es_par = indice % 2 == 0
        radio = LOOP_RAD_PAR if es_par else LOOP_RAD_IMPAR
        offset_y = LOOP_OFFSET_Y_PAR if es_par else LOOP_OFFSET_Y_IMPAR

        # Dibuja el arco del lazo usando FancyArrowPatch
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
        # Dibuja la etiqueta del simbolo (a o b) cerca del lazo
        plt.text(
            x, y + offset_y, datos["label"],
            fontsize=FONT_SIZE_LOOP, ha="center", va="center",
        )


def _dibujar_aristas_normales(grafo, posiciones, contador):
    """Dibuja aristas entre nodos distintos.

    Si hay dos aristas entre el mismo par de nodos (una en cada direccion),
    las curva en sentidos opuestos para que no se superpongan.
    """
    # Itera sobre todas las aristas del grafo
    for origen, destino, clave, datos in grafo.edges(keys=True, data=True):
        # Saltea los lazos (se dibujan en _dibujar_lazos)
        if origen == destino:
            continue

        # Lleva la cuenta de aristas entre este par de nodos
        indice = contador.get((origen, destino), 0)
        contador[(origen, destino)] = indice + 1
        # Alterna curvatura entre par e impar para evitar superposicion
        es_par = indice % 2 == 0
        radio = RADIO_CURVA_PAR if es_par else RADIO_CURVA_IMPAR

        # Dibuja la flecha de la arista con la curvatura calculada
        nx.draw_networkx_edges(
            grafo, posiciones,
            edgelist=[(origen, destino)],
            connectionstyle=f"arc3,rad={radio}",
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
        )

        # Calcula la posicion de la etiqueta desplazada perpendicularmente
        desplazamiento = OFFSET_ETIQUETA_PAR if es_par else OFFSET_ETIQUETA_IMPAR
        lx, ly = _punto_medio_desplazado(posiciones[origen], posiciones[destino], desplazamiento)
        # Dibuja la etiqueta del simbolo (a o b) sobre la arista
        plt.text(
            lx, ly, datos["label"],
            fontsize=FONT_SIZE_ARISTA, ha="center", va="center",
        )


def dibujar_paso(grafo, posiciones, estado_actual, paso: int, simbolo: str = None):
    """Dibuja el estado completo del autómata en un paso de la simulación.

    Resalta el nodo activo, los estados finales, y las transiciones.
    """
    # Limpia la figura actual para dibujar el nuevo paso
    plt.clf()

    # Dibuja los nodos con el estado actual resaltado
    _dibujar_nodos(grafo, posiciones, estado_actual)

    # Dibuja todas las aristas (lazos y normales)
    contador = {}
    _dibujar_lazos(grafo, posiciones, contador)
    _dibujar_aristas_normales(grafo, posiciones, contador)

    # Arma el titulo del paso mostrando el numero, el estado y el simbolo leido
    titulo = f"Paso {paso}: {estado_actual}"
    if simbolo:
        titulo += f" | '{simbolo}'"
    plt.axis("off")
    plt.title(titulo, fontsize=FONT_SIZE_TITULO)
    # Pausa para que se vea la animacion antes del siguiente paso
    plt.pause(PAUSA_SEGUNDOS)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    # Toma la cadena de argumentos o la pide por teclado
    cadena = sys.argv[1] if len(sys.argv) > 1 else input("Cadena (a/b): ").strip()

    try:
        # Ejecuta la simulacion del DFA sobre la cadena
        historial, acepta = ejecutar(cadena)
        # Muestra el resultado por consola
        resultado = "ACEPTA" if acepta else "RECHAZA"
        print(f"{resultado} (estado final: {historial[-1]})")

        # Construye el grafo del automata
        grafo, posiciones = construir_grafo()

        # Activa modo interactivo de matplotlib para la animacion
        plt.ion()
        # Dibuja el paso 0: solo el estado inicial
        dibujar_paso(grafo, posiciones, historial[0], 0)

        # Dibuja un paso por cada caracter leido
        for indice, simbolo in enumerate(cadena, start=1):
            dibujar_paso(grafo, posiciones, historial[indice], indice, simbolo)

        # Desactiva modo interactivo y mantiene la ventana abierta
        plt.ioff()
        plt.show()

    except Exception as error:
        # Si ocurre un error (transicion faltante), imprime RECHAZA
        print("RECHAZA:", error)

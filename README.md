# Simulador Visual de DFA (Autómata Finito Determinista)

Este programa implementa un **Autómata Finito Determinista (DFA)** que reconoce un lenguaje sobre el alfabeto `{a, b}` y visualiza gráficamente la ejecución paso a paso usando `matplotlib` y `networkx`.

## Requisitos

```bash
pip install matplotlib networkx
```

## Uso

```bash
python Main.py <cadena>
```

O sin argumentos:

```bash
python Main.py
# Luego ingresa la cadena por teclado
```

## Explicación del código

### 1. Importaciones

```python
import sys, matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import FancyArrowPatch
```

- `sys` → permite leer argumentos desde la línea de comandos
- `matplotlib.pyplot` → para generar los gráficos
- `networkx` → para crear y manipular el grafo del autómata
- `FancyArrowPatch` → para dibujar flechas curvas (necesario para los lazos o auto-transiciones)

---

### 2. Definición del DFA

```python
states = {"q0","q1","q2","q3","q4"}
alphabet = {"a","b"}
```

**`states`**: conjunto de 5 estados: `q0`, `q1`, `q2`, `q3`, `q4`.

**`alphabet`**: alfabeto de entrada, solo contiene `a` y `b`.

```python
delta = {("q0","a"):"q1",
         ("q1","a"):"q4",
         ("q1","b"):"q4",
         ("q2","a"):"q0",
         ("q2","b"):"q1",
         ("q3","b"):"q2",
         ("q4","a"):"q4",
         ("q4","b"):"q4"}
```

**`delta`**: función de transición representada como un diccionario.

- La clave es una tupla `(estado_origen, símbolo)`
- El valor es el `estado_destino`

| Desde | Símbolo | Hacia |
|-------|---------|-------|
| q0    | a       | q1    |
| q1    | a       | q4    |
| q1    | b       | q4    |
| q2    | a       | q0    |
| q2    | b       | q1    |
| q3    | b       | q2    |
| q4    | a       | q4    |
| q4    | b       | q4    |

**Importante**: no todas las combinaciones están definidas. Por ejemplo, `(q0, "b")` y `(q3, "a")` no existen, lo que provocará un error si la cadena de entrada las requiere.

```python
q0, F = "q0", {"q4"}
```

- `q0` = estado inicial
- `F` = conjunto de estados de aceptación (solo `q4`)

---

### 3. Función `run(s)` — Simulación

```python
def run(s):
    q, steps = q0, [q0]
    for i,ch in enumerate(s):
        if (q,ch) not in delta:
            raise ValueError(f"Sin transición desde {q} con '{ch}' en pos {i}")
        q = delta[(q,ch)]; steps.append(q)
    return steps, steps[-1] in F
```

**Parámetro**: `s` — cadena de entrada compuesta por caracteres `a` y `b`.

**Proceso**:

1. Inicializa el estado actual `q = q0` y la lista `steps = [q0]`
2. Itera sobre cada caracter `ch` de la cadena con su índice `i`
3. Verifica si existe una transición desde `q` con `ch` en `delta`
   - Si **no existe**, lanza `ValueError` con un mensaje indicando dónde falló
   - Si **existe**, actualiza `q` al destino y agrega el nuevo estado a `steps`
4. Retorna una tupla:
   - `steps` — lista con todos los estados visitados (incluyendo el inicial)
   - `steps[-1] in F` — booleano que indica si el estado final es de aceptación

---

### 4. Construcción del grafo

```python
G = nx.MultiDiGraph()
G.add_nodes_from(states)
for (q, a), p in delta.items():
    G.add_edge(q, p, key=a, label=a)
pos = nx.spring_layout(G, seed=7)
```

- `nx.MultiDiGraph()` → grafo dirigido que permite múltiples aristas entre el mismo par de nodos (útil cuando q1 → q4 tanto con `a` como con `b`)
- Se agregan todos los estados como nodos
- Por cada transición en `delta` se agrega una arista con la letra como etiqueta
- `spring_layout` calcula posiciones automáticas para los nodos usando el algoritmo de resorte; `seed=7` fija la semilla para obtener siempre el mismo layout

---

### 5. Función auxiliar `_mid(p1, p2, o=0.10)`

```python
def _mid(p1, p2, o=0.10):
    (x1,y1),(x2,y2)=p1,p2
    mx,my=(x1+x2)/2,(y1+y2)/2
    dx,dy=x2-x1,y2-y1
    nx_,ny_=-dy,dx
    L=(nx_**2+ny_**2)**0.5 or 1
    return mx+o*nx_/L, my+o*ny_/L
```

Calcula el **punto medio desplazado** entre dos nodos. El desplazamiento perpendicular evita que las etiquetas de aristas opuestas se superpongan.

- Calcula el punto medio `(mx, my)`
- Obtiene el vector perpendicular `(-dy, dx)`
- Normaliza y escala por `o` (offset) para desplazar la etiqueta
- Si la distancia entre nodos es 0 (mismo nodo), usa 1 para evitar división por cero

---

### 6. Función `draw_step(current, idx, sym=None)` — Dibujo por paso

Esta función dibuja el estado actual de la simulación en cada paso.

#### 6a. Limpiar y dibujar nodos

```python
plt.clf()
nodes = list(G.nodes())
nx.draw_networkx_nodes(G, pos,
    nodelist=nodes,
    node_size=[900 if n == current else 600 for n in nodes],
    linewidths=[3 if n in F else 1 for n in nodes],
    edgecolors="black")
nx.draw_networkx_labels(G, pos)
```

- `plt.clf()` → limpia la figura anterior
- El **estado actual** se dibuja más grande (900) que los demás (600)
- Los **estados de aceptación** tienen borde más grueso (linewidth=3), esto permite identificar visualmente q4 como el estado final
- Se dibujan las etiquetas de cada nodo (q0, q1, etc.)

#### 6b. Dibujar aristas y lazos

```python
seen = {}
for u, v, k, d in G.edges(keys=True, data=True):
```

Usa un diccionario `seen` para llevar la cuenta de cuántas aristas se han dibujado entre cada par de nodos. Esto permite alternar la curvatura para evitar superposición.

**Lazos (auto-transiciones)**:

Cuando `u == v` (ej: q4 → q4):

```python
rad  = 0.5 if j % 2 == 0 else -0.6
dx   = 0.08
offy = 0.22 if j % 2 == 0 else -0.22

loop = FancyArrowPatch((x - dx, y), (x + dx, y),
    connectionstyle=f"arc3,rad={rad}",
    arrowstyle='-|>', mutation_scale=18, linewidth=1.2,
    shrinkA=6, shrinkB=6, zorder=5, clip_on=False)
plt.gca().add_patch(loop)
plt.text(x, y + offy, d["label"], fontsize=10, ha="center", va="center")
```

- Alterna la curvatura (`rad`) hacia arriba o abajo según el índice
- `FancyArrowPatch` dibuja un arco que sale del nodo y vuelve a él
- La etiqueta se coloca ligeramente arriba o abajo del nodo

**Aristas normales**:

```python
i = seen.get((u, v), 0)
seen[(u, v)] = i + 1
rad = 0.18 if i % 2 == 0 else -0.18
nx.draw_networkx_edges(G, pos, edgelist=[(u, v)],
    connectionstyle=f"arc3,rad={rad}",
    arrows=True, arrowstyle='-|>', arrowsize=20)
lx, ly = _mid(pos[u], pos[v], 0.10 if i % 2 == 0 else -0.10)
plt.text(lx, ly, d['label'], fontsize=11, ha='center', va='center')
```

- Alterna curvatura positiva/negativa para separar aristas paralelas
- La etiqueta (a o b) se coloca en el punto medio desplazado

#### 6c. Título y pausa

```python
plt.axis('off')
plt.title(f"Paso {idx}: {current}" + (f" | '{sym}'" if sym else ""))
plt.pause(1.0)
```

- Oculta los ejes
- Muestra el número de paso, el estado actual y el símbolo leído
- Pausa 1 segundo para que el usuario pueda ver el avance

---

### 7. Bloque `main`

```python
if __name__ == '__main__':
    s = sys.argv[1] if len(sys.argv) > 1 else input("Cadena (a/b): ").strip()
```

Obtiene la cadena de entrada:
- Desde el primer argumento de línea de comandos si existe
- O la pide por teclado

```python
    try:
        steps, ok = run(s)
        print("ACEPTA" if ok else "RECHAZA", f"(estado final: {steps[-1]})")
```

Ejecuta la simulación e imprime el resultado.

```python
        plt.ion()
        draw_step(steps[0], 0)
        for i, ch in enumerate(s, 1):
            draw_step(steps[i], i, ch)
        plt.ioff()
        plt.show()
```

- `plt.ion()` → activa modo interactivo (la ventana se actualiza sin bloquear el programa)
- Dibuja el **paso 0**: solo el estado inicial resaltado
- Por cada caracter en la cadena, dibuja el paso correspondiente
- `plt.ioff()` + `plt.show()` → desactiva modo interactivo y mantiene la ventana abierta al final

```python
    except Exception as e:
        print("RECHAZA:", e)
```

Captura cualquier error (como transiciones indefinidas) y muestra el mensaje.

---

## Lenguaje aceptado

El DFA acepta cadenas que:

1. Empiezan con `a` (única transición desde `q0`)
2. Tienen al menos **longitud 2** (la segunda letra lleva a `q4`)
3. `q4` es un estado **sumidero**: una vez allí, cualquier caracter mantiene el estado

**Ejemplos**:

| Cadena | Acepta | Estados recorridos           |
|--------|--------|------------------------------|
| "a"    | No     | q0 → q1                      |
| "aa"   | Sí     | q0 → q1 → q4                 |
| "ab"   | Sí     | q0 → q1 → q4                 |
| "aba"  | Sí     | q0 → q1 → q4 → q4            |
| "b"    | Error  | q0 no tiene transición con b |
| "ba"   | Error  | q0 no tiene transición con b |

## Estructura del proyecto

```
Guia-3/
├── Main.py      # Código principal del simulador
├── app.py       # Archivo simple (hola mundo)
└── README.md    # Esta documentación
```

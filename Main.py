import sys, matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import FancyArrowPatch

# === Definición del DFA ===
states = {"q0","q1","q2","q3","q4"}
alphabet = {"a","b"}
delta = {("q0","a"):"q1",         # función de transición: (origen, símbolo) -> destino
        ("q1","a"):"q4",
        ("q1","b"):"q4",
        ("q2","a"):"q0",
        ("q2","b"):"q1",
        ("q3","b"):"q2",
        ("q4","a"):"q4",          # q4 es sumidero
        ("q4","b"):"q4"}

q0, F = "q0", {"q4"}             # estado inicial y conjunto de aceptación

# === Simulación ===
def run(s):
    q, steps = q0, [q0]           # empieza en q0, registra cada paso
    for i,ch in enumerate(s):
        if (q,ch) not in delta: raise ValueError(f"Sin transición desde {q} con '{ch}' en pos {i}")
        q = delta[(q,ch)]; steps.append(q)
    return steps, steps[-1] in F  # (recorrido, acepta?)

# === Grafo y layout ===
G = nx.MultiDiGraph(); G.add_nodes_from(states)
for (q,a),p in delta.items(): G.add_edge(q,p,key=a,label=a)
pos = nx.spring_layout(G, seed=7)  # posición fija de nodos

# === Dibujo por paso ===
def _mid(p1,p2,o=0.10):            # punto medio con desplazamiento perpendicular
    (x1,y1),(x2,y2)=p1,p2; mx,my=(x1+x2)/2,(y1+y2)/2; dx,dy=x2-x1,y2-y1; nx_,ny_=-dy,dx; L=(nx_**2+ny_**2)**0.5 or 1
    return mx+o*nx_/L, my+o*ny_/L

def draw_step(current, idx, sym=None):
    plt.clf(); nodes=list(G.nodes())
    # nodo actual más grande; aceptación con borde grueso
    nx.draw_networkx_nodes(G,pos,nodelist=nodes,node_size=[900 if n==current else 600 for n in nodes],linewidths=[3 if n in F else 1 for n in nodes],edgecolors="black")
    nx.draw_networkx_labels(G,pos)
    seen={}                        # contador de aristas dibujadas por par
    for u,v,k,d in G.edges(keys=True,data=True):
        if u == v:                 # lazo (auto-transición)
            x, y = pos[u]
            j = seen.get((u, u), 0); seen[(u, u)] = j + 1
            rad  = 0.5 if j % 2 == 0 else -0.6
            dx   = 0.08
            offy = 0.22 if j % 2 == 0 else -0.22
            loop = FancyArrowPatch((x - dx, y), (x + dx, y),
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle='-|>', mutation_scale=18, linewidth=1.2,
                shrinkA=6, shrinkB=6, zorder=5, clip_on=False)
            plt.gca().add_patch(loop)
            plt.text(x, y + offy, d["label"], fontsize=10, ha="center", va="center")
            continue
        i=seen.get((u,v),0); seen[(u,v)]=i+1; rad = 0.18 if i % 2 == 0 else -0.18
        nx.draw_networkx_edges(G,pos,edgelist=[(u,v)],connectionstyle=f"arc3,rad={rad}",arrows=True,arrowstyle='-|>',arrowsize=20)
        lx,ly=_mid(pos[u],pos[v],0.10 if i%2==0 else -0.10); plt.text(lx,ly,d['label'],fontsize=11,ha='center',va='center')
    plt.axis('off'); plt.title(f"Paso {idx}: {current}" + (f" | '{sym}'" if sym else "")); plt.pause(1.0)



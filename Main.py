import sys, matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import FancyArrowPatch

# === Definición del DFA ===
states = {"q0","q1","q2","q3","q4"}
alphabet = {"a","b"}
delta = {("q0","a"):"q1", 
        ("q1","a"):"q4", 
        ("q1","b"):"q4", 
        ("q2","a"):"q0", 
        ("q2","b"):"q1", 
        ("q3","b"):"q2", 
        ("q4","a"):"q4", 
        ("q4","b"):"q4"}

q0, F = "q0", {"q4"}

# === Simulación ===
def run(s):
    q, steps = q0, [q0]
    for i,ch in enumerate(s):
        if (q,ch) not in delta: raise ValueError(f"Sin transición desde {q} con '{ch}' en pos {i}")
        q = delta[(q,ch)]; steps.append(q)
    return steps, steps[-1] in F

# === Grafo y layout ===
G = nx.MultiDiGraph(); G.add_nodes_from(states)
for (q,a),p in delta.items(): G.add_edge(q,p,key=a,label=a)
pos = nx.spring_layout(G, seed=7)

# === Dibujo por paso ===
def _mid(p1,p2,o=0.10):
    (x1,y1),(x2,y2)=p1,p2; mx,my=(x1+x2)/2,(y1+y2)/2; dx,dy=x2-x1,y2-y1; nx_,ny_=-dy,dx; L=(nx_**2+ny_**2)**0.5 or 1
    return mx+o*nx_/L, my+o*ny_/L

def draw_step(current, idx, sym=None):
    plt.clf(); nodes=list(G.nodes())
    nx.draw_networkx_nodes(G,pos,nodelist=nodes,node_size=[900 if n==current else 600 for n in nodes],linewidths=[3 if n in F else 1 for n in nodes],edgecolors="black")
    nx.draw_networkx_labels(G,pos)
    seen={}
    for u,v,k,d in G.edges(keys=True,data=True):
        if u == v:
            x, y = pos[u]
            j = seen.get((u, u), 0); seen[(u, u)] = j + 1

            rad  = 0.5 if j % 2 == 0 else -0.6    # curva más compacta
            dx   = 0.08                           # menos ancho de arco
            offy = 0.22 if j % 2 == 0 else -0.22  # etiqueta más cerca

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

# === main ===
if __name__=='__main__':
    s = sys.argv[1] if len(sys.argv)>1 else input("Cadena (a/b): ").strip()
    try:
        steps, ok = run(s); print("ACEPTA" if ok else "RECHAZA", f"(estado final: {steps[-1]})")
        plt.ion(); draw_step(steps[0],0)
        for i,ch in enumerate(s,1): draw_step(steps[i],i,ch)
        plt.ioff(); plt.show()
    except Exception as e:
        print("RECHAZA:", e)

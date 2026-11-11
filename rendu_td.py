import random
import math
from collections import deque

COUT = [[5, 3, 4],     
        [6, 7, 2]]      
OFFRE = [8, 9]         
DEMANDE = [4, 5, 8]     


def cout_transport(x):
    return sum(COUT[i][j] * x[i][j]
               for i in range(len(x)) for j in range(len(x[0])))


def coin_nord_ouest(offre, demande):
    """Solution initiale réalisable (règle du coin Nord-Ouest)."""
    o, d = offre[:], demande[:]
    x = [[0] * len(d) for _ in o]
    i = j = 0
    while i < len(o) and j < len(d):
        q = min(o[i], d[j])
        x[i][j] = q
        o[i] -= q
        d[j] -= q
        if o[i] == 0:
            i += 1
        else:
            j += 1
    return x


def voisins_transport(x):
    """Voisinage : déplacer 1 unité sur un cycle 2x2 (conserve offres/demandes).
    +1 en (i1,j1) et (i2,j2) ; -1 en (i1,j2) et (i2,j1)."""
    m, n = len(x), len(x[0])
    for i1 in range(m):
        for i2 in range(i1 + 1, m):
            for j1 in range(n):
                for j2 in range(n):
                    if j1 != j2 and x[i1][j2] >= 1 and x[i2][j1] >= 1:
                        y = [r[:] for r in x]
                        y[i1][j1] += 1
                        y[i2][j2] += 1
                        y[i1][j2] -= 1
                        y[i2][j1] -= 1
                        yield (i1, i2, j1, j2), y


def tabou_transport(nb_iter=20, tenure=3):
    x = coin_nord_ouest(OFFRE, DEMANDE)
    best, best_cout = x, cout_transport(x)
    tabou = deque(maxlen=tenure)
    print(f"Solution initiale : {x}  cout = {best_cout}")
    for it in range(1, nb_iter + 1):
        choix = None
        for mv, y in voisins_transport(x):
            c = cout_transport(y)
            est_tabou = mv in tabou
            
            if est_tabou and c >= best_cout:
                continue
            if choix is None or c < choix[2]:
                choix = (mv, y, c)
        if choix is None:
            break
        mv, x, c = choix
        
        tabou.append((mv[0], mv[1], mv[3], mv[2]))
        if c < best_cout:
            best, best_cout = x, c
        print(f"it {it:2d} : mouvement {mv}  cout = {c}  (meilleur = {best_cout})")
    print("\n>>> Meilleure solution (transport) :")
    for i, ligne in enumerate(best, 1):
        print(f"  D{i} -> {ligne}")
    print(f"  Cout minimal trouvé = {best_cout}\n")
    return best, best_cout



INF = 1000  
ARETES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}


def dist(a, b):
    return ARETES.get((min(a, b), max(a, b)), INF)


def cout_tournee(t):
    """Cout du cycle t[0]-t[1]-...-t[-1]-t[0]."""
    return sum(dist(t[k], t[(k + 1) % len(t)]) for k in range(len(t)))


def echange(t, i, j):
    s = t[:]
    s[i], s[j] = s[j], s[i]
    return s


def deux_opt(t, i, j):
    """Inverse le segment t[i..j] (voisinage 2-opt)."""
    return t[:i] + t[i:j + 1][::-1] + t[j + 1:]


def affiche(t):
    return "-".join(map(str, t + [t[0]]))



def tabou_tsp(nb_iter=10, tenure=3):
    x = [1, 2, 3, 4, 5, 6, 7, 8]          
    best, best_cout = x, cout_tournee(x)
    tabou = deque(maxlen=tenure)            
    print(f"Solution initiale : {affiche(x)}  cout = {best_cout}")
    for it in range(1, nb_iter + 1):
        choix = None
        for i in range(1, len(x)):          
            for j in range(i + 1, len(x)):
                paire = frozenset((x[i], x[j]))      
                y = deux_opt(x, i, j)
                c = cout_tournee(y)
                if paire in tabou and c >= best_cout:   
                    continue
                if choix is None or c < choix[2]:
                    choix = (paire, y, c)
        paire, x, c = choix
        tabou.append(paire)
        if c < best_cout:
            best, best_cout = x, c
        print(f"it {it:2d} : 2-opt sur {sorted(paire)}  {affiche(x)}  cout = {c}  (meilleur = {best_cout})")
    print(f"\n>>> Tabou : meilleure tournée {affiche(best)}  cout = {best_cout}\n")
    return best, best_cout



def recuit_tsp(nb_iter=5, T0=50.0, alpha=0.8, seed=32):
    random.seed(seed)
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    c = cout_tournee(x)
    best, best_cout = x, c
    T = T0
    print(f"Solution initiale : {affiche(x)}  cout = {c}  T0 = {T0}")
    for it in range(1, nb_iter + 1):
        i, j = sorted(random.sample(range(1, len(x)), 2))   
        y = deux_opt(x, i, j)
        cy = cout_tournee(y)
        delta = cy - c
        if delta <= 0:
            accepte, raison = True, "meilleur"
        else:
            p = math.exp(-delta / T)
            r = random.random()
            accepte = r < p
            raison = f"p={p:.3f}, r={r:.3f}"
        if accepte:
            x, c = y, cy
            if c < best_cout:
                best, best_cout = x, c
        print(f"it {it} : T={T:6.2f}  voisin {affiche(y)}  cout={cy}  delta={delta:+d}  "
              f"{'ACCEPTE' if accepte else 'refuse'} ({raison})")
        T *= alpha        
    print(f"\n>>> Recuit : meilleure tournée {affiche(best)}  cout = {best_cout}\n")
    return best, best_cout


if __name__ == "__main__":
    print("=" * 60, "\nEXERCICE 2 - Tabou (transport)\n", "=" * 60, sep="")
    tabou_transport()
    print("=" * 60, "\nEXERCICE 3 - 1) Tabou (TSP)\n", "=" * 60, sep="")
    tabou_tsp()
    print("=" * 60, "\nEXERCICE 3 - 2) Recuit simulé (TSP)\n", "=" * 60, sep="")
    recuit_tsp()

    print("=" * 60, "\nEXERCICE 3 - 1) Tabou (TSP)\n", "=" * 60, sep="")
    tabou_tsp()
    print("=" * 60, "\nEXERCICE 3 - 2) Recuit simulé (TSP)\n", "=" * 60, sep="")
    recuit_tsp()

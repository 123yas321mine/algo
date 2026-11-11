import random

CAP = [20, 15, 35, 40, 15, 15, 10]            
DEM = [80, 90, 65, 70]                       
TOTAL = 150
G1 = ['1100', '0110', '0011']                 
G2 = ['1000', '0100', '0010', '0001']        
DOM = [G1, G1] + [G2] * 5

def init():
    return [random.choice(DOM[u]) for u in range(7)]

def reserves(ch):
    return [TOTAL - sum(CAP[u] for u in range(7) if ch[u][t] == '1') - DEM[t]
            for t in range(4)]

def fitness(ch):                              
    return max(0, min(reserves(ch)))


def roulette(pop, fits):                      
    total = sum(fits)
    if total == 0:
        return random.choice(pop)[:]
    r, cumul = random.random(), 0
    for ch, f in zip(pop, fits):
        cumul += f / total
        if r <= cumul:
            return ch[:]
    return pop[-1][:]

def tournoi(pop, fits, t=3):                  # Algo 13
    best = random.randrange(len(pop))
    for _ in range(t - 1):
        nxt = random.randrange(len(pop))
        if fits[nxt] > fits[best]:
            best = nxt
    return pop[best][:] if random.random() > 0.5 else random.choice(pop)[:]


def cx_1point(p1, p2):
    k = random.randint(1, 6)
    return p1[:k] + p2[k:], p2[:k] + p1[k:]

def cx_2points(p1, p2):
    i, j = sorted(random.sample(range(1, 7), 2))
    return p1[:i] + p2[i:j] + p1[j:], p2[:i] + p1[i:j] + p2[j:]

def cx_uniforme(p1, p2):
    c1, c2 = p1[:], p2[:]
    for u in range(7):
        if random.random() < 0.5:
            c1[u], c2[u] = c2[u], c1[u]
    return c1, c2


def mutation(ch, pm, type_m):
    ch = ch[:]
    for u in range(7):
        if random.random() < pm:
            if type_m == "inversion":
                ch[u] = ch[u][::-1]          
            else:
                ch[u] = random.choice(DOM[u]) 
    return ch

def ag(selection, cx, type_m, taille=42, gens=100, pc=0.8, pm=0.1):
    P = [init() for _ in range(taille)]                     
    nb_elite = taille // 2                                    
    for _ in range(gens):                                    
        fits = [fitness(c) for c in P]                        
        elite = sorted(P, key=fitness, reverse=True)[:nb_elite]
        desc = []
        while len(desc) < taille - nb_elite:
            p1, p2 = selection(P, fits), selection(P, fits)   
            c1, c2 = cx(p1, p2) if random.random() < pc else (p1[:], p2[:])  
            desc += [mutation(c1, pm, type_m), mutation(c2, pm, type_m)]    
        P = elite + desc[:taille - nb_elite]
        
    return max(P, key=fitness)


def tabou(iters=100, taille_tabou=5):
    s = init(); best = s[:]; M = []
    for _ in range(iters):
        voisins = []                                          
        for u in range(7):
            for g in DOM[u]:
                if g != s[u]:
                    v = s[:]; v[u] = g
                    voisins.append((v, (u, g), (u, s[u])))
        voisins.sort(key=lambda x: fitness(x[0]), reverse=True)
        for v, mv, ancien in voisins:
            if mv not in M or fitness(v) > fitness(best):     
                s = v; M.append(ancien); break
        if len(M) > taille_tabou:
            M.pop(0)
        if fitness(s) > fitness(best):
            best = s[:]
    return best

SELECTIONS = {"roulette": roulette, "tournoi": tournoi}
CROISEMENTS = {"1 point": cx_1point, "2 points": cx_2points, "uniforme": cx_uniforme}
MUTATIONS = ["inversion", "remplacement"]

meilleur = None
for ns, sel in SELECTIONS.items():
    for nc, cx in CROISEMENTS.items():
        for nm in MUTATIONS:
            b = ag(sel, cx, nm)
            print(f"{ns:8} | {nc:8} | {nm:12} | perf = {fitness(b)}")
            if meilleur is None or fitness(b) > fitness(meilleur):
                meilleur = b

b = tabou()
print(f"Tabou                                | perf = {fitness(b)}")
if fitness(b) > fitness(meilleur):
    meilleur = b

print("\nle meilleur individu est :", meilleur)
print("réserves par intervalle :", reserves(meilleur))
print("le meilleur score est :", fitness(meilleur))

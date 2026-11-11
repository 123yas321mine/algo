import random

groupe1 = ['1100', '0110', '0011']           
groupe2 = ['1000', '0100', '0010', '0001']    
nombre_individu = 5
max_generation = 3
capacite_maximum = 150
capacite = [20, 15, 35, 40, 15, 15, 10]
intervalle = [80, 90, 65, 70]

def creation_individu():
    return [random.choice(groupe1 if i < 2 else groupe2) for i in range(7)]

def createGeneration():
    generation = []
    while len(generation) < nombre_individu:     
        ind = creation_individu()
        if ind not in generation:
            generation.append(ind)
    return generation

def puissance(individu, capacite):
   
    return [sum(int(individu[j][i]) * capacite[j] for j in range(7))
            for i in range(4)]

def reser_maxi(intervalle, perdue):
   
    reserv = [capacite_maximum - perdue[i] - intervalle[i] for i in range(4)]
    return max(0, min(reserv))

def score(ind):
    return reser_maxi(intervalle, puissance(ind, capacite))

def croisement_point(init, ind1, ind2, position):
    gen1 = ind2[:position] + ind1[position:]
    gen2 = ind1[:position] + ind2[position:]
    init.append(gen1)
    init.append(gen2)

def mutation(individu, position):
    individu = individu[:]
    individu[position] = random.choice(groupe1 if position < 2 else groupe2)
    return individu

def developpement_generation(g, position_croisement, position_mutation):
    croisement_point(g, g[1], g[2], position_croisement)
    croisement_point(g, g[3], g[4], position_croisement)
    g.append(mutation(g[0], position_mutation))

def selection(generation):
    """Trier par score décroissant et garder les meilleurs"""
    return sorted(generation, key=score, reverse=True)[:nombre_individu]

def evaluation(generation):
    best = max(generation, key=score)
    return [score(best), generation.index(best)]


generation = createGeneration()
for n in range(1, max_generation + 1):
    developpement_generation(generation,
                             random.randint(1, 6),   
                             random.randint(0, 6))    
    generation = selection(generation)
    print("Génération", n)
    for k, ind in enumerate(generation, 1):
        print(f"  {k}) {ind} score: {score(ind)}")

ev = evaluation(generation)
print("le meilleur individu est :", generation[ev[1]])
print("le meilleur score est :", ev[0])
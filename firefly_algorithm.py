import numpy as np


# def f1(x):
#     # Exact solutions should be (1,1,...,1)
#     return np.sum((x - 1) ** 2)


# Définition des variables
n_taches = 10  # Nombre de tâches
n_noeuds = 4  # Nombre de nœuds de calcul

# Capacités de traitement maximales
C = np.array([10, 12, 8, 15])

# Puissance consommée par tâche
P = np.random.rand(n_taches, n_noeuds)

# Temps de processing par tâche
t = np.random.rand(n_taches, n_noeuds)

# Charge de travail par tâche
w = np.random.rand(n_taches)

# Paramètres de l'algorithme Firefly
alpha = 0.5  # Coefficient d'absorption
beta = 0.2  # Coefficient de randomisation
gamma = 1.0  # Facteur d'atténuation





# Fonction objectif 1: Minimiser la consommation d'énergie totale
def f1(x):
    x_reshaped = x.reshape((n_taches, n_noeuds))
    return np.sum(P * t * x_reshaped)

# Fonction objectif 2: Minimiser le temps d'exécution total
def f2(x):
    x_reshaped = x.reshape((n_taches, n_noeuds))
    return np.sum(t * x_reshaped)

# Fonction objectif 3: Minimiser l'équilibre de charge des serveurs
def f3(x):
    x_reshaped = x.reshape((n_taches, n_noeuds))
    return np.sum(t + x_reshaped)

def init_ffa(n, d, Lb, Ub, u0):
    ns = np.zeros((n, d))
    if len(Lb) > 0:
        for i in range(n):
            ns[i, :] = Lb + (Ub - Lb) * np.random.rand(d)
    else:
        for i in range(n):
            ns[i, :] = u0 + np.random.randn(d)
    Lightn = np.ones(n) * 10 ** 100
    return ns, Lightn


def alpha_new(alpha, NGen):
    delta = 1 - (10 ** (-4) / 0.9) ** (1 / NGen)
    return (1 - delta) * alpha


def findlimits(n, ns, Lb, Ub):
    for i in range(n):
        ns_tmp = ns[i, :]
        ns_tmp[ns_tmp < Lb] = Lb[ns_tmp < Lb]
        ns_tmp[ns_tmp > Ub] = Ub[ns_tmp > Ub]
        ns[i, :] = ns_tmp
    return ns


def ffa_move(n, d, ns, Lightn, nso, Lighto, nbest, Lightbest, alpha, betamin, gamma, Lb, Ub):
    scale = np.abs(Ub - Lb)
    for i in range(n):
        for j in range(n):
            r = np.sqrt(np.sum((ns[i, :] - ns[j, :]) ** 2))
            if Lightn[i] > Lighto[j]:
                beta0 = 1
                beta = (beta0 - betamin) * np.exp(-gamma * r ** 2) + betamin
                tmpf = alpha * (np.random.rand(d) - 0.5) * scale
                ns[i, :] = ns[i, :] * (1 - beta) + nso[j, :] * beta + tmpf
    ns = findlimits(n, ns, Lb, Ub)
    return ns


def ffa_mincon(fhandle, u0, Lb, Ub, para):
    if len(para) < 5:
        para.extend([0.25, 0.20, 1])
    n, MaxGeneration, alpha, betamin, gamma = para
    NumEval = n * MaxGeneration
    if len(Lb) == 0:
        Lb = np.zeros_like(u0)
    if len(Ub) == 0:
        Ub = np.full_like(u0, 2)
    d = len(u0)
    zn = np.ones(n) * 10 ** 100
    ns, Lightn = init_ffa(n, d, Lb, Ub, u0)
    for k in range(MaxGeneration):
        alpha = alpha_new(alpha, MaxGeneration)
        for i in range(n):
            zn[i] = fhandle(ns[i, :])
            Lightn[i] = zn[i]
        Lightn_sorted_indices = np.argsort(zn)
        ns_tmp = ns.copy()
        for i in range(n):
            ns[i, :] = ns_tmp[Lightn_sorted_indices[i], :]
        nso = ns.copy()
        Lighto = Lightn.copy()
        nbest = ns[0, :]
        Lightbest = Lightn[0]
        fbest = Lightbest
        ns = ffa_move(n, d, ns, Lightn, nso, Lighto, nbest, Lightbest, alpha, betamin, gamma, Lb, Ub)
    return nbest, fbest, NumEval






if __name__ == "__main__":
    # parameters [n N_iteration alpha betamin gamma]
    para = [20, 500, alpha, beta, gamma]

    # Simple bounds/limits for d-dimensional problems
    d = 15 # n_taches * n_noeuds
    Lb = np.zeros(d)
    Ub = np.full(d, 2)

    # Initial random guess
    u0 = Lb + (Ub - Lb) * np.random.rand(d)

    for objective_func in [f1, f2, f3]:
        u, fval, NumEval = ffa_mincon(objective_func, u0, Lb, Ub, para)
        # Display results for each objective function
        print("Best solution:", u)
        print("Best objective:", fval)
        print("Total number of function evaluations:", NumEval)
        print()

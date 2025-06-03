from gurobipy import Model, GRB, quicksum

model = Model("Armazenagem")

import numpy as np


def gerar_modelo(num_posicoes, num_secoes, num_bobinas, ):

    # Conjuntos
    Psi = list(range(num_posicoes))         # posições disponíveis
    S = list(range(num_secoes))             # seções de tempo
    A = list(range(num_bobinas))            # bobinas
    Phi = [0, num_posicoes - 1]             # entrada (I) e saída (O) simplificadas
    A_in = A[:1]                             # uma bobina entra
    A_out = A[1:]                            # o resto sai
    M = 99999                                # constante grande

    # Camadas
    Psi1 = Psi[:num_posicoes // 2]
    Psi2 = Psi[num_posicoes // 2:]

    # Vetores de janelas de tempo de entrada e saída
    # TODO: Adicionar lógica para definir janelas de tempo de entrada e saída
    sigma_minus = np.random.randint(0, 3, size=len(A)) * 1800 # em segundos (30 minutos)
    sigma_plus = sigma_minus + np.random.randint(1, 4, size=len(A)) * 1800
    omega_minus = np.random.randint(3, 6, size=len(A)) * 1800
    omega_plus = omega_minus + np.random.randint(1, 4, size=len(A)) * 1800

    # Matrizes de tempo e energia de movimentação
    t_load = np.random.randint(1, 5, size=(num_posicoes, num_posicoes))
    t_empty = np.random.randint(1, 5, size=(num_posicoes, num_posicoes))
    E_load = np.random.randint(10, 50, size=(num_posicoes, num_posicoes, len(A)))
    E_empty = np.random.randint(5, 20, size=(num_posicoes, num_posicoes))

    # Variáveis de decisão (inicializadas com zeros)
    W = np.zeros((len(S), num_posicoes, num_posicoes, len(A)), dtype=int)
    V = np.zeros((len(S), num_posicoes, num_posicoes), dtype=int)
    x = np.zeros((len(S), num_posicoes, len(A)), dtype=int)

    tau = np.zeros(len(S), dtype=float)
    tau[0] = 0.0  # conforme a restrição τ¹ = 0

    # Saída de dados para verificação (exemplo)
    print("t_load[0][1] =", t_load[0][1])
    print("E_load[0][1][0] =", E_load[0][1][0])
    print("σ⁻[a] =", sigma_minus)
    print("ω⁺[a] =", omega_plus)
    # Definindo variáveis de decisão no modelo



    # W[s][k][q][a] = 1 se bobina a se move de k -> q na seção s
    W = model.addVars(len(S), len(Psi), len(Psi), len(A), vtype=GRB.BINARY, name="W")

    # V[s][k][q] = 1 se movimentação vazia de k -> q ocorre na seção s
    V = model.addVars(len(S), len(Psi), len(Psi), vtype=GRB.BINARY, name="V")

    # x[s][q][a] = 1 se bobina a está na posição q na seção s
    x = model.addVars(len(S), len(Psi), len(A), vtype=GRB.BINARY, name="x")

    # τ[s] = instante de tempo do início da seção s
    tau = model.addVars(len(S), vtype=GRB.CONTINUOUS, name="tau")


    # Definindo restrições do modelo


    model.addConstr(tau[0] == 0)  # restrição τ¹ = 0

    for a in A_in:
        model.addConstr(quicksum(W[s, Phi[0], q, a] for s in S for q in Psi) == 1, name=f"entrada_bobina_{a}")

    for a in A_out:
        model.addConstr(quicksum(W[s, q, Phi[1], a] for s in S for q in Psi) == 1, name=f"saida_bobina_{a}")

    for a in A:
        if a not in A_out:
            model.addConstr(quicksum(W[s, k, Phi[1], a] for s in S for k in Psi) == 0, name=f"nao_movimenta_bobina_{a}")


    ## TODO: rename constraints after here
    for a in A_in: 
        for s in S:
            model.addConstr(
                tau[s] + sigma_plus[a] <= (1 - x[s, Phi[0], a]) * M,
                name=f"entrada_bobina_{a}_seção_{s}"
            )

    for a in A_in: 
        for s in S:
            model.addConstr(
                omega_minus[a] - tau[s] <= x[s, Phi[1], a] * M,
                name=f"saida_bobina_{a}_seção_{s}"
            )

    for a in A_out:
        for s in S:
            model.addConstr(
                omega_minus[a] - (tau[s] + quicksum(W[s, k, Phi[1], a] * t_load[k, Phi[1]] for k in Psi)) <= (1 - x[s, Phi[1], a]) * M,
                name=f"saida_bobina_{a}_seção_{s}"
            )

    for ids, s in enumerate(S): 
        if ids != 1:
            model.addConstr(
                s >= 
                    s[ids - 1] 
                    + quicksum(t_empty[k,q] * V[S[ids - 1], k, q] for k in Psi for q in Psi)
                    + quicksum(t_load[k,q] * W[S[ids - 1], k, q] for k in Psi for q in Psi)
            )

    for a in A:
        for s in S:
            model.addConstr(
                quicksum(x[s, k, a] for k in Psi) == 1,
                name=f"bobina_{a}_seção_{s}"
            )

    for a in A:
        for s in S:
            model.addConstr(
            quicksum(x[s, k, a] for k in Psi) <= 1,
            name=f"max_1_bobina_{a}_seção_{s}_espaco_{k}"
            )

    for s in S:
        model.addConstr(
            quicksum(W[s, k, q, a] for k in Psi for q in I for a in A) == 0,
            name=f"block_mover_{a}_para_I"
        )

    for s in S:
        model.addConstr(
            quicksum(w[s, k, q, a] for k in O for q in Psi for a in A) == 0,
            name=f"block_mover_{a}_para_O"
        )

    for s in S:
        model.addConstr(
            quicksum(V[s, k, q] for k in Psi for q in Psi) 
            + quicksum(W[s, k, q, a] for k in Psi for q in Psi for a in A)  <= 1,
            name=f"max_1_movimento_por_secao_{s}"
        )

    for k in Psi:
        for ids, s in enumerate(S): 
            if ids != 1:
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in Psi) == quicksum(V[S[ids -1], q, k]),
                    name=f"precedencia_{k}_secao_{s}_carregado"
                )

    for k in Psi:
        for ids, s in enumerate(S): 
            if ids != 1:
                model.addConstr(
                    quicksum(V[s, k, q] for q in Psi) - quicksum(W[S[ids - 1], q, k, a] for q in Psi for a in A),
                    name=f"precedencia_{k}_secao_{s}_descarregado"
                )

    for k in Psi:
        for ids, s in enumerate(S):
            if ids != 1:
                model.addConstr(
                    x[s, k, a] == x[1, k, a] - quicksum(W[s_hat, k, q, a] for q in Psi for a in A for s_hat in S)
                    + quicksum(W[s_hat, q, k, a] for q in Psi for a in A for s_hat in S),
                    name=f"ocupacao_de_{k}_na_secao_{s}_depende_de_movimentos_carregados"
                )

    for s in S:
        for idk, k in enumerate(Psi1):
            if idk != len(Psi1) - 1:
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in Psi for a in A) 
                    <= 1  - quicksum(x[s, Psi1[k + 1], a] for a in A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_vizinho_superior"
                )

    for s in S:
        for idk, k in enumerate(Psi1):
            if idk != 1:
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in Psi for a in A) 
                    <= 1  - quicksum(x[s, Psi1[k - 1], a] for a in A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_vizinho_inferior"
                )

    for s in S:
        for idk, q in enumerate(Psi2):
            if idk != len(Psi2) - 1:
                model.addConstr(
                    2 * quicksum(W[s, k, q, a] for k in Psi for a in A)
                    <= quicksum(x[s, Psi2[q - 1], a] + x[s, Psi2[q + 1], a] for a in A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_inferiores_ocupados"
                )

    model.setObjective(
        quicksum(
            W[s, k, q, a] * E_load[k][q][a] + V[s, k, q] * E_empty[k][q] for s in S for k in Psi for q in Psi for a in A
        ),
        GRB.MINIMIZE
    );

    model.update()

    model.optimize()

    return model




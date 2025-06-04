
import json
import math
from traceback import print_stack
import numpy as np
from gurobipy import Model, GRB, quicksum

def gerar_posicoes(
    num_fileiras: int,
    num_posicoes_nivel_inferior: int,
    num_entrada_saida: int,
):
    """
    Gera as posições de armazenamento. No formato proposto por 
    Weckenborg et al. (2025).
    Exemplo para uma pilha de 3 bobinas

    I + [(111), (112), (121)] + O
    """
    posicoes = []
    for y in range(num_fileiras):
        for x in range(num_posicoes_nivel_inferior):
            print("x", x)
            posicoes.append((y + 1, 1, x + 1))  # nível inferior
            if (x != num_posicoes_nivel_inferior - 1):
                posicoes.append((y + 1, 2, x + 1))  # nível superior, entre duas inferiores

    I = [(-1, 1, y) for y in range(num_entrada_saida)]
    O = [(num_fileiras + 1, 1, y) for y in range(num_entrada_saida)]

    print("posicoes", posicoes)
    print("I", len(I)) 
    print("O", len(O))
    print("Phi", len(posicoes))
    print("Psi", len(posicoes))
    print("Psi1", len(posicoes[0::2]))
    print("Psi2", len(posicoes[1::2]))

    return {
        "Psi":  posicoes,
        "Psi1": posicoes[0::2],
        "Psi2": posicoes[1::2],
        "Phi": I + posicoes + O,
        "I": I,
        "O": O,
    }


def places_are_equal(place1, place2) -> bool:
    return place1[0] == place2[0] and place1[1] == place2[1] and place1[2] == place2[2]

def gerar_custos_de_movimentacao(Phy, A_size):
    """
    Gera os custos de movimentação para o problema de armazenamento.
    
    Cada movimentação vertical no diametro de uma bobina custa 1 unidade de tempo.
    Cada movimentação horizontal no diametro de uma bobina custa 0.5 unidades de tempo.
    
    """
    t_load = np.zeros((len(Phy), len(Phy)), dtype=float)
    t_empty = np.zeros((len(Phy), len(Phy)), dtype=float)
    E_load = np.zeros((len(Phy), len(Phy), A_size), dtype=float)
    E_empty = np.zeros((len(Phy), len(Phy)), dtype=float)

    for idk, k in enumerate(Phy):
        for idq, q in enumerate(Phy):
            if idk == idq:
                continue
            t_vertical = 3 - k[1] +  3 - q[1];
            t_horizontal = ((q[0] - k[0]) + (q[2] - k[2])) *0.5/math.sqrt(2);
            ## TODO: Avaliar pesos abaixo
            t_load[idk][idq] = t_vertical * 20 + t_horizontal * 10
            t_empty[idk][idq] = t_load[idk][idq] * 0.9

    for idk, k in enumerate(Phy):
        for idq, q in enumerate(Phy):
            E_empty[idk][idq] = t_empty[idk][idq] * 20;
            for a in range(A_size):
                # Por simplicidade, todos os custos de movimentação são iguais
                # Isso pode ser ajustado para refletir a realidade de bobinas difrentes
                E_load[idk][idq][a] = t_load[idk][idq] * 100;
    
    print("custos");

    print("t_load", t_load.shape)
    print("t_empty", t_empty.shape)
    print("E_load", E_load.shape)
    print("E_empty", E_empty.shape)

    return {
        "t_load": t_load,
        "t_empty": t_empty,
        "E_load": E_load,
        "E_empty": E_empty
    }


posicoes = gerar_posicoes(
    num_fileiras=1,
    num_posicoes_nivel_inferior=2,
    num_entrada_saida=1,
)

print(json.dumps(posicoes))

custos = gerar_custos_de_movimentacao(posicoes["Phi"], 1)
print("custos", custos)
    
# "Psi":  posicoes,
# "Psi1": posicoes[0::2],
# "Psi2": posicoes[1::2],
# "Phi": I + posicoes + O,
# "I": I,
# "O": O,

# "t_load": t_load,
# "t_empty": t_empty,
# "E_load": E_load,
# "E_empty": E_empty

# A
# Falta A_in e A_out
# Junto com os limites de tempo

from gurobipy import Model, GRB, quicksum

model = Model("Armazenagem")

import numpy as np


def gerar_modelo(Psi, Psi1, Psi2, Phi, I, O, t_load, t_empty, E_load, E_empty, A_in, A_out, A) -> Model:

    # Conjuntos
    S = list(range(len(t_load) * 3))             # seções de tempo (Melhorar lógica aqui)
    M = 99999                    # constante grande

    Phi = np.zeros(len(Psi), dtype=int);
    Psi = np.zeros(len(Psi), dtype=int);
    Psi1 = np.zeros(len(Psi1), dtype=int);
    Psi2 = np.zeros(len(Psi2), dtype=int);
    I = np.zeros(len(I), dtype=int);
    O = np.zeros(len(O), dtype=int);
    A_in = np.zeros(len(A_in), dtype=int);
    A_out = np.zeros(len(A_out), dtype=int);
    A = np.zeros(len(A), dtype=int);

    # Set ranges for all sets

    range_Phi = list(range(len(Phi)))
    range_Psi = list(range(len(Psi)))
    range_Psi1 = list(range(len(Psi1)))
    range_Psi2 = list(range(len(Psi2)))
    range_I = list(range(len(I)))
    range_O = list(range(len(O)))
    range_A = list(range(len(A)))
    range_A_in = list(range(len(A_in)))
    range_A_out = list(range(len(A_out)))

    # Vetores de janelas de tempo de entrada e saída
    # TODO: Adicionar lógica para definir janelas de tempo de entrada e saída
    sigma_minus = np.random.randint(0, 3, size=len(A)) * 1800 # em segundos (30 minutos)
    sigma_plus = sigma_minus + np.random.randint(1, 4, size=len(A)) * 1800
    omega_minus = np.random.randint(3, 6, size=len(A)) * 1800
    omega_plus = omega_minus + np.random.randint(1, 4, size=len(A)) * 1800

    # Variáveis de decisão (inicializadas com zeros)
    W = np.zeros((len(S), len(Phi), len(Phi), len(A)), dtype=int)
    V = np.zeros((len(S), len(Phi), len(Phi)), dtype=int)
    x = np.zeros((len(S), len(Phi), len(A)), dtype=int)
    tau = np.zeros(len(S), dtype=float)
    tau[0] = 0.0  # conforme a restrição τ¹ = 0

    print("sizes")
    print("W", W.shape)
    print("V", V.shape)
    print("x", x.shape)
    print("tau", tau.shape)

    # Saída de dados para verificação (exemplo)
    print("t_load[0][1] =", t_load[0][1])
    print("E_load[0][1][0] =", E_load[0][1][0])
    print("σ⁻[a] =", sigma_minus)
    print("ω⁺[a] =", omega_plus)
    # Definindo variáveis de decisão no modelo



    # W[s][k][q][a] = 1 se bobina a se move de k -> q na seção s
    W = model.addVars(len(S), len(Phi), len(Phi), len(A), vtype=GRB.BINARY, name="W")

    # V[s][k][q] = 1 se movimentação vazia de k -> q ocorre na seção s
    V = model.addVars(len(S), len(Phi), len(Phi), vtype=GRB.BINARY, name="V")

    # x[s][q][a] = 1 se bobina a está na posição q na seção s
    x = model.addVars(len(S), len(Phi), len(A), vtype=GRB.BINARY, name="x")

    # τ[s] = instante de tempo do início da seção s
    tau = model.addVars(len(S), vtype=GRB.CONTINUOUS, name="tau")


    # Definindo restrições do modelo


    # R (1) - tempo_inicial_zero (τ¹ = 0)
    model.addConstr(tau[0] == 0, name="R1_tempo_inicial_zero")  # restrição τ¹ = 0

    # R (2) - entrada_unica_bobina
    for a in range_A_in:
        q_not_in_I = [q for q in range_Phi if q not in I]
        model.addConstr(quicksum(W[s, 0, q, a] for s in S for q in q_not_in_I) == 1, name=f"R2_entrada_unica_bobina_{a}")

    # R (3) - saida_unica_bobina
    for a in range_A_out:
        k_not_in_O = [k for k in range_Phi if k not in O]
        model.addConstr(quicksum(W[s, k, len(Phi) - 1, a] for s in S for k in k_not_in_O) == 1, name=f"R3_saida_unica_bobina_{a}")

    # R (4) - nao_entrega_bobina_armazenada
    for a in range_A:
        if a not in range_A_out:
            model.addConstr(quicksum(W[s, k, len(Phi) - 1, a] for s in S for k in range_Phi) == 0, name=f"R4_nao_entrega_bobina_{a}")

    # R (5) - janela_max_entrada
    for a in range_A_in: 
        for s in S:
            model.addConstr(
                tau[s] + sigma_plus[a] <= (1 - x[s, 0, a]) * M,
                name=f"R5_janela_max_entrada_a{a}_s{s}"
            )

    # R (6) - janela_min_entrada
    for a in range_A_in: 
        for s in S:
            model.addConstr(
                omega_minus[a] - tau[s] <= x[s, 0, a] * M,
                name=f"R6_janela_min_entrada_a{a}_s{s}"
            )

    # R (7) - tempo_min_saida
    for a in range_A_out:
        for s in S:
            model.addConstr(
                omega_minus[a] - (tau[s] + quicksum(W[s, k, len(Phi) - 1, a] * t_load[k, len(Phi) - 1] for k in range_Phi)) <= (1 - x[s, len(Phi) - 1, a]) * M,
                name=f"R7_tempo_min_saida_a{a}_s{s}"
            )

    # R (8) - tempo_progressao
    for ids, s in enumerate(S): 
        if ids != 0:
            model.addConstr(
                s >= 
                    S[ids - 1] 
                    + quicksum(t_empty[k,q] * V[ids - 1, k, q] for k in range_Phi for q in range_Phi)
                    + quicksum(t_load[k,q] * W[ids - 1, k, q, a] for k in range_Phi for q in range_Phi for a in range_A),
                name=f"R8_tempo_progressao_s{s}"
            )

    # R (9) - bobina_ocupa_uma_posicao
    for a in range_A:
        for s in S:
            model.addConstr(
                quicksum(x[s, k, a] for k in range_Phi) == 1,
                name=f"R9_bobina_ocupa_uma_posicao_a{a}_s{s}"
            )

    # R (10) - espaco_ocupa_uma_bobina
    for a in range_A:
        for s in S:
            model.addConstr(
            quicksum(x[s, k, a] for k in range_Psi) <= 1,
            name=f"R10_espaco_ocupa_uma_bobina_a{a}_s{s}"
            )
    # R (11) - bloqueia_movimento_para_entrada
    for s in S:
        model.addConstr(
            quicksum(W[s, k, 0, a] for k in range_Phi for a in range_A) == 0,
            name=f"R11_bloqueia_movimento_para_entrada_s{s}"
        )
    # R (12) - bloqueia_movimento_para_saida
    for s in S:
        model.addConstr(
            quicksum(W[s, len(Phi) - 1, q, a] for q in range_Phi for a in range_A) == 0,
            name=f"R12_bloqueia_movimento_para_saida_s{s}"
        )

    # R (13) - max_1_movimento_por_secao
    for s in S:
        model.addConstr(
            quicksum(V[s, k, q] for k in range_Phi for q in range_Phi) 
            + quicksum(W[s, k, q, a] for k in range_Phi for q in range_Phi for a in range_A)  <= 1,
            name=f"R13_max_1_movimento_por_secao_s{s}"
        )

    # R (14) - precedencia_carregado_apos_vazio
    for k in range_Phi:
        for ids, s in enumerate(S): 
            if ids != 0:
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in range_Phi) == quicksum(V[ids - 1, q, k] for q in range_Phi),
                    name=f"R14_precedencia_carregado_apos_vazio_k{k}_s{s}"
                )

    # R (15) - precedencia_vazio_apos_carregado
    for k in range_Phi:
        for ids, s in enumerate(S): 
            if ids != 0:
                model.addConstr(
                    quicksum(V[s, k, q] for q in range_Phi) - quicksum(W[ids - 1, q, k, a] for q in range_Phi for a in range_A) <= 0,
                    name=f"R15_precedencia_vazio_apos_carregado_k{k}_s{s}"
                )

    # R (16) - ocupacao_depende_movimentos_anteriores
    for k in range_Phi:
        for ids, s in enumerate(S):
            if ids != 0:
                model.addConstr(
                    x[s, k, a] == x[1, k, a] - quicksum(W[s_hat, k, q, a] for q in range_Phi for a in range_A for s_hat in S)
                    + quicksum(W[s_hat, q, k, a] for q in range_Phi for a in range_A for s_hat in S),
                    name=f"R16_ocupacao_depende_movimentos_anteriores_k{k}_s{s}"
                )

    # R17 - Restrição (eq:upper_layer_blocking) do artigo
    # Garante que uma bobina na camada 1 só pode ser movimentada se não houver bobina acima (camada 2, próxima posição)
    for s in S:
        for idk, k in enumerate(Psi1):
            # Psi1 não inclui entrada/saída, garantir isso
            if idk < len(Psi1) - 1:  # idk+1 existe
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in range_Phi for a in range_A)
                    <= 1  - quicksum(x[s, idk + 1, a] for a in range_A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_vizinho_superior"
                )

    # R18 - Restrição (eq:upper_layer_blocking_1) do artigo
    # Garante que uma bobina na camada 2 só pode ser movimentada se não houver bobina abaixo (camada 1, posição anterior)
    for s in S:
        for idk, k in enumerate(Psi1):
            if idk > 0:  # idk-1 existe
                model.addConstr(
                    quicksum(W[s, k, q, a] for q in range_Phi for a in range_A)
                    <= 1  - quicksum(x[s, idk - 1, a] for a in range_A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_vizinho_inferior"
                )

    # R19 - Restrição (eq:lower_layer_blocking) do artigo
    # Garante que uma bobina só pode ser posicionada na camada 2 se houver bobina imediatamente abaixo (camada 1) nos dois vizinhos
    for s in S:
        for idk, q in enumerate(Psi2):
            if idk != 0:
                model.addConstr(
                    2 * quicksum(W[s, k, q, a] for k in range_Phi for a in range_A)
                    <= quicksum(x[s, idk - 1, a] + x[s, idk + 1, a] for a in range_A),
                    name=f"movimento_carregado_{k}_na_secao_{s}_inferiores_ocupados"
                )

    model.setObjective(
        quicksum(
            W[s, k, q, a] * E_load[k][q][a] for s in S for k in range_Phi for q in range_Phi for a in range_A
        )
        + quicksum(
            V[s, k, q] * E_empty[k][q] for s in S for k in range_Phi for q in range_Phi
        ),
        GRB.MINIMIZE
    );

    model.update()

    model.optimize()


    print("Status:", model.printStats())
    print("Tempo de execução:", model.runtime)

    return model

testes = [
    {
        "num_fileiras": 1,
        "num_posicoes_nivel_inferior": 2,
        "num_entrada_saida": 1,
        "num_bobinas": 1,
        "num_bobinas_entrada": 1,
        "num_bobinas_saida": 1,
    },
    {
        "num_fileiras": 2,
        "num_posicoes_nivel_inferior": 2,
        "num_entrada_saida": 1,
        "num_bobinas": 1,
        "num_bobinas_entrada": 1,
        "num_bobinas_saida": 1,
    }
]

def test():
    for teste in testes:
        posicoes = gerar_posicoes(
            teste["num_fileiras"],
            teste["num_posicoes_nivel_inferior"],
            teste["num_entrada_saida"],
        )
        custos = gerar_custos_de_movimentacao(posicoes["Phi"], teste["num_bobinas"])
        
        A = [ 0 ]

        gerar_modelo(
            posicoes["Psi"],
            posicoes["Psi1"],
            posicoes["Psi2"],
            posicoes["Phi"],
            posicoes["I"],
            posicoes["O"],
            custos["t_load"],
            custos["t_empty"],
            custos["E_load"],
            custos["E_empty"],
            A,
            A,
            A,
        )

test()
        


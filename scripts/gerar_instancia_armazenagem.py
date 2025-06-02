'''
    Função plotar_instancia_2d()

Esta função cria uma visualização 2D do layout de armazenamento.
Os símbolos vermelhos representam as bobinas do tipo "saída" (conforme definido no dicionário cores onde "saida" é
 mapeado para "red").

O formato dos marcadores é definido pelo dicionário marcadores:
"o" (círculo) para nível inferior (z=0)
"s" (quadrado) para nível superior (z=1)
"X" para pontos de entrada/saída (nível -1)

    Função plotar_instancia_3d()

Cria uma visualização 3D mais realista, representando as bobinas como cilindros horizontais:
Pontos de entrada/saída são marcados com "X"
Bobinas são representadas como cilindros coloridos
Cada bobina tem uma letra indicando seu tipo (E, S, B, I)

    Função gerar_instancia_armazenagem()

Gera uma configuração aleatória de armazenamento com:
Bobinas de entrada (azuis)
Bobinas de saída (vermelhas)
Bobinas bloqueadoras (laranjas)
Bobinas irrelevantes (cinzas)
Posições vazias (brancas)

Na visualização 2D, os símbolos vermelhos são especificamente:

Círculos vermelhos ("o"): bobinas de saída no nível inferior
Quadrados vermelhos ("s"): bobinas de saída no nível superior
"X" vermelhos: pontos de saída físicos (definidos em pontos_saida)
Estes elementos são gerados com base nos parâmetros num_bobinas_saida e pontos_saida passados para a função
gerar_instancia_armazenagem().

    Exemplo de Uso

No exemplo atualmente gerado, são criadas:

2 bobinas de saída (vermelhas)
1 bobina de entrada (azul)
1 bobina bloqueadora (laranja)
Pontos de entrada em (0,-1) e (1,-1)
Pontos de saída em (0,4) e (1,4)

Isso explica por que você vê símbolos vermelhos no plot - eles representam as bobinas que estão marcadas para
saída e os pontos físicos de saída do armazém.
'''

import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def plotar_instancia_2d(instancia):
    cores = {
        "entrada": "blue",
        "saida": "red",
        "bloqueadora": "orange",
        "irrelevante": "gray",
        "vazio": "white"
    }

    marcadores = {
        1: "o",  # nível inferior
        2: "s",  # nível superior
        0: "X"   # pontos de entrada/saída
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    for item in instancia:
        x, y, z = item["x"], item["y"], item["z"]
        cor = cores.get(item["tipo"], "black")
        marcador = marcadores.get(item["nivel"], "^")
        ax.scatter(x, y, c=cor, marker=marcador, s=100, edgecolors='black', label=item["tipo"])

    # Remover duplicatas da legenda
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    ax.set_title("Visualização 2D das Bobinas na Área de Armazenagem")
    ax.set_xlabel("x (coluna)")
    ax.set_ylabel("y (fileira)")
    ax.grid(True)
    ax.set_aspect('equal')
    plt.show()


def plotar_instancia_3d(instancia, raio=0.4, altura_bobina=1.0):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    cmap_tipo = {
        "entrada": "blue",
        "saida": "red",
        "bloqueadora": "orange",
        "irrelevante": "gray",
        "vazio": "white"
    }

    def plotar_cilindro_horizontal(x, y, z, r, comprimento, cor):
        theta = np.linspace(0, 2 * np.pi, 20)
        y_cil = np.linspace(y - comprimento / 2, y + comprimento / 2, 2)
        theta_grid, y_grid = np.meshgrid(theta, y_cil)
        x_grid = r * np.cos(theta_grid) + x
        z_grid = r * np.sin(theta_grid) + z
        ax.plot_surface(x_grid, y_grid, z_grid, color=cor, edgecolor='k', linewidth=0.2)

    for item in instancia:
        if item["tipo"] == "vazio":
            continue
        if item["nivel"] == 0:
            ax.scatter(item["x"], item["y"], 0, c=cmap_tipo.get(item["tipo"], "black"), marker="X", s=80)
        else:
            plotar_cilindro_horizontal(
                item["x"],
                item["y"],
                item["z"] * 1.1,
                raio,
                altura_bobina,
                cmap_tipo.get(item["tipo"], "black")
            )
            ax.text(item["x"], item["y"], item["z"] * 1.1 + 0.6,
                    item["tipo"][0].upper(), fontsize=7, color="black", ha='center')

    ax.set_xlabel("x (coluna)")
    ax.set_ylabel("y (fileira)")
    ax.set_zlabel("z (nível)")
    ax.set_title("Visualização 3D das Bobinas Empilhadas")
    ax.set_box_aspect([2, 2, 1])
    ax.view_init(elev=20, azim=45)
    plt.tight_layout()
    plt.show()


def gerar_instancia_armazenagem(
    num_fileiras: int,
    num_posicoes_nivel_inferior: int,
    num_bobinas_entrada: int,
    num_bobinas_saida: int,
    num_bobinas_bloqueadoras: int,
    pontos_entrada: list,
    pontos_saida: list,
    incluir_irrelevantes: bool = True,
    random_seed: int = None
):
    if random_seed is not None:
        random.seed(random_seed)

    # Gera posições do nível inferior (z=0) e superior (z=1)
    posicoes = []
    for y in range(num_fileiras):
        for x in range(num_posicoes_nivel_inferior):
            posicoes.append((x, y, 0))  # nível inferior
        for x in range(num_posicoes_nivel_inferior - 1):
            posicoes.append((x + 0.5, y, 1))  # nível superior, entre duas inferiores
    
    posicoes_ordenadas = posicoes.copy()

    random.shuffle(posicoes)

    instancia = []
    contador_id = 1

    def alocar_bobinas(qtd, tipo):
        nonlocal contador_id
        bobinas = []
        for _ in range(qtd):
            while posicoes:
                x, y, z = posicoes.pop(0)
                if z == 1:
                    # Verifica se há suporte embaixo
                    esquerda = (x - 0.5, y, 0)
                    direita = (x + 0.5, y, 0)
                    if esquerda not in ocupadas or direita not in ocupadas:
                        continue  # sem suporte
                pos = {
                    "id": f"B{contador_id}",
                    "x": x,
                    "y": y,
                    "z": z,
                    "tipo": tipo,
                    "nivel": 1 if z == 0 else 2
                }
                ocupadas.add((x, y, z))
                bobinas.append(pos)
                contador_id += 1
                break
        return bobinas

    ocupadas = set()

    instancia.extend(alocar_bobinas(num_bobinas_saida, "saida"))
    instancia.extend(alocar_bobinas(num_bobinas_bloqueadoras, "bloqueadora"))
    instancia.extend(alocar_bobinas(num_bobinas_entrada, "entrada"))

    if incluir_irrelevantes:
        while posicoes:
            x, y, z = posicoes.pop(0)
            if z == 1:
                esquerda = (x - 0.5, y, 0)
                direita = (x + 0.5, y, 0)
                if esquerda not in ocupadas or direita not in ocupadas:
                    continue
            instancia.append({
                "id": f"B{contador_id}",
                "x": x,
                "y": y,
                "z": z,
                "tipo": "irrelevante",
                "nivel": 1 if z == 0 else 2
            })
            ocupadas.add((x, y, z))
            contador_id += 1

    # Adiciona posições vazias restantes (sem bobinas alocadas)
    for y in range(num_fileiras):
        for x in range(num_posicoes_nivel_inferior):
            if (x, y, 0) not in ocupadas:
                instancia.append({
                    "id": None, "x": x, "y": y, "z": 0, "tipo": "vazio", "nivel": 1
                })
        for x in range(num_posicoes_nivel_inferior - 1):
            if (x + 0.5, y, 1) not in ocupadas:
                esquerda = (x, y, 0)
                direita = (x + 1, y, 0)
                if esquerda in ocupadas and direita in ocupadas:
                    instancia.append({
                        "id": None, "x": x + 0.5, "y": y, "z": 1, "tipo": "vazio", "nivel": 2
                    })

    # Adiciona os pontos de entrada/saída como referência
    for ponto in pontos_entrada:
        instancia.append({"id": None, "x": ponto[0], "y": ponto[1], "z": -1, "tipo": "entrada", "nivel": 0})
    for ponto in pontos_saida:
        instancia.append({"id": None, "x": ponto[0], "y": ponto[1], "z": -1, "tipo": "saida", "nivel": 0})

    return instancia


instancia = gerar_instancia_armazenagem(
    num_fileiras=2,
    num_posicoes_nivel_inferior=3,
    num_bobinas_entrada=1,
    num_bobinas_saida=2,
    num_bobinas_bloqueadoras=1,
    pontos_entrada=[(0, -1), (1, -1)],
    pontos_saida=[(0, 4), (1, 4)],
    incluir_irrelevantes=False,
    random_seed=42
)

for b in instancia:
    print(b)

plotar_instancia_2d(instancia)
plotar_instancia_3d(instancia)
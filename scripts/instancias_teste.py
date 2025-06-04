import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple  # Para type hinting


def distribuir_bobinas(
        num_total_bobinas: int,
        num_fileiras: int,
        max_bobinas_base_fileira: int
) -> Tuple[List[Tuple[int, int, int]], List[int]]:
    """
    Organiza as bobinas aleatoriamente em um espaço com fileiras e camadas e retorna
    a lista de bobinas colocadas e um array indicando a ocupação de todas as posições possíveis.

    A regra de empilhamento é que uma camada superior (l) deve ter no máximo
    uma bobina a menos que a camada imediatamente inferior (l-1) na mesma fileira.
    (N_camada_l <= N_camada_l-1 - 1).

    Args:
        num_total_bobinas (int): O número total de bobinas a serem organizadas.
        num_fileiras (int): O número de fileiras disponíveis (1-indexado).
        max_bobinas_base_fileira (int): A capacidade máxima de bobinas na camada base (camada 1)
                                         de cada fileira.

    Returns:
        Tuple[List[Tuple[int, int, int]], List[int]]:
            - Primeiro elemento: Uma lista de tuplas (fileira, camada, posicao_na_camada),
              todas 1-indexadas, representando a organização das bobinas colocadas.
              Pode ser uma lista parcial se nem todas as bobinas puderam ser colocadas.
            - Segundo elemento: Uma lista de 0s e 1s. Esta lista representa todas as
              posições possíveis no espaço definido. Um 1 indica que a posição
              correspondente está ocupada por uma bobina, e um 0 indica que está vazia.
              A ordem das posições possíveis é: fileira por fileira (crescente),
              dentro de cada fileira camada por camada (crescente), e dentro de
              cada camada posição por posição (crescente).
    """
    bobinas_colocadas: List[Tuple[int, int, int]] = []

    # 1. Gerar a lista de todas as posições possíveis no espaço definido.
    #    Esta lista também define a ordem para o array de ocupação.
    todas_posicoes_possiveis_ordenadas: List[Tuple[int, int, int]] = []
    if num_fileiras > 0 and max_bobinas_base_fileira > 0:
        for r_loop in range(1, num_fileiras + 1):
            for l_loop in range(1, max_bobinas_base_fileira + 1):
                # Número máximo de posições na camada l_loop, para uma base de max_bobinas_base_fileira
                # (formando uma pirâmide de slots potenciais)
                max_p_nesta_camada = max_bobinas_base_fileira - (l_loop - 1)
                if max_p_nesta_camada < 1:
                    break  # Nenhuma posição nesta camada ou mais profundas para esta fileira
                for p_loop in range(1, max_p_nesta_camada + 1):
                    todas_posicoes_possiveis_ordenadas.append((r_loop, l_loop, p_loop))

    # 2. Lidar com entradas de dimensão inválidas ou 0 bobinas solicitadas.
    # Se as dimensões não permitem posições, todas_posicoes_possiveis_ordenadas será [].
    if not (num_fileiras > 0 and max_bobinas_base_fileira > 0):
        if num_total_bobinas > 0:  # Só imprime erro se bobinas eram esperadas
            print(
                "Erro: 'max_bobinas_base_fileira' e 'num_fileiras' devem ser positivos para definir o espaço de posições.")
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)  # Resulta em [] se não há posições
        return [], ocupacao_array

    if num_total_bobinas == 0:
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)
        return [], ocupacao_array

    # 3. Verificar capacidade máxima teórica do sistema
    max_capacidade_total_sistema = len(todas_posicoes_possiveis_ordenadas)
    if num_total_bobinas > max_capacidade_total_sistema:
        print(f"Erro: O número de bobinas ({num_total_bobinas}) excede a capacidade máxima "
              f"do sistema ({max_capacidade_total_sistema}) definida pelas dimensões.")
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)  # Array de zeros para o espaço vazio
        return [], ocupacao_array  # Nenhuma bobina colocada

    # 4. Loop principal para colocar bobinas
    for _ in range(num_total_bobinas):
        posicoes_validas_para_adicionar: List[Tuple[int, int, int]] = []

        for r_idx in range(1, num_fileiras + 1):
            bobinas_na_camada_1_fileira_r = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == 1]
            num_bobinas_camada_1_fileira_r = len(bobinas_na_camada_1_fileira_r)

            if num_bobinas_camada_1_fileira_r < max_bobinas_base_fileira:
                posicao_para_adicionar_c1 = (r_idx, 1, num_bobinas_camada_1_fileira_r + 1)
                posicoes_validas_para_adicionar.append(posicao_para_adicionar_c1)

            max_camadas_teoricas_na_fileira = max_bobinas_base_fileira
            for l_idx in range(2, max_camadas_teoricas_na_fileira + 1):
                bobinas_na_camada_anterior = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == l_idx - 1]
                num_bobinas_camada_anterior = len(bobinas_na_camada_anterior)

                if num_bobinas_camada_anterior == 0:
                    break

                bobinas_na_camada_atual_l = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == l_idx]
                num_bobinas_camada_atual_l = len(bobinas_na_camada_atual_l)

                if num_bobinas_camada_atual_l + 1 <= num_bobinas_camada_anterior - 1:
                    posicao_para_adicionar_cl = (r_idx, l_idx, num_bobinas_camada_atual_l + 1)
                    posicoes_validas_para_adicionar.append(posicao_para_adicionar_cl)
                else:
                    break

        if not posicoes_validas_para_adicionar:
            print(f"Aviso: Não foi possível encontrar uma posição válida para a próxima bobina. "
                  f"{len(bobinas_colocadas)} de {num_total_bobinas} bobinas foram colocadas.")
            # Sai do loop de colocação; bobinas_colocadas contém as bobinas colocadas até este ponto.
            break

        posicao_escolhida = random.choice(posicoes_validas_para_adicionar)
        bobinas_colocadas.append(posicao_escolhida)

    # 5. Gerar o array de ocupação final com base nas bobinas efetivamente colocadas.
    ocupacao_array_final: List[int] = []
    conjunto_bobinas_colocadas = set(bobinas_colocadas)  # Para busca eficiente (O(1) em média)
    for pos_possivel in todas_posicoes_possiveis_ordenadas:
        if pos_possivel in conjunto_bobinas_colocadas:
            ocupacao_array_final.append(1)
        else:
            ocupacao_array_final.append(0)

    return bobinas_colocadas, ocupacao_array_final


def plotar_organizacao(bobinas_colocadas, num_total_bobinas_solicitadas, num_fileiras, max_bobinas_base_fileira):
    """
    Plota a organização das bobinas. (Função inalterada da resposta anterior)
    """
    if not bobinas_colocadas:
        if num_total_bobinas_solicitadas > 0:
            print("Nenhuma bobina foi colocada para plotar (possível erro na geração).")
        else:
            print("Nenhuma bobina solicitada para plotar.")
        fig, ax = plt.subplots()
        ax.set_title("Organização de Bobinas (Vazio)")
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()
        return

    fig_largura = max(8, max_bobinas_base_fileira * 1.5)
    fig_altura = max(6, num_fileiras * 2.5)
    fig, ax = plt.subplots(figsize=(fig_largura, fig_altura))

    RAIO_BOBINA = 0.45
    DIAMETRO_VISUAL = 2 * RAIO_BOBINA

    ESPACAMENTO_Y_CAMADA = 0.866 * DIAMETRO_VISUAL * 1.05
    ESPACAMENTO_X_BOBINA = DIAMETRO_VISUAL * 1.05
    OFFSET_X_CAMADA = ESPACAMENTO_X_BOBINA / 2.0

    ALTURA_MAX_FILEIRA_VISUAL = max_bobinas_base_fileira * ESPACAMENTO_Y_CAMADA
    ESPACAMENTO_Y_FILEIRA_ENTRE_BASES = ALTURA_MAX_FILEIRA_VISUAL + 1.5 * ESPACAMENTO_Y_CAMADA

    min_x_plot, max_x_plot = float('inf'), float('-inf')
    min_y_plot, max_y_plot = float('inf'), float('-inf')

    for r_idx, l_idx, p_idx in bobinas_colocadas:
        y_centro = -(r_idx - 1) * ESPACAMENTO_Y_FILEIRA_ENTRE_BASES + (l_idx - 1) * ESPACAMENTO_Y_CAMADA
        x_centro = (p_idx - 1) * ESPACAMENTO_X_BOBINA + (l_idx - 1) * OFFSET_X_CAMADA

        circulo = patches.Circle((x_centro, y_centro), RAIO_BOBINA,
                                 facecolor='skyblue', edgecolor='black', linewidth=1)
        ax.add_patch(circulo)

        texto_bobina = f"{r_idx}{l_idx}{p_idx}"
        ax.text(x_centro, y_centro, texto_bobina,
                ha='center', va='center', fontsize=7, color='black', weight='bold')

        min_x_plot = min(min_x_plot, x_centro - RAIO_BOBINA)
        max_x_plot = max(max_x_plot, x_centro + RAIO_BOBINA)
        min_y_plot = min(min_y_plot, y_centro - RAIO_BOBINA)
        max_y_plot = max(max_y_plot, y_centro + RAIO_BOBINA)

    if not bobinas_colocadas and num_total_bobinas_solicitadas == 0:  # Caso especial para 0 bobinas solicitadas
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
    elif not bobinas_colocadas:  # Outros casos onde bobinas_colocadas está vazio
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
    else:
        padding = DIAMETRO_VISUAL
        ax.set_xlim(min_x_plot - padding, max_x_plot + padding)
        ax.set_ylim(min_y_plot - padding, max_y_plot + padding)

    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f"Organização de {len(bobinas_colocadas)} Bobinas")
    ax.axis('off')

    plt.show()


# def ordenar_instancia(arranjo):
#     """
#     Ordena a instancia de acordo com o formato proposto por Weckenborg et al. (2025).
    
#     Args:
#         instancia (list): Lista de dicionários representando as bobinas.
    
#     Returns:
#         list: Lista ordenada de acordo com o formato.
#     """
#     instancia_ordenada = sorted(instancia, key=lambda x: (x["nivel"], x["x"], x["y"]))
#     return instancia_ordenada

# Exemplo de uso:
if __name__ == '__main__':
    # Cenário 1: Exemplo do usuário para o array de ocupação
    print("Cenário 1: Exemplo do Usuário")
    num_bobinas_ex1 = 5
    num_fileiras_ex1 = 2
    max_base_ex1 = 3

    # A função agora retorna duas listas
    arranjo_ex1, ocupacao_ex1 = distribuir_bobinas(num_bobinas_ex1, num_fileiras_ex1, max_base_ex1)

    # arranjo_ex1_ordenado = ordenar_instancia(arranjo_ex1)
    print(f"Arranjo gerado (bobinas colocadas): {arranjo_ex1}")
    print(f"Array de ocupação de todas as posições possíveis: {ocupacao_ex1}")

    # Para verificar com o exemplo do usuário:
    # Se arranjo_ex1 contiver as bobinas {(2,1,1), (2,1,2), (2,1,3), (1,1,1), (2,2,1)}
    # (a ordem no arranjo_ex1 pode variar devido à aleatoriedade),
    # o ocupacao_ex1 esperado seria [1,0,0,0,0,0,1,1,1,1,0,0]
    # O comprimento total de posições possíveis para (fil=2, base=3) é (3+2+1)*2 = 12.
    print(f"(Comprimento do array de ocupação: {len(ocupacao_ex1)})")

    if arranjo_ex1 or num_bobinas_ex1 == 0:  # Plota mesmo se arranjo_ex1 for vazio mas 0 bobinas foram pedidas
        plotar_organizacao(arranjo_ex1, num_bobinas_ex1, num_fileiras_ex1, max_base_ex1)
    print("-" * 30)

    # Cenário 2: Uma fileira completa
    print("Cenário 2: Uma Fileira Completa")
    num_bobinas_ex2 = 6  # (3 na base, 2 na camada 2, 1 na camada 3)
    num_fileiras_ex2 = 1
    max_base_ex2 = 3
    arranjo_ex2, ocupacao_ex2 = distribuir_bobinas(num_bobinas_ex2, num_fileiras_ex2, max_base_ex2)
    print(f"Arranjo gerado: {arranjo_ex2}")
    print(f"Array de ocupação: {ocupacao_ex2}")  # Esperado: [1,1,1,1,1,1] para (fil=1,base=3)
    if arranjo_ex2 or num_bobinas_ex2 == 0:
        plotar_organizacao(arranjo_ex2, num_bobinas_ex2, num_fileiras_ex2, max_base_ex2)
    print("-" * 30)

    # Cenário 3: Múltiplas fileiras, parcialmente preenchidas
    print("Cenário 3: Múltiplas Fileiras Parciais")
    num_bobinas_ex3 = 10
    num_fileiras_ex3 = 3
    max_base_ex3 = 4  # Max posições por fileira: 4+3+2+1 = 10. Total: 30.
    arranjo_ex3, ocupacao_ex3 = distribuir_bobinas(num_bobinas_ex3, num_fileiras_ex3, max_base_ex3)
    print(f"Arranjo gerado: {arranjo_ex3}")
    print(f"Array de ocupação: {ocupacao_ex3}")
    if arranjo_ex3 or num_bobinas_ex3 == 0:
        plotar_organizacao(arranjo_ex3, num_bobinas_ex3, num_fileiras_ex3, max_base_ex3)
    print("-" * 30)

    # Cenário 4: Tentativa de colocar mais bobinas do que o possível
    print("Cenário 4: Excesso de Bobinas")
    num_bobinas_ex4 = 15
    num_fileiras_ex4 = 2
    max_base_ex4 = 3  # Capacidade máxima por fileira: 3+2+1=6. Total: 12.
    arranjo_ex4, ocupacao_ex4 = distribuir_bobinas(num_bobinas_ex4, num_fileiras_ex4, max_base_ex4)
    print(f"Arranjo gerado: {arranjo_ex4}")  # Esperado: [] e mensagem de erro
    print(f"Array de ocupação: {ocupacao_ex4}")  # Esperado: array de 12 zeros
    if arranjo_ex4 or num_bobinas_ex4 == 0:
     print("-" * 30)

    # Cenário 5: Zero bobinas
    print("Cenário 5: Zero Bobinas")
    num_bobinas_ex5 = 0
    num_fileiras_ex5 = 2
    max_base_ex5 = 3
    arranjo_ex5, ocupacao_ex5 = distribuir_bobinas(num_bobinas_ex5, num_fileiras_ex5, max_base_ex5)
    print(f"Arranjo gerado: {arranjo_ex5}")  # Esperado: []
    print(f"Array de ocupação: {ocupacao_ex5}")  # Esperado: [0,0,0,0,0,0,0,0,0,0,0,0] (12 zeros)
    plotar_organizacao(arranjo_ex5, num_bobinas_ex5, num_fileiras_ex5, max_base_ex5)
    print("-" * 30)

    # Cenário 6: Dimensões inválidas
    print("Cenário 6: Dimensões Inválidas (fileiras=0)")
    num_bobinas_ex6 = 5
    num_fileiras_ex6 = 7
    max_base_ex6 = 2
    arranjo_ex6, ocupacao_ex6 = distribuir_bobinas(num_bobinas_ex6, num_fileiras_ex6, max_base_ex6)
    print(f"Arranjo gerado: {arranjo_ex6}")  # Esperado: []
    print(f"Array de ocupação: {ocupacao_ex6}")  # Esperado: []
    if arranjo_ex6 or num_bobinas_ex6 == 0:
        plotar_organizacao(arranjo_ex6, num_bobinas_ex6, num_fileiras_ex6, max_base_ex6)
    print("-" * 30)

    print("Cenário 7: Dimensões Inválidas (max_base=0)")
    num_bobinas_ex7 = 5
    num_fileiras_ex7 = 2
    max_base_ex7 = 0
    arranjo_ex7, ocupacao_ex7 = distribuir_bobinas(num_bobinas_ex7, num_fileiras_ex7, max_base_ex7)
    print(f"Arranjo gerado: {arranjo_ex7}")  # Esperado: []
    print(f"Array de ocupação: {ocupacao_ex7}")  # Esperado: []
    if arranjo_ex7 or num_bobinas_ex7 == 0:
        plotar_organizacao(arranjo_ex7, num_bobinas_ex7, num_fileiras_ex7, max_base_ex7)
    print("-" * 30)

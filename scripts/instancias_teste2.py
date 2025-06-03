import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple, Set


def distribuir_bobinas(
        num_total_bobinas: int,
        num_fileiras: int,
        max_bobinas_base_fileira: int
) -> Tuple[List[Tuple[int, int, int]], List[int]]:
    """
    Organiza as bobinas aleatoriamente em um espaço com fileiras e camadas,
    com a altura máxima de cada fileira limitada a duas camadas.
    Retorna a lista de bobinas colocadas e um array indicando a ocupação de todas as posições possíveis.

    A regra de empilhamento para a segunda camada é que ela deve ter no máximo
    uma bobina a menos que a camada base (l-1) na mesma fileira.
    (N_camada_2 <= N_camada_1 - 1).

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
    bobinas_colocadas_set: Set[Tuple[int, int, int]] = set()

    # 1. Gerar a lista de todas as posições possíveis no espaço definido, LIMITANDO A 2 CAMADAS.
    todas_posicoes_possiveis_ordenadas: List[Tuple[int, int, int]] = []
    if num_fileiras > 0 and max_bobinas_base_fileira > 0:
        for r_loop in range(1, num_fileiras + 1):
            # Limitamos l_loop para ir apenas até a camada 2
            for l_loop in range(1, 3):  # Vai de 1 a 2 (inclusive)
                # Número máximo de posições na camada l_loop, para uma base de max_bobinas_base_fileira
                max_p_nesta_camada = max_bobinas_base_fileira - (l_loop - 1)
                if max_p_nesta_camada < 1:
                    break
                for p_loop in range(1, max_p_nesta_camada + 1):
                    todas_posicoes_possiveis_ordenadas.append((r_loop, l_loop, p_loop))

    # 2. Lidar com entradas de dimensão inválidas ou 0 bobinas solicitadas.
    if not (num_fileiras > 0 and max_bobinas_base_fileira > 0):
        if num_total_bobinas > 0:
            print(
                "Erro: 'max_bobinas_base_fileira' e 'num_fileiras' devem ser positivos para definir o espaço de posições.")
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)
        return [], ocupacao_array

    if num_total_bobinas == 0:
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)
        return [], ocupacao_array

    # 3. Verificar capacidade máxima teórica do sistema
    max_capacidade_total_sistema = len(todas_posicoes_possiveis_ordenadas)
    if num_total_bobinas > max_capacidade_total_sistema:
        print(f"Erro: O número de bobinas ({num_total_bobinas}) excede a capacidade máxima "
              f"do sistema ({max_capacidade_total_sistema}) definida pelas dimensões (limitado a 2 camadas).")
        ocupacao_array = [0] * len(todas_posicoes_possiveis_ordenadas)
        return [], ocupacao_array

    # Embaralha todas as posições possíveis para randomizar a ordem de tentativa de preenchimento
    posicoes_para_tentar_preencher = list(todas_posicoes_possiveis_ordenadas)
    random.shuffle(posicoes_para_tentar_preencher)

    # Iterar sobre as posições embaralhadas e tentar colocar as bobinas
    for r_idx, l_idx, p_idx in posicoes_para_tentar_preencher:
        if len(bobinas_colocadas) >= num_total_bobinas:
            break

        if (r_idx, l_idx, p_idx) in bobinas_colocadas_set:
            continue

        is_position_currently_valid = False
        if l_idx == 1:  # Posição na camada base
            bobinas_na_camada_1_fileira_r = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == 1]
            num_bobinas_camada_1_fileira_r = len(bobinas_na_camada_1_fileira_r)
            # A posição p_idx deve ser a próxima na sequência E dentro do limite da base
            if p_idx == num_bobinas_camada_1_fileira_r + 1 and p_idx <= max_bobinas_base_fileira:
                is_position_currently_valid = True
        elif l_idx == 2:  # Posição na segunda camada
            bobinas_na_camada_anterior = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == 1]  # Camada 1
            num_bobinas_camada_anterior = len(bobinas_na_camada_anterior)

            if num_bobinas_camada_anterior > 0:  # Deve haver bobinas na camada 1 para suportar a 2
                bobinas_na_camada_atual_l = [b for b in bobinas_colocadas if b[0] == r_idx and b[1] == 2]  # Camada 2
                num_bobinas_camada_atual_l = len(bobinas_na_camada_atual_l)

                # Verifica se a posição 'p_idx' é a próxima na sequência para a camada 2
                # E se a regra N_camada_2 <= N_camada_1 - 1 é respeitada
                if p_idx == num_bobinas_camada_atual_l + 1 and \
                        (num_bobinas_camada_atual_l + 1) <= (num_bobinas_camada_anterior - 1):
                    is_position_currently_valid = True
        # Nenhuma outra camada (l_idx > 2) será considerada devido ao limite do loop for

        if is_position_currently_valid:
            bobinas_colocadas.append((r_idx, l_idx, p_idx))
            bobinas_colocadas_set.add((r_idx, l_idx, p_idx))

    # Gerar o array de ocupação final com base nas bobinas efetivamente colocadas.
    ocupacao_array_final: List[int] = []
    for pos_possivel in todas_posicoes_possiveis_ordenadas:
        if pos_possivel in bobinas_colocadas_set:
            ocupacao_array_final.append(1)
        else:
            ocupacao_array_final.append(0)

    return bobinas_colocadas, ocupacao_array_final


def plotar_organizacao(bobinas_colocadas: List[Tuple[int, int, int]],
                       num_total_bobinas_solicitadas: int,
                       num_fileiras: int,
                       max_bobinas_base_fileira: int) -> None:
    """
    Plota a organização das bobinas, incluindo posições vazias que poderiam ser ocupadas.
    Esta função foi adaptada para plots com apenas duas camadas de altura.
    """
    fig_largura = max(8, max_bobinas_base_fileira * 1.5)
    # A altura visual para 2 camadas é menor do que para múltiplas camadas
    fig_altura = max(6, num_fileiras * 1.5)  # Ajuste da altura do plot

    fig, ax = plt.subplots(figsize=(fig_largura, fig_altura))

    RAIO_BOBINA = 0.45
    DIAMETRO_VISUAL = 2 * RAIO_BOBINA

    ESPACAMENTO_Y_CAMADA = 0.866 * DIAMETRO_VISUAL * 1.05
    ESPACAMENTO_X_BOBINA = DIAMETRO_VISUAL * 1.05
    OFFSET_X_CAMADA = ESPACAMENTO_X_BOBINA / 2.0

    # A altura máxima de cada fileira será sempre baseada em 2 camadas
    ALTURA_MAX_FILEIRA_VISUAL = ESPACAMENTO_Y_CAMADA  # A altura é do topo da camada 2 para a base da 1
    ESPACAMENTO_Y_FILEIRA_ENTRE_BASES = ALTURA_MAX_FILEIRA_VISUAL + 1.5 * ESPACAMENTO_Y_CAMADA

    min_x_plot, max_x_plot = float('inf'), float('-inf')
    min_y_plot, max_y_plot = float('inf'), float('-inf')

    # Obter todas as posições possíveis (limitado a 2 camadas) para plotagem
    todas_posicoes_possiveis: List[Tuple[int, int, int]] = []
    if num_fileiras > 0 and max_bobinas_base_fileira > 0:
        for r_loop in range(1, num_fileiras + 1):
            for l_loop in range(1, 3):  # Apenas camada 1 e 2
                max_p_nesta_camada = max_bobinas_base_fileira - (l_loop - 1)
                if max_p_nesta_camada < 1:
                    break
                for p_loop in range(1, max_p_nesta_camada + 1):
                    todas_posicoes_possiveis.append((r_loop, l_loop, p_loop))

    conjunto_bobinas_colocadas = set(bobinas_colocadas)

    for r_idx, l_idx, p_idx in todas_posicoes_possiveis:
        # As coordenadas Y são invertidas para que a camada 1 seja a mais baixa no gráfico
        y_centro = -(r_idx - 1) * ESPACAMENTO_Y_FILEIRA_ENTRE_BASES + (l_idx - 1) * ESPACAMENTO_Y_CAMADA
        x_centro = (p_idx - 1) * ESPACAMENTO_X_BOBINA + (l_idx - 1) * OFFSET_X_CAMADA

        cor_face = 'white' if (r_idx, l_idx, p_idx) not in conjunto_bobinas_colocadas else 'skyblue'
        cor_borda = 'gray' if (r_idx, l_idx, p_idx) not in conjunto_bobinas_colocadas else 'black'
        linha_borda = 0.5 if (r_idx, l_idx, p_idx) not in conjunto_bobinas_colocadas else 1

        circulo = patches.Circle((x_centro, y_centro), RAIO_BOBINA,
                                 facecolor=cor_face, edgecolor=cor_borda, linewidth=linha_borda)
        ax.add_patch(circulo)

        if (r_idx, l_idx, p_idx) in conjunto_bobinas_colocadas:
            texto_bobina = f"{r_idx}{l_idx}{p_idx}"
            ax.text(x_centro, y_centro, texto_bobina,
                    ha='center', va='center', fontsize=7, color='black', weight='bold')

        min_x_plot = min(min_x_plot, x_centro - RAIO_BOBINA)
        max_x_plot = max(max_x_plot, x_centro + RAIO_BOBINA)
        min_y_plot = min(min_y_plot, y_centro - RAIO_BOBINA)
        max_y_plot = max(max_y_plot, y_centro + RAIO_BOBINA)

    if not todas_posicoes_possiveis:
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
    else:
        padding = DIAMETRO_VISUAL
        ax.set_xlim(min_x_plot - padding, max_x_plot + padding)
        ax.set_ylim(min_y_plot - padding, max_y_plot + padding)

    ax.set_aspect('equal', adjustable='box')
    ax.set_title(
        f"Organização de {len(bobinas_colocadas)} Bobinas (de {num_total_bobinas_solicitadas} solicitadas) - Max 2 Camadas")
    ax.axis('off')

    plt.show()


# Exemplo de uso:
if __name__ == '__main__':
    print("--- Testes com Altura Máxima de 2 Camadas ---")

    # Cenário 1: Exemplo com 5 bobinas
    print("\nCenário 1: 5 Bobinas, 2 Fileiras, Base 3")
    num_bobinas_ex1 = 5
    num_fileiras_ex1 = 2
    max_base_ex1 = 3  # Capacidade por fileira: 3 (camada 1) + (3-1=2) (camada 2) = 5. Total: 2 * 5 = 10.
    arranjo_ex1, ocupacao_ex1 = distribuir_bobinas(num_bobinas_ex1, num_fileiras_ex1, max_base_ex1)
    print(f"Arranjo gerado: {arranjo_ex1}")
    print(f"Número de bobinas colocadas: {len(arranjo_ex1)}")
    print(f"Array de ocupação: {ocupacao_ex1}")
    plotar_organizacao(arranjo_ex1, num_bobinas_ex1, num_fileiras_ex1, max_base_ex1)
    print("-" * 30)

    # Cenário 2: Preenchendo uma fileira inteira com 2 camadas
    print("\nCenário 2: 5 Bobinas (Fileira Cheia), 1 Fileira, Base 3")
    num_bobinas_ex2 = 5  # 3 na base, 2 na camada 2
    num_fileiras_ex2 = 1
    max_base_ex2 = 3
    arranjo_ex2, ocupacao_ex2 = distribuir_bobinas(num_bobinas_ex2, num_fileiras_ex2, max_base_ex2)
    print(f"Arranjo gerado: {arranjo_ex2}")
    print(f"Número de bobinas colocadas: {len(arranjo_ex2)}")
    print(f"Array de ocupação: {ocupacao_ex2}")
    plotar_organizacao(arranjo_ex2, num_bobinas_ex2, num_fileiras_ex2, max_base_ex2)
    print("-" * 30)

    # Cenário 3: Seu caso de teste original adaptado para 2 camadas
    print("\nCenário 3: Seu Caso de Teste (92 bobinas, 3 fileiras, base 9) com 2 Camadas")
    num_bobinas_ex3 = 92
    num_fileiras_ex3 = 3
    max_base_ex3 = 9
    # Capacidade por fileira: 9 (camada 1) + (9-1=8) (camada 2) = 17.
    # Capacidade total: 3 fileiras * 17 bobinas/fileira = 51 bobinas.
    # As 92 bobinas solicitadas EXCEDEM a capacidade.
    arranjo_ex3, ocupacao_ex3 = distribuir_bobinas(num_bobinas_ex3, num_fileiras_ex3, max_base_ex3)
    print(f"Arranjo gerado: {arranjo_ex3}")
    print(f"Número de bobinas colocadas: {len(arranjo_ex3)}")
    print(f"Array de ocupação: {ocupacao_ex3}")
    plotar_organizacao(arranjo_ex3, num_bobinas_ex3, num_fileiras_ex3, max_base_ex3)
    print("-" * 30)

    # Cenário 4: Preenchendo a capacidade máxima com 2 camadas
    print("\nCenário 4: Preenchendo Capacidade Máxima (51 bobinas), 3 Fileiras, Base 9")
    num_bobinas_ex4 = 51
    num_fileiras_ex4 = 3
    max_base_ex4 = 9
    arranjo_ex4, ocupacao_ex4 = distribuir_bobinas(num_bobinas_ex4, num_fileiras_ex4, max_base_ex4)
    print(f"Arranjo gerado: {arranjo_ex4}")
    print(f"Número de bobinas colocadas: {len(arranjo_ex4)}")
    print(f"Array de ocupação: {ocupacao_ex4}")
    plotar_organizacao(arranjo_ex4, num_bobinas_ex4, num_fileiras_ex4, max_base_ex4)
    print("-" * 30)

    # Cenário 5: Zero bobinas
    print("\nCenário 5: Zero Bobinas")
    num_bobinas_ex5 = 10
    num_fileiras_ex5 = 2
    max_base_ex5 = 3
    arranjo_ex5, ocupacao_ex5 = distribuir_bobinas(num_bobinas_ex5, num_fileiras_ex5, max_base_ex5)
    print(f"Arranjo gerado: {arranjo_ex5}")
    print(f"Array de ocupação: {ocupacao_ex5}")
    plotar_organizacao(arranjo_ex5, num_bobinas_ex5, num_fileiras_ex5, max_base_ex5)
    print("-" * 30)

    # Cenário 6: Dimensões inválidas (fileiras=0)
    print("\nCenário 6: Dimensões Inválidas (fileiras=0)")
    num_bobinas_ex6 = 12
    num_fileiras_ex6 = 6
    max_base_ex6 = 2
    arranjo_ex6, ocupacao_ex6 = distribuir_bobinas(num_bobinas_ex6, num_fileiras_ex6, max_base_ex6)
    print(f"Arranjo gerado: {arranjo_ex6}")
    print(f"Array de ocupação: {ocupacao_ex6}")
    if arranjo_ex6 or num_bobinas_ex6 == 0:
        plotar_organizacao(arranjo_ex6, num_bobinas_ex6, num_fileiras_ex6, max_base_ex6)
    print("-" * 30)

    print("\nCenário 7: Dimensões Inválidas (max_base=0)")
    num_bobinas_ex7 = 5
    num_fileiras_ex7 = 2
    max_base_ex7 = 3
    arranjo_ex7, ocupacao_ex7 = distribuir_bobinas(num_bobinas_ex7, num_fileiras_ex7, max_base_ex7)
    print(f"Arranjo gerado: {arranjo_ex7}")
    print(f"Array de ocupação: {ocupacao_ex7}")
    if arranjo_ex7 or num_bobinas_ex7 == 0:
        plotar_organizacao(arranjo_ex7, num_bobinas_ex7, num_fileiras_ex7, max_base_ex7)
    print("-" * 30)
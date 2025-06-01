import json
import random
import argparse


def gerar_instancia(n_posicoes=5, n_bobinas=3, n_secoes=10, seed=42, arquivo_saida="instancia.json"):
    random.seed(seed)

    # Conjuntos de posições e seções
    psi = list(range(1, n_posicoes + 1))  # Posições disponíveis
    phi = [1, n_posicoes]  # Entrada (I=1) e Saída (O=n_posicoes)
    secoes = list(range(1, n_secoes + 1))  # Seções de tempo

    # Camadas (opcional, pode ser estendido depois)
    psi1 = psi[:len(psi) // 2]  # Metade para camada 1
    psi2 = psi[len(psi) // 2:]  # Metade para camada 2

    # Gerar bobinas
    bobinas = []
    for i in range(n_bobinas):
        entrada_inicio = random.randint(0, 10)
        entrada_fim = entrada_inicio + random.randint(1, 3)
        saida_inicio = entrada_fim + random.randint(3, 5)
        saida_fim = saida_inicio + random.randint(1, 3)
        bobinas.append({
            "id": f"a{i + 1}",
            "entrada": [entrada_inicio, entrada_fim],
            "saida": [saida_inicio, saida_fim]
        })

    # Gerar custos e tempos de movimentação
    E_load = {}
    E_empty = {}
    t_load = {}
    t_empty = {}

    for k in phi:
        for q in psi:
            key = f"{k}_{q}"
            E_load[key] = random.randint(5, 15)
            E_empty[key] = random.randint(2, 8)
            t_load[key] = random.randint(1, 3)
            t_empty[key] = random.randint(1, 2)

    # Construir dicionário completo
    instancia = {
        "Psi": psi,
        "Phi": phi,
        "Psi1": psi1,
        "Psi2": psi2,
        "S": secoes,
        "bobinas": bobinas,
        "E_load": E_load,
        "E_empty": E_empty,
        "t_load": t_load,
        "t_empty": t_empty
    }

    # Salvar em arquivo
    with open(arquivo_saida, "w") as f:
        json.dump(instancia, f, indent=4)

    print(f"Instância gerada com sucesso em '{arquivo_saida}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de instâncias para o problema de otimização de galpão.")
    parser.add_argument("--n_posicoes", type=int, default=5, help="Número de posições disponíveis (Ψ)")
    parser.add_argument("--n_bobinas", type=int, default=3, help="Número de bobinas")
    parser.add_argument("--n_secoes", type=int, default=10, help="Número de seções de tempo (S)")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória")
    parser.add_argument("--saida", type=str, default="instancia.json", help="Arquivo de saída")

    args = parser.parse_args()
    gerar_instancia(args.n_posicoes, args.n_bobinas, args.n_secoes, args.seed, args.saida)

import requests

menu_moedas = """
=== Opções de Moedas para Consulta ===

Tradicionais:
USD-BRL (Dólar Americano)
EUR-BRL (Euro)
GBP-BRL (Libra Esterlina)
ARS-BRL (Peso Argentino)

Criptomoedas:
BTC-BRL (Bitcoin)
ETH-BRL (Ethereum)
=====================================
"""

def consultar_moeda(moeda):
    url = f"https://economia.awesomeapi.com.br/json/last/{moeda}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        return resposta.json()
    else:
        # Se der erro (ex: 404), exibe a mensagem de erro e retorna None
        try:
            erro = resposta.json()
            print("\n--- DEU ERRO! ---")
            print(f"Status do erro: {erro.get('status')}")
            print(f"Código: {erro.get('code')}")
            print(f"Mensagem: {erro.get('message')}")
        except:
            print("\nErro inesperado ao consultar a API.")
        return None

# 1. Mostra o menu PRIMEIRO
print(menu_moedas)

# 2. Pede o input garantindo que fica em maiúsculas (upper) e sem espaços (strip)
moeda_desejada = input("Digite a moeda que deseja consultar (ex: USD-BRL): ").strip().upper()

dados_api = consultar_moeda(moeda_desejada)

# -----------------------------------tratamento do json-----------------------------------
if dados_api:
    chave = moeda_desejada.replace("-", "")
    
    # 3. Verifica se a chave realmente existe no dicionário retornado
    if chave in dados_api:
        valor = dados_api[chave]["bid"]
        print("\nRequisição bem-sucedida!")
        print(f"O valor atual de {moeda_desejada} é:")
        print(f"R$ {float(valor):.2f}")
    else:
        print("\nErro: Não foi possível extrair o valor (bid) da resposta.")
else:
    print(f"\nErro ao consultar moeda: {moeda_desejada}\nVerifique se o formato está correto.")
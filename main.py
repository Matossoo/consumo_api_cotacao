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
        print("Deu certo!")
        print(resposta.json())
        return resposta.json()
    elif resposta.status_code == 404:
        print("deu erro!")
        erro = resposta.json()
        status = erro["status"]
        codigo = erro["code"]
        mensagem = erro["message"]
        print(f"Status do erro: {status}")
        print(f"Código: {codigo}")
        print(f"Mensagem: {mensagem}")
        return resposta.json()


moeda_desejada = input("Digite a moeda que deseja consultar(ex: USD-BRL):")

dados_api = consultar_moeda(moeda_desejada)
#-----------------------------------tratamento do json-----------------------------------
if dados_api:
    chave = moeda_desejada.replace("-","")
    valor = dados_api[chave]["bid"]
    print("\nRequisição bem-sucedida")

    print(f"O valr atual de {moeda_desejada} é: ")
    print(f"R$ {float(valor):.2f}")
    
else:
    print(f"\nErro ao consultar moeda: {moeda_desejada} \nVerifique se o formato está correto")

print(menu_moedas)


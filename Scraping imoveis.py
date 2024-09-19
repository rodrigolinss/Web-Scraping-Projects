import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

header = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}

def extrair_dados(paginas):
    localizacao_lista = []
    valores = []
    metros_quadrados = []
    quartos_lista = []
    suite_lista = []
    vagas_lista = []
    desc_lista = []

    for pagina in range(1, paginas + 1):
        url = f"https://www.dfimoveis.com.br/venda/df/brasilia/park-sul/apartamento?pagina={pagina}"
        html = requests.get(url=url, headers=header)
        site = BeautifulSoup(html.text, "html.parser")


        for loc in site.find_all(class_ = "new-title phrase"):
            localizacao_lista.append(loc.text.strip())

        for div in site.find_all('div', class_='new-price'):
            for h4 in div.find_all('h4'):
                span = h4.find('span')
                if span:
                    valor = span.text.strip()  
                    valores.append(valor)
                    break  

        for m in site.find_all(class_ ="m-area"):
            metros_quadrados.append(m.text.strip())

        for li in site.find_all('li'):
            if 'Quarto' in li.text:
                quartos_lista.append(li.span.text.strip())

        for li in site.find_all('li'):
            if 'Suíte' in li.text:
                suite_lista.append(li.span.text.strip())

        for li in site.find_all('li'):
            if 'Vaga' in li.text:
                vagas_lista.append(li.span.text.strip())

        for desc in site.find_all(class_ = "new-simple phrase"):
            desc_lista.append(desc.text.strip())

    max_length = max(len(localizacao_lista), len(valores), len(metros_quadrados),
                     len(quartos_lista), len(suite_lista), len(vagas_lista), len(desc_lista))

    localizacao_lista += [None] * (max_length - len(localizacao_lista))
    valores += [None] * (max_length - len(valores))
    metros_quadrados += [None] * (max_length - len(metros_quadrados))
    quartos_lista += [None] * (max_length - len(quartos_lista))
    suite_lista += [None] * (max_length - len(suite_lista))
    vagas_lista += [None] * (max_length - len(vagas_lista))
    desc_lista += [None] * (max_length - len(desc_lista))


    df = pd.DataFrame({
        'Localização': localizacao_lista,
        'Valor': valores,
        'Metros Quadrados': metros_quadrados,
        'Quartos': quartos_lista,
        'Suítes': suite_lista,
        'Vagas': vagas_lista,
        'Descrição': desc_lista
    })

    return df


numero_de_paginas = 14
df_imoveis = extrair_dados(numero_de_paginas)


print(df_imoveis)

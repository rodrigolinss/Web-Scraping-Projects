# Importando bibliotecas necessárias
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL base do site Books to Scrape
url_base = 'http://books.toscrape.com/'

def extrair_livros(url_pagina, categoria):

    resposta = requests.get(url_pagina)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Encontrar todos os elementos de livro na página
    livros = soup.find_all('article', class_='product_pod')
    dados_livros = []

    for livro in livros:
        # Título do livro
        titulo = livro.find('h3').find('a')['title']

        # Preço do livro
        preco_elemento = livro.find('p', class_='price_color')
        preco = preco_elemento.text.strip() if preco_elemento else None
        if preco:
            preco = preco[1:]

        # Disponibilidade do livro
        disponibilidade = livro.find('p', class_='instock availability').text.strip()

        # Link para o livro
        link = livro.find('h3').find('a')['href']
        link = url_base + "catalogue/" + link

        # Avaliação do livro
        avaliacao_elemento = livro.find('p', class_='star-rating')
        if avaliacao_elemento:
            avaliacao_classes = avaliacao_elemento['class']
            avaliacao = [classe for classe in avaliacao_classes if classe != 'star-rating']
            avaliacao = avaliacao[0] if avaliacao else 'None'
        else:
            avaliacao = 'None'

        # Adiciona os dados do livro à lista
        dados_livros.append([titulo, preco, disponibilidade, link, categoria, avaliacao])

    return dados_livros


def coletar_todas_categorias():

    resposta = requests.get(url_base)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Encontrar todas as categorias no menu lateral
    categorias = soup.find('ul', class_='nav-list').find_all('li')[1:]
    categorias_urls = [(cat.find('a').text.strip(), url_base + cat.find('a')['href']) for cat in categorias]

    return categorias_urls


# Função para coletar livros de todas as categorias
def coletar_todos_livros():
    todos_livros = []
    categorias = coletar_todas_categorias()

    for nome_categoria, url_categoria in categorias:
        numero_pagina = 1

        # Iterar pelas páginas de cada categoria
        while True:
            url_pagina = url_categoria.replace('index.html', f'page-{numero_pagina}.html')
            livros = extrair_livros(url_pagina, nome_categoria)

            if not livros:
                break

            todos_livros.extend(livros)
            numero_pagina += 1

    return todos_livros


# Coletar dados de todos os livros no site
dados_livros = coletar_todos_livros()

# Criar um DataFrame com os dados coletados
df = pd.DataFrame(dados_livros, columns=['Título', 'Preço', 'Disponibilidade', 'Link', 'Categoria', 'Avaliação'])


print(df)

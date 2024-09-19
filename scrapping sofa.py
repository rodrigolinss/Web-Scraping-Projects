from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import pandas as pd
import re
import time
import random

# Configuração inicial do WebDriver para Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument('--ignore-certificate-errors')  # Ignorar erros de certificado SSL
# chrome_options.add_argument('--headless')  # Habilitar modo headless se necessário

service = Service(r'C:\Users\bogsk\Downloads\Web Scraping do Rodrigo meu filhao amado\chromedriver-win64\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Lista para armazenar os dados coletados
dados_jogos = []
urls_visitados = set()
contador_jogos = 0  # Contador de jogos coletados

# Variáveis para rolagem progressiva
rolagem_inicial = 100
incremento_rolagem = 50

# Função para rolar a página suavemente com maior probabilidade para baixo
def rolar_pagina_suave(quantidade):
    try:
        driver.execute_script(f"window.scrollBy(0, {quantidade});")
    except Exception as e:
        print(f'Erro ao rolar a página: {e}')

def gerar_urls_ultimos_10_dias():
    urls = []
    data_inicial = datetime.strptime('2024-07-13', '%Y-%m-%d')
    for i in range(10):
        data = data_inicial + timedelta(days=i)
        url = f'https://www.sofascore.com/football/{data.strftime("%Y-%m-%d")}'
        urls.append(url)
    return urls

# Função para manter o navegador ativo e simular atividade
def manter_navegador_ativo():
    try:
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f'Erro ao manter navegador ativo: {e}')

# Função para coletar dados de uma página específica de um jogo
def coletar_dados_jogo():
    global contador_jogos
    try:
        # Coletar o breadcrumb
        breadcrumb = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.BreadcrumbContent'))
        )
        items = breadcrumb.find_elements(By.CSS_SELECTOR, 'li[data-testid="breadcrumb"] a')

        if len(items) >= 3:
            regiao = items[1].text.strip()
            campeonato = items[2].text.strip()
        else:
            regiao = "Não disponível"
            campeonato = "Não disponível"

        print(f"Breadcrumbs encontrados: {[item.text for item in items]}")
        print(f"Região: {regiao}, Campeonato: {campeonato}")

        # Coletar nome do time da esquerda e o time da direita
        times = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'bdi.Text.joBMGr'))
        )

        if len(times) >= 2:
            time_esquerda = times[0].text.strip()
            time_direita = times[1].text.strip()
        else:
            raise Exception("Não foram encontrados times suficientes na página.")

        # Aguardar o elemento do placar da esquerda aparecer
        placar_esquerda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="left_score"]'))
        ).text.strip()

        # Aguardar o elemento do placar da direita aparecer
        placar_direita = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="right_score"]'))
        ).text.strip()

        # Coletar os tempos dos gols do time da esquerda
        gols_esquerda = driver.find_elements(By.CSS_SELECTOR, 'span.Text.dyJlxJ')
        lista_tempos_esquerda = []
        for gol in gols_esquerda:
            try:
                texto = gol.text.strip()
                tempos_gols = re.findall(r'\d{1,2}\'(?:[^\s]*)', texto)
                if tempos_gols:
                    lista_tempos_esquerda.extend(tempos_gols)
                else:
                    lista_tempos_esquerda.append(None)
            except Exception as e:
                print(f'Erro ao processar tempo do gol (Time Esquerda): {e}')
                lista_tempos_esquerda.append(None)

        # Coletar os tempos dos gols do time da direita
        gols_direita = driver.find_elements(By.CSS_SELECTOR, 'span.Text.cDXPee')
        lista_tempos_direita = []
        for gol in gols_direita:
            try:
                texto = gol.text.strip()
                tempos_gols = re.findall(r'\d{1,2}\'(?:[^\s]*)', texto)
                if tempos_gols:
                    lista_tempos_direita.extend(tempos_gols)
                else:
                    lista_tempos_direita.append(None)
            except Exception as e:
                print(f'Erro ao processar tempo do gol (Time Direita): {e}')
                lista_tempos_direita.append(None)

        # Coletar porcentagens de opinião
        opinioes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Text.bGtKrY span'))
        )

        if len(opinioes) >= 3:
            opiniao_esquerda = opinioes[0].text.strip()
            opiniao_empate = opinioes[1].text.strip()
            opiniao_direita = opinioes[2].text.strip()
        else:
            opiniao_esquerda = "Não disponível"
            opiniao_empate = "Não disponível"
            opiniao_direita = "Não disponível"

        yellow_cards_esquerda = None
        yellow_cards_direita = None

        # Navegar até a página de estatísticas
        try:
            aba_estatisticas = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'h2[data-tabid="statistics"] a'))
            )
            aba_estatisticas.click()

            time.sleep(0.500)  # Aguarde o carregamento da página de estatísticas

            # Coletar o bloco de estatísticas específico
            divs_estatisticas = driver.find_elements(By.CSS_SELECTOR, 'div.Box.Flex.heNsMA.bnpRyo')


            for div in divs_estatisticas:
                try:
                    titulo = div.find_element(By.CSS_SELECTOR, 'div.Box.gmloMx span.Text').text.strip()
                    if 'Yellow cards' in titulo:
                        valores = div.find_elements(By.CSS_SELECTOR, 'bdi.Box span.Text')
                        if len(valores) >= 3:
                            yellow_cards_esquerda = valores[0].text.strip()
                            yellow_cards_direita = valores[2].text.strip()
                        break
                except Exception as e:
                    print(f'Erro ao processar bloco de estatísticas: {e}')

            driver.back()
            time.sleep(0.500)  # Aguarde o carregamento da página do jogo

        except Exception as e:
            print(f'Erro ao acessar a página de estatísticas: {e}')

        print(f'Coletado: Região: {regiao}, Campeonato: {campeonato}')
        print(f'Coletado: Time Esquerda: {time_esquerda}, Placar Esquerda: {placar_esquerda}')
        print(f'Coletado: Time Direita: {time_direita}, Placar Direita: {placar_direita}')
        print(f'Tempos Gols Time Esquerda: {lista_tempos_esquerda}')
        print(f'Tempos Gols Time Direita: {lista_tempos_direita}')
        print(f'Opinião Esquerda: {opiniao_esquerda}')
        print(f'Opinião Empate: {opiniao_empate}')
        print(f'Opinião Direita: {opiniao_direita}')
        print(f'Cartões Amarelos - Esquerda: {yellow_cards_esquerda}')
        print(f'Cartões Amarelos - Direita: {yellow_cards_direita}')

        dados_jogos.append({
            'Região': regiao,
            'Campeonato': campeonato,
            'Time Esquerda': time_esquerda,
            'Placar Esquerda': placar_esquerda,
            'Time Direita': time_direita,
            'Placar Direita': placar_direita,
            'Tempos Gols Time Esquerda': lista_tempos_esquerda if lista_tempos_esquerda else None,
            'Tempos Gols Time Direita': lista_tempos_direita if lista_tempos_direita else None,
            'Opinião Esquerda': opiniao_esquerda,
            'Opinião Empate': opiniao_empate,
            'Opinião Direita': opiniao_direita,
            'Cartões Amarelos Esquerda': yellow_cards_esquerda,
            'Cartões Amarelos Direita': yellow_cards_direita
        })

        global contador_jogos
        contador_jogos += 1
        print(f'Número de jogos coletados: {contador_jogos}')

    except Exception as e:
        print(f'Erro ao coletar dados do jogo: {e}')

    finally:
        manter_navegador_ativo()  # Manter o navegador ativo após cada coleta de dados

# Função principal para navegação e coleta de dados
def navegar_e_coletar():
    global rolagem_inicial, incremento_rolagem
    
    try:
        # Gerar URLs para os 10 dias consecutivos
        urls = gerar_urls_ultimos_10_dias()
        
        for url in urls:
            driver.get(url)
            time.sleep(2)  # Aguarde o carregamento da página
            
            jogos_total = set()
            jogos_atualizados = True

            while jogos_atualizados:
                try:
                    jogos_na_pagina = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="event_cell"]')
                    jogos_atualizados = False

                    if not jogos_na_pagina:
                        print("Nenhum jogo encontrado na página.")
                        break

                    for jogo in jogos_na_pagina:
                        link = jogo.get_attribute('href')
                        if link not in urls_visitados:
                            urls_visitados.add(link)
                            jogos_total.add(link)
                            jogos_atualizados = True

                    if jogos_atualizados:
                        # Rolar a página para carregar mais jogos
                        rolar_pagina_suave(rolagem_inicial)
                        rolagem_inicial += incremento_rolagem  # Aumentar a quantidade de rolagem
                        time.sleep(3)  # Aguarde o carregamento dos novos jogos

                except Exception as e:
                    print(f'Erro ao coletar jogos: {e}')
                    break

            print(f'Total de jogos encontrados no dia {url.split("/")[-1]}: {len(jogos_total)}')

            # Processar cada jogo encontrado
            for link in jogos_total:
                try:
                    driver.get(link)
                    time.sleep(2)  # Aguarde o carregamento da página do jogo
                    coletar_dados_jogo()  # Função que coleta os dados do jogo
                    driver.back()
                    time.sleep(2)  # Aguarde o carregamento da página inicial

                except Exception as e:
                    print(f'Erro ao processar o jogo: {e}')
                    continue
            
            # Após processar todos os jogos para o dia atual, salvar os dados coletados em um arquivo Excel
            df = pd.DataFrame(dados_jogos)
            nome_arquivo = f'dados_jogos_{url.split("/")[-1]}.xlsx'
            df.to_excel(nome_arquivo, index=False, engine='openpyxl')
            print(f"Dados salvos em '{nome_arquivo}'")
            print(df.head())

            # Limpar a lista de dados para o próximo dia
            dados_jogos.clear()

    finally:
        driver.quit()

navegar_e_coletar()
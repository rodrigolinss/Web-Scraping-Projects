from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()  # ou o driver apropriado
driver.get('https://www.sofascore.com/football/match/cuiaba-atletico-mineiro/COscJu#id:12117195')

try:
    breadcrumb = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.BreadcrumbContent'))
    )
    items = breadcrumb.find_elements(By.CSS_SELECTOR, 'li[data-testid="breadcrumb"] a')

    if items:
        regiao = items[1].text.strip() if len(items) > 1 else "Não disponível"
        campeonato = items[2].text.strip() if len(items) > 2 else "Não disponível"
        print(f"Região: {regiao}, Campeonato: {campeonato}")
    else:
        print("Breadcrumbs não encontrados.")
finally:
  time.sleep(3)
  driver.quit()

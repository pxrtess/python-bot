from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pyautogui as pg
import pandas as pd
import time
import csv
import pyperclip
from tqdm import tqdm

# dir_arquivo = input('Digite o nome do arquivo que deseja consultar: ')
dir_arquivo = "pacientes_202402272148"
url = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
servico = Service(ChromeDriverManager().install())
tabela = pd.read_csv('./'+dir_arquivo+'.csv', sep=',', encoding='latin-1', index_col=False, dtype=str)
tabela.columns = [coluna.lower().replace(' ', '_').replace('.', '') for coluna in tabela.columns]

dados_consulta = tabela[['ds_cpf', 'dt_nascimentox']]
dados_consulta = dados_consulta[dados_consulta['ds_cpf'].notnull()]
dados_consulta['ds_cpf'] = dados_consulta['ds_cpf'].astype(str)
lista_navegador = []
total_linhas = len(dados_consulta)
progresso = tqdm(total=total_linhas, desc='Progresso')
for linha in dados_consulta.itertuples():
    progresso.update(1)
    if progresso.n < 1119:
        pass
    pyperclip.copy('')
    if len(linha.ds_cpf) == 11:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        navegador = webdriver.Chrome(service=servico, options=chrome_options)
        navegador.get(url)
        navegador.find_element(By.ID, 'id_clear').click()
        navegador.find_element(By.ID, 'txtCPF').click()
        navegador.find_element(By.ID, 'txtCPF').send_keys(linha.ds_cpf)
        navegador.find_element(By.ID, 'txtDataNascimento').send_keys(linha.dt_nascimentox)
        time.sleep(3) 
        pg.press('tab')
        time.sleep(1) 
        pg.press('enter')
        time.sleep(1) 
        pg.press('enter')
        time.sleep(3)
        navegador.find_element(By.ID, 'id_submit').click()
        time.sleep(2) 
        pg.hotkey('ctrl', 'a')
        pg.hotkey('ctrl', 'c')
        copied_text = pyperclip.paste()
        filtered_lines = []
        errors = []
        for line in copied_text.split('\n'):
            if 'No do CPF:' in line:
                filtered_lines.append(line)
            elif 'Nome:' in line:
                filtered_lines.append(line)
            elif 'Data de Nascimento:' in line:
                filtered_lines.append(line)
            elif 'Situação Cadastral:' in line:
                filtered_lines.append(line)
            elif 'Data da Inscrição:' in line:
                filtered_lines.append(line)
            elif 'Digito Verificador:' in line:
                filtered_lines.append(line)
            elif 'CPF incorreto' in line:
                errors.append("CPF incorreto")
            elif 'divergente da constante na base de dados' in line:
                errors.append("Data de Nascimento divergente")
        filtered_data = {}
        
        for line in filtered_lines:
            field_name, field_value = line.split(': ', 1)
            filtered_data[field_name] = field_value
        filtered_data = {key: value.replace('\r', '') for key, value in filtered_data.items()}
        if filtered_lines != []: 
            with open(dir_arquivo+'_resultados.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=filtered_data.keys())  
                writer.writerow(filtered_data)
        if errors != []: 
            errors_data = {'data_nascimento': linha.dt_nascimentox, 'cpf': linha.ds_cpf,'errors': errors}
            with open(dir_arquivo+'_erros.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=errors_data.keys())  
                writer.writerow(errors_data)
        if filtered_lines == [] and errors == []:
            errors.append("Erro desconhecido")
            errors_data = {'data_nascimento': linha.dt_nascimentox, 'cpf': linha.ds_cpf,'errors': errors}
            with open(dir_arquivo+'_erros.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=errors_data.keys())  
                writer.writerow(errors_data)
        time.sleep(2)
        navegador.quit()
        pass      
progresso.close()
print('Fim do processo')          

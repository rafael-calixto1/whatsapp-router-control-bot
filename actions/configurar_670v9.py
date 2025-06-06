from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configurações a partir de variáveis de ambiente
device_url = os.getenv('ROUTER_URL', 'http://192.168.1.1')
username = os.getenv('ROUTER_CONFIG_USERNAME', 'multipro')
password = os.getenv('ROUTER_CONFIG_PASSWORD', 'multipro')
config_file_path = os.getenv('CONFIG_FILE_PATH', '/home/rafael/Desktop/NOC/roteadores/ZTE-F670LV9.0/config.bin')
gecko_driver_path = os.getenv('GECKO_DRIVER_PATH', '/usr/bin/geckodriver')
headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

# Driver compartilhado entre as actions
driver_global = None

class ActionConfigurar670v9Inicio(Action):
    def name(self):
        return "action_configurar_670v9_inicio"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        options = Options()
        options.headless = headless
        service = Service(gecko_driver_path)
        driver_global = webdriver.Firefox(service=service, options=options)

        dispatcher.utter_message("🔄 Acessando o roteador...")
        driver_global.get(device_url)

        return [FollowupAction("action_configurar_670v9_login")]

class ActionConfigurar670v9Login(Action):
    def name(self):
        return "action_configurar_670v9_login"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🔐 Realizando login...")
        WebDriverWait(driver_global, 10).until(
            EC.presence_of_element_located((By.ID, "Frm_Username"))
        ).send_keys(username)
        driver_global.find_element(By.ID, "Frm_Password").send_keys(password)
        driver_global.find_element(By.ID, "LoginId").click()

        return [FollowupAction("action_configurar_670v9_sair_quick")]

class ActionConfigurar670v9SairQuick(Action):
    def name(self):
        return "action_configurar_670v9_sair_quick"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🚪 Saindo da configuração rápida...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Outquicksetup"))
        ).click()

        return [FollowupAction("action_configurar_670v9_navegar_menu")]

class ActionConfigurar670v9NavegarMenu(Action):
    def name(self):
        return "action_configurar_670v9_navegar_menu"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📂 Navegando para 'Gerência & Diagnóstico'...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "mgrAndDiag"))
        ).click()

        dispatcher.utter_message("⚙️ Navegando para 'Administração de Sistema'...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "devMgr"))
        ).click()

        dispatcher.utter_message("📑 Exibindo mais opções...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "scrollRightBtn"))
        ).click()

        return [FollowupAction("action_configurar_670v9_abrir_config")]

class ActionConfigurar670v9AbrirConfig(Action):
    def name(self):
        return "action_configurar_670v9_abrir_config"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🛠️ Abrindo 'Gerenciamento de configuração padrão'...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "ConfigMgr"))
        ).click()

        dispatcher.utter_message("🔽 Expandindo 'Restaurar configuração padrão'...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "DefConfUploadBar"))
        ).click()

        return [FollowupAction("action_configurar_670v9_upload_config")]

class ActionConfigurar670v9UploadConfig(Action):
    def name(self):
        return "action_configurar_670v9_upload_config"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📁 Selecionando o arquivo de configuração...")
        file_input = WebDriverWait(driver_global, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(config_file_path)

        dispatcher.utter_message("🔃 Clicando no botão de restauração...")
        upload_button = WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Btn_Upload"))
        )
        upload_button.click()

        return [FollowupAction("action_configurar_670v9_confirmar")]

class ActionConfigurar670v9Confirmar(Action):
    def name(self):
        return "action_configurar_670v9_confirmar"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("✅ Confirmando pop-up de restauração...")
        confirm_popup = WebDriverWait(driver_global, 10).until(
            EC.visibility_of_element_located((By.ID, "confirmLayer"))
        )
        confirm_ok_button = confirm_popup.find_element(By.ID, "confirmOK")
        confirm_ok_button.click()

        dispatcher.utter_message("🎉 Restauração de configuração realizada com sucesso!")

        return [FollowupAction("action_configurar_670v9_finalizar")]

class ActionConfigurar670v9Finalizar(Action):
    def name(self):
        return "action_configurar_670v9_finalizar"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🧹 Fechando o navegador...")
        driver_global.quit()

        dispatcher.utter_message("✅ Processo concluído com sucesso.")
        return [] 
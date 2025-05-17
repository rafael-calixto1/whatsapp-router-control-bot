from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

device_url = os.getenv('ROUTER_DIR615_URL', 'http://192.168.0.1/')
username = os.getenv('ROUTER_DIR615_USERNAME', 'Admin')
password = os.getenv('ROUTER_DIR615_PASSWORD', '210204')
config_file_path = os.getenv('CONFIG_DIR615_FILE_PATH', '/home/rafael/Desktop/NOC/roteadores/DIR615-T3/defaultconfig.img')
gecko_driver_path = os.getenv('GECKO_DRIVER_PATH', '/usr/bin/geckodriver')
headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

driver_global = None

class ActionRestaurarConfigDir615T3(Action):
    def name(self):
        return "action_resetar_dir_615_t3"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        dispatcher.utter_message("🚀 Iniciando processo de restauração do DIR-615 T3...")

        try:
            # Inicializa o navegador
            options = Options()
            options.headless = headless
            service = Service(gecko_driver_path)
            driver_global = webdriver.Firefox(service=service, options=options)

            dispatcher.utter_message("🌐 Acessando a interface do roteador...")
            driver_global.get(device_url)

            # Login
            username_field = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.click()
            username_field.clear()  # Clear the existing "User" value
            username_field.send_keys(username)

            driver_global.find_element(By.ID, "password").send_keys(password)
            driver_global.find_element(By.ID, "loginBtn").click()
            
            # Check for login error alert
            try:
                time.sleep(2)  # Wait for potential alert
                alert = WebDriverWait(driver_global, 5).until(EC.alert_is_present())
                alert_text = alert.text
                alert.accept()  # Accept the alert
                dispatcher.utter_message(f"❌ Erro de login: {alert_text}")
                dispatcher.utter_message("⚠️ Verifique as credenciais de acesso no arquivo .env")
                return []
            except:
                # No alert means login was successful
                dispatcher.utter_message("🔐 Login realizado com sucesso...")
            
            time.sleep(2)
            dispatcher.utter_message("⏳ Aguardando carregamento da interface...")

            # Switch to frame 1
            dispatcher.utter_message("🔄 Mudando para o frame correto...")
            driver_global.switch_to.frame(1)

            # Navigate to Maintenance
            dispatcher.utter_message("🔧 Acessando menu 'Maintenance'...")
            maintenance_link = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Maintenance"))
            )
            maintenance_link.click()
            dispatcher.utter_message("✅ Menu 'Maintenance' acessado")

            # Navigate to Backup/Restore
            dispatcher.utter_message("📁 Acessando 'Backup/Restore'...")
            backup_restore_link = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Backup/Restore"))
            )
            backup_restore_link.click()
            dispatcher.utter_message("✅ Menu 'Backup/Restore' acessado")

            # Upload configuration file
            dispatcher.utter_message("📁 Selecionando arquivo de configuração...")
            file_input = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.NAME, "download image file"))
            )
            file_input.send_keys(config_file_path)
            dispatcher.utter_message("✅ Arquivo selecionado")

            # Submit/Send
            dispatcher.utter_message("📤 Realizando upload da configuração...")
            send_button = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.NAME, "send"))
            )
            send_button.click()
            
            # Handle alert confirmation
            dispatcher.utter_message("⏳ Aguardando confirmação...")
            time.sleep(1)
            
            # Accept the alert
            dispatcher.utter_message("✅ Confirmando restauração...")
            alert = WebDriverWait(driver_global, 10).until(EC.alert_is_present())
            alert_text = alert.text
            dispatcher.utter_message(f"📋 Confirmação: {alert_text}")
            alert.accept()
            
            time.sleep(5)
            dispatcher.utter_message("⏳ Aguardando restauração finalizar...")

            dispatcher.utter_message("🎉 Restauração concluída com sucesso!")

        except Exception as e:
            dispatcher.utter_message(f"❌ Erro no processo: {str(e)}")
        finally:
            if driver_global:
                driver_global.quit()

        return []
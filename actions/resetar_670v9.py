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

device_url = os.getenv('ROUTER_URL', 'http://192.168.1.1')
username = os.getenv('ROUTER_USERNAME', 'admin')
password = os.getenv('ROUTER_PASSWORD', '210204')
config_file_path = os.getenv('CONFIG_FILE_PATH', '/home/rafael/Desktop/NOC/roteadores/ZTE-F670LV9.0/config.bin')
gecko_driver_path = os.getenv('GECKO_DRIVER_PATH', '/usr/bin/geckodriver')
headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

driver_global = None

class ActionResetar670v9Inicio(Action):
    def name(self):
        return "action_resetar_670v9_inicio"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        options = Options()
        options.headless = headless
        service = Service(gecko_driver_path)
        driver_global = webdriver.Firefox(service=service, options=options)

        dispatcher.utter_message("🔄 Acessando o roteador...")
        driver_global.get(device_url)

        return [FollowupAction("action_resetar_670v9_login")]


class ActionResetar670v9Login(Action):
    def name(self):
        return "action_resetar_670v9_login"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🔐 Realizando login...")

        WebDriverWait(driver_global, 10).until(
            EC.presence_of_element_located((By.ID, "Frm_Username"))
        ).send_keys(username)

        driver_global.find_element(By.ID, "Frm_Password").send_keys(password)
        driver_global.find_element(By.ID, "LoginId").click()

        # Executa leitura óptica após login
        return [FollowupAction("action_ler_sinal_optico")]


class ActionLerSinalOptico(Action):
    def name(self):
        return "action_ler_sinal_optico"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📡 Lendo níveis ópticos...")

        try:
            WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.ID, "internet"))
            ).click()

            WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "RxPower"))
            )

            rx_element = driver_global.find_element(By.ID, "RxPower")
            tx_element = driver_global.find_element(By.ID, "TxPower")

            rx_title = rx_element.get_attribute("title")
            tx_title = tx_element.get_attribute("title")

            if rx_title == "-40" or rx_element.text.strip() == "--":
                dispatcher.utter_message("📉 Sinal óptico: LOS (Loss of Signal).")
            else:
                try:
                    rx_power = float(rx_title)
                    tx_power = float(tx_title)
                    tx_signal = rx_power - tx_power

                    dispatcher.utter_message(f"🔍 RxPower: {rx_power} dBm")
                    dispatcher.utter_message(f"🔍 TxPower: {tx_signal:.4f} dBm")
                except (TypeError, ValueError):
                    dispatcher.utter_message("⚠️ Não foi possível converter os valores Rx/Tx.")

        except Exception as e:
            dispatcher.utter_message(f"❌ Erro ao ler os níveis ópticos: {str(e)}")
            if driver_global:
                driver_global.quit()

        return [FollowupAction("action_resetar_670v9_navegar_menu")]


class ActionResetar670v9NavegarMenu(Action):
    def name(self):
        return "action_resetar_670v9_navegar_menu"

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

        return [FollowupAction("action_resetar_670v9_abrir_config")]


class ActionResetar670v9AbrirConfig(Action):
    def name(self):
        return "action_resetar_670v9_abrir_config"

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

        return [FollowupAction("action_resetar_670v9_upload_config")]


class ActionResetar670v9UploadConfig(Action):
    def name(self):
        return "action_resetar_670v9_upload_config"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📁 Selecionando o arquivo de configuração...")
        try:
            file_input = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(config_file_path)

            dispatcher.utter_message("🔃 Clicando no botão de restauração...")
            upload_button = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.ID, "Btn_Upload"))
            )
            upload_button.click()
        except Exception as e:
            dispatcher.utter_message(f"❌ Erro ao fazer upload da configuração: {str(e)}")
            if driver_global:
                driver_global.quit()
            return []

        return [FollowupAction("action_resetar_670v9_confirmar")]


class ActionResetar670v9Confirmar(Action):
    def name(self):
        return "action_resetar_670v9_confirmar"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("✅ Confirmando pop-up de restauração...")
        try:
            confirm_popup = WebDriverWait(driver_global, 10).until(
                EC.visibility_of_element_located((By.ID, "confirmLayer"))
            )
            confirm_ok_button = confirm_popup.find_element(By.ID, "confirmOK")
            confirm_ok_button.click()

            dispatcher.utter_message("🎉 Restauração de configuração realizada com sucesso!")

        except Exception as e:
            dispatcher.utter_message(f"❌ Erro ao confirmar: {str(e)}")
            if driver_global:
                driver_global.quit()
            return []

        return [FollowupAction("action_resetar_670v9_finalizar")]


class ActionResetar670v9Finalizar(Action):
    def name(self):
        return "action_resetar_670v9_finalizar"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🧹 Fechando o navegador...")
        if driver_global:
            driver_global.quit()

        dispatcher.utter_message("✅ Processo concluído com sucesso.")
        return []

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
import time

# Load environment variables
load_dotenv()

device_url = os.getenv('ROUTER_URL', 'http://192.168.1.1')
username = os.getenv('ROUTER_USERNAME', 'admin')
password = os.getenv('ROUTER_PASSWORD', '210204')
gecko_driver_path = os.getenv('GECKO_DRIVER_PATH', '/usr/bin/geckodriver')
headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

driver_global = None

class ActionRemoverSenha670v1Inicio(Action):
    def name(self):
        return "action_remover_senha_670v1_inicio"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        options = Options()
        options.headless = headless
        service = Service(gecko_driver_path)
        driver_global = webdriver.Firefox(service=service, options=options)

        dispatcher.utter_message("🔄 Acessando o roteador...")
        driver_global.get(device_url)

        return [FollowupAction("action_remover_senha_670v1_login")]

class ActionRemoverSenha670v1Login(Action):
    def name(self):
        return "action_remover_senha_670v1_login"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🔐 Realizando login...")
        WebDriverWait(driver_global, 10).until(
            EC.presence_of_element_located((By.ID, "Frm_Username"))
        ).send_keys(username)

        driver_global.find_element(By.ID, "Frm_Password").send_keys(password)
        driver_global.find_element(By.ID, "LoginId").click()
        dispatcher.utter_message("✅ Login realizado com sucesso!")

        return [FollowupAction("action_remover_senha_670v1_navegar_menu")]

class ActionRemoverSenha670v1NavegarMenu(Action):
    def name(self):
        return "action_remover_senha_670v1_navegar_menu"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        
        #correct frame
        driver_global.switch_to.frame(1)

        dispatcher.utter_message("📡 Acessando menu de rede...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "mmNet"))
        ).click()

        return [FollowupAction("action_remover_senha_670v1_configurar_wifi1")]

class ActionRemoverSenha670v1ConfigurarWifi1(Action):
    def name(self):
        return "action_remover_senha_670v1_configurar_wifi1"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📶 Configurando WiFi 2.4GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "smWLANONE"))
        ).click()

        dispatcher.utter_message("🔒 Acessando configurações de segurança do WiFi 2.4GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "ssmWLANSec1"))
        ).click()

        dispatcher.utter_message("🔓 Alterando autenticação para Open System...")
        auth_dropdown = WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Frm_Authentication"))
        )
        auth_dropdown.click()
        auth_dropdown.find_element(By.XPATH, "//option[. = 'Open System']").click()

        dispatcher.utter_message("💾 Salvando configurações do WiFi 2.4GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Btn_Submit"))
        ).click()

        return [FollowupAction("action_remover_senha_670v1_configurar_wifi2")]

class ActionRemoverSenha670v1ConfigurarWifi2(Action):
    def name(self):
        return "action_remover_senha_670v1_configurar_wifi2"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("📶 Configurando WiFi 5GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "smWLANTWO"))
        ).click()

        dispatcher.utter_message("🔒 Acessando configurações de segurança do WiFi 5GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "ssmWLANSec2"))
        ).click()

        dispatcher.utter_message("🔓 Alterando autenticação para Open System...")
        auth_dropdown = WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Frm_Authentication"))
        )
        auth_dropdown.click()
        auth_dropdown.find_element(By.XPATH, "//option[. = 'Open System']").click()

        dispatcher.utter_message("💾 Salvando configurações do WiFi 5GHz...")
        WebDriverWait(driver_global, 10).until(
            EC.element_to_be_clickable((By.ID, "Btn_Submit"))
        ).click()

        return [FollowupAction("action_remover_senha_670v1_finalizar")]

class ActionRemoverSenha670v1Finalizar(Action):
    def name(self):
        return "action_remover_senha_670v1_finalizar"

    def run(self, dispatcher, tracker, domain):
        global driver_global

        dispatcher.utter_message("🧹 Fechando o navegador...")
        if driver_global:
            driver_global.quit()

        dispatcher.utter_message("✅ Senhas removidas com sucesso! Ambos os WiFis (2.4GHz e 5GHz) estão configurados como Open System.")
        return [] 
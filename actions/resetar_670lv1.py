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

device_url = os.getenv('ROUTER_URL', 'http://192.168.1.1')
username = os.getenv('ROUTER_USERNAME', 'admin')
password = os.getenv('ROUTER_PASSWORD', '210204')
config_file_path = os.getenv('CONFIG_V1_FILE_PATH', '/home/rafael/Desktop/NOC/roteadores/ZTE-F670LV1.1.01/config.bin')
gecko_driver_path = os.getenv('GECKO_DRIVER_PATH', '/usr/bin/geckodriver')
headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

driver_global = None

class ActionRestaurarConfig670LV1(Action):
    def name(self):
        return "action_restaurar_config_670lv1"

    def run(self, dispatcher, tracker, domain):
        global driver_global
        dispatcher.utter_message("🚀 Iniciando processo de restauração da ZTE F670LV1...")

        try:
            # Inicializa o navegador
            options = Options()
            options.headless = headless
            service = Service(gecko_driver_path)
            driver_global = webdriver.Firefox(service=service, options=options)

            dispatcher.utter_message("🌐 Acessando a interface do roteador...")
            driver_global.get(device_url)

            # Login
            WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "Frm_Username"))
            ).send_keys(username)

            driver_global.find_element(By.ID, "Frm_Password").send_keys(password)
            driver_global.find_element(By.ID, "LoginId").click()
            dispatcher.utter_message("🔐 Login realizado com sucesso...")
            
            time.sleep(2)
            
            # Switch to frame 1
            driver_global.switch_to.frame(1)

            # LEITURA DO PON SERIAL NUMBER
            try:
                pon_serial_element = WebDriverWait(driver_global, 10).until(
                    EC.presence_of_element_located((By.ID, "Frm_PonSerialNumber"))
                )
                pon_serial = pon_serial_element.text
                dispatcher.utter_message(f"🔢 PON Serial Number: {pon_serial}")
            except Exception as e:
                dispatcher.utter_message(f"⚠️ Não foi possível ler o PON Serial Number: {str(e)}")

            # LEITURA DO SINAL ÓPTICO
            # Click on Network Interface
            dispatcher.utter_message("📡 Acessando informações do sinal óptico...")
            interface_menu = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tr[@class='h2_content' and contains(@onclick, 'smWanStatu')]"))
            )
            driver_global.execute_script("arguments[0].click();", interface_menu)

            # Click on PON Information
            pon_info_menu = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tr[@class='h3' and contains(@onclick, 'pon_status_link_info_t')]"))
            )
            driver_global.execute_script("arguments[0].click();", pon_info_menu)

            # Wait for the page to load and read signal values
            time.sleep(2)
            
            # Read RxPower
            rx_power_element = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "Fnt_RxPower"))
            )
            rx_power = rx_power_element.text
            
            # Read TxPower
            tx_power_element = driver_global.find_element(By.ID, "Fnt_TxPower")
            tx_power = tx_power_element.text
            
            # Check for LOS (Loss of Signal)
            if rx_power == "--":
                dispatcher.utter_message("📉 Sinal óptico: LOS (Loss of Signal)\n⚠️ Verificar fibra, conector e acoplador.")
            else:
                # Calculate RX - TX
                try:
                    rx_value = float(rx_power)
                    tx_value = float(tx_power)
                    true_tx_value = rx_value - tx_value
                    dispatcher.utter_message(f"📊 Sinal óptico - RX: {rx_power} dBm | TX: {true_tx_value} dBm")
                except ValueError:
                    # If conversion fails, just show the original values
                    dispatcher.utter_message(f"📊 Sinal óptico - RX: {rx_power} dBm | TX: {tx_power} dBm")

            # CONTINUAÇÃO DO PROCESSO DE RESTAURAÇÃO
            # Expand Administration menu
            admin_font = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "Fnt_mmManager"))
            )
            driver_global.execute_script("arguments[0].click();", admin_font)
            dispatcher.utter_message("✅ Menu 'Administração' expandido")

            # Click System Management
            dispatcher.utter_message("🧭 Clicando em 'Administração de sistema'...")
            sys_mgr_font = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "smSysMgr"))
            )
            driver_global.execute_script("arguments[0].click();", sys_mgr_font)

            # Click Default Configuration Management
            dispatcher.utter_message("🧾 Clicando em 'Gerenciamento de configuração padrão'...")
            def_cfg_font = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "ssmDefCfgMgr"))
            )
            driver_global.execute_script("arguments[0].click();", def_cfg_font)
            dispatcher.utter_message("✅ Gerenciamento de configuração padrão clicado")

            # Upload file
            dispatcher.utter_message("📁 Selecionando arquivo de configuração...")
            file_input = WebDriverWait(driver_global, 10).until(
                EC.presence_of_element_located((By.ID, "DefCfgUpload"))
            )
            file_input.send_keys(config_file_path)

            # Upload
            dispatcher.utter_message("📤 Realizando upload da configuração...")
            upload_button = WebDriverWait(driver_global, 10).until(
                EC.element_to_be_clickable((By.ID, "upload"))
            )
            upload_button.click()
            
            time.sleep(3)
            dispatcher.utter_message("⏳ Aguardando processamento do upload...")

            # Confirm
            dispatcher.utter_message("✅ Confirmando restauração...")
            confirm_button = WebDriverWait(driver_global, 15).until(
                EC.element_to_be_clickable((By.ID, "msgconfirmb"))
            )
            confirm_button.click()
            
            time.sleep(5)
            dispatcher.utter_message("⏳ Aguardando restauração finalizar...")

            dispatcher.utter_message("🎉 Restauração concluída com sucesso!")

        except Exception as e:
            dispatcher.utter_message(f"❌ Erro no processo: {str(e)}")
        finally:
            if driver_global:
                driver_global.quit()

        return []

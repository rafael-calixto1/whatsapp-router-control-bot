from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ActionResetar670V9Script(Action):
    def name(self):
        return "action_resetar_670v9_script"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="🔄 Executando o reset do 670V9...")

        try:
            result = subprocess.run(
                [
                    "/bin/bash",
                    "-c",
                    "source /home/rafael/Desktop/bot/selenium-env/bin/activate && python /home/rafael/Desktop/bot/selenium-env/670V9_reset.python"
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                executable="/bin/bash"
            )
            dispatcher.utter_message(text=f"✅ Reset concluído com sucesso!\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"❌ Falha ao executar o reset:\n{e.stderr}")

        return []

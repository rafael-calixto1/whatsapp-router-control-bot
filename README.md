# RouterControl Bot

A WhatsApp bot built with Venom-bot and Rasa to control and configure ZTE-F670LV9.0 routers.

## Features

- Reset ZTE-F670LV9.0 routers with a simple WhatsApp command (`reset v9`)
- Configure ZTE-F670LV9.0 routers through WhatsApp
- Natural language understanding powered by Rasa
- Automated browser interaction using Selenium

## Prerequisites

- Node.js (v14+)
- Python 3.8+
- Firefox
- GeckoDriver
- Redis (optional for tracker store)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/conexao-bot.git
   cd conexao-bot/whatsapp2
   ```

2. Install Rasa dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install WhatsApp bot dependencies:
   ```bash
   cd venom-rasa-bridge
   npm install
   cd ..
   ```

4. Create a `.env` file in the root directory with your configuration:
   ```
   # Copy the sample .env file
   cp .env.example .env
   
   # Edit the .env file with your settings
   nano .env
   ```

## Setup

1. Train the Rasa model:
   ```bash
   rasa train
   ```

2. Start the Rasa action server:
   ```bash
   rasa run actions
   ```

3. Start the Rasa server:
   ```bash
   rasa run --enable-api --cors "*"
   ```

4. In a separate terminal, start the WhatsApp bot:
   ```bash
   cd venom-rasa-bridge
   node index.js
   ```

## Usage

Once the bot is running, you can send the following commands on WhatsApp:

- `reset v9` - Reset a ZTE-F670LV9.0 router
- `config v9` - Configure a ZTE-F670LV9.0 router

## Project Structure

- `/actions` - Custom Rasa actions for controlling routers
- `/data` - Training data for Rasa NLU
- `/models` - Trained Rasa models
- `/venom-rasa-bridge` - WhatsApp bot implementation using Venom-bot

## Modifying the Bot

1. To add new functionality, update the intent examples in `data/nlu.yml`
2. Add new rules in `data/rules.yml`
3. Create new custom actions in the `actions` directory
4. Register new actions in `domain.yml`
5. Train the model again using `rasa train`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
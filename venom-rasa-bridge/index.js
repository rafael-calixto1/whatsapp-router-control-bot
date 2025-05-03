const venom = require('venom-bot');
const axios = require('axios');
require('dotenv').config({ path: '../.env' });

// Get environment variables
const WHATSAPP_SESSION_NAME = process.env.WHATSAPP_SESSION_NAME || 'whatsapp-session';
const WHATSAPP_HEADLESS = process.env.WHATSAPP_HEADLESS === 'true';
const RASA_API_URL = process.env.RASA_API_URL || 'http://localhost:5005';
const RASA_WEBHOOK_ENDPOINT = process.env.RASA_WEBHOOK_ENDPOINT || '/webhooks/rest/webhook';

venom
  .create({
    session: WHATSAPP_SESSION_NAME,
    headless: WHATSAPP_HEADLESS,
    browserArgs: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--headless=new', // ✅ Required for compatibility with Chromium 120+
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
    ],
    useChrome: false, // Uses Puppeteer's Chromium instead of system Chrome
  })
  .then((client) => start(client))
  .catch((error) => {
    console.error('❌ Venom bot failed to initialize:', error);
  });

function start(client) {
  console.log('✅ Venom bot is running...');
  client.onMessage(async (message) => {
    if (!message.isGroupMsg && message.body) {
      console.log(`📩 Received from ${message.from}: ${message.body}`);

      try {
        // Send message to Rasa backend
        const response = await axios.post(`${RASA_API_URL}${RASA_WEBHOOK_ENDPOINT}`, {
          sender: message.from,
          message: message.body,
        });

        // Respond with Rasa messages
        for (const msg of response.data) {
          if (msg.text) {
            await client.sendText(message.from, msg.text);
            console.log(`📤 Sent to ${message.from}: ${msg.text}`);
          }
        }
      } catch (error) {
        console.error('❌ Error communicating with Rasa:', error.message);
      }
    }
  });
}

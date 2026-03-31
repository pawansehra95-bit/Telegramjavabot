import os
import threading
import telebot
from flask import Flask
from openai import OpenAI

# --- 1. Fetch Environment Variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not BOT_TOKEN or not HF_TOKEN:
    raise ValueError("BOT_TOKEN and HF_TOKEN must be set in environment variables.")

# --- 2. Initialize Telegram Bot and Flask App ---
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- 3. Initialize OpenAI Client (Using HuggingFace Router) ---
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# --- 4. Telegram Bot Logic ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am an AI chatbot powered by DeepSeek. Ask me anything!")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    # Shows a "typing..." status in Telegram while the AI generates the response
    bot.send_chat_action(message.chat.id, 'typing') 
    
    try:
        # Translated from your JavaScript API snippet
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2:novita",
            messages=[
                {
                    "role": "user",
                    "content": message.text, # Takes the user's message dynamically
                },
            ],
        )
        
        # Extract the AI's response and send it back to the user
        reply_text = response.choices[0].message.content
        bot.reply_to(message, reply_text)
        
    except Exception as e:
        bot.reply_to(message, f"Sorry, I encountered an error: {str(e)}")

# --- 5. Flask Web Server Logic (Required for Render.com) ---
@app.route('/')
def home():
    return "Telegram Bot is running smoothly!"

def run_flask():
    # Render automatically assigns a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- 6. Start Both Web Server and Bot ---
if __name__ == "__main__":
    # Start the Flask web server in a background thread so Render doesn't crash
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Start the Telegram bot polling in the main thread
    print("Bot is starting...")
    bot.infinity_polling()

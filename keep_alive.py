from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot çalışıyor! 🤖"

@app.route('/status')
def status():
    return {
        "status": "online",
        "message": "Discord Bot aktif",
        "timestamp": time.time()
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "uptime": time.time()
    }

def run():
    app.run(host='0.0.0.0', port=5000, debug=False)

def keep_alive():
    """Flask sunucusunu ayrı thread'de çalıştırır"""
    server_thread = threading.Thread(target=run)
    server_thread.daemon = True
    server_thread.start()
    print("Keep-alive sunucusu başlatıldı: http://0.0.0.0:5000")

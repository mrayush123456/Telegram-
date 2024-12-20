from flask import Flask, request, render_template_string, redirect, url_for
from telethon import TelegramClient, errors, sync
import threading
import time

app = Flask(__name__)

# Telegram credentials
api_id = None
api_hash = None
client = None
stop_flag = False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Telegram Bot</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: rgb(34, 193, 195);
      background: linear-gradient(135deg, rgba(34, 193, 195, 1) 0%, rgba(253, 187, 45, 1) 100%);
      color: white;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    .container {
      background: rgba(0, 0, 0, 0.5);
      padding: 20px;
      border-radius: 10px;
      width: 100%;
      max-width: 600px;
    }
    .btn-stop {
      background-color: #ff4444;
      border: none;
    }
  </style>
</head>
<body>
  <div class="container text-center">
    <h1 class="mb-4">Telegram Messaging Bot</h1>
    {% if not client %}
      <form method="POST" action="/login">
        <div class="mb-3">
          <label for="api_id" class="form-label">API ID:</label>
          <input type="text" class="form-control" id="api_id" name="api_id" required>
        </div>
        <div class="mb-3">
          <label for="api_hash" class="form-label">API Hash:</label>
          <input type="text" class="form-control" id="api_hash" name="api_hash" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
    {% else %}
      <form method="POST" action="/send_messages" enctype="multipart/form-data">
        <div class="mb-3">
          <label for="target" class="form-label">Target Username/Group Chat:</label>
          <input type="text" class="form-control" id="target" name="target" required>
        </div>
        <div class="mb-3">
          <label for="hatersname" class="form-label">Haters Name:</label>
          <input type="text" class="form-control" id="hatersname" name="hatersname">
        </div>
        <div class="mb-3">
          <label for="txt_file" class="form-label">Upload Message File (.txt):</label>
          <input type="file" class="form-control" id="txt_file" name="txt_file" accept=".txt" required>
        </div>
        <div class="mb-3">
          <label for="delay" class="form-label">Delay (in seconds):</label>
          <input type="number" class="form-control" id="delay" name="delay" required>
        </div>
        <button type="submit" class="btn btn-success w-100 mb-2">Send Messages</button>
      </form>
      <form method="POST" action="/stop">
        <button type="submit" class="btn btn-stop w-100">Stop Sending</button>
      </form>
    {% endif %}
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, client=client)

@app.route('/login', methods=['POST'])
def login():
    global api_id, api_hash, client
    api_id = request.form.get('api_id')
    api_hash = request.form.get('api_hash')

    try:
        client = TelegramClient('telegram_session', api_id, api_hash)
        client.start()
        return redirect(url_for('index'))
    except errors.TelegramError as e:
        return f"<p>Error logging in: {e}</p>"

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global stop_flag

    if not client:
        return redirect(url_for('index'))

    target = request.form.get('target')
    hatersname = request.form.get('hatersname', '')
    delay = int(request.form.get('delay'))
    txt_file = request.files['txt_file']

    try:
        messages = txt_file.read().decode('utf-8').splitlines()
    except Exception as e:
        return f"<p>Error reading file: {e}</p>"

    stop_flag = False

    def message_sender():
        global stop_flag
        try:
            for message in messages:
                if stop_flag:
                    break
                full_message = f"{hatersname}: {message}" if hatersname else message
                client.send_message(target, full_message)
                print(f"Sent: {full_message}")
                time.sleep(delay)
        except Exception as e:
            print(f"Error while sending messages: {e}")

    threading.Thread(target=message_sender).start()

    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    global stop_flag
    stop_flag = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  

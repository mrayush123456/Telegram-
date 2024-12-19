from flask import Flask, request, render_template_string
from telethon import TelegramClient
import asyncio
import os
import time

# Flask App
app = Flask(__name__)

# Telegram API credentials (replace with your API ID and Hash)
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Telegram Bot</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #282c34;
      color: #ffffff;
      font-family: Arial, sans-serif;
      background-image: radial-gradient(circle, #ff7eb3, #ff758c, #ff7977, #ff845e, #ff9947);
      height: 100vh;
    }
    .container {
      max-width: 600px;
      margin: auto;
      padding: 20px;
      background-color: rgba(0, 0, 0, 0.7);
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    .btn-submit {
      width: 100%;
    }
    h1 {
      text-align: center;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Telegram Bot</h1>
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="phone" class="form-label">Enter Mobile Number:</label>
        <input type="text" class="form-control" id="phone" name="phone" placeholder="+1234567890" required>
      </div>
      <div class="mb-3">
        <label for="otp" class="form-label">Enter OTP Code:</label>
        <input type="text" class="form-control" id="otp" name="otp" placeholder="12345">
      </div>
      <div class="mb-3">
        <label for="username" class="form-label">Target Username/Group:</label>
        <input type="text" class="form-control" id="username" name="username" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Upload Message File (.txt):</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3">
        <label for="delay" class="form-label">Delay Between Messages (seconds):</label>
        <input type="number" class="form-control" id="delay" name="delay" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Submit</button>
    </form>
  </div>
</body>
</html>
'''

# Global Telegram client variable
client = None

@app.route("/", methods=["GET", "POST"])
def telegram_bot():
    global client

    if request.method == "POST":
        # Get form data
        phone = request.form.get("phone")
        otp = request.form.get("otp")
        username = request.form.get("username")
        delay = int(request.form.get("delay"))
        txt_file = request.files["txtFile"]

        # Read messages from the uploaded file
        try:
            messages = txt_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"

        # Step 1: Initialize Telegram client if not already logged in
        if not client:
            client = TelegramClient("session_name", API_ID, API_HASH)

        async def run_bot():
            # Connect to Telegram
            await client.connect()

            # Login or enter OTP
            if not await client.is_user_authorized():
                try:
                    if otp:
                        await client.sign_in(phone, code=otp)
                    else:
                        await client.send_code_request(phone)
                        return "<p>OTP sent. Please enter it in the OTP field and resubmit.</p>"
                except Exception as e:
                    return f"<p>Error during login: {e}</p>"

            # Send messages to the target
            try:
                for message in messages:
                    await client.send_message(username, message)
                    time.sleep(delay)  # Delay between messages
            except Exception as e:
                return f"<p>Error sending message: {e}</p>"

            return "<p>Messages sent successfully!</p>"

        # Run the Telegram bot
        asyncio.run(run_bot())

    return render_template_string(HTML_TEMPLATE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
  

from flask import Flask, request, render_template_string
from telethon import TelegramClient, errors
import time

# Flask app
app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Telegram Bot</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <div class="container mt-5">
    <h1 class="text-center">Telegram Messaging Bot</h1>
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="apiId" class="form-label">Telegram API ID:</label>
        <input type="text" class="form-control" id="apiId" name="apiId" required>
      </div>
      <div class="mb-3">
        <label for="apiHash" class="form-label">Telegram API Hash:</label>
        <input type="text" class="form-control" id="apiHash" name="apiHash" required>
      </div>
      <div class="mb-3">
        <label for="phoneNumber" class="form-label">Telegram Phone Number:</label>
        <input type="text" class="form-control" id="phoneNumber" name="phoneNumber" required>
      </div>
      <div class="mb-3">
        <label for="targetUsername" class="form-label">Target Username:</label>
        <input type="text" class="form-control" id="targetUsername" name="targetUsername" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Upload Message File (.txt):</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3">
        <label for="delay" class="form-label">Delay Between Messages (in seconds):</label>
        <input type="number" class="form-control" id="delay" name="delay" required>
      </div>
      <div class="mb-3">
        <label for="repeat" class="form-label">Number of Times to Repeat:</label>
        <input type="number" class="form-control" id="repeat" name="repeat" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Send Messages</button>
    </form>
  </div>
</body>
</html>
'''

# Route to handle the form
@app.route("/", methods=["GET", "POST"])
def telegram_bot():
    if request.method == "POST":
        # Get form data
        api_id = int(request.form["apiId"])
        api_hash = request.form["apiHash"]
        phone_number = request.form["phoneNumber"]
        target_username = request.form["targetUsername"]
        delay = int(request.form["delay"])
        repeat_count = int(request.form["repeat"])
        txt_file = request.files["txtFile"]

        # Read messages from file
        try:
            messages = txt_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"

        # Initialize Telegram client
        client = TelegramClient("session", api_id, api_hash)

        async def send_messages():
            try:
                await client.start(phone=phone_number)
                print("[INFO] Logged into Telegram successfully!")
                
                for _ in range(repeat_count):
                    for message in messages:
                        try:
                            await client.send_message(target_username, message)
                            print(f"[SUCCESS] Message sent to {target_username}: {message}")
                            time.sleep(delay)
                        except errors.rpcerrorlist.UsernameNotOccupiedError:
                            return f"<p>[ERROR] Username {target_username} does not exist.</p>"
                        except Exception as e:
                            print(f"[ERROR] Failed to send message: {e}")
                            time.sleep(5)

            except Exception as e:
                return f"<p>[ERROR] Failed to log in or send messages: {e}</p>"
            finally:
                await client.disconnect()
                print("[INFO] Disconnected from Telegram.")

        # Run the Telegram client and send messages
        client.loop.run_until_complete(send_messages())
        return "<p>Messages sent successfully!</p>"

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

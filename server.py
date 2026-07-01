import os
import pty
import subprocess
import select
from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

master_fd, slave_fd = pty.openpty()

# 🔥 global history buffer
history = []

proc = subprocess.Popen(
    ["tradingagents"],
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    text=False,
    bufsize=0
)

@sock.route("/ws")
def ws(ws):

    # 🔥 1. send full history on connect
    for chunk in history:
        ws.send(chunk)

    while True:
        r, _, _ = select.select([master_fd], [], [], 0.1)

        if master_fd in r:
            try:
                output = os.read(master_fd, 1024).decode(errors="ignore")
            except OSError:
                break

            if output:
                # 🔥 store history
                history.append(output)

                # optional safety limit (avoid memory leak)
                if len(history) > 5000:
                    history.pop(0)

                ws.send(output)

        msg = ws.receive()
        if msg:
            os.write(master_fd, msg.encode())


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

import os
import pty
import subprocess
import select
from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# spawn CLI in a real pseudo-terminal
master_fd, slave_fd = pty.openpty()

proc = subprocess.Popen(
    ["tradingagents"],   # your CLI
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    text=True,
    bufsize=0
)

@sock.route("/ws")
def ws(sock):
    while True:
        # read CLI output
        r, _, _ = select.select([master_fd], [], [], 0.1)

        if master_fd in r:
            output = os.read(master_fd, 1024).decode(errors="ignore")
            if output:
                sock.send(output)

        # receive browser input
        msg = sock.receive()
        if msg:
            os.write(master_fd, msg.encode() + b"\n")


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

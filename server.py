import os
import pty
import subprocess
from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# Start CLI in a pseudo terminal
master_fd, slave_fd = pty.openpty()

proc = subprocess.Popen(
    ["tradingagents"],   # your CLI
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    text=True
)

@sock.route("/ws")
def ws(sock):
    import os
    import select

    while True:
        r, _, _ = select.select([master_fd], [], [], 0.1)

        if master_fd in r:
            output = os.read(master_fd, 1024).decode(errors="ignore")
            if output:
                sock.send(output)

        msg = sock.receive()
        if msg:
            os.write(master_fd, msg.encode() + b"\n")


@app.get("/")
def index():
    return """
<!doctype html>
<html>
<head>
<style>
body { margin:0; background:black; color:#00ff88; font-family: monospace; }
#term { white-space: pre-wrap; padding:10px; }
input { width:100%; background:black; color:#00ff88; border:none; }
</style>
</head>
<body>
<pre id="term"></pre>
<input id="input" autofocus />

<script>
const term = document.getElementById("term");
const input = document.getElementById("input");

const ws = new WebSocket("ws://" + location.host + "/ws");

ws.onmessage = (e) => {
  term.textContent += e.data;
  window.scrollTo(0, document.body.scrollHeight);
};

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    ws.send(input.value);
    input.value = "";
  }
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

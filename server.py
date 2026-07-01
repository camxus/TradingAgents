import os
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def run_tradingagents():
    # run CLI
    result = subprocess.run(
        ["tradingagents"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )

    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "code": result.returncode
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

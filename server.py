import os
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def health():
    return jsonify({"status": "ok"})


@app.get("/run")
def run_tradingagents():
    try:
        result = subprocess.run(
            ["tradingagents"],
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )

        return jsonify({
            "code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # IMPORTANT: must bind to 0.0.0.0 for Cloud Run
    app.run(host="0.0.0.0", port=port)

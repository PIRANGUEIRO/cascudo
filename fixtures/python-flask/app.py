from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return helper()

def helper():
    return "ok"

def dead_python():
    return "nunca usado"

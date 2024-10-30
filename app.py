from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello Flask!"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=9000)
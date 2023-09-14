import pandas as pd
from flask import Flask, render_template, jsonify, request

from nn import run_model

deberta_v3_large = '/kaggle/input/deberta-v3-large-hf-weights'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mcq', methods=['POST'])
def mcq():
    data = request.get_json()
    print(data)
    print(type(data))
    df = pd.DataFrame.from_dict([data], orient="columns")
    answer = run_model(df)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

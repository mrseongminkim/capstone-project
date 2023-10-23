import pandas as pd
from flask import Flask, render_template, jsonify, request

from neural_network import infer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mcq', methods=['POST'])
def mcq():
    data = request.get_json()
    df = pd.DataFrame.from_dict([data], orient="columns")
    answer, prob = infer(df)
    return jsonify({'answer': answer, 'prob': prob})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4200, debug=False)

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

# pip install flask-cors

# Rutas de los archivos
API_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(API_DIR)
CRAWLER_DIR = os.path.join(BASE_DIR, 'CrawlerIndexerSearcher', 'SAR_Crawler.py')
INDEXER_DIR = os.path.join(BASE_DIR, 'CrawlerIndexerSearcher', 'SAR_Indexer.py')
SEARCHER_DIR = os.path.join(BASE_DIR, 'CrawlerIndexerSearcher', 'SAR_Searcher.py')


app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

@app.route('/', methods=['GET'])
def root():
    return "root"


@app.route('/api/holamundo', methods=['GET'])
def holamundo():
    parametro1 = request.args.get('parametro1')
    parametro2 = request.args.get('parametro2')

    args = ['python', os.path.join(API_DIR, 'holamundo.py')]

    if parametro1:
        args.append(parametro1)
    if parametro2:
        args.append(parametro2)

    result = subprocess.run(args, capture_output=True, text=True)

    return jsonify({'output': result.stdout, 'error': result.stderr})


@app.route('/api/crawler', methods=['GET'])
def crawler():
    outBaseFilename = request.args.get('OUT_BASE_FILENAME')
    initialURL = request.args.get('INITIAL_URL')
    batchSize = request.args.get('BATCH_SIZE')
    documentLimit = request.args.get('DOCUMENT_LIMIT')
    maxDepthLevel = request.args.get('MAX_DEPTH_LEVEL')

    args = ['python', CRAWLER_DIR]

    if outBaseFilename:
        args.append("--out-base-filename")
        args.append(outBaseFilename)
    if initialURL:
        args.append("--initial-url")
        args.append(initialURL)
    if batchSize:
        args.append("--batch-size")
        args.append(batchSize)
    if documentLimit:
        args.append("--document-limit")
        args.append(documentLimit)
    if maxDepthLevel:
        args.append("--max-depth-level")
        args.append(maxDepthLevel)

    print(args)

    result = subprocess.run(args, capture_output=True, text=True)
    return jsonify({'output': result.stdout, 'error': result.stderr})


@app.route('/api/indexer', methods=['GET'])
def indexer():
    dir = request.args.get('dir')
    index = request.args.get('index')
    stem = request.args.get('stem')
    permuterm = request.args.get('permuterm')
    multifield = request.args.get('multifield')
    positional = request.args.get('positional')

    args = ['python', INDEXER_DIR]

    if dir:
        args.append(dir)
    if index:
        args.append(index)
    if stem:
        args.append("-S")
    if permuterm:
        args.append("-P")
    if multifield:
        args.append("-M")
    if positional:
        args.append("-O")

    result = subprocess.run(args, capture_output=True, text=True)
    print(result)
    return jsonify({'output': result.stdout, 'error': result.stderr})


@app.route('/api/searcher', methods=['GET'])
def searcher():
    index = request.args.get('index')
    stem = request.args.get('stem')
    snippet = request.args.get('snippet')
    count = request.args.get('count')
    all = request.args.get('all')
    query = request.args.get('query')

    args = ['python', SEARCHER_DIR]

    if index:
        args.append(index)
    if stem:
        args.append("-S")
    if snippet:
        args.append("-N")
    if count:
        args.append("-C")
    if all:
        args.append("-A")
    if query:
        args.append("-Q " + query)

    result = subprocess.run(args, capture_output=True, text=True)
    return jsonify({'output': result.stdout, 'error': result.stderr})


@app.route('/api/post', methods=['POST'])
def post():
    dato1 = request.args.get('dato1')
    dato2 = request.args.get('dato2')
    print(dato2)
    return jsonify({'dato1': dato1})

if __name__ == '__main__':
    app.run(port=5000)
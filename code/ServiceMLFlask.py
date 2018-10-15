#!flask/bin/python
import sys
import logging
from threading import Thread
import requests

from flask import Flask
from flask import jsonify
from flask import request


sys.path.append('./vgg19')

from Persistancy import Persistancy
from ModelVgg19 import ModelVgg19

app = Flask(__name__, static_folder='./html/')

# @app.route('/mlflask/1.0/health', methods=['get'])
# def health():
#     return jsonify(status='OK')

# @app.route('/mlflask/1.0/vgg19start', methods=['get'])
# def health():
#     return jsonify(status='OK')

# @app.route('/mlflask/1.0/vgg19status', methods=['get'])
# def health():
#     return jsonify(status='OK')
#
# @app.route('/mlflask/1.0/vgg19stop', methods=['get'])
# def health():
#     return jsonify(status='OK')

@app.route('/mlflask/1.0/index', methods=['get'])
def index():
    return app.send_static_file('index.html')

@app.route('/mlflask/1.0/imageresultforurl', methods=['post'])
def imageresultforurl():
    jsonObject = request.get_json()
    #validate data
    if jsonObject == None:
        return jsonify('no json payload'), 500
    if not 'url' in jsonObject:
        return jsonify('missing: url'), 500
    url = jsonObject['url']
    downloadImage(persistancy, url)
    model.enqueue(url)
    while(persistancy.loadImageResult(url) == None):
        time.sleep(0.1)
    return jsonify(persistancy.loadImageResult(url))




def downloadImage(persistancy, url):
    filePath = persistancy.getImageFilePath(url)
    response = requests.get(url, allow_redirects=True)

    with open(filePath, 'wb') as file:
        file.write(response.content)



modelFilePath = './data/vgg19.npy'
persistancy = Persistancy('./data/')
model = ModelVgg19(persistancy, modelFilePath)

t = Thread(target=model.start)
t.daemon = True
t.start()




if __name__ == '__main__':
    # logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(debug=True)

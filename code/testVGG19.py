import sys
from threading import Thread
import requests
import time
sys.path.append('./vgg19')

from Persistancy import Persistancy
from ModelVgg19 import ModelVgg19


def downloadImage(persistancy, url):
    filePath = persistancy.getImageFilePath(url)
    response = requests.get(url, allow_redirects=True)

    with open(filePath, 'wb') as file:
        file.write(response.content)



modelFilePath = './data/vgg19.npy'

persistancy = Persistancy('./data/')
model = ModelVgg19(persistancy, modelFilePath)

print('starting tread')
t = Thread(target=model.start)
t.daemon = True
t.start()
print('downloadImage')

url = 'https://circaoldhouses.com/wp-content/uploads/2017/10/key-hole-house-1.jpg'
downloadImage(persistancy, url)
print('enqueue')
sys.stdout.flush()
model.enqueue(url)
while(persistancy.loadImageResult(url) == None):
    # print('sleep')
    sys.stdout.flush()
    time.sleep(1)
print('join')
sys.stdout.flush()
t.join()

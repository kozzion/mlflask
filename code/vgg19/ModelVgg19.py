import requests
import os
import urllib.request
import argparse
import vgg19
import cv2
import tensorflow as tf
import numpy as np
import caffe_classes
import warnings
import os
import time
import sys
import json

from queue import *

class ModelVgg19(object):

    def __init__(self, persistancy, modelFilePath):
        super(ModelVgg19, self).__init__()
        self.persistancy = persistancy
        self.modelFilePath = modelFilePath
        self.workQueue = Queue()
        self.thread = None #TODO internalize thread
        self.status = 'Unloaded'
        self.isRunning = False

    def downloadModel(self):
        self.status = 'Downloading Model'
        raise "not implemented"


    def enqueue(self, url):
        self.workQueue.put(url)

    def work(self, session, softmax, x) :
        url = self.workQueue.get()
        imageFilePath = self.persistancy.getImageFilePath(url)
        imageResult = self.doFile(session, softmax, x, imageFilePath)
        os.remove(imageFilePath)
        self.persistancy.saveImageResult(url, imageResult)

    def doFile(self, session, softmax, x, imageFilePath) :
        imgResult = {} # todo get result
        imgResult['error'] = ''
        imgResult['resultRaw'] = []
        imgResult['mainLabel'] = ''

        try :
            img = cv2.imread(imageFilePath)# move this to other loop
            imgMean = np.array([104, 117, 124], np.float)# move this to other loop
            resized = cv2.resize(img.astype(np.float), (224, 224)) - imgMean # move this to other loop

            resultRaw = session.run(softmax, feed_dict = {x: resized.reshape((1, 224, 224, 3))})
            mainLabel = caffe_classes.class_names[np.argmax(resultRaw)]
            imgResult['resultRaw'] = resultRaw.tolist()
            imgResult['mainLabel'] = mainLabel
        except Exception as e:
            imgResult['error'] = 'could not process image'

        return imgResult



    def start(self):
        self.isRunning = True
        self.status = 'starting'
        if not(os.path.isfile(self.modelFilePath)) :
            downloadModel(self)
            raise "model not found"
        warnings.simplefilter(action='ignore', category=FutureWarning)

        #some params
        dropoutPro = 1
        classNum = 1000
        skip = []
        x = tf.placeholder("float", [1, 224, 224, 3])
        model = vgg19.VGG19(x, dropoutPro, classNum, skip, modelPath=self.modelFilePath)
        score = model.fc8
        softmax = tf.nn.softmax(score)

        with tf.Session() as session:
            session.run(tf.global_variables_initializer())
            model.loadModel(session)
            self.status = 'running'
            while(self.isRunning):
                self.work(session, softmax, x)

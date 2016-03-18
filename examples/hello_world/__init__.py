import itertools as it
import numpy as np
from collections import namedtuple
from tidml import DataSource, Algorithm, SimpleEngine

MyQuery = namedtuple('MyQuery', 'day')
MyTrainingData = namedtuple('MyTrainingData', 'temperatures')
MyPredictedResult = namedtuple('MyPredictedResult', 'temperature')


class MyModel(namedtuple('MyModel', 'temperatures')):
    def sanity_check(self, label):
        days = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
        for k in self.temperatures.keys():
            if k not in days:
                raise RuntimeError("{}: Invalid day '{}'".format(label, k))


class MyDataSource(DataSource):
    def read_training(self):
        data = [
            {'day': 'mon', 'temperature': 30},
            {'day': 'thu', 'temperature': 10},
            {'day': 'mon', 'temperature': 21},
        ]
        training_data = MyTrainingData(temperatures=data)
        print training_data
        return training_data


class MyAlgorithm(Algorithm):
    def train(self, training_data):
        lines = training_data.temperatures
        keyfunc = lambda i: i['day']
        training_data = sorted(lines, key=keyfunc)
        avg = {}
        for k, v in it.groupby(training_data, keyfunc):
            temps = map(lambda i: i['temperature'], v)
            avg[k] = np.mean(temps)
        model = MyModel(temperatures=avg)
        print model
        return model

    def predict(self, model, query):
        temp = model.temperatures[query.day]
        return MyPredictedResult(temperature=temp)


class MyEngineFactory(object):
    @staticmethod
    def create():
        return SimpleEngine({
            "datasource": {
                "class": MyDataSource
            },
            "algorithm": {
                "class": MyAlgorithm,
                "params": {
                    "model.pickle": "~/.tidml/hello_world/model.pkl"
                }
            }
        })

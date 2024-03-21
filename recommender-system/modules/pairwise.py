
import importlib

class PairwiseModel():

    @classmethod
    def fit(cls, data):

        module_name = "sklearn.metrics.pairwise"
        module = importlib.import_module(module_name)
        func = getattr(module, cls.metric)

        results = func(data.iloc[0:1], data.iloc[:]).argsort()[0][-7:-1]
        return results

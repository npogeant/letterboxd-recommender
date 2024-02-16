
from modules.pairwise import PairwiseModel

class Model(PairwiseModel):
    NAME = 'distance_model'
    MODEL_LIBRARIES = {'scikit-learn': '0.24.1'}
    FEATURES = 'pairwise'
    metric = 'euclidean_distances'

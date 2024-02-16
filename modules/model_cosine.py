
from modules.pairwise import PairwiseModel

class Model(PairwiseModel):
    NAME = 'similarity_model'
    MODEL_LIBRARIES = {'scikit-learn': '0.24.1'}
    FEATURES = 'pairwise'
    metric = 'cosine_similarity'

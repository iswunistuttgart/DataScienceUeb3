import pickle

class MachineLearning():
    
    def __init__(self):
        self.X_test=0        
    
    def trainMLStift(self):
        self.knn_clf_ = pickle.load( open( 'Models/tree_clf.p', "rb" ) )

    def predictStift(self, snapshot):
        return self.knn_clf_.predict([snapshot])

    def predictStiftProbability(self, snapshot):
        return self.knn_clf_.predict_proba([snapshot])

    def prepareModels(self):
        self.trainMLStift()

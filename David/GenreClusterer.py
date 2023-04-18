## Made by David Gaviria    April 13, 2023 ##

from sklearn import model_selection
from sklearn import cluster
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from clusteval import clusteval
import pandas as pd


## Grouping class for clusters used by GenreClusterer
class Grouping:

    # init
    def __init__(self, _id):
        self._id = _id
        self.composition = dict()       # stores the genres and a list of points belonging to said genre in the cluster
        self.profile = []               # stores tuples of the genre and percentage of cluster belonging to said genre
        self.size = 0                   # total points in cluster

    # add sample to composition
    def insert(self, genre, sample=1):
        if genre not in self.composition:
            self.composition[genre] = []    
        #insert corresponding point
        genreSlot = self.composition[genre]
        genreSlot.append(sample)
        self.size += 1

    # draws up profile of cluster
    def computeProfile(self):
        otherPercentage = 0
        for genre in self.composition:
            genrePercent = len(self.composition[genre]) / self.size
            if genrePercent >= 0.05:
            # dont add genres that are insignificant
                self.profile.append((genre, genrePercent))
            else:
            #add it instead to 'other
                otherPercentage += genrePercent
        # add other percentage to make percentages = 1
        self.profile.append(('other', otherPercentage))     
        self.profile.sort(key = lambda x:x[1], reverse=True)



## GenreClusterer class
class GenreClusterer:

    # init
    def __init__(self, model):
        self.clusters = {}
        # get model type
        if model == 'KMeans':
            self.model = cluster.KMeans(init='k-means++')
            self.modelType = 'KMeans'
        elif model == 'DBScan':
            self.model = cluster.DBSCAN()
            self.modelType = 'DBScan'
        else:
            raise Exception("Invalid model type, accepted models are 'KMeans' and 'DBScan'")
    
    # % written by niki %
    def update(self, param):
        if self.model == 'KMeans':
            self.model = cluster.KMeans(init='k-means++', n_clusters=param)
        else:
            self.model = cluster.DBSCAN(eps=param)

    # % written by niki %
    # tune optimal parameters for model
    def find_parameters(self, xValidate):
        if self.modelType =='KMeans':
            ce = clusteval(evaluate='silhouette')
            out = ce.fit(xValidate)
            param_df = pd.DataFrame(out['score'])
            param_df = param_df.drop(columns=['cluster_threshold'])
            max_score = max(param_df['score'])
            bestK = int(param_df.loc[param_df['score'] == max_score]['clusters'])
            bestParameters = [bestK, round(max_score,3)]
            ce.plot()
        else:
            ce = clusteval(cluster='dbscan', max_clust=25)
            out = ce.fit(xValidate)
            clusters = out['fig']['sillclust']
            eps = out['fig']['eps']
            sil_scores = out['fig']['silscores']
            param_df = pd.DataFrame({'n_clusters':clusters, 'Epsilon':eps, 'Silhouette Score':sil_scores})
            param_df = param_df.sort_values(by=['n_clusters', 'Epsilon'])
            max_score = max(param_df['Silhouette Score'])
            bestEps = round(min(param_df.loc[param_df['Silhouette Score'] == max_score]['Epsilon']),3)
            bestParameters = [bestEps, round(max_score,3)]
            ce.plot()
        return bestParameters, param_df

    # fits the model
    def fit(self, xTrain):   
        self.model.fit(xTrain)
        return self.model.labels_
        
    # generates cluster profiles based off predicted cluster labels and actual genre labels
    def generateClusterProfiles(self, yHat, genreLabels):
        # build cluster profiles 
        for i in range(len(yHat)):
            #sample = xTrain.iloc[i]  
            thisGenre = genreLabels.iloc[i]
            clusterId = yHat[i]
            # get cluster
            if clusterId not in self.clusters:
                self.clusters[clusterId] = Grouping(_id=i)
            thisCluster = self.clusters[clusterId] 
            # insert into cluster
            thisCluster.insert(thisGenre)
        # compute the stats of the clusters
        for clusterId in self.clusters:
            thisCluster = self.clusters[clusterId]
            thisCluster.computeProfile()



    # print out clusters
    def displayClusters(self):
        for clusterId in self.clusters:
            thisCluster = self.clusters[clusterId]
            print("<Cluster %s>(%s)" % (thisCluster._id, thisCluster.profile))

    # % written by niki %
    # TODO: display first two principal components of clustering
    def plot_components(self, xTrain):
        n = len(xTrain.columns)
        pca = PCA(n_components=n)
        return None

            


# necessary imports
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import sklearn.cluster as clustering
import sklearn.preprocessing
from sklearn.decomposition import PCA
import math

a = np.loadtxt("data.out", delimiter=',').T
num_clusters = math.ceil(a.shape[0]*a.shape[1] / np.count_nonzero(a))

a = sklearn.preprocessing.StandardScaler().fit_transform(a)
a = PCA(.95).fit_transform(a)


k_means = clustering.KMeans(num_clusters).fit(a);
labels = k_means.labels_

subjects = np.loadtxt('subjects.out', dtype=object, delimiter='\n', encoding='utf-8', comments=None).T
np.set_printoptions(threshold=np.nan)
print(np.c_[subjects, labels]);

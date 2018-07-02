import numpy as np
import os, json
import pandas as pd
import matplotlib.pyplot as plt
import sklearn.cluster as clustering
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

data = json.load(os.popen('''
    perl 'email_scraper.pl' 'Archived.mbox'
'''))

email_df = pd.DataFrame(data)
email_df.drop(email_df.query(
        "bodies == ''"
        ).index, inplace=True)

def top_tfidf_feats(row, features, top_n=20):
    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    df = pd.DataFrame(top_feats, columns=['features', 'score'])
    return df
def top_feats_in_doc(X, features, row_id, top_n=25):
    row = np.squeeze(X[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)
def top_mean_feats(X, features,
    grp_ids=None, min_tfidf=0.1, top_n=25):
    if grp_ids:
        D = X[grp_ids].toarray()
    else:
        D = X.toarray()
    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)

#print(json.load(os.popen('''
#    perl 'email_scraper.pl' 'Archived.mbox'
#''')))

vect = TfidfVectorizer(stop_words='english', max_df=0.50, min_df=2)
X = vect.fit_transform(email_df.bodies)
X_dense = X.todense()
coords = PCA(n_components=2).fit_transform(X_dense)
plt.scatter(coords[:, 0], coords[:, 1], c='m')
#plt.show()

features = vect.get_feature_names()
#print(top_mean_feats(X, features, top_n=10))

n_clusters = 5
clf = clustering.KMeans(n_clusters=n_clusters, max_iter=100, init='k-means++', n_init=1)
labels = clf.fit_predict(X)
def top_feats_per_cluster(X, y, features, min_tfidf=0.1, top_n=25):
    dfs = []
    labels = np.unique(y)
    for label in labels:
        ids = np.where(y==label) 
        feats_df = top_mean_feats(X, features, ids,    min_tfidf=min_tfidf, top_n=top_n)
        feats_df.label = label
        dfs.append(feats_df)
    return dfs

print(top_feats_per_cluster(X, labels, features))

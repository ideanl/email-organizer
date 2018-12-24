import numpy as np
import os, json
import pandas as pd
import random
import colorsys
import matplotlib.pyplot as plt
import sklearn.cluster as clustering
from sqlalchemy import create_engine
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.cluster import OPTICS

def read_json_and_store_emails(json_name, hdf_name):
    if not os.path.isfile(hdf_name):
        if os.path.isfile(json_name):
            with open(json_name) as f:
                data = json.load(f)
        else:
            data = json.load(os.popen('''
                perl 'email_scraper.pl' 'Archived.mbox'
            '''))

        email_df = pd.DataFrame(data)
        email_df.drop(email_df.query(
                "bodies == '' | subjects == '' | subjects.str.contains('Production Exception') == True | subjects.str.contains('Staging Exception') == True"
                ).index, inplace=True)
        store = pd.HDFStore(hdf_name)
        store['df'] = email_df
        return store['df']
    else:
        store = pd.HDFStore(hdf_name)
        return store['df']

def top_feats_per_cluster(svd, kmeans, labels, terms):
    labels = np.unique(labels)
    if svd:
        original_space_centroids = svd.inverse_transform(kmeans.cluster_centers_)
        order_centroids = original_space_centroids.argsort()[:, ::-1]
    else:
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

    for label in labels:
        print("Cluster %d:" % label, end='')
        for ind in order_centroids[label, :10]:
            print(' %s' % terms[ind], end='')
        print()

def get_colors(n):
    HSV_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = [int(x*255) for x in colorsys.hsv_to_rgb(*rgb)]
        hex_out.append('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])) 
    return hex_out

engine = create_engine('postgresql://localhost:5432/email_classifier')
email_df = read_json_and_store_emails('email_metadata.json', 'email_store.h5')

print("Vectorizing...")
vect = TfidfVectorizer(stop_words='english', max_df=0.50, min_df=2)
X = vect.fit_transform(email_df.bodies)

svd = True

if svd:
    print("Performing SVD...")
    svd = TruncatedSVD(500)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    X_new = lsa.fit_transform(X)

n_clusters = 8
kmeans = False

if kmeans:
    print("Performing K-Means...")
    clf = clustering.KMeans(n_clusters=n_clusters, init='k-means++', n_jobs=-1)
    labels = clf.fit_predict(X_new)
else:
    clf = OPTICS(max_eps=5, min_samples=8, metric='cosine', n_jobs=-1)
    labels = clf.fit_predict(X_new)
    colors = get_colors(len(np.unique(labels)))
    colors = [colors[l] for l in labels]
#X_dense = X.todense()
#coords = PCA(n_components=2).fit_transform(X)

coords = TruncatedSVD(n_components=2).fit_transform(X)
plt.scatter(coords[:, 0], coords[:, 1], c=colors)
plt.show()


email_df['label'] = labels
email_df.to_sql('emails', engine, if_exists='replace')

colors = get_colors(len(np.unique(labels)))
colors = [colors[l] for l in labels]
#X_dense = X.todense()
#coords = PCA(n_components=2).fit_transform(X)
coords = TruncatedSVD(n_components=2).fit_transform(X)
plt.scatter(coords[:, 0], coords[:, 1], c=colors)
plt.show()

features = vect.get_feature_names()
top_feats_per_cluster(svd, clf, labels, features)

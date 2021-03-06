import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KDTree
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

from postlearn.utils import rediscretize_cmap, colorbar_index


def compute_centers(km, X):
    centers = []
    for label in sorted(set(km.labels_)):
        centers.append(X[km.labels_ == label].mean(0))

    return np.array(centers)


def plot_decision_boundry(data, pipe, reducer=PCA):
    fig, ax = plt.subplots(figsize=(16, 12))
    if callable(reducer):
        reducer = reducer(n_components=2)
    # else assume it's already been instantiated...

    if isinstance(pipe, Pipeline) and len(pipe.steps) > 1:
        prepipe = Pipeline(pipe.steps[:-1])
        km = pipe.steps[-1][1]
        data_ = prepipe.transform(data)
    elif isinstance(pipe, Pipeline):
        prepipe = None
        km = pipe.steps[0][1]
        data_ = data
    else:
        prepipe = None
        km = pipe
        data_ = data

    X_reduced = reducer.fit_transform(data_)

    cluster_centers = getattr(km, 'cluster_centers_',
                              compute_centers(km, data_))

    mu_reduced = reducer.transform(cluster_centers)
    n_clusters = len(np.unique(km.labels_))
    tree = KDTree(mu_reduced)

    cmap = rediscretize_cmap(n_clusters, 'Set1')
    ax.scatter(mu_reduced[:, 0], mu_reduced[:, 1],
               c=np.arange(n_clusters), cmap=cmap,
               s=300)
    colorbar_index(ncolors=n_clusters, cmap=cmap)

    ax.scatter(X_reduced[:, 0], X_reduced[:, 1], c=km.labels_,
               cmap=cmap, alpha=.95)

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 100),
                         np.linspace(ymin, ymax, 100))
    T = np.c_[xx.ravel(), yy.ravel()]
    _, group = tree.query(T)

    Z = group.ravel().reshape(xx.shape)
    ax.pcolormesh(xx, yy, Z, alpha=.25, cmap=cmap)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    for label, xy in enumerate(mu_reduced[:, :2]):
        ax.annotate(label, xy, fontsize=28, fontweight="bold")
    return ax

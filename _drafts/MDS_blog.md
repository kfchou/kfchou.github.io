---
layout: post
---
<style>
td, th {
   border: none!important;
}
</style>

# MDS in a nutshell
MDS is a technique to visualize inter-object distances in a low dimensional, abstract space. In classification tasks, objects dissimilar to one another should have larger relative distances between one another and be farther apart in this abstract space. Hence, MDS is a valuable tool in various stages of building machine learning models for classification tasks. In particular, it can be used to evaluate the features used to train your ML model, the embeddings produced by your model, and how well the distance metrics used in the model captures the inherent similarities or dissimilarities in your data.

# Minimal Example
I'll use the UCI ML hand-written digits datasets as an example. Each hand-written digit is represented by a vector (flattened from its 2d representation). By default, [`sklearn.manifold.MDS`](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.MDS.html) calculates the L2 norm (i.e., Euclidean distance) between each vector prior to applying MDS on these vector distances.

```python
from sklearn.datasets import load_digits

digits = load_digits(n_class=4)
X, y = digits.data, digits.target

embedding = MDS(n_components=2, normalized_stress='auto')
X_transformed = embedding.fit_transform(X)

plot_embedding(X_transformed, "MDS") # see appendix
plt.show()
```
![MDS](/assets/MDS_digits_euclidean.png)

In this example, we can clearly see the handwritings of "0" is clustered away from "1", "2", and "3". On the other hand, some of the "2"s and "3"s that look alike are clustered closer together. Meanwhile, some "1"s are strangely far apart. It seems like there may be better ways to arrange these handwritten numbers.


# Distance Between Objects
## The Distance Matrix
The default setting of `sklearn.manifold.MDS` combines *distance calculations* with *dimenality reduction*. Let's talk about these two steps in more detail.

Conceptually, distance between vectors act like embeddings. The difference here is that while embeddings are abstract representations of objects, distances act as the abstract representation of relationships between objects. We can also think of distance as a quantification of "dissimilarity" between objects. 

`sklearn.manifold.MDS` calculates the [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) by default:

$d(p,q) = \sqrt{\sum^n_{i=1}(q_i-p_i)^2}$

By calculating the distances between all pairs of $p_i$ and $q_i$, we contruct a *distance matrix*. In the following example, the hand-writings of "0"s are visually similar and have smaller distances. On the other hand, the "1"s are more visually similar to the "2"s and "3"s than to each other. This is all captured by the distance matrix (left) and its visualization (right).

|  Distance Matrix     |   Corresponding MDS Visualization    |
| ---------------- | ---------------- |
| ![Distance Matrix](/assets/example_distances2.png) | ![MDS](/assets/example_mds2.png) |

## Comparing Distance Metrics
SK-Learn calculates inter-object Euclidean distances by default, but it can also visualize other distances metrics. To do this, we set `dissimilarity="precomputed"` and provide a distance matrix we calculate. 

SKlearn provides a [list of metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.DistanceMetric.html) intended for operating in the vector (i.e., Euclidean) space. Let's compare three commonly used distances in ML: Manhattan (L1), Euclidean (L2), and Cosine distances.

```py
from sklearn.metrics.pairwise import cosine_distances, manhattan_distances, euclidean_distances

distance_matrix = {}
distance_matrix['Manhattan'] = manhattan_distances(X)
distance_matrix['Euclidean'] = euclidean_distances(X)
distance_matrix['Cosine'] = cosine_distances(X)

embedding = MDS(
    n_components=2, 
    normalized_stress='auto', 
    dissimilarity='precomputed', 
    random_state=123)

for key, dist in distance_matrix.items():
    X_transformed = embedding.fit_transform(dist)
    plot_embedding(X_transformed, f"MDS, {key} Distance")
    plt.show()
```

|       |           |           |
| ---------------- | ---------------- | ---------------- |
| ![MDS](/assets/MDS_digits_euclidean.png) | ![MDS](/assets/MDS_digits_manhattan.png) | ![MDS](/assets/MDS_digits_cosine.png) |



When using the Manhattan distance, it seems like the "1"s are correctly grouped into a single cluster. Does this mean the Manhattan distance is a better metric? The only way to know for certain is to train some classifiers, and see how they perform based on a particular embedding.

There are [other distance metrics](https://sites.google.com/site/mb3gustame/reference/dissimilarity) intended to focus on relationships between objects, though these are less popular.

# Dimensionality & Goodness-of-fit
It's possible that embeddings are prefectly separated into clusters, but we cannot visualize this on a 2-dimensional plane. How many dimensions is necessary for this separation to occur? To answer this question, we plot stress vs. n_components. **Stress** is the goodness-of-fit statistic that MDS tries to minimize (see [Kruskal Stress](https://github.com/GeostatsGuy/PythonNumericalDemos/blob/master/SubsurfaceDataAnalytics_MultidimensionalScaling_Cities.ipynb)). Each **Component**  conceptually corresponds to a dimension, like in principal components analysis.

Stress varies between 0 and 1, with values near 0 indicating better fit. As we increase the dimensionality of MDS, we should find that stress approaches 0. Plotting stress against n_components is a good way to discover the number of dimensions needed to clearly separate your data into clusters. Empirically speaking, stress > 0.2 indicate a poor fit.

![stress](/assets/MDS_stress.png)

Based on this result, we would expect increasing `n_components` to 3 or 4 would better separate the clusters. Using 4 components would result in the following:

{% include scatter_plot_rotation.html %}

and we see that all clusters are clearly separated.


If the stress plot shows values increase or decrease in uneven steps, that may indicate something fishy with our embeddings [1].


# MDS vs. t-SNE
t-SNE is another popular dimensionality reduction technique to visualize high-dimensional data. The main difference between the two, in a practical sense, is that t-SNE performs a non-linear operation on the distance data and can exaggerate (or compress) the distances between groups. While this enables t-SNE to better visualize inter-group similarities, it distorts the global structure. On the other hand, MDS preserves distances between each datapoint, which may be more desired depending on your use case.

|      |       |
| ---------------- | ---------------- |
| ![MDS](/assets/mds_digits.png) | ![t-SNE](/assets/tsne_digits.png) |


# MDS as features in ML


# Further Reading:
Theory:
* Comparisons across embedding techniques: [sklearn](https://scikit-learn.org/stable/auto_examples/manifold/plot_lle_digits.html#sphx-glr-auto-examples-manifold-plot-lle-digits-py)

Practical Applications & Examples:
* https://pages.mtu.edu/~shanem/psy5220/daily/Day16/MDS.html
Politics, personality analyses
* [I. Kovan](https://towardsdatascience.com/multidimensional-scaling-mds-for-dimensionality-reduction-and-data-visualization-d5252c8bc4c0) - Examples from a geospatial perspective
* [J. Korstanje](https://towardsdatascience.com/multidimensional-scaling-d84c2a998f72) - Mapping & grouping people by their preferences; Mapping & grouping products by people's preferences
* [A. Scherman](https://github.com/GeostatsGuy/PythonNumericalDemos/blob/master/SubsurfaceDataAnalytics_MultidimensionalScaling_Cities.ipynb) - Python workflow



# Appendix: Plotting Functions
```py
import numpy as np
from matplotlib import offsetbox
from sklearn.preprocessing import MinMaxScaler


def plot_embedding(X, y, title, show_scatter=True, show_images=True):
    _, ax = plt.subplots()
    X = MinMaxScaler().fit_transform(X)

    # show scatter plot with digits as point markers
    if show_scatter:
        for digit in digits.target_names:
            ax.scatter(
                *X[y == digit].T,
                marker=f"${digit}$",
                s=60,
                color=plt.cm.Dark2(digit),
                alpha=0.225,
                zorder=2,
            )
    
    # show image examples
    if show_images:
        shown_images = np.array([[1.0, 1.0]])  # just something big
        for i in range(X.shape[0]):
            # plot every digit on the embedding
            # show an annotation box for a group of digits
            dist = np.sum((X[i] - shown_images) ** 2, 1)
            if np.min(dist) < 2e-3:
                # don't show points that are too close
                continue
            shown_images = np.concatenate([shown_images, [X[i]]], axis=0)
            imagebox = offsetbox.AnnotationBbox(
                offsetbox.OffsetImage(digits.images[i], cmap=plt.cm.gray_r), X[i]
            )
            imagebox.set(zorder=1)
            ax.add_artist(imagebox)

    ax.set_title(title)
    ax.axis("off")
```

# References
http://cda.psych.uiuc.edu/mds_509_2013/readings/systat_scaling_manual.pdf


---
layout: post
---

# MDS in a nutshell
MDS is a technique to visualize inter-object distances in a low dimensional, abstract space. In classification tasks, objects dissimilar to one another should have larger relative distances between one another and be farther apart in this abstract space. Hence, MDS is a valuable tool in various stages of building machine learning models for classification tasks. In particular, it can be used to evaluate the features used to train your ML model, the embeddings produced by your model, and how well the distance metrics used in the model captures the inherent similarities or dissimilarities in your data.

# Minimal Example
I'll use the UCI ML hand-written digits datasets as an example:

```python
from sklearn.datasets import load_digits

digits = load_digits(n_class=6)
X, y = digits.data, digits.target
n_samples, n_features = X.shape

# more code later
```
![MDS](/assets/MDS_digits.png)

# Distance between objects
The default distance between vectors is the L2 norm (Euclidean distance), and this is the default distance used by ` sklearn.manifold.MDS` (https://scikit-learn.org/stable/modules/generated/sklearn.manifold.MDS.html)
But we can also use L1 and other distances.
Examples and how they affect the clusters
See: https://sites.google.com/site/mb3gustame/reference/dissimilarity

# Number of dimensions necessary
“Stress” plot

# Compared to t-SNE
t-SNE is another popular dimensionality reduction technique to visualize high-dimensional data. The main difference between the two, in a practical sense, is that t-SNE performs a non-linear operation on the distance data and can exaggerate (or compress) the distances between groups. While this enables t-SNE to better visualize inter-group similarities, it distorts the global structure. On the other hand, MDS preserves distances between each datapoint, which may be more desired depending on your use case. 

Pictures from SK-learn

Comparisons across embedding techniques:
https://scikit-learn.org/stable/auto_examples/manifold/plot_lle_digits.html#sphx-glr-auto-examples-manifold-plot-lle-digits-py


# Practical Applications
https://pages.mtu.edu/~shanem/psy5220/daily/Day16/MDS.html
Politics, personality analyses


# High-dimensional feature geometry in a one-layer language model

Created: May 27, 2025 5:34 PM

# Summary

In this note, I investigate the feature geometry of 16384 features extracted from the 2048-dimenisonal activation of a single-layer language model using a sparse autoencoder. The main takeaways are summarized below.

- Feature directions are approximately uniformly distributed on the surface of a hypersphere in the high-dimensional latent space. This is also observed in my previous [toy models](https://wxu26.github.io/projects/sparse_superposition/index.html).
- The high dimensionality of the latent space allows efficient packing of features; features remain approximately orthogonal to each other despite superposition.
- The encoder and decoder vectors corresponding to the same feature could be substantially different. This difference is because the decoder vector corrects for interference by shifting away from neighboring features. The encoder vector is likely a better (though still imperfect) approximation of the true feature.
- Features with lower frequency tend to be squeezed into low-dimensional substrcutures because they are strongly repulsed by nearby high-frequency features to reduce interference. This effect does not seem to be caused by feature correlation, but it is more pronounced for correlated features because correlation reduces the penalty of squeezing.

Implications and open questions:

- Near orthogonality between features suggest that it may be feasible to manipulate features in-place (i.e., within the latent space) without much interference. I plan to explore this in a subsequent project.
- Correlated low-frequency features can cluster and develop low-dimensional substructures due to the aforementioned squeezing mechanism; thus it may be possible to zoom into a set of correlated features by focusing on a small neighborhood or a low-dimensional projection of the latent space. One caveat is that clustering requires not only strong correlation but also low feature frequency, which may limit its applicability.
- Neither the encoder nor the decoder faithfully trace the true features, although the encoder is slightly better. Is there a way to obtain a better estimate on true feature directions?

# Motivation and model setup

One fascinating feature of neural networks is that they can encode many more features than the model’s latent space dimension (e.g., dimension of residual stream) through superposition. Superposition involves a mapping between features and neurons that is complex in both ways: a single feature can be encoded using many neurons, and a neuron can be activated by many features; and understanding this mapping beyond a few dimensions remains a challenging problem.

Here I want to understand feature embedding in superposition by focusing on feature geometry: given a high-dimensional latent space, how are feature vectors distributed within this space? Understanding feature geometry is crucial for conceptualizing feature superposition beyond a few neurons, and may also offer new opportunities for improving feature extraction and steering.

In my [previous](https://wxu26.github.io/projects/sparse_superposition/index.html) [note](https://users.flatironinstitute.org/~wxu10/superposition_sparse.html), I showed that in a toy model encoding sparse features, features form a nearly uniform lattice on a $n_{\rm model}$-dimensional hypersphere. This layout fully utilizes the latent space to maximize feature separation and minimize interference. On the other hand, research from Anthropic that extract features from language models ([single-layer](https://transformer-circuits.pub/2023/monosemantic-features/index.html) or [Claude Sonnet](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)) seem to show more feature clustering. (One caveat that the clustering is demonstrated by a UMAP 2D embedding, which does not fully capture the high-dimensional feature geometry.) The goal of this note is to carefully analyze a feature set from a language model and determine how to revise and extend the insights from my previous toy model.

I analyze a feature set extracted from a one-layer language model; the model and features come from [Neel Nanda’s open-source reproduction of Anthropic’s paper](https://www.alignmentforum.org/posts/fKuugaxt2XLTkASkk/open-source-replication-and-commentary-on-anthropic-s). Using a sparse autoencoder (SAE), it extracts 16384 features from the activation of 2048 neurons.

The sparse encoder predicts activation $x_i$  with shape $(n_{\rm model},)=(2048,)$ as follows:

$$
x' = W_{\rm dec}^T{\rm ReLU}(W_{\rm enc}x+b_{\rm enc})+b_{\rm dec}.
$$

Here I use a notation slightly different from the original paper so that the encoding and decoding weights $W_{\rm enc},W_{\rm dec}$ both have the same shape $(n_{\rm feature},n_{\rm model},)=(16384,2048,)$. A feature $i$ is mainly represented by two vectors, $W_{{\rm enc},i}$ and $W_{{\rm dec},i}$. Since the normalization of these vectors can be arbitrary, I mainly focus on their directions, $\hat w_{{\rm enc},i}$ and $\hat w_{{\rm dec},i}$. In the discussion below, “features” and “feature vectors” all refer to these unit vectors unless otherwise noted. By definition, these unit vectors lay on the surface of a $n_{\rm model}$-dimensional hypersphere.

# An overall uniform and nearly orthogonal distribution, with a few exceptions

Let’s begin with three simple feature-level properties:

- the frequency of the feature: the probability of having nonzero feature amplitude $A_i={\rm ReLU}(W_{\rm enc}x+b_{\rm enc})_i$ on the test sample.
- the volume of the feature: the fraction of hypersphere surface which is closer to this feature than any other features; this provides an estimate for feature density. Feature volume is hard to calculate analytically, and I just perform a Monte Carlo estimation using $1024\times n_{\rm feature}$ random directions on the hypersphere.
- angular separation from nearest neighbor: this provides more information on the level of clustering and interference.

![overview.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/overview.png)

The above plot shows these properties for the encoder (top) and decoder (bottom) feature vectors. The most obvious trend is a dichotomy between ultra-low-frequency (grey) and finite-frequency (blue) features, which has been noted in Neel’s original blog post. The ultra-low-frequency component makes up about half of all features; they all map to approximately the same direction in the encoder (hence nearly zero volume and separation), and map to (seemingly) random directions in the decoder. It is most likely an artifact arising from SAE training: their direction in the encoder has no significance (because it can change between different SAE runs), and the model performance is barely affected if we remove all these features. Because these features are not a property of the language model, in all analysis below I will simply ignore this population with a cut at feature frequency $f_i=3\times 10^{-4}$.

After excluding the ultra-low-frequency features, the zeroth order takeaway is that in the encoder the features are overall uniformly distributed and near-orthogonal. All features have approximately the same volume. The minimum separation is also quite uniform and nearly orthogonal, with $\cos\theta_{\rm min}\sim 0.1$.

The equipartition of feature volume may come as a surprise. Intuitively, one may assume that more important (i.e., more frequent) features naturally take up more space, which is seen in low-dimensional toy models (e.g., [Anthropic’s toy model paper](https://transformer-circuits.pub/2022/toy_model/index.html)). In our case, while there is indeed a positive correlation between frequency and volume, this correlation is very weak, with feature volume varying by only ~20% across ~2 orders of magnitude in feature frequency. This behavior has been hypothesized in my previous note: as the model dimension increases, it is increasingly uneconomic to increase the volume of the more important features, because the increase in feature volume can no longer translate to significant increase in feature separation.

Beyond this zeroth-order result of approximately uniform, nearly orthogonal embedding, a few interesting trends stand out.

**Decoder features are different from encoder features.** This is already visible in the results above; the decoder features show much closer separations (median $\cos\theta_{\rm min}\sim 0.4$). While the encoding and decoding features still show good correspondence in that for all features $\hat w_{{\rm dec},i}$ is closer to $\hat w_{{\rm enc},i}$ than any other $\hat w_{{\rm dec},j}$, the alignment between the corresponding encoder and decoder vectors show large scatter.

![enc_dec_alignment.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/enc_dec_alignment.png)

**Features are not as orthogonal as they can be.** In the figure below I plot the distribution of $\theta$ between all pairs (left) and $\theta_{\rm min}$ (right) in the encoder, and compare them with the expected value of a random distribution of the same number of features on the hypersphere surface. Features are less separated from each other compared to a random distribution, even for the more orthogonal encoder embedding. (As a side note, random distribution is a pretty good benchmark here; in the limit of large $n_{\rm model}$ and $n_{\rm feature}$ the typical $\theta_{\rm min}$ from a random distribution of directions is within an order-unity factor of the optimal $\theta_{\rm min}$ from hyperpshere packing theory.) This is different from my previous toy model results where the features are maximally orthogonal through forming a lattice representing the densest hypersphere packing.

![mu_distribution.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/mu_distribution.png)

Understanding these trends will be the focus of the next couple of sections.

# Understanding encoder-decoder asymmetry

The asymmetry between encoder and decoder is quite puzzling; if they represent the same feature, shouldn’t they be the same? And since they are different, which of them better represents the feature’s embedding in the model’s activation space?

My conjecture is that this behavior is related to feature interference. Since features are not perfectly orthogonal, input in one feature could also cause low-amplitude excitation of nearby features in the SAE. If encoders and decoders are unit vectors $\hat w_i$ perfectly aligned with the real features and all biases are zero, this creates an error $\sim \cos\theta_{\rm min} A_i\hat w_j$ where j is i’s nearest neighbor and $A_i$ is the true amplitude of feature i. The key observation is that this error term scales linearly with $A_i$; therefore it can be perfectly canceled by a shift to the decoder vector by

$$
W_{{\rm dec},i}-W_{{\rm enc},i}=-\cos\theta_{\rm min}W_{{\rm dec},j}.
$$

In summary, a shift away from the nearest neighbor offsets interference.

A real SAE is more complex than this for a few reasons: biases break the perfect linearity; a feature may interfere with multiple nearby features; most importantly, this kind of shift may not be geometrically allowed because the equation above can be satisfied by all interfering pairs when there are more interfering pairs than the number of features. Therefore it cannot fully cancel interference. But the basic idea remains valid: shifting decoder away from the nearest neighbor (or neighbors) reduces interference.

To test this idea on the feature data, I check whether the decoder vector deviate from the encoder vector in a way that avoid its nearest neighbor. It is hard to characterize such three-vector geometry ($\hat w_{{\rm enc},i},\hat w_{{\rm dec},i},\hat w_{{\rm dec},j}$) in a high-dimensional space, but this can be done by checking whether the decoder vector is closer to the mirror image of the nearest neighbor, $2\hat w_{{\rm enc},i}-\hat w_{{\rm dec},j}$, than the nearest neighbor $\hat w_{{\rm dec},j}$ itself.

![mu_with_mirror.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/mu_with_mirror.png)

The result of this comparison in the figure above agrees very well with my conjecture; the deviation is significantly better aligned with the mirrored vector, suggesting a shift that avoids the nearest neighbor.

This interpretation also suggests that the encoder vector better traces the true feature, because the decoder vector contains this additional interference correction term. However, it is worth noting that even the encoder vector may not exactly trace the feature. Similar to the interference correction discussed above, it is beneficial for the encoder to slightly deviate from the true feature in a direction opposite to its nearest neighbor(s), because a sufficiently small shift always reduces interference: an $\epsilon$ shift reduces the response to the nearest feature by $\mathcal{O}(\epsilon)$ at the cost of reducing the response to the true feature by only $\mathcal{O}(\epsilon^2)$.

This leaves an important question: how do we estimate the true feature direction using a SAE? As a rough estimate, we can use the encoder direction; this is the approach I will take here. But can we do better than this? Two directions that may be worth looking into in future works are (1) training SAEs at different resolutions to observe how encoder vectors shift as the encoder space becomes more crowded; (2) using toy models with prescribed features to quantitatively understand the encoder-feature shift. Hopefully these efforts could put upper limits on shift amplitude or allow one to estimate the unknown encoder-feature shift with the measurable decoder-encoder shift.

# Feature squeezing and low-dimensional substructures

Another important trend we have observed earlier is that features are closer to each other than a uniform distribution - in other words, features seem to be somewhat clustered. This is clearly demonstrated in the figure below, where I plot the number of neighbors within a given separation for a random collection of features.

![n_neighbor.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/n_neighbor.png)

Many of these features show more clustering than a uniform distribution; the local feature density can increase by many orders of magnitude.

Comparing this with the feature volume result reveals an interesting contrast: feature density is nearly uniform when defined with volume per feature, but more clustered when defined with feature per volume. Together, this suggests that features deviate from a uniform distribution by squeezing instead of compression. To be specific, instead of being clustered along all directions, the features are only clustered along some directions but are further separated along other directions, allowing the feature volume to remain roughly in equipartition.

This squeezing interpretation suggests that features should develop substructures with dimensionality $<n_{\rm model}$. We can probe these low-dimensional substructures by measuring the fractal dimension $D$ for a given $\theta$ neighborhood of a feature. This is achieved by solving the following equation:

$$
\frac{\partial \log n_{\rm neighbor}}{\partial\theta} = \frac{\partial \log C_{D}(\theta)}{\partial \theta}
$$

Here $C_{D}(\theta)$ is the area of the spherical cap with radius $\theta$ on the $D$ dimensional surface of a $D+1$ dimensional hypersphere. Note that in the small $\theta$  limit this relation gives the fractal dimension in Euclidean space.

![dimension.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/dimension.png)

The above feature shows the estimated fractal dimension for a random selection of encoder features. At a global scale ($\theta\approx\pi/2$), the encoder features are broadly consistent with uniform distribution (which would give $D=n_{\rm model}-1=2047$). As a side note, the estimate becomes more noisy when the dimension is high, since as $D$ increases, uncertainty in $\theta(n_{\rm neighbor})$ translates to larger uncertainty in $D$. So the scatter at larger $\theta$ is likely just the uncertainty in the estimate. On the other hand, at more local scales (smaller $\theta$) there is clear sign of clustering into lower-dimensional substructures. The scale-dependent dimensionality can be interpreted as a result of substructures being developed locally and losing coherence across larger scales. (One analogy could be the filamentary structures in the cosmic web.) Also note that the dimensionality among closest neighbors (left end of each line) is often higher than the dimensionality among intermediate-distance neighbors; this may be a result of the encoder-feature shift discussed earlier.

How are these low-dimensional substructures formed? Broadly speaking there are three possibilities: by attraction, by repulsion, or by neuron alignment.

- Attraction: low-dimensional structure forms because features in the substructure attract each other (more precisely, because they repulse each other less than typical features); this can be due to feature correlation, as has been demonstrated in toy models before.
- Repulsion: low-dimensional substructure forms because features are compressed externally; for example, in order to avoid a nearby feature (not in the compressed substructure) with high importance.
- Neuron alignment: features are preferentially encoded by fewer neurons, so nearby features are likely encoded by the same small collection of neurons.

As a side note, examples of forming low-dimensional substructures by attraction and repulsion abound in nature; for example, filamentary structures of gas in star-forming regions can form both from self-gravity (attraction) or from the push of powerful winds from massive stars (repulsion).

There are several lines of evidence suggesting that low-dimensional substructures are formed primarily by repulsion.

![dimension_w_freq.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/dimension_w_freq.png)

First, the features in these low-dimensional substructures are mainly low-frequency features, whereas high-frequency features barely show signs of squeezing. (Extrapolating this result a bit, the cluster of excluded ultra-low-frequency features that end up in a single direction may even be an extreme case of squeezing into a 0-D structure.) This is reasonable because avoiding interference means that a feature is repulsed by all its neighbors, and features receive stronger push from more frequent neighbors. One caveat is that this could happen both when training the model and when training the SAE; it is therefore unclear whether the substructures we see now are primarily due to the SAE training.

Additionally, the neighbors within the same low-dimensional substructure does not show much correlation with each other, suggesting that correlation is not the main driver of squeezing.

![corrlation.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/corrlation.png)

Here I plot the feature occurrence correlation for the nearest neighbors for random features in low-dimensional substructures (top row), and compare that with random features not in low-dimensional substructures (bottom row). There is no substantial difference between the two populations.

![dimension_dec.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/dimension_dec.png)

Substructure formation by repulsion also explains the trend that the decoder features show even stronger squeezing (above figure). It is worth noting that here even the more frequent features are squeezed into lower dimensions. This is mainly because the encoder-decoder shift only depends on separation with neighbors and does not depend on feature frequency - it corrects the error induced by the activation of the feature itself, not the error induced by the activation of nearby features. This might also explain why the Anthropic papers, which focus on the decoder features, seem to show substantial clustering.

Finally, let’s consider neuron alignment. There is some degree of neuron alignment, which is visible from the effective neuron dimensionality

$$
D^{\rm neuron}_{i}=\sum_{j} |\hat w_{{\rm enc},i,j}|
.
$$

![neuron_dim.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/neuron_dim.png)

However, it does not explain the substructures we see because reduced neuron dimensionality is primarily seen for high-frequency features which are not in low-dimensional substructures.

Physically, neuron alignment may be related to the neurons being a privileged basis given the nonlinear layers in the model. If alignment with neurons provide some advantage (for example, in encoding feature operations in the MLP layer), it makes sense for more neuron-aligned directions to be reserved for the more frequent features. It is also worth noting that the tendency of neuron alignment only means that features are much more aligned to the neuron basis than random vectors are; however, in most cases, it still requires many neurons to explain a sufficiently large fraction of the feature vector (say, 90% of $||\hat w_{{\rm enc},i} ||^2$).

![neuron_dim_2.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/neuron_dim_2.png)

# How are correlated features embedded?

Another important aspect of feature geometry is how the relation between features affect their embedding. So far, it seems that we do not need feature correlation to explain any of the trends we observed. Now let’s look at the problem from another perspective: if we limit our attention to correlated features, what kind of structures do they form?

Some basic insights on this problem came from [Anthropic’s toy model paper](https://transformer-circuits.pub/2022/toy_model/index.html); they found that correlated features prefer to be orthogonal; and if that is not possible, positively/negatively correlated features prefer to be aligned / anti-aligned.

![mu_corr.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/mu_corr.png)

These trends are indeed seen in our feature set. The plot above shows the cumulative distribution of separation for pairs of features with different levels of correlation $r$. Indeed, all are fairly close to orthogonal, and positive/negative correlation shifts the distribution towards alignment/anti-alignment.

![mu_corr_2.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/mu_corr_2.png)

But that is not the whole picture. Inspecting these results more carefully, I realized that correlated features are not as orthogonal as they can be: the distribution of the separation from the most correlated feature is much less orthogonal than the separation from another random feature, as shown in the figure above. Why is that?

With results from the previous section, one reasonable hypothesis is that these features are less orthogonal because they form lower-dimensional subspaces. This is indeed visible if we perform a dimensionality analysis for features that are correlated with the reference feature.

![dimension_corr.png](High-dimensional%20feature%20geometry%20in%20a%20one-layer%20l%20201831dee5098033996bc02221ee3509/dimension_corr.png)

As shown by the figure above, correlated features show stronger clustering and lower dimensionality. This might be interpreted as a result of correlated features being more “squeezable” than uncorrelated features: as long as $\cos\theta$ between two correlated features has the same sign as their correlation, adding correlation reduces the error from interference and reduces the penalty of squeezing these features.

Overall, I think the findings here is mainly a null result: correlated features are not that much different from uncorrelated features, except correlation makes them slightly more prone to squeezing. Still, this could offer some interesting insights for feature extraction of low-frequency correlated features. For example, with all our understanding so far, it seems quite natural that Arabic features - which are rare but strongly correlated - form a tight cluster in [Anthropic’s one-layer model](https://transformer-circuits.pub/2023/monosemantic-features/index.html).
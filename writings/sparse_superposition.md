# Superposition of sparse features: Exponential embedding efficiency through hypersphere packing

Created: May 14, 2025 5:09 PM

# Summary

In this note, I use a toy model to investigate feature superposition in the limit of large feature sets and high sparsity. The main goal is to understand the efficiency and geometry of superposition, especially their asymptotic behaviors as model size increases. The main findings include:

- For sparse features, models tend to embed all features even when there are orders of magnitude more features than the model dimension.
- In a n-D model, features form a near-uniform lattice on the surface of a n-D hypersphere. Feature geometry can be quantitatively estimated using [hypersphere packing](https://mathworld.wolfram.com/HyperspherePacking.html) theory.
- Superposition allows models to pack more features at the cost of ignoring weak input. Interference between nearby features is exponentially suppressed in large models.
- At given error tolerance, the number of features that can be embedded increases exponentially with model dimension. (Similar results have been obtained in previous studies on compressed sensing - e.g., [Ba et al. 2010](https://epubs.siam.org/doi/pdf/10.1137/1.9781611973075.95))
- As the number of feature increases, low-dimensional models demonstrate a phase transition from non-degenerate embedding to degenerate embedding. Degeneracy can be suppressed by varying the loss function.
- Under the assumption of approximately symmetric embedding, the optimal embedding for high-dimensional ($n\gtrsim 5$) models always embed all features and always avoid degeneracy.

Results in this note can be reproduced using [this Colab notebook](https://colab.research.google.com/drive/1161Cw2_sPQwVXTCZoOmjhci3FJd6sTNq?usp=sharing).

# Motivation

Superposition is a fundamental feature of neural networks. When the input is sparse (i.e., only a small fraction of features are nonzero for each input), a low-dimensional model can noisily encode more features than its dimensions. One important observation in the [Toy Model paper](https://transformer-circuits.pub/2022/toy_model/index.html#learning) is that superposition becomes stronger as sparsity increases. Within the range of sparsity surveyed in the paper (up to $1-S\sim 10^{-2}$ for several $10^2$ features), it is unclear whether the behavior converges.

The motivation of this note is to study the asymptotic behavior of superposition in the limits of sparse input, large feature sets, and large models. Specifically, I will focus on two topics:

- The efficiency of superposition: How many features can a n-D model encode? What determines the tradeoff between embedding more features and accurately representing each embedded feature? This is important for understanding the scaling laws of large models and estimating their performance.
- The geometry of superposition: What kind of geometric structure do features form in superposition? (This refers to the geometry of embedded features in the space spanned by the model’s hidden dimensions.) This is important for feature extraction (e.g., can we extract features from only a fraction of the network’s dimensions?), for understanding the embedding of related features, and for understanding how computation takes place in the hidden layer.

To investigate these problems, I study superposition in the limit of large $n_{\rm feature}$ and high sparsity. I will first develop a toy model and obtain some numerical results at low model dimensions ($n\leq 8$). I will then use the insights from these models to motivate a theoretical framework for sparse feature embedding and obtain some asymptotic results for large models.

# Toy model setup

Here we consider the same ReLU toy model used in the Toy Model paper, which involves encoding a vector $x\in R^{n_{\rm features}}$ into a lower-dimension vector $h\in R^n$ and recovering it:

$$
x'={\rm ReLU}(W^TWx+b).
$$

For simplicity, I only consider the case when all feature dimensions are independent and equally important. In the Toy Model paper, to represent sparse features, each dimension of the input has a probability S of being zero; when it is nonzero, its value is uniformly distributed in [0,1].

For this study, I consider the limit of infinitely sparse features with $(1-S)n_{\rm feature}\ll 1$. This limit is of course not realistic; for real-world applications one should at least expect $(1-S)n_{\rm feature}\gtrsim 1$. But this could be a useful limiting case to study before we venture towards more realistic parameters. In this limit, the problem is equivalent to optimizing the model for inputs where each input has exactly one nonzero dimension under the constraint of $b_i<0~\forall i$. In practice, this is how I train the model and define the loss function.

The loss function is just the L2 loss,

$$
l= \sum_{i}^{}(x_i'-x_i)^2.
$$

I will also experiment with different loss functions later in this note.

To survey the different outcomes in the limit of large $n_{\rm feature}$ (more specifically, large $n_{\rm feature}/n$), I train the model for $n_{\rm feature}$ between 4 and 1024 and $n\in \{2,3,4,6,8\}.$

# Results

## Models tend to embed all features, sometimes with degeneracy

One original motivation of this work is to study how many features a model can embed before it decides to ignore additional features. To my surprise, across all parameters I surveyed (up to 1024 features), the model always tries to embed all (or nearly all) of them.

[A technical note: Here a feature is “embedded” means that input in this feature dimension can generate nontrivial output. Mathematically, a feature $i$ is embedded if $|W_i|^2+b_i>0$. Note that for our sparse models, the bias $b_i$ is always ≤ 0.]

To understand how this takes place, let us first focus on the 2D models. The figure below visualizes the weights and responses of the models. In the top panels, each marker corresponds to the weight vector $W_i$ of a feature; within the same panel, all weight vectors have the same opacity, and degeneracy results in darker colors. In bottom panels, we plot $x_i$ vs. $x_i'$ when the input is nonzero in feature $i$.

![superposition_2d.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/superposition_2d.png)

Below I make a similar plot for 3D models. The only difference is that the top panels now show the directions of weight vectors for embedded features projected to 2D, and we only show features whose weight is positive in the third dimension. This can be understood as projecting the directions of weight vectors onto the unit sphere and taking a front view.

![superposition_3d.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/superposition_3d.png)

These low-dimensional models exhibit a few interesting trends:

- As the number of features increases, the model first tries to embed the features non-degenerately as additional directions, but eventually begins to embed new features degenerately.
- The directions of the embedded features form a nearly uniform lattice.
- As the model becomes more degenerate, the response of the model becomes weaker.

Below I will discuss these trends, especially whether they persist in higher dimensions, using more detailed diagnostics.

[A note on the 2D model at $n_{\rm feature}=128$: This model is different from nearby models in the group, because the model settles into a sub-optimal local minimum. Later in this note I will show that the gain (the improvement of loss function compared to not embedding any feature) of this model is lower than other models in this group.]

## A phase transition from non-degenerate to degenerate packing

Now let’s more systematically analyze the feature packing and the emergence of degeneracy. In the figure below, I plot the distribution of the angular separation between each embedded weight vector and its nearest neighbor, $\theta_{\rm min}$; a separation $\theta_{\rm min}=0$ corresponds to degeneracy.

![theta_min.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/theta_min.png)

For all models, increasing $n_{\rm feature}$ first causes the model to pack more features without degeneracy while decreasing $\theta_{\rm min}$. For $n=2,3,4$, there is eventually a phase transition into degenerate packing. Later on I will discuss whether this phase transition also exists for models with higher dimensions.

![multiplicity.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/multiplicity.png)

The above plots show how the number of directions and the average multiplicity of degenerate directions evolve for 3D and 4D models. The 3D model clearly demonstrate the phase transition; the 4D model is overall similar, but we do not have a clear view into the degenerate regime since I only surveyed $n_{\rm feature}$ up to 1024.

![amplitudes.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/amplitudes.png)

The above figure summarizes the amplitudes of weight vectors in the 3D and 4D models. Two trends are worth nothing: First, in the non-degenerate regime, weight vectors in the same model have nearly uniform amplitudes, which increases with $n_{\rm feature}$. Second, in the degenerate regime, each set of degenerate weight vectors tend to have the same amplitude, and it negatively correlates with multiplicity.

Interestingly, for 2D models the degenerate weight vectors show a different amplitude distribution where one vector tends to have large amplitude and the remaining ones share a uniform but much smaller amplitude. This is probably a unique feature of 2D that does not generalize to higher dimensions.

## Feature geometry: a lattice on hypersphere surface

As we have mentioned previously, when the embedding is non-degenerate, the weight vectors of all embedded features tend to have approximately the same amplitude; in other words, for a n-D model they lay on the surface of a n-D hypersphere. We also know that within the same model, the distance to the nearest embedded feature is approximately the same for all embedded features (see $\theta_{\rm min}$ plot earlier), suggesting that they form an approximately uniform lattice. This could be a natural consequence of minimizing interference by maximizing the separation between nearby features, similar to a high-dimension version of the Thomson problem.

![theta_distribution.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/theta_distribution.png)

The figure above shows the distribution of the separation between all pairs of weight vectors of embedded features for one of our models. Overall, it resembles the distribution for uniformly distributed directions on the n-D hypersphere surface (blue line). We can also see deviation from this uniform distribution due to the weight vectors developing a lattice pattern in attempt to maximize $\theta_{\rm min}$. Specifically, all features that would be at a smaller theta are now packed near $\theta_{\rm min}$, creating a peak there. We also see some additional, more diffuse peaks, and those likely correspond to second and third neighbors on the lattice (i.e., points with Manhattan distance 2 and 3).

It is worth noting that the features do try to spread over the whole hypersphere surface, as opposed to self-organize into lower-dimensional objects. (If they did, the $\theta$ distribution would have a strong peak at $\pi/2$.) This is in contrast to the low-sparsity behaviors observed in the Toy Model paper, where features tend to organize into low-dimensional polygons. This difference highlights the importance of extending our understanding of superposition into the sparse limit. This also calls for a more detailed investigation on how the preferred dimension of packing scales with sparsity and whether there is a phase transition from partitioning into smaller subspaces (e.g., low-dimensional polygons) and using all dimensions.

## Model response: trading sensitivity with more features

Now let’s turn to the response pattern of the model. Here I mainly provide some qualitative intuitions; a more quantitative analysis is left to the theoretical framework later in this note.

In the degenerate packing regime, the model response becomes weaker (reduced weight vector amplitude and model output) at increasing multiplicity. This result is easy to understand, as degenerate embedding at uniform amplitudes means that the model gives the same output in all degenerate dimensions; as multiplicity increases, the model favors weaker outputs for it generate less errors on the degenerate dimensions other than the input dimension.

In the non-degenerate regime, we see a different trend: as $n_{\rm feature}$ increases, the response becomes steeper and the intercept on the input axis (i.e. the minimum input that is not fully suppressed by the bias) also increases. A good example is the response for 8D models below.

![intercept.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/intercept.png)

This behavior can be interpreted as a result of avoiding interference between adjacent features. For a nearly symmetric embedding (i.e., all features have similar amplitudes, biases, and $\theta_{\rm min}$), an intercept of $\cos\theta_{\rm min}$ is sufficient to suppress all interference between adjacent features. In general, the nature of the L2 error means that the optimize setup is always an intercept that is slightly smaller than $\cos\theta_{\rm min}$; however, since the number of adjacent neighboring points on a lattice increases exponentially with lattice dimension, as $n$ increases the optimal intercept should quickly converge towards $\cos\theta_{\rm min}.$

The notion of an intercept at $\approx\cos\theta_{\rm min}$ is consistent with our model results. Note that in 8D the intercept still lies below $\cos\theta_{\rm min}$ by a noticeable amount, because in this case the number of neighbors of each feature is not still too large - considering spherical packing in $n-1=7$ dimensions yields $\sim 10^2$ neighbors.

One interesting implication is that **in the non-degenerate regime and large $n$, interference remains negligible no matter how many features are packed**. New features are embedded only at the cost of ignoring weak inputs.

## Inefficient training at degenerate packing

Another interesting observation is that in the degenerate regime the model often end up in a suboptimal local minimum, which suggests inefficient training.

![training_inefficiency.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/training_inefficiency.png)

The figure above shows the net gain of the models, defined as

$$
g\equiv (l_0-\bar{l})n_{\rm feature}.
$$

Here $\bar{l}$ is the average loss, and $l_0=1/3$ represents the loss of not embedding any feature. This gain function is designed so that it stays the same when we add unembedded new features. As a result, for optimal embedding, when $n_{\rm feature}$ increases, gain should be non-decreasing. This provides a sufficient (but not necessary) criterion of suboptimal embedding: if there exist any embedding with smaller $n_{\rm feature}$ and larger gain, the embedding has to be suboptimal. Following this criterion, we can see that the 3D and 4D models show clear sign of suboptimal embedding as soon as degeneracy develops. As a side note, the 2D model with 128 features, which shows a hexagon pattern qualitatively different from nearby models, is also suboptimal.

The suboptimal results suggest that training may be inefficient in the degenerate regime. I conjecture that this could be associated with the existence of many local minima. The multiplicity of a degenerate feature is quantized (as it needs to be an integer), and for each multiplicity there could be a local minimum of the loss function. This web of local minimum could trap the model before it reaches the global minimum.

## Changing loss function can suppress degeneracy

Overall, degeneracy appears to be an undesirable behavior since it makes training less efficient and, in the limit of high degeneracy, leaves all features essentially useless because the response is always very weak. So, is there any way to avoid this behavior?

Fundamentally, degeneracy arises because having multiple features at large error is still better than accurately embedding a single feature but ignoring the rest. This is related to the property of the L2 loss function, which provides a strong incentive to improve the least accurate results (the ignored features).

![huber.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/huber.png)

It is therefore reasonable to expect the behavior to change at a different loss function. In particular, degeneracy should reduce when we switch to a loss function with less prioritization on reducing large errors. In the figure above, I consider a Huber loss function with varying $\delta$; this becomes a L1/L2 loss at $\delta=0/1$. As $\delta$ decreases, there is a phase transition from degenerate packing of nearly all features to non-degenerate packing. Further reducing delta causes the model to prefer embedding fewer features.

It would be useful to think a little more about how this relates to real-world applications. For many real-world applications, we can only tolerate error up to a certain amount; beyond that, the result is useless so it is as bad as (if not worse than) simply ignoring the input. For example, in networks that do multiple steps of computation, the amplification of error may effectively set an critical error for each stage beyond which the final result will be significantly corrupted. Therefore, if we want to use this kind of toy model as an abstraction of, say, one layer of a large model, it is beneficial to consider a loss function other than L2, or even a loss function that behaves like L2 near zero but flattens out beyond a certain point (e.g., 1-Gaussian), and study how superposition is affected by the critical error of the loss function.

# A theoretical framework of sparse feature embedding in high dimensions

## Assumptions

The results in the previous section motivates a simple model for sparse feature embedding. It is worth stressing that this model is more of a tool for building intuition, as opposed to a rigorous mathematical proof. The key assumption of this model is that features are packed in an approximately **symmetric** way; this means

- All embedded features have the same multiplicity;
- All embedded features have the same weight vector amplitude and bias;
- The directions of weight vectors (or degenerate groups of weight vectors) of embedded features form a uniform lattice, where the separation between adjacent directions, $\theta_{\rm min}$, is approximately constant for all directions.

These assumptions are all consistent with our model results at $n>2$. One caveat is that for multiplicity we do tend to see some finite spread within a given model; it is unclear whether this will lead to any significant problem of this model.

I also take the approximation of large $n$ when necessary. Specifically, this means keeping only the leading order $n$ dependence and ignoring any perturbations that vanishes in the $n\to\infty$ limit.

With these assumptions, let’s calculate the optimal gain functions when a model embeds $n_{\rm embed}$ features at degeneracy $n_{\rm deg}$ in $n_{\rm dir}=n_{\rm embed}/n_{\rm deg}$ directions.

## Lattice embedding: $\theta_{\rm min}$ scaling

First let us work out the separation of the lattice, $\theta_{\rm min}$, in a n-D model when the lattice consists o $n_{\rm dir}$ directions. This is equivalent to packing (n-1)-D hyperspheres with radius $\approx\theta_{\rm min}/2$ on the surface of a n-D hypersphere. In the limit of small $\theta_{\rm min}$, this is equivalent to the classic problem of hyperspheres packing in Cartesian space at (n-1)-D. To lowest order in $\theta_{\rm min}$, this gives

$$
n_{\rm dir}(\theta_{\rm min}/2)^{n-1}V_{n-1} = \delta_{n-1} S_{n-1}.
$$

Here $V_n$ is the volume of a unit n-hypersphere, $S_n$ is the surface area of a (n+1)-hypersphere, and $\delta_n$ is the efficiency of hypersphere packing in n-D.

[A note on small-$\theta_{\rm min}$ approximation: Since the hypersphere surface is not exactly Cartesian across finite angular span, the above result could slightly underestimate $\theta_{\rm min}$. One can also obtain an upper bound of theta by replacing $\theta_{\rm min}/2$ with $2\sin(\theta_{\rm min}/4)$. These two bounds are at most 10% different.]

$V_n$ and $S_n$ have simple analytic forms; for $\delta_n$, hypersphere packing in arbitrary dimension is generally an unsolved problems but there are (1) exact result for a number of dimensions (1~8 and 24), and (2) upper and lower boundaries in large-n limit which constrains delta to ~ factor of 2. (See [this page](https://mathworld.wolfram.com/HyperspherePacking.html) and references therein.) Specifically, delta can be described using the [Hermite constants](https://mathworld.wolfram.com/HermiteConstants.html) $\gamma_n$, which are defined by

$$
\gamma_n = 4\left(\frac{\delta_n}{V_n}\right)^{2/n}
$$

A simple estimate is that $\gamma_n/n\sim1/2\pi e$, with the prefactor on the RHS between 1 and 1.744 at large $n$. Using this together with the formula for hypersphere surface area

$$
S_{n-1}=\frac{2\pi^{n/2}}{\Gamma(n/2)},
$$

and adopting Stirling’s approximation, we get the following relation:

$$
\frac{n_{\rm dir}}{\sqrt{2}}\sim\left(\frac{\sqrt{\xi}}{\theta_{\rm min}}\right)^{n-1},
$$

where $\xi$ is an order-unity parameter defined by

$$
\xi\equiv \frac{2\pi e\gamma_{n-1}}{n-1} \in [1,1.744] ~~{\rm at~large}~n.
$$

This result gives some very interesting implications:

- At a given $\theta_{\rm min}$, as model dimension increases, the number of features that can be packed increases exponentially; the rate of this exponential increase depends on $\theta_{\rm min}/\sqrt{\xi}$, which in practice may be related to the error tolerance of the problem.
- For large $n$, as long as $n_{\rm dir}$ is below some exponentially large number, $\theta_{\rm min}$ is not very sensitive to $n_{\rm dir}$ and stays around $\sqrt{\xi}$. This means:
- As long as $n_{\rm feature}$ is below some exponentially large number, the model can non-degenerately embed all features at reasonable accuracy (i.e., order-unity gain per feature) even when there are many more features than model dimensions.
- As long as $n_{\rm feature}$ is below some exponentially large number, adding new feature barely affects $\theta_{\rm min}$; this may explain the tendency for models to pack more features (see following section).
- There may a very hard limit on much sensitivity a model in superposition can have: input below $\cos\theta_{\rm min}$ will generally by be ignored, whereas $\cos\theta_{\rm min}>\cos\sqrt{\xi}>\cos\sqrt{1.744}=0.248$. (Note that this number is just a rough approximation due to the small-$\theta_{\rm min}$ approximation adopted earlier.)

## Loss function: Why packing all features? When is degeneracy preferred?

Now let’s quantitatively model $W, b$, and the loss function. For a given feature (and all its degenerate peers), the output of the model is described with a ReLU-like profile with intercept $-b_i/|W_i|^2$ and slope $k=|W_i|^2$. Since there are exponentially many neighbors at large $n$, the optimal intercept asymptotes to $\cos\theta_{\rm min}$ - i.e., no interference between features.

Minimizing the loss function at given $n_{\rm deg}$ and $\theta_{\rm min}$ gives

$$
k=\frac{1}{1+n_{\rm deg}}\frac{1+(\cos\theta_{\rm min})/2}{1-\cos\theta_{\rm min}},
$$

When the input is in an embedded direction, the average loss function is given by

$$
\bar l_{\rm embed} = \frac{1}{12}\frac{1}{n_{\rm deg}+1}(4n_{\rm deg}+3\cos^2\theta_{\rm min}+\cos^3\theta_{\rm min}).
$$

An the total gain is

$$
g\equiv(l_0-\bar l)n_{\rm feature}=(l_0-\bar l_{\rm embed})n_{\rm embed}\\=\frac{1}{12}\frac{n_{\rm embed}}{n_{\rm deg}+1}(4-3\cos^2\theta_{\rm min}-\cos^3\theta_{\rm min}).
$$

The figure below shows the gain for various $n_{\rm embed}, n_{\rm deg}$ and $n$. The location where $n_{\rm deg}=1$ becomes less optimal than $n_{\rm deg}=2$ (marked by red vertical line) serves as a good estimate of the phase transition to degeneracy in our toy models. We can also see that the $n=2,3$ results seem qualitatively different from the higher $n$ results, which serves as a caution that insights from toy models at very low dimension may not always generalize into higher dimensions.

![analytic_gain.png](Superposition%20of%20sparse%20features%20Exponential%20embed%201f3831dee5098038bdddff7cb4987d36/analytic_gain.png)

For large $n$ and $n_{\rm feature}$ values not directly accessible in our models, analyzing the derivatives of $g$ helps us understand how the model determines whether to embed more features and whether it does so in degeneracy. Our previous analysis on $\theta_{\rm min}$ gives

$$
\frac{\partial\log\theta_{\rm min}(n_{\rm embed}, n_{\rm deg})}{\partial\log n_{\rm embed}} = -\frac{1}{n-1},~~~\frac{\partial\log\theta_{\rm min}(n_{\rm embed}, n_{\rm deg})}{\partial\log n_{\rm deg}} = \frac{1}{n-1}.
$$

To lowest nontrivial order in $\theta_{\rm min}$, we have

$$
\frac{\partial g(n_{\rm embed}, n_{\rm deg})}{\partial n_{\rm embed}} \approx \frac{9}{24}\frac{1}{n_{\rm deg}+1}\left(1-\frac{2}{n-1}\right)\theta_{\rm min}^2.
$$

We can immediately see why $n=2,3$
 are different: these are the only cases where $g$ does not always increase with $n_{\rm embed}$. **For models with $n>3$, it is always advantageous to embed more features.**

Meanwhile, the derivative with respect to multiplicity is

$$
\frac{\partial g(n_{\rm embed}, n_{\rm deg})}{\partial n_{\rm deg}} \approx \frac{9}{24}\frac{n_{\rm embed}}{n_{\rm deg}+1}\left(\frac{2}{n_{\rm deg}(n-1)}-\frac{1}{n_{\rm deg}+1}\right)\theta_{\rm min}^2.
$$

For $n>5$, $\partial g/\partial n_{\rm deg}<0$ for all $n_{\rm deg}\geq 1$. In other words, **models with $n>5$ always prefer non-degenerate packing over degenerate packing**. This is consistent with our numerical results, though one may need to survey much larger $n_{\rm feature}$ values before using that as a strong empirical evidence for this.

# Questions for future studies

## Probing the boundaries of hyperspherical geometry

The main finding in this study is that features in a n-D model tend to pack into a near-uniform lattice on the surface of the n-D hypersphere; for large n and L2 loss function, the model always embed all features and always do so without degeneracy.

To understand whether this regime is relevant to real-world applications, it is important to understand how these results generalize to finite sparsity and different loss functions:

**Finite sparsity:** In real-world examples, we roughly expect $(1-S)n_{\rm feature}$ to be $\gtrsim 1$ but still $\ll n$. Does this affect the behavior? Intuitively, having $\mathcal{O}(1)$ coexisting features may be fine since they are unlikely to be neighbors in the embedding. But accurately determining the condition when the spare assumption breaks down requires future studies.

Previous studies on compressed sensing (e.g., [Ba et al. 2010](https://epubs.siam.org/doi/pdf/10.1137/1.9781611973075.95)) could also be quite relevant to this topic, though one key difference is that their problem requires minimizing the maximum error whereas for typical LLM applications we care more about mean error; having very few (perhaps exponentially few) outliers is usually acceptable. This may lead to different optimal configurations.

**Different loss functions:** As discussed earlier, in some real-world applications we can only tolerate a finite amount of error (e.g., when this toy model just represents one layer of a large model). How does the embedding dynamics change in that case? My conjecture is that setting a characteristic error tolerance limits the minimum $\theta_{\rm min}$ below which the model stops embedding additional features.

## How are feature importance/correlations/operations embedded in high dimensions?

The original Toy Model paper touched on the subject of feature importance and correlation shaping the geometry of embedding. One natural questions to ask is to what extent these results generalize to higher model dimensions and sparse features.

A key difference between high and low $n$ is that in high dimensions the interference between features is much weaker; therefore, it may be much easier to handle correlated features.

On the other hand, it is no longer clear whether feature importance could cause it to occupy a larger volume. At high $n$, since the volume of the (n-1)-D hypersphere taken up by each feature increases rapidly with $\theta_{\rm min}$, it may become uneconomic to increase $\theta_{\rm min}$ for more important features.

Another direction that requires better understanding is how operations are embedded in superposition. The Toy Model paper touched on this subject by considering abs() as an example of a nonlinear function. However, the limitation of this choice is that it is a in-place operation whereas in reality features interact a lot with each other; to some extent we can view the features as functions and the model is just doing a reduction in lambda calculus. So, how does the geometrical structure of the features, as described by how they interact with each other, affect the embedding? I find this to be a very interesting direction, though designing an appropriate test problem could be challenging.

## Real-world implications of hyperspherical geometry

**Do we see spherical geometry in models for real-world applications?** Perhaps the simplest test to understand whether our intuition from the toy model is relevant is to check how models trained for realistic tasks embed features and whether that resemble the hypersphere layout in the toy models. For example, one may take a feature extraction result and map the features back to the original network, and study the distribution of the angular separation between these features; do they show the near-uniform lattice we saw for toy models?

**Feature extraction:** This work suggests that an efficient model would use all its dimensions for all the features; there is generally no low-dimensional subspaces that embed subsets of features. This sounds like bad news for feature extraction, as it means that feature extraction can only be done globally; for example, one probably cannot use a subset of a layer to perform feature extraction. On the other hand, one interesting possibility is that the this spherical embedding may also be somewhat holographic, in that a subset of the dimensions may already noisily encode the whole embedding. If this is the case, it may have some interesting implications for efficient feature extraction and model distillation.

**Model robustness:** Similar to the discussion above, the spherical embedding offers two opposite intuitions. On the one hand, since superposition makes use of all dimensions simultaneously, no part is left untouched if we perturb one of the dimensions (either in input or in the model). On the other hand, since all dimensions are used, the effect of perturbing - or even eliminating - one of the dimensions may be quite limited. Which of these are more correct? The fact that the human brain works quite well despite neurons randomly dying or malfunctioning may suggest a good amount of robustness, and it will be fun to demonstrate similar robustness in an artificial neural network with strong superposition.

**Scaling laws:** The number of sparse features that can be embedded with a given accuracy requirement scales exponentially with model size. But why do real-world model performance tend to show more power-law scalings? Does this just imply that superposition is not the bottleneck of model performance for any sufficiently large model, or are there additional considerations (e.g., error tolerance, feature interactions) that eventually reduce this exponential scaling to a power-law?
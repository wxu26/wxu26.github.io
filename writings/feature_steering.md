# Model steering with SAE features: In-place unlearning and reducing interference

Created: June 7, 2025 2:56 PM

# Summary

In this note, I train a small transformer that predicts Shakespeare scripts, extract features from its residual stream using a sparse autoencoder (SAE), and explore how these features can be used for model steering through a simple unlearning test. Below are the main takeaways:

- Compared to perturbing a feature in the SAE, perturbing the feature in-place (in the residual stream) significantly reduces evaluation cost and slightly improves performance.
- A linear perturbation to feature amplitude is sufficient for unlearning, but it tends to cause significant performance drop in semantically related non-target contexts (semantic interference).
- Semantic interference is more important than geometric interference: perturbing a feature affects semantically related contexts more than contexts that activate neighboring features in latent space.
- Interference can be significantly reduced when I use a feature activation criterion to turn off perturbation in non-target context.
- The same semantic concept can be encoded by multiple features, and strong perturbation on a subset of them is sufficient for unlearning. For semantic concepts encoded by multiple features, controlling perturbation with a multi-feature criterion could reduce interference.

# Motivation

Several recent works have demonstrated the ability of SAEs to extract interpretable and largely monosemantic features from language models (e.g., Anthropic’s [towards monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html) and [scaling momosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) papers) and the potential for model steering through manipulating feature amplitudes in the SAE (e.g., [Farrell+2024](https://arxiv.org/abs/2410.19278), [Khoriaty+2025](https://arxiv.org/abs/2503.11127)).

However, before steering with SAE feature can be applied at production level, there are two challenges that we need to overcome. One is computational cost: SAEs are expensive to run. For typical hyperparameters, the ratio between the cost of evaluating the SAE and evaluating the model is of order $\mathcal O(n_{\rm feature}/n_{\rm layer}n_{\rm model})$ where $n_{\rm feature}$ is the number of features, $n_{\rm model}$ is the dimension of the residual stream, and $n_{\rm layer}$ is the number of layers in the language model. Since the number of features can scale exponentially with model size, for large models the SAE will be much more expensive to evaluate than the model itself. This limitation may be overcome by perturbing the model in-place; instead of evaluating the the whole SAE, we may only evaluate the activation of the features we want to steer and perturb the residual stream according to these activations. (This only helps with inference cost, and training the SAE is still necessary and costly. Still, this could mean significant saving in practice as training is only a one-time cost.) In theory, this should be quite trivial to accomplish.

A bigger challenge is interference. Neural networks encode large number of features through superposition, where features can be conceptualized as vectors in the $n_{\rm model}$-dimensional activation space that are not fully orthogonal with each other. It seems inevitable that perturbing a feature will have some impact on its latent-space neighbors. In particular, as the nearest neighbors of a feature is often something completely unrelated, manipulation of a feature may lead to unpredictable consequence on the model’s response to unrelated contexts. However, the situation is not completely hopeless. As discussed in [my previous notes](https://wxu26.github.io/projects/feature_geometry/index.html), superposition is very efficient in high dimensions, and features can remain largely orthogonal with their nearest neighbors despite strong superposition. So perhaps this geometric interference is not that strong. Characterizing the level of interference and exploring how to avoid it is another goal of this note.

# Language model preparation

To construct a toy problem that is small enough to fit into my GPU and still preserve some complexity of language models, I train a transformer on [40,000 lines of Shakesphere plays](https://www.kaggle.com/datasets/thedevastator/the-bards-best-a-character-modeling-dataset/) to predict the next character using the preceding 1-256 characters. (For simplicity, the text is embedded at character level; there are only 66 unique characters in this dataset.) The model has 6 layers and a residual stream dimension of 256.

Other details of the model architecture and training are documented in [this notebook](https://github.com/wxu26/SAE_unlearning/blob/main/train_model.ipynb).

At the end of the day, the model achieves a cross entropy loss of 1.64 and an accuracy of 45.3% on the test set. To provide a broad impression of the model’s behavior, below is a passage generated by the model:

![Screenshot 2025-06-08 at 7.21.27 PM.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/Screenshot_2025-06-08_at_7.21.27_PM.png)

The generated text is still largely meaningless, but we can see that model does pick up the basic format, many words, and some grammar.

# Feature extraction with SAE

Next let’s try to identify some features of the model. I train two SAEs on the residual stream of the model, one after layer 3 (L3) and another after layer 6 (L6). The sparse autoencoders have a dimension of $n_{\rm feature}=8n_{\rm model}=2048$.

The details of training is documented in [this notebook](https://github.com/wxu26/SAE_unlearning/blob/main/train_SAE.ipynb); I largely adopted the approach in this [circuit update from Anthropic](https://transformer-circuits.pub/2024/april-update/index.html#training-saes), except that some hyperparameters have been modified to accommodate the smaller problem size.

After some training, the sparse autoencoder is able to recover most of model performance; the L3 model has a residual stream relative MSE of 0.022 and recovers 94.1% of the cross-entropy loss; the L6 model has a residual stream relative MSE of 0.098 and recovers 92.0% of the cross-entropy loss. The two SAEs are trained with identical hyperpatameters, but half of the features (1017/2048) are dead in the L3 model whereas the L6 model has only 2 dead features. This differences is probably because the L6 residual stream contains more features than the L3 residual stream; this is consistent with the notion that each layer writes new information to the residual stream.

Both layers yield plenty of interpretable features. For example, here is a feature that mainly adds the line break after a character name:

![Screenshot 2025-06-08 at 7.25.59 PM.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/Screenshot_2025-06-08_at_7.25.59_PM.png)

In the visualization above, I randomly draw a sample of contexts where the feature is active, and sort them by feature activation. Black font is the context used for prediction. Correct predictions are marked in cyan, and incorrect predictions are marked in red followed by the correct answer in cyan.

# Experiment design

To experiment with feature-based steering, I construct a simple unlearning task. Given a feature that activates on a certain context (”target context”), I want to manipulate the feature so that the model no longer makes the correct prediction in this context but still maintain its original performance for other contexts. The result will be evaluated using the accuracy and cross-entropy loss in target and non-target contexts. For each feature, I will try the following methods:

- SAE linear perturbation: The amplitude of the target feature t, $f^{(t)}$, is multiplied by a linear factor $1+\delta$. Intuitively, $\delta <0$ should suppress the feature. The modified SAE ($x\to x'$) is now given by
    
    $$
    f = {\rm ReLU}(W_{\rm enc}x+b_{\rm enc}),\\
    f^{(t)}=f^{(t)}(1+\delta),\\
    x' = W_{\rm dec}f + b_{\rm dec}.
    $$
    
- In-place linear perturbation: This is a simple modification to the scheme above that avoids the use of the full SAE. To save computational cost, I only compute the feature amplitude for the target $f^{(t)}$, and then add the perturbation to the residual stream.

$$
f^{(t)}={\rm ReLU}(W_{\rm enc}^{(t)}x+b^{(t)}_{\rm enc}),\\
x' = x+\delta f^{(t)}W_{\rm dec}^{(t)}.
$$

- In-place nonlinear perturbation: The linear perturbation $\delta f^{(t)}$ is further generalized to some nonlinear function of $f^{(t)}$. The exact format will be discussed later.

# Single-feature manipulation: unlearning “thou”

For this experiment, I focus on feature L6/923. This feature mainly predicts the “u” in “thou”:

![Screenshot 2025-06-08 at 7.35.52 PM.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/Screenshot_2025-06-08_at_7.35.52_PM.png)

The activation of this feature strongly correlates with the predicting-“u”-in-“thou” context, with a correlation of 0.88. This feature is ideal for my experiment for several reasons. First, the model has great baseline performance on this context: the accuracy for predicting “u” in “thou” is >95% even though the overall accuracy of the model is only ~45%. Additionally, L6/923 is the only feature that strongly correlates with this context; the highest correlation from other features is only 0.42. Finally, there exists several alphabetically similar contexts (”though”, “without”, etc.) that can serve as a good test for interference on semantically related contexts.

### SAE linear perturbation

![L6_SAE.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L6_SAE.png)

Performing a linear perturbation on the feature amplitude yields the above result. Here I consider the accuracy and loss on several different contexts:

- Target: predicting “u” for “thou”. Note that here “thou” needs to be a full word - I only consider contexts where the characters before and after “thou” or “Thou” are both non-alphabetic.
- Near miss: predicting the letter after “tho” or “Tho”, but not in the target context. Examples of this includes “though”, “without”, and “those”. Note that the correct prediction could still be “u”.
- Latent space neighbors: inputs that produce activation on the 5 nearest features that are closest to L6/923 in terms of angular separation in the latent space.

The goal is to decrease performance on target (red) while preserving (if nor increasing) performance on other contexts.

When $\delta$ takes a sufficiently large negative value, the model successfully unlearns the target. The overall performance of the model, including the performance on latent space neighbors, is also not significantly affected. This agrees with my earlier conjecture that near-orthogonality between features causes interference to be insignificant during feature manipulation.

However, one key limitation remains: the near-miss contexts are significantly affected, and by the time the model unlearns the target, it also unlearns all these near-miss contexts. It is somewhat surprising that the near-miss contexts are affected more than the latent space neighbors, as geometrically the near-miss contexts should be less affected. One possibility is that the target feature is still used in some way in these near-miss contexts. Indeed, in these near-miss contexts, the target feature is activated 94.6% of the time.

Another interesting trend is that fully suppressing the feature (i.e., achieving near-zero target accuracy) actually requires a $\delta$ that’s slightly further below -1. In other words, even when the target feature is zeroed ($\delta=-1$), some other features in the model still want to make the correct prediction - for example, some features may have learned that “o” is often followed by “u”.

These observations suggest that features can show complex coupling. Even for a highly monosemantic feature, other features may be used in its target context and it may be used outside of its target context, creating a source of semantic interference. For feature manipulation, semantic interference is probably a bigger challenge than geometric interference (i.e., interference between latent space neighbors).

### In-place linear perturbation

![L6_inplace.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L6_inplace.png)

Now let’s switch to in-place linear perturbation. The performance is overall the same. This result is quite intuitive, as the difference between the SAE linear perturbation and the in-place linear perturbation is simply the error of the SAE, which is quite small anyway. And by recovering this error, the in-place model actually performs a few percent better. This is quite encouraging for deploying SAE-based feature steering technique in production.

### Digression: a note on encoder-decoder misalignment

Now that we inject the perturbation in-place, one may question whether the misalignment between encoder and decoder vectors should be kept. For this feature, the difference between the two is actually quite significant - their cosine similarity is only 0.68. As discussed in [my previous note](https://wxu26.github.io/projects/feature_geometry/index.html), the encoder vector could be a better approximation of the true feature. Indeed, rotating encoder to align with decoder (figure below) causes a significant performance drop for latent space neighbors.

![L6_inplace_dec.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L6_inplace_dec.png)

On the other hand, rotating the decoder to align with the encoder barely impacts performance. Since eliminating the misalignment does not noticeably improve the model, I choose to stick to the original encoder and decoder vectors for convenience.

### In-place nonlinear perturbation: adding activation threshold

Now let’s see if going beyond a linear perturbation can help us reduce the semantic interference that impacts the near-miss context. This may be done If we could better distinguish between target feature activation in target and non-target contexts. It turns out that some improvement can be made by making a cut based on target feature activation.

![L6_activation.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L6_activation.png)

As shown in the figure above, target feature activation shows a bimodal distribution, where the activation in target context is separated from target feature activation in other contexts. Motivated by this observation, I insert another factor to turn on the perturbation only after the activation pass a threshold of $f_0^{(t)}=6$: 

$$
f^{(t)}={\rm ReLU}(W_{\rm enc}^{(t)}x+b^{(t)}_{\rm enc}),\\
\xi={\rm ReLU}(f^{(t)}-f_0^{(t)}),\\
x' = x+\delta\xi f^{(t)}W_{\rm dec}^{(t)}.
$$

![L6_inplace_nl.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L6_inplace_nl.png)

With this nonlinear perturbation, the performance on the near-miss context improved significantly. Now, when the target has been unlearned, the near-miss accuracy remains above 20%; this is a lot better than the near-zero accuracy before.

There are many ways to achieve the same effect; one may, for example, replace $\xi$ with a step function or simply replace the $f^{(t)}$ in linear perturbation by ${\rm ReLU}(f^{(t)}-f^{(t)}_0)$. But generally speaking, using a ReLU factor is a good default choice as it is continuous across the threshold and strictly zero below the threshold. It also easily generalizes to multi-feature steering, as demonstrated in the next section.

It should be noted that even with this improvement, the near-miss accuracy is still way lower compared to the original model. This is likely because the model is inherently unable to distinguish between “thou” and other “thou*” words (mainly “though” and “thought”), and unlearning one necessarily affects the other. To be more precise, my target feature L6/923 is really a “thou*” feature; it responds equally strongly to “thou” and “thou*”. I originally identified it as a “thou” feature mainly because “thou” is much more common than “thou*” in the corpus. The model’s inability to distinguish between “thou” and “thou*” is also supported by the observation that when it predicts the next character after seeing “thou”, it almost always predicts a space. For example, below is a random sample of predictions (by the original model) on “thou*” words - the model basically (incorrectly) assumes that all of them are “thou”.

![Screenshot 2025-06-08 at 9.00.58 PM.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/Screenshot_2025-06-08_at_9.00.58_PM.png)

Meanwhile, the remaining 20% accuracy comes from the predictions for “*thou*” words like “without”. It is much easier for the model to distinguish between “thou” and “*thou*” by checking whether the character before “thou” is a letter.

This serves as a good example of an inherent limitation of feature-based model steering: the granularity of steering cannot exceed the granularity of the features themselves.

# Multi-feature manipulation: Petruchio vs Lucentio

When inspecting L3 features that produces accurate predictions when activated, I came across a group of features associated with predicting the “c” in two names, Petruchio and Lucentio. (These names are from *The Taming of the Shrew*.) I found four features that correlate strongly with the occurrence of these names; interestingly, there is no single feature that activates only at one of these two names; all features that strongly correlate with them activate at both, although they seem to show slightly different preference between the two.

![Screenshot 2025-06-08 at 8.25.57 PM.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/Screenshot_2025-06-08_at_8.25.57_PM.png)

The origin of four distinct features that encodes two names in some mixture is an interesting problem, and I have some speculations on why this happens. The existence of multiple semantically identical features might be common in general if it encodes something sufficiently important. (This is also seen among other high-frequency and high-accuracy features, particularly those predicting line breaks and spaces.) This makes sense from the perspective of reducing superposition-induced error - when features are sufficiently sparse, having $n$ copies of a feature in distinct directions reduces the maximum superposition error by a factor of $n$. Meanwhile, the (incomplete) differentiation between these features may be a result of training dynamics; perhaps all of them started with the same semantic function (e.g., predicting “c” after “u”) but then diversified to capture additional subtleties. This diversification is probably motivated by the difference that “Petru” is always followed by a “c”, whereas “Lu” can be followed by more diverse characters.

The origin of this phenomenon aside, this set of features offer an excellent opportunity for investigating steering when strong semantic interference is present. In this case, is there a good way to unlearn one of Petruchio and Lucentio without affecting the other?

### Linear perturbation

Let’s first try the linear perturbation on each of the four features. Below I show the result of in-place linear perturbation; the SAE version gives nearly identical results.

![L3_inplace.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L3_inplace.png)

The two names remain strongly tangled. While some of the features exhibit differential suppression of the two names, it never manages to unlearn one name without significantly affecting the other. This result is not surprising as all these features respond to both names.

As a side note, while a negative $\delta$ reduces accuracy as expected, sometimes a large positive $\delta$ also reduces the accuracy. This suggests that the model responds to feature activation in a non-monotonic way. This is reasonable given that this L3 feature will be processed by three more transformer layers (which introduce a lot of nonlinearity) before output.

### Nonlinear perturbation

Now let’s try to untangle the two names though nonlinear feature perturbation. The basic idea is similar to the single-feature case: I want to find a trend in activation space that distinguishes between target (the name I want to unlearn) and non-target (the other name) and modify the perturbation accordingly. To do this, let’s take a look at how activation of each feature correlates with the two names; here red/blue/grey correspond to Petruchio/Lucentio/others:

![L3_activation.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L3_activation.png)

Among the four features, 772 and 274 show significant differential response to names, but there is still some degeneracy. Plotting these two features yield a better separation of the two names, which are now largely separated by a line.

![L3_activation_2.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L3_activation_2.png)

Motivated by this observation, we can modify the residual stream perturbation as follows:

$$
f^{(772,274)}={\rm ReLU}(W_{\rm enc}^{(772,274)}x+b^{(772,274)}_{\rm enc}),\\
\xi={\rm ReLU}[\pm(f^{(772)}-3f^{(274)})],\\
x' = x+\delta\xi (f^{(772)}W_{\rm dec}^{(772)}+f^{(274)}W_{\rm dec}^{(274)}).
$$

Here the $\pm$ sign correspond to unlearning Lucentio and Petruchio, respectively. The perturbation now only activates in the correct half of the 2D activation space.

![L3_inplace_mix.png](Model%20steering%20with%20SAE%20features%20In-place%20unlearni%2020b831dee509801fa53ad59de75b90fe/L3_inplace_mix.png)

Applying this perturbation allows the two names to be untangled fairly well.

It is also worth noting that here I only perturb two of the four features that significantly affect these names. This demonstrates that it is possible to fully unlearn a target by only perturbing a subset of its corresponding features as long as the perturbation is strong enough to compensate for the unperturbed features.
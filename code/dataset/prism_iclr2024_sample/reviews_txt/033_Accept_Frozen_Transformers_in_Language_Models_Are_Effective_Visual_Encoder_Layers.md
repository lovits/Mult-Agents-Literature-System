# Frozen Transformers in Language Models Are Effective Visual Encoder Layers

OpenReview ID: t0FI3Q66K5
Decision: Accept

## Abstract
This paper reveals that large language models (LLMs), despite being trained solely on text data, are surprisingly}strong encoders for purely visual tasks in the absence of language. Even more intriguingly, this can be achieved by a simple yet previously overlooked strategy -- employing a frozen transformer block from pre-trained LLMs as a constituent encoder layer to directly process visual tokens. Our work pushes the boundaries of leveraging LLMs for computer vision tasks, significantly departing from conventional practices that typically necessitate a multi-modal vision-language setup with associated language prompts, inputs, or outputs. We demonstrate that our approach consistently enhances performance across a diverse range of tasks} encompassing pure 2D or 3D visual recognition tasks (e.g., image and point cloud classification), temporal modeling tasks (e.g., action recognition), non-semantic tasks (e.g., motion forecasting), and multi-modal tasks (e.g., 2D/3D visual question answering and image-text retrieval). Such improvements are a general phenomenon, applicable to various types of LLMs (e.g., LLaMA and OPT) and different LLM transformer blocks. We additionally propose the information filtering hypothesis to explain the effectiveness of pre-trained LLMs in visual encoding -- the pre-trained LLM transformer blocks discern informative visual tokens and further amplify their effect. This hypothesis is empirically supported by the observation that the feature activation, after training with LLM transformer blocks, exhibits a stronger focus on relevant regions. We hope that our work inspires new perspectives on utilizing LLMs and deepening our understanding of their underlying mechanisms.

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper suggests a new paradigm for training ViTs and ViT-based multimodal Transformers, which indicates that the performance of ViTs and ViT-based multimodal Transformers can be enhanced by appending a frozen Transformer layer inherited from LLMs behind the original ViTs. Furthermore, this paper develops an information filtering hypothesis to explain how the frozen LLM transformer layer can benefit visual tasks by distinguishing the informative tokens for scenarios directly using all visual tokens and amplifying informative tokens' contributions to [CLS] token for scenarios only using the [CLS] token.

#### Strengths
- This paper is generally well-written and easy to follow.
- This paper provides detailed investigations of how and why the proposed paradigm works.
- The experimental results verified the proposed paradigm that training ViTs with frozen transformer layers inherited from LLMs is simple yet effective.

#### Weaknesses
- Method
  - The statement "we place the LLaMA transformer behind the last self-attention block in ViT" is inconsistent with Figure 1. It is unclear why the LLaMA transformer should be placed behind the last self-attention block instead of the last layer (i.e., behind the last FFN block) in ViT. Could the authors provide some insights?

- Experiments
  - Some baselines are missing. 
    - For example, it is not persuasive enough to only compare with "ViT-MLP" in Table 6, whose number of trainable parameters remains unchanged, but the total number of the parameters is significantly reduced, especially when layers of LLMs have notably more parameters than layers of ViT -Base/-Small. Therefore, an important baseline that should be added is to append frozen ViT layers behind the original ViT to keep the total number of parameters the same as "ViT-S-LLaMA."
    - Moreover, the total number of parameters, FLOPs, and throughput/latency of ViTs with the LLM layer inserted should be reported to investigate whether the proposed paradigm is more competitive than directly scaling up vanilla ViTs.
  - Some ablation studies are missing.
    - For example, append the frozen LLM layer behind prior layers instead of the last layer in ViT.
    - How does the number of the appended frozen LLM layers affect the model performance?

#### Questions
See Weaknesses.

### Review 2
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper explores the use of a transformer layer from a pre-trained large-language model as part of visual encoders. A frozen transformer block from a pre-trained LLM, typically the last block, is inserted towards the end of standard ViT based visual encoders and this layer is kept frozen throughout the visual encoder training. Experimental results across a range of vision and vision-language benchmarks are presented demonstrating the superiority of the proposed LLM-block enhanced visual encoder against the baseline visual encoder. In explanation to this phenomenon, the paper hypothesizes that LLM-blocks discern important visual information and amplify their effect, and  finally presents qualitative and quantitative results supporting such hypothesis.

#### Strengths
This paper proposes a simple approach to enhance the capabilities of many existing visual encoders for multiple tasks by just adding frozen LLM blocks with some projection layers into the training process. Experiments are presented on a breadth of image, video, 3D, visual-question answering tasks covering multiple vision problems. Hence, the approach has a broad applicability to the community.

This paper also analyzes why their method works and presents a promising hypothesis: the frozen-LLM selectively amplifies the informative tokens. Fig. 3, 4 and 5 offer evidence to this hypothesis. 

The paper is well-written and easy to follow.

#### Weaknesses
The main weakness of this paper is the choice of the baseline. 
- The proposed approach adds an additional (frozen) LLM block and (learnable) projection layers to the baseline network. So, it's unclear whether the performance improvements in Tables 1, 2, 3, 4 and 5 are just because of the increased network capacity.
- The ablation in Table 6 already demonstrates that matching the MLP parameter count already bridges some gap between the proposed method and baseline, revealing a clear inferiority of the baseline used in rest of the tables.
- More importantly, the main (implicit) claim in this paper is that the (frozen) LLM weights have some transferrable knowledge to vision tasks and they can be exploited using the proposed methodology. So, an ideal baseline to support this claim should be the same model with (learnable) weights that are randomly initialized instead of LLM weights.

Without a good baseline, the strong claims across multiple tasks are not well supported.

#### Questions
What happens to the results in Tables 1, 2, 3, 4 and 5, if we don't use the LLM weights and just use learnable random weights?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The paper proposes to incorporate frozen transformer layers from large language models (LLMs) into vision models when training the model from scratch. By evaluating this approach on a variety of vision tasks, the authors find that when the LLM layer is included, the resulting models observe a slight boost in performance. Finally, the paper proposes the information filtering hypothesis as an explanation to why this happens. Namely, the pre-trained LLM transformer layer focuses the attention and information flow on object-related tokens similar to how self-supervised models such as DINO learn semantically meaningful attention maps.

#### Strengths
- Reusing pre-trained layers from LLMs is a novel and intriguing idea that could spark further research in the direction of knowledge transfer from foundation models to more specific use cases.
- The experimental evaluation is extensive covering image classification, point cloud detection, video action recognition, motion forecasting, VQA, image retrieval. The proposed method achieves a small boost in performance across the board. The ablation study highlights some important design choices, e.g., which LLM layer to transfer.
- The information filtering hypothesis allows some insight and inspection into the reason for why this method works.
- Good writing style and presentation making the paper an easy read.

#### Weaknesses
- The experimental improvements are most of the time rather marginal with a few cases showing practical improvements. One could argue that ViT-S-MLP from Tab. 6 would be a fairer comparison for all experiments as it more closely matches the parameter count. In this case, one would expect the gap to further close.
- Some additional ablations might have been of interest.
    - Why only transfer a single LLM layer? Does it also work with more?
    - Why is the layer inserted at the end of the ViT? How does the outcome change when the layer is inserted earlier?
    - How would the results change if we instead transfer a pre-trained vision layer? (see next point)
- The transfer from a language model to a vision model is interesting and most surprising that it works. However, to generalize the approach, one could have also tested to transfer layers from other types of foundation models, e.g. vision-language models (CLIP) or self-supervised vision models (DINO). If there is a considerable gap between LLM and vision layers, one could conclude that, while it works, LLM layers might not be optimal for the domain.
- It remains an open question if this approach scales with large-scale models and training. One could expect diminishing returns as data and model allow for learning equally capable layers. This might still make this approach attractive for smaller scales so it would be interesting to know about this potential limitation. While this is difficult to evaluate, are there any indications how it might behave?

#### Questions
- Which task and dataset was evaluated for the results in Tab. 6 and Fig. 2?
- The information filtering hypothesis allows some valuable insights. At the same time, it seems to be most prominent after $F_{LM}^A$ judging by Fig. 3, but then in Fig. 4, $F_{LM}^A$ obtains a low score for ViT-B-LLaMA. Why is this the case? Which model size is evaluated in Fig. 3? Is this observation not consistent across architectures?

### Review 4
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
Previous work has shown that large language models (LLMs) that are trained only on text can be effectively sutured with visual models via simple linear layers or more complicated cross-attention modules, so as to build multi-modal vision-language frameworks.

This paper studies an interesting problem and tries to answer whether LLMs can deal with single-modal visual tasks without the help of language inputs.

A major finding of this work is that a frozen transformer block from pre-trained LLMs can be used as an effective block in a visual encoder to process visual tokens. 

The authors have verified this finding via comprehensive experiences with a variety of 2D and 3D vision tasks.

#### Strengths
- ***Scope and relevance***: Considering the growing research interest in LLMs, this paper is exceptionally timely as it broadens their application towards visual perception tasks.

- ***Significance of contributions***:  This paper proposed a straightforward yet effective approach to incorporate a frozen transformer block
from a pre-trained LLM as a general-purpose visual encoder layer that can directly process the visual tokens. 

- ***Experimental results***: The experiments in this paper are enough to prove the effectiveness of the proposed method and revealed findings.

- ***Clarity***: The main body of the paper is written very well.

#### Weaknesses
- ***Proposed hypothesis***:  The authors proposed the information filtering hypothesis to explain why pre-trained LLMs can be used for visual encoding. To verify this hypothesis, feature activations regarding both magnitudes and frequencies of features are visualized for comparison. However, visualizing feature activations or attention maps cannot explain their finding well, as transformers (both in ViTs and LLMs) are built with the self-attention mechanism. 

- ***Technical details***: Although the inserted LLM block is frozen, is still not clear whether the performance gains truly stem from it. How about adding a random initialized LLM block for comparison?  In Table 2, about the point cloud recognition task, the performance gains are marginal, especially on ModelNet40 (degraded performances for 1k and 4k). 

- ***Theoretical justification***: Despite not being compulsory, can the author provide some theoretical justifications rather than experimental observations to explain why the language-trained LLM block can work for visual encoding? Or any potential theory that might lead to a better explanation?

#### Questions
In addition to the above weaknesses, here are more questions:

- Why only insert one frozen LLM block for visual encoding? can adding more blocks bring more performance again?

- Why choose the last transformer block from LLaMA-7B for experiments? Can other blocks also work well? Is there any guidance to choose which block?

- Is there any other way to insert the frozen LLM block in visual encoders? How about adding it at the beginning of visual transformers, or in the middle of visual transformers?

- The authors removed the attention mask and positional embedding for the frozen LLM block, is there any experimental study for these designs?

## Meta Reviews

### Meta Review 1
The paper proposes to incorporate frozen transformer layers from large language models (LLMs) into vision models when training the model from scratch. After rebuttal, this paper received scores of 6668.

All the reviewers are happy about the paper, commenting that the paper is well written, it provides detailed investigations of how and why the proposed paradigm works, reusing pre-trained layers from LLMs is a novel and intriguing idea, and experimental results are sufficient. The information filtering hypothesis also provides some insights into the reason for why this method works. Therefore, the AC would like to recommend acceptance of the paper.

## Decisions

Decision: Accept (spotlight)

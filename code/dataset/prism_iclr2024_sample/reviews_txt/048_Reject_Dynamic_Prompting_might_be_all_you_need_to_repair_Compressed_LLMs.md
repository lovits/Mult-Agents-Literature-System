# (Dynamic) Prompting might be all you need to repair Compressed LLMs

OpenReview ID: SyuQKk7sX2
Decision: Reject

## Abstract
Large language models (LLMs), while transformative for NLP, come with significant computational demands, underlining the need for efficient, training-free compression. Notably, the reliability of perplexity as a benchmark for compressed model efficacy is in question, as our tests using LLaMA-7B and OPT-6.7b reveal a significant performance drop in several realistic downstream tasks, underscoring the disparity between perplexity as a performance indicator and real-world performance. Investigation into the trade-off between resource-intensive post-compression re-training highlights the prospect of prompt-driven recovery as a lightweight adaption tool. However, existing studies, confined mainly to perplexity evaluations and simple tasks, fail to offer unequivocal confidence in the scalability and generalizability of prompting.We tackle this uncertainty in two key ways. First, we uncover the vulnerability of naive prompts in LLM compression as an over-reliance on a singular prompt per input. In response, we propose \textit{inference-time dynamic prompting} (IDP), a mechanism that autonomously chooses from a set of curated prompts based on the context of each individual input. Second, we delve into a scientific understanding of why ``prompting might be all you need post-LLM compression". Our findings suggest that compression doesn't irretrievably erase LLM model knowledge but displace it, necessitating a new inference path. IDP effectively redirects this path, enabling the model to tap into its inherent yet displaced knowledge and thereby recover performance. Empirical tests affirm the value of IDP, demonstrating an average performance improvement of 1.24\% across nine varied tasks spanning multiple knowledge domains.

## Reviews

### Review 1
Rating: 3: reject, not good enough
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper introduces a novel approach to enhance the performance of compressed Language Model Models (LLMs). The proposed method, referred to as Inference-time Dynamic Prompting (IDP), involves adding a set of trainable soft prompts to the user input. During inference, only the prompt with the highest attention score is activated, making it dynamically selected. The authors have empirically validated the efficacy of their approach across nine downstream tasks, demonstrating that IDP effectively restores the performance of two LLMs (LLaMA and OPT) subjected to two compression techniques (quantization and sparsification). The results show that IDP outperforms the baseline models in terms of overall performance.

#### Strengths
The contribution of this paper is two-fold.

From a theoretical perspective, it delves into the limitations of existing prompting methods by highlighting the deficiency in prompt diversity. Furthermore, it provides an in-depth analysis of the underlying mechanism of IDP, illustrating how IDP effectively "re-channels" the concealed knowledge impacted by compression algorithms.

In the realm of empirical experimentation, IDP demonstrates its superior effectiveness in mitigating the performance degradation caused by compression algorithms when compared to baseline models. Across nine distinct downstream tasks, IDP consistently outperforms these baseline models, which include single prompt, prompt tuning, and LoRA.

#### Weaknesses
1. Writings

The paper's clarity and organization require improvement. In particular, the flow of the paper can be challenging to follow, particularly in the experiment section. Section 3.3.1 is titled "IDP results," while 3.3.2 is titled "More Comparisons and Ablation Studies," but it is not clear what differentiates these experiments. Additionally, the discussion of Table 1 and Table 2 occurs after the discussion of Table 3, which can be confusing for readers. The suffixes /short and /large in Table 1 and Table 2 are not adequately explained in the main paper. Furthermore, the details of Table 3 and Table 4, specifically the 3 settings of parameter sizes for LoRA, prompt, and ptune, are not provided in either the captions or the main paper.

There are some critical details missing in the paper, particularly concerning hyperparameters. For example, the paper does not specify the prompt length and number, which are denoted as n and m in Section 3.2. Furthermore, there is a lack of information regarding the settings for LoRA, ptuning, and soft prompts. Moreover, it would be helpful if the authors presented the results of the original LLMs to demonstrate the performance drop resulting from compression algorithms.

2. Novelty

The general idea of IDP is based on soft prompting with a dynamic module to select one prompt from a collection of prompts during inference. This solution is akin to the ensemble solution, with the ensembling replaced with a hard selection. Prompt ensembling has been studied by many papers in recent years, and solely applying it to repair compression algorithms isn't novel enough.

3. Performance

The performance enhancement achieved by IDP, in comparison to the baseline models, tends to be relatively modest. Across Table 1 to Table 4, the observed improvement in performance typically falls within the range of 1%. In cases where the performance gap is quite narrow, it may be helpful to conduct a significance test to assess the statistical significance of the results.

4. Hypothesis test

One of the claimed contributions of this paper pertains to the exploration of the reasons behind the performance enhancement achieved by IDP. It introduces hypotheses, denoted as H0 and H1, and conducts hypothesis testing. It's worth noting, however, that this process doesn't adhere to the conventional standard of hypothesis testing, which typically involves the rejection of the null hypothesis (H0). Instead, the authors undertake an analysis of the behavior of IDP and the baseline models, drawing the conclusion that H1 is the more plausible explanation.

The distinction between "data attrition" and "knowledge rechanneling" is somewhat subtle and challenging to precisely define. The evidence presented in the paper, including the shift in attention patterns, may not be compelling enough to definitively support H1, as factors such as the incorporation of new data sources could also lead to changes in attention patterns, making them difficult to reject.

#### Questions
1. Typo: In page 8, triviqa -> TriviaQA
2. In Table 3, what do /small and /large mean? Do they correspond to "individual prompts"? How long are they?
3. In all experiments, is the performance of the original models comparable? By showing the performance of un-compressed models, we can clearly see how much compression impairs the model performance.

### Review 2
Rating: 8: accept, good paper
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The work explores the use of dynamic prompting as a tool to improve performance in compressed large language models (LLMs). The authors question the reliability of perplexity as a benchmark for measuring the effectiveness of compressed models and propose dynamic prompting as a solution. They introduce inference-time dynamic prompting (IDP), which selects prompts based on the context of each input. The paper also discusses the displacement of LLM model knowledge during compression and how IDP can utilize this displaced knowledge to enhance performance. Empirical tests demonstrate an average performance improvement across nine tasks.

#### Strengths
The idea of using inference-time dynamic prompting is interesting, simple and effective.

The paper is clear and easy to follow.

#### Weaknesses
As the proposed method is quite straightforward, the technical contribution of this paper is not significant. 

The idea of using dynamic prompts to enhance downstream task performance is also not novel. The contributions of the method part is limited to a selection mechanism of the dynamic prompts.

#### Questions
May the author provide further explanation about why the prompt is selected by the maximal mean attention? Why does a large mean attention result in a better prompt?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The paper delves into the exploration of prompt tuning as a method to rejuvenate the effectiveness of compressed models. It contrasts this approach with existing methods, especially emphasizing its edge in terms of improving model efficiency without increasing parameters. Through various experiments, it was evidenced that prompt tuning, especially with the proposed IDP (Inference Dynamic Prompting), effectively re-channels the inherent knowledge within models rather than just adding new data. This enables compressed models to perform at par, if not better than their uncompressed counterparts, particularly in world knowledge tasks.

#### Strengths
Originality: The paper introduces a novel concept called Inference Dynamic Prompting (IDP), standing out as a fresh approach in the realm of compressed models and their performance enhancement.

Quality: The experiments are meticulously carried out, with careful visualization of layer-wise attention and activation matrices. The contrast with other methods like LoRA provides a comprehensive understanding of the efficacy of IDP.

Clarity: The paper is lucidly written, with each section building on the previous, gradually taking the reader from the introduction of the problem to the proposed solution and its validation.

Significance: In a world emphasizing model efficiency, the proposed method is highly relevant. It not only offers a solution to the performance degradation in compressed models but does so without adding extra computational burden, making it significantly impactful in real-world applications.

#### Weaknesses
While the paper emphasizes the strengths of IDP and prompt tuning, a direct comparison with a broader range of methods, apart from LoRA, would have given a more holistic perspective.

The paper could have benefitted from a more detailed explanation or a separate section dedicated to the underlying theory or intuition behind why IDP works the way it does.

The experiments, though comprehensive, seem to focus predominantly on world knowledge tasks. Incorporating a wider variety of tasks could showcase the versatility of the approach.

#### Questions
Could the authors elaborate on the foundational theory behind IDP's ability to rechannel inherent knowledge? Is there any theoretical upper limit to its efficiency?

Are there any domains or tasks where IDP might not be as effective, and if so, what are the challenges faced in those scenarios?

Given the effectiveness of IDP in re-channeling latent knowledge within the model, how does it fare in terms of transfer learning across different domains?

### Review 4
Rating: 3: reject, not good enough
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper focuses on improving compressed LLMs, such as LLMs with 3-bit quantization. The authors argued that the prior work (Xu et al., 2023) suffers from worse performance as the prompt length increases, due to using perplexity as their metric. This paper thus proposed a method called inference-time dynamic prompting (IDP), which learns a collection of prompts and then automatically selects the best prompt during the inference time. Experiments were conducted based on OPT-6.7b and Llama-7b, when 3-bit GPTQ and SparseGPT were applied to compress the LLMs. The results indicate slightly better performance from IDP compared with baselines such as prompt tuning, prefix-tuning, and LoRA.

#### Strengths
1. The paper studied an important problem of improving compressed LLMs, such that one can strike a better balance between model size/compute and performance.
2. The proposed approach, IDP, was shown to outperform baselines.
3. The discussion about incorporating new knowledge vs. directing knowledge is interesting.

#### Weaknesses
1. Motivation/intuition: It is not clear to me how the proposed IDP can intuitively address the failure discussed in Section 3.1 (which was said to be caused by the discrepancy between perplexity and accuracy), though I understand that the authors are suggesting to replace long prompts with multiple smaller ones as well as a selection mechanism.
2. For most of the experimental results, IDP outperforms baselines only marginally, and the authors have not conducted any significant tests, which makes the results unconvincing.
3. Lack of clarity and reproducibility: Several experimental or implementation details are missing. For example, what are the sizes of n, e, and m in IDP? What are the prompt sizes for small- and large-prompts in Figure 5?

#### Questions
Please respond to my concerns in weaknesses.

## Meta Reviews

### Meta Review 1
The authors propose a strategy for making LLMs more efficient via inference-time dynamic prompting, or IDP. This approach is based on soft prompts, but here the idea is to keep a collection of these around select which to use at inference time (hence, "dynamically"). 

This paper offers some nice ideas, but as pointed out by reviewers dG5d, zxJa, and gfXp, the technical approach is not particularly novel. This is not in and of itself a critical issue, but the empirical performance realized using this simple approach is only marginally better than existing methods (it appears to offer an average improvement of ~0.5 points in accuracy over the datasets considered). The authors attempted to address this latter point in response by providing p-values under hypothesis testing, which appears to show "significance" (I'm not clear on how the "pairing" was done here, but that's beside the point); nonetheless, "significance" does not change the marginal mean improvement.

## Decisions

Decision: Reject

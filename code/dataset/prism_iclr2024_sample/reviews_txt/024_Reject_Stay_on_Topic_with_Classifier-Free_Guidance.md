# Stay on Topic with Classifier-Free Guidance

OpenReview ID: RmRA7Q0lwQ
Decision: Reject

## Abstract
Classifier-Free Guidance (CFG) has recently emerged in text-to-image generation as a lightweight technique to encourage prompt-adherence in generations. In this work, we demonstrate that CFG can be used broadly as an inference-time technique in pure language modeling. We show that CFG (1) improves the performance of Pythia, GPT-2 and LLaMA-family models across an array of tasks: Q&A, reasoning, code generation, and machine translation, achieving SOTA on LAMBADA with LLaMA-7B over PaLM-540B; (2) brings improvements equivalent to a model with twice the parameter-count; (3) can stack alongside other inference-time methods like Chain-of-Thought and Self-Consistency, yielding further improvements in difficult tasks; (4) can be used to increase the faithfulness and coherence of assistants in challenging form-driven and content-driven prompts: in a human evaluation we show a 75% preference for GPT4All using CFG over baseline.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The authors demonstrate that CFG, which has primarily been used in text-to-iamge generation, can bring improvements in pure language modeling. The authors demonstrate that CFG boosts performance on benchmarks and provide results on multiple models.

#### Strengths
[+] The authors suggest new improvements to training in large language models, leading to faster training times and more granular control. 
[+] The paper has a thorough background section, containing diverse and relevant works to their proposed method.
[+] The paper contains extensive comparative results on numerous tasks.
[+] The authors provide an insightful computational cost analysis.

#### Weaknesses
[-] The idea of using CFG is not novel. The authors simply apply this principle to different models. 
[-] The explanations for why CFG works well for language models are not very solid. I'd like to see more concrete evidence of what is being altered in the model in this training process.

#### Questions
It is insightful to see these experiments. However, despite the great results, the idea is not surprising or novel. It does not feel like quite a strong contribution to the community yet. How can CFG be extended to help language models specifically? This seem like a generic application of the idea.

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper explores the effectiveness of classifier-free guidance (CFG) in pure language modelling. Drawing inspiration from the equation employed in text-to-image generation, the authors apply CFG to the logits of next-token predictions in language models.
Through a plethora of designed experiments, they validate the remarkable efficacy of CFG: 1) enhancing the performance of LLMs on many NLP tasks; 2)  improving the performance of CoT and self-consistency; 3) increasing the faithfulness and coherence.

#### Strengths
- The idea is simple and reasonable.
- This paper conducted extensive experiments to validate the effectiveness of CFG.

#### Weaknesses
- The \gamma values in one context are poorly suited for another context, making CFG tricky in practice. 
- Some recent works have explored CFG in language models, weakening the contribution of this paper.

#### Questions
- Have you explored this method in controllable NLG tasks or constraint-decoding tasks, or compared it with SOTA methods? 
- Compared with text-to-image generation, the optimal \gamma value in the language modelling seems to be small (<2), while large \gamma value leads to poor performance. Have any observations on it?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper adapts the classifier-free guidance from text-to-image diffusion model into text generation to have better control on the generation content. With a $\gamma$ multiplier deciding the strength of the guidance away from the unconditional vector in the direction of the conditioning, it allows a finer controll on the prompt adherence. By extensive experiments on chain-of-though prompting, long-context generation, programme synthesis and conversational asisstant, the author shows that the proposed method can achieve similar performance as a double-sized model without significant increase in computation cost.

#### Strengths
1. The proposed method is very straightforward and easy to implement yet effective, requiring only the $\gamma$ multiplier and the second-run of the model.
2. The paper is well written and easy to follow.
3. The experiment performance is impressive and allow a LM to perform nearly as well as a doule-sized one without significant increase in computation cost.

#### Weaknesses
1. some formatting issues (not necessarily reason to reject):
    The citation format and style in the submission is not correct. It seems that the authors always use \citet{} instead of \citep{}
    Some important reference are missing. For example, the original PaLM paper is not cited.
    In figure 2, some part of the curve is overlapped with the legend.
    In figure 2, the ticks for the x-axis are not evenly distributed.
    In table 2, the percentage sign is missing for some numbers.
    In the first paragraph of section3, LLaMa -> LLaMA.
    In the line above Eq.6, $N$ is used to denote the number of tokens to model which is different from the $T$ in Eq.6.

2. A memory cost analysis is recommended. The proposed method requires a second run of the model, which may increase the memory cost (for example, the key-value cache).

#### Questions
There is no grantee that the Eq.6 will obtain a legal probability with the probabilities of all possibilities summing up to 1. Is there any normalization technique to deal with this?

## Meta Reviews

### Meta Review 1
In this paper, the authors explore that CFG (Classifier-Free Guidance) can be an effective way of increasing adherence to the prompt in
autoregressive language modeling. Inspired by the employment in text-to-image generation, the authors apply CFG to the logits of next-token predictions in language models. Extensive experiments show that CFG is beneficial for enhancing the performance of LLMs on NLP tasks, improving the performance of CoT and self-consistency, and increasing faithfulness and coherence.

The paper is well-written and easy to follow. However, we are concerned about the novelty and contribution of the paper as many recent works have explored CFG in language models and the authors also cannot convince the reviewers how this study differs from the other related works.

## Decisions

Decision: Reject

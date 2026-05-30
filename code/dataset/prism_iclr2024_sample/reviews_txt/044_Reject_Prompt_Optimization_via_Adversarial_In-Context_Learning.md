# Prompt Optimization via Adversarial In-Context Learning

OpenReview ID: v6a1pXXADC
Decision: Reject

## Abstract
We propose a new method, Adversarial In-Context Learning (adv-ICL), to optimize prompt for in-context learning (ICL) by employing one LLM as a generator, another as a discriminator, and a third as a prompt modifier. As in traditional adversarial learning, adv-ICL is implemented as a two player game between the generator and discriminator, where the generator tries to generate realistic enough output to fool the discriminator. In each round, given an input prefixed by task instructions and several exemplars, the generator produces an output. The discriminator is then tasked with classifying the generator input-output pair as model-generated or real data. Based on the discriminator loss, the prompt modifier proposes possible edits to the generator and discriminator prompts, and the edits that most improve the adversarial loss are selected. We show that adv-ICL results in significant improvements over state-of-the-art prompt optimization techniques for both open and closed-source models on 11 generation and classification tasks including summarization, arithmetic reasoning, machine translation, data-to-text generation, and the MMLU and big-bench hard benchmarks. In addition, because our method uses pre-trained models and updates only prompts rather than model parameters, it is computationally efficient, easy to extend to any LLM and task, and effective in low-resource settings.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes Adversarial In-Context Learning (adv-ICL) to optimize prompts for in-context learning (ICL). 
It uses an LLM-based prompt modifier to modify the prompts of LLM-based generator G and LLM-based discriminator D.
In each round, the prompt modifier produces $r$ samples, and the best one is selected based on the discriminator loss to update the prompts of G and D.
The method shows improvements on 11 tasks.

#### Strengths
1. The experimental results show clear improvements over the baselines.
2. Using adversarial optimization for prompt optimization is a novel idea.
3. The implementation and experimentation details are relatively adequate.

#### Weaknesses
1. The novelty is limited:
    - The resampling method (as the prompt modifier) is already proposed in APE (Zhou et al., 2023). The prompt used to modify instructions in this work is very similar to the prompt used in APE but without proper citation.
    - For problems where the discriminator is trivial (e.g. for multiple-choice problems), the method is very similar to APE except that the demonstrations are also resampled.
    - The idea of adversarial optimization comes from GAN.
2. The presentation needs to be improved, I would suggest including a running example in the method section to explain the generator, discriminator, and prompt modifier, and how they interact with each other.
3. Some ablation studies are missing (see questions below).
4. The limitations are missing.

#### Questions
1. Why the discriminator is necessary?
    - Can you do an ablation study when the discriminator is frozen?
    - Can you compare the performance of using a trivial discriminator (e.g. exact match) and using an LLM-based discriminator on classification and reasoning tasks?
    - Can you compare the performance of adv-ICL with APE which uses LLM's log-likelihood as the objective function, on summarization, data-to-text, and machine translation tasks?
2. In Table 3, too many iterations $T$ or samples $m$ seem to harm the performance, could you give some explanation or hypothesis about why?
3. In the appendix, for figures 9 and 10, what's the baseline in these figures? Is adv-ICL always not worse than the baselines and why?

Minor:
- Some captions could be longer to better explain the figures and tables.
- Please place the caption of the Tables above.

Misc:
- There is a concurrent work you may discuss in related work: LLM as optimizers [1].

---
The response partially addresses my concerns. I would raise my score from 3 to 5.

[1] Yang, C., Wang, X., Lu, Y., Liu, H., Le, Q. V., Zhou, D., & Chen, X. (2023). Large language models as optimizers. arXiv preprint arXiv:2309.03409.

### Review 2
Rating: 3: reject, not good enough
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes a new method called Adv-ICL that applies the framework of generative adversarial networks to LLMs to improve in-context learning. Instead of directly updating the weights of a target model, the method employ a prompt modifier to generate prompts, which are then fed into the generator and discriminator to lower their respective loss functions.

#### Strengths
S1. The idea of applying generative adversarial networks to imporve in-context learning is plausible. 
S2. According to the experimental results shown by the authors, Adv-ICL outperforms the baselines in some settings.

#### Weaknesses
W1. The convergence of the proposed approach. It seem that the prompts are modified by chance rather than gradient signals. This poses a serious concerns on the convergence and efficiency of the proposed approach. Yet the paper does not discuss this aspect in details.

W2. Unconvencing Experiments:

W2-a. Disregarded Prompts:
During the iterative training process, when a new prompt is introduced to optimize the loss function, the model (either the generator or the discriminator) engages in in-context learning, regardless of whether the new prompt is accepted or discarded. It's worth noting that discarded prompts can also impact the model's training, but the paper does not explore this aspect in detail.

W2-b. Unclear Origin of Benefits:
The observed performance improvements in the experiments may not be solely attributed to the accepted examples but could also be influenced by the discarded ones. Furthermore, given that the optimization process relies on the stochastic behavior of large language models, it's possible that the learning effect results from the repeated trial-and-error of prompt modifications occurring during the training iterations rather than from improved prompts. Therefore, the assumption that improvements in experimental results are solely due to adversarial training may not be valid.

#### Questions
1. Is there a method to modify the prompts that doesn't involve trial-and-error? How does it compared to gradient descent?
2. What are the training time and memory usage of your approach compared to the baselines? 
3. Does your GANs framework converge effectively? What's the learning curves for the generator and discriminator, respectively?
4. How reliably can the experimental results be reproduced considering the stochastic nature of the optimization process and an LLM itself?
5. In terms of fairness, it seems that not all methods in the experiments use the prompts generated (or modified) by the same prompt modifier. Why?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
In this paper, the authors introduce Adversarial In-Context Learning (adv-ICL), which uses 3 LLMs as a generator, a discriminator, and a prompt modifier to optimize prompts. Similar to traditional adversarial learning, there is a minimax game between the generator and the discriminator, where the generator aims to generate realistic text to fool the discriminator. The generator is provided with task instructions, several exemplars, and input at each round and produces the output; the discriminator then tries to decide whether the generator input-output pair is real data or model generated. After that, the prompt modifier makes changes to the generator, and the discriminator prompts to improve the adversarial loss. They perform a set of experiments using both open and closed-source models on various generation and classification tasks to evaluate their model.

#### Strengths
- Since there are no updates to the model parameters and only the prompts change, adv-ICL is computationally efficient and effective in low-resource settings. Moreover, adv-ICL only needs a few iterations and training samples in order to achieve high performance.

- There is a thorough analysis of the quantitative and qualitative aspects of their method.

#### Weaknesses
- Some more RL-based prompt optimization baselines (e.g., Mingkai Deng, Jianyu Wang, Cheng-Ping Hsieh, Yihan Wang, Han Guo, Tianmin Shu, Meng Song, Eric P. Xing, & Zhiting Hu. (2022). RLPrompt: Optimizing Discrete Text Prompts with Reinforcement Learning.) could be used in the evaluation section to provide more insight.

#### Questions
- It seems that in order to make edits to the prompts, the prompt modifier is prompted with a template text, and the last best-performing generator and discriminator prompts. What if you provide more feedback to the prompt modifier, such as the last best-performing prompt, alongside its predecessor, and how much better this last prompt performed than the other?

- For human evaluation, it is mentioned that annotators are tasked with verifying whether the sampled instruction/demonstration is semantically similar to the original one or not. What if you also add a module that can automatically verify this, check the content preservation score, and also consider this metric when choosing a prompt?

## Meta Reviews

### Meta Review 1
The paper proposes Adversarial In-Context Learning (adv-ICL), a method that employs adversarial learning concepts to optimize prompts for in-context learning using LLMs. The paper's strengths and weaknesses, as noted by the reviewers, are summarized below:

Strengths:

+ Computational Efficiency: Adv-ICL's reliance solely on prompt modifications, without updating model parameters, makes it computationally efficient and particularly effective in low-resource settings.

+ Novel Application of GANs: The idea of applying generative adversarial networks (GANs) to improve in-context learning is innovative and shows potential based on the experimental results.

+ Performance Improvements: According to the experiments, adv-ICL outperforms baselines in some settings, demonstrating clear improvements.

+ Comprehensive Analysis: The paper includes a thorough analysis of the quantitative and qualitative aspects of the method.

Weaknesses:

- Limited Novelty: The novelty of the approach is questioned, particularly in relation to the resampling method used as the prompt modifier, which appears similar to previously proposed methods in existing literature.

- Presentation and Clarity Issues: The presentation of the method and its components lacks clarity. Inclusion of a running example to explain the interactions between the generator, discriminator, and prompt modifier would improve understanding.


- Convergence Concerns: There are serious concerns about the convergence and efficiency of the proposed approach, as the prompts seem to be modified by chance rather than clear gradient signals. (Addressed in the rebuttal)

- Unconvincing Experiments and Lack of Detail: The paper fails to convincingly demonstrate that performance improvements are solely due to the adversarial training and not influenced by stochastic behaviors or discarded prompts. (Partially addressed in the rebuttal)

Given these observations, the paper, while presenting an interesting and potentially impactful idea, falls short in several areas.

## Decisions

Decision: Reject

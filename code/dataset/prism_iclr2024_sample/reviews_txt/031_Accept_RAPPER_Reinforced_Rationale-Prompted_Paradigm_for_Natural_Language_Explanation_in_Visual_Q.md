# RAPPER: Reinforced Rationale-Prompted Paradigm for Natural Language Explanation in Visual Question Answering

OpenReview ID: bshfchPM9H
Decision: Accept

## Abstract
Natural Language Explanation (NLE) in vision and language tasks aims to provide human-understandable explanations for the associated decision-making process. In practice, one might encounter explanations which lack informativeness or contradict visual-grounded facts, known as implausibility and hallucination problems, respectively. To tackle these challenging issues, we consider the task of visual question answering (VQA) and introduce Rapper, a two-stage Reinforced Rationale-Prompted Paradigm. By knowledge distillation, the former stage of Rapper infuses rationale-prompting via large language models (LLMs), encouraging the rationales supported by language-based facts. As for the latter stage, a unique Reinforcement Learning from NLE Feedback (RLNF) is introduced for injecting visual facts into NLE generation. Finally, quantitative and qualitative experiments on two VL-NLE benchmarks show that Rapper surpasses state-of-the-art VQA-NLE methods while providing plausible and faithful NLE.

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The paper introduces RAPPER, a two-stage Reinforced Rationale-Prompted Paradigm designed to improve Natural Language Explanation (NLE) in Visual Question Answering (VQA) tasks. The first stage employs knowledge distillation from large language models (LLMs) to generate rationales that are fact-based. The second stage introduces a unique Reinforcement Learning from NLE Feedback (RLNF) to incorporate visual facts into the NLE generation. The paper claims that RAPPER outperforms existing state-of-the-art methods in VQA-NLE on two benchmarks, providing more plausible and faithful explanations.

#### Strengths
The paper addresses the problem of implausibility and hallucination in NLE for VQA, which is a novel contribution. The two-stage approach combining knowledge distillation and reinforcement learning is also unique and the RLNF technique for incorporating visual facts into NLE is particularly noteworthy.

The paper is well-organized and clearly articulates the problem, the proposed solution, and its advantages. The use of figures to illustrate the model architecture and the comparison with existing methods is helpful.

Improving the plausibility and faithfulness of NLE in VQA has important implications for real-world applications, such as medical VQA, where interpretability is crucial.

#### Weaknesses
The two-stage approach, while novel, adds complexity to the model. It would be beneficial to see a discussion on the trade-offs involved, such as computational cost.

The paper focuses on VQA tasks, and it's not clear how's performance of the proposed method when it was adapted to other vision-language tasks.

No human evaluation is conducted regarding the generation quality.

#### Questions
How does the complexity of the two-stage approach impact the computational efficiency of the model?

Could you elaborate on how the RLNF stage specifically tackles the hallucination problem in NLE?

### Review 2
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The authors propose a reinforced rationale-prompted paradigm (Rapper) for natural language explanation (NLE) in visual question answering (VQA). They aim to generate plausible and faithful NLEs to address issues like implausibility and hallucination in existing VQA-NLE methods. Rapper has two stages - knowledge distillation from large language models (LLMs) and reinforcement learning from NLE feedback (RLNF). In stage 1, it elicits pseudo rationales from LLM to encourage plausibility and filters rationales using QA model for quality.
In stage 2, it uses RLNF with answer and explanation scores as rewards to inject visual facts into rationales, improving faithfulness.
RAPPER, when evaluated on VQA-X and e-SNLI-VE datasets, achieves new SOTA on both for NLE metrics. It shows better plausibility via higher CIDEr and SPICE scores compared to prior VQA-NLE methods and demonstrates improved faithfulness through higher RefCLIPScore than previous methods. The approach reduces hallucination and implausibility qualitatively over other approaches.

#### Strengths
The paper offers a novel two-stage approach to inject both language-based facts and visual content into rationales.
It leverages powerful knowledge and reasoning capabilities of LLMs through distillation. RLNF provides a way to align rationales with visual input for faithfulness. Rationale prompting is interpretable and improves reasoning module's NLE. Training is end-to-end, does not need ground truth rationales.
Moreover, the qualitative results show more precise and reasonable NLEs: if achieves new SOTA on VQA-X and e-SNLI-VE for all NLE metrics in both filtered and unfiltered settings. It also shows higher CIDEr and SPICE scores demonstrating enhanced plausibility of NLEs.
Improved RefCLIPScore indicates increased faithfulness and reduced hallucination.
Ablations validate importance of both knowledge distillation and RLNF stages and analysis of derived rationales indicates progressively better quality.
Qualitative examples exhibit more visually grounded and plausible NLEs than prior methods. It also reduces cases of implausible and hallucinated explanations over other VQA-NLE approaches.
The claims seem reasonably supported by the quantitative and qualitative results on the standard benchmarks. The improved performance across NLE metrics substantiates the effectiveness of the Rapper approach for plausible and faithful explanation generation. The ablation studies validate the contribution of the individual components. The qualitative examples provide additional evidence that Rapper produces more precise and reasonable rationales and explanations.

#### Weaknesses
Some potential weaknesses include:
The approach relies on eliciting high-quality pseudo rationales from the LLM, but the process for doing so is not extensively analyzed. In fact LLMs, especially smaller ones  (relative to e.g. GPT4) are prone to hallucinations. 
The impact of different choices of LLM for knowledge distillation is not addressed.
Evaluation is limited to VQA; extending Rapper to other VL tasks may reveal additional challenges.
More human evaluations on plausibility and faithfulness could further validate the approach.

#### Questions
How did you determine the optimal hyperparameters (e.g. threshold τ) for filtering pseudo rationales from the LLM? Was any tuning or analysis done to validate these settings?
Did you experiment with different LLMs for knowledge distillation? If so, how did the choice of LLM impact the quality of the distilled rationales?
You mention the potential to extend Rapper to other vision-language tasks. What challenges do you anticipate in adapting the approach to other datasets and tasks?
The elicitation process for pseudo rationales is a key component of your approach but is not analyzed in depth. Can you provide more details on this process and how the prompts were designed?
Can you discuss any trade-offs between plausibility and faithfulness you observed? Does optimizing one tend to hurt the other?

### Review 3
Rating: 3: reject, not good enough
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The paper is about mitigating implausibility and hallucination problems (non-informative or contradicting visual context) for generating natural language explanation (NLE) under VQA problems. To mitigate the issue, the authors introduced a notion of “rationale” which is similar to chain-of-thought prompting. To combat the issue of generating rationale without training data, the authors distill rationale from LLMs into the rationale generator. To penalize hallucinated rationale, “Reinforcement Learning from NLE Feedback” is used. The combination of proposed method brings a marginal improvement on benchmarks.

#### Strengths
- The paper is largely well-written and easy to understand.
-  The function of each component in the method is clear and sound.
- The method achieves SOTA on NLE benchmarks.

#### Weaknesses
- The role of using rationale to improve implausibility and hallucination is unclear. It is well-known that chain-of-thought can improve reasoning. However, it is unclear to me if adding one more step, i.e., rationale could really mitigate hallucination.
- While the method is sound, I’m not very convinced that we cannot just use large vision language models and perform a chain-of-thought style prompting (which was actually the inspiration of this method)? How does large vision language models (e.g. BLIP-family or LLAVA models) perform?
- In ablation study table, the impact of proposed method is small. Especially, RLNF effect is small.
- A clear definition of “rationale” is not presented in the paper. Only mentioned that it is like an “intermediate” just like in chain-of-thought prompting.

#### Questions
- Please answer my questions in “weaknesses” section. I may raise score if the rebuttal is satisfactory.

## Meta Reviews

### Meta Review 1
While the work shows promise in generating more plausible and faithful VQA explanations, the reviewers identify several limitations and request further clarification before fully endorsing the work. I recommend for a weak accept with the expectation of addressing the identified weaknesses.

Strengths include combining knowledge distillation and reinforcement learning to inject visual and factual data into rationales.  Improved RefCLIPScore suggests less hallucination and increased faithfulness. Qualitative results demonstrate more precise and visually grounded rationales compared to prior methods.

However, the process for eliciting high-quality rationales from the LLM is unclear and potentially prone to hallucinations, especially with smaller LLMs. Evaluation focuses mainly on VQA, raising concerns about generalizability to other vision-language tasks. Human evaluation is provided during discussion phase, but need further cross-checking on human experimental setup details.

## Decisions

Decision: Accept (poster)

# RA-DIT: Retrieval-Augmented Dual Instruction Tuning

OpenReview ID: 22OTbutug9
Decision: Accept

## Abstract
Retrieval-augmented language models (RALMs) improve performance by accessing long-tail and up-to-date knowledge from external data stores, but are challenging to build. Existing approaches require either expensive retrieval-specific modifications to LM pre-training or use post-hoc integration of the data store that leads to suboptimal performance. We introduce Retrieval-Augmented Dual Instruction Tuning (RA-DIT), a lightweight fine-tuning methodology that provides a third option by retrofitting any LLM with retrieval capabilities. Our approach operates in two distinct fine-tuning steps: (1) one updates a pre-trained LM to better use retrieved information, while (2) the other updates the retriever to return more relevant results, as preferred by the LM. By fine-tuning over tasks that require both knowledge utilization and contextual awareness, we demonstrate that each stage yields significant performance improvements, and using both leads to additional gains. Our best model, RA-DIT 65B, achieves state-of-the-art performance across a range of knowledge-intensive zero- and few-shot learning benchmarks, significantly outperforming existing in-context RALM approaches by up to +8.9% in 0-shot setting and +1.4% in 5-shot setting on average.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper introduces a two-stage fine-tuning process aimed at enhancing a pre-trained language model's performance. In the first stage, the focus is on improving the LM's ability to effectively utilize retrieved information, while in the second stage, the retriever is fine-tuned to provide more contextually relevant results as desired by the LM. The study reveals that both of these stages contribute significantly to performance enhancements. Furthermore, when both stages are combined, even greater improvements are observed. The proposed model, RA-DIT 65B, achieves state-of-the-art results in various knowledge-intensive zero-/few-shot learning tasks, surpassing existing in-context RALM approaches by a substantial margin.

#### Strengths
* One of the standout strengths of this paper is its ability to outperform other presented baseline models. 

* The paper's approach offers practical value by demonstrating that the fine-tuning process is lightweight. This means it can be implemented efficiently, making it a more accessible and feasible solution for real-world applications.

* The method presented in the paper is well-motivated and clearly described, enhancing its accessibility and potential for replication. This transparency in methodology ensures that other researchers can easily understand and build upon the work, further advancing the field.

#### Weaknesses
* The paper's architecture lacks significant novelty as it primarily relies on existing models and introduces minor modifications. This may limit its impact and originality in the field.

* The paper raises concerns about the accuracy of the ATLAS scores in the 64-shot fine-tuning results presented in Table 2. Discrepancies between the reported scores and those from the ATLAS paper, as observed in Table 10 of the ATLAS paper, undermine the credibility of the findings.

* The paper does not include a comparison with a strong baseline model, such as FID+RS (Hofstätter et al., 2022). If included, it is suggested that FID+RS would outperform the proposed model, based on reported scores from the FID+RS paper. Additionally, FID+RS has the advantage of a significantly smaller model size, which raises questions about the efficiency and resource requirements of the proposed model. (11B vs 65B)

#### Questions
If any of the concerns raised stem from misunderstandings, kindly bring them to my attention. I would greatly appreciate the opportunity to gain a better understanding and, if necessary, reevaluate the content in question

### Review 2
Rating: 6: marginally above the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The paper proposed the Retriever-Agument dual Instruction tuning, aimed to get the pretrained language model to better understand the retrieved text. The paper constructs a dataset, consisting of different domains (Open book QA, summarization, general conversation, etc.). The dataset improves the performance of the original model by a good margin.

#### Strengths
1. The paper presents very solid experiments on the instruction tuning. 
2. The paper is very well presented.
3. The ablation of the paper is solid.

#### Weaknesses
1. The author mentioned the early stopping, training the model for ~500 steps would bring the best performance. How is the dataset size scaling with this? Can we change the cap of 7000 data points per domain to smaller or larger? will the performance change?
2. Is there a criteria of how to choose the domains? And does jointly training on multiple domains help boost the performance? The choice of different domains seems a bit random.
3. How sensitive is the model to different type of retrievers? Like can contriever/dpr work in this setting?

#### Questions
Please see above.

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes retrieval-augmented instruction tuning for pre-trained LLM. It also finetunes retriever.

#### Strengths
- Important topic.
- Overall good results on knowledge intensive tasks in contrast to previous methods.

#### Weaknesses
- Fine-tuning the retrievers seems to be unnecessary given the very marginal improvement. However, this paper is written in a way that encourages the fine-tuning of retrievers.
- The retrieval-augmented instruction tuning may encourage hallucination. See detailed comments.

#### Questions
Detailed comments:

1. “To stay within the context window size limit, each retrieved chunk is prepended individually to the prompt”
- Llama has 2k context. What’s the length of the retrieved chunk? How many chunks (top-?) are used in the experiment? Did you try to pack top-5 all-together into the prompt?

2. “Secondly, even state-of-the-art retrievers can falter and return inaccurate results. By training the LLM to make correct predictions when a wrong retrieved chunk is given, we enable the LLM to ignore misleading retrieval content and lean into its parametric knowledge in such cases”
- This process may encourage the LLM to hallucinate if i) answer is not in retrieved context, and ii) the required knowledge for answering the question is not stored in LLM parameters. 

3. For baseline Llama 65B, did you apply instruction tuning using the same blended dataset? In Table 4, the improvement from IT 65B vs.RA-IT 65B is pretty marginal with the top-1 chunk. 

4. Could the authors also provide the results using top-5 in Table 4?

5. In Table 2 main results, why is Llama 65B so bad on NQ? Do you evaluate it in a close-book manner i.e., non-retrieval setting?

6. In Table 5, fine-tuning retriever seems to only provide very marginal improvements.

Concurrent work:

InstructRetro: Instruction Tuning post Retrieval-Augmented Pretraining.
It would be recommended to include relevant discussion in related work.

### Review 4
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes a method to endow LLMs with retrieval-augmented generation capabilities through a lightweight fine-tuning procedure that is in-between costly ad-hoc retrieval-aware pretraining and cheaper but subobtimal post-hoc integration techniques.
The proposed approach consists in two fine-tuning steps: one to update a pretrained LLM to make good use of retrieve information and one to fine-tune the retriever itself.
The paper shows that each of these procedures improve the performance on tasks that require knowledge utilization and contextual awareness, achieving state-of-the art performance across multiple knowledge-intensive benchmarks.

#### Strengths
* The method is well-motivated in terms of practical applicability in providing pretrained LLMs with retrieval capabilities
* Reproducibility is ensured by the detailed documentation of the used instruction tuning datasets and at what stage of fine tuning they are being used
* Baseline comparisons and ablation studies are thorough and convincing

#### Weaknesses
* The proposed components are well motivated and clear, but the presentation could make it easier to get a sense of the paper in a quick glance. For instance, it might be beneficial to expand Figure 1 and its caption to help in that.
* The method is presented as two independent fine-tuning steps. On the other hand, the two fine-tuned elements depend on each other: LM-fine-tuning uses the retriever, while the retriever fine-tuning needs the LM to score the outputs. It could be beneficial for the understanding of the paper to emphasize this point.

#### Questions
* Connecting back to the point above, it seems that the final version of the algorithm consists in fine-tuning the LM using the pretrained retriever, and then the retriever is fine-tuned using this fine-tuned LM. Is that indeed the case?
* Either way, what would be the drop in performance in actually performing the two fine-tuning steps independently, as opposed to fine-tuning the retriever with the (as said presumably) already fine-tuned LM?

## Meta Reviews

### Meta Review 1
The paper provides a simple method to fine-tune LLMs to give them retrieval-augmented generation capabilities. The method is clearly explained, well-motivated and empirical results are extensive and thorough. Most reviewers recommended acceptance and all the concerns raised seem to be well-addressed by the authors. We encourage the authors to reflect all the reviewer feedback in the updated version.

## Decisions

Decision: Accept (poster)

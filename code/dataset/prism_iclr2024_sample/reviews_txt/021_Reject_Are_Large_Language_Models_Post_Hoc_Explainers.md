# Are Large Language Models Post Hoc Explainers?

OpenReview ID: MOtZlKkvdz
Decision: Reject

## Abstract
Large Language Models (LLMs) are increasingly used as powerful tools for a plethora of natural language processing (NLP) applications. A recent innovation, in-context learning (ICL), enables LLMs to learn new tasks by supplying a few examples in the prompt during inference time, thereby eliminating the need for model fine-tuning. While LLMs have been utilized in several applications, their applicability in explaining the behavior of other models remains relatively unexplored. Despite the growing number of new explanation techniques, many require white-box access to the model and/or are computationally expensive, highlighting a need for next-generation post hoc explainers. In this work, we present the first framework to study the effectiveness of LLMs in explaining other predictive models. More specifically, we propose a novel framework encompassing multiple prompting strategies: i) Perturbation-based ICL, ii) Prediction-based ICL, iii) Instruction-based ICL, and iv) Explanation-based ICL, with varying levels of information about the underlying ML model and the local neighborhood of the test sample. We conduct extensive experiments with real-world benchmark datasets to demonstrate that LLM generated explanations perform on par with state-of-the-art post hoc explainers using their ability to leverage ICL examples and their internal knowledge in generating model explanations. On average, across four datasets and two ML models, we observe that LLMs identify the most important feature with 72.19% accuracy, opening up new frontiers in explainable artificial intelligence (XAI) to explore LLM-based explanation frameworks.

## Reviews

### Review 1
Rating: 3: reject, not good enough
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper aims to explain the black-box models' output by in-context learning on large language models (LLMs). To achieve this, the authors transformed the input into sentences and proposed four prompting strategies to generate different instructions for LLMs, using LLMs to extract top-k important features to explain the black-box model. The authors compare their faithfulness of explanation with other baselines, showing competitive results.

#### Strengths
1. This paper is well-written and easy to understand.
2. The proposed method is easy to reproduce.
3. The authors provide enough experimental data to support their claim.

#### Weaknesses
The soundness of this paper is poor. The authors treat LLMs as a principal component analysis model, use them to fit the data distribution and find the top-k most important features with different prompts as the explanations for black-box models. This is not a guaranteed process because it is unclear how LLMs fit the data distribution inside the prompt, not to mention how LLMs "understand" the data distribution and further provide a faithful explanation from the perspective of data. In fact, the "logical thinking skill"[1], the ability to process math problems[1], and the instruction-following ability of LLMs[2] are poor or remain unclear; even the order of the input will affect the output of a LLM[3].

To maximize the power of LLM, a better way is to post-hoc explain the model's output from the perspective of "natural language", like [4], which is easy to understand and easy to evaluate. Using language as output, the faithfulness of explanation can be easily evaluated by human annotators intuitively. Another way is to let LLMs use tools (e.g., use Python to code) to enhance the extra ability of LLMs and further obtain a guaranteed faithful explanation for a black-box model.

[1] Song et al. NLPBench: Evaluating Large Language Models on Solving NLP Problems. Arxiv 2023.

[2] Zeng et al. Evaluating Large Language Models at Evaluating Instruction Following. Arxiv 2023.

[3] Pouya et al. Large language models sensitivity to the order of options in multiple-choice questions. Arxiv 2023.

[4] Menon et al. Visual Classification via Description from Large Language Models. ICLR 2023

#### Questions
N/A

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The authors investigate the potential of using LLMs as explainers of the external models’ behavior. To this end, the authors explore 4 strategies to quantify feature importance. Authors compare existing feature attribution algorithms to LLM-based explainers, and demonstrate comparable performance to existing algorithms.

#### Strengths
1. The idea of using LLMs as general-purpose explainers is an interesting one that could be practical and useful if it works well. This paper does a good job at taking an initial stab to demonstrate the potential of such approaches.

2. Authors show that LLMs can employ existing feature attribution paradigms, such as perturbation-based feature attributions to replace existing algorithms such as LIME or Shap. If the LLMs can perform better than or for cheaper than the existing algorithms, these approaches could be effective in practice.

#### Weaknesses
1. (Pareto Curve) Even if the LLMs are decisively better/worse than the existing explainability methods, the ultimate decision of the practitioner would also be based on how cheap/expensive it is to obtain the explanations. I would be interested to see an approximate cost-benefit tradeoff to have a better sense of whether the LLM-in-the-loop explainers are preferable in practice. The cost here could be with respect to $ compute and with respect to time. 

2. Authors focus on relatively simple tabular datasets, which I personally think limits the impact of the methodology and results. While I understand that it’s not yet possible to focus on many different domains (e.g. vision seems not possible yet); I believe it would have been possible to use existing text classifiers, as perturbations could still be communicated to existing models via prompts. This would increase the practicality and the value of the evaluation, in my view.

3. (Lack of sufficient experimental details) I find that the presentation of the experiments could be significantly improved. As it stands, there are a lot of missing details in the experiments section or the Appendix, which makes me feel less confident about the reliability of the results. I detail several points below. I believe most of these points could easily be addressed in the rebuttal phase, and I will be happy to revise my assessment during the rebuttal.

- 3.1 Importantly, I believe the authors should define their evaluation metrics; e.g., for metrics like PGI, PGU, RA, FA the authors refer to earlier papers without explicitly defining what they are. The reader should ideally be able to see the metrics without navigating to different papers.

- 3.2 I cannot find the hyperparameters of the explainers or the rationale for picking them. In particular, it’s unclear if the performance may or may not be explained by a poor choice of hyperparameters, as even the rationale of the hyperparameter choices for existing algorithms (LIME, SHAP etc.) are not presented in the paper. Since most of the results are meaningful in a relative sense (compared to the baselines), this is an important point to clarify.

- 3.3 Similarly, for reproducibility purposes, the details around the models used should be better provided. E.g. it’s unclear what optimizer is used to train the models, with which learning rate, whether early stopping is applied, and so on. This would surely raise reproducibility issues for follow-up work unless addressed.

- 3.4 The authors describe the process of parsing the response as `We first save each LLM query’s reply to a text file and use a script to extract the features.` I believe further details are needed to better understand this process. Specifically, what is the existing parsing strategy? Are the responses always parseable? What fraction of the time they are not parseable? 

- 3.5 The authors present ` LLMs accurately identify the most important feature` as a significant result (e.g. abstract `identify the most important feature with 72.19% accuracy,`), however for this specific task I do not see baselines. Why do the authors have baselines for faithfulness, but not for this specific task (apologies if I’m missing this and the result exists)? Specifically – how good are existing algorithms at identifying the most important feature?

- 3.6 There are claims I find unjustified. For instance, `The second approach significantly aids the LLM in discerning the most important features` – how can we claim this without any results in Page 6 under implementation details? If there is an experimental finding that supports this, please refer to the result. 

4. I’m slightly confused about the insights we can draw from the experiments. Specifically, the authors propose 3 different explanation strategies that seem to perform reasonably similarly. I understand the overall message that LLMs have the potential to be used as explainers. However, the confusing part to me is there are 3 algorithms presented, and it’s hard to understand which one is better or when. I’d appreciate it if the authors could provide a concise discussion around this.

#### Questions
1. How do the authors pick the hyperparameters for the baseline explainers?

2. Could the authors please explicitly define the metric they are using?

3. Could the authors please clarify the claim on Page 6 `The second approach significantly aids the LLM in discerning the most important features`?

4. Do the authors have any insights about the costs of the explanation methods, to inform practitioners about whether it is worth using LLMs in practice?

5. How well do the baselines perform in the most important feature identification tasks?

6. Is it possible to verify the effectiveness of these methods in text classification tasks?

### Review 3
Rating: 3: reject, not good enough
Confidence: 2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper proposes using language models to provide post-hoc explanations for other model decisions in four ways.

#### Strengths
This paper addresses an important problem.

#### Weaknesses
The critical weakness, in my view, is that the interpretability method itself is uninterpretable. When the task involves understanding language, this can be somewhat understood, like Bills et al.'s 2023 "Language models can explain neurons in language models." But this paper applies language models to ask them directly, "What are the most important features in determining the model's prediction?" And it does so on purely numerical datasets. It oversimplifies the task of interpretability, arbitrarily modeling logistic regression coefficients as fixed ground truths and using prediction gap -- but there are a million dramatically cheaper ways that they could have selected the most important features according to the same criteria.

Also, a notable limitation (if the more fundamental questions did not overshadow it) is that the models interpreted are all quite simple, the datasets are themselves simple, and more standard models for tabular data are not considered (but again, this is not the paper's primary limitation). Lastly, it seems presumptive to suggest that this approach is better than SHAP, at least without a deeper investigation into where this method outperforms it (and some discussion on why it ostensibly performs almost as poorly as randomly selecting features). These points are less important to me, but they are still worth raising.

#### Questions
1) What do you mean when you say the logistic regression model has "one layer of size 16"?
2) Can you elaborate on the motivation for this work - why did you feel that a language model would be an appropriate tool here?
3) When would you use this approach instead of LIME, which consistently performed better?
4) Can you give some examples where SHAP performed worst according to your metrics? What were the values produced? What were the correct metrics?

## Meta Reviews

### Meta Review 1
The submission explores the idea of using language models for interpretability, by using LLMs for posthoc explanations of other models. Four methods are introduced for this problem. Reviewers agree that this is an interesting direction, and highly impactful if can be made to work convincingly. However, at the current stage, reviewers believe it falls beneath the bar for acceptance. In particular, only relatively simple models
 are interpreted, and reviewers believe that simpler and much cheaper methods may work just as well.

## Decisions

Decision: Reject

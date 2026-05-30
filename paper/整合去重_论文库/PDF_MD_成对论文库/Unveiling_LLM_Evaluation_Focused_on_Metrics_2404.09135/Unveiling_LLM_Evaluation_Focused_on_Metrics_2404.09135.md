---
pdf: Unveiling_LLM_Evaluation_Focused_on_Metrics_2404.09135.pdf
source: MinerU API
batch_id: d6e8dbb5-b049-4ed8-8c56-40ee66b039f6
data_id: Unveiling_LLM_Evaluation_Focused_on_Metrics_2404.09135
parsed_at: 2026-05-23
---

# Unveiling LLM Evaluation Focused on Metrics: Challenges and Solutions

Taojun Hu Department of Biostatistics, Peking University and

Department of Biostatistics, Peking University Chongqing Big Data Research Institute, Peking University Beijing International Center for Mathematical Research, Peking University

April 16, 2024

## Abstract

Natural Language Processing (NLP) is witnessing a remarkable breakthrough driven by the success of Large Language Models (LLMs). LLMs have gained significant attention across academia and industry for their versatile applications in text generation, question answering, and text summarization. As the landscape of NLP evolves with an increasing number of domain-specific LLMs employing diverse techniques and trained on various corpus, evaluating performance of these models becomes paramount. To quantify the performance, it’s crucial to have a comprehensive grasp of existing metrics. Among the evaluation, metrics which quantifying the performance of LLMs play a pivotal role. This paper offers a comprehensive exploration of LLM evaluation from a metrics perspective, providing insights into the selection and interpretation of metrics currently in use. Our main goal is to elucidate their mathematical formulations and statistical interpretations. We shed light on the application of these metrics using recent Biomedical LLMs. Additionally, we offer a succinct comparison of these metrics, aiding researchers in selecting appropriate metrics for diverse tasks. The overarching goal is to furnish researchers with a pragmatic guide for effective LLM evaluation and metric selection, thereby advancing the understanding and application of these large language models.

Keywords: Large language models; Evaluation; Statistical interpretations; Metrics; Biomedical LLMs; Repositories

## 1 Introduction

ChatGPT, also namely GPT3.5, (Brown et al. 2020, Wang et al. 2022) has demonstrated its remarkable ability to generate coherent sequences of words and engage in conversational interactions. As the popularity of ChatGPT surged, quantities of large language models (LLMs) emerged rapidly. Researchers not only explore distinct model architectures and propose various fine-tuning methods to enhance LLM capabilities but also investigate ways to tailor LLMs to specific domains.

LLMs present a significant opportunity for tasks such as generating scientific texts, answering questions, and extracting core information from articles. For instance, amidst the daily influx of over 3000 new articles in peer-reviewed journals (Sayers et al. 2023), LLMs can swiftly extract key insights, aiding readers in navigating through vast amounts of medical literature. Furthermore, LLMs can potentially analyze symptoms described by patients to suggest diagnoses and treatment options, thus alleviating physicians’ workload and improving patient care, which is a useful application in medicine. These applications underscore two primary functionalities of LLMs: information retrieval and text generation. However, LLMs can also contribute to various other aspects of medical research and applications. Due to these advantages, today’s LLMs are attracting increasing attention across multiple fields. With the surge of novel LLMs, reviewing and evaluating existing LLMs is of great importance. Among evaluations, the intrinsic statistical interpretations are frequently neglected in current research and reviews.

The proliferation of LLMs has prompted the emergence of reviews aimed at providing insights into their development and potential applications. For instance, Naveed et al. (2023) reviewed LLMs from 2019, starting with T5, up to the latest releases in 2023, offering comprehensive references and comparisons. Wang et al. (2023) highlighted the promising applications of LLMs in addressing biomedical questions, while Chen et al. (2023) focused on evaluating biomedical LLMs with respect to benchmarks and summarization capabilities. While existing reviews generally discuss LLM structures and applications, evaluating LLMs is crucial for guiding their development and deployment but understudied. Evaluation encompasses various aspects, including downstream tasks, criteria, benchmark datasets, and metrics. Although Chang et al. (2023) surveyed LLM evaluation, comprehensive summarizing the metrics remains scarce. This work aims to fill this gap by providing a survey of contemporary LLM evaluation metrics, along with mathematical formulations and statistical explanations and practical guidance for implementation using open-source libraries. Our paper shed lights on the bridge between the existing LLM evaluations and statistics by exploring the statistical interpretations of the metrics. Additionally, we showcase how these metrics have been utilized in conjunction with published biomedical LLMs through illustrative examples. Our main contributions are four-folds:

• Summarizing and categorizing the metrics for LLM evaluation into three distinct types;

• Providing mathematical formulations and statistical interpretations for each metric, along with a comparative analysis to serve as a guide for LLM researchers;

• Identifying repositories containing the discussed metrics;

• Showcasing how these metrics and baseline datasets are applied in the evaluation of recently developed biomedical LLMs, facilitating further studies to keep alignment with previous models.

The article is structured as follows: Section 2 offers a concise overview of LLM evaluation criteria. Section 3 details the most utilized metrics in LLM evaluations, including their mathematical expressions and statistical interpretations, alongside a directory of repositories for implementing these metrics. Section 4 showcases the application of these metrics using biomedical LLMs as case studies, including the baseline datasets employed for evaluation. Section 5 discusses the pros and cons of the existing widely used metrics and stresses two major common problems that are often ignored: the imperfect gold standard issue and absent of statistical inference method. The paper concludes with Section 6, summarizing our findings and the limitations for this paper.

## 2 Evaluations for LLMs

We provide a brief overview of evaluation criteria for LLMs, which, although not the main focus of this paper, are essential for understanding critical development aspects of LLMs. With NLP’s long history, models have been developed for specific tasks, either supervised or unsupervised. Accuracy in generating a desired answer is a predominant focus in LLM evaluations. However, issues such as overfitting and ignoring detrimental aspects like unfairness or hallucination render accuracy an imperfect evaluation metric. Hallucination, gaining researchers’ attention recently, involves generating false or misleading information by well-trained LLMs, often due to biases in training data, leading to overconfident and inaccurate outputs. This overconfidence is closely linked to an overreliance on accuracyoriented training. To address these issues, it’s crucial to understand the key considerations and criteria in LLM evaluation. We discuss these evaluation criteria from various perspectives in this section.

Accuracy (Bengio et al. 2000, Morin & Bengio 2005) measures how well the LLM produces desired results, a primary performance concern. Typically, gold standard answers are used, or specialists are employed to assess LLM performance. High accuracy ensures optimal quality and unbiased predictions, aligning LLMs with user needs and instructions, making it a fundamental requirement.

Ethicality (Weidinger et al. 2021, Ganguli et al. 2022, Jobin et al. 2019) involves a broad range of concerns, including privacy protection, misinformation reduction, fairness, and transparency. Given LLMs are trained on large datasets that may include sensitive information or deceptive content, ethicality mandates LLMs to produce legal, safe, and ethical outputs. Ongoing research, transparent practices, and thoughtful policy-making are essential for ensuring LLMs’ positive societal contributions.

Fairness (Bolukbasi et al. 2016, Dixon et al. 2018, Hovy & Yang 2021, Selbst et al. 2019), a critical aspect of ethicality with significant social implications, demands equal treatment from LLM outputs, regardless of individual or group demographics. It requires bias mitigation to prevent discriminatory decisions, highlighted by the need for fairness in pronoun prediction in sentences like ” is a nurse,”. A fair system of LLMs is supposed to put no preference on ”he” or ”she” that suggests the sex directly. The criterion of fairness promotes unbiased system responses.

Generalization (Raffel et al. 2020, Hupkes et al. 2023, Lazaridou et al. 2021) indicates an LLM’s ability to adapt to unseen data, crucial for responding to diverse queries and understanding text generation mechanisms. Techniques like regularization and diverse dataset training enhance generalization, which is key for LLMs to comprehend language and context broadly.

Robustness (Wang et al. 2021, Goel et al. 2021, Goyal et al. 2023) describes an LLM’s resilience to errors, manipulations, or adversarial attacks, aiming for trustworthy and consistent outputs. Addressing this involves varied dataset training and adversarial methods to ensure performance stability and real-world application trustworthiness.

Reasoning (Valmeekam et al. 2022, Jin et al. 2023), or an LLM’s ability to logically infer or deduce information, is essential for applying learned knowledge to new contexts. This capability, requiring further research, underscores the need for LLMs to exhibit logical and causal reasoning.

Evaluating LLMs comprehensively requires examining not only accuracy but also ethicality, fairness, generalization, robustness, and reasoning. Each aspect is vital for creating intelligent LLMs that benefit society and users. Employing benchmark datasets is a common solution for comprehensive evaluation, with metric design playing a crucial role in assessing LLM capabilities, which we explore further in the next section.

## 3 Metrics

The metrics can be broadly categorized into three types. The first type, which assesses the ability to accurately classify texts into at least two labels, is the most prevalent. We refer to these as the Multiple-Classification (MC) metrics. They can be applied to various tasks with developed benchmark datasets. The second type, known as the Token-Similarity (TS) metrics, evaluates how well the generated texts align with the expected texts. Lastly, a metric specifically tailored for the Question-Answering task is the Question-Answering (QA) metrics. In the following sections, we will provide a detailed illustration of each metric along with its mathematical formulation. Meanwhile, we also explain for these metrics from a statistical perspective.

<table><tr><td>True/Prediction</td><td>Positive</td><td>Negative</td></tr><tr><td>Positive</td><td> $y _ { 1 1 } ( T P )$ </td><td> $y _ { 1 0 } ( F N )$ </td></tr><tr><td>Negative</td><td> $y _ { 0 1 } ( F N )$ </td><td> $y _ { 0 0 } ( T N )$ </td></tr></table>

Table 1: The contingency table for a two-label classification problem

## 3.1 Multiple-Classification metrics

The Multiple-Classification (MC) metrics assess how effectively the LLM classifies texts into multiple groups, with each group serving as a label. These metrics encompass Accuracy (Acc), Recall (R), Precision (P), and F1 scores (Goutte & Gaussier 2005), particularly in two-label classification scenarios. In multi-label classification, the micro-F1 and macro-F1 metrics (Ghamrawi & McCallum 2005) are commonly employed. To illustrate, let’s consider a two-label problem, distinguishing between ”positive” and ”negative” cases. Benchmark datasets provide the gold standard label for each case, while the LLM performs classification and generates predictions. This process results in a $2 \times 2$ chart (Table 1), with cells representing True Positive (TP), False Positive (FP), False Negative (FN), and True Negative (TN) instances. Thus, Accuracy (Acc) can be expressed as:

$$
\mathrm { A c c } = { \frac { T P + T N } { T P + F N + F P + T N } }\tag{1}
$$

The Recall, also known as Sensitivity or True Positive Rate, signifies the proportion of positive detections among the actual ”positive” instances. It gauges an LLM’s ability to identify positive instances. The formula for the Recall is given by:

$$
\mathrm { R e c a l l } = { \frac { \mathrm { T P } } { \mathrm { T P } + \mathrm { F N } } }\tag{2}
$$

Precision, also referred to the Positive Predictive Value, indicates the proportion of actual positive instances among all instances identified as positive. It measures an LLM’s precision in filtering out negative instances falsely labeled as positive. The Precision formula is:

$$
\mathrm { P r e c i s i o n } = { \frac { \mathrm { T P } } { \mathrm { T P } + \mathrm { F P } } }\tag{3}
$$

However, high Recall often corresponds to low Precision, and vice versa. The F1 score balances these two metrics using a simple harmonic mean operation:

$$
\mathrm { F 1 } = \frac { \mathrm { 2 } \times \mathrm { R e c a l l } \times \mathrm { P r e c i s i o n } } { \mathrm { R e c a l l } + \mathrm { P r e c i s i o n } }\tag{4}
$$

The F1 score ranges from 0 to 1, with F1= 1 indicating both perfect Recall and perfect Precision.

From a statistical perspective, the aforementioned metrics carry inherent probabilis tic interpretations. Before delving into their statistical interpretations, it’s important to briefly define the sample and population of these metrics, an aspect often overlooked by researchers. The population for LLMs refers to the global corpus on which the models are evaluated, while the sample comprises the test datasets. In most cases, the test datasets are assumed to be randomly sampled from the global corpus, allowing the metrics computed on them to represent the model’s performance on the global corpus.

Let’s consider the classification outcomes provided by the LLM denoted as X, and the true labels as Y , both binary variables within {0, 1}. The Accuracy metric represents $P ( X = Y ) = P ( X = 1 , Y = 1 ) + P ( X = 0 , Y = 0 )$ , while Recall denotes $P ( X = 1 \mid Y = 1 )$ and Precision denotes $P ( Y = 1 \mid X = 1 )$ . The F1-score means the harmonic mean of the previous two metric, that is $\frac { 2 } { 1 / P ( X { = } 1 | Y { = } 1 ) + 1 / P ( Y { = } 1 | X { = } 1 ) }$ . The Receiver Operating Characteristic (ROC) curve, along with the Area Under the Curve (AUC), offers a comprehensive assessment of a classifier or diagnostic tool. It illustrates all possible trade-offs between sensitivity and specificity across various decision cut-offs. Similarly, the Precision-Recall (PR) curve showcases the interplay between Precision and Recall under different cut-offs, with Recall on the x-axis and Precision on the y-axis. The area under the Precision-Recall curve (PRAUC) quantifies the classifier’s performance. Studies by Saito & Rehmsmeier (2015) have demonstrated that PRAUC can provide more informative insights with imbalanced datasets where the negatives far outnumber the positives. However, to esti mate AUC/PRAUC, a continuous biomarker for classification is necessary. Consequently, AUC/PRAUC evaluation may not be directly applicable to LLMs lacking such continuous biomarkers. Both the AUC and PRAUC offer comprehensive evaluations for LLMs without relying on specific cutoff values. Despite their potential advantages, many studies on LLMs have not reported AUC/PRAUC results, even when continuous biomarkers are available. This omission limits the comprehensiveness of evaluating LLM performance.

In multi-label cases, where there are more than two labels, the accuracy and two variants of the F1 score are widely used: micro-F1 and macro-F1. We illustrate the notations first. Suppose there are $L$ labels marked from 1 to $L ,$ then the number of instances that are classified as label i by the LLM but belong to the label $j$ is noted by $y _ { i j }$ . We have an $L \times L$ matrix with elements $\left( y _ { i j } \right) _ { 1 \le i \le L , \ 1 \le j \le L } .$ Then the simplest way to evaluate the LLM is the accuracy, that is

$$
{ \mathrm { A c c } } _ { \mathrm { m u l t i } } = { \frac { \sum _ { i = 1 } ^ { L } y _ { i i } } { \sum _ { i = 1 } ^ { L } \sum _ { j = 1 } ^ { L } y _ { i j } } }\tag{5}
$$

To overcome the multi-label confusion, both the macro-F1 score and micro-F1 score treat each label separately as a single classification problem. For example, for the instances which belong to the label i, the label i is regarded as the positive, and all the other labels are regarded as the negative. In other words, the $y _ { i i }$ is the true positive, $\textstyle \sum _ { j \neq i } y _ { i j }$ is the false positive, $\textstyle \sum _ { j \neq i } y _ { j i }$ is the false negative. The rest instances belong to the true negative. The micro-F1 harmonically averages the micro-precision and micro-recall. The micro-precision is

$$
{ \mathrm { m i c r o - p r e c i s i o n } } = { \frac { \mathrm { T o t a l ~ T P } } { \mathrm { T o t a l ~ T P + T o t a l ~ F P } } } = { \frac { \sum _ { i = 1 } ^ { L } y _ { i i } } { \sum _ { i = 1 } ^ { L } \left( y _ { i i } + \sum _ { j \neq i } y _ { i j } \right) } }\tag{6}
$$

While the micro-recall is

$$
{ \mathrm { m i c r o - r e c a l l } } = { \frac { \mathrm { T o t a l ~ T P } } { \mathrm { T o t a l ~ T P + T o t a l ~ F N } } } = { \frac { \sum _ { i = 1 } ^ { L } y _ { i i } } { \sum _ { i = 1 } ^ { L } \left( y _ { i i } + \sum _ { j \neq i } y _ { j i } \right) } }\tag{7}
$$

Then the micro-F1 is the harmonic mean of micro-recall and micro-precision, that is

$$
{ \mathrm { M i c r o - F 1 } } = { \frac { 2 \times { \mathrm { m i c r o - r e c a l l } } \times { \mathrm { m i c r o - p r e c i s i o n } } } { \mathrm { m i c r o - r e c a l l } } } + { \mathrm { m i c r o - p r e c i s i o n } }\tag{8}
$$

The macro-F1 evaluates the LLM in another way by averaging the class F1 for each label. For label i, the class F1 can be calculated by

$$
\mathrm { F 1 } _ { i } = \frac { 2 \left( \frac { y _ { i i } } { \sum _ { ( j \neq i ) } y _ { j i } + y _ { i i } } \right) \left( \frac { y _ { i i } } { \sum _ { j \neq i } y _ { i j } + y _ { i i } } \right) } { \left( \frac { y _ { i i } } { \sum _ { ( j \neq i ) } y _ { j i } + y _ { i i } } \right) + \left( \frac { y _ { i i } } { \sum _ { j \neq i } y _ { i j } + y _ { i i } } \right) }\tag{9}
$$

Then the macro-F1 is

$$
\mathrm { M a c r o - F 1 } = \frac { 1 } { L } \sum _ { i = 1 } ^ { L } \mathrm { F } 1 _ { i }\tag{10}
$$

The micro-F1 gives equal weight to each instance, which means it leans to the class with more instances, while the macro-F1 gives equal weight to each class.

From a statistical perspective, both micro-precision and micro-recall quantify the probability that predicted labels exactly match the true labels, symbolized as P (X = Y ). This is equivalent to the multi-label accuracy, implying that these metrics essentially measure the same aspect of model performance. The micro-F1 score, calculated as the harmonic mean of micro-precision and micro-recall, similarly reflects P (X = Y ). Consequently, micro-F1 does not offer a distinct advantage over accuracy in evaluating LLMs, as it essentially conveys the same information. This analysis presupposes that the true label space is the same with the classifier’s label space, sharing the same set of labels, as a common assumption in LLM evaluations. Contrastingly, the macro-F1 score takes a different approach by averaging the F1 scores of each class with equal weight, as denoted by the equation:

$$
{ \frac { 1 } { L } } \sum _ { i = 1 } ^ { L } { \frac { 2 } { 1 / P ( X = i \mid Y = i ) + 1 / P ( Y = i \mid X = i ) } } .\tag{11}
$$

Although this formula doesn’t directly translate to a simple probability expression, it addresses a critical limitation of accuracy metrics: their tendency to overlook classes with fewer samples. This feature makes macro-F1 a preferred metric for evaluating LLMs, as it ensures that all classes, regardless of size, are considered equally. The widespread adop tion of macro-F1 in LLM evaluations can be attributed to its ease of implementation and its ability to facilitate comparisons with previously developed models. Despite these considerations, more comprehensive evaluation methods, such as the ROC surface, remain underutilized in LLM assessments. These metrics, which can offer a more nuanced understanding of model performance in multi-label problems, have yet to become standard in the evaluation of LLMs.

## 3.2 Token-Similarity(TS) Metrics

Token-Similarity metrics encompass metrics that gauge the similarity between the texts generated by LLMs and the reference texts. They are instrumental in assessing how well LLMs can produce a desired sequence of words given contextual information. LLMs frequently employ these metrics to evaluate the quality of generated texts and their impact on tasks such as machine translation and text summarization. Key metrics in this category include Perplexity, BLEU (Bilingual Evaluation Understudy), ROUGE (Recall-Oriented Understudy for Gisting Evaluation)-1 or 2, ROUGE-L, and BertScore, METEOR (Metric for Evaluation of Translation with Explicit Ordering). They primarily assess LLM performance at the token level.

To narrow our focus, we omit the tokenization process performed by LLMs and assume that the texts are already adequately tokenized. We proceed with the understanding that the LLM generates texts as follows: Given the context $\left\{ X _ { - t } \right\} _ { t = T } ^ { 0 } .$ , where T represents the total length of the context, the LLM predicts a sequence of tokens after this contextual information. These contextual texts could be either the prompt or the original texts that need to be summarized in LLMs. Let the predicted sequence of tokens by the LLM be represented as $\{ x _ { i } \} _ { i = 1 } ^ { N }$ . To assess the quality of the generated texts, benchmark datasets provide a reference sequence of tokens $\{ y _ { j } \} _ { j = 1 } ^ { M }$ , which serves as the gold standard.

LLMs assign probabilities to each token in the vocabulary and select tokens based on specific criteria to compose the desired generated texts. We denote the probabilities assigned by the LLM as $\hat { P } ( \cdot )$ . Perplexity, introduced by Brown et al. (1988), focuses on measuring the occurrence probability of the reference sequence $\{ y _ { j } \} _ { j = 1 } ^ { M }$ according to the LLM, formulated as:

$$
\begin{array} { r } { \mathrm { P e r p l e x i t y } = 2 ^ { - \frac { 1 } { M } \sum _ { j = 1 } ^ { M } \log _ { 2 } \hat { P } ( y _ { j } ) } , } \end{array}\tag{12}
$$

where $\hat { P } ( y _ { j } )$ represents the probability assigned by the LLM to the $j \mathrm { - t h }$ token in the reference sequence.

From a statistical perspective, Perplexity is inversely proportional to the likelihood

function $\textstyle \prod _ { j = 1 } ^ { M } { \hat { P } } ( y _ { j } )$ , thus lower perplexity values indicate better performance by the LLM in predicting the data.

BLEU proposed by Papineni et al. (2001) evaluates the LLM based on n-grams. An n-gram is a re-grouping of token-level sequences to measure the co-occurrences of tokens. Given a sequence $\{ x _ { i } \} _ { i = 1 } ^ { N }$ , an n-gram indicates subsequences of length n as,

$$
\{ ( x _ { i } , \ x _ { i + 1 } , \cdot \cdot \cdot , \ x _ { i + n - 1 } ) \} _ { i = 1 } ^ { N - n + 1 }
$$

Two n-grams match if every element matches in the given order, i.e., $x _ { i } = y _ { j } , \ x _ { i + 1 } =$ $y _ { j + 1 } , \ \cdot \cdot \cdot , \ x _ { i + n - 1 } = y _ { j + n - 1 }$ . Then, the Precision between the generated texts $\{ x _ { i } \} _ { i = 1 } ^ { N }$ and the reference texts $\{ y _ { j } \} _ { j = 1 } ^ { M }$ at the n-gram level is given by:

$$
{ \begin{array} { r l } { { \mathrm { P r e c i s i o n } } _ { n } } & { = { \frac { \mathrm { N u m b e r ~ o f ~ m a t c h i n g ~ n ^ { - } g r a m s } } { \mathrm { T o t a l ~ n u m b e r ~ o f ~ n ^ { - } g r a m s ~ i n ~ g e n e r a t e d ~ t e x t } } } } \\ & { \qquad = { \frac { \mathrm { N u m b e r ~ o f ~ m a t c h i n g ~ n ^ { - } g r a m s } } { N - n + 1 } } } \end{array} }\tag{13}
$$

Token-level matching is a special case, equivalent to 1-gram matching. BLEU introduces a Brevity Penalty to penalize cases where the generated text is too short and only partially matches the reference text, neglecting key information. The Brevity Penalty is:

$$
\mathrm { B r e v i t y ~ P e n a l t y } ( \mathrm { B P } ) = \operatorname* { m i n } \left( 1 , { \frac { \mathrm { T o k e n s ~ i n ~ g e n e r a t e d ~ t e x t } } { \mathrm { T o k e n s ~ i n ~ r e f e r e n c e ~ t e x t } } } \right) = \operatorname* { m i n } \left( 1 , { \frac { N } { M } } \right)\tag{14}
$$

The first type of BLEU employs the formula:

$$
{ \mathrm { B L E U } } = { \mathrm { B P } } \times \exp \left( \log \left( { \mathrm { P r e c i s i o n } } _ { 1 } \right) \right)\tag{15}
$$

Another type combines precision for n-grams with orders 1-4:

$$
{ \mathrm { B L E U } } = { \mathrm { B P } } \times \exp \left( { \frac { 1 } { 4 } } \sum _ { n = 1 } ^ { 4 } \log { \mathrm { P r e c i s i o n } _ { n } } \right)\tag{16}
$$

The BLEU also possesses its statistical meaning. We assume the event that a token in the corpus to appear in the reference text is denoted by $A _ { 1 }$ , and to appear in the generated text is denoted by $B _ { 1 }$ . Similarly, the events for the n-gram appearing in two texts are denoted by $A _ { n }$ and $B _ { n }$ . Then the Precision within the BLEU in the first form denotes $P ( A _ { 1 } \cap B _ { 1 } \mid B _ { 1 } )$ and the BLEU is proportional to it. The second form of BLEU is proportional to the $\prod _ { i = 1 } ^ { 4 } P ( A _ { i } \cap B _ { i } \mid B _ { i } )$ . BLEU primarily emphasizes precision but overlooks evaluations of recall. LLMs may achieve high BLEU scores by capturing partial information from the reference texts, even if failing to predict the entirety of the reference texts accurately. This limitation makes BLEU less suitable for researchers who require LLMs to capture all relevant information from the context and accurately predict the reference texts.

Different from BLEU, ROUGE-n and ROUGE-L (Lin 2004) are n-gram level F1 scores. ROUGE-n can be calculated as:

$$
{ \begin{array} { r l } { { \mathrm { P r e c i s i o n - n } } } & { = { \frac { \mathrm { N u m b e r ~ o f ~ m a t c h i n g ~ n ^ { - } g r a m s } } { \mathrm { T o t a l ~ n u m b e r ~ o f ~ n ^ { - } g r a m s ~ i n ~ g e n e r a t e d ~ t e x t } } } } \\ & { = { \frac { \mathrm { N u m b e r ~ o f ~ m a t c h i n g ~ n ^ { - } g r a m s } } { N - n + 1 } } } \end{array} }\tag{17}
$$

$$
\mathrm { R e c a l l - n } = { \frac { \mathrm { N u m b e r ~ o f ~ m a t c h i n g ~ n \mathrm { - } g r a m s } } { M - n + 1 } }
$$

$$
{ \begin{array} { r l } { { \mathrm { R O U G E - n } } } & { = { \frac { 2 \times { \mathrm { P r e c i s i o n } } - { \mathrm { n } } \times { \mathrm { R e c a l l } } - { \mathrm { n } } } { \mathrm { P r e c i s i o n } - { \mathrm { n } } + { \mathrm { R e c a l l } } - { \mathrm { n } } } } } \end{array} }
$$

The most common ROUGE-n metrics are ROUGE-1 and ROUGE-2. ROUGE-L extends ROUGE-n by focusing on finding the Longest Common Subsequence (LCS), denoted as nLCS. ROUGE-L is calculated as the harmonic mean of Precision and Recall:

$$
{ \mathrm { R O U G E - L } } = { \frac { 2 \times { \frac { \mathrm { n L C S } } { M } } \times { \frac { \mathrm { n L C S } } { N } } } { { \frac { \mathrm { n L C S } } { M } } + { \frac { \mathrm { n L C S } } { N } } } } .\tag{18}
$$

The ROUGE-n can be expressed as a realization for

$$
\frac { 2 } { 1 / P ( A _ { n } \cap B _ { n } \mid B _ { n } ) + 1 / P ( A _ { n } \cap B _ { n } \mid A _ { n } ) } ,
$$

while the ROUGE-L can be similarly defined.

METEOR proposed by Banerjee & Lavie (2005) is a metric based on ROUGE but aims to mitigate the effects of different word variants and synonymy issues. Initially, both the reference texts and the generated texts are tokenized. Then, METEOR applies stemming to reduce the words to their base form in both texts. The stemmed sequences are denoted as $\{ x _ { i } ^ { \prime } \} _ { i = 1 } ^ { N }$ and $\left\{ y _ { j } ^ { \prime } \right\} _ { j = 1 } ^ { M }$ . ROUGE is then applied to the stemmed sequences of texts, with ROUGE-1 being the most commonly used metric for METEOR. Upon ROUGE, METEOR also introduces a penalty term to reward the LLM for generating sequences of tokens in the same order as they appeared in the reference texts. The penalty is calculated based on the number of chunks. Let $\left\{ \boldsymbol { z } _ { k } \right\} _ { k = 1 } ^ { K }$ represent the matched tokens ordered by their appearances in the generated texts. If a sequence of these tokens appears adjacently in both the generated and reference texts, they are combined into a chunk. For example, if the reference texts are $^ { \circ } \mathrm { I t }$ is a guide to action” and the generated texts are ”It is a guide to directing the learners”, then the matched tokens include ”It”, ”is”, ”a”, ”guide”, and ”to”. However, since the combination ”It is a guide to” appears in both texts in the same order, it is considered a chunk. The penalty is calculated as:

$$
{ \mathrm { P e n a l t y } } = \left( { \frac { \# { \mathrm { c h u n k s } } } { \# { \mathrm { m a t c h e d ~ t o k e n s } } } } \right) ^ { 3 } ,\tag{19}
$$

where $\#$ denotes the number. In an extreme case where the generated texts exactly match the reference texts, the number of chunks is only 1. A lower penalty indicates a better match between the generated and reference texts. When there are no bi-grams or longer

matches, the number of chunks is equal to the number of matched tokens, suggesting the Penalty increases to 1. METEOR combines ROUGE and the Penalty as follows:

$$
\mathrm { M E T E O R } = \mathrm { R O U G E } \mathrm { - } 1 ( 1 - \beta \mathrm { P e n a l t y } ) ,\tag{20}
$$

where $\beta$ is selected as 0.5 by Banerjee & Lavie (2005). In the worst-case scenario where there are no bi-grams or longer matches, METEOR’s performance can decrease to half of that of ROUGE-1. Conversely, when there are mostly longer matches, METEOR closely aligns with ROUGE-1. Unlike ROUGE, METEOR tackles issues related to synonymy and word variants, prioritizing longer matches between the generated and reference texts.

BertScore proposed by Zhang et al. (2019) also measures token similarities but not based on the matching of n-grams; instead, it relies on BERT (Devlin et al. 2018) pretrained embeddings. Initially, it loads the BERT embeddings. For each token in the generated texts $\{ x _ { i } \} _ { i = 1 } ^ { N }$ and the reference texts $\{ y _ { j } \} _ { j = 1 } ^ { M }$ , the corresponding embeddings can be found within the BERT embeddings, each represented as fixed-length vectors denoted by $\{ \widehat { \mathbf { x } } _ { \mathbf { i } } ^ { \mathbf { e } } \} _ { i = 1 } ^ { N }$ and $\left\{ \widehat { \mathbf { y } } _ { \mathbf { j } } ^ { \mathbf { e } } \right\} _ { j = 1 } ^ { M }$ . These sequences of vectors are then zipped to a single vector representing the two texts. The usual approach is to element-wise average:

$$
\widehat { \mathbf { x } } ^ { \mathbf { e } } = \frac { 1 } { N } \sum _ { i = 1 } ^ { N } \widehat { \mathbf { x _ { i } ^ { e } } } , \quad \widehat { \mathbf { y } } ^ { \mathbf { e } } = \frac { 1 } { M } \sum _ { j = 1 } ^ { M } \widehat { \mathbf { y _ { j } ^ { e } } } .\tag{21}
$$

BertScore then calculates the cosine similarity of these two vectors as a measure of the similarity between the reference texts and the generated texts:

$$
{ \mathrm { B e r t S c o r e } } = { \frac { { \widehat { x } } ^ { e } \cdot { \widehat { y } } ^ { e } } { \left| \left| { \widehat { x } } ^ { e } \right| \right| \cdot \left| \left| { \widehat { y } } ^ { e } \right| \right| } } .\tag{22}
$$

The cosine similarity measures the angle between two vectors projected onto a multidimensional space, regardless of their size. It ranges from -1 to 1, with a higher value indicating greater similarity between the generated and reference texts. It aids in gauging the semantic similarities among documents, thus widely used in NLP. Given that cosine similarity maps the similarity of two vectors to the space [−1, 1], statistical methods designed to measure correlation with high-dimensional random vectors can be applied. These include Pearson’s correlation, Canonical Correlation (Borga 2001), Distance Correlation (Sz´ekely & Rizzo 2013), and others.

METEOR and BertScore represent more complex evaluation metrics for LLMs compared to those previously discussed. Their complexity arises from the reliance on external linguistic information, making a straightforward statistical explanation challenging. Unlike simpler metrics, METEOR and BertScore effectively address synonymy issues, offering a significant advantage in evaluating LLMs for nuanced linguistic understanding. These metrics have thus become widely adopted in the assessment of LLMs. It is noteworthy that, with the exception of perplexity, all metrics discussed in this section favor higher scores as indicators of superior LLM performance.

## 3.3 Question-Answering(QA) Metrics

Different from general classification problems or text matching problems, the Question-Answering task is a special task that involves fuzzy matching issues, making the application of previous metrics not straightforward. The QA task requires the LLM to identify the answer to a specific question given a contextual passage. The answer for this question is usually located in the contextual passage, so the QA task is transformed to predict the starting position and the ending position in the contextual passage, assuming the middle part is the answer. This is a restricted double-task prediction problem. An LLM often predicts the starting position and ending position separately and excludes combinations that are unreasonable, such as when the predicted ending position is before the predicted starting position. Among the remaining combinations, the LLM ranks them by the overall prediction probability for the starting position and ending position. Suppose there are overall N questions, each with a contextual passage. For question i, the LLM places predictions in order from the most likely one to the less likely one, denoted by $( s _ { i 1 } , \ e _ { i 1 } ) , \ ( s _ { i 2 } , e _ { i 2 } ) , \ \cdot \cdot \cdot ,$ where $s , e$ denotes the starting position and ending position located in the original text respectively. Assume the gold standard answer is located in the passage with starting position and ending position as $\left( \boldsymbol { s } _ { i k _ { i } } , \ \boldsymbol { e } _ { i k _ { i } } \right)$ , where $k _ { i }$ is the rank of it among all predictions given by the LLM. There are three most popular metrics for these $\mathrm { Q A }$ tasks. Strict Accuracy (SaCC) (Tsatsaronis et al. 2015) is the proportion of completely correct predictions:

$$
\mathrm { S a C C } = \frac { \# \left\{ k _ { i } = 1 \right\} } { N } ,\tag{23}
$$

here $k _ { i } = 1$ means the optimal prediction ranking first among all the predictions is exactly the gold standard answer.

Lenient Accuracy (LaCC) (Tsatsaronis et al. 2015) is a more relaxed metric that allows partially correct predictions:

$$
\mathrm { L a C C } = { \frac { \# \left\{ k _ { i } \leq 5 \right\} } { N } } .\tag{24}
$$

With Lenient Accuracy, if the top-5 predictions contain the gold standard answer, it is regarded as correct predictions.

Mean Reciprocal Rank (MRR) (Tsatsaronis et al. 2015) comprehensively evaluates the LLM, considering not only the optimal predictions but also suboptimal predictions perfectly matching the gold standard answer. It is the average of the reciprocal ranks of the correct predictions:

$$
\mathrm { M R R } = \frac { 1 } { N } \sum _ { i = 1 } ^ { N } \frac { 1 } { k _ { i } } .\tag{25}
$$

<table><tr><td>Metrics</td><td>Statistical interpretation</td></tr><tr><td>Accuracy</td><td>P(X = Y )</td></tr><tr><td>Recall</td><td> $P ( X = 1 \mid Y = 1 )$ </td></tr><tr><td>Precision</td><td> $P ( Y = 1 \mid X = 1 )$ </td></tr><tr><td>F1-score</td><td> $2 / ( 1 / P ( X = 1 \mid Y = 1 ) + 1 / P ( Y = 1 \mid X = 1 ) )$ </td></tr><tr><td>Micro-F1</td><td> $P ( X = Y )$ </td></tr><tr><td>Macro-F1</td><td> $1 / L \sum _ { i = 1 } ^ { L } 2 / ( 1 / P ( X = i \mid Y = i ) + 1 / P ( Y = i \mid X = i ) )$ </td></tr><tr><td>Perplexity</td><td> $( \mathrm { L i k e l i h o o d } ( \{ y _ { i } \} _ { i = 1 } ^ { M } ) ) ^ { - 1 / M }$ </td></tr><tr><td>BLEU</td><td> $P ( A _ { 1 } \cap B _ { 1 } \mid B _ { 1 } )$ </td></tr><tr><td>ROUGE-n</td><td> $2 / ( 1 / P ( A _ { n } \cap B _ { n } \mid B _ { n } ) + 1 / P ( A _ { n } \cap B _ { n } \mid A _ { n } ) )$ </td></tr><tr><td>ROUGE-L</td><td> $2 / ( 1 / P ( A _ { L C S } \cap B _ { L C S } \mid B _ { L C S } ) + 1 / P ( A _ { L C S } \cap B _ { L C S } \mid A _ { L C S } ) )$ </td></tr><tr><td>METEOR</td><td></td></tr><tr><td>BertScore</td><td></td></tr><tr><td>SaCC</td><td> $P ( R ( S ) = 1 )$ </td></tr><tr><td>LaCC</td><td> $P ( R ( S ) \leq 5 )$ </td></tr><tr><td>MRR</td><td> $E ( 1 / R ( S ) )$ </td></tr></table>

Table 2: Statistical interpretations for each metric

All the three metrics are highly related to the rank statistics. Assume the rank statistics for the gold standard answer is R(S), then we have $S a C C = P ( R ( S ) = 1 )$ , LaCC = $P ( R ( S ) < = 5 )$ , and $M R R = E ( 1 / R ( S ) )$ , where E(·) denotes the expectation. We summarize the statistical interpretations for all above metrics in Table 2.

So far, we have classified the most popular metrics used to evaluate the LLMs into three categories: Multi-Classification, Token-Similarity, and Question-Answering metrics, and introduced the mathematical formulations and statistical implications for each metric.

To facilitate researchers in applying these metrics, we list the existing packages or functions for these methods in Python in Table 3. While there may be other metrics used to measure the efficiency of LLMs, most of them are less popular compared to the above metrics, so we did not provide their mathematical formulations. In the next section, we will showcase their applications with recently published LLMs in biomedical and global fields.

## 4 Application of these metrics: examples with biomedical LLMs

We highlight the use of metrics through recently developed biomedical LLMs, spanning a broad spectrum from specialized biomedical to general corpora. The advent of pre-trained biomedical LLMs enhances capabilities such as abstract summarization within biomedical texts, specific question answering, and task completion relevant to medical contexts, like associating treatments with symptoms or clinical histories. Our literature review spanned databases like Google Scholar, PubMed, ArXiV, and ACM digital libraries, focusing on works from 2018 onwards that significantly relate to biomedical LLMs using keywords like ”Medical/Biomedical/Clinical/Radiology” and ”Large Language Model/Pre-trained model”. While not exhaustive, our selection is representative, focusing on widely referenced works. We delineated applications of these metrics in biomedical LLMs, compiling training and benchmark datasets, and outlined the tasks applicable to each LLM, aiding researchers in benchmarking their models against the previous competitive LLMs.

We provide a concise listing of biomedical LLMs in the Supplementary Information B due to the length of our paper, detailing their training datasets alongside the downstream tasks mentioned in the paper for each model, showcasing their performance capabilities.

<table><tr><td>Classification</td><td>Metrics</td><td>Repositories or Python functions</td></tr><tr><td rowspan="6">Multi-Classification</td><td>Accuracy</td><td>sklearn.metrics.accuracy_score</td></tr><tr><td>Recall</td><td>sklearn.metrics.recall_score</td></tr><tr><td>Precision</td><td>sklearn.metrics.precision_score</td></tr><tr><td>F1-score</td><td>sklearn.metrics.f1 _score</td></tr><tr><td>Micro-F1</td><td>sklearn.metrics.f1_score(average=&#x27;micro&#x27;)</td></tr><tr><td></td><td>Macro-F1 sklearn.metrics.f1_score(average=&#x27;macro&#x27;)</td></tr><tr><td rowspan="6">Token-Similarities</td><td>Perplexity nltk.perplexity</td><td></td></tr><tr><td>BLEU</td><td>nltk.translate.bleu_score</td></tr><tr><td></td><td>ROUGE-n https://github.com/pltrdy/rouge</td></tr><tr><td></td><td>ROUGE-L https://github.com/pltrdy/rouge</td></tr><tr><td>METEOR</td><td>nltk.translate.meteor_score;</td></tr><tr><td></td><td>https://github.com/mcjoshi/qgeval</td></tr><tr><td></td><td>BertScore</td><td>https://github.com/Tiiiger/bertscore</td></tr><tr><td rowspan="3">Question-Answering LaCC</td><td>SaCC</td><td>Manual Implementation</td></tr><tr><td></td><td>Manual Implementation</td></tr><tr><td>MRR</td><td>Manual Implementation</td></tr></table>

Table 3: Repositories or Python functions to realized the metrics

Before diving into these biomedical LLMs, we offer a concise overview of downstream tasks in LLMs, which play an important role in evaluating the performance of the LLMs. We left the overview of the downstream tasks in the Supplementary Information A. From the listing of existing biomedical LLMs, the PubMed and PMC corpus emerge as the most frequently utilized training datasets across the biomedical LLM landscape, reflecting their extensive adoption for model training. We also found that most LLMs showcase their capabilities across multiple downstream tasks but not a single one.

We further illustrate the application of various metrics in evaluating these biomedical LLMs, as detailed in Table 4. A checkbox in the table indicates the utilization of a spe cific metric for evaluation in the corresponding LLM. Beyond the aforementioned metrics, additional metrics are occasionally employed in some studies, though they represent a minor fraction of the papers reviewed. Among them, MC metrics are predominantly favored across all three categories of metrics due to their straightforward applicability to established benchmark datasets. For TS metrics, ROUGE-n and ROUGE-L are the most commonly used, acting as F1-scores at the token level between reference and generated texts. QA metrics are often applied together. Despite being specifically designed for Question Answering tasks, there’s a noticeable trend towards employing MC metrics with redesigned QA benchmarks as an alternative to QA-specific metrics. For instance, both BioInstruct (Tran et al. 2023) and RoBERTa (Liu et al. 2021) include QA tasks in their evaluations but rely solely on MC metrics and BERTScore. This preference for simpler MC metrics facilitates alignment with other LLMs but might neglect the inherent challenges LLMs face in fully comprehending human language and ensuring the fluency and comprehensibility of generated text. Therefore, a comprehensive evaluation incorporating a broad spectrum of metrics is advisable for a thorough assessment of an LLM’s capabilities.

<table><tr><td>Biomedical LLMs Acc Recall Precision</td><td></td><td></td><td></td><td></td><td></td><td>F1/macro-F1 BLEU ROUGE-1/2/L METEOR BERT-Score</td><td></td><td></td><td>MRR SaCC</td><td>LaCC</td><td>Additional</td></tr><tr><td>BioBERT</td><td></td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td></tr><tr><td>BioGPT</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>BioLinkBERT</td><td>✓</td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>BioMedGPT</td><td>✓</td><td></td><td></td><td></td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td></td></tr><tr><td>BioMegatron</td><td></td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td>✓</td><td></td></tr><tr><td>ClinicalBERT</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>DoT5</td><td>✓</td><td></td><td></td><td>✓</td><td>√</td><td>✓</td><td></td><td></td><td></td><td></td><td>NEM, cheXbert</td></tr><tr><td>ELECTRAMed</td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>GatorTronGPT</td><td></td><td>✓</td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td>Pearson- Correlation</td></tr><tr><td>MedPaLM</td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>MedPaLM2</td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>PubMedBERT</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>BLURB</td></tr><tr><td>SciBERT</td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>SciFive</td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>GenCompareSum</td><td></td><td></td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>RadBERT</td><td>✓</td><td></td><td></td><td>✓</td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>BioBERTsum</td><td></td><td></td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>BioBART</td><td></td><td>✓</td><td></td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td><td></td><td></td><td></td></tr><tr><td>KeBioSum</td><td></td><td></td><td></td><td>✓</td><td></td><td>√</td><td>✓</td><td></td><td></td><td></td><td></td></tr><tr><td>Biolnstruct</td><td></td><td>✓</td><td>✓</td><td>√</td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td></tr><tr><td>BioRoBERTa</td><td></td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>RoBERTa</td><td>✓</td><td></td><td></td><td>✓</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>BioELMo</td><td>√</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

Table 4: The metrics used in the published paper for each LLM

In addition to the metrics, we have also summarized the benchmark datasets employed in these biomedical LLMs, which is left in the Supplementary Information C. Among all the downstream tasks, NER, RE, QA and TS are the focal points for biomedical LLMs. Datasets such as BC5CDR, NCBI Disease, MedNLI, and CHEMPROT are frequently used, each by more than five LLMs, indicating their widespread adoption for evaluating model performance in these specific tasks.

## 5 Strengths and weakness on the metrics

The metrics in language model evaluations are categorized into Multiple-Classification (MC), Token-Similarity (TS), and Question-Answering (QA) types. MC metrics, primarily used in multiple classification tasks, are prevalent in assessing LLM performance. While MC metrics offer simplicity and alignment in LLM evaluations, they depend heavily on well-structured benchmark datasets with each subject assigned to a single label, assuming perfect labeling. This reliance on perfect labeling presents inherent limitations: firstly, creating such datasets demands significant resources; secondly, MC metrics struggle with subjects having ambiguous or multiple labels, necessitating more advanced metrics; finally, the assumption of perfect labeling overlooks the challenges of real-world data without human-assigned labels, potentially impacting LLM performance and generalization.

Moreover, an interesting parallel exists between MC metrics and the metrics used in diagnostic studies, particularly in their emphasis on sensitivity and specificity, along with ROC/AUC analysis. While diagnostic studies might prioritize sensitivity and specificity, LLM evaluations often focus on Recall and Precision, analogous to sensitivity and Positive Predictive Value (PPV), respectively. Challenges arise in the context of unbalanced datasets, where a classifier could misleadingly show high performance metrics by overpredicting the majority class. Supposing a dataset with only a few subjects labeled as negative, an extreme classifier predicting all the subjects as positive would obtain both high recall and precision, accordingly high F1-score. However, it is not a classifier that should be preferred. Thus it highlights the inadequacy of using conventional metrics like F1-score without considering the balance between classes or employing techniques like resampling or weighted scores. The aforementioned example of imbalanced data underscores the importance for researchers to meticulously select metrics tailored to the data structure. Additionally, for LLMs predicting only the label, a thorough evaluation with the pair of sensitivity/specificity and the pair of Recall/Prediction as well as the F1-score is recommended. For LLMs predicting labels with continuous biomarkers, methods that are free of the cut-off points can provide a more comprehensive assessment of model performance. When dealing with binary labels, consideration of AUC/PRAUC is essential, while for models with ordinal multiple labels, novel approaches such as ROC surface analysis are preferred. However, these methods remain underexplored in the context of existing LLMs. Additionally, the lack of an efficient selection threshold complicates the determination of LLM performance adequacy, as F1-score lacks robust statistical properties. Addressing these evaluation challenges necessitates the development of new metrics, possibly inspired by diagnostic studies, to ensure statistical reliability in LLM assessments.

Compared to MC metrics, TS metrics assess the quality of generated texts by comparing them with original texts or aligning the provided answers accordingly. Among TS metrics, ROUGE-n and ROUGE-L (Lin 2004) are particularly prominent, effectively extending the F1-score to evaluate token-level similarity between reference and generated texts. However, these metrics assign equal importance to every token, not distinguishing between contentcritical words (nouns, verbs, adjectives) and less impactful particles, potentially skewing the assessment of a text’s semantic quality. Additionally, ROUGE metrics struggle with word variants and synonymy, making it challenging to capture the essence of longer texts comprehensively. Although METEOR (Banerjee & Lavie 2005) and BERTScore (Zhang et al. 2019) aim to address these issues, they heavily rely on external techniques or pre-defined parameters. Exploring the development of more reliable metrics to evaluate token similarities and conducting a comprehensive evaluation with various metrics for LLMs would be intriguing.

QA metrics, tailored for Question Answering tasks, presume that answers reside within the original texts, necessitating meticulous benchmark dataset design. Traditional QA metrics, however, fall short in the era of abundant dialogue-based QA data, as they merely assess an LLM’s ability to pinpoint answer boundaries within texts. Such metrics overlook ambiguously correct responses, where slight variations in answer positioning might still provide valid answers, underscoring the need for an automatic, versatile metric capable of handling free-form dialogue-type QA data without the constraints of traditional evaluation methods.

A major issue across all metric categories is imperfect labeling, known as an imperfect gold standard, which signifies inaccuracies or unreliability in reference labels or texts used for evaluation. Imperfect labeling manifests as misassigned labels in MC metrics, flawed reference texts in TS metrics, and ambiguously correct responses in QA metrics. It may stem from human error or the use of unverified techniques. While pre-trained LLMs like GPT-4 are increasingly employed to generate gold standards, they may introduce hallucinations, where LLMs may generate false or misleading information and the generated results are not aligned with user requests. Sensitivity analysis and statistical adjustment methods, primarily developed for diagnostic studies, offer solutions to mitigate bias arising from imperfect gold standards. Umemneku Chikere et al. (2019) conducted a systematic review of methods addressing imperfect gold standard bias in diagnostic studies. Studies by Alonzo & Pepe (2005) and To Duc et al. (2016) employ imputation methods to mitigate bias, while others like (Brenner 1996, Emerson et al. 2018, Albert 2009) assume access to sensitivity and specificity information of the reference standard, leveraging it to adjust for bias. Yet, these methods are underutilized in LLM research. Overlooking such bias may lead researchers to draw incorrect conclusions. Borrowing ideas from correcting imperfect gold standard bias could offer new insights for evaluations in LLMs.

Another issue, particularly concerning TS metrics, is the absence of statistical inference methods. Most metrics solely provide a performance value for models without accompanying confidence intervals to gauge the reliability of the estimate. The intricate structures of texts may obscure the necessity of proposing statistical inference methods for these metrics. Nonetheless, this absence renders the metrics unreliable, as researchers cannot address the uncertainty surrounding the models’ performance. A substantial variation may coincide with high LLM performance; however, such models may prove unsuitable for real-world applications.

## 6 Conclusions

Our study comprehensively reviews the most frequently utilized metrics in the evaluation of LLMs, showcasing their application through recently published biomedical LLMs. We aggregate benchmark datasets and downstream tasks associated with each LLM, marking the first comprehensive summary of metrics, benchmark datasets, and their evaluations in LLMs, complete with detailed mathematical formulations, statistical interpretations, and repositories for these metrics. This study aims to guide researchers in biomedical or other domain-specific/general LLMs in selecting appropriate benchmark datasets and evaluation metrics, facilitating better evaluation of their LLMs and comparison with competing models.

However, our study encounters several challenges. Firstly, while we encompass the most common evaluation metrics found in published literature, detailing every existing metric for all potential use cases is beyond our scope due to its complexity and the extensive manpower required. However, the metrics and recommendations we provide are representative and valuable. Secondly, we do not directly correlate benchmark datasets with specific metrics due to the flexibility in their application: a single dataset may be assessed using various metrics, and different LLMs might employ different metrics even when using the same dataset. Additionally, benchmark datasets may be adapted for particular tasks and metrics depending on the researchers’ objectives. Thus, prescribing fixed metric usage for each benchmark dataset is neither feasible nor advisable. Nevertheless, a future study offering a comprehensive recommendation with detailed application scenarios would be of great interest.

## Acknowledgments

This research was funded by supported by National Key R&D Program of China $( \mathrm { N o . }$ 2021YFF0901400) and Novo Nordisk $\mathrm { A } / \mathrm { S }$

## Conflict of Interest

The authors report there are no competing interests to declare.

## SUPPLEMENTARY MATERIAL

Title: Supplementary Information. (pdf)

## References

(n.d.).

Abacha, A. B., Agichtein, E., Pinter, Y. & Demner-Fushman, D. (2017), Overview of the medical question answering task at trec 2017 liveqa., in ‘TREC’, pp. 1–12.

Abacha, A. B. & Demner-Fushman, D. (2019), On the summarization of consumer health questions, in ‘Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics’, pp. 2228–2234.

Abacha, A. B., Mrabet, Y., Sharp, M., Goodwin, T. R., Shooshan, S. E. & Demner-Fushman, D. (2019), Bridging the gap between consumers’ medication questions and trusted answers., in ‘MedInfo’, pp. 25–29.

Albert, P. S. (2009), ‘Estimating diagnostic accuracy of multiple binary tests with an imperfect reference standard’, Statistics in medicine 28(5), 780–797.

Alonzo, T. A. & Pepe, M. S. (2005), ‘Assessing accuracy of a continuous screening test in the presence of verification bias’, Journal of the Royal Statistical Society Series C: Applied Statistics 54(1), 173–190.

Alsentzer, E., Murphy, J. R., Boag, W., Weng, W.-H., Jin, D., Naumann, T. & McDermott, M. (2019), ‘Publicly available clinical bert embeddings’, arXiv preprint arXiv:1904.03323

Banerjee, S. & Lavie, A. (2005), Meteor: An automatic metric for mt evaluation with improved correlation with human judgments, in ‘Proceedings of the acl workshop on intrinsic and extrinsic evaluation measures for machine translation and/or summarization’, pp. 65–72.

Basaldella, M., Liu, F., Shareghi, E. & Collier, N. (2020), ‘Cometa: A corpus for medical entity linking in the social media’, arXiv preprint arXiv:2010.03295 .

Beltagy, I., Lo, K. & Cohan, A. (2019), ‘Scibert: A pretrained language model for scientific text’, arXiv preprint arXiv:1903.10676 .

Bengio, Y., Ducharme, R. & Vincent, P. (2000), ‘A neural probabilistic language model’, Advances in neural information processing systems 13.

Bishop, J., Xie, Q. & Ananiadou, S. (2022), Gencomparesum: a hybrid unsupervised summarization method using salience, in ‘Proceedings of the 21st workshop on biomedical language processing’, pp. 220–240.

Blagec, K., Dorffner, G., Moradi, M., Ott, S. & Samwald, M. (2022), ‘A global analysis of metrics used for measuring performance in natural language processing’, arXiv preprint arXiv:2204.11574 .

Bolukbasi, T., Chang, K.-W., Zou, J. Y., Saligrama, V. & Kalai, A. T. (2016), ‘Man is to computer programmer as woman is to homemaker? debiasing word embeddings’, Advances in neural information processing systems 29.

Borga, M. (2001), ‘Canonical correlation: a tutorial’, On line tutorial http://people. imt. liu. se/magnus/cca 4(5).

Bravo, A., Pi˜nero, J., Queralt-Rosinach, N., Rautschka, M. & Furlong, L. \` I. (2015), ‘Extraction of relations between genes and diseases from text and large-scale data analysis: implications for translational research’, BMC bioinformatics 16, 1–17.

Brenner, H. (1996), ‘Correcting for exposure misclassification using an alloyed gold standard’, Epidemiology pp. 406–410.

Brown, P. F., Cocke, J., Della Pietra, S. A., Della Pietra, V. J., Jelinek, F., Mercer, R. L. & Roossin, P. (1988), A statistical approach to language translation, in ‘Coling Budapest 1988 Volume 1: International Conference on Computational Linguistics’.

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A. et al. (2020), ‘Language models are few-shot learners’, Advances in neural information processing systems 33, 1877–1901.

Chang, Y., Wang, X., Wang, J., Wu, Y., Zhu, K., Chen, H., Yang, L., Yi, X., Wang, C., Wang, Y. et al. (2023), ‘A survey on evaluation of large language models’, arXiv preprint arXiv:2307.03109 .

Chen, Q., Du, J., Hu, Y., Keloth, V. K., Peng, X., Raja, K., Zhang, R., Lu, Z. & Xu, H. (2023), ‘Large language models in biomedical natural language processing: benchmarks, baselines, and recommendations’, arXiv preprint arXiv:2305.16326 .

Cohan, A., Dernoncourt, F., Kim, D. S., Bui, T., Kim, S., Chang, W. & Goharian, N. (2018), ‘A discourse-aware attention model for abstractive summarization of long documents’, arXiv preprint arXiv:1804.05685 .

Collier, N., Ohta, T., Tsuruoka, Y., Tateisi, Y. & Kim, J.-D. (2004), Introduction to the bio entity recognition task at jnlpba, in ‘Proceedings of the International Joint Workshop on Natural Language Processing in Biomedicine and its Applications (NLPBA/BioNLP)’, pp. 73–78.

Devlin, J., Chang, M.-W., Lee, K. & Toutanova, K. (2018), ‘Bert: Pre-training of deep

bidirectional transformers for language understanding’, arXiv preprint arXiv:1810.04805

Dixon, L., Li, J., Sorensen, J., Thain, N. & Vasserman, L. (2018), Measuring and mitigating unintended bias in text classification, in ‘Proceedings of the 2018 AAAI/ACM Conference on AI, Ethics, and Society’, pp. 67–73.

Do˘gan, R. I., Leaman, R. & Lu, Z. (2014), ‘Ncbi disease corpus: a resource for disease name recognition and concept normalization’, Journal of biomedical informatics 47, 1–10.

Du, Y., Li, Q., Wang, L. & He, Y. (2020), ‘Biomedical-domain pre-trained language model for extractive summarization’, Knowledge-Based Systems 199, 105964.

Emerson, S. C., Waikar, S. S., Fuentes, C., Bonventre, J. V. & Betensky, R. A. (2018), ‘Biomarker validation with an imperfect reference: Issues and bounds’, Statistical methods in medical research 27(10), 2933–2945.

Ganguli, D., Lovitt, L., Kernion, J., Askell, A., Bai, Y., Kadavath, S., Mann, B., Perez, E., Schiefer, N., Ndousse, K. et al. (2022), ‘Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned’, arXiv preprint arXiv:2209.07858 .

Gerner, M., Nenadic, G. & Bergman, C. M. (2010), ‘Linnaeus: a species name identification system for biomedical literature’, BMC bioinformatics 11(1), 1–17.

Ghamrawi, N. & McCallum, A. (2005), Collective multi-label classification, in ‘Proceedings of the 14th ACM international conference on Information and knowledge management’, pp. 195–200.

Goel, K., Rajani, N., Vig, J., Tan, S., Wu, J., Zheng, S., Xiong, C., Bansal, M. & R´e,

C. (2021), ‘Robustness gym: Unifying the nlp evaluation landscape’, arXiv preprint arXiv:2101.04840 .

Goutte, C. & Gaussier, E. (2005), A probabilistic interpretation of precision, recall and fscore, with implication for evaluation, in ‘European conference on information retrieval’, Springer, pp. 345–359.

Goyal, S., Doddapaneni, S., Khapra, M. M. & Ravindran, B. (2023), ‘A survey of adversarial defenses and robustness in nlp’, ACM Computing Surveys 55(14s), 1–39.

Gu, Y., Tinn, R., Cheng, H., Lucas, M., Usuyama, N., Liu, X., Naumann, T., Gao, J. & Poon, H. (2021), ‘Domain-specific language model pretraining for biomedical natural language processing’, ACM Transactions on Computing for Healthcare (HEALTH) 3(1), 1–23.

Gururangan, S., Marasovi´c, A., Swayamdipta, S., Lo, K., Beltagy, I., Downey, D. & Smith, N. A. (2020), ‘Don’t stop pretraining: Adapt language models to domains and tasks’, arXiv preprint arXiv:2004.10964 .

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D. & Steinhardt, J. (2020), ‘Measuring massive multitask language understanding’, arXiv preprint arXiv:2009.03300 .

Herrero-Zazo, M., Segura-Bedmar, I., Mart´ınez, P. & Declerck, T. (2013), ‘The ddi corpus: An annotated corpus with pharmacological substances and drug–drug interactions’, Journal of biomedical informatics 46(5), 914–920.

Hou, Y., Xia, Y., Wu, L., Xie, S., Fan, Y., Zhu, J., Qin, T. & Liu, T.-Y. (2022), ‘Discovering drug–target interaction knowledge from biomedical literature’, Bioinformatics 38(22), 5100–5107.

Hovy, D. & Yang, D. (2021), The importance of modeling social factors of language: Theory and practice, in ‘Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies’, pp. 588– 602.

Hupkes, D., Giulianelli, M., Dankers, V., Artetxe, M., Elazar, Y., Pimentel, T., Christodoulopoulos, C., Lasri, K., Saphra, N., Sinclair, A. et al. (2023), ‘A taxonomy and review of generalization research in nlp’, Nature Machine Intelligence 5(10), 1161–1174.

Jahan, I., Laskar, M. T. R., Peng, C. & Huang, J. (2023), ‘A comprehensive evaluation of large language models on benchmark biomedical text processing tasks’, arXiv preprint arXiv:2310.04270 .

Jin, D., Pan, E., Oufattole, N., Weng, W.-H., Fang, H. & Szolovits, P. (2021), ‘What disease does this patient have? a large-scale open domain question answering dataset from medical exams’, Applied Sciences 11(14), 6421.

Jin, Q., Dhingra, B., Cohen, W. W. & Lu, X. (2019), ‘Probing biomedical embeddings from language models’, arXiv preprint arXiv:1904.02181 .

Jin, Q., Dhingra, B., Liu, Z., Cohen, W. W. & Lu, X. (2019), ‘Pubmedqa: A dataset for biomedical research question answering’, arXiv preprint arXiv:1909.06146 .

Jin, Z., Chen, Y., Leeb, F., Gresele, L., Kamal, O., Zhiheng, L., Blin, K., Adauto, F. G., Kleiman-Weiner, M., Sachan, M. et al. (2023), Cladder: Assessing causal reasoning in language models, in ‘Thirty-seventh Conference on Neural Information Processing Systems’.

Jobin, A., Ienca, M. & Vayena, E. (2019), ‘The global landscape of ai ethics guidelines’, Nature machine intelligence 1(9), 389–399.

Ju, Z., Chakravorty, S., He, X., Chen, S., Yang, X. & Xie, P. (2020), ‘Coviddialog: Medical dialogue datasets about covid-19’.

Karimi, S., Metke-Jimenez, A., Kemp, M. & Wang, C. (2015), ‘Cadec: A corpus of adverse drug event annotations’, Journal of biomedical informatics 55, 73–81.

Kim, J.-D., Ohta, T., Tateisi, Y. & Tsujii, J. (2003), ‘Genia corpus—a semantically annotated corpus for bio-textmining’, Bioinformatics 19(suppl 1), i180–i182.

Krallinger, M., Rabal, O., Akhondi, S. A., P´erez, M. P., Santamar´ıa, J., Rodr´ıguez, G. P., Tsatsaronis, G., Intxaurrondo, A., L´opez, J. A., Nandal, U. et al. (2017), Overview of the biocreative vi chemical-protein interaction track, in ‘Proceedings of the sixth BioCreative challenge evaluation workshop’, Vol. 1, pp. 141–146.

Krallinger, M., Rabal, O., Leitner, F., Vazquez, M., Salgado, D., Lu, Z., Leaman, R., Lu, Y., Ji, D., Lowe, D. M. et al. (2015), ‘The chemdner corpus of chemicals and drugs and its annotation principles’, Journal of cheminformatics 7(1), 1–17.

Krithara, A., Mork, J. G., Nentidis, A. & Paliouras, G. (2023), ‘The road from manual to automatic semantic indexing of biomedical literature: a 10 years journey’, Frontiers in Research Metrics and Analytics 8.

Krithara, A., Nentidis, A., Bougiatiotis, K. & Paliouras, G. (2023), ‘Bioasq-qa: A manually curated corpus for biomedical question answering’, Scientific Data 10(1), 170.

Lazaridou, A., Kuncoro, A., Gribovskaya, E., Agrawal, D., Liska, A., Terzi, T., Gimenez, M., de Masson d’Autume, C., Kocisky, T., Ruder, S. et al. (2021), ‘Mind the gap: Assessing temporal generalization in neural language models’, Advances in Neural Information Processing Systems 34, 29348–29363.

Lee, J., Yoon, W., Kim, S., Kim, D., Kim, S., So, C. H. & Kang, J. (2020), ‘Biobert: a pre-trained biomedical language representation model for biomedical text mining’, Bioinformatics 36(4), 1234–1240.

Li, J., Sun, Y., Johnson, R. J., Sciaky, D., Wei, C.-H., Leaman, R., Davis, A. P., Mattingly, C. J., Wiegers, T. C. & Lu, Z. (2016), ‘Biocreative v cdr task corpus: a resource for chemical disease relation extraction’, Database 2016.

Limsopatham, N. & Collier, N. (2016), Normalising medical concepts in social media texts by learning semantic representation, in ‘Proceedings of the 54th annual meeting of the association for computational linguistics (volume 1: long papers)’, pp. 1014–1023.

Lin, C.-Y. (2004), Rouge: A package for automatic evaluation of summaries, in ‘Text summarization branches out’, pp. 74–81.

Liu, F., Liu, Q., Bannur, S., P´erez-Garc´ıa, F., Usuyama, N., Zhang, S., Naumann, T., Nori, A., Poon, H., Alvarez-Valle, J. et al. (2023a), ‘Compositional zero-shot domain transfer with text-to-text models’, arXiv preprint arXiv:2303.13386 .

Liu, F., Liu, Q., Bannur, S., P´erez-Garc´ıa, F., Usuyama, N., Zhang, S., Naumann, T., Nori, A., Poon, H., Alvarez-Valle, J. et al. (2023b), ‘Compositional zero-shot domain transfer with text-to-text models’, arXiv preprint arXiv:2303.13386 .

Liu, Z., Lin, W., Shi, Y. & Zhao, J. (2021), A robustly optimized bert pre-training approach with post-training, in ‘China National Conference on Chinese Computational Linguistics’, Springer, pp. 471–484.

Lo, K., Wang, L. L., Neumann, M., Kinney, R. & Weld, D. S. (2019), ‘S2orc: The semantic scholar open research corpus’, arXiv preprint arXiv:1911.02782 .

Luo, R., Sun, L., Xia, Y., Qin, T., Zhang, S., Poon, H. & Liu, T.-Y. (2022), ‘Biogpt: generative pre-trained transformer for biomedical text generation and mining’, Briefings in Bioinformatics 23(6), bbac409.

Luo, Y., Zhang, J., Fan, S., Yang, K., Wu, Y., Qiao, M. & Nie, Z. (2023), ‘Biomedgpt: Open multimodal generative pre-trained transformer for biomedicine’, arXiv preprint arXiv:2308.09442 .

Miolo, G., Mantoan, G. & Orsenigo, C. (2021a), ‘Electramed: a new pre-trained language representation model for biomedical nlp’, arXiv preprint arXiv:2104.09585 .

Miolo, G., Mantoan, G. & Orsenigo, C. (2021b), ‘Electramed: a new pre-trained language representation model for biomedical nlp’, arXiv preprint arXiv:2104.09585 .

Mohan, S. & Li, D. (2019), ‘Medmentions: A large biomedical corpus annotated with umls concepts’, arXiv preprint arXiv:1902.09476 .

Morin, F. & Bengio, Y. (2005), Hierarchical probabilistic neural network language model, in ‘International workshop on artificial intelligence and statistics’, PMLR, pp. 246–252.

Naveed, H., Khan, A. U., Qiu, S., Saqib, M., Anwar, S., Usman, M., Barnes, N. & Mian, A. (2023), ‘A comprehensive overview of large language models’, arXiv preprint arXiv:2307.06435 .

Nye, B., Li, J. J., Patel, R., Yang, Y., Marshall, I. J., Nenkova, A. & Wallace, B. C. (2018), A corpus with multi-level annotations of patients, interventions and outcomes to support language processing for medical literature, in ‘Proceedings of the conference. Association for Computational Linguistics. Meeting’, Vol. 2018, NIH Public Access, p. 197.

Pafilis, E., Frankild, S. P., Fanini, L., Faulwetter, S., Pavloudi, C., Vasileiadou, A., Ar vanitidis, C. & Jensen, L. J. (2013), ‘The species and organisms resources for fast and accurate identification of taxonomic names in text’, PloS one 8(6), e65390.

Pal, A., Umapathi, L. K. & Sankarasubbu, M. (2022), Medmcqa: A large-scale multisubject multi-choice dataset for medical domain question answering, in ‘Conference on Health, Inference, and Learning’, PMLR, pp. 248–260.

Pampari, A., Raghavan, P., Liang, J. & Peng, J. (2018), ‘emrqa: A large corpus for question answering on electronic medical records’, arXiv preprint arXiv:1809.00732 .

Papineni, K., Roukos, S., Ward, T. & Zhu, W. (2001), ‘A method for automatic evaluation of machine translation”’, the Proceedings of ACL-2002, ACL, Philadelphia, PA, July 2002 .

Phan, L. N., Anibal, J. T., Tran, H., Chanana, S., Bahadroglu, E., Peltekian, A. & Altan-Bonnet, G. (2021), ‘Scifive: a text-to-text transformer model for biomedical literature’, arXiv preprint arXiv:2106.03598 .

Poon, H., Naumann, T., Zhang, S. & Gonz´alez Hern´andez, J. (2023), Precision health in the age of large language models, in ‘Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining’, pp. 5825–5826.

Pradhan, S., Elhadad, N., South, B. R., Martinez, D., Christensen, L. M., Vogel, A.,

Suominen, H., Chapman, W. W. & Savova, G. K. (2013), ‘Task 1: Share/clef ehealth evaluation lab 2013.’, CLEF (working notes) 1179.

Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., Zhou, Y., Li, W. & Liu, P. J. (2020), ‘Exploring the limits of transfer learning with a unified text-to-text transformer’, The Journal of Machine Learning Research 21(1), 5485–5551.

Rajpurkar, P., Jia, R. & Liang, P. (2018), ‘Know what you don’t know: Unanswerable questions for squad’, arXiv preprint arXiv:1806.03822 .

Rajpurkar, P., Zhang, J., Lopyrev, K. & Liang, P. (2016), ‘Squad: 100,000+ questions for machine comprehension of text’, arXiv preprint arXiv:1606.05250 .

Romanov, A. & Shivade, C. (2018), ‘Lessons from natural language inference in the clinical domain’, arXiv preprint arXiv:1808.06752 .

Saito, T. & Rehmsmeier, M. (2015), ‘The precision-recall plot is more informative than the roc plot when evaluating binary classifiers on imbalanced datasets’, PloS one 10(3), e0118432.

Savery, M., Abacha, A. B., Gayen, S. & Demner-Fushman, D. (2020), ‘Question-driven summarization of answers to consumer health questions’, Scientific Data 7(1), 322.

Sayers, E. W., Bolton, E. E., Brister, J. R., Canese, K., Chan, J., Comeau, D. C., Farrell, C. M., Feldgarden, M., Fine, A. M., Funk, K. et al. (2023), ‘Database resources of the national center for biotechnology information in 2023’, Nucleic acids research 51(D1), D29–D38.

Selbst, A. D., Boyd, D., Friedler, S. A., Venkatasubramanian, S. & Vertesi, J. (2019),

Fairness and abstraction in sociotechnical systems, in ‘Proceedings of the conference on fairness, accountability, and transparency’, pp. 59–68.

Shin, H.-C., Zhang, Y., Bakhturina, E., Puri, R., Patwary, M., Shoeybi, M. & Mani, R. (2020), ‘Biomegatron: Larger biomedical domain language model’, arXiv preprint arXiv:2010.06060 .

Singhal, K., Azizi, S., Tu, T., Mahdavi, S. S., Wei, J., Chung, H. W., Scales, N., Tanwani, A., Cole-Lewis, H., Pfohl, S. et al. (2022a), ‘Large language models encode clinical knowledge’, arXiv preprint arXiv:2212.13138 .

Singhal, K., Azizi, S., Tu, T., Mahdavi, S. S., Wei, J., Chung, H. W., Scales, N., Tanwani, A., Cole-Lewis, H., Pfohl, S. et al. (2022b), ‘Large language models encode clinical knowledge’, arXiv preprint arXiv:2212.13138 .

Singhal, K., Tu, T., Gottweis, J., Sayres, R., Wulczyn, E., Hou, L., Clark, K., Pfohl, S., Cole-Lewis, H., Neal, D. et al. (2023), ‘Towards expert-level medical question answering with large language models’, arXiv preprint arXiv:2305.09617 .

Smith, L., Tanabe, L. K., Ando, R. J. n., Kuo, C.-J., Chung, I.-F., Hsu, C.-N., Lin, Y.-S., Klinger, R., Friedrich, C. M., Ganchev, K. et al. (2008), ‘Overview of biocreative ii gene mention recognition’, Genome biology 9, 1–19.

So˘gancıo˘glu, G., Ozt¨urk, H. &¨ Ozg¨ur, A. (2017), ‘Biosses: a semantic sentence similarity¨ estimation system for the biomedical domain’, Bioinformatics 33(14), i49–i58.

Srivastava, A., Rastogi, A., Rao, A., Shoeb, A. A. M., Abid, A., Fisch, A., Brown, A. R., Santoro, A., Gupta, A., Garriga-Alonso, A. et al. (2022), ‘Beyond the imitation game: Quantifying and extrapolating the capabilities of language models’, arXiv preprint arXiv:2206.04615 .

Stubbs, A., Kotfila, C. & Uzuner, O. (2015), ‘Automated systems for the de-identification¨ of longitudinal clinical narratives: Overview of 2014 i2b2/uthealth shared task track 1’, Journal of biomedical informatics 58, S11–S19.

Stubbs, A. & Uzuner, O. (2015), ‘Annotating longitudinal clinical narratives for de-¨ identification: The 2014 i2b2/uthealth corpus’, Journal of biomedical informatics 58, S20–S29.

Sun, W., Rumshisky, A. & Uzuner, O. (2013a), ‘Annotating temporal information in clinical narratives’, Journal of biomedical informatics 46, S5–S12.

Sun, W., Rumshisky, A. & Uzuner, O. (2013b), ‘Evaluating temporal relations in clinical text: 2012 i2b2 challenge’, Journal of the American Medical Informatics Association 20(5), 806–813.

Sz´ekely, G. J. & Rizzo, M. L. (2013), ‘The distance correlation t-test of independence in high dimension’, Journal of Multivariate Analysis 117, 193–213.

To Duc, K., Chiogna, M. & Adimari, G. (2016), ‘Bias–corrected methods for estimating the receiver operating characteristic surface of continuous diagnostic tests’.

Touvron, H., Lavril, T., Izacard, G., Martinet, X., Lachaux, M.-A., Lacroix, T., Rozi\`ere, B., Goyal, N., Hambro, E., Azhar, F. et al. (2023), ‘Llama: Open and efficient foundation language models’, arXiv preprint arXiv:2302.13971 .

Tran, H., Yang, Z., Yao, Z. & Yu, H. (2023), ‘Bioinstruct: Instruction tuning of large language models for biomedical natural language processing’, arXiv preprint arXiv:2310.19975 .

Tsatsaronis, G., Balikas, G., Malakasiotis, P., Partalas, I., Zschunke, M., Alvers, M. R., Weissenborn, D., Krithara, A., Petridis, S., Polychronopoulos, D. et al. (2015), ‘An overview of the bioasq large-scale biomedical semantic indexing and question answering competition’, BMC bioinformatics 16(1), 1–28.

Umemneku Chikere, C. M., Wilson, K., Graziadio, S., Vale, L. & Allen, A. J. (2019), ‘Diagnostic test evaluation methodology: a systematic review of methods employed to evaluate diagnostic tests in the absence of gold standard–an update’, PLoS One 14(10), e0223832.

Uzuner, O., Luo, Y. & Szolovits, P. (2007), ‘Evaluating the state-of-the-a¨ rt in automatic de-identification’, Journal of the American Medical Informatics Association 14(5), 550– 563.

Uzuner, O., South, B. R., Shen, S. & DuVall, S. L. (2011), ‘2010 i2b2/va challen ¨ ge on concepts, assertions, and relations in clinical text’, Journal of the American Medical Informatics Association 18(5), 552–556.

Valmeekam, K., Olmo, A., Sreedharan, S. & Kambhampati, S. (2022), ‘Large language models still can’t plan (a benchmark for llms on planning and reasoning about change)’, arXiv preprint arXiv:2206.10498 .

Van Mulligen, E. M., Fourrier-Reglat, A., Gurwitz, D., Molokhia, M., Nieto, A., Trifiro, G., Kors, J. A. & Furlong, L. I. (2012), ‘The eu-adr corpus: annotated drugs, diseases, targets, and their relationships’, Journal of biomedical informatics 45(5), 879–884.

Wang, B., Xie, Q., Pei, J., Chen, Z., Tiwari, P., Li, Z. & Fu, J. (2023), ‘Pre-trained language models in biomedical domain: A systematic survey’, ACM Computing Surveys 56(3), 1–52.

Wang, L. L., Lo, K., Chandrasekhar, Y., Reas, R., Yang, J., Burdick, D., Eide, D., Funk, K., Katsis, Y., Kinney, R. et al. (2020), ‘Cord-19: The covid-19 open research dataset’, ArXiv .

Wang, X., Wang, H. & Yang, D. (2021), ‘Measure and improve robustness in nlp models: A survey’, arXiv preprint arXiv:2112.08313 .

Wang, Y., Afzal, N., Fu, S., Wang, L., Shen, F., Rastegar-Mojarad, M. & Liu, H. (2020), ‘Medsts: a resource for clinical semantic textual similarity’, Language Resources and Evaluation 54, 57–72.

Wang, Y., Kordi, Y., Mishra, S., Liu, A., Smith, N. A., Khashabi, D. & Hajishirzi, H. (2022), ‘Self-instruct: Aligning language model with self generated instructions’, arXiv preprint arXiv:2212.10560 .

Weidinger, L., Mellor, J., Rauh, M., Griffin, C., Uesato, J., Huang, P.-S., Cheng, M., Glaese, M., Balle, B., Kasirzadeh, A. et al. (2021), ‘Ethical and social risks of harm from language models’, arXiv preprint arXiv:2112.04359 .

Wu, C., Zhang, X., Zhang, Y., Wang, Y. & Xie, W. (2023), ‘Pmc-llama: Further finetuning llama on medical papers’, arXiv preprint arXiv:2304.14454 .

Xie, Q., Bishop, J. A., Tiwari, P. & Ananiadou, S. (2022), ‘Pre-trained language models with domain knowledge for biomedical extractive summarization’, Knowledge-Based Systems 252, 109460.

Xu, G., Rong, W., Wang, Y., Ouyang, Y. & Xiong, Z. (2021), ‘External features enriched model for biomedical question answering’, BMC bioinformatics 22(1), 272.

Yan, A., McAuley, J., Lu, X., Du, J., Chang, E. Y., Gentili, A. & Hsu, C.-N. (2022), ‘Radbert: Adapting transformer-based language models to radiology’, Radiology: Artificial Intelligence 4(4), e210258.

Yang, X., Bian, J., Fang, R., Bjarnadottir, R. I., Hogan, W. R. & Wu, Y. (2020), ‘Iden tifying relations of medications with adverse drug events using recurrent convolutional neural networks and gradient boosting’, Journal of the American Medical Informatics Association 27(1), 65–72.

Yasunaga, M., Leskovec, J. & Liang, P. (2022), ‘Linkbert: Pretraining language models with document links’, arXiv preprint arXiv:2203.15827 .

Yuan, H., Yuan, Z., Gan, R., Zhang, J., Xie, Y. & Yu, S. (2022), ‘Biobart: Pretraining and evaluation of a biomedical generative language model’, arXiv preprint arXiv:2204.03905

Zeng, A., Liu, X., Du, Z., Wang, Z., Lai, H., Ding, M., Yang, Z., Xu, Y., Zheng, W., Xia, X. et al. (2022), ‘Glm-130b: An open bilingual pre-trained model’, arXiv preprint arXiv:2210.02414 .

Zeng, G., Yang, W., Ju, Z., Yang, Y., Wang, S., Zhang, R., Zhou, M., Zeng, J., Dong, X., Zhang, R. et al. (2020), Meddialog: Large-scale medical dialogue datasets, in ‘Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)’, pp. 9241–9250.

Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q. & Artzi, Y. (2019), ‘Bertscore: Evaluating text generation with bert’, arXiv preprint arXiv:1904.09675 .
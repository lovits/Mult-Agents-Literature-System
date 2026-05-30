# ARE LARGE LANGUAGE MODELS POST HOC EXPLAINERS?

Anonymous authors

Paper under double-blind review

## ABSTRACT

Large Language Models (LLMs) are increasingly used as powerful tools for a plethora of natural language processing (NLP) applications. A recent innovation, in-context learning (ICL), enables LLMs to learn new tasks by supplying a few examples in the prompt during inference time, thereby eliminating the need for model fine-tuning. While LLMs have been utilized in several applications, their applicability in explaining the behavior of other models remains relatively unexplored. Despite the growing number of new explanation techniques, many require white-box access to the model and/or are computationally expensive, highlighting a need for next-generation post hoc explainers. In this work, we present the first framework to study the effectiveness of LLMs in explaining other predictive models. More specifically, we propose a novel framework encompassing multiple prompting strategies: i) Perturbation-based ICL, ii) Prediction-based ICL, iii) Instruction-based ICL, and iv) Explanation-based ICL, with varying levels of information about the underlying ML model and the local neighborhood of the test sample. We conduct extensive experiments with real-world benchmark datasets to demonstrate that LLM-generated explanations perform on par with state-of-the-art post hoc explainers using their ability to leverage ICL examples and their internal knowledge in generating model explanations. On average, across four datasets and two ML models, we observe that LLMs identify the most important feature with 72.19% accuracy, indicating promising avenues for further research into LLMbased explanation frameworks within explainable artificial intelligence (XAI).

## 1 INTRODUCTION

Over the past decade, machine learning (ML) models have become ubiquitous across various industries and applications. With their increasing use in critical applications (e.g., healthcare, financial systems, and crime forecasting), it becomes essential to ensure that ML developers and practitioners understand and trust their decisions. To this end, several approaches (Ribeiro et al., 2016; 2018; Smilkov et al., 2017; Sundararajan et al., 2017; Lundberg & Lee, 2017; Shrikumar et al., 2017) have been proposed in explainable artificial intelligence (XAI) literature to generate explanations for understanding model predictions. However, these explanation methods are highly sensitive to changes in their hyperparameters (Yeh et al., 2019; Bansal et al., 2020), require access to the underlying black-box ML model (Lundberg & Lee, 2017; Ribeiro et al., 2016), and/or are often computationally expensive (Situ et al., 2021), thus impeding reproducibility and the trust of relevant stakeholders.

More recently, generative models such as Large Language Models (LLMs) (Radford et al., 2017) have steered ML research into new directions and shown exceptional capabilities, allowing them to surpass state-of-the-art models at complex tasks like machine learning translation (Hendy et al., 2023), language understanding (Brown et al., 2020), commonsense reasoning (Wei et al., 2022b; Krishna et al., 2023), and coding tasks (Bubeck et al., 2023). However, there is very little work on systematically analyzing the reliability of LLMs as explanation methods. While recent research has used LLMs to explain what patterns in a text cause a neuron to activate, they simply explain correlations between the network input and specific neurons and do not explain what causes model behavior at a mechanistic level (Bills et al., 2023). Thus, the ability of LLMs to act as reliable explainers and improve the understanding of ML models lacks sufficient exploration.

![](images/32f35ae8938945dee7c6f151035eb895a4ddeba7835da3ee1a3be8f571a0c677.jpg)  
Figure 1: Overview of our framework. Given a dataset and model to explain, we provide 1) different prompting strategies to generate explanations using LLMs, 2) functions to parse LLM-based explanations, 3) utility functions to support new LLMs, and 4) diverse performance metrics to evaluate the faithfulness of explanations.

Present work. In this work, we present the first framework to study the effectiveness of LLMs in explaining other predictive models (see Fig. 1). More specifically, we introduce four broad prompting strategies — Perturbation-based ICL, Prediction-based ICL, Instruction-based ICL, and Explanation-based ICL — for generating post hoc explanations using LLMs. Our first three strategies entail providing local neighborhood samples and labels of a given instance whose prediction we want to explain, before asking an LLM to identify features that are key drivers in the model’s predictions. In our last approach, we leverage the in-context learning (ICL) (Liu et al., 2023b) behavior of LLMs by providing a small set of instances and their corresponding explanations (output by state-ofthe-art post hoc explanation methods) as input to an LLM and ask it to generate feature importancebased explanations for new samples. We also explore different prompting and design choices, such as increasing the level of information in each, to generate more faithful explanations using LLMs.

We conduct extensive experimentation with four benchmark datasets, two black-box models, and two GPT models to analyze the efficacy of our proposed framework. Our empirical studies reveal the following key findings. 1) LLMs, on average, accurately identify the most important feature (top-??=1) with 72.19% accuracy across different datasets, with performance drop for larger values of top-?? features. 2) LLMs can mimic the behavior of six state-of-the-art post hoc explanation methods using the proposed Explanation-based ICL prompting strategy and only four ICL samples. On average, LLMs behave as post hoc explainers by providing explanations that are on par with existing methods, such as LIME and gradient-based methods, in terms of their faithfulness. 3) LLMs struggle to retrieve relevant information from longer prompts, resulting in a decrease in the faithfulness of the explanations generated using a large set of ICL samples. 4) Our proposed framework paves the way for a new paradigm in XAI research, where LLMs can aid in explaining black-box model predictions.

## 2 RELATED WORKS

Our work lies at the intersection of post hoc explanations, large language models, and in-context learning, which we discuss below.

Post Hoc Explanations. The task of understanding model predictions has become increasingly in tricate with the growing popularity of complex ML models (Doshi-Velez & Kim, 2017) due to their inherent black box nature, which makes it difficult to interpret their internal reasoning. To this end, a plethora of feature attribution methods (commonly referred to as post hoc explanation methods) have been proposed to provide explanations for these models’ predictions. These explanations are predominantly presented in the form of feature attributions, which highlight the importance of each input feature on the model’s prediction. Broadly, post hoc explainers can be divided into perturbationbased and gradient-based methods. While perturbation-based methods (Ribeiro et al., 2016; Lundberg & Lee, 2017; Zeiler & Fergus, 2014) leverage perturbations of the given instance to construct an interpretable approximation of the black-box model behavior, gradient-based methods (Smilkov et al., 2017; Sundararajan et al., 2017) leverage gradients w.r.t. the given instance to explain model predictions. In this work, we primarily focus on state-of-the-art local post hoc explainers, i.e., methods explaining individual feature importance for model predictions of individual instances.

Large Language Models. LLMs have seen exponential growth in recent years, both in terms of their size and the complexity of tasks they can perform (Radford et al., 2017). Recent advances in LLMs like GPT-4 (OpenAI), Bard (Google), Claude-2 (Anthropic) and Llama-2 (Meta) are changing the paradigm of NLP research and have led to their widespread use across applications spanning machine translation (Vaswani et al., 2017), question-answering (Brown et al., 2020), text generation (Radford et al., 2017), and medical data records (Lee et al., 2020; Alsentzer et al., 2019). In this work, we, for the first time, explore the use of LLMs in explaining other predictive models.

In-context Learning. While the high performance and generalization capabilities have led to highly effective language models for numerous tasks (Wei et al., 2022a), they have also increased the models’ parameter sizes and the computational costs for additional fine-tuning on new downstream tasks. To alleviate this, recent works have introduced in-context learning (ICL), which allows an LLM to perform well on new tasks by simply using a few task samples in the prompt (Liu et al., 2023b). Despite their effectiveness in enhancing the performance of LLMs, these methods have not been thoroughly explored for their potential to generate post-hoc explanations. In this work, we investigate the utility of LLMs in generating post hoc explanations by leveraging their in-context learning abilities.

## 3 OUR FRAMEWORK

Next, we describe our framework that aims to generate explanations using LLMs. To achieve this goal, we outline four distinct prompting strategies — Perturbation-based ICL (Sec. 3.1), Predictionbased ICL (Sec. 3.2), Instruction-based ICL (Sec. 3.3), and Explanation-based ICL (Sec. 3.4).

Notation. Let $f : \mathbb { R } ^ { d }  [ 0 , 1 ]$ denote a black-box ML model that takes an input $\textbf { x } \in \mathbb { R } ^ { d }$ and returns the probability of x belonging to a class ?? ∈ C and the predicted label $y .$ Following previous XAI works (Ribeiro et al., 2016; Smilkov et al., 2017), we randomly sample points from the local neighborhood $\mathcal { N } _ { \mathrm { c } }$ of the given input x to generate explanations, where $\mathcal { N } _ { \mathrm { c } } = \bar { N } ( \mathbf { x } , \sigma ^ { 2 } )$ denotes the neighborhood of perturbations around x using a Normal distribution with mean 0 and variance $\sigma ^ { 2 }$

## 3.1 PERTURBATION-BASED ICL

In the Perturbation-based ICL prompting strategy, we use an LLM to explain $f ,$ trained on tabular data, by querying the LLM to identify the top-?? most important features in determining the output of $f$ in a rank-ordered manner. To tackle this, we sample input-output pairs from the neighborhood $\mathcal { N } _ { \mathrm { c } }$ of x and generate their respective strings following a serialization template; for instance, a perturbed sample’s feature vector $\dot { \mathbf { x } ^ { \prime } } = [ 0 . 0 5 8 , \dot { 0 . 6 } 3 2 , - 0 . 0 \dot { 1 } \dot { 5 } , 1 . 0 1 2 , - 0 . 0 2 2 , - \dot { 0 } . 1 0 8 ]$ , belonging to class 0 in the COMPAS dataset, is converted into a natural-language string as:

# Serialization template   
Input: A = 0.058, B = 0.632, C = -0.015, D = 1.012, E = -0.022, F = -0.108   
Output: 0

While previous post hoc explainers suggest using a large number of neighborhood samples (Ribeiro et al., 2016; Smilkov et al., 2017), it is impractical to provide all samples from $\mathcal { N } _ { \mathrm { c } }$ in the prompt for an LLM due to their constraint on the maximum context length and performance loss when given more information (Liu et al., 2023a). Consequently, we select $n _ { \mathrm { I C L } }$ samples from $\mathcal { N } _ { \mathrm { c } }$ to use in the LLM’s prompt. In the interest of maintaining a neutral and fundamental approach, we employ two primary sampling strategies, both selecting balanced class representation within the neighborhoods defined by $\mathcal { N } _ { \mathrm { c } }$ . The first strategy selects samples randomly, while the second chooses those with the highest confidence levels, aiding the LLM in generating explanations centered on model certainty.

Given ??ICL input-output pairs from $\mathcal { N } _ { \mathrm { c } }$ and the test sample x to be explained, we add context with respect to the predictive model, dataset, and task description in our prompt to aid the LLM in behaving like a post hoc explanation method. Motivated by the local neighborhood approximation works in XAI, the Perturbation-based ICL prompting strategy presumes that the local behavior of $f$ is a simple linear decision boundary, contrasting with the often globally exhibited complex nonlinear decision boundary. Hence, assuming a sufficient number of perturbations in $\mathcal { N } _ { \mathrm { c } }$ , the LLM is expected to accurately approximate the black box model’s behavior and utilize this information to identify the top-?? most important features. The final prompt structure is given below, where the “Context” provides the LLM with the background of the underlying ML model, the number of features in the dataset, and model predictions, “Dataset” denotes the $n _ { \mathrm { I C L } }$ instances sampled from the neighborhood $\mathcal { N } _ { \mathrm { c } }$ of $\mathbf { x } , \ ^ { \ast } Q u e s t i o n ^ { \prime \prime }$ is the task we want our LLM to perform, and “Instructions” are the guidelines we want the LLM to follow while generating the output explanations.

# Perturbation-based ICL Prompt Template   
Context: “We have a two-class machine learning model that predicts based on 6 features: [‘A’, ‘B’, ‘C’,   
‘D’, ‘E’, ‘F’]. The model has been trained on a dataset and has made the following predictions.”   
Dataset:   
Input: A = -0.158, B = 0.293, C = 0.248, D = 1.130, E = 0.013, F = -0.038   
Output: 0   
. . .   
Input: A = 0.427, B = 0.016, C = -0.128, D = 0.949, E = 0.035, F = -0.045   
Output: 1   
Question: “Based on the model’s predictions and the given dataset, what appears to be the top five most   
important features in determining the model’s prediction?”   
Instructions: “Think about the question. After explaining your reasoning, provide your answer as the top   
five most important features ranked from most important to least important, in descending order. Only   
provide the feature names on the last line. Do not provide any further details on the last line.”

## 3.2 PREDICTION-BASED ICL

Here, we devise Prediction-based ICL, a strategy closer to the traditional ICL prompting style, where the primary objective remains the same — understanding the workings of the black-box model ?? by identifying the top-?? most important features. This strategy positions the LLM to first emulate the role of the black-box model by making predictions, staging it to extract important features that influenced its decision. We follow the perturbation strategy of Sec. 3.1 and construct the Prediction-based ICL prompt using ??ICL input-output pairs from N??. The main difference in the Prediction-based ICL prompting strategy lies in the structuring of the prompt, which is described below:

# Prediction-based ICL Prompt Template   
Context: “We have a two-class machine learning model that predicts based on 6 features: [‘A’, ‘B’, ‘C’,   
‘D’, ‘E’, ‘F’]. The model has been trained on a dataset and has made the following predictions.”   
Dataset:   
Input: A = 0.192, B = 0.240, C = 0.118, D = 1.007, E = 0.091, F = 0.025   
Output: 0   
. . .   
Input: A = 0.709, B = -0.102, C = -0.177, D = 1.056, E = -0.056, F = 0.015   
Output: 1   
Input: A = 0.565, B = -0.184, C = -0.386, D = 1.003, E = -0.123, F = -0.068   
Output:   
Question: “Based on the model’s predictions and the given dataset, estimate the output for the final input.   
What appears to be the top five most important features in determining the model’s prediction?”   
Instructions: “Think about the question. After explaining your reasoning, provide your answer as the top   
five most important features ranked from most important to least important, in descending order. Only   
provide the feature names on the last line. Do not provide any further details on the last line.”

Here, we construct the prompt using the task description followed by the ??ICL ICL samples and then ask the LLM to provide the predicted label for the test sample x and explain how it generated that label. The primary motivation behind the Prediction-based ICL prompting strategy is to investigate whether the LLM can learn the classification task using the ICL set and, if successful, identify the important features in the process. This approach aligns more closely with the traditional ICL prompting style, offering a different perspective on the problem.

## 3.3 INSTRUCTION-BASED ICL

The Instruction-based prompting transitions from specifying task objectives to providing detailed guidance on the strategy for task execution. Rather than solely instructing the LLM on what the task entails, this strategy delineates how to conduct the given task. The objective remains to understand the workings of the black-box model and identify the top-?? most important features. However, in using step-by-step directives, we aim to induce a more structured and consistent analytical process within the LLM to target more faithful explanations. The final prompt structure is as follows:

![](images/e952acad00e90eccbe650323947b0aeb3e07630cdb0d1185cfc7205d854cbd15.jpg)  
Here, we provide some general instructions to the LLM for understanding the notion of important features and how to interpret them through the lens of correlation analysis. To achieve this, we instruct LLMs to analyze each feature sequentially and ensure that both positive and negative correlations are equally emphasized. The LLM assigns an importance score for each feature in the given dataset and then positions it in a running rank. This rank is necessary to differentiate features and avoid ties in the LLM’s evaluations. The final line ensures that the LLM’s responses are strictly analytical, minimizing non-responsiveness or digressions into tool or methodology recommendations.

## 3.4 EXPLANATION-BASED ICL

Recent studies show that LLMs can learn new tasks through ICL, enabling them to excel in new downstream tasks by merely observing a few instances of the task in the prompt. In the Explanation-based ICL prompting strategy, we leverage the ICL capability of LLMs to alleviate the computation complexity of some post hoc explanation methods. In particular, we investigate whether an LLM can mimic the behavior of a post hoc explainer by looking at a few input, output, and explanation examples. We generate explanations for a given test sample x using LLMs by utilizing the ICL framework and supplying ??ICL input, output, and explanation examples to the LLM, where the explanations in the ICL can be generated using any post hoc explanation method. For constructing the ICL set, we randomly select ??ICL input instances XICL from the ICL split of the dataset and generate their predicted labels yICL using model ?? . Next, we generate explanations EICL for samples (XICL, yICL) using any post hoc explainer. Using the above input, output, and explanation samples, we construct a prompt by concatenating each pair as follows:

# Explanation-based ICL Prompt Template   
Input: A = 0.172, B = 0.000, C = 0.000, D = 1.000, E = 0.000, F = 0.000   
Output: 1   
Explanation: A,C,B,F,D,E   
. . .   
Input: A = 0.052, B = 0.053, C = 0.073, D = 0.000, E = 0.000, F = 1.000   
Output: 0   
Explanation: A,B,C,E,F,D   
Input: A = 0.180, B = 0.222, C = 0.002, D = 0.000, E = 0.000, F = 1.000   
Output: 0   
Explanation:  
Using the Explanation-based ICL prompting strategy, we aim to investigate the learning capability of LLMs such that they can generate faithful explanations by examining the ??ICL demonstration pairs of inputs, outputs, and explanations generated by state-of-the-art post hoc explainer.

## 4 EXPERIMENTS

Next, we evaluate the effectiveness of LLMs as post hoc explainers. More specifically, our experimental analysis focuses on the following questions: Q1) Can LLMs generate faithful post hoc explanations? Q2) Do LLM-Augmented post hoc explainers achieve similar faithfulness vs. their vanilla counterpart? Q3) Are LLMs better than state-of-the-art post hoc explainers at identifying the most important feature? Q4) Is GPT-4 a better explainer than GPT-3.5? Q5) Are changes to the LLM’s prompting strategy necessary for generating faithful explanations?

## 4.1 DATASETS AND EXPERIMENTAL SETUP

We first describe the datasets and models used to study the reliability of LLMs as post hoc explainers and then outline the experimental setup.

Datasets. Following previous LLM works (Hegselmann et al., 2023), we performed analysis on four real-world tabular datasets: Blood (Yeh et al., 2009) having four features, Recidivism (ProPublica) having six features, Adult (Kaggle) having 13 features, and Default Credit (UCI) having 10 features. The datasets come with a random train-test split, and we further subdivide the train set, allocating 80% for training and the remaining 20% for ICL sample selection, as detailed in Sec. 3.4. We use a random set of 100 samples from the test split to generate explanations for all of our experiments.

Predictive Models. We consider two ML models with varying complexity in our experiments: i) Logistic Regression (LR) and ii) Artificial Neural Networks (ANN). We use PyTorch (Paszke et al., 2019) to implement the ANNs with the following combination of hidden layers: one layer of size 16 for the LR model; and three layers of size 64, 32, and 16 for the ANN, using RELU for the hidden layers and SOFTMAX for the output (see Table 1 for predictive performances of these models).

Large Language Model. We consider GPT-3.5 and GPT-4 as language models for all experiments.

Baseline Explanation Methods. We use six post hoc explainers as baselines to investigate the effectiveness of explanations generated using LLMs: LIME (Ribeiro et al., 2016), SHAP (Lundberg & Lee, 2017), Vanilla Gradients (Zeiler & Fergus, 2014), SmoothGrad (Smilkov et al., 2017), Integrated Gradients (Sundararajan et al., 2017), and Gradient x Input (ITG) (Shrikumar et al., 2017).

Performance Metrics. We employ four distinct metrics to measure the faithfulness of an explanation. To quantify the faithfulness of an explanation where there exists a ground-truth top-?? explanation for each test input (i.e., LR model coefficients), we use the Feature Agreement (FA) and Rank Agreement (RA) metrics introduced in Krishna et al. (2022), which compares the LLM’s top-?? directly with the model’s ground-truth. The FA and RA metrics range from [0, 1], where 0 means no agreement and 1 means full agreement. However, in the absence of a top-?? ground-truth explanation (as is the case with ANNs), we use the Prediction Gap on Important feature perturbation (PGI) and the Prediction Gap on Unimportant feature perturbation (PGU) metrics from OpenXAI (Agarwal et al., 2022). While PGI measures the change in prediction probability that results from perturbing the features deemed as influential, PGU examines the impact of perturbing unimportant features. Here, the perturbations are generated using Gaussian noise $N ( 0 , \sigma ^ { 2 } )$ .

Implementation Details. To generate perturbations for each ICL prompt, we use a neighborhood size of $\sigma = 0 . 1$ and generate local perturbation neighborhoods $\mathcal { N } _ { \mathrm { c } }$ for each test sample x. We sample $n _ { x } = 1 0 , 0 0 0$ points sampled for each neighborhood, where the values for $\sigma$ and $n _ { x }$ were chosen to give an equal number of samples for each class, whenever possible. We present perturbations in two main formats: as the raw perturbed inputs alongside their corresponding outputs (shown in the Sec. 3.1 and 3.2 templates); or as the change between each perturbed input and the test sample, and the corresponding change in output (shown in Sec. 3.3). The second approach significantly aids the LLM in discerning the most important features (see Fig. 11), providing only the changes relative to the test sample, and bypassing the LLM’s need to internally compute these differences. As a result, the consistent value of the original test point becomes irrelevant, and this clearer, relational view allows the LLM to focus directly on variations in input and output. Note that both of these formats are absent from Sec. 3.4, which uses test samples directly and does not compute perturbations.

For the LLMs, we use OpenAI’s text generation API with a temperature of $\tau = 0$ for our main experiments. To evaluate the LLM explanations, we extract and process its answers to identify the top-?? most important features. We first save each LLM query’s reply to a text file and use a script to extract the features. We added explicit instructions like “. . . provide your answer as a feature name on the last line. Do not provide any further details on the last line.” to ensure reliable parsing of LLM outputs. In rare cases, the LLM won’t follow our requested response format or it replies with “I don’t have enough information to determine the most important features.” See Appendix 6.1 for further details.

## 4.2 RESULTS

Next, we discuss experimental results that answer key questions highlighted at the beginning of this section about LLMs as post hoc explainers (Q1-Q5).

1) LLMs can generate faithful explanations. We compare our proposed prompting-based LLM explanation strategies to existing post hoc explainers on the task of identifying important features for understanding ANN (Fig. 2) and LR (Fig. 3) model predictions across four real-world datasets (see Table 2). For the ANN model, the LLM-based explanations perform on par with the gradient-based methods (despite having white-box access to the underlying black-box model) and LIME (that approximates model behavior using a surrogate linear model). In particular, our proposed prompting strategies perform better than ITG, SHAP, a Random baseline, and a 16-sample version of LIME, namely $\mathrm { L I M E } _ { 1 6 } ,$ which is analogous to the number of ICL samples used in the LLM prompts. We observe that LLM explanations, on average, achieve 51.74% lower PGU and 163.40% higher PGI than ITG, SHAP, and Random baseline for larger datasets (more number of features) like Adult and Credit compared to 25.56% lower PGU and 22.86% higher PGI for Blood and Recidivism datasets. While our prompting strategies achieve competitive PGU and PGI scores among themselves across different datasets for ANN models, the Instruction-based ICL strategy, on average across datasets, achieves higher FA and RA scores for the LR model (Fig. 3). We find that gradient-based methods and LIME achieve almost perfect scores on FA and RA metrics as they are able to get accurate model gradients and approximate the model behavior with high precision. Interestingly, the LLM-based explanations perform better than ITG, SHAP, and Random baseline methods, even for a linear model.

![](images/d0851d6e54123d1b6c930ffbff48f5845842d21dac9669a0bf760f869fa5f7c5.jpg)  
P3: Instruction-based ICL

P2: Prediction-based ICL  
![](images/4afee756bb1537db5f0d1ed5fd271ac1348908609d5e166312ef57a729c9d21d.jpg)  
P1: Perturbation-based ICL

Figure 2: PGU and PGI scores of explanations generated using post hoc methods and LLMs (Instruction-based, Prediction-based, and Perturbation-based ICL prompting strategies) for an ANN model. On average, across four datasets, we find that LLM-based explanations perform on par with gradient-based and LIME methods and outperform $\mathrm { L I M E } _ { 1 6 } ,$ ITG, and SHAP methods.  
![](images/c749815bcc4a0c64d803cf831a6f42e5d4e774592b123c9da47131559442fec6.jpg)  
P3: Instruction-based ICL

![](images/b81aae639e43d038862fbc40ad94e67db58c02efbecbfbebfe815f1115c83a4f.jpg)  
P2: Prediction-based ICL  
P1: Perturbation-based ICL  
Figure 3: FA and RA scores of explanations generated using post hoc methods and LLMs (Instruction-based, Prediction-based, and Perturbation-based ICL prompting strategies) for an LR model. On average, across four datasets, we find that gradient-based methods and the LIME method (with 1000 samples) outperform all other methods and Instruction-based ICL explanations outperform other two prompting strategies across all datasets.

2) LLM-augmented explainers achieve similar faithfulness to their vanilla counterparts. We evaluate the faithfulness of the explanations generated using the Explanation-based ICL prompting strategy. Our results show that LLMs generate explanations that achieve faithfulness performance on par with those generated using state-of-the-art post hoc explanation methods for LR and large ANN predictive models across all four datasets (Fig. 4; see Table 3 for complete results) and four evaluation metrics. We demonstrate that very few in-context examples (here, $n _ { \mathrm { I C L } } = 4 )$ are sufficient to make the LLM mimic the behavior of any post hoc explainer and generate faithful explanations, suggesting the effectiveness of LLMs as an explanation method. Interestingly, for low-performing explanation methods like ITG and SHAP, we find that explanations generated using their LLM counterparts achieve higher feature and rank agreement (Fig. 4) scores in the case of LR models, hinting that LLMs can use their internal knowledge to improve the faithfulness of explanations.

![](images/ee4012898a538f5bae12bf3f563a54f579b531f70f316afe795f78f3479f264d.jpg)

![](images/8755139c5794c78a556e4d2f7761f8963b87f0a7beab6143008758419de41198.jpg)

![](images/ab2c7ed4a3098ede3ad39a313bd1336cf65824c62148c7b8442a9aa6ef983db8.jpg)

![](images/ec4aad1736935da0ca784dbd7e55ca7afa209958f02de62f2ebd5bef64834a32.jpg)  
Figure 4: Faithfulness metrics on the Recidivism dataset for six post hoc explainers and their LLM-augmented counterparts for a given LR (left) and ANN (right) model. LLM-augmented explanations achieve on-par performance w.r.t. post hoc methods across all four metrics (see Table 3 for complete results on all other datasets).

3) LLMs accurately identify the most important feature. To demonstrate the LLM’s capability in identifying the most important feature, we show the faithfulness performance of generated explanations across four datasets. Our results in Fig. 5 demonstrate the impact of different top-?? feature values on the faithfulness of explanations generated using our prompting strategies. We observe a steady decrease in RA scores (0.722 for top-??=1 vs. 0.446 for top-??=2 vs. 0.376 for top-??=4) across three datasets (Blood, Credit, and Adult) as the top-?? value increases. Interestingly, the RA value for top-??=1 for the Recidivism dataset is almost zero, though this can be attributed to the LLM’s handling of the two primary features, whose LR coefficients have nearly identical magnitudes; the LLM generally places them both within the top two but, due to their similar importance, defaults to alphabetical order. However, when employing our Instruction-based ICL running-rank strategy, we find that the RA value rises from 0 to 0.5, highlighting the influence of nuanced prompts on the LLM’s ranking mechanism. Further, we observe that LLMs, on average across four datasets and three prompting strategies, faithfully identify top-??=1 features with 72.19% FA score (see Fig. 12), and their faithfulness performance takes a hit for higher top-?? values. In the context of our 72.19% result, baseline methods’ performances in identifying top-??=1 features are as follows: Random baseline (15%), SHAP (29.75%), ITG (29.5%), and LIME/IG/SG/Grad (100%) (see Tables 4-5).

![](images/ef3da5baacd425b66540582cb393446f410941f9511e733cacdb719b0beb8b81.jpg)

![](images/3deabe05371a26a99a2e4504e1eeacff0ed727afbccb70ae47158082ef7c93e3.jpg)

![](images/5733b66b5bda4b54e8290ae0e53ab4992b2a080612678979e0b8f31cbdd6abda.jpg)  
Figure 5: Effects of top-?? value on the RA metric using Perturbation-based, Prediction-based, and Instructionbased ICL prompting strategies. Shown are the results for three prompting strategies and four datasets using the LR model. On average, LLMs successfully achieve high scores in identifying the most important feature (top-??=1) and the performance decreases as we increase the top-?? value (see Fig. 12 for results on FA).

4) GPT-3.5 vs. GPT-4. An interesting question is how the reasoning capability of an LLM affects the faithfulness of the generated explanations. Hence, we compare the output explanations from GPT-3.5 and GPT-4 models to understand black-box model predictions. Results in Fig. 6-8 show that explanations generated using GPT-4, on average across four datasets, achieve higher faithfulness scores than explanations generated using the GPT-3.5 model. Across four prompting strategies, GPT-4, on average, obtains 4.53% higher FA and 48.01% higher RA scores than GPT-3.5 on explanations generated for the Adult dataset. We attribute this increase in performance of GPT-4 to its superior reasoning capabilities compared to the GPT-3.5 model (OpenAI, 2023). In Figure 6, we find that Instruction-based ICL, on average across four datasets, outperforms the Perturbation-based ICL and Prediction-based ICL strategies on the RA metric. Further, our results in Fig. 8 show that the faithfulness performance of GPT-4 and GPT-3.5 are on par with each other when evaluated using our Explanation-based ICL strategy, which highlights that both models are capable of emulating the behavior of a post hoc explainer by looking at a few input, output, and explanation examples.

![](images/747ab10ec0a972034f1339b8c1f8e6ce7c999043497730a73b746940a1200f5a.jpg)

![](images/afb1181367a040bbe49eb489a3c125a2a56b27ea12a2955541f55601df41dd97.jpg)

![](images/83d400bd0c023bae413d728268d61a3ad16b6ad6877510b890d2a61502afa013.jpg)  
Figure 6: RA faithfulness metric of explanations generated using Perturbation-based ICL, Prediction-based ICL, and Instruction-based ICL prompting strategies on four real-world datasets. Explanations from GPT-4, on average, achieve higher RA scores than their GPT-3.5 counterparts (see Figures 8-9 for similar plots on Feature Agreement metric and Explanation-based ICL strategy).

5) Ablation Study. We conduct ablations on several components of the prompting strategies, namely the number of ICL samples, perturbation format, and temperature values. Results show that our choice of hyperparameter values is important for the prompting techniques to generate faithful post hoc explanations (Figs. 7,10). Our ablation on the number of ICL samples (Fig. 7) shows that fewer and larger numbers of ICL samples are not beneficial for LLMs to generate post hoc explanations. While fewer ICL samples provide insufficient information to the LLM to approximate the predictive behavior of the underlying ML model, a large number of ICL samples increases the input context, where the LLM struggles to retrieve relevant information from longer prompts, resulting in a decrease in the faithfulness of the explanations generated by LLMs. In contrast to LIME, the faithfulness of LLM explanations deteriorates upon increasing the number of ICL samples (analogous to the neighborhood of a given test sample). Across all four prompting strategies, we observe a drop in FA, RA, and PGI scores as we increase the number of ICL samples to 64. Further, our ablation on the temperature parameter of the LLMs shows that the faithfulness performance of the explanations does not change much across different values of temperature (see Appendix Fig. 10). Finally, results in Fig. 11 show that our prompting strategies achieve higher faithfulness when using the difference between the perturbed and test sample as input in the ICL sample.

![](images/00c42316c41002e38a8273ded2d34f9bfc356371eac15d4fa450624fab561ae7.jpg)

![](images/d5dd7a3cf51805c6575b69dc4689f412a1a592f3375d12f03aeaf9345ca3fe56.jpg)

![](images/dc4bb5cd90c0597b2d895007be0ccdaad848c0bb048ab4f81088613d8cd4d9ca.jpg)  
LIME — Perturbation-based ICL —Prediction-based ICL —Instruction-based ICL —Explanation-based ICL  
Figure 7: FA, RA, and PGI Performance of LIME and all four proposed prompting strategies as we increase the number of ICL samples (analogous to neighborhood samples in LIME) for the LR model trained on the Adult dataset. In contrast to LIME, the faithfulness of LLM explanations across different metrics decreases for a higher number of ICL samples, likely due to the limited capabilities of LLM for longer prompt length.

## 5 CONCLUSION

We introduce and explore the potential of using state-of-the-art LLMs as post hoc explainers. To this end, we propose four prompting strategies — Perturbation-based ICL, Prediction-based ICL, Instruction-based ICL, and Explanation-based ICL— with varying levels of information about the local neighborhood of a test sample to generate explanations using LLMs for black-box model predictions. We conducted several experiments to evaluate LLM-generated explanations using four benchmark datasets. Our results across different prompting strategies highlight that LLMs can generate faithful explanations and consistently outperform methods like ITG and SHAP. Our work paves the way for several exciting future directions in explainable artificial intelligence (XAI) to explore LLM-based explanation frameworks.

## REFERENCES

Chirag Agarwal, Satyapriya Krishna, Eshika Saxena, Martin Pawelczyk, Nari Johnson, Isha Puri, Marinka Zitnik, and Himabindu Lakkaraju. Openxai: Towards a transparent evaluation of model explanations. NeurIPS, 2022.

Emily Alsentzer, John R Murphy, Willie Boag, Wei-Hung Weng, Di Jin, Tristan Naumann, and Matthew McDermott. Publicly available clinical bert embeddings. arXiv, 2019.

Anthropic. Anthropic \ claude 2. https://www.anthropic.com/index/claude-2. (Accessed on 07/17/2023).

Naman Bansal, Chirag Agarwal, and Anh Nguyen. Sam: The sensitivity of attribution methods to hyperparameters. In CVPR, 2020.

Steven Bills, Nick Cammarata, Dan Mossing, Henk Tillman, Leo Gao, Gabriel Goh, Ilya Sutskever, Jan Leike, Jeff Wu, and William Saunders. Language models can explain neurons in language models. https://openaipublic.blob.core.windows.net/ neuron-explainer/paper/index.html, 2023.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. NeurIPS, 2020.

Sebastien Bubeck, Varun Chandrasekaran, Ronen Eldan, Johannes Gehrke, Eric Horvitz, Ece Ka-´ mar, Peter Lee, Yin Tat Lee, Yuanzhi Li, Scott Lundberg, et al. Sparks of artificial general intelligence: Early experiments with gpt-4. arXiv, 2023.

Finale Doshi-Velez and Been Kim. Towards a rigorous science of interpretable machine learning. arXiv, 2017.

Google. Try bard, an ai experiment by google. https://bard.google.com/. (Accessed on 07/17/2023).

Stefan Hegselmann, Alejandro Buendia, Hunter Lang, Monica Agrawal, Xiaoyi Jiang, and David Sontag. Tabllm: Few-shot classification of tabular data with large language models. In AISTATS. PMLR, 2023.

Amr Hendy, Mohamed Abdelrehim, Amr Sharaf, Vikas Raunak, Mohamed Gabr, Hitokazu Matsushita, Young Jin Kim, Mohamed Afify, and Hany Hassan Awadalla. How good are gpt models at machine translation? a comprehensive evaluation. arXiv, 2023.

Kaggle. Adult income dataset. https://www.kaggle.com/wenruliu/ adult-income-dataset. Accessed: 2020-01-01.

Satyapriya Krishna, Tessa Han, Alex Gu, Javin Pombra, Shahin Jabbari, Steven Wu, and Himabindu Lakkaraju. The disagreement problem in explainable machine learning: A practitioner’s perspective. arXiv, 2022.

Satyapriya Krishna, Jiaqi Ma, Dylan Slack, Asma Ghandeharioun, Sameer Singh, and Himabindu Lakkaraju. Post hoc explanations of language models can improve language models. arXiv, 2023.

Jinhyuk Lee, Wonjin Yoon, Sungdong Kim, Donghyeon Kim, Sunkyu Kim, Chan Ho So, and Jaewoo Kang. Biobert: a pre-trained biomedical language representation model for biomedical text mining. Bioinformatics, 2020.

Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. Lost in the middle: How language models use long contexts. arXiv, 2023a.

Pengfei Liu, Weizhe Yuan, Jinlan Fu, Zhengbao Jiang, Hiroaki Hayashi, and Graham Neubig. Pretrain, prompt, and predict: A systematic survey of prompting methods in natural language processing. ACM Computing Surveys, 2023b.

Scott M Lundberg and Su-In Lee. A unified approach to interpreting model predictions. In NeurIPS, 2017.

Meta. Llama 2 - meta ai. https://ai.meta.com/llama/. (Accessed on 09/15/2023).

OpenAI. Introducing chatgpt. https://openai.com/blog/chatgpt. (Accessed on 07/17/2023).

OpenAI. Gpt-4 technical report, 2023.

Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury, Gregory Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca Antiga, Alban Desmaison, Andreas Kopf, Ed-¨ ward Yang, Zach DeVito, Martin Raison, Alykhan Tejani, Sasank Chilamkurthy, Benoit Steiner, Lu Fang, Junjie Bai, and Soumith Chintala. Pytorch: An imperative style, high-performance deep learning library. In NeurIPS, 2019.

ProPublica. How we analyzed the compas recidivism algorithm. https://www.propublica. org/article/how-we-analyzed-the-compas-recidivism-algorithm. Accessed: 2021-01-20.

Alec Radford, Rafal Jozefowicz, and Ilya Sutskever. Learning to generate reviews and discovering sentiment, 2017.

Marco Ribeiro, Sameer Singh, and Carlos Guestrin. Anchors: High-precision model-agnostic explanations. In AAAI, 2018.

Marco Tulio Ribeiro, Sameer Singh, and Carlos Guestrin. “Why should I trust you?” Explaining the predictions of any classifier. In KDD, 2016.

Avanti Shrikumar, Peyton Greenside, and Anshul Kundaje. Learning important features through propagating activation differences. In ICML, 2017.

Xuelin Situ, Ingrid Zukerman, Cecile Paris, Sameen Maruf, and Gholamreza Haffari. Learning to explain: Generating stable explanations fast. In IJNLP, 2021.

Daniel Smilkov, Nikhil Thorat, Been Kim, Fernanda Viegas, and Martin Wattenberg. Smoothgrad:´ Removing noise by adding noise. arXiv, 2017.

Mukund Sundararajan, Ankur Taly, and Qiqi Yan. Axiomatic attribution for deep networks. In ICML, 2017.

UCI. Default of credit card clients data set. https://archive.ics.uci.edu/ml/ datasets/default+of+credit+card+clients. Accessed: 2020-01-01.

Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. Attention is all you need. NeurIPS, 2017.

Jason Wei, Yi Tay, Rishi Bommasani, Colin Raffel, Barret Zoph, Sebastian Borgeaud, Dani Yogatama, Maarten Bosma, Denny Zhou, Donald Metzler, et al. Emergent abilities of large language models. arXiv, 2022a.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Ed Chi, Quoc Le, and Denny Zhou. Chain of thought prompting elicits reasoning in large language models. arXiv, 2022b.

Chih-Kuan Yeh, Cheng-Yu Hsieh, Arun Suggala, David I Inouye, and Pradeep K Ravikumar. On the (in) fidelity and sensitivity of explanations. NeurIPS, 2019.

I-Cheng Yeh, King-Jang Yang, and Tao-Ming Ting. Knowledge discovery on rfm model using bernoulli sequence. Expert Systems with applications, 2009.

Matthew D Zeiler and Rob Fergus. Visualizing and understanding convolutional networks. In ECCV, 2014.

## 6 APPENDIX: ADDITIONAL RESULTS AND EXPERIMENTAL DETAILS

## 6.1 ADDITIONAL EXPERIMENTAL DETAILS

The median number of occurrences for cases where the LLM didn’t follow our requested response format or it replies with “I don’t have enough information to determine the most important features” is 3 for Perturbation-based ICL, 0.5 for Prediction-based ICL, and 0 for Explanation-based ICL. We use the LLM’s top-?? features to calculate explanation faithfulness using four evaluation metrics. For calculating PGU and PGI metrics, we use perturbation mean $\scriptstyle \mu _ { P G } = 0$ , standard deviation $\sigma _ { P G } { = } 0 . 1$ and the number of perturbed samples $m _ { P G } = 1 0 , 0 0 0$ . We follow the default hyperparameters from OpenXAI for generating explanations from standard post hoc explainers.

Metrics. We follow Agarwal et al. (2022) and used their evaluation metrics in our work. Below, we provide their respective definitions.

a) Feature Agreement (FA) metric computes the fraction of top-?? features that are common between a given post hoc explanation and the corresponding ground truth explanation.

b) Rank Agreement (RA) metric measures the fraction of top-?? features that are not only common between a given post hoc explanation and the corresponding ground truth explanation, but also have the same position in the respective rank orders.

c) Prediction Gap on Important feature perturbation (PGI) metric measures the difference in prediction probability that results from perturbing the features deemed as influential by a given post hoc explanation.

d) Prediction Gap on Unimportant feature perturbation (PGU) which measures the difference in prediction probability that results from perturbing the features deemed as unimportant by a given post hoc explanation.

For a given instance x, we first obtain the prediction probability ??ˆ output by the underlying model $f , i . e . , \hat { y } = f ( \mathbf { x } )$ Let $e _ { \mathbf { x } }$ be an explanation for the model prediction of x. In the case of PGU, we then generate a perturbed instance $\mathbf { x } ^ { \prime }$ in the local neighborhood of x by holding the top-?? features constant, and slightly perturbing the values of all the other features by adding a small amount of Gaussian noise. In the case of PGI, we generate a perturbed instance $\mathbf { x } ^ { \prime }$ in the local neighborhood of x by slightly perturbing the values of the top-?? features by adding a small amount of Gaussian noise and holding all the other features constant. Finally, we compute the expected value of the prediction difference between the original and perturbed instances as:

$$
\mathrm { P G I } ( \mathbf { x } , f , e _ { \mathbf { x } } , k ) = \mathbb { E } _ { \mathbf { x } ^ { \prime } \sim \mathrm { p e r t u r b } ( \mathbf { x } , e _ { \mathbf { x } } , \mathrm { t o p } \cdot K ) } [ | \hat { y } - f ( \mathbf { x } ^ { \prime } ) | ] ,\tag{1}
$$

$$
\mathrm { P G U } ( \mathbf { x } , f , e _ { \mathbf { x } } , k ) = \mathbb { E } _ { \mathbf { x } ^ { \prime } \sim \mathrm { p e r t u r b } ( \mathbf { x } , e _ { \mathbf { x } } , \mathrm { n o n t o p } \cdot K ) } [ | \hat { y } - f ( \mathbf { x } ^ { \prime } ) | ] ,\tag{2}
$$

where perturb(·) returns the noisy versions of x as described above.

Hyperparameters for XAI methods. Below, we provide the values for all hyperparameters of the explanation methods used in our experiments.

a) LIME. kernel width = 0.75; std LIME = 0.1; mode = ’tabular’; sample around instance = True; n samples LIME = 1000 or 16; discretize continuous = False

b) Grad. absolute value = True

c) Smooth grad. n samples SG = 100; std SG = 0.005

d) Integrated gradients. method = ’gausslegendre’; multiply by inputs = False; n steps = 50

e) SHAP. n samples = 500

## 6.2 ADDITIONAL RESULTS

Here, we include additional and detailed results of the experiments discussed in Sec. 4.

![](images/acabdc332718a8c3e330354ef861b92997e45f32cc12231f79f07156c616201b.jpg)

![](images/8655e7c9d7afda6a026985028a07b19822cbb3d150b2803cd82dbec71978696b.jpg)  
Figure 8: FA and RA metric performances for six LLM-augmented post hoc explainers (Sec. 3.4) when generating explanations for a given LR model using GPT-3.5 vs. GPT-4. Explanations from GPT-4, on average, outperform those generated using GPT-3.5 on both metrics on the Adult dataset.  
PERTURBATION-BASED ICL

![](images/752f7bd56ef44e0664d53836b2ccd5ba93c88862c6391a7e133f1ad2e493ee39.jpg)

PREDICTION-BASED ICL  
![](images/8c1e8e7ca1ae9fbd083a0fd03d8d582ceee96492bbc1766424aa77586580a5cd.jpg)  
INSTRUCTION-BASED ICL

![](images/24a48a52b3a3af5b6d52657e863c07293254a904b1923869ba1025c19ef527f5.jpg)  
Figure 9: FA metric performances of explanations generated using Perturbation-based ICL, Prediction-based ICL, and Instruction-based ICL prompting strategies on four real-world datasets. Explanations from GPT-4, on average, achieve higher FA scores than their GPT-3.5 counterparts.

## LOGISTIC REGRESSION

![](images/70d4a71e0c6414608af39b811f877b5db6ba127c6d5a02ddd32ce6e532a7d2c5.jpg)

![](images/676365afd82fc5557342e26d145e455275c744ac66e12659a48f586cd6342b79.jpg)

![](images/88817f7145c1d92281435aad1d5e451358140449197b2642d5885c2ab922edad.jpg)  
NEURAL NETWORK

![](images/aa663bf156a07684f88d27e773a6cd86ceddf3edfcd51b7817a2eb5b07598a7b.jpg)  
Figure 10: Metric performances for explanations generated using LLMs for different temperatures (??) with a Logistic Regression model (left) and a Neural Network (right) model. LLM-based explanations perform almost consistently across different temperature values, but LLMs will more often reply along the lines of “not enough information to determine the most important features,” for higher temperatures.

PERTURBATION-BASED ICL  
![](images/f5f73f3a1d8054665e9d34a7a6702f83ab87e18328374c7ade54dd7a6fe47d53.jpg)

PREDICTION-BASED ICL  
![](images/70baa08889bb83a31d89408e2e2fa845d1d1bed60bfecf6fe01a102fc1a75765.jpg)  
Figure 11: Faithfulness performance of explanations generated using Perturbation-based ICL (left) and Prediction-based ICL (right) on using perturbed samples vs difference between perturbed samples and the input sample (raw perturbations) in the ICL prompts for LR models trained on the Adult dataset. Across both prompting strategies, we find that using ICL samples using the raw perturbation style results in significantly better faithfulness performance across all four metrics.

Blood Recidivism Credit Adult

Table 1: Results of the machine learning models trained on four datasets. Shown are the accuracy of the LR and ANN models trained the datasets. The best performance is bolded.
<table><tr><td>Dataset</td><td>LR</td><td>ANN</td></tr><tr><td>Blood</td><td>70.59%</td><td>64.71%</td></tr><tr><td>Recidivism</td><td>76.90%</td><td>76.90%</td></tr><tr><td>Default Credit</td><td>87.37%</td><td>88.34%</td></tr><tr><td>Adult</td><td>77.37%</td><td>80.11%</td></tr></table>

PERTURBATION-BASED ICL  
![](images/8d4377743eda76874cf09714d24243530c321bd5b5713ce2c489915864ce63d0.jpg)

![](images/d8b2714d2564350d24b3f735841781a03acaa2cf4d6e548ddc8d6740c19d50ed.jpg)

INSTRUCTION-BASED ICL  
![](images/861ecc8c71be0907bfbc3eda0afe4a295285100a377cfe919054dc7351683f95.jpg)  
Figure 12: Effects of top-?? value on the FA explanation faithfulness metric when using Perturbationbased ICL, Prediction-based ICL, and Instruction-based ICL prompting strategies. Shown are the results for three prompting strategies and four datasets using the LR model. On average, LLMs successfully achieve high scores in identifying the most important feature $( \mathrm { t o p } { - } k = 1 )$ and the performance decreases as we increase the top-?? value. For the Blood and Recidivism datasets, FA increases for $\mathrm { t o p } { - } k \geq 4$ because they have four and six features in their dataset, respectively.

Table 2: Here we provide the average and standard error faithfulness metric values of explanations calculated across 100 instances in the test set. The results are generated using Perturbation-based ICL, Prediction-based ICL, Instruction-based ICL, six post hoc explanation methods, and a random baseline. For the LLM methods, we queried the LLM for the top-?? = 5 (?? = 4 for Blood) most important features and calculated each metric’s area under the curve (AUC) for ?? = 3 (where the AUC is calculated from ?? = 1 to ?? = 3). This will help us better understand the model’s (Logistic Regression and Artificial Neural Network) predictions trained on four datasets. Arrows (↑, ↓) indicate the direction of better performance.
<table><tr><td colspan="2" rowspan="2">Dataset Method</td><td colspan="3">LR</td><td colspan="2">ANN</td></tr><tr><td>FA(↑)</td><td>RA(↑)</td><td>PGU ()</td><td>PGI (↑)</td><td>PGU () PGI (↑)</td></tr><tr><td rowspan="11">Blood</td><td>Grad</td><td></td><td>1.000±0.000 1.000±0.000 0.010±0.0000.042±0.000|0.060±0.009 0.115±0.013</td><td></td><td></td><td></td></tr><tr><td>SG</td><td></td><td>1.000±0.000 1.000±0.000 0.010±0.000 0.042±0.000</td><td></td><td></td><td>0.060±0.009 0.115±0.013</td></tr><tr><td>IG</td><td></td><td>1.000±0.000 1.000±0.000 0.010±0.000 0.042±0.000</td><td></td><td></td><td>0.061±0.0090.116±0.013</td></tr><tr><td>ITG</td><td></td><td>0.722±0.019 0.563±0.037 0.019±0.001 0.037±0.001</td><td></td><td></td><td>0.081±0.010 0.100±0.012</td></tr><tr><td>SHAP</td><td></td><td>0.723±0.0200.556±0.037 0.019±0.001 0.036±0.001</td><td></td><td></td><td>0.085±0.011 0.098±0.012</td></tr><tr><td>LIME</td><td></td><td>1.000±0.000 1.000±0.000 0.010±0.000 0.042±0.000|</td><td></td><td></td><td>|0.061±0.0090.116±0.013</td></tr><tr><td></td><td>Random</td><td>0.502±0.022 0.232±0.032 0.029±0.001 0.026±0.001</td><td></td><td></td><td>0.091±0.011 0.090±0.012</td></tr><tr><td></td><td></td><td>Perturbation-based ICL 0.790±0.011 0.656±0.018 0.015±0.000 0.041±0.001</td><td></td><td></td><td>0.064±0.010 0.110±0.013</td></tr><tr><td rowspan="8"></td><td></td><td></td><td>Prediction-based ICL 0.789±0.009 0.638±0.018 0.014±0.000 0.041±0.000|0.063±0.010 0.110±0.013</td><td></td><td></td></tr><tr><td>Instruction-based ICL 0.802±0.015 0.578±0.037 0.014±0.000 0.040±0.001 0.068±0.010 0.106±0.013</td><td></td><td></td><td></td><td></td></tr><tr><td>Grad</td><td>1.000±0.000 1.000±0.000 0.059±0.003 0.106±0.005|0.095±0.008 0.149±0.011</td><td></td><td></td><td></td></tr><tr><td rowspan="10"></td><td>SG</td><td>1.000±0.000 1.000±0.000 0.059±0.003 0.106±0.0050.095±0.008 0.149±0.011</td><td></td><td></td><td></td></tr><tr><td>IG</td><td></td><td></td><td></td><td></td></tr><tr><td>ITG</td><td></td><td>1.000±0.000 1.000±0.0000.059±0.0030.106±0.005</td><td></td><td>0.096±0.0080.149±0.011</td></tr><tr><td>SHAP</td><td>0.473±0.023 0.217±0.032 0.092±0.005 0.076±0.004</td><td>0.493±0.021 0.214±0.030 0.090±0.005 0.078±0.004 0.129±0.011 0.122±0.010</td><td></td><td></td></tr><tr><td>LIME</td><td></td><td></td><td></td><td>40.130±0.011 0.122±0.010 1.000±0.000 1.000±0.000 0.059±0.003 0.106±0.005 0.096±0.008 0.149±0.011</td></tr><tr><td>Random</td><td></td><td>0.308±0.023 0.127±0.024 0.101±0.005 0.063±0.005</td><td></td><td>0.146±0.011 0.092±0.009</td></tr><tr><td></td><td></td><td>Perturbation-based ICL 0.744±0.004 0.084±0.003 0.060±0.003 0.104±0.005</td><td></td><td>0.096±0.008 0.148±0.011</td></tr><tr><td></td><td></td><td>Prediction-based ICL 0.744±0.008 0.120±0.017 0.061±0.003 0.103±0.0050.096±0.008 0.146±0.011</td><td></td><td></td></tr><tr><td></td><td></td><td></td><td>Instruction-based ICL 0.811±0.017 0.478±0.044 0.063±0.003 0.103±0.0050.102±0.009 0.146±0.011</td><td></td></tr><tr><td>Grad</td><td></td><td></td><td></td><td></td></tr><tr><td rowspan="9">Adult</td><td></td><td></td><td></td><td>0.999±0.001 0.999±0.001 0.056±0.006 0.221±0.011</td><td>|0.081±0.011 0.228±0.014</td><td></td></tr><tr><td>SG IG</td><td></td><td>0.999±0.001 0.999±0.001 0.056±0.006 0.221±0.011</td><td></td><td>0.080±0.011 0.227±0.014</td><td></td></tr><tr><td>ITG</td><td></td><td>1.000±0.000 1.000±0.000 0.056±0.0060.221±0.011</td><td></td><td>0.082±0.011 0.228±0.014</td><td></td></tr><tr><td>SHAP</td><td></td><td>0.385±0.012 0.099±0.019 0.215±0.011 0.061±0.007</td><td></td><td></td><td>0.227±0.014 0.075±0.010</td></tr><tr><td>LIME</td><td></td><td>0.387±0.012 0.150±0.020 0.215±0.011 0.061±0.007</td><td></td><td></td><td>0.225±0.014 0.075±0.010</td></tr><tr><td>Random</td><td></td><td>0.963±0.012 0.953±0.015 0.056±0.006 0.221±0.011</td><td></td><td></td><td>0.078±0.011 0.229±0.014</td></tr><tr><td></td><td></td><td>0.130±0.017 0.053±0.015 0.198±0.012 0.054±0.008 0.213±0.014 0.064±0.010</td><td></td><td></td><td></td></tr><tr><td>Prediction-based ICL</td><td></td><td>Perturbation-based ICL 0.589±0.018 0.516±0.027 0.079±0.007 0.212±0.0120.101±0.012 0.216±0.013</td><td></td><td></td><td></td></tr><tr><td>Instruction-based ICL</td><td></td><td>0.598±0.017 0.505±0.029 0.080±0.008 0.210±0.0110.106±0.014 0.207±0.014</td><td></td><td></td><td></td></tr><tr><td rowspan="9">Default Credit</td><td></td><td></td><td></td><td>0.748±0.020 0.716±0.027 0.069±0.007 0.217±0.0110.097±0.012 0.219±0.014</td><td></td><td></td></tr><tr><td>Grad</td><td></td><td>1.000±0.000 1.000±0.000 0.065±0.005 0.195±0.009|0.072±0.008 0.173±0.011</td><td></td><td></td><td></td></tr><tr><td>SG</td><td></td><td>1.000±0.000 1.000±0.000 0.065±0.005 0.195±0.009</td><td></td><td>0.072±0.008 0.172±0.011</td><td></td></tr><tr><td>IG ITG</td><td></td><td>1.000±0.000 1.000±0.000 0.065±0.005 0.195±0.009</td><td></td><td></td><td>0.074±0.008 0.172±0.010</td></tr><tr><td>SHAP</td><td></td><td>0.211±0.026 0.157±0.026 0.150±0.006 0.106±0.012</td><td></td><td></td><td>20.155±0.009 0.089±0.011</td></tr><tr><td></td><td></td><td>0.212±0.026 0.161±0.026 0.150±0.006 0.107±0.0120.150±0.008 0.098±0.012</td><td></td><td></td><td></td></tr><tr><td>LIME</td><td></td><td>0.988±0.005 0.985±0.007 0.065±0.005 0.195±0.009</td><td></td><td>0.071±0.008 0.173±0.010</td><td></td></tr><tr><td>Random</td><td></td><td>0.173±0.020 0.095±0.020 0.185±0.010 0.054±0.0060.176±0.011 0.053±0.007</td><td></td><td></td><td>Perturbation-based ICL 0.609±0.006 0.595±0.006 0.077±0.006 0.192±0.0090.077±0.008 0.170±0.011</td></tr><tr><td>Prediction-based ICL</td><td></td><td>0.577±0.009 0.565±0.010 0.080±0.007 0.189±0.0090.081±0.009 0.166±0.011</td><td></td><td></td><td></td></tr><tr><td></td><td></td><td>Instruction-based ICL 0.628±0.014 0.587±0.020 0.080±0.007 0.188±0.0100.085±0.009 0.163±0.011</td><td></td><td></td><td></td></tr></table>

Table 3: Results of explanations generated using Explanation-based ICL and six post hoc explanation methods for understanding model (Logistic Regression and Artificial Neural Network) predictions trained on three datasets. Shown are average and standard error metric values computed across 100 test samples. Arrows (↑, ↓) indicate the direction of better performance. Evaluation metrics were computed for the top-??, ?? being set to the number of features in each respective dataset.
<table><tr><td rowspan="2">Dataset</td><td rowspan="2">Method</td><td colspan="4">LR</td><td colspan="2">ANN</td></tr><tr><td>FA(↑)</td><td>RA(↑)</td><td>PGU (↓)</td><td>PGI (↑)</td><td>PGU (1)</td><td>PGI (↑)</td></tr><tr><td rowspan="11"></td><td></td><td>LLM-Lime0.708±0.006 0.465±0.009 0.013±0.000 0.041±0.001</td><td></td><td></td><td></td><td>0.074±0.009 0.099±0.012</td><td></td></tr><tr><td>Lime</td><td></td><td></td><td>1.000±0.000 1.000±0.000 0.008±0.000 0.043±0.000</td><td></td><td>0.044±0.006 0.121±0.013</td><td></td></tr><tr><td></td><td>LLM-Grad 0.997±0.003 0.996±0.004 0.008±0.000 0.043±0.000</td><td></td><td></td><td></td><td>0.058±0.009 0.116±0.012</td><td></td></tr><tr><td>Grad</td><td></td><td></td><td>1.000±0.000 1.000±0.000 0.008±0.000 0.043±0.000</td><td></td><td>0.044±0.006 0.120±0.013</td><td></td></tr><tr><td>LLM-SG</td><td></td><td>0.990±0.006 0.983±0.011 0.008±0.000 0.043±0.000</td><td></td><td></td><td>0.055±0.008 0.116±0.012</td><td></td></tr><tr><td>SG</td><td>1.000±0.000 1.000±0.000 0.008±0.000 0.043±0.000</td><td></td><td></td><td></td><td>0.044±0.006 0.120±0.013</td><td></td></tr><tr><td>LLM-IG</td><td></td><td>0.989±0.005 0.982±0.009 0.008±0.000 0.043±0.000</td><td></td><td></td><td>0.046±0.007 0.120±0.013</td><td></td></tr><tr><td>IG</td><td></td><td>1.000±0.000 1.000±0.000 0.008±0.000 0.043±0.000</td><td></td><td></td><td>0.044±0.006 0.120±0.013</td><td></td></tr><tr><td></td><td>LLM-Shap 0.684±0.013 0.401±0.025 0.020±0.001 0.034±0.001</td><td></td><td></td><td></td><td>0.069±0.009 0.102±0.012</td><td></td></tr><tr><td>Shap</td><td></td><td>0.773±0.014 0.516±0.033 0.015±0.001 0.038±0.001</td><td></td><td></td><td>0.066±0.009 0.107±0.012</td><td></td></tr><tr><td></td><td>LLM-ITG 0.702±0.013 0.387±0.029 0.017±0.001 0.036±0.001</td><td></td><td></td><td></td><td></td><td>0.069±0.010 0.105±0.012</td></tr><tr><td rowspan="11"></td><td>ITG</td><td>0.774±0.014 0.532±0.034 0.014±0.001 0.038±0.001</td><td></td><td></td><td></td><td>0.063±0.008 0.108±0.012</td></tr><tr><td>LLM-Lime 0.990±0.0010.958±0.005 0.029±0.0010.115±0.002</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Lime</td><td></td><td></td><td></td><td></td><td>0.048±0.0010.165±0.004</td></tr><tr><td>LLM-Grad 0.997±0.001 0.990±0.003 0.029±0.0010.115±0.002</td><td>1.000±0.000 1.000±0.000 0.029±0.002 0.116±0.006</td><td></td><td></td><td></td><td>0.044±0.004 0.164±0.012</td></tr><tr><td>Grad</td><td></td><td>1.000±0.000 1.000±0.000 0.029±0.002 0.116±0.006</td><td></td><td></td><td>0.048±0.0010.165±0.004</td></tr><tr><td>LLM-SG</td><td></td><td>0.997±0.001 0.990±0.003 0.029±0.001 0.115±0.002</td><td></td><td></td><td>0.043±0.004 0.165±0.012</td></tr><tr><td>SG Recidivism</td><td>1.000±0.000 1.000±0.000 0.029±0.002 0.116±0.006</td><td></td><td></td><td></td><td>0.047±0.0010.165±0.004 0.043±0.004 0.165±0.012</td></tr><tr><td>LLM-IG</td><td>0.996±0.001 0.988±0.003 0.029±0.001 0.115±0.002</td><td></td><td></td><td></td><td></td></tr><tr><td>IG</td><td></td><td>1.000±0.000 1.000±0.000 0.029±0.002 0.116±0.006</td><td></td><td></td><td>0.048±0.0010.166±0.004 0.044±0.004 0.165±0.012</td></tr><tr><td></td><td></td><td>LLM-Shap0.666±0.0040.216±0.0080.057±0.0010.098±0.002</td><td></td><td>0.082±0.002 0.151±0.004</td><td></td></tr><tr><td>Shap LLM-ITG</td><td></td><td>0.670±0.012 0.200±0.024 0.058±0.003 0.099±0.005</td><td></td><td></td><td>0.087±0.008 0.146±0.011</td></tr><tr><td rowspan="9"></td><td></td><td>0.690±0.004 0.247±0.008 0.056±0.001 0.099±0.002</td><td></td><td></td><td></td><td>0.085±0.002 0.148±0.004</td></tr><tr><td>ITG</td><td>0.689±0.011 0.195±0.022 0.056±0.003 0.100±0.005</td><td></td><td></td><td>0.078±0.007 0.149±0.011</td><td></td></tr><tr><td></td><td>LLM-Lime 0.909±0.001 0.632±0.005 0.023±0.001 0.222±0.003</td><td></td><td></td><td>0.035±0.002 0.230±0.004</td><td></td></tr><tr><td>Lime</td><td>0.907±0.005 0.743±0.017 0.018±0.002 0.224±0.011</td><td></td><td></td><td></td><td>0.029±0.005 0.235±0.014</td></tr><tr><td>Grad</td><td>LLM-Grad 0.938±0.000 0.801±0.0010.022±0.0010.223±0.003</td><td></td><td></td><td>0.035±0.002 0.230±0.004</td><td></td></tr><tr><td>LLM-SG</td><td>0.999±0.001 0.997±0.003 0.018±0.002 0.224±0.011</td><td></td><td></td><td></td><td>0.029±0.004 0.234±0.014</td></tr><tr><td>SG</td><td>0.938±0.000 0.802±0.001 0.022±0.001 0.223±0.003</td><td></td><td></td><td></td><td>0.035±0.002 0.230±0.004</td></tr><tr><td>LLM-IG</td><td>0.999±0.001 0.997±0.003 0.018±0.002 0.224±0.011</td><td></td><td></td><td></td><td>0.029±0.004 0.234±0.014</td></tr><tr><td>IG</td><td>0.938±0.000 0.804±0.000 0.022±0.001 0.223±0.003</td><td></td><td></td><td></td><td>0.033±0.002 0.231±0.004</td></tr><tr><td rowspan="9"></td><td></td><td>1.000±0.000 1.000±0.000 0.018±0.002 0.224±0.011</td><td></td><td></td><td>0.031±0.005 0.235±0.014</td><td></td></tr><tr><td></td><td>LLM-Shap0.676±0.0020.069±0.0030.109±0.0020.148±0.003</td><td></td><td></td><td></td><td></td></tr><tr><td>Shap</td><td>0.662±0.007 0.107±0.012 0.139±0.009 0.127±0.009</td><td></td><td></td><td>0.144±0.011 0.149±0.013</td><td>0.123±0.0030.153±0.004</td></tr><tr><td>LLM-ITG</td><td>0.665±0.002 0.039±0.002 0.107±0.002 0.150±0.003</td><td></td><td></td><td></td><td>0.132±0.003 0.146±0.004</td></tr><tr><td>ITG</td><td>0.627±0.006 0.068±0.010 0.175±0.010 0.099±0.009</td><td></td><td></td><td>0.170±0.011 0.130±0.013</td><td></td></tr><tr><td>Lime</td><td>LLM-Lime 0.954±0.0010.787±0.003 0.030±0.0010.189±0.003</td><td></td><td></td><td></td><td>0.042±0.002 0.178±0.003</td></tr><tr><td></td><td>0.977±0.004 0.878±0.015 0.030±0.003 0.201±0.009</td><td></td><td></td><td>0.042±0.002 0.178±0.003</td><td>0.037±0.004 0.186±0.010</td></tr><tr><td>Grad</td><td>LLM-Grad0.984±0.000 0.896±0.001 0.029±0.0010.189±0.003</td><td></td><td></td><td></td><td></td></tr><tr><td>LLM-SG</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td rowspan="11">Default Credit</td><td></td><td>1.000±0.000 1.000±0.000 0.030±0.003 0.201±0.009</td><td></td><td></td><td></td><td>0.038±0.005 0.185±0.011</td></tr><tr><td>SG</td><td>0.984±0.000 0.897±0.000 0.029±0.001 0.189±0.003 1.000±0.000 1.000±0.000 0.030±0.003 0.201±0.009</td><td></td><td></td><td></td><td>0.072±0.0030.165±0.003 0.037±0.004 0.185±0.011</td></tr><tr><td>LLM-IG</td><td>0.984±0.000 0.896±0.001 0.029±0.0010.189±0.003</td><td></td><td></td><td>0.041±0.002 0.179±0.003</td><td></td></tr><tr><td>IG</td><td>1.000±0.000 1.000±0.000 0.030±0.003 0.201±0.009</td><td></td><td></td><td>0.041±0.005 0.185±0.010</td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Shap</td><td>LLM-Shap0.543±0.0030.067±0.0040.088±0.0020.140±0.003</td><td>0.525±0.009 0.086±0.012 0.088±0.005 0.163±0.010</td><td></td><td></td><td>0.094±0.003 0.126±0.003 0.091±0.006 0.146±0.011</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td>LLM-ITG 0.526±0.003 0.052±0.003 0.088±0.002 0.139±0.003</td><td></td><td>0.091±0.002 0.129±0.003</td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>ITG</td><td></td><td>0.516±0.010 0.076±0.012 0.086±0.005 0.165±0.010</td><td></td><td>0.084±0.006 0.152±0.010</td><td></td></tr></table>

Table 4: Shown are the faithfulness scores for the most important feature value, top-?? = 1, identified by existing post hoc explanation methods as well as the three LLM methods which generated explanations from GPT-4 across four datasets and the ANN model.
<table><tr><td rowspan="2">Method</td><td colspan="2">Recidivism</td><td colspan="2">Adult</td><td colspan="2">Credit</td><td colspan="2">Blood</td></tr><tr><td>PGU (1↓)</td><td>PGI (↑)</td><td>PGU (1)</td><td>PGI (↑)</td><td>PGU (1)</td><td>PGI (↑)</td><td>PGU (↓)</td><td>PGI (↑)</td></tr><tr><td>Grad</td><td>0.147±0.011</td><td>0.117±0.010</td><td>0.103±0.013</td><td>0.224±0.014</td><td>0.085±0.009</td><td>0.166±0.010</td><td>0.087±0.012</td><td>0.103±0.012</td></tr><tr><td>SG</td><td>0.146±0.011</td><td>0.117±0.010</td><td>0.103±0.013</td><td>0.224±0.014 0.084±0.009</td><td></td><td>0.167±0.010 0.087±0.012</td><td></td><td>0.102±0.012</td></tr><tr><td>IG</td><td>0.147±0.011</td><td>0.116±0.010</td><td></td><td>0.103±0.013 0.225±0.014</td><td>0.085±0.009</td><td>0.167±0.010</td><td>0.087±0.012</td><td>0.103±0.012</td></tr><tr><td>ITG</td><td>0.154±0.012</td><td>0.084±0.009</td><td></td><td>0.232±0.014 0.056±0.009</td><td>0.181±0.010</td><td>0.057±0.009</td><td>0.103±0.012</td><td>0.083±0.012</td></tr><tr><td>SHAP</td><td>0.152±0.012</td><td>0.092±0.009</td><td></td><td>0.231±0.014 0.047±0.008</td><td>0.169±0.009</td><td>0.076±0.011</td><td>0.104±0.012</td><td>0.083±0.012</td></tr><tr><td>LIME</td><td>0.147±0.011</td><td>0.116±0.010</td><td>0.104±0.013</td><td>0.225±0.014</td><td>0.084±0.009</td><td>0.167±0.010</td><td>0.087±0.012</td><td>0.103±0.012</td></tr><tr><td>Random</td><td>0.163±0.012</td><td>0.062±0.009</td><td>0.228±0.014</td><td>0.031±0.008</td><td>0.187±0.011</td><td>0.033±0.006</td><td>0.115±0.012</td><td>0.067±0.010</td></tr><tr><td>Sec. 3.1</td><td>0.146±0.012</td><td>0.114±0.010</td><td></td><td>0.142±0.0150.179±0.015 0.083±0.009</td><td></td><td>0.166±0.011</td><td>0.085±0.012</td><td>0.099±0.013</td></tr><tr><td>Sec. 3.2</td><td>0.145±0.012</td><td>0.113±0.010 0.137±0.015 0.172±0.016 0.087±0.009 0.162±0.011</td><td></td><td></td><td></td><td></td><td>0.085±0.012</td><td>0.097±0.012</td></tr><tr><td>Sec. 3.3</td><td>0.149±0.011</td><td></td><td></td><td></td><td></td><td></td><td></td><td>0.113±0.010 0.121±0.014 0.202±0.014 0.097±0.010 0.151±0.011 0.094±0.012 0.084±0.012</td></tr></table>

Table 5: Shown are the faithfulness scores for the most important feature value, top-?? = 1, identified by existing post hoc explanation methods as well as the three LLM methods which generated explanations from GPT-4 across four datasets and the LR model. (Since FA = RA for top-?? = 1, we omit RA to prevent redundancy).
<table><tr><td rowspan="2">Method</td><td colspan="2">Recidivism</td><td colspan="2">Adult</td><td colspan="2">Credit</td><td colspan="2">Blood</td></tr><tr><td>FA()</td><td>PGU (1L)</td><td>FA(↑)</td><td>PGU (1↓)</td><td>FA(↑)</td><td>PGU (↓)</td><td>FA(↑)</td><td>PGU (1)</td></tr><tr><td>Grad</td><td>1.000±0.000</td><td>0.096±0.005</td><td>1.000±0.000</td><td>0.073±0.007</td><td>1.000±0.000</td><td>0.081±0.006</td><td>1.000±0.000</td><td>0.020±0.000</td></tr><tr><td>SG</td><td>1.000±0.000</td><td>0.095±0.005</td><td></td><td>1.000±0.000 0.073±0.007</td><td>1.000±0.000</td><td>0.081±0.006 1.000±0.000</td><td></td><td>0.020±0.000</td></tr><tr><td>IG</td><td>1.000±0.000</td><td>0.096±0.005</td><td>1.000±0.000</td><td>0.073±0.007</td><td>1.000±0.000</td><td>0.081±0.006</td><td>1.000±0.000</td><td>0.020±0.000</td></tr><tr><td>ITG</td><td>0.190±0.039</td><td>0.108±0.006</td><td>0.020±0.014</td><td>0.221±0.011</td><td>0.270±0.044</td><td>0.163±0.007</td><td>0.700±0.046</td><td>0.026±0.001</td></tr><tr><td>SHAP</td><td>0.210±0.041</td><td>0.108±0.006</td><td></td><td>0.020±0.014 0.221±0.011</td><td>0.270±0.044</td><td>0.163±0.007</td><td>0.700±0.046</td><td>0.026±0.001</td></tr><tr><td>LIME</td><td>1.000±0.000</td><td>0.096±0.005</td><td>0.990±0.010</td><td>0.221±0.011</td><td>1.000±0.000</td><td>0.081±0.006</td><td>1.000±0.000</td><td>0.020±0.000</td></tr><tr><td>Random</td><td>0.130±0.034</td><td>0.113±0.006</td><td>0.060±0.024</td><td>0.214±0.011</td><td>0.070±0.026</td><td>0.195±0.010</td><td>0.190±0.039</td><td>0.038±0.001</td></tr><tr><td>Sec. 3.1</td><td>0.000±0.000</td><td>0.101±0.005</td><td>0.821±0.039</td><td>0.101±0.010</td><td>1.000±0.000</td><td>0.081±0.007</td><td>0.978±0.015</td><td>0.020±0.000</td></tr><tr><td>Sec. 3.2</td><td>0.051±0.022</td><td>0.101±0.005</td><td></td><td></td><td></td><td></td><td>0.781±0.042 0.109±0.010 0.969±0.017 0.084±0.007 0.970±0.017</td><td>0.020±0.000</td></tr><tr><td>Sec. 3.3</td><td></td><td>0.490±0.050 0.098±0.005</td><td></td><td>0.919±0.027 0.086±0.009</td><td>0.926±0.027</td><td></td><td>0.090±0.007 0.758±0.045</td><td>0.025±0.001</td></tr></table>

Table 6: Run time in seconds across 100 samples for explanations generated using LLMs and other post hoc explanation methods.
<table><tr><td rowspan="2">Method</td><td colspan="3">LR</td><td colspan="6">ANN</td></tr><tr><td>COMPAS</td><td></td><td>Blood Adult</td><td>Credit</td><td>COMPAS</td><td></td><td>Blood Adult</td><td>Credit</td><td>Mean runtime (in secs)</td></tr><tr><td>Grad</td><td>0.183</td><td>0.001</td><td>0.002</td><td>0.001</td><td>0.003</td><td>0.001</td><td>0.002</td><td>0.002</td><td>0.024</td></tr><tr><td>SG</td><td>0.174</td><td>0.121</td><td>0.124</td><td>0.123</td><td>0.134</td><td>0.127</td><td>0.131</td><td>0.128</td><td>0.133</td></tr><tr><td>IG</td><td>0.044</td><td>0.043</td><td>0.043</td><td>0.043</td><td>0.047</td><td>0.045</td><td>0.047</td><td>0.046</td><td>0.045</td></tr><tr><td>ITG</td><td>0.001</td><td>0.001</td><td>0.001</td><td>0.001</td><td>0.001</td><td>0.001</td><td>0.002</td><td>0.001</td><td>0.001</td></tr><tr><td>SHAP</td><td>8.93</td><td>9.064</td><td>9.151</td><td>8.996</td><td>11.21</td><td>11.143</td><td>11.165</td><td>11.077</td><td>10.092</td></tr><tr><td>LIME</td><td>2.922</td><td>1.482</td><td>0.407</td><td>0.398</td><td>3.051</td><td>1.574</td><td>0.476</td><td>0.456</td><td>1.346</td></tr><tr><td>LLM</td><td>1732</td><td>1668</td><td>1418</td><td>1624</td><td>1578</td><td>1313</td><td>1349</td><td>1723</td><td>1550</td></tr></table>
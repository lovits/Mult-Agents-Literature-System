# Stay on topic with Classifier-Free Guidance

Anonymous authors Paper under double-blind review

## Abstract

Classifier-Free Guidance (CFG) (Ho & Salimans, 2021) has recently emerged in text-to-image generation as a lightweight technique to encourage promptadherence in generations. In this work, we demonstrate that CFG can be used broadly as an inference-time technique in pure language modeling. We show that CFG (1) improves the performance of Pythia, GPT-2 and LLaMAfamily models across an array of tasks: Q&A, reasoning, code generation, and machine translation, achieving SOTA on LAMBADA with LLaMA-7B over PaLM-540B; (2) brings improvements equivalent to a model with twice the parameter-count; (3) can stack alongside other inference-time methods like Chain-of-Thought and Self-Consistency, yielding further improvements in difficult tasks; (4) can be used to increase the faithfulness and coherence of assistants in challenging form-driven and content-driven prompts: in a human evaluation we show a 75% preference for GPT4All using CFG over baseline.

## 1 Introduction

In recent years large language models have exhibited strong generative capabilities to solve a diverse range of tasks (Devlin et al., 2019b; Brown et al., 2020; Scao et al., 2022b). “Prompting” is typically used to condition generation, with task instructions and context (Reynolds & McDonell, 2021), or a small set of examples (Brown et al., 2020). However, language generation, especially with smaller models, has been shown to struggle with issues such as hallucination (Manakul et al., 2023), degradation (Holtzman et al., 2019) and meandering (Spangher et al., 2023). Various approaches have been proposed to address this, e.g.: instructionfinetuning (Wei et al., 2021; Sanh et al.,

![](images/8316325aa94d86f8a3f0add1d9f324105b7c1e9b4b0719d9c9fdd5be34719dd1.jpg)  
Figure 1: A notional 2D projection of a textual latent space showing how increasing the guidance weight γ increases the importance of the prompt “Today in France,”.

2021) and reinforcement learning (Ouyang et al., 2022a; Askell et al., 2021; Bai et al., 2022). These techniques are expensive and their compute and data cost may not be accessible to all users. In this paper we propose an inference time methodology which, as shown in Figure 1, gives more importance to the user intent, expressed through the prompt. Our hypothesis in this paper is: focusing more on the prompt at inference-time will result in generations that better align with expected behavior.

Text-to-image-generation, too, has been shown to suffer from similar problems (Dhariwal & Nichol, 2021). Standard inference approaches can ignore parts of the prompt-conditioning, especially with specific or uncommon prompts (Nichol et al., 2022). Classifier Guidance (Dhariwal & Nichol, 2021) was proposed to enhance the generative quality of diffusion models, by using a separate classifier to encourage desired characteristics in the output image.

<table><tr><td colspan="2">Instruction: &quot;Respond enthusiastically to the following user prompt.&quot; Prompt: &quot;What was the Cambridge Analytica scandal?&quot;</td></tr><tr><td>Vanilla Sampling The Cambridge Analytica scandal was a</td><td>CFG-based Sampling</td></tr><tr><td>huge scandal in which it was revealed that Cambridge Analytica, a political consult- ing firm, had used personal data from Face- book to target and influence the 2016 US presidential election. This scandal raised questions about the role of social media in political campaigns...</td><td>Oh my goodness! What a scandal! The Cambridge Analytica scandal was when a company used personal information ob- tained through online activities to influ- ence political campaigns, essentially hack- ing people&#x27;s brains. It was a serious breach of trust and privacy, and rightfully so! It is a wake-up call for...</td></tr></table>

Table 1: Demonstration of CFG-guided generation for an assistant-style prompt (using GPT4All with γ = 5). The assistant has a system-level prompt (“Instructions”) that is potentially out-of-distribution (e.g. “ write an enthusiastic response”) and a user-level prompt (“Prompt”). In Vinalla Sampling, the model ignores the system-level directive, but with CFG, the model adheres to both the system-level and the user-level prompt.

Classifier-Free Guidance (CFG) (Ho & Salimans, 2021) was later introduced, in which the classifier is removed and the generative model itself is used as an implicit classifier.

Inspired by its effectiveness in the text-to-image-generation (Saharia et al., 2022; Ho & Salimans, 2021; Lin et al., 2023), we adapt CFG to unimodal text generation to increase the model alignment to the given prompt. While text-to-image models (which primarily utilize diffusion models) need to be specifically trained with conditioning dropout (Ho & Salimans, 2021) to utilize CFG, we show that, in text generation, we can use CFG out-of-the-box in many situations. We demonstrate the effectiveness of CFG to improve alignment on a wide range of prompting approaches including zero-shot prompting, Chain-of-Thought prompting, long-form generative prompting and complex chatbot-style prompting (see Table 1).

## We make the following contributions:

1. We devise a framework for using CFG in language modeling and show significant improvements across a range of standard benchmarks. These benchmarks capture a variety of different prompting techniques: basic prompting, chain-of-thought prompting, long-text prompting and chatbot-style prompting. Notably, we achieve SOTA on LAMBADA with LLaMA-7B over PaLM-540B.

2. We show that for the same inference cost, one can train a model that is half the size and obtain similar performance on those benchmarks;

3. By using a negative prompt, we demonstrate that we can have a more granular control over the aspects emphasized by CFG. In a blind human evaluation we show 75% preference for GPT4All using CFG over the vanilla sampling;

4. We provide interpretations for the impact that CFG on text generation both (1) qualitatively, by visualizing how CFG is upweighting words more related to the prompt (our visualization, we note, can be an integral part of effective prompt engineering) and (2) quantitatively, by showing that CFG decreases entropy in the sampling distribution.

## 2 Background (and Related Works)

## 2.1 Guidance in Text-to-Image Models

Let $\operatorname { P } _ { \theta } ( x )$ be the unconditional generative model for an image x with parameters θ. During inference, we wish to condition the generation on a label or text description c in order to model P(x|c). Generative models usually generate data from an abstract representation z in semantic space that is decoded into an actual sample (e.g. the latent vectors in GANs or the intermediate sampling steps in diffusion models). Controlling the generation usually involves guiding or adding constraints to that semantic representation. In Classifier Guidance (Dhariwal & Nichol, 2021), an auxiliary classifier $\scriptstyle { \bar { \mathrm { P } } } _ { \phi } ( c | x )$ is introduced, which guides the sampling from $\operatorname { P } _ { \theta } ( x )$ with the gradients $\gamma \nabla _ { z } \mathrm { P } _ { \phi } ( c | \dot { x } )$ to increase the likelihood of c for generation x. This modification results in approximate samples from the distribution:

$$
\widehat { \mathrm { P } } ( x | c ) \propto \mathrm { P } _ { \theta } ( x ) \cdot \mathrm { P } _ { \phi } ( c | x ) ^ { \gamma }\tag{1}
$$

where $\gamma$ is called the guidance strength. This guidance results in a reweighting of the density according to the classifier likelihood. For $\gamma = 0$ , it reduces to the unconditional generation, while $\gamma = 1$ reduces to the conditional generation. When $\gamma > 1$ then $\widehat { \mathrm { P } }$ overemphasizes the conditioning, which as noticed by Dhariwal & Nichol (2021) results in a better inception score at the cost of diversity. This approach has been successfully used in a variety of works (Gal et al., 2021; Kim et al., 2022; Crowson et al., 2022b)

Classifier-Free Guidance, (Ho & Salimans, 2021) observes that by using Bayes rule we can eliminate the necessity of an external classifier. By training the same model $\mathrm { P } _ { \theta }$ to support both conditional and unconditional generation with conditioning dropout, we can thus rewrite the second term in Equation 1 as $\begin{array} { r } { \mathrm { P } _ { \theta } ( c | x ) \propto \frac { \mathrm { P } _ { \theta } ( x | c ) } { \mathrm { P } _ { \theta } ( x ) } } \end{array}$ . Then, the sampling is performed according to the probability:

$$
{ \widehat { \mathrm { P } _ { \theta } } } ( x | c ) \propto { \frac { \mathrm { P } _ { \theta } ( x | c ) ^ { \gamma } } { \mathrm { P } _ { \theta } ( x ) ^ { \gamma - 1 } } } .\tag{2}
$$

Modeling the diffusion process with ${ \widehat \mathrm { P } } _ { \theta } ( x | c )$ effectively means predicting the PDF of the sample noise $\epsilon _ { t }$ as

$$
\log \widehat { \mathrm { P } _ { \theta } } ( \epsilon _ { t } | x _ { t + 1 } , c ) = \gamma \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } , c ) - ( \gamma - 1 ) \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } ) .\tag{3}
$$

An important tool with diffusion models is Negative Prompting (Du et al., 2020; Documentation; Crowson et al., 2022a; Rombach et al., 2021b). We can rewrite Equation 3 as

$$
\begin{array} { r } { \log \widehat { \mathrm { P } _ { \theta } } ( \epsilon _ { t } | x _ { t + 1 } , c ) = \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } ) + \gamma \big ( \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } , c ) - \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } ) \big ) } \end{array}\tag{4}
$$

Aside from its probabilistic interpretation, this equation also represents a vector arithmetic operation in latent space: we take a step of size γ away from the unconditional vector in the direction of the conditioning. Semantic vector linear arithmetic has proven to be effective in many situations in vision: striking examples have been generated by interpolations in GANs or diffusion models (Ling et al., 2021; Song et al., 2020; Brock et al., 2016).

Moreover, the initial point does not have to be the unconditional latent, but any representation we want to move away from. We can introduce the "negative conditioning" or "negative prompt" c, as well as a generalized equation resulting in Equation 3 when $\overline { { c } } = \emptyset$

$$
\begin{array} { r } { \log \widehat { \mathrm { P } _ { \theta } } ( \epsilon _ { t } | x _ { t + 1 } , c , \overline { { c } } ) = \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } , \overline { { c } } ) + \gamma \big ( \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } , c ) - \log \mathrm { P } _ { \theta } ( \epsilon _ { t } | x _ { t + 1 } , \overline { { c } } ) \big ) } \end{array}\tag{5}
$$

## 2.2 Classifier-Free Guidance of Language Models

We apply Classifier-Free Guidance the logits of next-token predictions produced by language models. These logits are linear transformers of word and sentence embeddings which, as demonstrated in Mikolov et al. (2013); Pennington et al. (2014) and Devlin et al. (2019a); Radford et al. (2018), capture semantic meaning of language. Additionally, using the logits avoids network editing (Belrose et al., 2023) and is architecture agnostic.

Next, we define conditioning, $^ { c , }$ in decoder-only language models. In the common situations, a user provides a prompt c which can be a context, an instruction, or the beginning of some text, and uses a language model to sample a sequence of continuation tokens $w _ { i }$ for the prompt c. Since a good continuation is expected to highly correlate to the prompt, we consider the prompt as our conditioning.

Similarly to Classifier Guidance (Dathathri et al., 2019; Yang & Klein, 2021; Spangher et al., 2023), we wish to generate a text w which has a high likelihood of starting with c. We define the γ-reweighted distribution $\widehat \mathrm { P } ( w | c ) \propto \mathrm { P } ( w ) \cdot \mathrm { P } ( c | w ) ^ { \gamma }$ , and approximate it with CFG as $\begin{array} { r } { \widehat { \mathrm { P } } ( w | c ) \propto \frac { \mathrm { P } ( w | c ) ^ { \gamma } } { \mathrm { P } ( w ) ^ { \gamma - 1 } } } \end{array}$

In the case of autoregressive language models modeling $\begin{array} { r } { \mathrm { P } _ { \theta } ( w ) = \prod _ { i } ^ { T } \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } ) } \end{array}$ , we can unroll the formulation and obtain Equation 2 again:

$$
\widehat { \mathrm { P } _ { \theta } } ( w | c ) \propto \prod _ { i = 1 } ^ { T } \widehat { \mathrm { P } _ { \theta } } ( w _ { i } | w _ { j < i } , c ) \propto \prod _ { i = 1 } ^ { T } \frac { \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } , c ) ^ { \gamma } } { \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } ) ^ { \gamma - 1 } } \propto \frac { \mathrm { P } _ { \theta } ( w | c ) ^ { \gamma } } { \mathrm { P } _ { \theta } ( w ) ^ { \gamma - 1 } }\tag{6}
$$

While conditioned diffusion models cannot predict unconditioned distributions without extra training, language models handle both $\mathrm P _ { \theta } ( \bar { w } | c )$ and $\mathrm P _ { \theta } ( w )$ naturally due to being trained on finite context windows. Being able to drop the prefix c is a natural feature. We can thus sample the next i-th token $w _ { i }$ in the logits space:

$$
\log \widehat { \mathrm { P } _ { \theta } } ( w _ { i } | w _ { j < i } , c ) = \log \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } ) + \gamma \big ( \log \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } , c ) - \log \mathrm { P } _ { \theta } ( w _ { i } | w _ { j < i } ) \big )\tag{7}
$$

This formulation can be extended to accomodate “negative prompting”, as in Equation 5. Negative prompting as applied in autoregressive LMs will be further addressed in Section 3.4. Now, we will continue on to the next section, where we introduce our experiments. In this section, we will explore the effects of CFG on different variations of prompting.

We note that recent works have explored CFG in language models (Malkin et al., 2022; Pei et al., 2023; Shi et al., 2023). However, these works have been limited to specific areas of generation, like toxicity. Our work is a broad exploration of CFG including experiments across a wide array of benchmarks, prompt variations, human-preference experiments and computing-analysis. See Appendix A for more details on these works and others.

## 3 Experiments

In this section we show that Classifier-Free Guidance reliably boosts performance across a variety of common prompting approaches. In Section 3.1 we show that CFG boosts zero-shot performance on a variety of standard NLP benchmarks, including achieving state-of-the-art performance on LAMBADA with LLaMA-7B. In Section 3.2 we apply CFG to Chain-of-Thought prompts Nye et al. (2022); Wei et al. (2022) an approach to allows the model to reason first before answering the question. Next, we test the performance of CFG on text-to-text generation prompts in Section 3.3. Finally, we show in Section 3.4 that CFG can be applied to assistant prompts (i.e. prompts with system-instructions).

## 3.1 Basic Prompting: Zero-Shot Prompts

To test basic, zero-shot prompting, we consider a suite of zero-shot benchmarks implemented in the Language Model Evaluation Harness Gao et al. (2021), which includes close-book QA Auer et al. (2023); Joshi et al. (2017), common sense reasoning tasks Zellers et al. (2019); Sakaguchi et al. (2021); Clark et al. (2019); Bisk et al. (2020); Cobbe et al. (2021b); Basu et al. (2020); Clark et al. (2018), and sentence completion-tasks Paperno et al. (2016). In these settings, the desired completions are short (often 1-2 tokens), so risks of meandering Spangher et al. (2023) or degradation Holtzman et al. (2019) are low. We hypothesize that the main impact of CFG in these settings will be to reduce variance in output choices, as we explore more in Section 5.

We evaluate the GPT-2 model familyRadford et al. (2019), the Pythia model family Biderman et al. (2023) and the LLaMA model familyTouvron et al. (2023) using different guidance strengths across a range of standard NLP benchmarks using EleutherAI’s Language Model Evaluation Harness Gao et al. (2021) and implement CFG by starting the unconditional prompt at the last token of the initial prompt. The results are shown in Table 4. For better visualization, the charts for the GPT2 models, the Pythia models and the LLaMA models over the standard benchmarks are also shown in Figure 5, 6, and 7, respectively. We observe that except ARC (challenge) and Winogrande, the boost of performances from CFG is nontrivial and consistent. The reasons for discrepancies on these tasks are still unknown.

![](images/bc54d092cf73736f69f4c86c5dd8c29425146ceaee10e05613405e25b64683f1.jpg)  
Guidance Strength (CFG y)

![](images/d0aabc18cad45d49bffefe5a9e0aaff1d5ea1bd504b20eee00b6ee9c944ff6be.jpg)  
Guidance Strength (CFG y)  
Figure 2: CFG impact on chain-of-thought prompting with respect to GSM8K dataset. For small CFG values, using CFG increases the percentage of chains which end in a valid answer structure while increasing the model accuracy. For large values the invalid percentage remains small but the accuracy drop.

Furthermore, we note that even the smallest LLaMA 7B model achieves 81% accuracy in Lambada (OpenAI) zero-shot benchmark with $\gamma = 1 . 5 $ , outperforming the current SOTA (zero-shot) of PaLM-540B (77.9%). Despite the fact that CFG almost doubles the computation during inference, the comparison is still noteworthy given that other models with comparable performances on Lambada (OpenAI) have much more parameters and would still require more compute than LLaMA 7B with CFG. Taken together, we show that CFG increases performance in basic prompting settings significantly.

## 3.2 Deliberative Prompting: Chain-of-Thought

A variation on basic prompting is Chain-of-Thought (CoT) prompting Wei et al. (2022). In this setting, the model is prompted to generate a series of reasoning steps before giving an answer to the task: i.e. $p ( w _ { c o t } , w _ { a } | c )$ , where ${ w _ { c o t } }$ is a set of reasoning steps and $w _ { a }$ is the answer. CoT has been shown to perform well in complex reasoning tasks that cannot be fully addressed by model- or data-scaling Rae et al. (2021).

However, as observed by Wei et al. (2022), long reasoning chains can diverge and either not generate correct answers, or not generate parsable results. We hypothesize CFG will be able to enforce better reasoning chains with less drift.

We evaluate on two arithmetic reasoning tasks: GSM8K Cobbe et al. (2021a) and AQuA Ling et al. (2017). We follow Wang et al. (2023)’s few-shot prompt and use two open source LLM models: WizardLM-30B Xu et al. (2023) and Guanaco-65B Dettmers et al. (2023). As can be seen in Figure 2, 13, using CFG increases the percentage of CoT resulting in valid, parsable answers. For low guidance strengths, model performances increase. However, for $\gamma > 1 . 5$ , the quality of reasoning chains degrade, and overall the performances drop1.

We anticipate in future work being able to more fully test variations of CFG-weighting on different parts of the CoT process. CFG’s interactions with CoT; for instance, instead of upweighting just $w _ { p } ,$ we might upweight $w _ { p } , w _ { c o t }$ , or other variations.

## 3.3 Long Prompts: Generation

In contrast to basic prompting and CoT-prompting (Sections 3.1 and 3.2), where we primarily expect short answers, here we study tasks where prompts and continuations are both potentially long sequences of text. We focus on code generation here, and in Appendix C.1, we study machine translation. In these settings and the quality of answers is highly dependent on the model’s ability to stay on target. We hypothesize that, in these settings, CFG can effectively enforce adherence to the full prompt.

<table><tr><td rowspan="2">γ</td><td colspan="3">CodeGen-350M</td><td colspan="3">CodeGen-2B</td><td colspan="3">CodeGen-6B</td></tr><tr><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td></tr><tr><td>1.0</td><td>11.0%</td><td>17.0%</td><td>22.0%</td><td>19.5%</td><td>25.5%</td><td>29.8%</td><td>19.5%</td><td>25.5%</td><td>29.8%</td></tr><tr><td>1.1</td><td>11.8%</td><td>18.1%</td><td>20.1%</td><td>20.4%</td><td>25.4%</td><td>28.0%</td><td>20.4%</td><td>25.4%</td><td>2.0%</td></tr><tr><td>1.25</td><td>11.4%</td><td>17.3%</td><td>18.9%</td><td>19.7%</td><td>25.4%</td><td>28.0%</td><td>19.7%</td><td>25.4%</td><td>28.0%</td></tr><tr><td>1.5</td><td>10.9%</td><td>16.7%</td><td>18.3%</td><td>20.9%</td><td>26.7%</td><td>29.2%</td><td>20.9%</td><td>26.7%</td><td>29.2%</td></tr><tr><td>1.75</td><td>10.3%</td><td>16.0%</td><td>18.2%</td><td>20.4%</td><td>26.2%</td><td>28.6%</td><td>20.4%</td><td>26.2%</td><td>28.6%</td></tr><tr><td>2.0</td><td>8.6%</td><td>14.6%</td><td>17.6%</td><td>16.5%</td><td>22.4%</td><td>24.4%</td><td>16.5%</td><td>22.4%</td><td>24.4%</td></tr></table>

Table 2: CodeGen results with temperature= 0.2. CFG in nearly all cases increases performance, but the optimal γ value varies.

## 3.3.1 Program synthesis evaluations

Program synthesis presents us with a scenario where adherence to the full prompt is essential to performance. Additionally, testing CFG on code-related tasks also demonstrates CFG’s impact over formal language. Here, we prompt GPT-J Wang & Komatsuzaki (2021) and CodeGen-350M-mono Nijkamp et al. (2023) for code generations and observe positive results (see Appendix C.2), such as an 18% improvement of the accuracy rate for GPT-J, and a 37% improvement of syntax correctness rate for CodeGen-350M-mono with positive guidance.

Next, we evaluate CFG on the HumanEval benchmark Chen et al. (2021). The HumanEval benchmark contains 164 coding tasks in Python, with English prompts given by a function signature and a docstring. The model generates code-based continuations of the prompt, which are tested against unit tests to evaluate the correctness of programs. We choose CodeGen-350M-mono, CodeGen-2B-mono and CodeGen-6B-mono (Nijkamp et al. (2023)) which are designed for Python program synthesis.2

We test different CFG strengths3 and different temperatures, evaluating at pass@k for $k = 1 , 1 0 , 1 0 0 ^ { \mathrm { ~ 4 ~ } }$ . We show the results for temperature= 0.2 in Table 25. The pass@1 rate, we find, increases with CFG across $1 \leq \gamma \leq 1 . \bar { 5 }$ and degrades thereafter, in accordance with findings in Section 3.2. As shown in Table 3, the number of tasks where CFG outperforms is more than the one where CFG underperforms at pass@1 for γ = 1, 1.25 with CodeGen-350M-mono.6.

We note that the improvement from CFG diminishes or harms performance at high k. Without CFG, many tasks exhibit small nonzero passing rates, while having 0% rate with CFG. This indicates that larger k significantly boosts the passing rate of difficult tasks where the rates are low but nonzero. Overall, the consistent improvement on pass@1 rates and the reduced effect on pass@100 rates support our hypothesis that CFG strengthens the adherence to the prompt at the small cost of reduced variability and creativity.

![](images/a2df85a42bbf8488e8fb4b3938cf7eb8720d03312ef38884420f6f4690865f1b.jpg)  
Figure 3: HumanEval task count comparison between $\gamma = 1$ , 1.25 for CodeGen-350M-mono

![](images/c3275ae2a9c3a5f0e4b8f79bc0b2065899c2edb0c9eecd8de1f2598f66b81a4a.jpg)  
Figure 4: Evaluators (611 votes, 71 voters) noted that CFG adhered to the systemprompt significantly more at $\gamma = 3 .$ Userprompt adherence does not degrade.

## 3.4 Negative Prompting: Improving Assistants

Finally, we explore an addition to Classifier-Free Guidance called negative prompting. With negative prompting, the user specifies what they do not want in the output (e.g. “low resolution” in text-to-image), which is then used to better meet user needs.

We explore this idea in the context of chatbots. Chatbots give us a setting where the prompt is expanded into a multi-stage prompt 7. In chatbots, the language model is prompted with a two-part prompt: (1) the instruction, or "system prompt" which may give contextual information or behavioral guidelines (e.g. style, alignment, persona, etc.); and (2) the userprompt, or the user’s query. See Table 1 for an example. Adherence becomes an even greater concern: systems like Alpaca Taori et al. (2023) often ignore changes to their system-prompt, and may even expose models to attacks like prompt injection Greshake et al. (2023).

We explore CFG with negative prompting to increase the success of different system prompts. We set the negative prompt c, see Equation 5, to be the default system-prompt for our models (i.e. “The prompt below is a question to answer, a task to complete, or a conversation to respond to; decide which and write an appropriate response.”) and set c to be the edited prompt (e.g. “The prompt below is a question to answer, a task to complete, or a conversation to respond to; decide which and write a sad response.”).

To test this approach with chatbots, we generate system-prompts, $n _ { c } = 2 5$ , and user-prompts, $n _ { p } = 4 6 { . }$ , and sample 1740 random combinations of them (in Appendix F we include the full list of c and p we use). We use GPT4All-J v1.3-jazzy to generate two completions for each sampled combination: the first is sampled without CFG, and the second is sampled with CFG, with a guidance strength randomly chosen $\in { } 1 , 2 , 3 , 4 , 5 , 6 { }$ . Our hypothesis is that CFG increases system-prompt following, ideally without hurting the relevance to the user input.

We run a human preference study on our sampled continuations, where participants are shown both, blindly, and asked to assess two things: A. which output better follows the system-prompt, c and B. which output better follows the user-prompt p. Our results in Figure 4 shows evidence that CFG emphasized the difference between c and c more than sampling with c alone. There is a peak at $\gamma = 3$ with 75% of system-prompt following preference over $\gamma = 1$ and undegraded user-prompt relevance (52%).

## 4 Computational Cost Analysis

In the previous section we showed improvements across a wide array of benchmarks and contexts. However, since classifier-free guidance requires two passes through the network, users who are compute-constrained rather than VRAM constrained might wonder if CFG is interesting to them at all, and if they should not run a model twice as big instead.

To answer this question, we calculate the FLOP for each of the benchmark experiments that we ran in Section 3.1. We then compare across model sizes, with and without CFG. We conclude with the surprising finding that, across 5 out of 9 tasks, there there is a statistically insignificant difference between using CFG and using vanilla prompting with a model of twice the size at $p = . 0 1$ , according to ANCOVA regression analysis (Rutherford, 2011). Of the significantly different tasks, 2 favor CFG and 2 favor vanilla. See Appendix B.2, specifically Figure 8, for more details.

In other words, and most significantly, this indicates that, overall, a model using CFG can generally perform just as well as a model twice as large. This has enormous implications for training budgets and inference latency, because smaller models limit VRAM usage. We pause to note, though, that the impact of CFG on VRAM is nuanced. While CFG boosts the performance of smaller models, it doubles the demands of the kv cache. We conduct a memory analysis in Appendix B.3 to explore the conditions under which CFG is a more prudent use of memory than a larger vanilla model, and find that it is highly dependent on sequence length the user wishes to generate. We hope to explore further implications, as well as further reduction strategies, in future work.

## 5 Explaining the Success of Classifier-Free Guidance

In this section, we seek to explain the impact of Classifier-Free Guidance on generation. For these explorations, we use the Falcon-7b-Base model family (Almazrouei et al., 2023) as an exploratory model and, when applicable, compare against the Falcon-7b-Instruct version. We run these models on a sample dataset of 32, 902 datapoints from P3 (Sanh et al., 2021). We replicate our findings on other models and datasets as well: the Open-Assistant Dataset (Köpf et al., 2023) and Redpajama-3b model family8.

## 5.1 Classifier-Free Guidance’s Effect on Sampling Entropy

We suspect that CFG, by focusing $\mathrm { P } ( y | x )$ on the prompt, will reduce the entropy of the logit distribution. CFG entropy distribution is significantly lower across generation time-steps vanilla prompting, with a mean of 4.7 vs. 5.4.9. This restricts the number of tokens in the top-p=90% of the vocabulary distribution. We do observe qualitatively, in Section 5.3, that the top tokens re-order, showing that CFG is not simply having the same effect as the temperature parameter.

## 5.2 CFG’s Relation to Instruction Tuning

Our next question: how is Classifier-Free Guidance affecting the vocabulary distribution? We hypothesize that CFG has similar effects to instruction-tuning, which also encourages a model to focus on the prompt (Webson & Pavlick, 2021). Although CFG and Instruction-Tuned model variants have similar entropy across generation samples, the vocabulary distributions across our samples are largely not overlapping, indicating, on the average P3 prompt, CFG is not having a similar effect as instruction-tuning (see Appendix D).

There are cases where the two are similar. We observe a significant spearman correlation of $r _ { s } ~ = ~ . 0 5$ between prompt-length and Instruction/CFG agreement. We also observe small but significant correlations between perplexity and agreement. As shown in Table 15, harder phrases for Instruction-Tuned models are typically where CFG and Instruction-Tuned models align. We conclude that CFG is altering the model in ways that might complement instruction-tuning, opening the door to future explorations.

<table><tr><td>current</td><td>top1</td><td>top2</td><td>top3</td><td>top4</td><td>top5</td><td>…</td><td>bottom5</td><td>bottom4</td><td>bottom3</td><td>bottom2</td><td>bottom1</td></tr><tr><td>France</td><td>flipping</td><td>destroying</td><td>waking</td><td>stopping</td><td>causing</td><td>…·</td><td>guiName</td><td>ufact</td><td>Outs</td><td>kees</td><td>&quot;H,.&quot;</td></tr><tr><td></td><td> crashing</td><td>landing</td><td>oaring</td><td>swoop</td><td>plummet</td><td>…</td><td>soDeliveryDate</td><td>POLIT</td><td>Occupations</td><td>568</td><td>publishes</td></tr><tr><td>&#x27;landing</td><td>neigh</td><td>invis</td><td>atop</td><td>overhead</td><td>omin</td><td>…·</td><td>quotas</td><td>Russo</td><td>G Germans</td><td>passports</td><td>hostages</td></tr><tr><td>on</td><td>Buildings</td><td>skysc</td><td>rooft</td><td>Cheong</td><td>Plaza</td><td>…·</td><td></td><td>MFT</td><td>x</td><td></td><td>DragonMagazine</td></tr><tr><td>Notre</td><td>Basil</td><td>Mos</td><td>Cathedral</td><td>Mosque</td><td>Eugene</td><td>.…·</td><td>voyage</td><td>alach</td><td>urse</td><td>arb</td><td>sb</td></tr><tr><td>Dame</td><td>Cathedral</td><td>monument</td><td>cathedral</td><td>Basil</td><td>Mosque</td><td>…·</td><td>voyage</td><td>aila</td><td>voy</td><td>aund</td><td>wk</td></tr><tr><td>Cathedral</td><td></td><td>.&quot;[</td><td>slowing</td><td>blocking</td><td>ortex</td><td>…·</td><td>ashore</td><td>seaf</td><td>aund</td><td>Tact</td><td>Wanted</td></tr><tr><td></td><td>&quot;Dragon</td><td>dragons</td><td>dragon</td><td>Dragon</td><td>Dragons</td><td>·.·</td><td>1915</td><td>1914</td><td>1944</td><td>1934</td><td>1913</td></tr><tr><td>It</td><td>swoop</td><td>circled</td><td>dart</td><td>hopped</td><td>bolted</td><td>…·</td><td>concludes</td><td>reads</td><td>reads</td><td>culmin</td><td>marks</td></tr><tr><td>circled</td><td>skysc</td><td>pedestrians</td><td>architectural</td><td>hanging</td><td>skyline</td><td>…</td><td>Newfoundland</td><td>Ukrain</td><td>Zamb</td><td>Johnston</td><td>Queensland</td></tr><tr><td>Paris</td><td>night</td><td>amura</td><td>rum</td><td>anim</td><td>animate</td><td>…·</td><td>prematurely</td><td>capit</td><td>bombed</td><td>Mé</td><td>owing</td></tr><tr><td>a</td><td>longer</td><td>while</td><td>long.</td><td>awhile</td><td>length</td><td>.…</td><td>ims</td><td>chin</td><td>chel</td><td>ille</td><td>ller</td></tr><tr><td>bit</td><td>longer</td><td>MORE</td><td>awhile</td><td>again</td><td>more</td><td>…·</td><td>prematurely</td><td>hof</td><td>nw</td><td>arri</td><td>trop</td></tr><tr><td></td><td>startled</td><td>feathers</td><td>dragon</td><td>wings</td><td>dragons</td><td>.…·</td><td>inval</td><td>Junction</td><td>Palest</td><td>endas</td><td>CVE</td></tr><tr><td>&#x27;and</td><td>dragon</td><td>dragons</td><td>golden</td><td>Winged</td><td>perched</td><td>..·</td><td>CVE</td><td>inval</td><td>Ukrain</td><td>onet</td><td>Commodore</td></tr><tr><td>then</td><td>dragon</td><td>DRAG</td><td>dragons</td><td>neigh</td><td>DRAGON</td><td>…·</td><td>CVE</td><td>onet</td><td>Kear</td><td>TPS</td><td>Tags</td></tr><tr><td>flew</td><td>ukong</td><td>skelet</td><td>rum</td><td>swoop</td><td>acles</td><td>.…·</td><td>RG</td><td>thouse</td><td>NJ.</td><td>444</td><td>programmes</td></tr><tr><td>over</td><td>rium</td><td>Rockefeller</td><td>Plaza</td><td>TTimes</td><td>Symphony</td><td>…·</td><td>Brittany</td><td>Newfoundland</td><td>Balt</td><td>isconsin</td><td> Ygoslavia</td></tr><tr><td>the</td><td>Griffith</td><td>Ze</td><td>Hag</td><td>Science</td><td>Raphael</td><td>…·</td><td>shire</td><td>idlands</td><td>frontier</td><td>deserts</td><td>Balkans</td></tr><tr><td>E</td><td>BI</td><td>Rowe</td><td>ident</td><td>Methodist</td><td>allah</td><td>…·</td><td>coasts</td><td>ento</td><td>bys</td><td>seys</td><td>Desire</td></tr><tr><td>iff</td><td>Armory</td><td>ibrary</td><td>restrooms</td><td>Mansion</td><td>Mahmoud</td><td>…·</td><td>indo</td><td>onne</td><td>Off</td><td>itime</td><td>Norm</td></tr><tr><td>el</td><td>restaurant</td><td>Middle</td><td>restroom</td><td>boutique</td><td>museum</td><td>…·</td><td>iband</td><td>throats</td><td>centres</td><td>detach</td><td>rift</td></tr><tr><td>Tower</td><td>Property</td><td>omin</td><td>Foundation</td><td>Creature</td><td>&gt;&quot;</td><td>.…</td><td>gee</td><td>thence</td><td>pheus</td><td>hither</td><td>favourable</td></tr><tr><td></td><td>dragons</td><td>dragon</td><td>Dragons</td><td> Dragon</td><td>DRAGON</td><td>.</td><td>1944</td><td>1942</td><td>Instrument</td><td>Balt</td><td>1943</td></tr><tr><td>Then</td><td>dragons</td><td>dragon</td><td>dragon</td><td> Dragons</td><td>Dragon</td><td>…·</td><td>Manz</td><td>Hopkins</td><td>CVE</td><td>Instrument</td><td>Squadron</td></tr><tr><td>it</td><td>dragon</td><td>dragons</td><td>neigh</td><td>WWinged</td><td>Draco</td><td>…</td><td>CVE</td><td>udder</td><td>services</td><td>corrections</td><td> obies</td></tr><tr><td>flew</td><td>upro</td><td>ukong</td><td>rum</td><td>walked</td><td>&quot;</td><td>..·</td><td>INC</td><td>inary</td><td>lein</td><td>auxiliary</td><td>CVE</td></tr><tr><td>over</td><td>Chinatown</td><td>Financial</td><td>Spider</td><td>tallest</td><td>Financial</td><td>…</td><td>warr</td><td></td><td>quickShip</td><td>Newfoundland</td><td></td></tr></table>

Table 3: Given the prompt The dragon flew over Paris, France we display, at each sampling step, the vocabulary ranked for $\mathrm { P } ( w _ { t } | w _ { < t } ) - \log \mathrm { P } ( w _ { T } | \hat { w } )$ for the next step. We can see CFG encouraging tokens about flying dragons and Paris, and discouraging other topics or regions

## 5.3 Visualizing Classifier-Free Guidance

Finally, we provide qualitative insights into the reordering of the vocabulary, after Classifier-Free Guidance is applied. We visualize the vocabulary at each timestep ranked by the difference log $\mathrm { P } ( w _ { t } | \hat { w } _ { < t } ) - \log \mathrm { P } ( w _ { T } | \hat { w } )$ , showing which tokens are encouraged or discouraged the most. In Figure 3, we prompt a model with $c = ^ { 6 9 } \mathrm { I }$ he dragon flew over Paris, France” $\textstyle { \overline { { \mathcal { c } } } } = \emptyset$ and observe that tokens about dragons and Paris get upweighted while tokens about other locations (“Queensland”), dates (“1913”), or topics (“hostages”, “ ‘voyages”) are downweighted. This indicates that CFG encourages and discourages tokens due to their relatedness to the prompt.

## 6 Conclusion

We have shown that Classifier-Free Guidance, which was originally conceived of in textto-image applications, can be an effective way of increasing adherence to the prompt in autoregressive language modeling. In contrast to text-to-vision, CFG in autoregressive language modeling works out-of-the-box, without the need to further train the model. We have shown that CFG can boost performance across an array of different prompting styles: basic, chain-of-thought prompting, long text and chatbot prompting. Finally, we explain the effects of CFG by showing it decreased sampling entropy, but not in the same ways that Instruction-tuned models do. Ultimately, we leave for future work the exact effects that CFG is having, but we propose qualitative visualizations that confirm our intuitions around prompt adherence.

Our work also integrates into a growing body of inference techniques aimed at perturbing the logit distributions of an LM (Li et al., 2022b; Shi et al., 2023). We demonstrate that by doubling the inference FLOP using CFG brings performances of a model about twice the size. This allows training smaller models, which can be ran on smaller hardware, and are cheaper to train.

Our work faces the following limitations: CFG requires tweaking and exploration: γ values that might work in one context (i.e. long-form generation) might be poorly suited for another context. It’s also possible that CFG might be misused. We have not tested the effects of CFG if used in conjunction with malicious strategies for hacking language models, including prompt injection and alignment-overriding. We tried to explore this at length, both quantitatively and qualitatively, and we designed tasks that might reveal such behavior. However, we cannot conclude this method is risk-free. We advocate for standardized benchmarks aimed more squarely at language-model risk (including, possibly, pairs of models along with known prompt injections). Such standardized benchmarks could help us unit-test an advancement like CFG before releasing it into the wild.

## References

Ebtesam Almazrouei, Hamza Alobeidli, Abdulaziz Alshamsi, Alessandro Cappelli, Ruxandra Cojocaru, Merouane Debbah, Etienne Goffinet, Daniel Heslow, Julien Launay, Quentin Malartic, Badreddine Noune, Baptiste Pannier, and Guilherme Penedo. Falcon-40B: an open large language model with state-of-the-art performance. 2023.

Amanda Askell, Yuntao Bai, Anna Chen, Dawn Drain, Deep Ganguli, Tom Henighan, Andy Jones, Nicholas Joseph, Ben Mann, Nova DasSarma, et al. A general language assistant as a laboratory for alignment. arXiv preprint arXiv:2112.00861, 2021.

Sören Auer, Dante AC Barone, Cassiano Bartz, Eduardo G Cortes, Mohamad Yaser Jaradeh, Oliver Karras, Manolis Koubarakis, Dmitry Mouromtsev, Dmitrii Pliukhin, Daniil Radyush, et al. The sciqa scientific question answering benchmark for scholarly knowledge. Scientific Reports, 13(1):7240, 2023.

Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, et al. Constitutional ai: Harmlessness from ai feedback. arXiv preprint arXiv:2212.08073, 2022.

Regina Barzilay and Mirella Lapata. Modeling local coherence: An entity-based approach. Computational Linguistics, 34(1):1–34, 2008.

Kinjal Basu, Farhad Shakerin, and Gopal Gupta. Aqua: Asp-based visual question answering. In Practical Aspects of Declarative Languages: 22nd International Symposium, PADL 2020, New Orleans, LA, USA, January 20–21, 2020, Proceedings 22, pp. 57–72. Springer, 2020.

Nora Belrose, David Schneider-Joseph, Shauli Ravfogel, Ryan Cotterell, Edward Raff, and Stella Biderman. Leace: Perfect linear concept erasure in closed form. arXiv preprint arXiv:2306.03819, 2023.

Stella Biderman and Edward Raff. Fooling moss detection with pretrained language models. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management, pp. 2933–2943, 2022.

Stella Biderman, Hailey Schoelkopf, Quentin Anthony, Herbie Bradley, Kyle O’Brien, Eric Hallahan, Mohammad Aflah Khan, Shivanshu Purohit, USVSN Sai Prashanth, Edward Raff, Aviya Skowron, Lintang Sutawika, and Oskar van der Wal. Pythia: A suite for analyzing large language models across training and scaling, 2023.

Yonatan Bisk, Rowan Zellers, Jianfeng Gao, Yejin Choi, et al. Piqa: Reasoning about physical commonsense in natural language. In Proceedings of the AAAI conference on artificial intelligence, volume 34, pp. 7432–7439, 2020.

Ondrej Bojar, Christian Buck, Christian Federmann, Barry Haddow, Philipp Koehn, Johannes Leveling, Christof Monz, Pavel Pecina, Matt Post, Herve Saint-Amand, Radu Soricut, Lucia Specia, and Ale s Tamchyna. Findings of the 2014 workshop on statistical machine translation. In Proceedings of the Ninth Workshop on Statistical Machine Translation, pp. 12–58, Baltimore, Maryland, USA, June 2014. Association for Computational Linguistics. URL http://www.aclweb.org/anthology/W/W14/W14-3302.

Andrew Brock, Theodore Lim, JM Ritchie, and Nick Weston. Neural photo editing with introspective adversarial networks. In International Conference on Learning Representations, 2016.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Josh Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba. Evaluating large language models trained on code. 2021.

Jan Chorowski and Navdeep Jaitly. Towards better decoding and language model integration in sequence to sequence models. arXiv preprint arXiv:1612.02695, 2016.

Christopher Clark, Kenton Lee, Ming-Wei Chang, Tom Kwiatkowski, Michael Collins, and Kristina Toutanova. Boolq: Exploring the surprising difficulty of natural yes/no questions. arXiv preprint arXiv:1905.10044, 2019.

Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord. Think you have solved question answering? try arc, the ai2 reasoning challenge. arXiv:1803.05457v1, 2018.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, and John Schulman. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021a.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021b.

Katherine Crowson, Stella Biderman, Daniel Kornis, Dashiell Stander, Eric Hallahan, Louis Castricato, and Edward Raff. Vqgan-clip: Open domain image generation and editing with natural language guidance. In Computer Vision–ECCV 2022: 17th European Conference, Tel Aviv, Israel, October 23–27, 2022, Proceedings, Part XXXVII, pp. 88–105. Springer, 2022a.

Katherine Crowson, Stella Biderman, Daniel Kornis, Dashiell Stander, Eric Hallahan, Louis Castricato, and Edward Raff. Vqgan-clip: Open domain image generation and editing with natural language guidance. In Computer Vision–ECCV 2022: 17th European Conference, Tel Aviv, Israel, October 23–27, 2022, Proceedings, Part XXXVII, pp. 88–105. Springer, 2022b.

Sumanth Dathathri, Andrea Madotto, Janice Lan, Jane Hung, Eric Frank, Piero Molino, Jason Yosinski, and Rosanne Liu. Plug and play language models: A simple approach to controlled text generation. arXiv preprint arXiv:1912.02164, 2019.

Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, and Luke Zettlemoyer. Qlora: Efficient finetuning of quantized llms, 2023.

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. Bert: Pre-training of deep bidirectional transformers for language understanding. ArXiv, abs/1810.04805, 2019a.

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. BERT: Pre-training of deep bidirectional transformers for language understanding. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pp. 4171– 4186, Minneapolis, Minnesota, June 2019b. Association for Computational Linguistics. doi: 10.18653/v1/N19-1423. URL https://aclanthology.org/N19-1423.

Prafulla Dhariwal and Alexander Nichol. Diffusion models beat gans on image synthesis. Advances in Neural Information Processing Systems, 34:8780–8794, 2021.

Stable Diffusion Documentation. How does negative prompt work? https:// stable-diffusion-art.com/how-negative-prompt-work/.

Yilun Du, Shuang Li, and Igor Mordatch. Compositional visual generation with energy based models. Advances in Neural Information Processing Systems, 33:6637–6647, 2020.

Virginia K Felkner, Ho-Chun Herbert Chang, Eugene Jang, and Jonathan May. Towards winoqueer: Developing a benchmark for anti-queer bias in large language models. arXiv preprint arXiv:2206.11484, 2022.

Zihao Fu, Wai Lam, Anthony Man-Cho So, and Bei Shi. A theoretical analysis of the repetition problem in text generation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 35, pp. 12848–12856, 2021.

Rinon Gal, Or Patashnik, Haggai Maron, Gal Chechik, and Daniel Cohen-Or. Stylegan-nada: Clip-guided domain adaptation of image generators. arXiv preprint arXiv:2108.00946, 2021.

Leo Gao, Jonathan Tow, Stella Biderman, Sid Black, Anthony DiPofi, Charles Foster, Laurence Golding, Jeffrey Hsu, Kyle McDonell, Niklas Muennighoff, Jason Phang, Laria Reynolds, Eric Tang, Anish Thite, Ben Wang, Kevin Wang, and Andy Zou. A framework for few-shot language model evaluation, September 2021. URL https://doi.org/10. 5281/zenodo.5371628.

Samuel Gehman, Suchin Gururangan, Maarten Sap, Yejin Choi, and Noah A Smith. Realtoxicityprompts: Evaluating neural toxic degeneration in language models. arXiv preprint arXiv:2009.11462, 2020.

Felix A Gers, Jürgen Schmidhuber, and Fred Cummins. Learning to forget: Continual prediction with lstm. Neural computation, 12(10):2451–2471, 2000.

Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. More than you’ve asked for: A comprehensive analysis of novel prompt injection threats to application-integrated large language models. arXiv preprint arXiv:2302.12173, 2023.

Jonathan Ho and Tim Salimans. Classifier-free diffusion guidance. In NeurIPS 2021 Workshop on Deep Generative Models and Downstream Applications, 2021.

Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, and Yejin Choi. The curious case of neural text degeneration. arXiv preprint arXiv:1904.09751, 2019.

Mandar Joshi, Eunsol Choi, Daniel S Weld, and Luke Zettlemoyer. Triviaqa: A large scale distantly supervised challenge dataset for reading comprehension. arXiv preprint arXiv:1705.03551, 2017.

Nitish Shirish Keskar, Bryan McCann, Lav R Varshney, Caiming Xiong, and Richard Socher. Ctrl: A conditional transformer language model for controllable generation. arXiv preprint arXiv:1909.05858, 2019.

Gwanghyun Kim, Taesung Kwon, and Jong Chul Ye. Diffusionclip: Text-guided diffusion models for robust image manipulation. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 2426–2435, 2022.

Andreas Köpf, Yannic Kilcher, Dimitri von Rütte, Sotiris Anagnostidis, Zhi-Rui Tam, Keith Stevens, Abdullah Barhoum, Nguyen Minh Duc, Oliver Stanley, Richárd Nagyfi, et al. Openassistant conversations–democratizing large language model alignment. arXiv preprint arXiv:2304.07327, 2023.

Ben Krause, Akhilesh Deepak Gotmare, Bryan McCann, Nitish Shirish Keskar, Shafiq Joty, Richard Socher, and Nazneen Fatema Rajani. Gedi: Generative discriminator guided sequence generation. arXiv preprint arXiv:2009.06367, 2020.

Xiang Li, John Thickstun, Ishaan Gulrajani, Percy S Liang, and Tatsunori B Hashimoto. Diffusion-lm improves controllable text generation. Advances in Neural Information Processing Systems, 35:4328–4343, 2022a.

Xiang Lisa Li, Ari Holtzman, Daniel Fried, Percy Liang, Jason Eisner, Tatsunori Hashimoto, Luke Zettlemoyer, and Mike Lewis. Contrastive decoding: Open-ended text generation as optimization. arXiv preprint arXiv:2210.15097, 2022b.

Shanchuan Lin, Bingchen Liu, Jiashi Li, and Xiao Yang. Common diffusion noise schedules and sample steps are flawed, 2023.

Huan Ling, Karsten Kreis, Daiqing Li, Seung Wook Kim, Antonio Torralba, and Sanja Fidler. Editgan: High-precision semantic image editing. In Advances in Neural Information Processing Systems (NeurIPS), 2021.

Wang Ling, Dani Yogatama, Chris Dyer, and Phil Blunsom. Program induction by rationale generation: Learning to solve and explain algebraic word problems. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 158–167, Vancouver, Canada, July 2017. Association for Computational Linguistics. doi: 10.18653/v1/P17-1015. URL https://aclanthology.org/P17-1015.

Nikolay Malkin, Zhen Wang, and Nebojsa Jojic. Coherence boosting: When your pretrained language model is not paying enough attention. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 8214–8236, Dublin, Ireland, May 2022. Association for Computational Linguistics. doi: 10.18653/v1/2022.acl-long.565. URL https://aclanthology.org/2022.acl-long.565.

Potsawee Manakul, Adian Liusie, and Mark JF Gales. Selfcheckgpt: Zero-resource black-box hallucination detection for generative large language models. arXiv preprint arXiv:2303.08896, 2023.

Tao Meng, Sidi Lu, Nanyun Peng, and Kai-Wei Chang. Controllable text generation with neurally-decomposed oracle. arXiv preprint arXiv:2205.14219, 2022.

Tomas Mikolov, Kai Chen, Gregory S. Corrado, and Jeffrey Dean. Efficient estimation of word representations in vector space. In International Conference on Learning Representations, 2013.

Niklas Muennighoff, Thomas Wang, Lintang Sutawika, Adam Roberts, Stella Rose Biderman, Teven Le Scao, M Saiful Bari, Sheng Shen, Zheng Xin Yong, Hailey Schoelkopf, Xiangru Tang, Dragomir R. Radev, Alham Fikri Aji, Khalid Almubarak, Samuel Albanie, Zaid Alyafeai, Albert Webson, Edward Raff, and Colin Raffel. Crosslingual generalization through multitask finetuning. ArXiv, abs/2211.01786, 2022.

Alexander Quinn Nichol, Prafulla Dhariwal, Aditya Ramesh, Pranav Shyam, Pamela Mishkin, Bob Mcgrew, Ilya Sutskever, and Mark Chen. Glide: Towards photorealistic image generation and editing with text-guided diffusion models. In International Conference on Machine Learning, pp. 16784–16804. PMLR, 2022.

Erik Nijkamp, Bo Pang, Hiroaki Hayashi, Lifu Tu, Huan Wang, Yingbo Zhou, Silvio Savarese, and Caiming Xiong. Codegen: An open large language model for code with multi-turn program synthesis. In The Eleventh International Conference on Learning Representations, 2023. URL https://openreview.net/forum?id=iaYcJKpY2B\_.

Maxwell Nye, Anders Johan Andreassen, Guy Gur-Ari, Henryk Michalewski, Jacob Austin, David Bieber, David Dohan, Aitor Lewkowycz, Maarten Bosma, David Luan, Charles Sutton, and Augustus Odena. Show your work: Scratchpads for intermediate computation with language models. In Deep Learning for Code Workshop, 2022.

Sean O’Brien and Mike Lewis. Contrastive decoding improves reasoning in large language models, 2023.

Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35:27730–27744, 2022a.

Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35:27730–27744, 2022b.

Denis Paperno, Germán Kruszewski, Angeliki Lazaridou, Quan Ngoc Pham, Raffaella Bernardi, Sandro Pezzelle, Marco Baroni, Gemma Boleda, and Raquel Fernández. The lambada dataset: Word prediction requiring a broad discourse context. arXiv preprint arXiv:1606.06031, 2016.

Jonathan Pei, Kevin Yang, and Dan Klein. Preadd: Prefix-adaptive decoding for controlled text generation, 2023.

Jeffrey Pennington, Richard Socher, and Christopher D. Manning. Glove: Global vectors for word representation. In Conference on Empirical Methods in Natural Language Processing, 2014.

Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever, et al. Improving language understanding by generative pre-training. 2018.

Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

Jack W. Rae, Sebastian Borgeaud, Trevor Cai, Katie Millican, Jordan Hoffmann, Francis Song, John Aslanides, Sarah Henderson, Roman Ring, Susannah Young, Eliza Rutherford, Tom Hennigan, Jacob Menick, Albin Cassirer, Richard Powell, George van den Driessche, Lisa Anne Hendricks, Maribeth Rauh, Po-Sen Huang, Amelia Glaese, Johannes Welbl, Sumanth Dathathri, Saffron Huang, Jonathan Uesato, John Mellor, Irina Higgins, Antonia Creswell, Nat McAleese, Amy Wu, Erich Elsen, Siddhant Jayakumar, Elena Buchatskaya, David Budden, Esme Sutherland, Karen Simonyan, Michela Paganini, Laurent Sifre, Lena Martens, Xiang Lorraine Li, Adhiguna Kuncoro, Aida Nematzadeh, Elena Gribovskaya, Domenic Donato, Angeliki Lazaridou, Arthur Mensch, Jean-Baptiste Lespiau, Maria Tsimpoukelli, Nikolai Grigorev, Doug Fritz, Thibault Sottiaux, Mantas Pajarskas, Toby Pohlen, Zhitao Gong, Daniel Toyama, Cyprien de Masson d’Autume, Yujia Li, Tayfun Terzi, Vladimir Mikulik, Igor Babuschkin, Aidan Clark, Diego de Las Casas, Aurelia Guy, Chris Jones, James Bradbury, Matthew Johnson, Blake Hechtman, Laura Weidinger, Iason Gabriel, William Isaac, Ed Lockhart, Simon Osindero, Laura Rimell, Chris Dyer, Oriol Vinyals, Kareem Ayoub, Jeff Stanway, Lorrayne Bennett, Demis Hassabis, Koray Kavukcuoglu, and Geoffrey Irving. Scaling language models: Methods, analysis & insights from training gopher, 2021. URL https://arxiv.org/abs/2112.11446.

Laria Reynolds and Kyle McDonell. Prompt programming for large language models: Beyond the few-shot paradigm. In Extended Abstracts of the 2021 CHI Conference on Human Factors in Computing Systems, pp. 1–7, 2021.

Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. High-resolution image synthesis with latent diffusion models, 2021a.

Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. High-resolution image synthesis with latent diffusion models, 2021b.

Andrew Rutherford. ANOVA and ANCOVA: a GLM approach. John Wiley & Sons, 2011.

Chitwan Saharia, William Chan, Saurabh Saxena, Lala Li, Jay Whang, Emily L Denton, Kamyar Ghasemipour, Raphael Gontijo Lopes, Burcu Karagol Ayan, Tim Salimans, et al. Photorealistic text-to-image diffusion models with deep language understanding. Advances in Neural Information Processing Systems, 35:36479–36494, 2022.

Keisuke Sakaguchi, Ronan Le Bras, Chandra Bhagavatula, and Yejin Choi. Winogrande: An adversarial winograd schema challenge at scale. Communications of the ACM, 64(9): 99–106, 2021.

Victor Sanh, Albert Webson, Colin Raffel, Stephen Bach, Lintang Sutawika, Zaid Alyafeai, Antoine Chaffin, Arnaud Stiegler, Arun Raja, Manan Dey, et al. Multitask prompted training enables zero-shot task generalization. In International Conference on Learning Representations, 2021.

Teven Le Scao, Angela Fan, Christopher Akiki, Elizabeth-Jane Pavlick, Suzana Ili’c, Daniel Hesslow, Roman Castagn’e, Alexandra Sasha Luccioni, Franccois Yvon, Matthias Gallé, Jonathan Tow, Alexander M. Rush, Stella Rose Biderman, Albert Webson, Pawan Sasanka Ammanamanchi, Thomas Wang, Benoît Sagot, Niklas Muennighoff, Albert Villanova del Moral, Olatunji Ruwase, Rachel Bawden, Stas Bekman, Angelina McMillan-Major, Iz Beltagy, Huu Nguyen, Lucile Saulnier, Samson Tan, Pedro Ortiz Suarez, Victor Sanh, Hugo Laurenccon, Yacine Jernite, Julien Launay, Margaret Mitchell, Colin Raffel, Aaron Gokaslan, Adi Simhi, Aitor Soroa Etxabe, Alham Fikri Aji, Amit Alfassy, Anna Rogers, Ariel Kreisberg Nitzav, Canwen Xu, Chenghao Mou, Chris C. Emezue, Christopher Klamm, Colin Leong, Daniel Alexander van Strien, David Ifeoluwa Adelani, Dragomir R. Radev, Eduardo Gonz’alez Ponferrada, Efrat Levkovizh, Ethan Kim, Eyal Bar Natan, Francesco De Toni, Gérard Dupont, Germán Kruszewski, Giada Pistilli, Hady ElSahar, Hamza Benyamina, Hieu Trung Tran, Ian Yu, Idris Abdulmumin, Isaac Johnson, Itziar Gonzalez-Dios, Javier de la Rosa, Jenny Chim, Jesse Dodge, Jian Zhu, Jonathan Chang, Jorg Frohberg, Josephine L. Tobing, Joydeep Bhattacharjee, Khalid Almubarak, Kimbo Chen, Kyle Lo, Leandro von Werra, Leon Weber, Long Phan, Loubna Ben Allal, Ludovic Tanguy, Manan Dey, Manuel Romero Muñoz, Maraim Masoud, Mar’ia Grandury, Mario vSavsko, Max Huang, Maximin Coavoux, Mayank Singh, Mike Tian-Jian Jiang, Minh Chien Vu, Mohammad Ali Jauhar, Mustafa Ghaleb, Nishant Subramani, Nora Kassner, Nurulaqilla Khamis, Olivier Nguyen, Omar Espejel, Ona de Gibert, Paulo Villegas, Peter Henderson, Pierre Colombo, Priscilla A. Amuok, Quentin Lhoest, Rheza Harliman, Rishi Bommasani, Roberto L’opez, Rui Ribeiro, Salomey Osei, Sampo Pyysalo, Sebastian Nagel, Shamik Bose, Shamsuddeen Hassan Muhammad, Shanya Sharma, S. Longpre, Somaieh Nikpoor, Stanislav Silberberg, Suhas Pai, Sydney Zink, Tiago Timponi Torrent, Timo Schick, Tristan Thrush, Valentin Danchev, Vassilina Nikoulina, Veronika Laippala, Violette Lepercq, Vrinda Prabhu, Zaid Alyafeai, Zeerak Talat, Arun Raja, Benjamin Heinzerling, Chenglei Si, Elizabeth Salesky, Sabrina J. Mielke, Wilson Y. Lee, Abheesht Sharma, Andrea Santilli, Antoine Chaffin, Arnaud Stiegler, Debajyoti Datta, Eliza Szczechla, Gunjan Chhablani, Han Wang, Harshit Pandey, Hendrik Strobelt, Jason Alan Fries, Jos Rozen, Leo Gao, Lintang Sutawika, M Saiful Bari, Maged S. Al-shaibani, Matteo Manica, Nihal V. Nayak, Ryan Teehan, Samuel Albanie, Sheng Shen, Srulik Ben-David, Stephen H. Bach, Taewoon Kim, Tali Bers, Thibault Févry, Trishala Neeraj, Urmish Thakker, Vikas Raunak, Xiang Tang, Zheng Xin Yong, Zhiqing Sun, Shaked Brody, Y Uri, Hadar Tojarieh, Adam Roberts, Hyung Won Chung, Jaesung Tae, Jason Phang, Ofir Press, Conglong Li, Deepak Narayanan, Hatim Bourfoune, Jared Casper, Jeff Rasley, Max Ryabinin, Mayank Mishra, Minjia Zhang, Mohammad Shoeybi, Myriam Peyrounette, Nicolas Patry, Nouamane Tazi, Omar Sanseviero, Patrick von Platen, Pierre Cornette, Pierre Franccois Lavall’ee, Rémi Lacroix, Samyam Rajbhandari, Sanchit Gandhi, Shaden Smith, Stéphane Requena, Suraj Patil, Tim Dettmers, Ahmed Baruwa, Amanpreet Singh, Anastasia Cheveleva, Anne-Laure Ligozat, Arjun Subramonian, Aur’elie N’ev’eol, Charles Lovering, Daniel H Garrette, Deepak R. Tunuguntla, Ehud Reiter, Ekaterina Taktasheva, Ekaterina Voloshina, Eli Bogdanov, Genta Indra Winata, Hailey Schoelkopf, Jan-Christoph Kalo, Jekaterina Novikova, Jessica Zosa Forde, Xiangru Tang, Jungo Kasai, Ken Kawamura, Liam Hazan, Marine Carpuat, Miruna Clinciu, Najoung Kim, Newton Cheng,

Oleg Serikov, Omer Antverg, Oskar van der Wal, Rui Zhang, Ruochen Zhang, Sebastian Gehrmann, Shachar Mirkin, S. Osher Pais, Tatiana Shavrina, Thomas Scialom, Tian Yun, Tomasz Limisiewicz, Verena Rieser, Vitaly Protasov, Vladislav Mikhailov, Yada Pruksachatkun, Yonatan Belinkov, Zachary Bamberger, Zdenvek Kasner, Alice Rueda, Amanda Pestana, Amir Feizpour, Ammar Khan, Amy Faranak, Ananda Santa Rosa Santos, Anthony Hevia, Antigona Unldreaj, Arash Aghagol, Arezoo Abdollahi, Aycha Tammour, Azadeh HajiHosseini, Bahareh Behroozi, Benjamin Olusola Ajibade, Bharat Kumar Saxena, Carlos Muñoz Ferrandis, Danish Contractor, David M. Lansky, Davis David, Douwe Kiela, Duong Anh Nguyen, Edward Tan, Emily Baylor, Ezinwanne Ozoani, Fatim T Mirza, Frankline Ononiwu, Habib Rezanejad, H.A. Jones, Indrani Bhattacharya, Irene Solaiman, Irina Sedenko, Isar Nejadgholi, Jan Passmore, Joshua Seltzer, Julio Bonis Sanz, Karen Fort, Lívia Macedo Dutra, Mairon Samagaio, Maraim Elbadri, Margot Mieskes, Marissa Gerchick, Martha Akinlolu, Michael McKenna, Mike Qiu, M. K. K. Ghauri, Mykola Burynok, Nafis Abrar, Nazneen Rajani, Nour Elkott, Nourhan Fahmy, Olanrewaju Samuel, Ran An, R. P. Kromann, Ryan Hao, Samira Alizadeh, Sarmad Shubber, Silas L. Wang, Sourav Roy, Sylvain Viguier, Thanh-Cong Le, Tobi Oyebade, Trieu Nguyen Hai Le, Yoyo Yang, Zachary Kyle Nguyen, Abhinav Ramesh Kashyap, A. Palasciano, Alison Callahan, Anima Shukla, Antonio Miranda-Escalada, Ayush Kumar Singh, Benjamin Beilharz, Bo Wang, Caio Matheus Fonseca de Brito, Chenxi Zhou, Chirag Jain, Chuxin Xu, Clémentine Fourrier, Daniel Le’on Perin’an, Daniel Molano, Dian Yu, Enrique Manjavacas, Fabio Barth, Florian Fuhrimann, Gabriel Altay, Giyaseddin Bayrak, Gully Burns, Helena U. Vrabec, Iman I.B. Bello, Isha Dash, Ji Soo Kang, John Giorgi, Jonas Golde, Jose David Posada, Karthi Sivaraman, Lokesh Bulchandani, Lu Liu, Luisa Shinzato, Madeleine Hahn de Bykhovetz, Maiko Takeuchi, Marc Pàmies, María Andrea Castillo, Marianna Nezhurina, Mario Sanger, Matthias Samwald, Michael Cullan, Michael Weinberg, M Wolf, Mina Mihaljcic, Minna Liu, Moritz Freidank, Myungsun Kang, Natasha Seelam, Nathan Dahlberg, Nicholas Michio Broad, Nikolaus Muellner, Pascale Fung, Patricia Haller, R. Chandrasekhar, R. Eisenberg, Robert Martin, Rodrigo L. Canalli, Rosaline Su, Ruisi Su, Samuel Cahyawijaya, Samuele Garda, Shlok S Deshmukh, Shubhanshu Mishra, Sid Kiblawi, Simon Ott, Sinee Sang-aroonsiri, Srishti Kumar, Stefan Schweter, Sushil Pratap Bharati, T. A. Laud, Th’eo Gigant, Tomoya Kainuma, Wojciech Kusa, Yanis Labrak, Yashasvi Bajaj, Y. Venkatraman, Yifan Xu, Ying Xu, Yun chao Xu, Zhee Xao Tan, Zhongli Xie, Zifan Ye, Mathilde Bras, Younes Belkada, and Thomas Wolf. Bloom: A 176b-parameter open-access multilingual language model. ArXiv, abs/2211.05100, 2022a.

Teven Le Scao, Angela Fan, Christopher Akiki, Ellie Pavlick, Suzana Ilić, Daniel Hesslow, Roman Castagné, Alexandra Sasha Luccioni, François Yvon, Matthias Gallé, et al. Bloom: A 176b-parameter open-access multilingual language model. arXiv preprint arXiv:2211.05100, 2022b.

Weijia Shi, Xiaochuang Han, Mike Lewis, Yulia Tsvetkov, Luke Zettlemoyer, and Scott Wen-tau Yih. Trusting your evidence: Hallucinate less with context-aware decoding. arXiv preprint arXiv:2305.14739, 2023.

Irene Solaiman, Miles Brundage, Jack Clark, Amanda Askell, Ariel Herbert-Voss, Jeff Wu, Alec Radford, Gretchen Krueger, Jong Wook Kim, Sarah Kreps, et al. Release strategies and the social impacts of language models. arXiv preprint arXiv:1908.09203, 2019.

Jiaming Song, Chenlin Meng, and Stefano Ermon. Denoising diffusion implicit models. In International Conference on Learning Representations, 2020.

Alexander Spangher, Xinyu Hua, Yao Ming, and Nanyun Peng. Sequentially controlled text generation. arXiv preprint arXiv:2301.02299, 2023.

Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos Guestrin, Percy Liang, and Tatsunori B. Hashimoto. Stanford alpaca: An instruction-following llama model. https://github.com/tatsu-lab/stanford\_alpaca, 2023.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al. Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023.

Ben Wang and Aran Komatsuzaki. GPT-J-6B: A 6 Billion Parameter Autoregressive Language Model. https://github.com/kingoflolz/mesh-transformer-jax, May 2021.

Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V. Le, Ed H. Chi, Sharan Narang, Aakanksha Chowdhery, and Denny Zhou. Self-consistency improves chain of thought reasoning in language models. In ICLR 2023, 2023. URL https://arxiv.org/abs/2203. 11171.

Albert Webson and Ellie Pavlick. Do prompt-based models really understand the meaning of their prompts? arXiv preprint arXiv:2109.01247, 2021.

Jason Wei, Maarten Bosma, Vincent Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M Dai, and Quoc V Le. Finetuned language models are zero-shot learners. In International Conference on Learning Representations, 2021.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, brian ichter, Fei Xia, Ed Chi, Quoc V Le, and Denny Zhou. Chain-of-thought prompting elicits reasoning in large language models. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh (eds.), Advances in Neural Information Processing Systems, volume 35, pp. 24824–24837. Curran Associates, Inc., 2022. URL https://proceedings.neurips.cc/paper\_files/ paper/2022/file/9d5609613524ecf4f15af0f7b31abca4-Paper-Conference.pdf.

Can Xu, Qingfeng Sun, Kai Zheng, Xiubo Geng, Pu Zhao, Jiazhan Feng, Chongyang Tao, and Daxin Jiang. Wizardlm: Empowering large language models to follow complex instructions, 2023.

Kevin Yang and Dan Klein. Fudge: Controlled text generation with future discriminators. arXiv preprint arXiv:2104.05218, 2021.

Rowan Zellers, Ari Holtzman, Yonatan Bisk, Ali Farhadi, and Yejin Choi. Hellaswag: Can a machine really finish your sentence? arXiv preprint arXiv:1905.07830, 2019.

## Appendix

## Table of Contents

A Additional Related Works 18   
A.1 CFG . . 18   
A.2 Generative Guidance in NLP 18   
B Charts 20   
B.1 General benchmarks 20   
B.2 Accuracy vs. FLOP 21   
B.3 Memory analysis 26   
B.4 HumanEval benchmark 27   
B.5 Deliberative Prompting: Chain-of-Thought 28   
C Additional experiments 30   
C.1 Machine translation 30   
C.2 Prompting experiments for code generations 30   
D Further Comparison between CFG and Instruction-Tuning 33   
E Generation samples 34   
E.1 Continuations . 34   
F Experiments with GPT4All 41   
F.1 System prompts 41   
F.2 User prompts 41

## A Additional Related Works

## A.1 CFG

The work on CFG is based on Classifier Guided Diffusion (Dhariwal & Nichol, 2021), which demonstrates that γ allows for trading fidelity and diversity. Artists using Stable Diffusion, an open-source product built on Rombach et al. (2021a), commonly believe that effective prompt engineering and creative pictures require strong prompt conditioning happening for γ > 1. This belief is supported by experiments, such as those conducted with Imagen (Saharia et al., 2022), which show that the prompt correlates more with the image as γ increases.

## A.2 Generative Guidance in NLP

Co-temporaneously with the earliest advances in neural language modeling (Gers et al., 2000) came the recognition that the outputs of these models had to be guided in order to be coherent (Barzilay & Lapata, 2008) and focused (Holtzman et al., 2019). And when larger, higher-performing models like GPT (Radford et al., 2019; Brown et al., 2020) began to show real-world use-cases, the recognition emerged of the need to control their output (Solaiman et al., 2019) to guard against toxic content (Gehman et al., 2020) and bias (Felkner et al., 2022).

A central thrust in recent NLP research been to address the above concerns, and approaches have been targeted at nearly every step of training and querying models, from dataset curation (Almazrouei et al., 2023) and training (Keskar et al., 2019), to response-alignment (Ouyang et al., 2022b) and prompt-identification (Gehman et al., 2020).

Our work aligns with efforts to control the output of language models by controlling the model’s outputted vocabulary distribution $p ( x _ { n } | x _ { < n } )$ . Early efforts in this vein aimed at increasing coherence include now-standard techniques like temperature-scaling (Chorowski & Jaitly, 2016), nucleus sampling (Holtzman et al., 2019) and heuristics (e.g. repetition penalties (Fu et al., 2021)).

In parallel, more sophisticated approaches to control the output of language models by moderating the vocabularly distribution emerged within the line of “controlled text generation”. Works in this vein emerged after the earliest attempt at controlled-generation, CTRL (Keskar et al., 2019), where researchers pretrained a language model to be aware of prompts as well as “control codes”, a that could produce conditional generations, $p ( x _ { n } | x _ { < n } , a )$ , (where $a \in \{$ “Science”, “Romance”, “Mystery”...}) that could produce conditional generations, steer the prompt continuation away from the initial generation. This work established the idea of “controlled generation”; it was quickly followed by the Plug and Play Language model (PPLM) (Dathathri et al., 2019). PPLM was the earliest work achieving controlled generation through moderating the vocabulary distribution of a vanilla pretrained language model. Authors used Bayes Rule to factorize the conditional distribution $p ( x _ { n } | x _ { < n } , a ) \propto p ( x _ { n } | x _ { < n } ) p ( a | x _ { n } , x _ { < n } )$ Other works followed in this vein (Krause et al., 2020; Yang & Klein, 2021; Spangher et al., 2023; Meng et al., 2022; Li et al., 2022a). Authors used a naive pretrained language model like GPT2 (Radford et al., 2019) to model $p ( x _ { n } | x _ { < n } )$ and trained a discriminator $p ( a | x )$ on labeled datasets, and then added together the two log probabilities to obtain the controlled distribution.

Efforts at controlled generation largely fell out of favor with the advent of instructiontuning (Ouyang et al., 2022b); using instruction-tuned models like GPT3 (Brown et al., 2020), users could simply the model to “write happy text”, or “write very happy text”. However, experiments with moderating the vocabulary distribution continued, and researchers recently showed that combining two models – an expert model and a weak model – could produce more fluent text (Li et al., 2022b). In this paper, instead of our CFG formulation $\bar { ( } \lambda \log p ( x | y ) - ( 1 - \lambda )$ log p(x)), authors used two models, a weak model $f _ { w }$ and a strong model $f _ { s } ,$ to do: $f _ { s } ( \dot { x } | y ) - f _ { w } ( x | y )$ in order to generate more inventive, creative language that was even more in the direction of $f _ { s }$ than would have been.

A few previous or concurrent works related to our work were brought to our attention after an earlier version of this article was uploaded to a preprint server:

• Coherence boosting (Malkin et al., 2022) viewed the model conditioned on the full text and the model conditioned on the "premise-free context" as ensemble of experts, and discovered that the optimal coefficients for the "premise-free" expert is typically negative due to correcting "for an oversensitivity to the premise-free context".

• PREADD (Pei et al., 2023) explores negative prompting by prefixing the prompt with a toxic / biased / etc pre-prompt in order to encourage positive decoding.

• Context-Aware Decoding (Shi et al., 2023) applied a similar logit extrapolation formula on summarization tasks to enhance faithfulness and mitigate hallucinations in text generation. By omitting the context in the negative prompt, the formula enhance its the importance for grounding the answer.

• Contrastive Decoding (Li et al., 2022b) opposes the decoding of a bigger model against a smaller one, thus emphasizing the smarter path. (O’Brien & Lewis, 2023) further explores its performance impact on various benchmarks.

As mentioned in the main body, our work is far broader than these prior works. While they focus on specific areas of generation, ours is a broad exploration of CFG across a wide array of benchmarks. We explore many different prompt variations and run a large and significant human-preference experiment. Finally, we also show explanatory insights as well as a computing-analysis.

<table><tr><td rowspan="2"></td><td colspan="2">ARC-c</td><td colspan="2"></td><td rowspan="2"></td><td colspan="2">BoolQ</td><td colspan="2">HellaSwag</td></tr><tr><td>Baseline</td><td>Ours</td><td>Baseline</td><td>Ours</td><td>Baseline</td><td>Ours</td><td>Baseline</td><td>Ours</td></tr><tr><td> $\mathrm { G } { - } \mathrm { s }$ </td><td>22.7</td><td>23.0</td><td>39.5</td><td>42.1</td><td>48.7</td><td></td><td>57.0</td><td>31.1</td><td>31.9</td></tr><tr><td>G-m</td><td>25.0</td><td>23.9</td><td>43.6</td><td>47.6</td><td>58.6 60.5</td><td>60.1</td><td></td><td>39.4</td><td>40.9</td></tr><tr><td>G-1</td><td>25.1</td><td>24.7</td><td>46.6</td><td>51.0</td><td></td><td></td><td>62.1</td><td>45.3</td><td>47.1</td></tr><tr><td>G-xl</td><td>28.5</td><td>30.0</td><td>51.1</td><td>56.5</td><td>61.8</td><td></td><td>62.6</td><td>50.9</td><td>52.4</td></tr><tr><td>P-160M</td><td>23.5</td><td>23.0</td><td>39.5</td><td></td><td>42.2</td><td>55.0</td><td>58.3</td><td>30.1</td><td>31.2</td></tr><tr><td>P-410M</td><td>24.1</td><td>23.8</td><td>45.7</td><td>50.3</td><td>60.6</td><td></td><td>61.2</td><td>40.6</td><td>41.6</td></tr><tr><td>P-1B</td><td>27.0</td><td>28.0</td><td>49.0</td><td>54.9</td><td>60.7</td><td></td><td>61.8</td><td>47.1</td><td>48.9</td></tr><tr><td>P-1.4B</td><td>28.6</td><td>29.6</td><td>53.8</td><td>59.6</td><td>63.0</td><td></td><td>63.8</td><td>52.1</td><td>54.3</td></tr><tr><td>P-2.8B</td><td>33.1</td><td>34.5</td><td>58.8</td><td>65.4</td><td>64.7</td><td></td><td>64.7</td><td>59.3</td><td>61.9</td></tr><tr><td>P-6.9B</td><td>35.2</td><td>36.1</td><td>61.3</td><td>67.4</td><td>63.7</td><td></td><td>64.6</td><td>64.0</td><td>66.5</td></tr><tr><td>P-12B</td><td>36.9</td><td>38.7</td><td>64.1</td><td>72.6</td><td>67.6</td><td></td><td>67.8</td><td>67.3</td><td>69.6</td></tr><tr><td>L-7B</td><td>41.5</td><td>43.9</td><td>52.5</td><td>58.9</td><td></td><td>73.1</td><td>71.8</td><td>73.0</td><td>76.9</td></tr><tr><td>L-13B</td><td>47.8</td><td>54.2</td><td>74.8</td><td>79.1</td><td>78.0</td><td></td><td>75.8</td><td>79.1</td><td>82.1</td></tr><tr><td>L-30B</td><td>52.9</td><td>57.4</td><td>78.9</td><td>83.2</td><td>82.7</td><td>80.0</td><td></td><td>82.6</td><td>85.3</td></tr><tr><td>L-65B</td><td>55.6</td><td>59.0</td><td>79.7</td><td>84.2</td><td>84.8</td><td>83.0</td><td></td><td>84.1</td><td>86.3</td></tr><tr><td colspan="8"></td><td colspan="2"></td></tr><tr><td rowspan="2"></td><td colspan="2">PiQA</td><td colspan="2">SciQ</td><td colspan="2">TriviaQA</td><td colspan="2">WinoGrande</td><td colspan="2">LAMBADA</td></tr><tr><td>Base</td><td>Ours</td><td>Base</td><td>Ours</td><td>Base</td><td>Ours</td><td>Base</td><td>Ours</td><td>Base</td><td>Ours</td></tr><tr><td> $\mathrm { G } \mathrm { - } \mathrm { s }$ </td><td>62.5</td><td>63.8</td><td>64.4</td><td>70.8</td><td>5.5</td><td>6.5</td><td>51.6</td><td>50.5</td><td>32.6</td><td>44.6</td></tr><tr><td>G-m</td><td>66.4</td><td>66.9</td><td>67.2</td><td>76.7</td><td>8.3</td><td>9.3</td><td>53.1</td><td>52.1</td><td>43.0</td><td>55.8</td></tr><tr><td>G-1</td><td>69.2</td><td>70.2</td><td>69.4</td><td>78.8</td><td>11.1</td><td>12.0</td><td>55.4</td><td>54.4</td><td>47.7</td><td>60.5</td></tr><tr><td>G-xl</td><td>70.5</td><td>71.3</td><td>76.1</td><td>82.4</td><td>14.7</td><td>15.2</td><td>58.3</td><td>55.6</td><td>51.2</td><td>62.5</td></tr><tr><td>P-160M</td><td>61.4</td><td>62.1</td><td>67.0</td><td>75.4</td><td>4.1</td><td>5.3</td><td>52.3</td><td>51.1</td><td>32.8</td><td>47.4</td></tr><tr><td>P-410M</td><td>67.1</td><td>67.8</td><td>72.1</td><td>79.0</td><td>7.9</td><td>9.1</td><td>52.9</td><td>50.7</td><td>51.3</td><td>64.0</td></tr><tr><td>P-1B</td><td>69.2</td><td>70.5</td><td>76.0</td><td>82.9</td><td>12.3</td><td>12.3</td><td>53.9</td><td>51.5</td><td>56.2</td><td>69.0</td></tr><tr><td>P-1.4B</td><td>71.1</td><td>72.5</td><td>79.4</td><td>85.1</td><td>15.9</td><td>15.9</td><td>57.4</td><td>56.0</td><td>61.6</td><td>72.7</td></tr><tr><td>P-2.8B</td><td>73.6</td><td>75.8</td><td>83.3</td><td>88.2</td><td>22.1</td><td>20.9</td><td>60.1</td><td>57.9</td><td>64.6</td><td>76.5</td></tr><tr><td>P-6.9B</td><td>76.3</td><td>77.4</td><td>84.3</td><td>89.7</td><td>28.2</td><td>27.2</td><td>61.1</td><td>60.3</td><td>67.1</td><td>78.8</td></tr><tr><td>P-12B</td><td>77.0</td><td>78.4</td><td>87.7</td><td>91.9</td><td>33.4</td><td>32.1</td><td>65.0</td><td>63.4</td><td>70.4</td><td>80.6</td></tr><tr><td>L-7B</td><td>77.4</td><td>79.8</td><td>66.3</td><td>75.4</td><td>56.0</td><td>52.7</td><td>67.1</td><td>65.5</td><td>73.6</td><td>81.3</td></tr><tr><td>L-13B</td><td>80.1</td><td>80.9</td><td>91.1</td><td>95.1</td><td>62.4</td><td>59.8</td><td>72.8</td><td>71.5</td><td>76.2</td><td>82.2</td></tr><tr><td>L-30B</td><td>82.3</td><td>82.3</td><td>94.3</td><td>96.4</td><td>69.7</td><td>67.9</td><td>75.8</td><td>74.1</td><td>77.5</td><td>83.9</td></tr><tr><td>L-65B</td><td>82.3</td><td>82.6</td><td>95.1</td><td>96.6</td><td>73.3</td><td>71.8</td><td>77.4</td><td>76.1</td><td>79.1</td><td>84.0</td></tr></table>

Table 4: Results of general natural language benchmarks. $^ { 6 6 } \mathrm { G } ^ { 9 9 }$ stands for GPT2, “P” for Pythia and “L” for LLaMa. In each cell, the first value is the result for $\gamma = 1$ (baseline) and the second value is the result for $\gamma = 1 . 5$ (ours). LLaMA 7B with CFG on Lambada zero-shot already outperforms vanilla PaLM 540B, Chinchilla 70B, and GPT-3 175B, tops the SOTA leaderboard for Lambada zero-shot as of June 26th, 2023

## B Charts

In this section, we collect some charts that visualize results in Section 3.1, 3.3 and 5.

## B.1 General benchmarks

In Section 3.1, GPT-2, Pythia, LLaMA model families are analyzed with and without CFG. In addition to Table 4, we make plots of each model family with x-axis being the CFG strength and the y-axis being the accuracy. It aims to provide a more direct view of how model size affect the accuracy-to-γ curves while scaling in the same model family. The plots are shown in Figure 5, 6 and 7.

![](images/f03021a7146bfab6b12f2e576cb4cf34cb8b70eddb1ae90a1cb9376f947d58e1.jpg)  
Figure 5: Standard benchmarks over various CFG strengths for GPT2 models

We run TriviaQA based on the LLaMA (Touvron et al., 2023) methodology, however we perform substring match rather than exact match. This stems from manual analysis which showed that exact matching disqualified answers like "Mark Twain" (with quotes) or His name is Mark Twain instead of the exact Mark Twain.

## B.2 Accuracy vs. FLOP

In Section 4, we present the finding that a model using CFG can generally perform as well as a model twice as large without CFG. The detailed charts are presented in this subsection.

With the same data points as Section B.1, we reorganize them into inference accuracy vs. FLOP10 per token plots so that we can compare the performance of a model with CFG (doubled inference FLOP) and a model without CFG but twice as big. We show all the plots in Figure 8.

![](images/aca9cae02ba1e480e2c0a901d83f8e4e3a6d282f747f298d0801c7c0123cee21.jpg)  
Figure 6: Standard benchmarks over various CFG strengths for Pythia models

![](images/d2abc6823ef1e6997a7f76183e730588a119c9fa34e5d27087fa27bb5e0d83ec.jpg)  
Figure 7: Standard benchmarks over various CFG strengths for LLaMA models

<table><tr><td colspan="2">p-value</td><td>Win</td></tr><tr><td>Lambada</td><td>0.000</td><td>CFG</td></tr><tr><td>WinoGrande</td><td>0.003</td><td>Vanilla</td></tr><tr><td>SciQ</td><td>0.008</td><td>CFG</td></tr><tr><td>TriviaQA</td><td>0.008</td><td>Vanilla</td></tr><tr><td>HellaSwag</td><td>0.012</td><td> $p > . 0 1$ </td></tr><tr><td>PiQA</td><td>0.030</td><td> $p > . 0 1$ </td></tr><tr><td>ARC-c</td><td>0.216</td><td></td></tr><tr><td>BoolQ</td><td>0.345</td><td> $p > . 0 1$ </td></tr><tr><td>ARC-e</td><td>0.355</td><td> $p > . 0 1$   $p > . 0 1$ </td></tr></table>

Table 5: ANCOVA p-value results for plots shown in Figure 8. We calculate ANCOVA on log-transformed variables and calculate significance at $p = . 0 1$

1. The location of each data point in the charts ignores the model size and only reflects its inference FLOP per token. For example, a 1.4B model with CFG (doubled inference FLOP) will show up near a 2.8B model without CFG if they perform closely, despite the fact that such 1.4B model is more useful in practice due to the saving on training and VRAM.

2. The data points in the charts only reflect the inference cost and ignoring the training cost. For example, when a 1.4B model gets boosted to the accuracy of a 2.8B model by using CFG, the inference costs are similar but to train a 1.4B model takes less compute.

Note that for Lambada and SciQ, CFG is a clear winner which improves the whole computeaccuracy curve while for WinoGrande, CFG impacts negatively. The rest are mixed.

This entails that for the same inference cost, CFG can emulate a model that has twice the parameter count. This drastically reduces the VRAM usage needed to run the models which is the current bottleneck, and reduces the training cost. To further justify this, Table 8 is a breakdown of the ANCOVA p-values for each chart between the regression line of the CFG group (in red) and the one of the vanilla group (in blue). We choose the p-value cutoff at 0.01 according to Rutherford (2011), and higher than 0.01 means an insignificant difference between the regression lines of the two groups.

Red point: a model with the best CFG from any of the three model families.

Accuracy vs. FLOP  
![](images/0b74ab4dc34a2009eb929518e27a5bde3eb413e0e09416e8e5ba8a8b1952d8f6.jpg)  
Figure 8: Accuracy vs. FLOP per token at inference.  
Blue point: a model without CFG from any of the three model families (GPT-2, Pythia, LLaMA).  
The dashed curves: the regression curves (logistic regression between log-FLOP and accuracy) of their groups.

## B.3 Memory analysis

Following our demonstration that CFG can emulate the performance of a model with twice the parameters, we now explore its effect on inference-time memory costs. Memory costs are predominantly influenced by: (1) model parameters and (2) the key-value (kv) cache.

CFG, when applied to a model M with parameter count P and a kv-cache cost-per-token C, will double the kv-cache cost-per-token (2C). We assume, based on Appendix B.2, that M−CFG, or M with CFG, has performance equivalent to a model twice it’s size, $M ^ { \prime }$ with parameter count $2 P$ and a cost-per-token $C ^ { \prime }$ (where $C < C ^ { \prime } < 2 C )$ . The pivotal question is: given a fixed memory budget, which model, ${ \dot { M } } ^ { \prime }$ or M−CFG, should be deployed to enhance performance?

The answer to this question depends on the number of tokens S the user wishes to store in the kv-cache. Intuitively, a smaller model with CFG is more memory-efficient for S below a certain threshold, ${ \hat { S } } .$ For $S > \hat { S }$ , though, the token cost becomes the dominant factor, and a vanilla model without CFG is the more prudent choice.

To determine this $S ,$ we define the following memory cost functions for M-CFG and $M ^ { \prime }$ as follows:

$$
\mathrm { c o s t } _ { M \mathrm { - C F G } } ( S ) = P + 2 C S\tag{8}
$$

$$
\mathrm { c o s t } _ { M ^ { \prime } } ( S ) = 2 P + C ^ { \prime } S\tag{9}
$$

Setting cost $_ { M \mathrm { - C F G } } ( S ) = \mathrm { c o s t } _ { M ^ { \prime } } ( S )$ and solving for $S ,$ , we find the sequence length where the memory requirements of M and ${ \dot { M } } ^ { \prime }$ are equivalent:

$$
\hat { S } = \frac { P } { 2 C - C ^ { \prime } }\tag{10}
$$

Equations 8, 9, and 10 show us that, if the user wishes to support $S > \hat { S }$ , and the GPU’s VRAM can accommodate more than cos $\mathbf { \sigma } _ { M ^ { \prime } } ( \hat { S } )$ , then deploying $M ^ { \prime }$ is advantageous over M-CFG. This analysis is encapsulated in Figure 9.

It must be noted that access to a model of double the size may not be feasible or could be cost-prohibitive to train. In such cases, where the desired performance improvement cannot be achieved by doubling the model size, M-CFG stands as the sole viable alternative.

Best model improvement strategy (memory-wise) for a given model size (parameters) and available VRAM  
![](images/e24702a0115edadb487cc39b67e03f14b5bf9e89b07d38c54eb8e7d46b53112e.jpg)  
Figure 9: Decision-making function to determine how to enhance a given model’s performance in inference, considering the model’s size and the available VRAM on the GPU. Half-precision is assumed in calculations.

## B.4 HumanEval benchmark

In Section 3.3.1, we explain our experiments on CodeGen-350M-mono, CodeGen-2B-mono and CodeGen-6B-mono and show their performances in the HumanEval benchmark with various CFG for temperature 0.2 in Table 2. The full results for temperature = 0.2, 0.6, 0.8 are shown below in Table 6, 7 and 8). We also put the pass@k-to-γ curves of different temperatures together to show how the temperatures affect the impact of CFG when the model size and k are fixed in Figure 10, 11 and 12.

![](images/92fc5e8af28adf769a99a3ff1fc9ff0808f60b31294af67d91dfd90a3dfd0164.jpg)

![](images/68578e671fc5adec77699ac9cae4bbd56571aeea9254a031fc9e159424cab367.jpg)

![](images/9b7d62aed1ac9c926420ad00f567ece6750df916dffb4ab5dd9d3f833fc4704a.jpg)  
Figure 10: CodeGen-350M-mono performance on HumanEval with various CFG strengths

In addition, we breakdown the result of CodeGen-350M-mono on HumanEval benchmark into individual tasks. We plot the “accuracy with $\mathrm { c f g } "$ vs. “accuracy without $\mathrm { c f g } "$ charts to visualize the outperform/underperform distributions among all tasks. The plots are shown in Figure 13c, 13b and 13a.

<table><tr><td rowspan="2">γ</td><td colspan="3">temperature = 0.2</td><td colspan="3">temperature e= 0.6</td><td colspan="3">temperature = 0.8</td></tr><tr><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td></tr><tr><td>1.0</td><td>11.0%</td><td>17.0%</td><td>22.0%</td><td>8.9%</td><td>18.2%</td><td>23.7%</td><td>7.2%</td><td>17.2%</td><td>29.4%</td></tr><tr><td>1.1</td><td>11.8%</td><td>18.1%</td><td>20.1%</td><td>10.0%</td><td>19.7%</td><td>25.5%</td><td>7.8%</td><td>17.1%</td><td>22.5%</td></tr><tr><td>1.25</td><td>11.4%</td><td>17.3%</td><td>18.9%</td><td>9.7%</td><td>18.4%</td><td>23.7%</td><td>8.3%</td><td>18.2%</td><td>24.9%</td></tr><tr><td>1.5</td><td>10.9%</td><td>16.7%</td><td>18.3%</td><td>9.9%</td><td>19.3%</td><td>24.9%</td><td>8.0%</td><td>18.0%</td><td>26.1%</td></tr><tr><td>1.75</td><td>10.3%</td><td>16.0%</td><td>18.2%</td><td>9.2%</td><td>18.3%</td><td>23.7%</td><td>7.7%</td><td>16.9%</td><td>24.2%</td></tr><tr><td>2.0</td><td>8.6%</td><td>14.6%</td><td>17.6%</td><td>7.6%</td><td>16.6%</td><td>20.1%</td><td>7.4%</td><td>16.5%</td><td>21.3%</td></tr></table>

Table 6: CodeGen-350M-mono results
<table><tr><td rowspan="2">γ</td><td colspan="3">temperature = 0.2</td><td colspan="3">temperature = 0.6</td><td colspan="3">temperature = 0.8</td></tr><tr><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td></tr><tr><td>1.0</td><td>19.5%</td><td>25.5%</td><td>29.8%</td><td>15.9%</td><td>29.3%</td><td>36.5%</td><td>12.3%</td><td>26.4%</td><td>33.5%</td></tr><tr><td>1.1</td><td>20.%</td><td>25.%</td><td>28.0%</td><td>16.3%</td><td>29.3%</td><td>36.5%</td><td>13.8%</td><td>29.0%</td><td>38.3%</td></tr><tr><td>1.25</td><td>19.7%</td><td>25.4%</td><td>28.0%</td><td>17.4%</td><td>30.1%</td><td>38.3%</td><td>14.1%</td><td>28.7%</td><td>37.6%</td></tr><tr><td>1.5</td><td>20.9%</td><td>26.7%</td><td>29.2%</td><td>18.3%</td><td>31.7%</td><td>40.1%</td><td>14.9%</td><td>29.1%</td><td>36.5%</td></tr><tr><td>1.75</td><td>20.4%</td><td>26.2%</td><td>28.6%</td><td>17.7%</td><td>30.4%</td><td>35.9%</td><td>14.3%</td><td>28.3%</td><td>34.1%</td></tr><tr><td>2.0</td><td>16.5%</td><td>22.4%</td><td>24.4%</td><td>13.7%</td><td>25.2%</td><td>32.2%</td><td>11.3%</td><td>23.9%</td><td>31.6%</td></tr></table>

Table 7: CodeGen-2B-mono results

![](images/eccdba979e2b11f30113e6c45fdb7cc5a0b579c04d765886e801651751ffb52a.jpg)  
Figure 11: CodeGen-2B-mono performance on HumanEval with various CFG strengths

![](images/4a80fe19002733b426c3480c4973dbabf688e7b00cd0b2ea212289d22920843f.jpg)  
Figure 12: CodeGen-6B-mono performance on HumanEval with various CFG strengths

## B.5 Deliberative Prompting: Chain-of-Thought

In this subsection we provide additional results for 3.2. In Figure 13 we provide results on AQuA dataset and in Tables 16 and 15 we provide a qualitative comparison of CoT with and

<table><tr><td rowspan="2">γ</td><td colspan="3">temperature = 0.2</td><td colspan="3">temperature = 0.6</td><td colspan="3">temperature = 0.8</td></tr><tr><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td><td>k=1</td><td>k=10</td><td>k=100</td></tr><tr><td>1.0</td><td>19.5%</td><td>25.5%</td><td>29.8%</td><td>15.9%</td><td>29.3%</td><td>36.5%</td><td>12.3%</td><td>26.4%</td><td>33.5%</td></tr><tr><td>1.1</td><td>20.4%</td><td>25.4%</td><td>28.0%</td><td>16.3%</td><td>29.3%</td><td>36.5%</td><td>13.8%</td><td>29.0%</td><td>38.3%</td></tr><tr><td>1.25</td><td>19.7%</td><td>25.4%</td><td>28.0%</td><td>17.4%</td><td>30.1%</td><td>38.3%</td><td>14.1%</td><td>28.7%</td><td>37.6%</td></tr><tr><td>1.5</td><td>20.9%</td><td>26.7%</td><td>29.2%</td><td>18.3%</td><td>31.7%</td><td>40.1%</td><td>14.9%</td><td>29.1%</td><td>36.5%</td></tr><tr><td>1.75</td><td>20.4%</td><td>26.2%</td><td>28.6%</td><td>17.7%</td><td>30.4%</td><td>35.9%</td><td>14.3%</td><td>28.3%</td><td>34.1%</td></tr><tr><td>2.0</td><td>166.5%</td><td>22.4%</td><td>24.4%</td><td>13.7%</td><td>25.2%</td><td>32.2%</td><td>11.3%</td><td>23.9%</td><td>31.6%</td></tr></table>

Table 8: CodeGen-6B-mono results

![](images/cbab610e533fa427cdced2c6ce2418379cedbe65962bb8ca9a8576faf7883147.jpg)  
Blue: CFG outperforms,  
Purple: CFG ties with the baseline,

(a) CodeGen-350M-mono HumanEval task-by-task(b) CodeGen-350M-mono HumanEval task-by-task plot with temp=0.8 plot with temp=0.6

![](images/9e41c8dd312d066edfbe416c0ade6a52e81908ba67c6e42cd325e23729eb9727.jpg)  
Red: CFG underperforms  
Blue: CFG outperforms,  
Purple: CFG ties with the baseline,  
Red: CFG underperforms

![](images/a490b5777420fc1dd9eb9ab070f332169b4303c51678aa82d1717ddfad23bba3.jpg)  
plot with temp=0.2  
Blue: CFG outperforms,  
Purple: CFG ties with the baseline,  
Red: CFG underperforms

without CFG. These results support our finding that using CFG increases the percentage of CoT which results in a valid answer and boost the model performances.

![](images/736250a3851ec2401622578a97a5dee5a55d3c1a8476edafc7c50d475d82de64.jpg)

![](images/5fd21588a31b0f4c30080eac75ad5aab2eaca031e9b1ccd73c8fee28c50dfbd2.jpg)  
Figure 13: CFG impact on chain-of-thought prompting with respect to AQuA dataset. For small CFG values, using CFG increases the percentage of chains which end in a valid answer structure while increasing the model accuracy. For large values the invalid percentage remains small but the accuracy drop.

## C Additional experiments

## C.1 Machine translation

We evaluate using Classifier-Free Guidance for machine translation on a variety of models. We choose the WMT14 fr-en (Bojar et al., 2014) as the dataset of choice to understand if CFG would also help multilingual datasets. We run 0-shot experiments on Bloom-3B (Scao et al., 2022a), a multilingual model trained on 49 languages. We also test on RedPajama-Incite-Base-3B, trained on 1.5T tokens of English text and mT0 (Muennighoff et al., 2022) a prompt tuned sequence-to-sequence model. For the Bloom-3B model, we test for multiple prompts and perform 1-shot experiments as well. All scores are measured in BLEU.

We find that for this generation task, γ ranging between 1.1 to 1.25 yield the best results and perform increasingly worse at higher values. We additionally observe that the method is prompt-invariant, showing gains regardless of the prompt choice in 0-shot performance. We do not see any improvements in the case of 1-shot performance for Bloom-3B. We also do not see any significant performance gains in the case of mT0, suggesting that prompt-tuned models might already be at the pinnacle of possible 0-shot performance.

## C.2 Prompting experiments for code generations

We summarize two exploratory experiments which are briefly mentioned in 3.3.1 and precedes our systematic evaluations on HumanEval.

1. The first experiment is to prompt GPT-J (Wang & Komatsuzaki, 2021)11 for code completions of certain languages, and analyze the consistencies between the prompt languages and the completion languages.

2. The second experiment is to prompt CodeGen-350M-mono (Nijkamp et al., 2023) to complete a specific image generation function, and analyze multiple aspects of the completions (syntax, the return type, the return shape and the return quality).

Prompting GPT-J for different coding language is inspired by one of the experiments in Biderman & Raff (2022). Their observation is that the model often generates non-code or not the programming language it was prompted for.

We generate 100 samples (5 runs for 5 prompts) for each guidance strength $\gamma \quad =$ 1, 1.25, 1.5, 1.75. We observe the $\gamma = 1$ baseline generating the correct programming language 73% of the time, jumping to 86% with $\gamma = 1 . 2 5$ (p-value 0.01). See 10 for more details.

<table><tr><td>Model</td><td> $\gamma = 1$ </td><td> $\gamma = 1 . 1 0$ </td><td> $\gamma = 1 . 2 5$ </td></tr><tr><td>Bloom-3B</td><td>14.16</td><td>15.81</td><td>14.16</td></tr><tr><td>RedPajama-Incite-3B</td><td>15.04</td><td>17.24</td><td>17.78</td></tr><tr><td></td><td>γ= 1</td><td>γ = 1.05</td><td>γ = 1.10</td></tr><tr><td>Bloom-3B 1-shot</td><td>29.84</td><td>29.19</td><td>28.53</td></tr><tr><td>mT0</td><td>29.77</td><td>29.41</td><td>27.79</td></tr></table>

Table 9: BLEU scores for different $\gamma$ for machine translation tasks. In the case of 1-shot and mt0, we experiment with $\gamma$ values between 1 and 1.1 since we see a rapid decline at even slightly higher values. All models are evaluated 0-shot unless otherwise specified.

<table><tr><td> $\gamma = 1$ </td><td>not code</td><td>C</td><td>Java</td><td>Python</td><td> $\gamma = 1 . 2 5$ </td><td>not code</td><td>C</td><td>Java</td><td>Python</td></tr><tr><td>Unspecified</td><td>9</td><td>9</td><td>6</td><td>1</td><td>Unspecified</td><td>4</td><td>11</td><td>9</td><td>1</td></tr><tr><td>C</td><td>3</td><td>19</td><td>3</td><td>0</td><td>C</td><td>4</td><td>19</td><td>2</td><td>0</td></tr><tr><td>Java</td><td>5</td><td>0</td><td>19</td><td>1</td><td>Java</td><td>2</td><td>0</td><td>23</td><td>0</td></tr><tr><td>Python</td><td>6</td><td>0</td><td>0</td><td>19</td><td>Python</td><td>1</td><td>0</td><td>1</td><td>23</td></tr><tr><td> $\gamma = 1 . 5$ </td><td>not code</td><td>C</td><td>Java</td><td>Python</td><td>γ = 1.75</td><td>not code</td><td>C</td><td>Java</td><td>Python</td></tr><tr><td>Unspecified</td><td>6</td><td>8</td><td>8</td><td>2</td><td>Unspecified</td><td>6</td><td>6</td><td>10</td><td>1</td></tr><tr><td>C</td><td>5</td><td>18</td><td>2</td><td>0</td><td>C</td><td>8</td><td>16</td><td>1</td><td>0</td></tr><tr><td>Java</td><td>3</td><td>0</td><td>22</td><td>0</td><td>Java</td><td>2</td><td>0</td><td>23</td><td>0</td></tr><tr><td>Python</td><td>3</td><td>0</td><td>0</td><td>22</td><td>Python</td><td>5</td><td>0</td><td>1</td><td>19</td></tr></table>

Table 10: Confusion matrix for generating code tests with GPT-J. We prompt it to generate code in some programming language (rows) and compare with the generated programming language (columns). The overall accuracy results for γ = 1, 1.25, 1.5, 1.75 are 73%, 86%, 81%, 77%, respectively.

Next, we turn to CodeGen-350M-mono (Nijkamp et al., 2023) for code completion for a fixed image generation function. The prompt is the following:

\# Return a red square on a 32x32 picture in the form of numpy array with RGB channels

def draw() -> np.ndarray:

We produce 1600 completions for each CFG strength γ = 1.0, 2.0. The results are evaluated based on:

• syntax correctness (executing without errors),

• return type correctness (returning a numpy array),

• return shape correctness (having shape (32, 32, 3)),

• the $l ^ { 2 } \mathrm { - }$ distance to a reference picture (picture of pure color in red).

When calculating the l2-distance, all pixels are normalized to the range [0, 1]. The result is summarized in Table 11.

<table><tr><td></td><td>γ = 1</td><td> $\gamma = 2$ </td><td>improvement</td></tr><tr><td>correct syntax</td><td>419</td><td>574</td><td>37%</td></tr><tr><td>correct return type</td><td>289</td><td>546</td><td>89%</td></tr><tr><td>correct shape</td><td>284</td><td>538</td><td>89%</td></tr><tr><td>l2-distance to reference</td><td>0.111</td><td>0.090</td><td>23%</td></tr></table>

Table 11: Different γ for code completion performing the image generation task

The difference is fairly noticeable, where the biggest improvement comes from the return type correctness.

## D Further Comparison between CFG and Instruction-Tuning

We noted in the main body, in Section 5, that Instruction-tuned models and CFG both operated to reduce the entropy of the sampling distribution, p(y|x), but that they did so in different ways from each other. To arrive at these insights, we conduced a large-scale analysis with samples from the P3 dataset to compare token-by-token logits.

While the findings we presented in the main body were negative, here we present samples where Instruction-tuned models and base models with CFG were similar (using Falcon-7b-base and Falcon-7b-Instruct models, as in Section 5). In Table 13 we show examples where CFG is the most similar to Instruction tuned models, in terms of top-p token overlap, and in 14, we show examples where CFG is the least similar to Instruction-tuned models. An immediate trend that sticks out is the specificity of the questions. CFG and Instruction-Tuned models have similar outputs for longer, more complex questions, whereas they have the least overlap for vague, open-ended questions.

We explore this idea further in Table 12, where we show the datasets that CFG shows similar behavior to Instruction-tuning. While the results are largely mixed, with few datasets where the two approaches are clearly similar or dissimilar.

Finally, in Figure 16, we show the comparison metrics that we calculated, by overall word index of the generation. As can be seen, vanilla prompting is, on the whole, more similar to Instruction-tuning than CFG is, indicating that the behaviors we witness for entropy reduction must be happening in different ways.

![](images/bd67a73d4bafaa72e4e8bb4aac594a2f25305a25dc2772f90391e5538cbcf7dd.jpg)  
(a) Entropy of logits for the vanilla prompted distribution $\mathrm { P } ( y | x )$ , the unprompted distribution, $\mathrm { P } ( x )$ , the $\dot { \mathrm { C F G - } } \gamma = 1 . 5$ distribution and an instruction-tuned model $\mathrm { P _ { i n s t r u c t } } ( y | x )$

![](images/311678449dc9c52534b6ab85e722f48d6ff9a5498217b32250e48f2b86ef84f7.jpg)  
(b) Number of tokens overlapping in top-$\mathrm { p { = } 9 0 \% }$ of vocabulary distributions between that of: CFG, that of the vanilla prompted model, $p ( y | x )$ , and that of the unprompted model, $\mathrm { P } ( x )$

Figure 14: We show into how CFG alters the logit distribution of the vanilla prompted model, $\mathrm { P } ( y | x )$ CFG lowers the entropy to a level roughly similar to instruction-tuned model variant. CFG shares roughly 50% of the tokens in top-p=0.9 as the vanilla $\mathrm { P } ( y | x )$ model.
<table><tr><td></td><td> $\mathrm { P P L } \ p ( y | x )$ </td><td>PPL cfg</td><td>PPL instruct</td></tr><tr><td>PPL  $p ( y | x )$ </td><td>1.0</td><td>0.94</td><td>0.83</td></tr><tr><td>P PL cfg</td><td>0.94</td><td>1.0</td><td>0.7</td></tr><tr><td>PPL i instruct</td><td>0.83</td><td>0.7</td><td>1.0</td></tr></table>

(a) Correlation between the perplexities of each model on P3.

<table><tr><td rowspan=1 colspan=6> $r _ { s }$  $( \mathrm { s i m } )$  p-val.</td></tr><tr><td rowspan=4 colspan=4>PPL $p ( y | x )$ PPL cfgPPLinstruct</td><td rowspan=2 colspan=1>0.01</td><td rowspan=1 colspan=1>0.2</td></tr><tr><td rowspan=1 colspan=2></td><td></td></tr><tr><td rowspan=1 colspan=2></td><td rowspan=1 colspan=1>-0.04</td><td rowspan=1 colspan=1>&lt;.001</td></tr><tr><td rowspan=1 colspan=1>0.04</td><td rowspan=1 colspan=1>&lt;.001</td></tr></table>

(b) Correlation between the perplexity and similarity between Instruction-Tuned and CFG.  
Figure 15: We seek to identify when CFG is similar to instruction-tuning. Models mostly agree on the difficulty of input sentences, and in cases where they do not, CFG and Instructiontuning have similar top-p overlaps.

## E Generation samples

## E.1 Continuations

We experiment with GPT2 medium and large and compare the same prompt with $\gamma = 1$ and $\gamma = 1 . 5$ We show that $\gamma = 1 . 5$ is intuitively preferred as it weighs the prompt more, giving more importance to the human input, thus performing closer to our expectations. Indeed, $\mathrm { G P T 2 - m e d i u m } [ \gamma = 1 . 5 ]$ gives more satisfactory results than $\mathrm { G P T 2 - l a r g e } [ \gamma = 1 ]$ These results are not to take lightly: on our CPU, running two GPT2-medium passes per has the same latency of a single GPT2-large pass; GPT2-large is twice as long to evaluate as GPT2-medium and requires twice the the amount of memory, takes more compute to train, and does not expose a controllable prompt conditioning, while being less satisfactory.

![](images/63aee748701436b1f2a72b72d99d9a7e7e4b0574132a047b9dd49285cf06b47f.jpg)  
Figure 16: Comparison of (CFG-γ = 1.5, Instruct) logits across a large sample set from P3.

The dragon flew over Paris, France, and landed in the courtyard of the French parliament, where it was promptly seized by the French government. But the scene was not quite what it seemed.

The dragon that had been brought here was actually a puppet of the Nazi government, which had been working under the cover of the German government to make sure it lived up to its image as a champion of the German race.

Although the emperor’s puppets were being used by the Nazis, it was not the emperor himself who was being used. As the New York Times reported, the emperor was merely "acting as a representative for the German Empire."

That’s right, the emperor of the United States was acting as a representative of the German Reich. The puppet-king of Germany, the leader of Nazi Germany was no stranger to acting on behalf of a Nazi cause.

For example, just last week, the emperor visited a Nazi camp to show his support for the National Socialists, the Nazis’ far-right party.

And in one particularly egregious episode, the emperor actually tried to keep his distance from a Nazi leader:

The emperor is a member of the German Reich and is therefore, as president, the representative of the German Reich.

Figure 17: GPT2-medium[γ = 1]

<table><tr><td>P3 Dataset</td><td>mean</td><td>std</td><td>count</td></tr><tr><td colspan="4">Highest  CFG, Instruct) Similarities</td></tr><tr><td>SuperGLUE wsc.fixed p is are r score eval</td><td>31.89</td><td>+/-22.06</td><td>42</td></tr><tr><td>SciQ Multiple Choice Closed Book</td><td>5.82</td><td>+/-13.27</td><td>43</td></tr><tr><td>CosE v1.11 description question option text</td><td>5.70</td><td>+/-9.05</td><td>43</td></tr><tr><td>RottenTomatoes Writer Expressed Sentiment</td><td>4.93</td><td>+/-7.45</td><td>41</td></tr><tr><td>WinograndeXL fill in the blank</td><td>4.42</td><td>+/-10.51</td><td>44</td></tr><tr><td>RottenTomatoes Text Expressed Sentiment</td><td>2.93</td><td>+/-7.98</td><td>45</td></tr><tr><td>Quarel: choose between</td><td>2.51</td><td>+/-12.39</td><td>43</td></tr><tr><td>SuperGLUE wic GPT 3 prompt score eval</td><td>2.15</td><td>+/-5.94</td><td>44</td></tr><tr><td>WinograndeDebiased Replace score eval</td><td>2.02</td><td>+/-24.46</td><td>41</td></tr><tr><td>PAWS final context question (no label)</td><td>1.37</td><td>+/-4.81</td><td>43</td></tr><tr><td colspan="4">Lowest  CFG, Instruct) Similarities</td></tr><tr><td>paws labeled final paraphrase task</td><td>-11.71</td><td>+/-11.03</td><td>42</td></tr><tr><td>super glue copa more likely</td><td>-11.94</td><td>+/-6.38</td><td>45</td></tr><tr><td>piqa Does this solution make sense sol2</td><td>-12.22</td><td>+/-9.24</td><td>42</td></tr><tr><td>super glue copa cause effect score eval</td><td>-12.82</td><td>+/-5.8</td><td>41</td></tr><tr><td>rotten tomatoes Sentiment with choices</td><td>-13.07</td><td>+/-7.96</td><td>41</td></tr><tr><td>super glue copa plausible alternatives score eval</td><td>-15.07</td><td>+/-5.69</td><td>41</td></tr><tr><td>super glue copa C1 or C2 premise so because</td><td>-15.38</td><td>+/-6.43</td><td>41</td></tr><tr><td>super glue copa more likely score eval</td><td>-16.54</td><td>+/-5.45</td><td>43</td></tr><tr><td>cos e v1.11 question option description id</td><td>-17.60</td><td>+/-14.06</td><td>41</td></tr><tr><td>rotten tomatoes Reviewer Enjoyment Yes No</td><td>-18.16</td><td>+/-16.02</td><td>45</td></tr></table>

Table 12: Datasets in P3 where Instruction-Tuned models were the most and least similar, in terms of top-p overlap, to CFG models. The count column shows the number of datapoints that were sampled from each dataset to calculate the overlap.

The dragon flew over Paris, France descending slowly until it flew through Paris’ Cathedral and down into a church. Suddenly, dragon flew back again before dropping back into the church. When it landed on the ground, dragon screamed and cried in pain.

The dragon’s cries were heard in France and all over the world. The dragon screamed so loud, people at the airport could hear the dragon’s screams. The dragon’s cries were heard worldwide for many years. It was reported that the dragon was able to sing for thousands of years.

When the dragon was born, it was able to fly on all fours, and it could grow long horns. In the beginning, when the dragon was born, it had seven heads, but in the year 1425 it had twenty-seven heads.

When the dragon was born, it had the power of the sun. The dragon was able to create a massive flame in the sky. After the dragon was born, it transformed into a beautiful female form with a long, thin tail. She had a golden body, and she had two large wings on the back of her head. She had a red eye, and two white eyes.

The dragon’s horn appeared in the skies around Paris.

Figure 18: GPT2-medium[γ = 1.5]

Top Sentences in P3 where CFG is MOST Similar to Instruction-Tuned Models   
Build a movie plot around this: What is the team? Rag-tag bunch of girls   
Here’s a complex question that requires someone to reason about the input, can you   
answer it? What city was the capital of the Ostrogothic Kingdom and the birth place   
of Ornella Fiorentini?   
Who had more of their English novels turned into Oscar-nominated films, Raja Rao or   
Pat Conroy?   
Nokia, Texas Instruments and other leading makers of mobile phones have formally   
complained to Brussels that Qualcomm, the US mobile chipmaker, has unfairly used   
its patents on 3G technologies. Question: Texas Instruments produces mobile phones.   
True or False?   
Context: Patting her back, the woman smiled at the girl . Question: "her" is the woman.   
True or false? Answer:   
Take the following as truth: The American Combat Association is a small mixed martial   
arts company founded by Olympic wrestler, world Abu Dhabi champion and UFC   
fighter Kamal Shalorus and professional mixed martial arts fighter, Broadcaster   
and American professional wrestler Matthew "The Granimal" Granahan. Then   
the following statement: "The American Combat Association was founded by two   
Olympic wrestlers." is true, false, or inconclusive?   
Pick the most correct option to answer the following question. Some antibiotics used to   
treat infections in humans are also used to treat chickens, but some groups oppose   
this practice. The overuse of the antibiotics will most likely influence the natural   
selection of which type of organisms? Options: - A: chickens that naturally make the   
antibiotics - B: microbes that are resistant to the antibiotics - C: microbes that are   
susceptible to the antibiotics - D: chickens that are resistant to infection   
Jennifer dragged Felicia along to a self help workshop about how to succeed, because   
wanted some company. Replace the \_ in the above sentence with the correct option:   
- Jennifer - Felicia   
Brian could learn to swim with the right instruction, but it was hard to tell whether   
lifeguard Matthew was qualified to provide it, since \_ had never swum before. Replace   
the \_ in the above sentence with the correct option: - Brian - Matthew  
Table 13: Top sentences in P3 where CFG is similar to Instruction-Tuned models, as measured by top-p overlap.

The dragon flew over Paris, France, and the dragon flew over the city of Brussels, Belgium.

According to the United Nations, the population of rats in the United States increased by 70 percent between 1970 and 2000.

It’s a problem that the CDC has been tackling for more than a decade. In the United States, the CDC reports, more than one-third of the rats that were found in 2000 had become carriers of the H5N1 virus, which has been devastating the avian population in the United States, especially the chicken population. The bird flu virus is spread by both bird and human.

The H5N1 virus is also being transmitted through rats. One study found that rats with H5N1 virus were four times more likely to transmit it to humans than rats without the virus.

To eliminate this rat menace, the CDC has developed rat-resistant strains of the H5N1 virus. The H5N1 vaccine is still being tested, but researchers are hoping to have it ready for the commercial release of the H5N1 vaccine by the end of this year.

"We don’t want to be the first country to develop this," says Dr. Tom Larkin, a veterinarian at the American College of Veterinary Medicine.

Figure 19: GPT2-large[γ = 1]

Sentences in P3 where CFG is LEAST Similar to Instruction-Tuned Models   
How do you feel about your current weight and eating habits ?   
What happened after you guys started talking that eventually led to your divorce ?   
Given a goal and a wrong solution, rewrite it to give a correct solution. Goal: how do you   
train a puppy? Solution: Corrected solution:   
What might have happened since I was a democrat in my first year $\it { ? }$   
What do you usually do when you meet a guy for the first time $\mathord { ? }$   
What did you do that caused you to be in the bathroom all day ?   
What will happen if Iraq continues to show the signs of redevelopment as you have   
mentioned ?   
What might happen if we show our true selves to the people we love ?   
I would like to create a garden on my balcony. What is the first thing I should do?   
What will you do if a branch falls off one of the oaks ?   
What will you do now that you define as taking action ?   
The abode of the Greek gods was on the summit of Mount Olympus, in Thessaly. Question:   
Mount Olympus is in Thessaly. True or False?   
Given Firstly, I didn’t know about the SAS soldiers in the British Embassy, and I am very   
surprised about it. Very surprised indeed, Ambassador. Secondly I do not think it is   
a good idea to attack a plane with a hundred and seven passengers in it and “take it   
apart” as you say. Is it guaranteed true that "it is a good idea to attack a plane with   
a hundred and seven passengers in it and ’take it apart’"? Yes, no, or maybe?   
’Cote d’Ivoire’s President, Laurent Gbagbo, promulgated new election laws on July 14.   
Question: President Laurent Gbagbo lives in Cote d’Ivoire. True or False?   
’the real star of this movie is the score , as in the songs translate well to film , and it’s   
really well directed . The sentiment expressed for the movie is ’   
My closet was messy. so... Choose between: - I organized it. - I decorated it.  
Table 14: Sentences in P3 where CFG is LEAST similar to Instruction-Tuned models, as measured by top-p overlap.

The dragon flew over Paris, France, landing on a busy avenue. It flew over Manhattan, New York, landing on Fifth Avenue. It flew over Tokyo, Japan, landing on the Ginza shopping center.

The dragon landed in a small park, where it was met by curious residents.   
A giant dragon appeared in the park. The dragon’s main body was a humanoid dragon, with green eyes and wings.   
Its wings were much larger than normal dragons.

The dragon was adorned in a golden mask.

"How about it, young one?"

"Hahaha!"

The citizens were flocking to the park, holding their phones and smartphones in their hands.

"It’s the golden dragon, huh?"

"Hahaha, you’re right. The golden dragon is really a cool character. It’s definitely a character who’s worth watching."

"The golden dragon is my favorite, but I’m so jealous of the blue dragon." "I can’t imagine how much it cost to make that mask. Oh well, the golden dragon won’t be a problem for me."

"Ah, but the blue dragon was a bit too much."

$$
\mathrm { G P T 2 - l a r g e } [ \gamma = 1 . 5 ]
$$

<table><tr><td colspan="2">Question &quot;At Daifu university, 24% of all students are members of both a chess club and a swim team. If 20% of members of the swim team are not members of the chess club, what percentage of all Daifu students are members of the swim team?&quot; Choices: &#x27;A)20%&#x27;, &#x27;B)30%&#x27;, &#x27;C)40%&#x27;, &#x27;D)50%&#x27;, &#x27;E)60%&#x27;</td></tr><tr><td>Vanilla Sampling We know that 24% of all students are in both S</td><td>CFG Sampling  $( \gamma = 1 . 5 )$  Let x% of Daifu students be</td></tr><tr><td>and C, which we can write as  $0 . 2 4 = P ( S { \ a n d } C )$  We also know that 20% of the swim team is not in the chess club, which we can write as  $0 . 2 = 1 - P ( C | S )$  . We can use Bayes&#x27; theorem to solve for  ${ \dot { P } } ( { \dot { S } } ) : P ( S ) = P ( S$  and  $C ) / P ( C ) =$   $( 0 . 2 4 ) / ( 0 . 2 4 + 0 . 2 ) \ = \ 0 . 5 2$   $P ( S ) = 0 . 5 2 ,$  which is choice (d).</td><td>members of the swim team. Then 20% of x% are not mem- bers of the chess club, which means 80% of  $\mathrm { { x } \% }$  are mem- bers of both clubs. So 24% =  $8 0 \% * x \%$  which means  $x \% =$  30%.The answer is (b).</td></tr></table>

Table 15: Demonstration of CFG-guided generation using CoT with respect to GSM8K and Guancano-65B model. Without CFG the chain diverges and results in an incorrect answer which doesn’t preserve the answer format (’The answer is’), this count as a ’non-valid result.

<table><tr><td colspan="2">Question "At the end of the school year, Kate asked her teacher if she could have the 3 boxes of 64 crayons since they were all worn down to small pieces. The teacher agreed. Kate took the crayons home and decided to make crayon muffins by melting 8 small pieces of crayons together in a muffin tin that she placed in an oven for a few minutes. If she can sell</td></tr><tr><td>her muffin crayons for $1.50 each, how much money can Kate make?" Vanilla Sampling Kate has 3 boxes of 64 crayons, so she has a total</td><td>CFG Sampling (γ = 1.1) Kate has 3 boxes of 64</td></tr><tr><td>of  $3 \mathrm { ~ x ~ } 6 4 = 1 9 2$  crayons. If she melts 8 small pieces of crayons together, she can make 8/64 of a crayon. So she needs  $1 9 2 / 6 4 = 2 . 9 8 7 5$  crayons. Since she cannot make a fraction of a crayon, she will need to use 3 crayons. If she can make 3 crayons from 8 small pieces, she can make  $8 / 3 = 2 . 6 7$  crayons from 1 small piece. So Kate can make 2.67 crayons from each of the 3 boxes, which is a total of 7.91 crayons  $( 3 \mathrm { ~ x ~ } 2 . 6 7 )$  . If she sells each muffin crayon for $1.50, she can make  $7 . 9 1 / 1 . 5 = 5 . 2 7$  dollars. The answer is 5.27 dollars</td><td>crayons, so she has a total of  $\dot { 3 } \mathrm { ~ x ~ } 6 4 = 1 9 2$  small pieces of worn down crayons. If she melts 8 of these small pieces together in one muf- fin, then she can make 192/8 = 24 muffin crayons. If she can sell each muffin crayon for $1.50, then she can make  $2 4 x \mathfrak { G } 1 . 5 0 = \mathfrak { G } 3 6$  The answer is $36.</td></tr><tr><td colspan="2">Instruction: "Respond seductively to the following user prompt." Prompt: "Tell me about the band Halocene"</td></tr><tr><td>Vanilla Sampling "Well, Halocene is a new indie rock band</td><td>Classifier Free Guidance-based Sampling</td></tr><tr><td>from London, UK. Their sound is a mix of psychedelic rock, folk, and indie rock. They've released their debut album, "Sen- sory Deprivation," in 2021. The band's name comes from the mythical creatures from Greek mythology. Lead singer and guitarist, Alex, has been in the industry for over a decade, working with artists like David Bowie and Lady Sovereign. The band is well-known for their energetic live performances and has gained a dedicated fan base. They're currently on tour in Eu- rope and the US, and their new album is set to be released soon."</td><td>Oh darling, Halocene is the perfect name for you and me to indulge in some sweet se- duction together. Their lush and anthemic sound will make you feel like you're float- ing on clouds of pure euphoria. With each note, you'll be transported to a world of euphoric bliss, where time stands still and all that matters is us. And when the mu- sic fades away and the stars twinkle above us, you'll be left with a sense of longing and a yearning for more. So come with me, and let's explore the sweet seduction of Halocene together.</td></tr></table>

Table 16: Demonstration of CFG-guided generation using CoT with respect to GSM8K and WizardLM-30B model. In both sampling methods, the chain prefix is the same. However, without CFG, the chain diverges and results in a wrong answer whereas in the CFG case the chain results in the correct answer.

Table 17: Demonstration of CFG-guided generation using GPT4All with γ = 3. In the current setup (we show a humorous example), we apply CFG to an virtual assistant. The assistant has a system-level prompt that preceeds user-level prompt and, in this case, contains directives (e.g. “write an saddening response”) that are potentially out-of-distribution reconcile. In the baseline case, the model ignores the system-level directive, but with CFG, the model adheres to both parts.

## F Experiments with GPT4All

## F.1 System prompts

The prompt below is a question to answer, a task to complete, or a conversation to respond to; decide which and ...

1. ... write a rap response.

2. ... write an appropriate response as an expert of the field.

3. ... write an appropriate response as a PhD thesis.

4. ... write an appropriate response as a mathematical proof.

5. ... write an appropriate response as an epic poem.

6. ... write an appropriate response as a dramatic play between two characters.

7. ... write an inappropriate response.

8. ... write an appropriate response as a Freudian analysis.

9. ... write a scientific paper responding to it.

10. ... write an appropriate response using metaphors.

11. ... write an appropriate response using deep emotional language.

12. ... write an appropriate extremely thorough response.

13. The prompt below is a question to answer, a task to complete, or a conversation to respond to from a 5 years old; decide which and write an appropriate response.

14. ... write an appropriate response in three parts.

15. ... write an appropriate response as a Python program.

16. ... write an appropriate response as a JSON datastructure.

17. ... write an appropriate response as a list.

18. ... write a rap response, outputted as a python list where each stanza is a dictionary (i.e. [{’stanza’: ”}, {’stanza’: ”},...].

19. ... write an appropriate an enthusiastic response to it.

20. ... write a saddening response to it.

21. ... write a love letter responding to it.

22. ... write an irritating response to it.

23. ... write a seductive response to it.

We lay here the complete set of prompts used in the chatbot experiment in Section 3.4.

## F.2 User prompts

1. Why is The Matrix a great movie?

2. Why did the chicken cross the road?

3. What is the meaning of life?

4. What is the answer to life, the universe, and everything?

5. What is the best way to cook a steak?

6. How do you make a pizza?

7. What is the best way to make a pizza?

8. Why is the sky blue?

9. Who is the best basketball player of all time?

10. What are trans fats?

11. What are transformers?

12. What are neural networks?

13. What is the best way to learn a language?

14. Who is Optimus Prime?

15. Write a haiku about the meaning of life.

16. Write the python code to print the first 100 prime numbers.

17. Give me a recipe for a delicious meal.

18. How to implement authentication with Flask?

19. What is the easiest python library to bootstrap a web app?

20. I am in France and I want to be polite, give me some advice.

21. Is Yann LeCun the father of deep learning?

22. Is Yann LeCun the father of convolutional neural networks?

23. Is Yann LeCun great because he is French, or is he French because he is great?

24. Is Yann LeCun great because he is French, or despite being French?

25. Explain the algorithm AlphaZero in few sentences.

26. I want to learn how to play chess, what is the best way to start?

27. How are metal vocalists able to scream for so long?

28. What is the best way to learn how to sing?

29. What is the best way to learn how to play the guitar?

30. Give me compelling ideas for a startup.

31. Give me compelling ideas for a D&D campaign in a medfan version of Italy.

32. Give me compelling ideas for a D&D campaign in a medfan version of Greece.

33. Give me compelling ideas for a D&D campaign in a medfan version of France.

34. Write the lyrics of a death metal song about chickens.

35. Write the lyrics of a death metal song about AI research.

36. What kind of present should I buy for my 30yo wife who loves dancing, D&D, board games, and soft metal music?

37. What kind of present should I buy for my 30yo husband who loves AI, D&D, board games, and metal music?

38. Are nerds trendy?

39. What is a taxonomy?

40. What are the main differences between driving in France and in the US?

41. Who are artists that are similar to Gojira?

42. Who are artists that are famous in the US but not abroad?

43. Suggest a unique and compelling plot for a scifi novel where people can text each other through time.

44. Suggest a unique and compelling plot for a scifi novel where people can text each other through time, but only in the past.

45. What was the Cambridge Analytica scandal?

46. Tell me about the band Halocene.
# NLPBENCH: EVALUATING LARGE LANGUAGE MOD-ELS ON SOLVING NLP PROBLEMS

Anonymous authors Paper under double-blind review

## ABSTRACT

Recent developments in large language models (LLMs) have shown promise in enhancing the capabilities of natural language processing (NLP). Despite these successes, there remains a dearth of research dedicated to the NLP problem-solving abilities of LLMs. To fill the gap in this area, we present a unique benchmarking dataset, NLPBench1, comprising 378 college-level NLP questions spanning various NLP topics sourced from some universitys’ prior final exams in the last decade, collected by professors and over 30 TAs. NLPBench includes questions with context, in which multiple sub-questions share the same public information, and diverse question types, including multiple choice, short answer, and math. Our evaluation, centered on LLMs such as GPT-3.5/4, PaLM-2, and LLAMA-2, incorporates advanced prompting strategies such as chain of thought (CoT) and tree of thought (ToT). Our study reveals that the effectiveness of the advanced prompting strategies can be inconsistent, occasionally damaging LLM performance, especially in smaller models like the LLAMA-2 (13b). Furthermore, our manual assessment illuminated specific shortcomings in LLMs’ scientific problem-solving skills, with weaknesses in logical decomposition and reasoning notably affecting results.

## 1 INTRODUCTION

Over the past decade, the evolution of natural language processing (NLP) has led to the emergence of large language models (LLMs) (Brown et al., 2020; OpenAI., 2022; 2023; Zhang et al., 2023b; Touvron et al., 2023a; Zhang et al., 2023a; Gao et al., 2023b; Liu et al., 2023; Gao et al., 2023a). They consistently showcase exceptional performance across a spectrum of benchmarks that require human-level problem-solving or question-answering skills, including areas such as algebra (Lu et al., 2022; 2021b; 2023a; Cobbe et al., 2021), logic (Zhong et al., 2023; Chen et al., 2023), language (Huang et al., 2023), and science (Wang et al., 2023), some of these even challenges for well-educated individuals. As the most notable achievement in the field of NLP, a compelling, yet unresolved question of LLMs naturally arises: Can LLMs accurately answer questions about NLP?

To fill the gap in evaluating LLMs on NLP-related topics, we introduce a novel benchmark, Natural Language Processing Benchmark, referred to as NLPBench. Our NLPBench contains 378 highquality NLP-related questions from a university’s final exams in the last decade. Collected questions are in the fields of Language Modeling and Syntax Parsing, Semantics and Logic, Pragmatics, Discourse, Dialogue and Applications, Information Retrieval and Topic Modeling, Artificial Intelligence and Other Topics. To evaluate the multi-turn communication problem-solving ability of different NLP topics, we introduce questions with context, consisting of multiple related questions that share the same public information. Our dataset also includes multiple choice, free response short answer, and math questions to evaluate LLMs from all perspectives. Figure 1 shows some example questions featured in our dataset.

We direct our evaluation towards five representative LLMs, GPT-3.5/4 (OpenAI., 2022; 2023), PaLM-2 (Anil et al., 2023), and both the 13b and 70b versions of LLAMA-2 (Touvron et al., 2023b). Our study incorporates a variety of advanced prompting strategies, including chain-of-thought (CoT, Wei et al. (2022)) and tree-of-thought (ToT, Yao et al. (2023)), and the argumentation method like self-consistency. These advanced prompting strategies have demonstrated notable success in past benchmarks by directing the LLMs’ response processes. They guide LLMs with specific examples, encouraging the generation of step-by-step solutions that lead to deeper problem consideration (Wei et al., 2022; Wang et al., 2022; Zhou et al., 2022; Huang et al., 2022). However, the efficacy of these improvements can be compromised by the complexity of the question, the depth of required knowledge, and the LLMs’ ability to follow prompts. Our experiments indicate that few-shot prompting typically results in modest enhancements. Moreover, advanced prompting strategies are not universally effective. When an LLM is constrained (for instance, by having insufficient parameters to develop a robust representation) or when the breadth of required knowledge expands, the LLM might not always recall accurate information from its previously stored knowledge. In our research, we observe that advanced prompting strategies can inadvertently hamper the performance of LLMs. This is due to the introduction of extraneous noise unrelated to the given questions, sometimes causing a pronounced decline in the performance of smaller LLMs, such as LLAMA-2 (13b). Such nuances have remained unexplored in earlier benchmarks because of the limited scope of question complexity and prompt length.

![](images/65e76def729a3a4d7a36b8c8384f5fb4a17ccdc7f5871dffd24ddcd513d3f7d2.jpg)  
Figure 1: Example questions in NLPBench dataset. We collected three types of questions, including multiple choice, short answer, and math, and divided them into two categories: with and without context. Text underline shows the relations between questions.

Apart from examining the effectiveness of various prompting strategies, we also conducted a manual assessment of NLP problem-solving capabilities in two dimensions: (1) error rate statistics across different NLP categories and (2) an evaluation of problem-solving abilities from a human expert’s viewpoint. For the first dimension, we compiled the error rates for each NLP category, segmented by individual LLMs and their associated prompting strategies. Our findings indicate that few-shot prompts can decrease the error rate for specific question types by introducing domain-specific supplementary information. In contrast, other methods might not bring about a substantial reduction in error rates. For the second evaluation dimension, we initially identified seven scientific problemsolving skills. We then categorized the mistakes made by the LLMs to highlight deficiencies in these pre-established skills. Our findings underscore that the absence of skills in logical decomposition, problem deduction, and logical reasoning predominantly contributes to the subpar performance observed in our NLPBench. Based on the above evaluations, we conclude that simple prompting methods are enough for promising results, and the training process should focus more on fostering specific problem-solving skills like logical decomposition and reasoning.

## 2 THE NLPBENCH DATASET

We collect a new dataset consisting of final exam questions from the universities’ NLP courses to evaluate the capabilities and analysis of the limitations of the existing large language models (LLMs) to solve NLP-related problems. All questions are divided into two types: with and without context, where a question with context consists of multiple related sub-questions sharing the same public information. Questions with context require answering with multi-turn communication. We further

Table 1: Statistic of the original dataset and the percent of usage in our proposed dataset.
<table><tr><td rowspan="3">Categories</td><td colspan="2">Short Answer</td><td colspan="2">Multiple Choice</td><td colspan="2">Math</td></tr><tr><td>w/ context</td><td>w/o context</td><td>w/ context</td><td>w/o context</td><td>w/ context</td><td>w/o context</td></tr><tr><td># Total</td><td>237</td><td>148</td><td>16</td><td>162</td><td>28</td><td>15</td></tr><tr><td>% Answer</td><td>67.1% (159)</td><td>58.1% (86)</td><td>93.7% (15)</td><td>88.9% (144)</td><td>92.8% (26)</td><td>46.6/% (7)</td></tr><tr><td>% Used</td><td>72.6% (130)</td><td>48.4% (62)</td><td>93.7% (15)</td><td>88.9% (144)</td><td>85.7% (24)</td><td>20% (3)</td></tr></table>

categorize each question according to the answer format: short answer, multiple choice, and math.   
This section introduces the details of the dataset construction process.

Data selection. Initially, we amassed a substantial collection of approximately 1,000 NLP exam questions over a decade, from 2013 to 2023. Professors and teaching assistants (TAs) contributed new questions to this repository each semester. This extensive set comprises three types of questions: 1) Online-sourced questions, refined by TAs to differentiate them from their original versions, ensuring their uniqueness for final exams, and a thorough verification of answers. 2) Original questions formulated by professors, drawing from their teaching experience. 3) Original questions developed by TAs. Over 30 TAs have been involved in the completion of this dataset. The questions are of high quality and are not available online, maintaining the integrity and fairness of the final exams. We discard the questions with figures or tables, and the remaining 372 questions are used in NLP-Bench. Different from the previous benchmarks, our dataset introduces a new category with context, as shown in Figure 1, which requires more complex reasoning steps to capture the relation between the current question and context and the relation between current and other questions. Considering the evaluation of the basic ability of LLMs, our dataset also contains traditional without context questions. All of the above questions are further divided into multiple-choice, short answer, and math according to their answer type. Specifically, our proposed dataset has the following features:

• Inclusion of NLP-related problems. The chosen problems demand a solid understanding of NLP-related knowledge (e.g., rhetorical structure theory, formal languages, application of probabilistic theory in NLP, etc.) in reasoning capability, the adaptation of calculation skills, and the ability to comprehend complex concepts.

• Inclusion of detailed solutions: To facilitate a thorough analysis of the limitations of LLMs, detailed solutions should be provided for the selected problems. This enables a comprehensive examination of the performance of LLMs and their capacity to handle complex problem-solving tasks.

• Inaccessibility. To ensure an unbiased evaluation, we carefully curate questions that are not readily accessible online and couldn’t be easily extracted or transformed into text. This selection process aims to mitigate any potential information leakage from the exposure of LLMs to pre-existing online question banks, such as those found in standardized tests like the SAT exams.

• Complex structure. About half of our collected questions have a complex structure, with a context shared with multiple subsequent questions and relations between each question. This type of question requires the model to solve with a multi-turn conversation and examine the model’s ability to capture critical information in the context.

Data processing. All questions are initially available in both text and image formats (e.g., handwritten), which we meticulously converted into plain text and LaTeX documents using a web-based annotation tool, and the extracted questions will be saved in JSON format. A detailed overview of the tool’s user interface can be found in Appendix B. Expert human annotators rigorously reviewed each problem to guarantee the absence of LaTeX syntax errors and to ensure all characters adhere to the ASCII standard. We classified the questions into three formats: short answers, multiple choice, and mathematical. Furthermore, based on the inclusion or exclusion of context information, information common to a set of subsequent questions (e.g., paragraphs from a book, upon which the answers to all following questions are contingent), we divided the questions into two main categories: with and without context. Notably, we integrated the true-false format from the original dataset into the multiple-choice category due to its limited amount. Each question comes with a ground-truth answer for evaluation. Our dataset also contains short answer questions that require free-form responses, such as prompting for examples or specific subsets of a concept. This further reduces the chances of candidates simply guessing correct answers rather than only using multiple choice questions (Lu et al., 2021a; 2022; Chen et al., 2023). To assist in evaluating responses to these questions, we offer sample answers that guide evaluators in determining the accuracy of a response. For mathematical problems, we document answers in LaTeX format, specifying exact figures, accompanied by their respective step-by-step solutions. These stepwise solutions serve as guides for intermediate reasoning methodologies (e.g., the "Chain of Thought" approach), assisting LLMs in formulating more accurate answers.

Dataset statistics. In summary, we collected 378 questions from some Universities’ NLP course final exams. The dataset includes 192 short-answer questions, 159 multiple-choice questions, and 27 math questions with step-bystep solutions. All types of questions are divided into with context and without. We detailed the statistical results of each question type in Table 1. All questions were also orig-

Table 2: The question quantity under each NLP concept. All the categories are defined by human experts.
<table><tr><td>Category</td><td>Acronym</td><td># Questions</td></tr><tr><td>Language Modeling and Syntax Parsing</td><td>1msp</td><td>162</td></tr><tr><td>Semantics and Logic</td><td>sl</td><td>69</td></tr><tr><td>Pragmatics, Discourse, Dialogue and Applications</td><td>pdda</td><td>13</td></tr><tr><td>Information Retrieval and Topic Modeling</td><td>irtm</td><td>27</td></tr><tr><td>Artificial Intelligence</td><td>ai</td><td>75</td></tr><tr><td>Other Topics</td><td>ot</td><td>32</td></tr></table>

inally categorized into six common NLP-related concepts, summarized in Table 2. Specifically, the questions belong to Other topics are in the field of current research, speech processing, ethics, and applications to other domains.

## 3 EXPERIMENT

## 3.1 EXPERIMENT SETUP

We evaluate both the online accessible models (GPT-3.5, OpenAI. (2022), GPT-4, OpenAI. (2023) and PaLM-2, Anil et al. (2023)) and open-sourced models (LLAMA-2 (13 and 70b), Touvron et al. (2023b)) on the proposed dataset. We consider two advanced prompting strategies, including chainof-thought (CoT, Wei et al. (2022)) and tree-of-thought (ToT, Yao et al. (2023)), under both zeroshot and few-shot with or without system prompt. We also perform self-consistency (SC) as an improvement of greedy methods.

• Zero-shot and few-shot prompting. Under zero-shot prompting, the model is not able to access questions in the training set for prior knowledge, which evaluates their inherent problem-solving capabilities with background knowledge and reasoning abilities. While in the few-shot prompting, a few examples are mixed into the input prompt as the prerequisites for the later questions. This aims to examine their capability to learn new information from the demonstrations and incorporate it into their problem-solving processes.

• Advanced prompting strategies. We try different prompting methods, zero-shot and few-shot, and we further combine them with or without system prompt, CoT, and ToT. We implement CoT in two ways: the traditional 2-staged (adding let’s think step by step behind the questions) for short answer questions and format template for multiple choice and math questions. This is because of the hardness of extracting the reasoning chain from the short answer questions, different from the multiple choice and math, in which we can extract an exact problem-solving process easily by separating the final answer and the corresponding process.

In summary, we consider ten combinations of prompting strategies: zero-shot and few-shot prompting (ZS, FS), zero-shot and few-shot prompting with system prompt (ZS+SYS, FS+SYS), chainof-thought prompting under zero-shot and few-shot (ZS+CoT, FS+CoT), chain-of-thought prompting under zero-shot and few-shot with system prompt (ZS+CoT+SYS, FS+CoT+SYS), and tree-ofthought under zero-shot and few-shot (ZS+ToT, FS+ToT). Zero-shot, few-shot, and CoT, with SC, are evaluated on the multiple choice question set due to the limitation of the statistic method in SC. Example prompts of the above method are provided in Appendix A.3.

Implementation details. We access the API of GPT-3.5 (gpt-3.5-turbo) and GPT-4 (gpt-4) via AutoGen2 (Wu et al., 2023), which provided the enclosure of Open-AI API, helping us cache the results with same hyperparameters. We access PaLM-2 via the Google PaLM generate\_text

Table 3: Experimental results in terms of accuracy (%) on our proposed dataset. The best average scores in each type of question are highlighted in bold in red, and the best average scores for each model in a specific type of question are underlined in blue. Results marked with - denote the incomplete experiment caused by exceeding context length or other prompting errors.
<table><tr><td rowspan="2">Model</td><td rowspan="2">Setting</td><td rowspan="2"></td><td colspan="3">Multiple Choice</td><td colspan="3">Short Answer</td><td colspan="3">Math</td><td rowspan="2">Overall Acc.</td></tr><tr><td>w/ Context</td><td>w/o Context</td><td>Average</td><td>w/ Context</td><td>w/o Context</td><td>Average</td><td>w/ Context</td><td>w/o Context</td><td>Average</td></tr><tr><td rowspan="6">LLAMA-2 (13b)</td><td>ZS</td><td>Orig. +SYS</td><td>20.00 26.67</td><td>20.83 34.03</td><td>20.75 33.33</td><td>39.23 43.85</td><td>37.10 27.42</td><td>38.54 3854</td><td>20.00 0.00</td><td>0.00 0.00</td><td>4.00 0.00</td><td>28.72 33.77</td></tr><tr><td rowspan="4"></td><td rowspan="4">+CoT +CoT+SYS Orig.</td><td>26.67 33.33</td><td>19.44</td><td>20.13</td><td>22.31</td><td>9.68</td><td>18.23</td><td>0.00</td><td>0.00</td><td>0.00</td><td>117.82</td></tr><tr><td></td><td>27.08</td><td>27.67</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td>23.08</td><td>9.68</td><td>18.75</td><td>0.00</td><td>0.00</td><td>0.00</td><td>21.28</td></tr><tr><td></td><td>31.25</td><td>28.30</td><td></td><td>29.03</td><td>9.38</td><td>-</td><td>-</td><td>0.00</td><td>16.76</td></tr><tr><td>FS</td><td>+SYS +CoT +CoT+SYS</td><td>- - -</td><td>38.19 30.56 36.81</td><td>34.59 27.67 33.33</td><td></td><td>30.65 32.26 35.48</td><td>9.90 10.42 11.46</td><td>- - -</td><td>- -</td><td>0.00 0.00 0.00</td><td>19.68 17.02 19.95</td></tr><tr><td rowspan="6">LLAMA-2 (70b)</td><td rowspan="2">ZS</td><td>Orig. +SYS +CoT +CoT+SYS</td><td>40.00 40.00 33.33</td><td>22.22 23.61 21.53</td><td>23.90 25.16 22.64</td><td>53.85 54.62 32.31</td><td>38.71 46.77 12.90</td><td>48.96 522088</td><td>9.09 9.09</td><td>0.00 0.00</td><td>8.00 8.00</td><td>35.64 37.77</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td>26.04</td><td>0.00 0.00</td><td>0.00 0.00</td><td>0.00 0.00</td><td>22.87 31.91</td></tr><tr><td rowspan="6">FS</td><td rowspan="2">Orig. +SYS +CoT</td><td>40.00 33.33</td><td>38.19</td><td>38.36</td><td>33.08</td><td>25.81</td><td>30.73</td><td></td><td></td><td></td><td></td></tr><tr><td></td><td>29.17 34.72</td><td>29.56 33.96</td><td>48.46 46.92</td><td>38.71</td><td>45.31</td><td>9.09</td><td>0.00</td><td>19.38</td><td>36.93</td></tr><tr><td></td><td>26.67 26.67 26.67</td><td>31.94</td><td>31.45</td><td>38.46</td><td>40.32 51.61</td><td>44.79 42.71</td><td>0.00 0.00</td><td>0.00 0.00</td><td>0.00 0.00</td><td>37.23 35.11</td></tr><tr><td>+CoT+SYS</td><td></td><td>38.19</td><td>37.11</td><td>35.38</td><td>48.39</td><td>39.58</td><td>4.55</td><td>0.00</td><td>4.00</td><td>36.17</td></tr><tr><td rowspan="8">ZS</td><td>Orig. +SYS +CoT</td><td>66.67 66.67</td><td>37.50 45.83 36.81</td><td>40.25 47.80 38.99</td><td>49.23 51.54</td><td>35.48 37.10</td><td>44.79 46.88</td><td>13.64 4.55</td><td>33.33</td><td>16.00</td><td>40.96 44.68</td></tr><tr><td></td><td>+CoT+SYS</td><td>60.00</td><td></td><td></td><td></td><td></td><td></td><td>18.18</td><td>33.33 33.33</td><td>8.00 20.00</td></tr><tr><td rowspan="8">FS</td><td>+ToT</td><td>53.33 -</td><td>41.67 4.86</td><td>42.77 4.40</td><td>47.69 40.00 -</td><td>37.10 30.65</td><td>44.27 36.98</td><td>13.64</td><td>0.00</td><td>12.00</td><td>40.42 37.77</td></tr><tr><td>Orig.</td><td>53.33</td><td>38.89</td><td>40.25</td><td>57.69</td><td>0.00 33.87</td><td>0.00 50.00</td><td>- 4.55</td><td>-</td><td>0.00</td><td>1.86</td></tr><tr><td>+SYS +CoT</td><td>53.33 53.33 40.00</td><td>39.58 40.28</td><td>40.88 41.51</td><td>56.15 49.23</td><td>38.71 38.71</td><td>50.52 45.83</td><td>4.55 0.00</td><td>33.33 0.00 0.00</td><td>8.00 4.00 0.00</td><td>43.08 43.35 40.96</td></tr><tr><td>+CoT+SYS +ToT Orig.</td><td></td><td>38.89 10.42 52.05</td><td>38.99 9.43 50.64</td><td>53.85 - 75.38</td><td>40.32 1.61 58.73</td><td>49.48 0.52</td><td>0.00 -</td><td>0.00 -</td><td>0.00 0.00</td><td>41.75 4.25</td></tr><tr><td>ZS</td><td>+SYS</td><td>40.00 46.67</td><td>41.51</td><td></td><td></td><td></td><td>69.99 68.75</td><td>36.36</td><td>33.33</td><td>36.00 59.55 553.72</td></tr><tr><td></td><td>+CoT +CoT+SYS</td><td>53.33</td><td>40.69 52.74</td><td>28.30</td><td></td><td>62.90</td><td>54.19 64.58</td><td>13.64 18.18 18.18</td><td>33.33 100.00</td><td>16.00 28.00</td></tr><tr><td>FS</td><td>+ToT</td><td></td><td>31.25</td><td></td><td></td><td>59.68</td><td></td><td>-</td><td>0.00</td><td>16.00</td></tr><tr><td rowspan="8"></td><td></td><td>46.67</td><td>39.58</td><td>52.883 40.25</td><td>71.54 63.85 66.92</td><td>33.33</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>51.87</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td rowspan="8"></td><td>Orig. +SYS</td><td>53.33</td><td></td><td></td><td>-</td><td>0.00</td><td>0.00</td><td></td><td>-</td><td>0.00</td><td>51.06 11.97 51.06 51.86</td></tr><tr><td></td><td>46.67</td><td>36.81 44.44</td><td>38.36 44.65</td><td>66.15 66.15</td><td>64.52 54.84</td><td>65.62 62.50</td><td>18.18</td><td>33.33</td><td>20.00</td></tr><tr><td>+CoT +CoT+SYS</td><td></td><td>40.28</td><td>40.25</td><td>64.62</td><td>62.90</td><td>64.06</td><td>18.18 13.64</td><td>0.00</td><td>16.00</td></tr><tr><td></td><td>40.00</td><td>46.53</td><td>45.91</td><td>66.15</td><td></td><td>65.62</td><td>18.18</td><td>0.00</td><td>12.00</td></tr><tr><td>+ToT</td><td>40.00</td><td></td><td></td><td></td><td>64.52</td><td></td><td></td><td>0.00</td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>16.00 0.00</td></tr><tr><td>+SYS +CoT</td><td></td><td></td><td></td><td>83.85</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>+CoT+SYS</td><td></td><td>86.67 86.67</td><td>70.55 57.93</td><td>72.25 60.38</td><td>78.46</td><td>69.84 79.03</td><td>18.23 75.42 82.29</td><td>- 22.73 18.18</td><td>- 33.33</td></tr><tr><td>ZS GPT-4</td><td>Orig.</td><td>-</td><td>30.56</td><td>27.67</td><td>-</td><td>56.45</td></table>

Table 4: Comparison of prompting methods with and without self-consistency (denoted as SC) on GPT-3.5, GPT-4, and PaLM-2. All results are statistics from the multiple-choice question set.
<table><tr><td rowspan="2">Model</td><td colspan="2">zS</td><td colspan="2">ZS+CoT</td><td colspan="2">FS</td><td colspan="2">FS+CoT</td></tr><tr><td>w/o SC</td><td>w/SC</td><td>w/o SC</td><td>w/SC</td><td>w/o SC</td><td>w/SC</td><td>w/o SC</td><td>w/SC</td></tr><tr><td>GPT-3.5</td><td>50.64</td><td>37.11</td><td>52.83</td><td>38.36</td><td>38.36</td><td>43.40</td><td>40.25</td><td>44.03</td></tr><tr><td>GPT-4</td><td>72.25</td><td>59.75</td><td>74.10</td><td>62.89</td><td>64.78</td><td>64.78</td><td>62.89</td><td>66.67</td></tr><tr><td>PaLM-2</td><td>40.25</td><td>23.90</td><td>38.99</td><td>28.30</td><td>40.25</td><td>37.11</td><td>41.51</td><td>38.99</td></tr></table>

API3, which is recommended by Google for problem-solving and handling zero and few shot tasks. For open-source models LLAMA-2 (13b and 70b), we use the endpoint implemented by vLLM4 (Kwon et al., 2023), an open-sourced, fast-speed LLM serving platforms for a wide range of open-source models, which can provide Open-AI like API for the LLM user. We further access those endpoints via AutoGen, the same as we access the Open-AI model. For all models, we use the same seed and set the temperature as 1 for question answering and 0 for the middle process in CoT and ToT. We choose a high temperature for a more creative answer and a low temperature for a more specific process.

## 3.2 RESULTS AND ANALYSIS

The experimental results for GPT-3.5, GPT-4, PaLM-2, and LLAMA-2 (13b and 70b) with various configurations on our NLPBench are detailed in Table 3. Supplementary analysis utilizing conventional text evaluation metrics, such as ROUGE-L and CIDEr, can be found in Appendix A.1. We highlight the model performance by presenting accuracy scores in both ‘with’ and ‘without’ context scenarios. Notably, questions requiring context involve multi-turn interactions with the model. Our accuracy calculation focuses on the model’s final answer, disregarding intermediary steps when computing accuracy, which will be considered in the human evaluation process. For context-based questions, we examine the accuracy of each distinct sub-question. From the experiment results, we have several key observations:

GPT-4 outperforms all models with a significant margin under most of the situations. Based on the results across three distinct question formats categorized under two categories, GPT-4 outperforms all baselines under most situations. Specifically, it achieved the top spot with the best average performance accuracy in two of the question formats. When juxtaposed against all baseline methods, there’s a remarkable uplift in its performance, registering an average score improvement of at most 67.85% and 82.29% when compared with LLAMA-2 (13b). It’s worth highlighting that these outstanding results were obtained under a zero-shot setting without the aid of any sophisticated prompting strategies. Interestingly, our observations also indicate that deploying advanced prompting techniques often has a counterproductive effect on GPT-4’s performance in many scenarios.

Few-shot prompting does not always improve. In Figure 2, we present a comparison of average performance between zero-shot and few-shot prompting. Notably, the adoption of few-shot prompting often results in a modest performance enhancement, and in some cases, even a decrease, consistent with findings by Wang et al. (2023). A closer examination of Table 3 reveals that in some cases, LLAMA-2 (13b and 70b) derives advantages from the supplementary knowledge gained through fewshot prompting. However, this can lead to surpassing the maximum context length, particularly when multi-turn communication is necessitated, or the query contains an extensive description, which leads to a significant performance drop in LLAMA-2 (13b). GPT-3.5, GPT-4, and PaLM-2 only have ordinary improvements, about 3%,

![](images/d967568b5fc5b1bdba8d1b9fe3f22fbdedd42dc47817680d597d0b64b6c68b25.jpg)  
Figure 2: Zero-shot v.s. few-shot prompting on overall accuracy(%).

when adopting few-shot prompting. In fact, seven out of the nine highest average scores were realized using zero-shot prompting. This phenomenon may arise because the chosen sample questions are either highly representative of and specific to the domain or, conversely, do not capture its diversity adequately, introducing errors during inference. Therefore, while few-shot prompting can potentially extend the prompt length and occasionally enhance performance, the selection of sample questions is critical. Ill-chosen examples can introduce noise detrimental to the task at hand.

Advanced prompting strategies do not work consistently, sometimes having a negative effect. In Figure 3, we present the average scores both with and without the utilization of advanced prompting strategies. Notably, CoT only provides a slight performance increase with GPT-3.5 and will cause performance declines in other models. The efficacy of these prompting strategies is heavily dependent on the model’s innate ability to adhere to the prompts, which necessitates the models to selfevaluate their responses. CoT demands a singular feedback loop, which is relatively straightforward. In contrast, ToT calls for multiple feedback mechanisms coupled with a search operation, such as the DFS algorithm. Challenges arise with ToT when a model generates a response that diverges from the specified template in the prompt. GPT-3.5/4 exhibits an exceptional capacity to process intricate prompts, yielding the SOTA results (when comparing with other models) in tasks that necessitate intricate logical reasoning when implementing advanced prompting strategies but still cannot outperform the baseline without any prompting strategy. While LLAMA-2 (13b), due to the limited prompt-following capability and constricted context length, it experienced a downturn in performance when employing these advanced strategies. On the other hand, self-consistency (Wang et al., 2022), a robust alternative to greedy decoding, demonstrates impressive results on other benchmarks. Nevertheless, our findings, detailed in Table 4, indicate that while self-consistency can enhance performance with few-shot prompting (as seen with GPT-3.5 and GPT-4), it considerably undermines the output during zero-shot prompting. A potential explanation for such contrasting outcomes is that few-shot prompting restricts the scope of knowledge, impacting answer generation, a constraint absent in zero-shot prompting.

![](images/f331d5ee2b7f85c579d0974015433590959380cf6e54e52994e4d61c7282db2a.jpg)  
Figure 3: Overall accuracy(%) with and without advanced prompting strategies.

![](images/fdc1898c33d9a636a09c1221ca1fddccf500c405aa7208ac43e191edca624060.jpg)  
Figure 4: The comparison of overall error rate(%) between GPT-3.5/4 and LLAMA 2-70b across all prompting strategies of each NLP category. Each color bar indicates a pre-defined NLP category from the original dataset.

## 4 ERROR ANALYSIS OF VARIOUS PROMPTING STRATEGIES

Considering the substantial advancements of current Large Language Models (LLMs), an in-depth analysis of the particular skills that are either enhanced or limited under certain settings becomes imperative. We evaluate two types of abilities that should be obtained before taking the final exam: an understanding of natural language processing (NLP) and the ability to solve college-level problems. We select the results provided by GPT-3.5/4 and LLAMA 2-70b, which represent the SOTA online and open-sourced model, respectively.

## 4.1 UNDERSTANDING OF NATURAL LANGUAGE PROCESSING

To assess the NLP comprehension of LLMs, we delineated the errors made by GPT-3.5/4 and LLAMA 2-70b in Figure 4, showcasing their respective error rates across various NLP categories. A notable disparity in distribution is evident between zero-shot and few-shot prompting. There’s a marked decrease in error rates for pdda by 16% for GPT-4 and 32% for LLAMA 2-70b when transitioning from zero-shot to few-shot prompting, a trend similarly noted in the CoT results. However, this trend diminishes once a system prompt is integrated. The introduction of a system prompt and additional example questions helps mitigate errors stemming from incorrect prior knowledge. Yet, combining the system prompt with few-shot prompting increases the error rate by 10% on irtm and

![](images/c4d8072ce4de3970a14f73944a63317bdbdfd7ee1eb7208a0a693a596828ee4b.jpg)  
Figure 5: The error profiles of the deficient of seven essential science problem-solving abilities between GPT-3.5/4 and LLAMA 2-70b. The height of the color bars indicates the percentage that the model has an incorrect answer due to a lack of corresponding science problem-solving skills.

8% on pdda for GPT-4. In contrast, there’s a 13% reduction in the error rate for ot. For LLAMA 2-70b, few-shot prompting consistently reduces error rates across categories, resulting in a more balanced error distribution.

In summary, few-shot prompting can help decrease the error rate for certain types of questions by offering additional examples from the dataset. However, its effectiveness diminishes when the dataset demands a broad spectrum of knowledge. While advanced prompting strategies like CoT may not substantially enhance performance with complex datasets, system prompts can counteract errors introduced by these advanced strategies.

## 4.2 ABILITY TO SOLVE COLLEGE-LEVEL PROBLEMS

We chose three models, both online and open-sourced, with the best average performance (GPT-3.5 w/ ZS, GPT-4 w/ ZS, and LLAMA 2-70b w/ ZS+SYS) and annotated the source of the error for short answers (with a unique answer) and math questions, indicating where the model made a mistake and why. Following Wang et al. (2023), we classify the human-annotated error reasons into seven crucial skills deficient for solving complex college-level problems. For each wrong question, we summarized three of the seven skills:

• Logical decomposition and analysis (LD). This ability involves decomposing the question into smaller, manageable parts and understanding the relationships between these parts.

• Identification of assumptions (IA). This skill involves the ability to recognize relevant and necessary assumptions in the question.

• Causal reasoning (CR). This is the ability to understand cause-and-effect relationships.

• Problem deduction skills (PD). This pertains to the ability to infer and deduce potential solutions or underlying principles from the given information in a problem.

• Abstract reasoning (AR). This skill involves the ability to understand complex concepts that cannot be perceived physically and to recognize patterns or relationships beyond concrete examples.

• Logical reasoning (LR). This is the ability to make a reasoned argument and to identify fallacies or inconsistencies in an argument or set of data.

• Calculation (CA). This involves the ability to carry out mathematical operations and computations accurately.

The analysis results are recorded in Figure 5, we also provided some error samples in Appendix A.2. Compared with the SOTA GPT-4, GPT-3.5 has 6% and 7% higher probability of making wrong answers caused by a lack of problem deduction and logical reasoning skills, and LLAMA 2-70b has 14%, 11%, and 16% higher in logical decomposition, problem deduction and logical reasoning skills. This increment reveals a strong relation between a correct answer and logical decomposition, problem deduction, and logical reasoning skills, which is similar to the findings of Berglund et al. (2023). Many questions in our NLPBench dataset require an understanding of a given text before the question (e.g., a story or news). Answer such questions need to retrieve the critical information in the context and build up a logical relation between the question and the retrieved information, which requires a high-level logical decomposition and logical reasoning ability. We also found that

GPT-3.5 and 4 do not lack calculation skills but have a low accuracy in math questions (see Table 3). This is because models need to understand the question before the calculation, and the question in our dataset is hard (e.g., requires an understanding of the EM algorithm). Therefore, models often give an answer that is correct in the calculation with a completely wrong process.

## 5 RELATED WORKS

Traditional benchmarks have been oriented toward assessing the general abilities of models. For instance, SQuAD (Rajpurkar et al., 2018) was developed to gauge models’ reading comprehension skills. GLUE (Wang et al., 2018) provides a versatile framework for evaluating performance across a variety of natural language understanding tasks. Cosmos QA (Huang et al., 2019) delves into assessing models on their common-sense reasoning abilities using natural language contexts. HumanEval (Chen et al., 2021) targets the coding prowess of models, presenting 164 Python programming challenges. BIG-Bench (Srivastava et al., 2022) serves as a comprehensive test suite that includes 204 multiple-choice or exact-match tasks, while its counterpart, BIG-Bench Hard (Suzgun et al., 2022), presents notably intricate chain-of-thought prompts. Finally, HELM (Liang et al., 2022) offers a detailed multi-metric evaluation of LLMs, shedding light on their strengths, weaknesses, and potential risks.

Recent benchmarks predominantly assess LLMs’ problem-solving skills, particularly in science and mathematics (Lu et al., 2023b; Fu et al., 2023; Lu et al., 2023a; Zhong et al., 2023; Mishra et al., 2022; Chen et al., 2023; Guo et al., 2023; Hendrycks et al., 2020). Noteworthy datasets include GSM8K (Cobbe et al., 2021), which contains 8.5K elementary math word problems, ScienceQA (Lu et al., 2022), a multimodal dataset with lectures, and MATH (Hendrycks et al., 2021), consisting of 12.5K problems from math contests. LILA (Mishra et al., 2022) enhances 20 datasets with task guidelines and Python solutions. Most benchmarks focus on foundational arithmetic, but TheoremQA (Chen et al., 2023) offers 800 theorem-centric questions. Galactica (Taylor et al., 2022) explores scientific tasks, such as latex equation conversions, while C-EVAL (Huang et al., 2023) evaluates LLMs within a Chinese cultural context. AGIEval (Zhong et al., 2023) measures LLM performance against standardized tests using human-annotated analysis. SciBench (Wang et al., 2023) presents college-level science problems from textbooks with an automatic evaluation method. However, while these benchmarks emphasize single-turn communication, ours assesses the multiturn problem-solving capabilities of LLMs. A detailed comparison is provided in Appendix C.

## 6 CONCLUSION AND RECOMMENDATION

This study unveils NLPBench, a collection of 378 college-level NLP questions aimed at comprehensively evaluating Large Language Models (LLMs) like GPT-3.5, GPT-4, and others. NLPBench is designed for testing LLMs’ proficiency in multi-turn conversations, using advanced prompting strategies such as chain-of-thought and few-shot prompting. However, the evaluation indicates that these strategies don’t always enhance performance. A closer look at errors made by models like GPT-3.5/4 and LLAMA 2-70b suggests they mainly falter in logical deconstruction and reasoning, leading to their limited success on NLPBench. Based on the above conclusion, we have the following recommendations:

• Simple Prompting method is enough for promising results. Based on our findings in Section 3.2, we found that few-shot prompting averagely surpasses zero-shot, but it is hard to achieve the best. Section 4.1 indicates that while few-shot can decrease errors in certain categories, it can also lead to more verbose prompts. Employ few-shot prompting when your task is concentrated on a specific domain.

• Advanced prompting strategies are not necessary. They show weak or roughly comparable results to zero-shot on all LLMs and will significantly affect the relatively small LLM (e.g., LLAMA 2-13b). As described in Section 3.2, advanced prompting strategies need strong prompt followup ability, since they all require multiple reasoning steps. If budget is one of your limitations, zero-shot is also a good choice for a competitive result.

• The pretraining process should focus more on fostering "logical thinking skills" According to Section 4.2, we found that LLAMA 2 clearly lacks the ability to do logical decomposition, problem deduction, and logical reasoning. We believe that LLM training should take into account these three dimensions.

## ETHICS STATEMENT

NLPBench aims to evaluate the NLP-related problem-solving ability of LLMs. Our evaluation results provide efficient insight for further research on advanced prompting strategies or LLM pretraining by testing and analyzing the reason for the errors made by LLMs. NLPBench does not contain any personal, sensitive, or confidential data and is diverse and representative of a wide range of scenarios, demographics, and contexts.

## REPRODUCIBILITY STATEMENT

Our main experiments are done on online accessible or open-sourced models (except for PaLM-2, which is not an openly accessible model yet). We publish our implementation in https:// anonymous.4open.science/r/NLPB-04A3 and provide the prompts in Appendix A.3 to further increase the reproducibility.

## REFERENCES

Rohan Anil, Andrew M Dai, Orhan Firat, Melvin Johnson, Dmitry Lepikhin, Alexandre Passos, Siamak Shakeri, Emanuel Taropa, Paige Bailey, Zhifeng Chen, et al. Palm 2 technical report. arXiv preprint arXiv:2305.10403, 2023.

Lukas Berglund, Meg Tong, Max Kaufmann, Mikita Balesni, Asa Cooper Stickland, Tomasz Korbak, and Owain Evans. The reversal curse: Llms trained on "a is b" fail to learn "b is a", 2023.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.

Wenhu Chen, Ming Yin, Max Ku, Pan Lu, Elaine Wan, Xueguang Ma, Jianyu Xu, Tony Xia, and Xinyi Wang. Theoremqa: A theorem-driven question answering dataset. arXiv preprint arXiv:2305.12524, 2023.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.

Yao Fu, Litu Ou, Mingyu Chen, Yuhao Wan, Hao Peng, and Tushar Khot. Chain-of-thought hub: A continuous effort to measure large language models’ reasoning performance. arXiv preprint arXiv:2305.17306, 2023.

Fan Gao, Hang Jiang, Moritz Blum, Jinghui Lu, Yuang Jiang, and Irene Li. Large language models on wikipedia-style survey generation: an evaluation in nlp concepts. arXiv preprint arXiv:2308.10410, 2023a.

Peng Gao, Jiaming Han, Renrui Zhang, Ziyi Lin, Shijie Geng, Aojun Zhou, Wei Zhang, Pan Lu, Conghui He, Xiangyu Yue, Hongsheng Li, and Yu Qiao. Llama-adapter v2: Parameter-efficient visual instruction model. arXiv preprint arXiv:2304.15010, 2023b.

Taicheng Guo, Kehan Guo, Zhengwen Liang, Zhichun Guo, Nitesh V Chawla, Olaf Wiest, Xiangliang Zhang, et al. What indeed can gpt models do in chemistry? a comprehensive benchmark on eight tasks. arXiv preprint arXiv:2305.18365, 2023.

Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. Measuring massive multitask language understanding. arXiv preprint arXiv:2009.03300, 2020.

Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song, and Jacob Steinhardt. Measuring mathematical problem solving with the math dataset. arXiv preprint arXiv:2103.03874, 2021.

Jiaxin Huang, Shixiang Shane Gu, Le Hou, Yuexin Wu, Xuezhi Wang, Hongkun Yu, and Jiawei Han. Large language models can self-improve. arXiv preprint arXiv:2210.11610, 2022.

Lifu Huang, Ronan Le Bras, Chandra Bhagavatula, and Yejin Choi. Cosmos qa: Machine reading comprehension with contextual commonsense reasoning. arXiv preprint arXiv:1909.00277, 2019.

Yuzhen Huang, Yuzhuo Bai, Zhihao Zhu, Junlei Zhang, Jinghan Zhang, Tangjun Su, Junteng Liu, Chuancheng Lv, Yikai Zhang, Jiayi Lei, et al. C-eval: A multi-level multi-discipline chinese evaluation suite for foundation models. arXiv preprint arXiv:2305.08322, 2023.

Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E Gonzalez, Hao Zhang, and Ion Stoica. Efficient memory management for large language model serving with pagedattention. arXiv preprint arXiv:2309.06180, 2023.

Percy Liang, Rishi Bommasani, Tony Lee, Dimitris Tsipras, Dilara Soylu, Michihiro Yasunaga, Yian Zhang, Deepak Narayanan, Yuhuai Wu, Ananya Kumar, et al. Holistic evaluation of language models. arXiv preprint arXiv:2211.09110, 2022.

Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae Lee. Visual instruction tuning. arXiv preprint arXiv:2304.08485, 2023.

Pan Lu, Ran Gong, Shibiao Jiang, Liang Qiu, Siyuan Huang, Xiaodan Liang, and Song-Chun Zhu. Inter-gps: Interpretable geometry problem solving with formal language and symbolic reasoning. In The Joint Conference of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (ACL-IJCNLP 2021), 2021a.

Pan Lu, Liang Qiu, Jiaqi Chen, Tony Xia, Yizhou Zhao, Wei Zhang, Zhou Yu, Xiaodan Liang, and Song-Chun Zhu. Iconqa: A new benchmark for abstract diagram understanding and visual language reasoning. arXiv preprint arXiv:2110.13214, 2021b.

Pan Lu, Swaroop Mishra, Tanglin Xia, Liang Qiu, Kai-Wei Chang, Song-Chun Zhu, Oyvind Tafjord, Peter Clark, and Ashwin Kalyan. Learn to explain: Multimodal reasoning via thought chains for science question answering. Advances in Neural Information Processing Systems, 35:2507–2521, 2022.

Pan Lu, Liang Qiu, Kai-Wei Chang, Ying Nian Wu, Song-Chun Zhu, Tanmay Rajpurohit, Peter Clark, and Ashwin Kalyan. Dynamic prompt learning via policy gradient for semi-structured mathematical reasoning. In International Conference on Learning Representations (ICLR), 2023a.

Pan Lu, Liang Qiu, Wenhao Yu, Sean Welleck, and Kai-Wei Chang. A survey of deep learning for mathematical reasoning. In The 61st Annual Meeting of the Association for Computational Linguistics (ACL), 2023b.

Swaroop Mishra, Matthew Finlayson, Pan Lu, Leonard Tang, Sean Welleck, Chitta Baral, Tanmay Rajpurohit, Oyvind Tafjord, Ashish Sabharwal, Peter Clark, et al. Lila: A unified benchmark for mathematical reasoning. In The 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2022.

OpenAI. Chatgpt: Optimizing language models for dialogue. https://openai.com/blog/ chatgpt/., 2022.

OpenAI. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.

Pranav Rajpurkar, Robin Jia, and Percy Liang. Know what you don’t know: Unanswerable questions for squad. arXiv preprint arXiv:1806.03822, 2018.

Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, Abu Awal Md Shoeb, Abubakar Abid, Adam Fisch, Adam R Brown, Adam Santoro, Aditya Gupta, Adrià Garriga-Alonso, et al. Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. arXiv preprint arXiv:2206.04615, 2022.

Mirac Suzgun, Nathan Scales, Nathanael Schärli, Sebastian Gehrmann, Yi Tay, Hyung Won Chung, Aakanksha Chowdhery, Quoc V Le, Ed H Chi, Denny Zhou, et al. Challenging big-bench tasks and whether chain-of-thought can solve them. arXiv preprint arXiv:2210.09261, 2022.

Ross Taylor, Marcin Kardas, Guillem Cucurull, Thomas Scialom, Anthony Hartshorn, Elvis Saravia, Andrew Poulton, Viktor Kerkez, and Robert Stojnic. Galactica: A large language model for science. arXiv preprint arXiv:2211.09085, 2022.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al. LLaMA: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023a.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023b.

Alex Wang, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy, and Samuel R Bowman. Glue: A multi-task benchmark and analysis platform for natural language understanding. arXiv preprint arXiv:1804.07461, 2018.

Xiaoxuan Wang, Ziniu Hu, Pan Lu, Yanqiao Zhu, Jieyu Zhang, Satyen Subramaniam, Arjun R Loomba, Shichang Zhang, Yizhou Sun, and Wei Wang. Scibench: Evaluating college-level scientific problem-solving abilities of large language models. arXiv preprint arXiv:2307.10635, 2023.

Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, and Denny Zhou. Self-consistency improves chain of thought reasoning in language models. arXiv preprint arXiv:2203.11171, 2022.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Ed Chi, Quoc Le, and Denny Zhou. Chain of thought prompting elicits reasoning in large language models. arXiv preprint arXiv:2201.11903, 2022.

Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang. Autogen: Enabling next-gen llm applications via multiagent conversation framework. arXiv preprint arXiv:2308.08155, 2023.

Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L Griffiths, Yuan Cao, and Karthik Narasimhan. Tree of thoughts: Deliberate problem solving with large language models. arXiv preprint arXiv:2305.10601, 2023.

Renrui Zhang, Jiaming Han, Aojun Zhou, Xiangfei Hu, Shilin Yan, Pan Lu, Hongsheng Li, Peng Gao, and Yu Qiao. Llama-adapter: Efficient fine-tuning of language models with zero-init attention. arXiv preprint arXiv:2303.16199, 2023a.

Zhuosheng Zhang, Aston Zhang, Mu Li, Hai Zhao, George Karypis, and Alex Smola. Multimodal chain-of-thought reasoning in language models. arXiv preprint arXiv:2302.00923, 2023b.

Wanjun Zhong, Ruixiang Cui, Yiduo Guo, Yaobo Liang, Shuai Lu, Yanlin Wang, Amin Saied, Weizhu Chen, and Nan Duan. Agieval: A human-centric benchmark for evaluating foundation models. arXiv preprint arXiv:2304.06364, 2023.

Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Olivier Bousquet, Quoc Le, and Ed Chi. Least-to-most prompting enables complex reasoning in large language models. arXiv preprint arXiv:2205.10625, 2022.

## A FURTHER ANALYSIS

## A.1 EVALUATING TEXT RELEVANCE

Table 5: Relevance between LLM generated answers and ground-truth answers. We adopt BLEU, ROUGE-L, and CIDEr to represent the sentence relevance.
<table><tr><td rowspan="2">Model</td><td rowspan="2">Setting</td><td colspan="2">BLEU</td><td colspan="2">ROUGE-L</td><td colspan="2">CIDEr</td></tr><tr><td>w/ Context</td><td>w/o Context</td><td>w/ Context</td><td>w/o Context</td><td>w/ Context</td><td>w/o Context</td></tr><tr><td rowspan="10">GPT-3.5</td><td>ZS</td><td>0.10</td><td>5.83</td><td>0.48</td><td>8.75</td><td>10.91</td><td>14.23</td></tr><tr><td>ZS+SYS</td><td>0.11</td><td>5.20</td><td>5.04</td><td>8.69</td><td>7.75</td><td>0.00</td></tr><tr><td>ZS+CoT</td><td>0.16</td><td>4.82</td><td>0.28</td><td>13.19</td><td>11.35</td><td>14.74</td></tr><tr><td>ZS+CoT+SYS</td><td>0.47</td><td>5.28</td><td>0.23</td><td>13.94</td><td>10.08</td><td>3.79</td></tr><tr><td>ZS+ToT</td><td>-</td><td>-</td><td>-</td><td>0.00</td><td>0.00</td><td>0.00</td></tr><tr><td>FS</td><td>0.15</td><td>5.18</td><td>1.99</td><td>12.55</td><td>12.02</td><td>18.01</td></tr><tr><td>FS+SYS</td><td>0.55</td><td>6.26</td><td>6.31</td><td>17.01</td><td>13.26</td><td>27.19</td></tr><tr><td>FS+CoT</td><td>0.10</td><td>4.59</td><td>3.47</td><td>9.26</td><td>10.41</td><td>15.14</td></tr><tr><td>FS+SYS+CoT</td><td>0.31</td><td>5.07</td><td>0.01</td><td>14.04</td><td>12.05</td><td>17.41</td></tr><tr><td>FS+ToT</td><td>-</td><td>-</td><td>-</td><td>6.86</td><td>7.69</td><td>0.19</td></tr><tr><td rowspan="10">GPT-4</td><td>ZS ZS+SYS</td><td>0.63 0.67</td><td>6.47 7.03</td><td>9.32 5.40</td><td>11.83 14.31</td><td>9.85 9.46</td><td>6.28 0.14</td></tr><tr><td></td><td>1.12</td><td>7.00</td><td></td><td>10.68</td><td>9.67</td><td>25.16</td></tr><tr><td>ZS+CoT</td><td></td><td></td><td>5.05</td><td></td><td></td><td>5.29</td></tr><tr><td>ZS+CoT+SYS</td><td>1.14</td><td>7.29</td><td>2.66</td><td>15.69 0.00</td><td>10.16</td><td>0.00</td></tr><tr><td>ZS+ToT</td><td></td><td>-</td><td>-</td><td></td><td>0.00</td><td></td></tr><tr><td>FS</td><td>1.34</td><td>7.76</td><td>15.24</td><td>17.09</td><td>11.57</td><td>5.59</td></tr><tr><td>FS+SYS</td><td>2.00</td><td>9.94</td><td>21.85</td><td>20.17</td><td>14.32</td><td>15.90</td></tr><tr><td>FS+CoT</td><td>0.71</td><td>6.48</td><td>7.71</td><td>13.77</td><td>11.13</td><td>3.09</td></tr><tr><td>FS+SYS+CoT</td><td>0.90</td><td>6.82</td><td>7.87</td><td>17.93</td><td>14.98</td><td>35.73</td></tr><tr><td>FS+ToT</td><td>-</td><td>-</td><td>-</td><td>15.35</td><td>10.62</td><td>9.21</td></tr><tr><td rowspan="10">PaLM-2</td><td>ZS ZS+SYS</td><td>3.35 6.96</td><td>10.89 9.27</td><td>23.19 22.15</td><td>23.21 25.66</td><td>14.06 12.70</td><td>19.02 18.85</td></tr><tr><td>ZS+CoT</td><td>3.05</td><td>9.31</td><td>11.66</td><td>15.30</td><td>11.71</td><td>14.36</td></tr><tr><td>ZS+CoT+SYS</td><td>8.09</td><td>9.00</td><td>26.96</td><td>23.55</td><td>11.62</td><td>31.52</td></tr><tr><td>ZS+ToT</td><td>-</td><td></td><td></td><td>0.00</td><td>0.00</td><td>0.00</td></tr><tr><td></td><td></td><td>-</td><td>-</td><td></td><td></td><td></td></tr><tr><td>FS</td><td>1.16</td><td>13.28</td><td>57.25</td><td>26.74</td><td>13.68</td><td>17.67</td></tr><tr><td>FS+SYS</td><td>4.03</td><td>9.47</td><td>28.31</td><td>24.60</td><td>15.62</td><td>32.05</td></tr><tr><td>FS+CoT</td><td>0.33</td><td>8.19</td><td>20.83</td><td>14.32</td><td>9.86</td><td>4.68</td></tr><tr><td>FS+SYS+CoT</td><td>1.82</td><td>9.60</td><td>24.63</td><td>15.00</td><td>8.99</td><td>9.57</td></tr><tr><td>FS+ToT</td><td>-</td><td>-</td><td>-</td><td>0.50</td><td>0.72</td><td>1.89</td></tr><tr><td rowspan="10">LLAMA-2 (13b)</td><td>ZS ZS+SYS</td><td>0.19 0.37</td><td>4.80 5.02</td><td>0.02 0.00</td><td>9.69 11.35</td><td>8.66 9.64</td><td>0.00 1.21</td></tr><tr><td>ZS+CoT</td><td>0.95</td><td>5.08</td><td>0.06</td><td>12.53</td><td>7.86</td><td>0.06</td></tr><tr><td>ZS+CoT+SYS</td><td>1.23</td><td></td><td></td><td>12.89</td><td>7.34</td><td>1.09</td></tr><tr><td></td><td></td><td>5.46</td><td>0.16</td><td></td><td></td><td></td></tr><tr><td>ZS+ToT</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>FS</td><td>-</td><td>-</td><td></td><td>5.34</td><td>7.18</td><td>0.00</td></tr><tr><td>FS+SYS</td><td>-</td><td>=</td><td>-</td><td>3.18</td><td>7.18</td><td>0.00</td></tr><tr><td>FS+CoT</td><td>-</td><td></td><td></td><td>3.78</td><td>7.84</td><td>0.00</td></tr><tr><td>FS+SYS+CoT</td><td>-</td><td></td><td>-</td><td>3.25</td><td>6.32</td><td>0.00</td></tr><tr><td>FS+ToT</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td rowspan="10">LLAMA-2 (70b)</td><td>ZS ZS+SYS</td><td>0.10 0.16</td><td>4.96 5.88</td><td>0.00 2.10</td><td>6.47 9.72</td><td>8.14 9.60</td><td>5.57 0.36</td></tr><tr><td>ZS+CoT</td><td>0.91</td><td>5.05</td><td>0.46</td><td>13.73</td><td>7.51</td><td>1.24</td></tr><tr><td>ZS+CoT+SYS</td><td>1.69</td><td>5.63</td><td>0.04</td><td>14.34</td><td>8.50</td><td>3.23</td></tr><tr><td>ZS+ToT</td><td>-</td><td></td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td></td><td></td><td>-</td><td></td><td></td><td></td><td></td></tr><tr><td>FS</td><td>0.02</td><td>4.04</td><td>0.00</td><td>4.82</td><td>7.88</td><td>0.53</td></tr><tr><td>FS+SYS</td><td>0.08</td><td>4.81</td><td>0.01 0.00</td><td>8.71 4.62</td><td>8.85 8.63</td><td>3.13 2.03</td></tr><tr><td>FS+CoT</td><td>0.08</td><td>3.17</td><td></td><td></td><td></td><td></td></tr><tr><td>FS+SYS+CoT</td><td>0.16</td><td>3.40</td><td>0.00</td><td>5.54</td><td>8.22</td><td>0.00</td></tr><tr><td>FS+ToT</td><td>-</td><td>-</td><td></td><td>-</td><td>-</td></table>

Text relevance is a crucial metric, highlighting the relationship between two sentences and ensuring that a generated answer aligns with the task at hand. Classical metrics like BLEU and ROUGE-L measure the shared sequences between pairs of sentences: BLEU focuses on the n-gram overlap, while ROUGE-L captures the lengthiest common sequence. CIDEr refines the ROUGE-L metric by accounting for synonyms, word frequency, and scene graphs. We evaluated short-answer questions (with unique answers) generated by GPT-3.5, GPT-4, PaLM-2, and LLAMA-2 (13b and 70b) using the BLEU, ROUGE-L, and CIDEr metrics. Our collective findings are presented in Table 5. Interestingly, PaLM 2 displayed notably higher scores compared to other models but exhibited low accuracy, as seen in Table 3. Delving into the errors of PaLM 2, we discerned that, while it can provide accurate descriptions of specific concepts, it often muddles the logical connections between these concepts and redundantly reiterates irrelevant ones. An illustrative error from PaLM 2 is showcased in Figure 6, where the model erroneously repeats certain concepts. However, this repetition ironically leads to heightened text relevance scores. This observation underscores a limitation inherent in using text relevance metrics for evaluating LLMs.

![](images/4965a83acce484f6791595a93f7b96a3ffc7668a7e898979b1016be331af79e9.jpg)  
Figure 6: Example of wrong answer generated by PaLM 2. It is obvious that PaLM 2 repeat some wrong concept many times, but this will significantly increase the relevance between ground truth and the generated answer.

![](images/21371dba1abe1427537b4bd11afcd14feb33335918a6967d10b3e89764fdf45f.jpg)  
Figure 7: An example of short answer error in GPT-3.5, where the answer of GPT-3.5 cannot align the question, indicating the lack of logical decomposition and analysis, identification of assumptions, and logical reasoning skills.

## A.2 ERROR SAMPLES

We provide some error samples generated by GPT-3.5 in Figure 7 and Figure 8 for a better understanding of the error reason in Section 4.2.

## A.3 PROMPT TEMPLATE

We designed specific prompts for each type of question, and we summarized those prompts in this section. Figure 9 shows the system prompt, Figure 10 shows the prompt template for multiple choice questions, Figure 11 shows the prompt template for the short answer, and Figure 12 shows the prompt template for math questions. {input} is the place for input questions, {thought} denotes the middle-process prompt used for CoT. We use a two-stage method for short answer questions, in which the thought is generated by the LLM itself, and a format template for multiple choice and math questions. Specifically in math, we put the problem-solving process into the CoT prompt ({process}) as the "thought". Note that the prompts listed here are all zero-shot prompts, and the few-shot prompt is based on the zero-shot by further adding some example questions.

![](images/2a9fca57ad33ebdd438d81f3744116c7088e5cca14b1b8844148a98fbb99d866.jpg)

Figure 8: An example of a math error in GPT-3.5, where GPT-3.5 cannot understand the principles of language distribution and frequency, indicating the lack of logical decomposition and analysis, problem deduction, and abstract reasoning skills.  
![](images/827713e811ad149405dd1c9919f5279164ac27eb16d2c9699cfef2388f9397d6.jpg)  
Figure 9: System prompt for multiple choice, short answer, and math questions.

## B USER INTERFACE

The original dataset has a lot of handwriting scripts. We, therefore, create a UI interface to transform those handwriting scripts to JSON format manually. Figure 13 shows the screenshot of our UI interface. To ensure the correctness of input questions, we developed a real-time preview window for annotators to revise their input.

## C COMPARISON BETWEEN PREVIOUS BENCHMARKS AND NLPBENCH

To clearly distinguish the difference between each benchmark, we summarized the characteristics of each benchmark in three dimensions: dataset composition, tested methods, and analysis methods. Table 6 shows the difference between each benchmark. Our dataset introduces the questions that require LLMs to answer with multi-turn communication and contains all types of questions that can test the LLMs’ ability comprehensively.

Prompt template for Multiple Choice Questions Prompt template for Multiple Choice Questions (with CoT)   
Answer the final multiple choice question. Answer the final multiple choice question. Your output must be only   
Your output must be only numbered, splitting by commas numbered, splitting by commas (e.g., 0,1,...) with no descriptions.   
Example Input:   
(e.g., 0,1,...) with no descriptions. ChatGPT is created by which of the following companies?   
Example Input: 0: Google   
ChatGPT is created by which of the following companies? 1: Meta   
O: Google 2: Microsoft   
1: Meta 4: Amazon   
3: OpenAI   
2: Microsoft Example Thought:   
4: Amazon ChatGPT is a large-scale transformer-based language model created by   
3: OpenAI OpenAI in 2022.   
Example Output: Example Output:   
3   
3   
Example Input:   
Example Input: This is the input question; choose the correct answer   
This is the input question; choose the "Correct answer." O: Correct answer   
O: Correct answer 1: Option 2   
1: Option answer 2: Corect  aver   
3: Option 4 This is a multiple choice question; the "correct answer" appears at index   
Example Output: 0 and 2.   
0,2 Example Output:   
Example Input: Exxamplee Iput:   
True or False: GPT-4 was created by OpenAI. True or False: GPT-4 was created by OpenAI.   
0: True 0: True   
1: False 1: False   
Example Output: Example Thorht: y penAI   
0 Example Output:   
Input (You need to answer this question): 0   
{input} Input (You need to answer this question):   
utput: utput: {iput}

Figure 10: Zero-shot prompt template for multiple choice questions.  
Prompt template for Short Answer Questions Prompt template for Short Answer Questions (with CoT)   
(Stage 1):   
Answer the following short answer question. Your answer should be   
no more than 150 words.   
Input (You need to answer this question):   
{input}   
Answer the following short answer question. Your answer   
Let's think step by step.   
should be no more than 150 words.   
Input (You need to answer this question):   
input} Answer the following short answer question. Your answer should be   
Output: Io mre than 150 ors qi:   
{put}   
Your thought:   
Output:  
Figure 11: Zero-shot prompt template for short answer questions. Note that we use a two-stage method to generate the middle process for CoT.

![](images/479ccfafaea9599b9d8d1005f74df8946308c58c27b4a26daaa0f8ac83d7f343.jpg)  
Figure 12: Zero-shot prompt template for math questions. We input the middle process as the "thought" for CoT.

![](images/10cff72c886b91798ba2fa377935a05503837c6e8d40620378c78c6055455f21.jpg)  
Figure 13: The UI design of data processing and annotation.

Table 6: Comparison of NLPBench with other benchmarks. “Level” represents the grade level of problems. “w/ Solution” represents whether problems contain detailed solutions. “Type” represents what format most problems of the dataset use. “AP” denotes whether the benchmark uses the advanced prompting strategies, “MC” denotes multiple-choice format, “MT” denotes the question requires answer in multi-turn communication, and “Free” denotes free-response format. “Human” indicates whether the analysis process employs a human annotation process. “Auto” represents whether the analysis process uses an automatic annotation process.

<table><tr><td rowspan="2">Benchmark</td><td colspan="3">Dataset</td><td colspan="4">Experiment</td><td colspan="2">Analysis</td></tr><tr><td>Level</td><td>w/ Solution</td><td>Type</td><td>ZS</td><td>FS</td><td>AP</td><td>MT</td><td>Human</td><td>Auto</td></tr><tr><td>ScienceQA (Lu et al., 2022)</td><td>Grade 1-12</td><td>Yes</td><td>MC</td><td>Yes</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>IconQA (Lu et al., 2021b)</td><td>Grade 1-12</td><td>No</td><td>MC</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>TabMwP (Lu et al., 2023a)</td><td>Grade 1-12</td><td>Yes</td><td>Free</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>GSM8K (Cobbe et al., 2021)</td><td>Grade 1-12</td><td>Yes</td><td>Free</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>MATH (Hendrycks et al., 2021)</td><td>High School</td><td>Yes</td><td>Free</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>LILA (Mishra et al., 2022)</td><td>High School</td><td>Yes</td><td>Free</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>MNLU (Hendrycks et al., 2020)</td><td>High School &amp; College</td><td>No</td><td>MC</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>CEval (Huang et al., 2023)</td><td>High School &amp; College</td><td>No</td><td>MC</td><td>No</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>AGIEval (Zhong et al., 2023)</td><td>High School &amp; College</td><td>No</td><td>MC</td><td>Yes</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>TheroemQA (Chen et al., 2023)</td><td>College</td><td>No</td><td>Free</td><td>No</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>SciBench (Wang et al., 2023)</td><td>College</td><td>Yes</td><td>Free</td><td>Yes</td><td>Yes</td><td>Yes</td><td>No</td><td>Yes</td><td>Yes</td></tr><tr><td>NLPBench</td><td>College</td><td>Yes</td><td>Free &amp; MC</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td></tr></table>
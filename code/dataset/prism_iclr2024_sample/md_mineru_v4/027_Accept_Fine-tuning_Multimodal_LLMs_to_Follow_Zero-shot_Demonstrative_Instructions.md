# FINE-TUNING MULTIMODAL LLMS TO FOLLOW ZERO-SHOT DEMONSTRATIVE INSTRUCTIONS

Juncheng Li1, 2∗ Kaihang Pan1∗ Zhiqi Ge1∗ Minghe Gao1∗ Wei Ji2 Wenqiao Zhang1 Tat-Seng Chua2 Siliang Tang1† Hanwang Zhang3 Yueting Zhuang1†

1Zhejiang University, 2National University of Singapore, 3Nanyang Technological University

## ABSTRACT

Recent advancements in Multimodal Large Language Models (MLLMs) have been utilizing Visual Prompt Generators (VPGs) to convert visual features into tokens that LLMs can recognize. This is achieved by training the VPGs on millions of image-caption pairs, where the VPG-generated tokens of images are fed into a frozen LLM to generate the corresponding captions. However, this image-captioning based training objective inherently biases the VPG to concentrate solely on the primary visual contents sufficient for caption generation, often neglecting other visual details. This shortcoming results in MLLMs’ underperformance in comprehending demonstrative instructions consisting of multiple, interleaved, and multimodal instructions that demonstrate the required context to complete a task. To address this issue, we introduce a generic and lightweight Visual Prompt Generator Complete module (VPG-C), which can infer and complete the missing details essential for comprehending demonstrative instructions. Further, we propose a synthetic discriminative training strategy to fine-tune VPG-C, eliminating the need for supervised demonstrative instructions. As for evaluation, we build DEMON, a comprehensive benchmark for demonstrative instruction understanding. Synthetically trained with the proposed strategy, VPG-C achieves significantly stronger zero-shot performance across all tasks of DEMON. Further evaluation on the MME and OwlEval benchmarks also demonstrate the superiority of VPG-C. The code and models are available at https://github.com/DCDmllm/Cheetah.

## 1 INTRODUCTION

Recent advances in Multimodal Large Language Models (MLLMs) (Li et al., 2023c; Liu et al., 2023; Zhu et al., 2023a) have exhibited promising capabilities in processing single-image instructions, such as producing detailed image descriptions and answering questions about the image. However, they fall short in demonstrative instructions consisting of multiple, interleaved, and multimodal instructions that demonstrate the required context to complete a task. For instance, the instruction in Figure 1 contains interleaved visual and textual context, requiring the model to determine the authenticity of the milk in the second image based on the official image provided in the first.

An MLLM should at least have the following two capabilities to comprehend demonstrative instructions effectively:

1) Not just the primary subject: Beyond focusing on the primary visual content, it should be able to meticulously discern the details within the demonstrations. These details, complementing the primary content, play a crucial role in semantically connecting the instructions. A case in point is Figure 1, wherein accurate discernment relies on recognizing the logo detail on a milk carton.

2) Reasoning-aware details: How to decide what details are complementary to the reasoning? We expect that an MLLM may “think twice”, that is, given a preliminary reasoning using the primary contents, it would know what additional contents are needed as complementary details. For example, in Figure 1, after preliminary reasoning, the model should re-attend details such as the logo and brand name on the milk carton, thereby discerning its authenticity. However, to follow zero-shot demonstrative instructions, this “reasoning-aware” capability should be acquired without the need for supervised demonstrative instructions.

![](images/6eedf0b96467259398fd2f22413fbfbbb7f24cd0d89f66ed72834b7ee5589dfc.jpg)  
Figure 1: An example of InstructBLIP (Dai et al., 2023) and our MLLM enhanced by VPG-C.

Unfortunately, we find that the reason why existing MLLMs are not effective in demonstrative instructions is due to the lack of the above capabilities. More specifically, the crux lies in the Visual Prompt Generator (VPG) in MLLMs. VPG, such as Q-former (Li et al., 2023c) and Resampler (Alayrac et al., 2022), translates visual features into tokens recognizable by LLMs, and the translation is trained on millions of image-caption pairs by feeding the VPG-generated tokens of images into a frozen LLM which generates the corresponding captions. However, this image captioning training strategy inevitably introduces the inductive bias that VPG only focuses on the primary visual contents which are just enough for the captioning task, but tends to omit other visual details. For example in Figure 1, the averaged attention map of InstructBLIP (Dai et al., 2023) (Figure 1) shows a dominant focus on the primary contents, neglecting the logo detail, which is however the key to answering the question.

To this end, we propose a lightweight Visual Prompt Generator Complete module (VPG-C), which can infer and complete the missing details essential for comprehending demonstrative instructions (Section 2.1). As shown Figure 2, 1) VPG-C first derives the instructionspecific guidance by intercepting the intermediate LLM’s output of the primary contents extracted by a conventional VPG, and then

![](images/5c462e446a734516018f27f684feeb15d98a548dd128d4b38d97982ff5a12a4a.jpg)  
Figure 2: An overview of VPG-C.

2) guides the VPG to recover the missing visual residual details. Finally, 3) these residual details are then seamlessly reintegrated into the intermediate LLM’s layer via a skip connection. Together with the original intermediate output, VPG-C is expected to provide an improved comprehension of the demonstration instructions. Yet, VPG-C is not ready to follow zero-shot demonstrative instructions because the “Guide” step requires fine-tuning to specialize in missing detail recovery. Therefore, we propose a synthetic discriminative training strategy to fine-tune VPG-C, without the need for the expensive data collection of “detail-caption” pairs (Section 2.2).

To evaluate VPG-C and diagnose existing MLLMs, we build DEMON, a comprehensive benchmark for demonstrative instruction understanding, covering 31 diverse tasks across 7 categories, as shown in Figure 4 (Section 3). Systematic evaluation on DEMON confirms the limitation of existing MLLMs in demonstrative instructions. Without additional demonstrative instruction data, the lightweight VPG-C module can be effectively tuned by the synthetic training strategy in several hours with a single A100 GPU. While computation- and data- efficient, VPG-C significantly outperforms existing MLLMs on the DEMON benchmark. Zero-shot evaluation on other multimodal instruction benchmarks (Fu et al., 2023; Ye et al., 2023) also indicates considerable improvement by VPG-C.

## 2 METHOD

## 2.1 VISUAL PROMPT GENERATOR COMPLETE

As illustrated in Figure 2, VPG-C is built upon the frozen LLM (Vicuna-7B (Chiang et al., 2023)) and vision encoder (EVA-CLIP (Fang et al., 2023)). We adopt the widely used Q-Former from BLIP-

2 (Li et al., 2023c) as our visual prompt generator. VPG-C first uses the intermediate output of the LLM to infer instruction-specific guidance. This then assists the VPG in attending to the missing visual details from the images. By merging these residual details back via a skip connection, VPG-C achieves a thorough grasp of the demonstrative instruction.

Given a demonstrative instruction, we first adopt the Q-former to generate general visual prompts for each image in the instruction. Q-former takes a fixed number of K $\bar { K }$ query vectors to interact with image features by several cross-attention layers, and the output query representations are used as visual prompts, which are inserted into the position of their corresponding im ages in the instruction. We denote the input instruction for the language decoder as $\bar { \mathcal { H } } ^ { 0 } \ =$ $\{ \mathbf { \widetilde { h } } _ { 1 } ^ { 0 } , \mathbf { h } _ { 2 } ^ { 0 } , . . . , \mathbf { v } _ { 1 1 } ^ { 0 } , . . . , \mathbf { v } _ { 1 K } ^ { 0 } , . . . , \mathbf { h } _ { i } ^ { 0 } , . . . , \mathbf { v } _ { j 1 } ^ { 0 } , . . . , \mathbf { v } _ { j K } ^ { 0 } , . . . , \mathbf { h } _ { N } ^ { 0 } \}$ , where ${ \bf h } _ { i } ^ { 0 }$ represents the i-th text token and $\mathcal { V } _ { j } ^ { 0 } = \{ \mathbf { v } _ { j 1 } ^ { 0 } , . . . , \mathbf { v } _ { j K } ^ { 0 } \}$ represents the K visual prompts for the $j \mathrm { - t h }$ interleaved image. Taking the instruction as input to the L-layer language decoder, we then extract the hidden representation of the last input token $\mathbf { h } _ { N } ^ { L / 2 }$ at the $\scriptstyle { \frac { L } { 2 } } - \operatorname { t h }$ layer, which can fully perceive the whole multimodal context during the first $\begin{array} { l } { { \frac { L } { 2 } } } \end{array}$ layers and contains comprehensive instruction-aware semantics. Next, we infer the instruction-specific guidance g from $\mathbf { h } _ { N } ^ { L / 2 }$ via a linear projection layer: $\mathbf { g } = \mathbf { L i n e a r } ( \mathbf { h } _ { N } ^ { L / 2 } )$ .

After obtaining the instruction-specific guidance from the language decoder, we compose it with a new set of learnable queries: $\mathbf { g } + \boldsymbol { \mathcal { Q } }$ where $\mathcal { Q } \in \mathbf { R } ^ { K \times d }$ and $\mathbf { g }$ is added to each query of $\mathcal { Q } .$ Then, we reuse the same Q-former with the above conditionally generated queries to attend to residual visual details, thus obtaining the visual prompts $\overline { { \mathcal { V } } } _ { j } ~ = ~ \left\{ \overline { { \bf v } } _ { j 1 } , . . . , \overline { { \bf v } } _ { j K } \right\}$ for each image $j ,$ , which contains the complementary details missed by the original visual prompts. Finally, the transformed $\overline { { \mathcal { V } } } _ { j }$ is reintegrated with the corresponding original intermediate representations of $\mathcal { V } _ { j } ^ { L / 2 }$ , via skip connection: $\tilde { \mathcal { V } } _ { j } ^ { L / 2 } = \mathcal { V } _ { j } ^ { L / 2 } + \mathbf { L i n e a r } ( \overline { { \mathcal { V } } } _ { j } )$ , which is taken as the input to the $\begin{array} { r } { ( \frac { L } { 2 } + 1 ) } \end{array}$ -th layer.

Efficient training. Our $\mathrm { V P G - C }$ module is parameter-efficient as the Q-former is frozen and only a set of query embeddings and two linear projection layers need to be fine-tuned, which only account for $\mathbf { 0 . 0 9 \% ( \sim 6 . 3 M ) }$ of the entire model. To stabilize the training process (Zhang & Agrawala, 2023), we initialize the linear projection layers with zeros. Thus, at the early training stage, the input to the $\begin{array} { r } { ( \frac { L } { 2 } + 1 ) } \end{array}$ -th layer can be converted to: $\tilde { \mathcal { V } } _ { j } ^ { L / 2 } = \mathcal { V } _ { j } ^ { L / 2 }$ , which will not cause any influence on LLMs.

Analysis on inserting VPG-C in the intermediate layer $( \textstyle { \frac { L } { 2 } } ) \colon 1 )$ Guidance generation. Previous studies have shown that features provided by the intermediate layer may suffice to preliminarily understand the given input samples (Xin et al., 2020) and can serve as guidance hints to improve training (Romero et al., 2014). Thus, generating guidance in the intermediate layer allows the model to form a preliminary understanding of the given instruction. Generating guidance too early could be problematic, as the model might not have gathered sufficient contextual information to generate effective guidance. Conversely, generating guidance too late could result in the model’s attention being narrowly focused on what it perceives as the final answer, hindering its ability to guide the Q-former to extract relevant details from the images. Therefore, placing the guidance generation step in the intermediate layer strikes a balance. 2) Detail reintegration. Intermediate-layer reintegration of residual visual details preserves prior knowledge and allows subsequent layers to integrate new information effectively. Reintegrating residual details too early in the pipeline might overwrite important context, while reintegrating it too late could limit the impact on the model’s reasoning. Therefore, the intermediate layer offers a strategic position for residual details reintegration, enabling the model to reason effectively and arrive at the correct answers by leveraging the complemented visual residual details. We further provide quantitative analysis in Section 4.4.

## 2.2 SYNTHETIC DISCRIMINATIVE TRAINING STRATEGY

The proposed training strategy diagnoses the areas initially ignored by Q-former according to its cross-attention maps between the queries and the image features, and generates a synthetic image by performing several types of editing on the ignored areas. Then, an inter-image discriminative task is formulated as describing the subtle difference between the original and the synthetic images. Considering the edits are performed in the mostly ignored areas, $\mathrm { V P G - C }$ is challenged to recover the missing details to describe the difference. An overview is illustrated in Figure 3.

Editing target identification. The Q-former takes the queries to interact with frozen image features through several cross-attention layers and uses the output query representations as the visual prompts. Therefore, the cross-attention maps between queries and image features reflect the interest of queries. We average the cross-attention maps across all layers and all queries to obtain the global cross-attention map A, where the value $\mathcal { A } _ { i j }$ indicates the significance degree of the corresponding image feature by the original task-agnostic Q-former queries. After that, we employ the advanced vision foundation model (Kirillov et al., 2023) to obtain all the objects with segmentation masks in the image. Then, the significance degree of each object $\Phi ( o _ { i } )$ is computed based on the crossattention map A with RoIAlign (He et al., 2017), where we average the values of A within the mask $m _ { i }$ by interpolation. $\Phi ( o _ { i } )$ reflects what degree the visual features of object $o _ { i }$ is extracted by the Q-former. Thus, we select the most ignored objects based on the $\Phi ( o _ { i } )$ value.

![](images/986271517a08dccf2b7d54c2b981c2e5945fc30a592d78d0d7d4e596a69a9b53.jpg)  
Figure 3: Pipeline demonstration of synthetic discriminative training strategy for VPG-C.

Editing description generation. We define four types of editing: modifying objects, swapping objects, deleting objects, and adding objects. Given the selected object, we instruct ChatGPT (OpenAI, 2023a) to generate a suitable editing description that is in harmony with the context, where ChatGPT is prompted with the corresponding image caption and detailed object information (i.e., labels, positions). For adding objects, we only select BACKGROUND objects to add objects.

Synthetic image generation. After obtaining the editing description, we generate the synthetic image using a text-to-image latent diffusion model (i.e., Blended Diffusion (Avrahami et al., 2022)). Blended Diffusion performs local editing on the image according to the target object mask and the editing description, thus rendering the synthetic image. To ensure quality, we filter the edited images using CLIP similarity (Radford et al., 2021b).

Inter-image discriminative training. Given the original image and the synthetic image pair, along with the task instruction (“Describe the difference between the images”), the inter-image discriminative training task is defined as generating sentences to describe the subtle difference between the images. We convert the editing description to acquire the ground-truth sentences.

## 3 DEMON BENCHMARK

Data format. All task instances are transformed into a unified instruction-response form for zeroshot evaluation. Formally, each instance in DEMON consists of the following components:

• Task\_Instruction: provides a complete natural language definition of a given task, including the input/output format and the task objective.

• Task\_Instance: is a concrete instance of a given task that consists of demonstrative imagetext sequential context (e.g., visually-rich textbooks, specific questions about the context).

• Response: represents the target output in natural language for a given task instruction and task instance. For classification tasks, we convert the class labels as options into the instruction and ask the model to output the option index in natural language as the response.

Without any specific emphasis, we use the term “instruction” to refer to the combination of Task\_Instruction and Task\_Instance. For each task, we manually design 10 Task\_Instruction templates in natural language to increase the diversity.

Task collection and categorization. To comprehensively benchmark the demonstrative instruction following ability, we extensively gather a wide variety of multimodal datasets from different fields and scenarios. As illustrated in Figure 4, DEMON has three important properties: 1) Demonstrative vision-language context, all the instructions contain sequences of inter-related images and texts, such as storyboards with scripts, and textbooks with diagrams. 2) Diverse forms of complex instructions, the instructions range from designing panels for comics, to discovering differences between surveillance images, and to conversational embodied tasks. 3) Vast range of instructionfollowing scenarios, the benchmark covers multiple practical scenarios, including cartoons, industrial visuals, driving recordings, recipes, etc.

![](images/4ed4657ae3df90e0a5918708b95f686cd6bb15c50bbde8399e8315c49757945f.jpg)  
Figure 4: Demonstrations and task taxonomy of the proposed DEMON benchmark.

Evaluation protocols. Thanks to the unified task format of DEMON, all tasks can be evaluated in a zero-shot manner. For the open-ended generation tasks, we adopt ROUGE-L for evaluation. For the tasks that require the models to output option indexes, we take Accuracy as the evaluation metric. While well-formated options are provided, we empirically observe that many MLLMs struggle to strictly follow instructions to output the option indexes but generate free-form text. Thus, when models do not exactly output the required options, we match their outputs to one of the given options based on the TF-IDF distance, which we find is more robust than model-based methods (OpenAI, 2023a; Reimers & Gurevych, 2019). Since we explore a large number of tasks, we take a maximum of 500 instances per task for evaluation efficiency and exclude several datasets that are difficult to obtain and are subject to strict copyright restrictions (referred to as DEMON-Core). Meanwhile, we report the full version of the benchmark to facilitate future research on large-scale multimodal instruction tuning (referred to as DEMON-Full). Unless specifically stated, we use DEMON to refer to DEMON-Core in the following.

Table 1: Detailed statistics of DEMON benchmark.
<table><tr><td></td><td>Tasks</td><td>Scenarios</td><td>Images</td><td>Instructions</td><td>Avg. Images / Instruction Avg. Words / Instruction</td><td></td></tr><tr><td>DEMON-Core</td><td>29</td><td>19</td><td>62.81K</td><td>18.18K</td><td>3.46</td><td>92.69</td></tr><tr><td>DEMON-Full</td><td>31</td><td>20</td><td>1.77M</td><td>477.72K</td><td>3.70</td><td>97.58</td></tr></table>

Benchmark analysis. Table 1 details the statistics. DEMON benchmark covers 31 tasks of 7 categories across 20 scenarios. In total, DEMON-Full includes 477.72K instruction-response pairs, serving as a large-scale benchmark for demonstrative instruction following. On average, each instruction contains 3.70 images and 97.58 words. Please refer to Appendix B for more details.

Table 2: Average results of zero-shot evaluation on each task category of DEMON Benchmark.
<table><tr><td></td><td>Multimodal Dialogue</td><td>Visual Storytelling</td><td>Visual Relation Inference</td><td>Multimodal Cloze</td><td>Knowledge Grounded QA</td><td>Text-Rich Images QA</td><td>Multi-Image Reasoning</td></tr><tr><td>BLIP-2 (Li et al., 2023c)</td><td>26.12</td><td>21.31</td><td>10.67</td><td>17.94</td><td>39.23</td><td>33.53</td><td>39.65</td></tr><tr><td>InstructBLIP (Dai et al., 2023)</td><td>33.58</td><td>24.41</td><td>11.49</td><td>21.20</td><td>47.40</td><td>44.40</td><td>48.55</td></tr><tr><td>LLaMA-Adapter V2 (Gao et al., 2023)</td><td>14.22</td><td>17.57</td><td>13.51</td><td>18.00</td><td>44.80</td><td>32.00</td><td>44.03</td></tr><tr><td>LLaVA (Liu et al., 2023)</td><td>7.79</td><td>10.70</td><td>8.27</td><td>15.85</td><td>36.20</td><td>28.33</td><td>41.53</td></tr><tr><td>MiniGPT-4 (Zhu et al., 2023a)</td><td>13.69</td><td>17.07</td><td>7.95</td><td>16.60</td><td>30.27</td><td>26.40</td><td>43.50</td></tr><tr><td>mPLUG-Owl (Ye et al., 2023)</td><td>12.67</td><td>19.33</td><td>5.40</td><td>16.25</td><td>33.27</td><td>32.47</td><td>42.50</td></tr><tr><td>OpenFlamingo (Awadalla et al., 2023)</td><td>16.88</td><td>24.22</td><td>13.85</td><td>21.65</td><td>32.00</td><td>30.60</td><td>41.63</td></tr><tr><td>Otter (Li et al., 2023a)</td><td>15.37</td><td>15.57</td><td>11.39</td><td>16.00</td><td>41.67</td><td>27.73</td><td>43.85</td></tr><tr><td>VPG-C</td><td>37.50</td><td>25.20</td><td>25.90</td><td>22.15</td><td>48.60</td><td>44.93</td><td>50.28</td></tr></table>

## 4 EXPERIMENTS

## 4.1 ZERO-SHOT EVALUATION ON DEMON BENCHMARK

Comparison with advanced MLLMs. In this section, we conduct comprehensive evaluation of our VPG-C and the recent advanced MLLMs on the proposed DEMON benchmark. For all methods, we choose versions with parameter sizes less than 10B. Please refer to Appendix D, F for details. The average results of each task category are summarized in Table 2, which indicates the following.

• VPG-C consistently outperforms existing models by a large margin across all categories, which demonstrates the stronger generalizability to follow such complicated demonstrative instructions.

• While previous works mainly fine-tune on massive multimodal instruction data, VPG-C still achieves the highest performance using synthetic training data with much lower computation cost. This validates the effectiveness of the proposed VPG-C module and its synthetic training strategy.

• Compared with previous works that fine-tune the large-scale language decoder or visual encoder (i.e., LLaVA, mPLUG-Owl), our model only tunes the lightweight VPG-C module with 6.3M parameters and achieves significant performance gain.

• VPG-C exhibits significant superiority in several challenging tasks. For instance, VPG-C surpasses SOTA methods by 3.92% on multimodal dialogue, which requires models to effectively associate the interleaved images mentioned in different turns of the dialogue.

Innovative findings. The extensive evaluation on DEMON benchmark reveals several key findings.

• Poor performance on demonstrative instructions. While several models (e.g., OpenFlamingo, Otter, mPLUG-owl) have been trained on interleaved vision-language data, such as mmc4 (Zhu et al., 2023b), they still struggle to perform well on the demonstraive instructions. We suppose that while mmc4 contains sequences of interleaved images as context, the web-crawled images are often weakly related. In contrast, the images and text in demonstrative instructions are highly related, requiring models to deeply associate them to comprehend the task intents.

• Limited instruction following ability. Despite existing vision-language models leveraging stateof-the-art LLMs, which have demonstrated impressive ability in following language instructions, this competence seems to falter when dealing with complex multimodal instructions. For instance, when tasked with selecting the correct answer from a choice list given the context of images and texts, we observed some models inclining more towards describing the contents of the images instead of addressing the posed questions. This is perceived as a deficiency in the image-text alignment training process, to which we attribute the discrepancy.

• Failing to process image-choice questions. When dealing with multimodal cloze tasks, all models are limited to processing instructions that involve images as options. We hope future work to utilize the new benchmark to make progress on this type of demonstrative instructions.

## 4.2 ZERO-SHOT EVALUATION ON MME BENCHMARK

We evaluate our VPG-C on the concurrently proposed MME benchmark (Fu et al., 2023) to further illustrate its strong generalizability to follow a diverse range of single-image instructions. MME benchmark measures both perception and cognition abilities on a total of 14 subtasks. We report the averaged results of perception tasks and cognition tasks in Table 3, respectively. While we do not use massive multimodal instruction data to fine-tune VPG-C, VPG-C still achieves superior performance, compared with the supervised instruction-tuned models. This indicates our method effectively overcomes the inherent limitation of VPGs and the completed residual details are also essential for single-image instructions. Please refer to Appendix E for detailed results.

Table 3: Zero-shot evaluation of perception and cognition abilities on MME benchmark.
<table><tr><td></td><td>BLIP-2</td><td>InstructBLIP</td><td>LA-V2</td><td>LLaVA</td><td>MiniGPT-4</td><td>mPLUG-Owl</td><td>Otter</td><td>VPG-C</td></tr><tr><td>Perception</td><td>1293.84</td><td>1212.82</td><td>972.67</td><td>502.82</td><td>866.57</td><td>967.34</td><td>1292.26</td><td>1299.24</td></tr><tr><td>Cognition</td><td>290.00</td><td>291.79</td><td>248.93</td><td>214.64</td><td>292.14</td><td>276.07</td><td>306.43</td><td>321.07</td></tr></table>

## 4.3 HUMAN EVALUATION ON GENERAL-PURPOSE LANGUAGE GENERATION

We further conduct human evaluation on the OwlEval benchmark (Ye et al., 2023), which contains 82 openended questions including advertisement and poem creation, diagram and flowchart comprehension, and teaching, etc. Specifically, we recruit 8 well-educated people to rank the randomly shuffled responses from VPG-C, MiniGPT-4, mPLUG-Owl, OpenFlamingo, and Instruct-BLIP. The scores range from 1 to 5 (5 means best) and are allowed to be equal for comparable instances. As shown in Figure 5, VPG-C also demonstrates better open-ended language generation ability in various practical cases.

![](images/17ffd945e72e6a66956bf072c0808c1bbcc1a422a5a749edb2baca7dcc8e7f1d.jpg)  
Figure 5: Human evaluation.

## 4.4 IN-DEPTH ANALYSIS

Effectiveness of individual components. We investigate the effectiveness of each component in Table 4. We start with the backbone model that uses the Q-former to generate visual prompts. 1) Instead of applying VPG-C to capture missing details, we first attempt a simple heuristic-based method that directly extracts the less attended visual features according to the cross-attention maps of Q-former and reintegrates them to the intermediate layer of the LLM as ours. We fine-tune a linear layer before reintegrating with 0.5 million image-caption pairs. The results of Row 2 show that such a sample heuristic can bring some improvement. This validates the importance of re-extracting missing visual features from images for comprehending demonstrative instructions. 2) Then, we replace it with VPG-C and train it only using the image-caption pairs without synthetic training. The results of Row 3 demonstrate that VPG-C can more accurately complete the required missing details by leveraging the intermediate inference results of the LLM. 3) However, solely using common image-caption data can not fully unleash the power of VPG-C. Comparing Row 3 and Row 4, we observe a significant improvement for all tasks, indicating that the proposed synthetic discriminative training strategy can methodically empower VPG-C to extract missing visual details.

VPG-C can better guide VPGs. Since InstructBLIP can perform conditional visual feature extraction, we implement a variant version that concatenates its initially generated answer with the instruction as condition to re-extract features. The initial generated answer serves as an additional heuristic from the LLM for guiding feature extraction. Then, the newly extracted visual prompts are used to re-generate answers. For a fair comparison, we provide a zero-shot version (Row 5) and a fine-tuned version (Row 6) using synthetic training as ours. As shown in Table 4, directly using synthetic data and inferred answers as heuristic conditions fails to yield a notable improvement. In contrast, VPG-C can better guide the VPG to complete the missing visual details by intercepting the intermediate representations of the LLM. Further, VPG-C is more computation-efficient as it only requires one full forward pass of the LLM, while the InstructBLIP variants require twice.

VPG-C works well on various language backbones. Table 4 also validates that our approach can well cooperate with language backbones of different families (LLaMA2) and sizes (Vicuna-13B).

VPG-C can be implemented with very simple VPG. As a generic method, VPG-C can be implemented with different VPGs. Beyond the widely used Q-former that is composed of multiple Transformer blocks, we further probe the effectiveness of VPG-C with a simpler VPG, i.e., Linear Projection, as used in LLaVA (please refer to Appendix C for implementation details). Table 4 Row 7 shows promising results. VPG-C can also significantly bolster the performance of a simple linear VPG, verifying the transferability of VPG-C. It is promising to adapt our generic VPG-C and corresponding low-resource synthetic training strategy to different VPGs in the future.

Table 4: Ablation results on DEMON Benchmark.
<table><tr><td></td><td></td><td>Multimodal Dialogue</td><td>Visual Storytelling</td><td>Visual Relation Inference</td><td>Multimodal Cloze</td><td>Knowledge Grounded QA</td><td>Text-Rich Images QA</td><td>Multi-Image Reasoning</td></tr><tr><td>1</td><td>Backbone</td><td>25.65</td><td>21.72</td><td>9.33</td><td>17.06</td><td>37.21</td><td>32.42</td><td>41.30</td></tr><tr><td>2</td><td>+Heuristic Details</td><td>28.13</td><td>22.76</td><td>12.69</td><td>18.81</td><td>38.75</td><td>34.14</td><td>43.26</td></tr><tr><td>3</td><td>+VPG-C</td><td>31.76</td><td>23.62</td><td>19.12</td><td>20.09</td><td>42.53</td><td>39.68</td><td>46.71</td></tr><tr><td>4</td><td>+Synthetic Training</td><td>37.50</td><td>25.20</td><td>25.90</td><td>22.15</td><td>48.60</td><td>44.93</td><td>50.28</td></tr><tr><td></td><td>InstructBLIP</td><td>33.58</td><td>24.41</td><td>11.48</td><td>21.20</td><td>47.40</td><td>44.40</td><td>48.55</td></tr><tr><td>5</td><td>+Answer Condition</td><td>32.10</td><td>23.76</td><td>11.02</td><td>21.86</td><td>47.94</td><td>42.08</td><td>49.01</td></tr><tr><td>6</td><td>+Synthetic Training</td><td>31.76</td><td>24.32</td><td>12.78</td><td>19.87</td><td>46.58</td><td>42.36</td><td>49.82</td></tr><tr><td></td><td>LLaVA</td><td>7.79</td><td>10.70</td><td>8.27</td><td>15.85</td><td>36.20</td><td>28.33</td><td>41.53</td></tr><tr><td>7</td><td>Linear VPG</td><td>16.43</td><td>19.48</td><td>14.75</td><td>18.54</td><td>41.32</td><td>36.87</td><td>46.02</td></tr><tr><td>8</td><td>VPG-C-LLaMA2-7B</td><td>42.70</td><td>24.76</td><td>25.50</td><td>22.95</td><td>51.00</td><td>44.93</td><td>48.68</td></tr><tr><td>9</td><td>VPG-C-Vicuna-13B</td><td>38.14</td><td>26.59</td><td>27.15</td><td>27.15</td><td>52.93</td><td>49.33</td><td>53.65</td></tr></table>

Analysis on the inserted layer of VPG-C. We investigate the impact of inserting VPG-C into different layers of LLMs. We report the averaged accuracy for multiplechoice tasks and averaged ROUGE-L for open-ended generation tasks in Figure 6. We observe that the performance is low when we insert VPG-C too early (i.e., 4, 8) as the model might not have gathered sufficient contextual information to generate effective guidance. Meanwhile, inserting VPG-C too late (i.e., 24, 28) degenerates the performance. We speculate this is due to the generated guidance being too concentrated and there not being enough layers to integrate the residual details.

![](images/0fe6838dc84166f8febdf053fc4857a1d9e5165ba6e0e54084b84cbaa47e8341.jpg)  
Figure 6: Performance on DEMON with different insertion layers.

Synthetic training is data-efficient. Since our proposed synthetic training strategy can construct challenging discriminative tasks in a targeted manner, enhancing VPG-C’s ability to complete missing details, it avoids the need for a large amount of supervised demonstrative instruction data. We further investigate the impact of different numbers of synthetic training data. As illustrated in Table 5, the performance keeps increasing when the number of data is increased from 16K to 64K. Beyond this, escalating the data count from 64K

Table 5: Efficiency analysis of synthetic training.
<table><tr><td></td><td>Accuracy</td><td>ROUGE-L</td></tr><tr><td>16K</td><td>38.93</td><td>25.67</td></tr><tr><td>32K</td><td>39.62</td><td>27.38</td></tr><tr><td>48K</td><td>40.45</td><td>28.81</td></tr><tr><td>64K</td><td>41.49</td><td>29.53</td></tr><tr><td>80K</td><td>41.62</td><td>29.73</td></tr><tr><td>96K</td><td>40.12</td><td>28.31</td></tr></table>

to 80K yields only marginal enhancement. Further amplification of data eventually triggers a performance dip as excessive data leads to model overfitting to the synthetic training task.

Image order sensitivity. The order of interleaved images in demonstrative instructions is pivotal for the compositional semantics of the instruction. Intuitively, altering the order of images within a demonstrative instruction can significantly shift its semantics. Consequently, variations in model performance can reveal the model’s sensitivity to the instruction semantics. An ideal model should keenly capture changes in instruction semantics. Therefore, we visualize the performance variations of models by randomly shuffling the order of interleaved images within the demonstrative instructions. Ac-

![](images/7eaea6a990c2222d3b487983c8eb74977872ea83df39b523662ab3e80ccc2421.jpg)  
Figure 7: Analysis on image order sensitivity.

cording to Figure 7, we surprisingly find that SOTA models are less sensitive to the image order. In contrast, VPG-C can keenly capture the semantic changes caused by the shuffled image order. Particularly, our performance varies dramatically in multimodal dialogue, as the order of images within these tasks is closely intertwined with the dialogue content.

Qualitative examples. As illustrated in Figure 8, VPG-C demonstrates strong abilities to perform reasoning over complicated demonstrative instructions. For instance, in (a), VPG-C can keenly identify the connections between the images and thereby infer the reason that causes this unusual phenomenon. In (b, c), VPG-C exhibits the ability to comprehend absurd objects through multimodal conversations with humans. In (d, e), VPG-C can reasonably infer the relations among the images and understand the metaphorical implications they want to convey. In Appendix G, we provide more practical examples as well as comparisons with other MLLMs, where we find that baseline models fail to correctly associate multiple images and comprehend demonstrative context.

![](images/af8c6cbc147c5685011641c9e7959bccff4ed56932373b8223ebd59210d9f3bc.jpg)  
Figure 8: Qualitative examples generated by our VPG-C-Vicuna-7B model.

## 5 RELATED WORK

MLLMs (Yin et al., 2023) aim to serve as a general-purpose assistant to perform various visionlanguage tasks by free-text generation. Flamingo (Alayrac et al., 2022) and BLIP-2 (Li et al., 2023c) bridge LLMs with powerful pre-trained visual encoders and demonstrate strong zero-shot ability by aligning visual features with LLMs. Follow-up works of LLaVA (Liu et al., 2023), MiniGPT-4 (Zhu et al., 2023a), InstructBLIP (Dai et al., 2023), Hallucidoctor (Yu et al., 2024), mPLUG-Owl (Ye et al., 2023) propose to fine-tune MLLMs with multimodal instruction tuning data. To effectively benchmark the recent progress in MLLMs, concurrent works of LVLM-eHub (Xu et al., 2023) and MME Benchmark (Fu et al., 2023) are proposed, while they mainly focus on instructions that only involve a single image with limited instruction diversity. In this paper, we propose the first demonstrative instruction-following benchmark, covering various tasks of diverse scenarios. Further, we propose a lightweight and generic VPG-C module to address the inherent limitation of current VPGs. Our VPG-C is efficiently tuned by our synthetic discriminative training strategy, which demonstrates powerful potentials of text-to-image diffusion models (He et al., 2022; Lin et al., 2023; Prabhu et al., 2023; Bansal & Grover, 2023; Yu et al., 2023b) to facilitate vision-language understanding (Radford et al., 2021b; Jia et al., 2021; Li et al., 2022b).

## 6 CONCLUSION

In this paper, we propose VPG-C, a generic and parameter-efficient approach that infers and completes the missing visual details for MLLMs to comprehend demonstrative instructions with interleaved multimodal context. Meanwhile, we present a synthetic discriminative training strategy to fine-tune VPG-C, eliminating the need for supervised demonstrative instruction data. To foster the research on demonstrative instruction understanding, we build DEMON, a comprehensive benchmark for multimodal large language models, consisting of 31 tasks with complicated vision-language demonstrative context, covering a wide range of scenarios. Through synthetic training, VPG-C showcases notable zero-shot performance on the DEMON benchmark. Its superior performance on other established benchmarks like MME and OwlEval further underscores its effectiveness.

Acknowledgment. This work was supported by the NSFC (No. 62272411), Key Research and Development Projects in Zhejiang Province (No. 2024C01106), the National Key Research and Development Project of China (2018AAA0101900), the Tencent WeChat Rhino-Bird Special Research Program (Tencent WXG-FR-2023-10), and Research funding from FinVolution Group.

## REFERENCES

Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc, Antoine Miech, Iain Barr, Yana Hasson, Karel Lenc, Arthur Mensch, Katherine Millican, Malcolm Reynolds, et al. Flamingo: a visual language model for few-shot learning. Advances in Neural Information Processing Systems, 35:23716– 23736, 2022.

Stanislaw Antol, Aishwarya Agrawal, Jiasen Lu, Margaret Mitchell, Dhruv Batra, C Lawrence Zitnick, and Devi Parikh. Vqa: Visual question answering. In Proceedings of the IEEE international conference on computer vision, pp. 2425–2433, 2015.

Omri Avrahami, Dani Lischinski, and Ohad Fried. Blended diffusion for text-driven editing of natural images. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 18208–18218, 2022.

Anas Awadalla, Irena Gao, Joshua Gardner, Jack Hessel, Yusuf Hanafy, Wanrong Zhu, Kalyani Marathe, Yonatan Bitton, Samir Gadre, Jenia Jitsev, Simon Kornblith, Pang Wei Koh, Gabriel Ilharco, Mitchell Wortsman, and Ludwig Schmidt. Openflamingo, March 2023. URL https: //doi.org/10.5281/zenodo.7733589.

Haoping Bai, Shancong Mou, Tatiana Likhomanenko, Ramazan Gokberk Cinbis, Oncel Tuzel, Ping Huang, Jiulong Shan, Jianjun Shi, and Meng Cao. Vision datasets: A benchmark for vision-based industrial inspection. arXiv preprint arXiv:2306.07890, 2023.

Ankan Bansal, Yuting Zhang, and Rama Chellappa. Visual question answering on image sets. In Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part XXI 16, pp. 51–67. Springer, 2020.

Hritik Bansal and Aditya Grover. Leaving reality to imagination: Robust classification via generated datasets. arXiv preprint arXiv:2302.02503, 2023.

Nilavra Bhattacharya, Qing Li, and Danna Gurari. Why does a visual question have different answers? In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 4271–4280, 2019.

Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora, Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Giancarlo Baldan, and Oscar Beijbom. nuscenes: A multimodal dataset for autonomous driving. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 11621–11631, 2020.

Yingshan Chang, Mridu Narang, Hisami Suzuki, Guihong Cao, Jianfeng Gao, and Yonatan Bisk. Webqa: Multihop and multimodal qa. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 16495–16504, 2022.

Wei-Lin Chiang, Zhuohan Li, Zi Lin, Ying Sheng, Zhanghao Wu, Hao Zhang, Lianmin Zheng, Siyuan Zhuang, Yonghao Zhuang, Joseph E Gonzalez, et al. Vicuna: An open-source chatbot impressing gpt-4 with 90% chatgpt quality, 2023. URL https://vicuna.lmsys.org.

Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Eric Li, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, et al. Scaling instruction-finetuned language models. arXiv preprint arXiv:2210.11416, 2022.

Wenliang Dai, Junnan Li, Dongxu Li, Anthony Meng Huat Tiong, Junqi Zhao, Weisheng Wang, Boyang Li, Pascale Fung, and Steven Hoi. Instructblip: Towards general-purpose vision-language models with instruction tuning. arXiv preprint arXiv:2305.06500, 2023.

Yuxin Fang, Wen Wang, Binhui Xie, Quan Sun, Ledell Wu, Xinggang Wang, Tiejun Huang, Xinlong Wang, and Yue Cao. Eva: Exploring the limits of masked visual representation learning at scale. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 19358–19369, 2023.

Maxwell Forbes, Christine Kaeser-Chen, Piyush Sharma, and Serge Belongie. Neural naturalist: generating fine-grained image comparisons. arXiv preprint arXiv:1909.04101, 2019.

Chaoyou Fu, Peixian Chen, Yunhang Shen, Yulei Qin, Mengdan Zhang, Xu Lin, Zhenyu Qiu, Wei Lin, Jinrui Yang, Xiawu Zheng, et al. Mme: A comprehensive evaluation benchmark for multimodal large language models. arXiv preprint arXiv:2306.13394, 2023.

Peng Gao, Jiaming Han, Renrui Zhang, Ziyi Lin, Shijie Geng, Aojun Zhou, Wei Zhang, Pan Lu, Conghui He, Xiangyu Yue, et al. Llama-adapter v2: Parameter-efficient visual instruction model. arXiv preprint arXiv:2304.15010, 2023.

Tanmay Gupta, Dustin Schwenk, Ali Farhadi, Derek Hoiem, and Aniruddha Kembhavi. Imagine this! scripts to compositions to videos. In Proceedings of the European conference on computer vision (ECCV), pp. 598–613, 2018.

Xintong Han, Zuxuan Wu, Phoenix X Huang, Xiao Zhang, Menglong Zhu, Yuan Li, Yang Zhao, and Larry S Davis. Automatic spatially-aware fashion concept discovery. In Proceedings of the IEEE international conference on computer vision, pp. 1463–1471, 2017.

Darryl Hannan, Akshay Jain, and Mohit Bansal. Manymodalqa: Modality disambiguation and qa over diverse inputs. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 34, pp. 7879–7886, 2020.

Kaiming He, Georgia Gkioxari, Piotr Dollar, and Ross Girshick. Mask r-cnn. In ´ Proceedings of the IEEE international conference on computer vision, pp. 2961–2969, 2017.

Ruifei He, Shuyang Sun, Xin Yu, Chuhui Xue, Wenqing Zhang, Philip Torr, Song Bai, and Xiaojuan Qi. Is synthetic data from generative models ready for image recognition? arXiv preprint arXiv:2210.07574, 2022.

Mehrdad Hosseinzadeh and Yang Wang. Image change captioning by learning from an auxiliary task. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 2725–2734, 2021.

Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. Lora: Low-rank adaptation of large language models. arXiv preprint arXiv:2106.09685, 2021.

Ting-Hao Huang, Francis Ferraro, Nasrin Mostafazadeh, Ishan Misra, Aishwarya Agrawal, Jacob Devlin, Ross Girshick, Xiaodong He, Pushmeet Kohli, Dhruv Batra, et al. Visual storytelling. In Proceedings of the 2016 conference of the North American chapter of the association for computational linguistics: Human language technologies, pp. 1233–1239, 2016.

Phillip Isola, Joseph J Lim, and Edward H Adelson. Discovering states and transformations in image collections. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 1383–1391, 2015.

Mohit Iyyer, Varun Manjunatha, Anupam Guha, Yogarshi Vyas, Jordan Boyd-Graber, Hal Daume, and Larry S Davis. The amazing mysteries of the gutter: Drawing inferences between panels in comic book narratives. In Proceedings of the IEEE Conference on Computer Vision and Pattern recognition, pp. 7186–7195, 2017.

Harsh Jhamtani and Taylor Berg-Kirkpatrick. Learning to describe differences between pairs of similar images. arXiv preprint arXiv:1808.10584, 2018.

Chao Jia, Yinfei Yang, Ye Xia, Yi-Ting Chen, Zarana Parekh, Hieu Pham, Quoc Le, Yun-Hsuan Sung, Zhen Li, and Tom Duerig. Scaling up visual and vision-language representation learning with noisy text supervision. In International conference on machine learning, pp. 4904–4916. PMLR, 2021.

Aniruddha Kembhavi, Minjoon Seo, Dustin Schwenk, Jonghyun Choi, Ali Farhadi, and Hannaneh Hajishirzi. Are you smarter than a sixth grader? textbook question answering for multimodal machine comprehension. In Proceedings of the IEEE Conference on Computer Vision and Pattern recognition, pp. 4999–5007, 2017.

Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C Berg, Wan-Yen Lo, et al. Segment anything. arXiv preprint arXiv:2304.02643, 2023.

Bo Li, Yuanhan Zhang, Liangyu Chen, Jinghao Wang, Fanyi Pu, Jingkang Yang, Chunyuan Li, and Ziwei Liu. Mimic-it: Multi-modal in-context instruction tuning. arXiv preprint arXiv:2306.05425, 2023a.

Dongxu Li, Junnan Li, Hung Le, Guangsen Wang, Silvio Savarese, and Steven CH Hoi. Lavis: A library for language-vision intelligence. arXiv preprint arXiv:2209.09019, 2022a.

Juncheng Li, Xin Wang, Siliang Tang, Haizhou Shi, Fei Wu, Yueting Zhuang, and William Yang Wang. Unsupervised reinforcement learning of transferable meta-skills for embodied navigation. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 12123–12132, 2020.

Juncheng Li, Xin He, Longhui Wei, Long Qian, Linchao Zhu, Lingxi Xie, Yueting Zhuang, Qi Tian, and Siliang Tang. Fine-grained semantically aligned vision-language pre-training. Advances in neural information processing systems, 35:7290–7303, 2022b.

Juncheng Li, Junlin Xie, Long Qian, Linchao Zhu, Siliang Tang, Fei Wu, Yi Yang, Yueting Zhuang, and Xin Eric Wang. Compositional temporal grounding with structured variational cross-graph correspondence learning. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 3032–3041, 2022c.

Juncheng Li, Minghe Gao, Longhui Wei, Siliang Tang, Wenqiao Zhang, Mengze Li, Wei Ji, Qi Tian, Tat-Seng Chua, and Yueting Zhuang. Gradient-regulated meta-prompt learning for generalizable vision-language models. 2023b.

Junnan Li, Dongxu Li, Silvio Savarese, and Steven Hoi. Blip-2: Bootstrapping languageimage pre-training with frozen image encoders and large language models. arXiv preprint arXiv:2301.12597, 2023c.

Mengze Li, Tianbao Wang, Haoyu Zhang, Shengyu Zhang, Zhou Zhao, Jiaxu Miao, Wenqiao Zhang, Wenming Tan, Jin Wang, Peng Wang, et al. End-to-end modeling via information tree for oneshot natural language spatial video grounding. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 8707–8717, 2022d.

Mengze Li, Haoyu Zhang, Juncheng Li, Zhou Zhao, Wenqiao Zhang, Shengyu Zhang, Shiliang Pu, Yueting Zhuang, and Fei Wu. Unsupervised domain adaptation for video object grounding with cascaded debiasing learning. In Proceedings of the 31st ACM International Conference on Multimedia, pp. 3807–3816, 2023d.

Yitong Li, Zhe Gan, Yelong Shen, Jingjing Liu, Yu Cheng, Yuexin Wu, Lawrence Carin, David Carlson, and Jianfeng Gao. Storygan: A sequential conditional gan for story visualization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 6329–6338, 2019.

Yongqi Li, Wenjie Li, and Liqiang Nie. Mmcoqa: Conversational question answering over text, tables, and images. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 4220–4231, 2022e.

Shaobo Lin, Kun Wang, Xingyu Zeng, and Rui Zhao. Explore the power of synthetic data on few-shot object detection. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 638–647, 2023.

Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae Lee. Visual instruction tuning. arXiv preprint arXiv:2304.08485, 2023.

Adyasha Maharana, Darryl Hannan, and Mohit Bansal. Storydall-e: Adapting pretrained text-toimage transformers for story continuation. In Computer Vision–ECCV 2022: 17th European Conference, Tel Aviv, Israel, October 23–27, 2022, Proceedings, Part XXXVII, pp. 70–87. Springer, 2022.

Minesh Mathew, Dimosthenis Karatzas, and CV Jawahar. Docvqa: A dataset for vqa on document images. In Proceedings of the IEEE/CVF winter conference on applications of computer vision, pp. 2200–2209, 2021.

Anand Mishra, Shashank Shekhar, Ajeet Kumar Singh, and Anirban Chakraborty. Ocr-vqa: Visual question answering by reading text in images. In 2019 international conference on document analysis and recognition (ICDAR), pp. 947–952. IEEE, 2019.

OpenAI. Chatgpt: A language model for conversational ai. Technical report, OpenAI, 2023a. URL https://www.openai.com/research/chatgpt.

OpenAI. Gpt-4 technical report. arXiv:2303.08774, 2023b.

Viraj Prabhu, Sriram Yenamandra, Prithvijit Chattopadhyay, and Judy Hoffman. Lance: Stresstesting visual models by generating language-guided counterfactual images. arXiv preprint arXiv:2305.19164, 2023.

Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748–8763. PMLR, 2021a.

Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748–8763. PMLR, 2021b.

Hareesh Ravi, Kushal Kafle, Scott Cohen, Jonathan Brandt, and Mubbasir Kapadia. Aesop: Ab stract encoding of stories, objects, and pictures. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 2052–2063, 2021.

Nils Reimers and Iryna Gurevych. Sentence-BERT: Sentence embeddings using Siamese BERTnetworks. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), pp. 3982–3992, 2019.

Adriana Romero, Nicolas Ballas, Samira Ebrahimi Kahou, Antoine Chassang, Carlo Gatta, and Yoshua Bengio. Fitnets: Hints for thin deep nets. arXiv preprint arXiv:1412.6550, 2014.

Piyush Sharma, Nan Ding, Sebastian Goodman, and Radu Soricut. Conceptual captions: A cleaned, hypernymed, image alt-text dataset for automatic image captioning. In Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 2556–2565, 2018.

Mohit Shridhar, Jesse Thomason, Daniel Gordon, Yonatan Bisk, Winson Han, Roozbeh Mottaghi, Luke Zettlemoyer, and Dieter Fox. Alfred: A benchmark for interpreting grounded instructions for everyday tasks. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 10740–10749, 2020.

Alane Suhr, Stephanie Zhou, Ally Zhang, Iris Zhang, Huajun Bai, and Yoav Artzi. A corpus for reasoning about natural language grounded in photographs. arXiv preprint arXiv:1811.00491, 2018.

Alon Talmor, Ori Yoran, Amnon Catav, Dan Lahav, Yizhong Wang, Akari Asai, Gabriel Ilharco, Hannaneh Hajishirzi, and Jonathan Berant. Multimodalqa: Complex question answering over text, tables and images. arXiv preprint arXiv:2104.06039, 2021.

Hao Tan, Franck Dernoncourt, Zhe Lin, Trung Bui, and Mohit Bansal. Expressing visual relationships via language. arXiv preprint arXiv:1906.07689, 2019.

Ryota Tanaka, Kyosuke Nishida, Kosuke Nishida, Taku Hasegawa, Itsumi Saito, and Kuniko Saito. Slidevqa: A dataset for document visual question answering on multiple images. arXiv preprint arXiv:2301.04883, 2023.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothee´ Lacroix, Baptiste Roziere, Naman Goyal, Eric Hambro, Faisal Azhar, et al. Llama: Open and\` efficient foundation language models. arXiv:2302.13971, 2023a.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton Ferrer, Moya Chen, Guillem Cucurull, David Esiobu, Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller, Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony Hartshorn, Saghar Hosseini, Rui Hou, Hakan Inan, Marcin Kardas, Viktor Kerkez, Madian Khabsa, Isabel Kloumann, Artem Korenev, Punit Singh Koura, Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Diana Liskovich, Yinghai Lu, Yuning Mao, Xavier Martinet, Todor Mihaylov, Pushkar Mishra, Igor Molybog, Yixin Nie, Andrew Poulton, Jeremy Reizenstein, Rashi Rungta, Kalyan Saladi, Alan Schelten, Ruan Silva, Eric Michael Smith, Ranjan Subramanian, Xiaoqing Ellen Tan, Binh Tang, Ross Taylor, Adina Williams, Jian Xiang Kuan, Puxin Xu, Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan, Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, and Thomas Scialom. Llama 2: Open foundation and fine-tuned chat models. arXiv:2307.09288, 2023b.

Fei Xia, Amir R Zamir, Zhiyang He, Alexander Sax, Jitendra Malik, and Silvio Savarese. Gibson env: Real-world perception for embodied agents. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 9068–9079, 2018.

Ji Xin, Raphael Tang, Jaejun Lee, Yaoliang Yu, and Jimmy Lin. Deebert: Dynamic early exiting for accelerating bert inference. arXiv preprint arXiv:2004.12993, 2020.

Kelvin Xu, Jimmy Ba, Ryan Kiros, Kyunghyun Cho, Aaron Courville, Ruslan Salakhudinov, Rich Zemel, and Yoshua Bengio. Show, attend and tell: Neural image caption generation with visual attention. In International conference on machine learning, pp. 2048–2057. PMLR, 2015.

Peng Xu, Wenqi Shao, Kaipeng Zhang, Peng Gao, Shuo Liu, Meng Lei, Fanqing Meng, Siyuan Huang, Yu Qiao, and Ping Luo. Lvlm-ehub: A comprehensive evaluation benchmark for large vision-language models. arXiv preprint arXiv:2306.09265, 2023.

Semih Yagcioglu, Aykut Erdem, Erkut Erdem, and Nazli Ikizler-Cinbis. Recipeqa: A challenge dataset for multimodal comprehension of cooking recipes. arXiv preprint arXiv:1809.00812, 2018.

Qinghao Ye, Haiyang Xu, Guohai Xu, Jiabo Ye, Ming Yan, Yiyang Zhou, Junyang Wang, Anwen Hu, Pengcheng Shi, Yaya Shi, et al. mplug-owl: Modularization empowers large language models with multimodality. arXiv preprint arXiv:2304.14178, 2023.

Shukang Yin, Chaoyou Fu, Sirui Zhao, Ke Li, Xing Sun, Tong Xu, and Enhong Chen. A survey on multimodal large language models. arXiv preprint arXiv:2306.13549, 2023.

Qifan Yu, Juncheng Li, Yu Wu, Siliang Tang, Wei Ji, and Yueting Zhuang. Visually-prompted language model for fine-grained scene graph generation in an open world. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 21560–21571, 2023a.

Qifan Yu, Juncheng Li, Wentao Ye, Siliang Tang, and Yueting Zhuang. Interactive data synthesis for systematic vision adaptation via llms-aigcs collaboration. arXiv preprint arXiv:2305.12799, 2023b.

Qifan Yu, Juncheng Li, Longhui Wei, Liang Pang, Wentao Ye, Bosheng Qin, Siliang Tang, Qi Tian, and Yueting Zhuang. Hallucidoctor: Mitigating hallucinatory toxicity in visual instruction data. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.

Lvmin Zhang and Maneesh Agrawala. Adding conditional control to text-to-image diffusion models. arXiv preprint arXiv:2302.05543, 2023.

Wenqiao Zhang, Siliang Tang, Yanpeng Cao, Shiliang Pu, Fei Wu, and Yueting Zhuang. Frame augmented alternating attention network for video question answering. IEEE Transactions on Multimedia, 22(4):1032–1041, 2019.

Wenqiao Zhang, Haochen Shi, Jiannan Guo, Shengyu Zhang, Qingpeng Cai, Juncheng Li, Sihui Luo, and Yueting Zhuang. Magic: Multimodal relational graph adversarial inference for diverse and unpaired text-based image captioning. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 36, pp. 3335–3343, 2022.

Deyao Zhu, Jun Chen, Xiaoqian Shen, Xiang Li, and Mohamed Elhoseiny. Minigpt-4: Enhancing vision-language understanding with advanced large language models. arXiv preprint arXiv:2304.10592, 2023a.

Wanrong Zhu, Jack Hessel, Anas Awadalla, Samir Yitzhak Gadre, Jesse Dodge, Alex Fang, Youngjae Yu, Ludwig Schmidt, William Yang Wang, and Yejin Choi. Multimodal c4: An open, billionscale corpus of images interleaved with text. arXiv preprint arXiv:2304.06939, 2023b.

## A OVERVIEW

In this appendix, we present:

• Detailed information of the proposed DEMON benchmark (Section B).

• Implementation details of our VPG-C (Section C).

• Implementation details of existing MLLMs on the DEMON benchmark (Section D).

• Detailed zero-shot performance on MME benchmark (Section E).

• Detailed zero-shot performance on DEMON benchmark (Section F).

• Qualitative comparison with existing MLLMs (Section G).

## B BENCHMARK DETAILS

<table><tr><td>Task</td><td>Scenario</td><td>Dataset</td><td>Metirc</td></tr><tr><td>Multimodal Dialogue</td><td></td><td></td><td></td></tr><tr><td>Conversational Embodied Dialogue</td><td>Embodied</td><td>ALFRED (Shridhar et al., 2020)</td><td>ROUGE-L</td></tr><tr><td>Multimodal Dialogue</td><td>Conversation</td><td>MMCoQA (Li et al., 2022e)</td><td>ROUGE-L</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Visual Storytelling</td><td></td><td>AESOP (Ravi et al., 2021)</td><td>ROUGE-L</td></tr><tr><td>Animated Story Completion Animated Story Completion</td><td>Cartoon Cartoon</td><td>PororoSV (Li et al., 2019)</td><td>ROUGE-L</td></tr><tr><td>Animated Story Completion</td><td>Cartoon</td><td></td><td>ROUGE-L</td></tr><tr><td>Sequential Photo Storytelling</td><td></td><td>FlintstonesSV (Gupta et al., 2018)</td><td>ROUGE-L</td></tr><tr><td>Sequential Photo Storytelling</td><td>Album</td><td>VIST (Huang et al., 2016) DiDeMoSV (Maharana et al., 2022)</td><td></td></tr><tr><td>Visual Relation Inference</td><td>Cartoon</td><td></td><td>ROUGE-L</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Visual Change Captioning</td><td>Surveillance</td><td>Spot-the-Diff (Jhamtani &amp; Berg-Kirkpatrick, 2018)</td><td>ROUGE-L</td></tr><tr><td>Visual Change Captioning</td><td>Synthetic</td><td>CLEVR-Change (Hosseinzadeh &amp; Wang, 2021)</td><td>ROUGE-L</td></tr><tr><td>Visual Relationship Expressing Subtle Difference Expressing</td><td>General</td><td>IEdit (Tan et al., 2019)</td><td>ROUGE-L</td></tr><tr><td>Multimodal Cloze</td><td>Fine-Grained</td><td>Birds-to-Words (Forbes et al., 2019)</td><td>ROUGE-L</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>Comic Dialogue Identification</td><td>Cartoon</td><td>COMICS-Dialogue (Iyyer et al., 2017)</td><td>Accuracy</td></tr><tr><td>Comic Panel Identification</td><td>Cartoon</td><td>COMICS-Panel (Iyyer et al., 2017)</td><td>Accuracy</td></tr><tr><td>Recipe Completion</td><td>Recipe</td><td>RecipeQA-TextCloze (Yagcioglu et al., 2018)</td><td>Accuracy</td></tr><tr><td>Visual Step Cloze Knowledge Grounded QA</td><td>Recipe</td><td>RecipeQA-VisualCloze (Yagcioglu et al., 2018)</td><td>Accuracy</td></tr><tr><td colspan="4"></td></tr><tr><td>Webpage QA</td><td>Webpage</td><td>WebQA (Chang et al., 2022)</td><td>Accuracy</td></tr><tr><td>Textbook QA</td><td>Textbook</td><td>TQA (Kembhavi et al., 2017)</td><td>Accuracy</td></tr><tr><td>Complex Multimodal QA</td><td>Wikipedia</td><td>MMQA (Talmor et al., 2021)</td><td>Accuracy</td></tr><tr><td>Complex Multimodal QA*</td><td>Wikipedia</td><td>MANYMODALQA (Hannan et al., 2020)</td><td>Accuracy</td></tr><tr><td colspan="4">Text-Rich Images QA</td></tr><tr><td>Slide QA</td><td>Slide</td><td>SlideVQA (Tanaka et al., 2023)</td><td>Accuracy</td></tr><tr><td>OCR QA</td><td>Book Cover</td><td>OCR-VQA (Mishra et al., 2019)</td><td>Accuracy</td></tr><tr><td>Document QA</td><td>Document Image</td><td>DocVQA (Mathew et al., 2021)</td><td>Accuracy</td></tr><tr><td colspan="4">Multi-Image Reasoning</td></tr><tr><td>Image-Set QA*</td><td>Indoor Egocentric</td><td>Gibson (Bansal et al., 2020; Xia et al., 2018)</td><td>Accuracy</td></tr><tr><td>Image-Set QA</td><td>Driving Recording</td><td>nuScenes (Bansal et al., 2020; Caesar et al., 2020)</td><td>Accuracy</td></tr><tr><td>Industrial Inspection</td><td>Industrial</td><td>VISION (Bai et al., 2023)</td><td>Accuracy</td></tr><tr><td>Fashion QA</td><td>Fashion</td><td>Fashion200K (Han et al., 2017)</td><td>Accuracy</td></tr><tr><td>Property Coherence</td><td>General</td><td>MIT-States-PropertyCoherence (Isola et al., 2015)</td><td>Accuracy</td></tr><tr><td>State Transformation Coherence</td><td>General</td><td>MIT-States-StateCoherence (Isola et al., 2015)</td><td>Accuracy</td></tr><tr><td>Visual Step Matching</td><td>Recipe</td><td>RecipeQA-ImageCoherence (Yagcioglu et al., 2018)</td><td>Accuracy</td></tr><tr><td>Multi-Image Visual Entailment</td><td>General</td><td>NLVR2 (Suhr et al., 2018)</td><td>Accuracy</td></tr><tr><td>Ambiguity Analysis</td><td>Mobile Photo</td><td>VizWiz (Bhattacharya et al., 2019)</td><td>Accuracy</td></tr></table>

Table 6: Summary of the demonstrative instruction-following tasks in DEMON benchmark. \* indicates the tasks that are not included in DEMON-Core.

## C IMPLEMENTATION DETAILS

Model. We choose ViT-G/14 from EVA-CLIP (Fang et al., 2023) as our visual encoder and pretrained Q-former from BLIP-2 without instruction tuning as the task-agnostic visual prompt generator. For the large language model, we implement three versions: LLaMA2-7B (Touvron et al.,

![](images/a0d227259e6799e1996fa6fdc557179a0f9d9b109de4a9ba97deb51f21d1281d.jpg)  
Figure 9: Detailed framework of our MLLM enhanced with VPG-C.

2023b), Vicuna-7B (Chiang et al., 2023), Vicuna-13B, with 32, 32, 48 Transformer layers, respectively. We derive instruction-specific conditions from the 16th / 24th layer and re-inject the conditional visual knowledge into the 17th / 25th layer. Furthermore, we provide detailed framework of our MLLM enhanced with VPG-C in Figure 9.

Choice of Q-former. Recently, InstructBLIP (Dai et al., 2023) proposes to take the instruction as additional input to the Q-former and fine-tune the Q-former to extract visual features according to in structions using 16M multimodal instruction tuning data. While achieving outstanding performance on in-domain tasks, a recent study (Xu et al., 2023) indicates that fine-tuning on massive in-domain data severely undermines its generalizability on open-world scenarios. Instead of directly relying on the Q-former to achieve task-specific feature extraction by massive instruction tuning, we aim to utilize the sophisticated reasoning ability of LLMs to guide the Q-former to conditionally attend to residual visual details. Thus, we use the Q-former without instruction data tuning from BLIP-2 (Li et al., 2023c), which extracts the task-agnostic primary visual contents at the first time.

Training. We implement VPG-C in LAVIS library (Li et al., 2022a). We keep the visual backbone, visual prompt generator, and the language model frozen, and tune the $\mathrm { V P G - C }$ module using the proposed training strategy. Since BLIP-2 models do not include pre-trained Q-former that matches Vicuna and LLaMA2, we reuse the Q-former that matches FlanT5-XXL and fine-tune the last linear projection layer with 5 million image-text pairs to align it with Vicuna/LLaMA2. All the tunable parameters of our VPG-C module are a set of query embeddings and two linear projection layers, which only accounts for 0.09% (∼6.3M) of the entire model. As for synthetic training, we select about 30k images from CC3M (Sharma et al., 2018) that contain significantly ignored objects and perform different types of editing on them. Totally, we generate approximately 64k synthetic images with suitable modifications. To stablize the training and avoid overfitting, we use 500k imagecaption pairs from CC3M to jointly train the VPG-C module. We tune the VPG-C module for 18k steps using a batch size of 24 for synthetic training and 64 for image captioning, which takes about 7 hours to complete with a single A100 GPU. Additionally, we adopt the AdamW optimizer with $\beta = ( 0 . 9 , 0 . 9 9 9 )$ , and set the learning rate and weight decay to 0.00002 and 0.05, respectively. We warm up the training with 2k warm-up steps, followed by a learning rate decay mechanism with the cosine schedule.

Implementation of VPG-C with the linear VPG. As a generic method, VPG-C can be implemented with different VPGs. Beyond widely used Q-former that is composed of multiple Transformer blocks, we further probe the effectiveness of VPG-C with a simpler VPG, i.e., Linear Projection, as used in LLaVA (Liu et al., 2023). LLaVA trains a simple linear layer as the VPG to connect image features into the word embedding space. To implement $\mathrm { V P G - C }$ with the linear VPG, we first linearly project the generated guidance g and then take it as a filter to perform element-wise Hadamard product with the visual features $\chi ^ { \smash { \scriptstyle \frac { Q } { \mathstrut } } }$ from the image encoder:

$$
\overline { { \mathcal { V } } } = ( \mathcal { W } _ { 1 } \mathbf { g } \mathbf { 1 } ^ { T } ) \odot ( \mathcal { W } _ { 2 } \mathcal { X } ^ { I } )\tag{1}
$$

where $\mathcal { W } _ { 1 }$ and $\mathcal { W } _ { 2 }$ are linear projection matrixes, $\mathbf { \Omega } _ { \mathbf { 1 } } { } ^ { T }$ is the transpose of an all-ones vector, and ⊙ represents Hadamard product. The output $\overline { { \mathcal { V } } }$ represents the newly-extracted missing visual details according to the inferred guidance. And V is reintegrated into the LLM in the same manner.

## D MODEL DETAILS IN DEMON BENCHMARK

Recent advancements in LLMs (OpenAI, 2023a;b) have heralded significant achievements across various domains. Inspired by this success, many MLLMs (Li et al., 2023c; Liu et al., 2023; Zhu et al., 2023a; Alayrac et al., 2022; Ye et al., 2023; Gao et al., 2023; Li et al., 2023a) have been proposed to foster generalist vision-language reasoning (Xu et al., 2015; Li et al., 2023b; 2020; Yu et al., 2023a; Li et al., 2022d; Zhang et al., 2022; Li et al., 2022c; 2023d; Zhang et al., 2019; Antol et al., 2015). In our experiments, we conducted comparisons with some of the most recent and representative MLLMs in the following.

• LLaVA (Liu et al., 2023) establishes a connection between the visual encoder ViT-L/14 from CLIP (Radford et al., 2021a) and the language decoder LLaMA (Touvron et al., 2023a), utilizing a lightweight, fully-connected (FC) layer. Initially, the system trains this FC layer using 595K image-text pairs, while keeping both the visual encoder and LLM static. Following this, LLaVA fine-tunes both the FC layer and LLM using a dataset comprising 158K instructional vision-language pairs. The tested version is “LLaVA-7B-v0”.

• LLaMA-Adapter V2 (Gao et al., 2023) stands as a model of parameter efficiency within the realm of visual instruction. Despite maintaining the visual encoder (ViT-L/14) and the LLM in a static state, LA-V2 distributes the instruction-following capacity of the entire LLaMA system via bias-tuning. This method allows for the refinement of scale, bias, norm, and prompt parameters on diverse data sets. These include 200M image captioning data, 158K visual instruction-following data, and an additional 52K language instructionfollowing data, the latter of which was assembled by GPT-4 (OpenAI, 2023b). The tested version is “LLaVA-7B”.

• MiniGPT-4 (Zhu et al., 2023a) bridges the gap between the visual encoder and text encoder using a fully-connected (FC) layer. Initially, this model trains the FC layer on a dataset comprised of 5M image-text pairs before fine-tuning it on 3.5K instructional visionlanguage data. Notwithstanding its simplicity, MiniGPT-4 requires the loading of a pretrained vision encoder from BLIP2, as well as a Vicuna LLM (Chiang et al., 2023). The tested version is “minigpt4-aligned-with-vicuna7b”.

• BLIP2 (Li et al., 2023c) employs a dual-stage strategy to seamlessly bridge the modality gap, utilizing a lean Q-Former pre-trained on 129 million image-text pairs. The initial stage kick-starts the learning process of vision-language representation, leveraging a frozen image encoder, the ViT-g/14 from EVA-CLIP (Fang et al., 2023). Subsequently, the second stage harnesses a frozen LLM, the FlanT5 (Chung et al., 2022), to initiate the visionto-language generative learning. This innovative strategy effectively facilitates zero-shot instructed image-to-text generation. The tested version is “blip2-pretrain-flant5xl”.

• mPLUG-Owl (Ye et al., 2023) introduces a visual abstractor, fundamentally close the Perceiver Resampler in Flamingo (Alayrac et al., 2022), as a bridge between the pre-trained visual encoder ViT-L/14 and the LLM (LLaMA (Touvron et al., 2023a)). This model adopts a two-stage fine-tuning procedure. In the initial phase, both the visual encoder and the visual abstractor undergo comprehensive fine-tuning using a dataset of 204M image-text pairs. Subsequently, in the second phase, mPLUG-Owl applies the 158K LLaVA-Instruct dataset to fine-tune the pre-trained LLM in a parameter-efficient manner through the use of LoRA (Hu et al., 2021). The tested version is “mplug-owl-llama-7b”.

• Otter (Li et al., 2023a) is a multimodal model that applies in-context instruction tuning based on OpenFlamingo (Alayrac et al., 2022). This model integrates a LLaMA-7B (Touvron et al., 2023a) language encoder and a CLIP ViT-L/14. While the visual and text encoders remain static, Otter refines an additional 1.3 billion parameters. These parameters are derived from adaptation modules and are trained using 158K instruction-following data. The tested version is “OTTER-Image-LLaMA7B-LA-InContext”.

• InstructBLIP (Dai et al., 2023) originates from a pre-trained BLIP-2 model, which consists of a ViT-g/14 image encoder, a Vicuna, and a Q-Former to act as the bridge between these two components. During the process of vision-language instruction tuning, only the Q-Former undergoes fine-tuning, with the training process leveraging data from 13 distinct visual question-answering datasets. The tested version is “blip2-vicuna-instruct-7b”.

• OpenFlamingo (Alayrac et al., 2022; Awadalla et al., 2023) represents one of the pioneering efforts to incorporate Language Model Learning (LLMs) into the domain of visionlanguage pretraining. To optimize its conditioning on visual features, Flamingo strategically integrates a number of gated cross-attention dense blocks amidst the layers of the pre-trained language encoder. OpenFlamingo offers an open-source rendition of this advanced model. The tested version is “llama-7b”.

The DEMON benchmark predominantly features interleaved vision-language instructions, distinguishing it from the traditional single-image datasets. While our innovative method, VPG-C, along with OpenFlamingo and MiniGPT-4, inherently accommodates interleaved image-text sequences, other models like BLIP-2, InstructBlip, LLaVA, mPLUG-Owl, Otter, and LLaMA-Adapter V2 do not. For these, we employed a strategy where we concatenate the embeddings of all images. This approach can be analogized to treating images as frames within a video. To maintain the positional context of each image in an interleaved image-text instruction, we explicitly indicate the location of each image within the context.

## E DETAILED ZERO-SHOT PERFORMANCE ON MME BENCHMARK

In this section, we report the detailed performance on the 14 subtasks of MME benchmark in Table 7.

Table 7: Detailed zero-shot performance on MME benchmark.
<table><tr><td></td><td>BLIP-2</td><td>InstructBLIP</td><td>LA-V2</td><td>LLaVA</td><td>MiniGPT-4</td><td>mPLUG-Owl</td><td>Otter</td><td>VPG-C</td></tr><tr><td>Existence</td><td>160.00</td><td>185.00</td><td>120.00</td><td>50.00</td><td>115.00</td><td>120.00</td><td>195.00</td><td>180.00</td></tr><tr><td>Count</td><td>135.00</td><td>143.33</td><td>50.00</td><td>50.00</td><td>123.33</td><td>88.33</td><td>50.00</td><td>96.67</td></tr><tr><td>Position</td><td>73.33</td><td>66.67</td><td>48.33</td><td>50.00</td><td>81.67</td><td>50.00</td><td>86.67</td><td>80.00</td></tr><tr><td>Color</td><td>148.33</td><td>153.33</td><td>75.00</td><td>55.00</td><td>110.00</td><td>55.00</td><td>113.33</td><td>116.67</td></tr><tr><td>Poster</td><td>141.84</td><td>123.81</td><td>99.66</td><td>50.00</td><td>55.78</td><td>136.05</td><td>138.78</td><td>147.28</td></tr><tr><td>Celebrity</td><td>105.59</td><td>101.18</td><td>86.18</td><td>48.82</td><td>65.29</td><td>100.29</td><td>172.65</td><td>164.12</td></tr><tr><td>Scene</td><td>145.25</td><td>153.00</td><td>148.50</td><td>50.00</td><td>95.75</td><td>135.50</td><td>158.75</td><td>156.00</td></tr><tr><td>Landmark</td><td>138.00</td><td>79.75</td><td>150.25</td><td>50.00</td><td>69.00</td><td>159.25</td><td>137.25</td><td>145.00</td></tr><tr><td>Artwork</td><td>136.50</td><td>134.25</td><td>69.75</td><td>49.00</td><td>55.75</td><td>96.25</td><td>129.00</td><td>113.50</td></tr><tr><td>OCR</td><td>110.00</td><td>72.50</td><td>125.00</td><td>50.00</td><td>95.00</td><td>65.00</td><td>72.50</td><td>100.00</td></tr><tr><td>Perception</td><td>1293.84</td><td>1212.82</td><td>972.67</td><td>502.82</td><td>866.57</td><td>967.34</td><td>1292.26</td><td>1299.24</td></tr><tr><td>Commonsense</td><td>110.00</td><td>129.29</td><td>81.43</td><td>57.14</td><td>72.14</td><td>78.57</td><td>106.43</td><td>98.57</td></tr><tr><td>Numerical</td><td>40.00</td><td>40.00</td><td>62.50</td><td>50.00</td><td>55.00</td><td>60.00</td><td>72.50</td><td>77.50</td></tr><tr><td>Text Translation</td><td>65.00</td><td>65.00</td><td>50.00</td><td>57.50</td><td>55.00</td><td>80.00</td><td>57.50</td><td>57.50</td></tr><tr><td>Code Reasoning</td><td>75.00</td><td>57.50</td><td>55.00</td><td>50.00</td><td>110.00</td><td>57.50</td><td>70.00</td><td>87.50</td></tr><tr><td>Cognition</td><td>290.00</td><td>291.79</td><td>248.93</td><td>214.64</td><td>292.14</td><td>276.07</td><td>306.43</td><td>321.07</td></tr></table>

## F DETAILED ZERO-SHOT PERFORMANCE ON DEMON BENCHMARK

Table 8: Zero-shot evaluation on multimodal dialogue.
<table><tr><td></td><td>Conversational Embodied Dialogue</td><td>Multimodal Dialogue</td></tr><tr><td>BLIP-2</td><td>16.75</td><td>35.49</td></tr><tr><td>InstructBLIP</td><td>18.07</td><td>49.09</td></tr><tr><td>LLaMA-Adapter V2</td><td>19.04</td><td>9.40</td></tr><tr><td>LLaVA</td><td>10.19</td><td>5.39</td></tr><tr><td>MiniGPT-4</td><td>16.82</td><td>10.57</td></tr><tr><td>mPLUG-Owl</td><td>11.07</td><td>14.27</td></tr><tr><td>OpenFlamingo</td><td>24.27</td><td>9.49</td></tr><tr><td>Otter</td><td>16.06</td><td>14.68</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>48.31</td><td>37.04</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>41.02</td><td>33.99</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>42.25</td><td>34.02</td></tr></table>

Table 9: Zero-shot evaluation on visual storytelling.
<table><tr><td></td><td>Animated Story Completion-AESOP</td><td>Animated Story Completion-PororoSV</td><td>Animated Story Completion-FlintstonesSV</td><td>Sequential Photo Storytelling-VIST</td><td>Sequential Photo Storytelling-DiDeMoSV</td></tr><tr><td>BLIP-2</td><td>21.64</td><td>26.24</td><td>29.61</td><td>13.16</td><td>24.2</td></tr><tr><td>InstructBLIP</td><td>18.80</td><td>28.20</td><td>33.32</td><td>16.92</td><td>24.80</td></tr><tr><td>LLaMA-Adapter V2</td><td>18.01</td><td>20.15</td><td>24.22</td><td>10.89</td><td>14.57</td></tr><tr><td>LLaVA</td><td>13.56</td><td>11.44</td><td>12.77</td><td>8.00</td><td>7.71</td></tr><tr><td>MiniGPT-4</td><td>12.23</td><td>16.00</td><td>26.48</td><td>14.82</td><td>15.81</td></tr><tr><td>mPLUG-Owl</td><td>18.28</td><td>20.49</td><td>32.12</td><td>10.82</td><td>14.94</td></tr><tr><td>OpenFlamingo</td><td>23.32</td><td>32.35</td><td>37.79</td><td>15.14</td><td>12.50</td></tr><tr><td>Otter</td><td>13.94</td><td>17.52</td><td>22.21</td><td>9.96</td><td>14.23</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>19.98</td><td>28.67</td><td>38.14</td><td>16.95</td><td>20.05</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>19.93</td><td>28.36</td><td>39.19</td><td>17.34</td><td>21.27</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>20.53</td><td>29.81</td><td>41.32</td><td>19.04</td><td>22.26</td></tr></table>

Table 10: Zero-shot evaluation on visual relation inference.
<table><tr><td></td><td>Visual Change Captioning -Spot-the-Diff</td><td>Visual Change Captioning -CLEVR-Change</td><td>Visual Relationship Expressing</td><td>Subtle Difference Expressing</td></tr><tr><td>BLIP-2</td><td>17.48</td><td>3.21</td><td>12.37</td><td>9.62</td></tr><tr><td>InstructBLIP</td><td>19.71</td><td>4.61</td><td>10.70</td><td>10.92</td></tr><tr><td>LLaMA-Adapter V2</td><td>16.72</td><td>15.52</td><td>7.88</td><td>13.92</td></tr><tr><td>LLaVA</td><td>8.50</td><td>8.76</td><td>6.72</td><td>9.11</td></tr><tr><td>MiniGPT-4</td><td>7.50</td><td>7.49</td><td>7.84</td><td>8.97</td></tr><tr><td>mPLUG-Owl</td><td>6.06</td><td>1.46</td><td>6.22</td><td>7.86</td></tr><tr><td>OpenFlamingo</td><td>13.01</td><td>11.90</td><td>12.57</td><td>17.90</td></tr><tr><td>Otter</td><td>12.69</td><td>11.63</td><td>8.85</td><td>12.38</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>21.02</td><td>42.05</td><td>14.10</td><td>24.81</td></tr><tr><td> $\mathtt { V P G - C - V i c u n a - 7 B }$ </td><td>20.01</td><td>41.60</td><td>16.35</td><td>25.64</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>21.56</td><td>40.67</td><td>20.27</td><td>26.08</td></tr></table>

Table 11: Zero-shot evaluation on multimodal cloze.
<table><tr><td></td><td>Comic Dialogue Identification</td><td>Comic Panel Identification1</td><td>Recipe Completion</td><td>Visual Step Cloze1</td></tr><tr><td>BLIP-2</td><td>39.70</td><td>0.00</td><td>30.46</td><td>1.60</td></tr><tr><td>InstructBLIP</td><td>40.60</td><td>0.00</td><td>27.40</td><td>16.80</td></tr><tr><td>LLaMA-Adapter V2</td><td>24.40</td><td>0.40</td><td>38.20</td><td>9.00</td></tr><tr><td>LLaVA</td><td>30.60</td><td>0.00</td><td>32.80</td><td>0.00</td></tr><tr><td>MiniGPT-4</td><td>33.00</td><td>1.00</td><td>31.60</td><td>0.80</td></tr><tr><td>mPLUG-Owl</td><td>36.60</td><td>0.00</td><td>27.60</td><td>0.80</td></tr><tr><td>OpenFlamingo</td><td>38.40</td><td>1.20</td><td>29.00</td><td>18.00</td></tr><tr><td>Otter</td><td>29.00</td><td>0.00</td><td>35.00</td><td>0.00</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>36.80</td><td>1.80</td><td>51.80</td><td>1.40</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>39.20</td><td>3.60</td><td>30.40</td><td>15.40</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>42.20</td><td>8.20</td><td>39.80</td><td>18.40</td></tr></table>

1 For tasks with images as options, only responses that begin with the correct answer will be evaluated as correct.

Table 12: Zero-shot evaluation on knowledge grounded QA.
<table><tr><td></td><td>Webpage QA</td><td>Textbook QA</td><td>Complex Multimodal QA</td></tr><tr><td>BLIP-2</td><td>47.60</td><td>29.73</td><td>40.36</td></tr><tr><td>InstructBLIP</td><td>45.20</td><td>30.20</td><td>66.80</td></tr><tr><td>LLaMA-Adapter V2</td><td>44.60</td><td>46.00</td><td>43.80</td></tr><tr><td>LLaVA</td><td>39.40</td><td>39.60</td><td>29.60</td></tr><tr><td>MiniGPT-4</td><td>27.40</td><td>28.60</td><td>34.80</td></tr><tr><td>mPLUG-Owl</td><td>34.20</td><td>30.00</td><td>35.60</td></tr><tr><td>OpenFlamingo</td><td>37.80</td><td>32.40</td><td>25.80</td></tr><tr><td>Otter</td><td>45.00</td><td>39.00</td><td>41.00</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>49.40</td><td>42.40</td><td>61.20</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>50.00</td><td>33.40</td><td>62.40</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>50.60</td><td>43.40</td><td>64.80</td></tr></table>

Table 13: Zero-shot evaluation on text-rich images QA.
<table><tr><td></td><td>Slide QA</td><td>OCR QA</td><td>Document QA</td></tr><tr><td rowspan="3">BLIP-2 InstructBLIP LLaMA-Adapter V2 LLaVA MiniGPT-4</td><td>43.80</td><td>10.40 44.20</td><td>46.40 47.00</td></tr><tr><td>42.00 43.00</td><td>3.40</td><td>49.60</td></tr><tr><td>38.80 35.20 35.60</td><td>2.60 7.20 22.60</td><td>43.60 36.80</td></tr><tr><td rowspan="3">mPLUG-Owl OpenFlamingo Otter VPG-C-LLaMA2-7B</td><td>35.60</td><td>3.80</td><td>39.20 52.40</td></tr><tr><td>38.40</td><td>2.20</td><td>42.60</td></tr><tr><td>45.80</td><td>39.60</td><td>49.40</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>46.80</td><td>39.40</td><td>48.60</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>48.80</td><td>46.60</td><td>52.60</td></tr></table>

Table 14: Zero-shot evaluation on multi-image reasoning.
<table><tr><td></td><td>Image-Set QA</td><td>Industrial Inspection</td><td>Fashion QA</td><td>Property Coherence</td><td>State Transformation Coherence</td><td>Visual Step</td><td>Multi-Image Visual Entailment</td><td>Ambiguity Analysis</td></tr><tr><td>BLIP-2</td><td>34.60</td><td>42.80</td><td>43.20</td><td>59.00</td><td>38.20</td><td>0.20</td><td>53.40</td><td>45.80</td></tr><tr><td>instructblip7b</td><td>65.00</td><td>50.60</td><td>44.40</td><td>59.20</td><td>59.40</td><td>11.60</td><td>55.20</td><td>43.00</td></tr><tr><td>LLaMA-Adapter V2</td><td>41.60</td><td>55.00</td><td>45.60</td><td>48.80</td><td>63.00</td><td>0.00</td><td>54.80</td><td>43.40</td></tr><tr><td>LLaVA</td><td>29.60</td><td>53.00</td><td>45.20</td><td>50.40</td><td>59.20</td><td>0.80</td><td>50.80</td><td>43.20</td></tr><tr><td>MiniGPT-4</td><td>30.40</td><td>59.80</td><td>49.20</td><td>52.00</td><td>57.80</td><td>0.20</td><td>50.60</td><td>48.00</td></tr><tr><td>mPLUG-Owl</td><td>29.20</td><td>54.20</td><td>45.80</td><td>50.00</td><td>60.60</td><td>0.00</td><td>55.00</td><td>45.20</td></tr><tr><td>OpenFlamingo</td><td>25.80</td><td>52.20</td><td>44.20</td><td>59.60</td><td>51.40</td><td>2.20</td><td>53.60</td><td>44.00</td></tr><tr><td>Otter</td><td>44.80</td><td>69.80</td><td>47.00</td><td>51.40</td><td>46.40</td><td>0.00</td><td>49.00</td><td>42.40</td></tr><tr><td>VPG-C-LLaMA2-7B</td><td>62.60</td><td>61.40</td><td>46.00</td><td>56.60</td><td>57.80</td><td>0.00</td><td>53.80</td><td>51.20</td></tr><tr><td>VPG-C-Vicuna-7B</td><td>67.20</td><td>48.80</td><td>50.00</td><td>60.80</td><td>60.00</td><td>0.20</td><td>57.80</td><td>57.40</td></tr><tr><td>VPG-C-Vicuna-13B</td><td>73.40</td><td>54.00</td><td>51.00</td><td>63.20</td><td>63.40</td><td>2.60</td><td>60.20</td><td>61.40</td></tr></table>

1 For tasks with images as options, only responses that begin with the correct answer will be evaluated as correct.

## G QUALITATIVE COMPARISON

In this section, we compare our model with existing MLLMs on some complicated demonstrative instructions.

![](images/95fe09619a9f42804dec49bf11e7320df5adf412959773e50b84eb97767fd59d.jpg)  
Figure 10: Qualitative comparison between our VPG-C and existing MLLMs.

![](images/82e8adb1731c40627664590029fc8ccd9fe97678999bb238d8d0808daa329732.jpg)  
Figure 11: Qualitative comparison between our VPG-C and existing MLLMs.

![](images/ef2c502f8540bfbe1d5d5f85f62fbec7914194ea576d036b0db8e8db0bcc77db.jpg)  
Figure 12: Qualitative comparison between our VPG-C and existing MLLMs.

![](images/b865cea4e7f5522d0000ac4feeeb0e9536e9b989fd5920c97615ecc9bbf0b71c.jpg)  
Figure 13: Qualitative comparison between our VPG-C and existing MLLMs.

![](images/24b6d1e78d8f43701730a2b3037492aa0e22190a2756fffe9ddedb063945044c.jpg)  
Figure 14: Qualitative comparison between our VPG-C and existing MLLMs.

![](images/ad8eb638c3e39512b0292a409e8a3d18d72240aa84907bae03cdd50462da251a.jpg)  
Figure 15: Qualitative comparison between our VPG-C and existing MLLMs.
# Large Language Models as Automated Aligners for  benchmarking  Vision-Language Models

OpenReview ID: kZEXgtMNNo
Decision: Accept

## Abstract
With the advancements in Large Language Models (LLMs), Vision-Language Models (VLMs) have reached a new level of sophistication, showing notable competence in executing intricate cognition and reasoning tasks. However, existing evaluation benchmarks, primarily relying on rigid, hand-crafted datasets to measure task-specific performance, face significant limitations in assessing the alignment of these increasingly anthropomorphic models with human intelligence. In this work, we address the limitations via Auto-Bench, which delves into exploring LLMs as proficient aligners, measuring the alignment between VLMs and human intelligence and value through automatic data curation and assessment. Specifically, for data curation, Auto-Bench utilizes LLMs (e.g., GPT-4) to automatically generate a vast set of question-answer-reasoning triplets via prompting on visual symbolic representations (e.g., captions, object locations, instance relationships, and etc. The curated data closely matches human intent, owing to the extensive world knowledge embedded in LLMs. Through this pipeline, a total of 28.5K human-verified and 3,504K unfiltered question-answer-reasoning triplets have been curated, covering 4 primary abilities and 16 sub-abilities. We subsequently engage LLMs like GPT-3.5 to serve as judges, implementing the quantitative and qualitative automated assessments to facilitate a comprehensive evaluation of VLMs. Our validation results reveal that LLMs are proficient in both evaluation data curation and model assessment, achieving an average agreement rate of 85%. We envision Auto-Bench as a flexible, scalable, and comprehensive benchmark for evaluating the evolving sophisticated VLMs.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The paper introduces Auto-Bench, an automated benchmarking pipeline that utilizes Large Language Models (LLMs) to curate data and evaluate Vision-Language Models (VLMs). The pipeline includes LLMs as automatic curators to generate question-answer-reasoning triplets and LLMs as judges to assess VLMs' performance. The paper shows the effectiveness of Auto-Bench in data curation, model evaluation, and supervised fine-tuning of VLMs.

#### Strengths
1. The paper introduces an innovative and comprehensive benchmarking pipeline for VLMs.
2. The use of LLMs as automatic curators and judges adds scalability to the evaluation process.
3. The extensive dataset curated by Auto-Bench enables effective evaluation and fine-tuning of VLMs.

#### Weaknesses
1. From my perspective, the approach provided by Visual Instruction Tuning [1] for constructing multimodal instruction data also constitutes a scalable, user-friendly, and comprehensive automated pipeline. Therefore, the claim about data generation is relatively weak. I've noticed that you mention your method being more diverse and complex, but in the analysis of 3.3 BENCHMARK STATISTICS, there is no mention of Visual Instruction Tuning. Lastly, could you please elaborate on any other significant differences and advantages of your method against Visual Instruction Tuning?
2. The use of GPT-4 or GPT-3.5 has already been mentioned in other articles, such as [2] and [3].
3. Assessments of different visual capabilities have also been addressed in other evaluations, such as [2], [3], [4], and [5].
[1] Visual Instruction Tuning
[2] MM-Vet: Evaluating Large Multimodal Models for Integrated Capabilities
[3] TouchStone: Evaluating Vision-Language Models by Language Models
[4] MME: A Comprehensive Evaluation Benchmark for Multimodal Large Language Models
[5] MMBench: Is Your Multi-modal Model an All-around Player?

#### Questions
Please check the weakness.

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.

#### Summary
The paper proposes AutoBench, a method to generate a large amount of instruction-response pairs for evaluating large multimodal models. The main motivation of the work is centered around the fact that the current datasets are either not suitable for open-ended evaluation or rely on expensive and limited human evaluation. The approach involves using LLM as data creators + LLM as evaluators. I like the motivation of the work, however, the paper majorly lacks in the quality of the experiments and its setup.

Comments:

- My major issue with the setup is using LLMs as data curators! Many existing LMMs are trained on GPT-4 generated data such as LLaVA, mPLUG-Owl etc. To what extent is the evaluation fair across all the models which are not specifically not trained on the GPT-4 generated data?
- The experiments are performed by generating instructions and responses for the COCO images and their corresponding COCO captions. I find this setup highly concerning since InstructBLIP (best model in their eval) is trained with COCO captions. Similarly, other models like LLaVA are also trained with the COCO captions. Again, this makes the evaluation unfair to all the models. 
- Quoting from the paper: “ Besides, we carefully curated approximately 28.5K high-quality samples to comprise the validation dataset, which was subsequently utilized for performance evaluation.” There is no information on how this curation was performed? 
- Benchmark scope: It remains unclear to me how an image in the dataset is assigned a particular subskill? When do you know that a particular image has physics related possible questions?
- Quoting from the paper: “Due to the nature of reasoning-based questions often lacking a unique answer, we format them as multiple-choice questions, thus reducing the difficulty of evaluation and ensuring its accuracy.” It would be better to provide some examples to understand why reasoning-based questions need multiple choice questions. Why can’t they be just open-ended even if they lack a unique answer.
- Thanks for showing distributions of the question length and cosine similarity. Figure 3b looks more or less overlapping and hence does not shout semantic richness in comparison to other dataset. 
- Figure 3 should also have datasets like Visit-Bench or Touchstone where the questions are collected from humans. I feel that the human questions will be the most diverse.
- How much does it cost to add a new model to your benchmark involving 28.5K instances?
- To establish LLM as a valid judge, the paper does not have any correlations with human numbers. In addition, it would be important to show that simpler metrics that are based on lexical similarity are not good judges for this dataset, which it currently does not do.
- I like the paper’s diversification into understanding the usefulness of the models along different skills and sub-skills.

#### Strengths
Mentioned in the summary

#### Weaknesses
Mentioned in the summary

#### Questions
Mentioned in the summary

### Review 3
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The authors use LLMs to generate and curate a new evaluation benchmark for vision-language models, dubbed Auto-Bench. By conditioned on image verbalizations (such as image captions, object locations, OCR etc) LLMs are used to generate question-answer-rationale triplets to evaluate a wide variety of vision-language capabilities, covering perception, reasoning, planning abilities and alignment with human values. To overcome evaluation bottlenecks such as surface form variation, he authors further propose using LLMs to judge model responses. Finally, the authors benchmark several state-of-the-art VL models using their proposed benchmark.

#### Strengths
- This work addresses an important challenge -- existing vision-language benchmarks only cover a narrow range of capabilities, and are limited in size due to the difficulty of manual curation.

- The primary contribution of this work is substantial -- a large benchmark containing more than 3 million examples, including a train split and a high-quality human-curated validation set, as well as an evaluation framework using LLMs.

- The authors choose a large breadth of the different capabilities to evaluate VLMs on, including planning and human value alignment which have not been focused on much in prior work. I also like how different tasks were framed as open-ended and close-ended depending on the nature of the task. 

- I really like the comparison between AutoBench and existing human-curated VQA datasets in section 4.2.

- The experiments are well done. I especially appreciate the Inclusion of qualitative model comparisons using an ELO system.

- The analysis of alignment between LLM and humans as judges in Section 4.4.

- The paper is well-written and easy to follow for the most part.

Well done!

#### Weaknesses
- The benchmark is built only on images sourced from MS-COCO. While I understand that this was done due to the richness of image annotations that could be fed to the LLM to generate questions, MS-COCO images also represent a narrow subset of all images which we would like to apply vision-language models to. Vision-language models have been oversaturated on COCO-based benchmarks, so performance on Auto-Bench may not be reflective of performance on other image domains (e.g. VizWiz, or medical images)

#### Questions
In section 4.2, "Users are guided to rank each sample based on its rationality and level of challenge." what does rationality mean?

## Meta Reviews

### Meta Review 1
This work explores using LLMs for curating evaluation benchmarks for vision-language models and creates a novel approach for this called Auto-Bench. Based on text explanations of the image (captions, object locations) Auto-Bench generates question-answer-reasoning triplets for evaluating different capabilities of VLMs. In addition, this work proposes to use LLMs also as part of computing the evaluation metrics by enabling these models to judge the VLM responses. Extensive experimentation is performed to showcase the utility of the method.

## Decisions

Decision: Accept (poster)

# Fine-tuning Multimodal LLMs to Follow Zero-shot Demonstrative Instructions

OpenReview ID: BXY6fe7q31
Decision: Accept

## Abstract
Recent advancements in Multimodal Large Language Models (MLLMs) have been utilizing Visual Prompt Generators (VPGs) to convert visual features into tokens that LLMs can recognize. This is achieved by training the VPGs on millions of image-caption pairs, where the VPG-generated tokens of images are fed into a frozen LLM to generate the corresponding captions. However, this image-captioning based training objective inherently biases the VPG to concentrate solely on the primary visual contents sufficient for caption generation, often neglecting other visual details. This shortcoming results in MLLMs’ underperformance in comprehending demonstrative instructions consisting of multiple, interleaved, and multimodal instructions that demonstrate the required context to complete a task. To address this issue, we introduce a generic and lightweight Visual Prompt Generator Complete module (VPG-C), which can infer and complete the missing details essential for comprehending demonstrative instructions. Further, we propose a synthetic discriminative training strategy to fine-tune VPG-C, eliminating the need for supervised demonstrative instructions. As for evaluation, we build DEMON, a comprehensive benchmark for demonstrative instruction understanding. Synthetically trained with the proposed strategy, VPG-C achieves significantly stronger zero-shot performance across all tasks of DEMON. Further evaluation on the MME and OwlEval benchmarks also demonstrate the superiority of VPG-C. The code and models are available at https://github.com/DCDmllm/Cheetah.

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper aims to address the issue that the image-captioning based training objective often leads the visual prompt generators (VPGs) to neglect visual details. It proposes a VPG-C(omplete) module to complete the missing details and a synthetic discriminative training strategy to train VPG-C without the need for supervised instructions. The experiments are conducted on the proposed DEMON benchmark, the MME, and OwlEval benchmarks.

#### Strengths
- The paper is well-written and easy to follow.
- The idea of completing the missing details for visual content is reasonable. The method of synthetic discriminative training is interesting and straightforward for training the VPG-C without the need for supervised instructions.
- The proposed DEMON benchmark encompasses a wide range of tasks spanning multiple categories, offering the potential for the evaluation of future research efforts.

#### Weaknesses
- The effectiveness of the proposed VPG-C has not been fully validated. On the proposed DEMON benchmark, the improvement of VPG-C compared to InstructBLIP is quite limited, which does not align with the expectation that completed details would significantly enhance VPG. The improvement on the MME benchmark is also not significant.
- The experimental evaluations on many common benchmarks are missing, such as the evaluation protocols of InstructBLIP (”divide the 26 datasets into 13 held-in datasets and 13 held-out datasets” including NoCaps, Flickr30K, GQA, VSR, IconQA, TextVQA, Visdial, HM, VizWiz, SciQA Image, MSVD QA, MSRVT QA, iVQA), the Mini-GPT4 dataset, the LLaVA-Instruct-150K benchmark, and the MIMIC-IT dataset. Evaluating on the same benchmarks as other MLLMs is important for a comprehensive and fair comparison.

#### Questions
The primary concerns are related to experimental evaluation, and the rating would improve if the experimental evaluation were comprehensive.

### Review 2
Rating: 6: marginally above the acceptance threshold
Confidence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.

#### Summary
This paper presents a new training method for Q-Former/Resampler, aiming to provide richer visual representations for lora-based Multimodal Language Models (MLLMs). In addition, the paper proposes a synthetic training dataset for training VPG-C. After training, VPG-C achieves surprising results on the benchmark proposed in this paper and other open-source benchmarks.

#### Strengths
1. The authors are the first (at least to my knowledge) to propose using the latent features of the intermediate layers of the llm as guidance for the q-former, providing directed detail supplementation for the LLM.

2. The provided dataset/training method may inspire future research.

3. The provided benchmark can better diagnose the capabilities of MLLMs.

#### Weaknesses
1. The paper does not mention the setting for instruction tuning. My understanding is that after using the synthetic discriminative training strategy, the model automatically acquires the ability to follow instructions without needing an instruction tuning phase.

2. The ablation in the paper validates the effectiveness of several proposed modules. But can VPG-C be applied to a finetuning setting, such as llava/minigpt4?

3. In multimodal dialogues, does the model need to update guidance multiple times when providing multiple answers? In other words, for each new additional question, does the model need to run the whole model to obtaion all hidden states and can't use the existing qkv cache?

#### Questions
See weakness.

### Review 3
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper studies the instruction tuning in multimodal language models. In particular, it tries to improve the bottleneck of visual prompt generator (VPG), aka the visual feature converter which converts a generic visual embedding into LLM-interpretable inputs. It hypothesizes that the bottleneck comes from the lacking of attention to details in VPG. To address this, the paper proposed two components: (1) a VGP-C architecture which additionally generate features for intermediate LLM layers with attention to LLM intermediate features, (2) a synthetic data generation procedure to generate training data to teach VPG to attend to details. In addition to these, the paper also introduced a new evaluation benchmark.

#### Strengths
1. The paper proposed two methods for multimodal instruction following, the VPGC architecture and the data synthesis technique. Both of them are novel and inspiring.
2. Plenty of ablation studies are provided to support the effectiveness of the method. Comprehensive experiments also demonstrate the superiority of the method compared to existing models.
3. The paper also introduced a benchmark for future research.

#### Weaknesses
1. The method contains several steps and is thus quite complicated. It may be hard to reproduce the whole framework in different settings and code bases.

#### Questions
NA.

### Review 4
Rating: 8: accept, good paper
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper aims to improve reasoning capabilities of Multi-modal Large Language Models (MLLMs) for demonstrative instructions. The authors highlight that most of MLLMs have been over-optimized on the image-captioning objective which has led to the use of visual features that could only describe the captions while neglecting its focus on minor yet discriminative features important for fine-grained reasoning.  

Firstly, this work proposes VPG-C which is a lightweight adaption on top of VPG which aims to reuse the information from the intermediate LLM layer and is used to modulate the VPG features through guidance. The modified VPG features are integrated into LLM intermediate layer which effectively improves the fine-grained reasoning performance.

Secondly, to train the VPG-module, this work proposes a automatic way to generate synthetic data used to improve fine-grained discriminative performance of MLLMs. 

Lastly, DEMON benchmark is proposed to evaluate the demonstrative instruction understanding of the proposed technique and other MLLMs.

The proposed approach is fairly motivated with analysis and ablation studies.

#### Strengths
Strengths:

1) This paper identifies and aims to address a crucial limitation of lack of reasoning capabilities of Multi-modal Large Language Models (MLLMs) for demonstrative instructions. Improving MLLMs for demonstrative instructions will pave more rapid growth for building human-friendly AI assistants.

2) The proposed VPG-C design is fairly motivated and it is compute friendly.

3) The idea of generating synthetic data with automatic pipeline to improve fine-grained discriminative capabilities of MLLMs is encouraging.

4) The authors have proposed a suitable benchmark demon which would enable more systematic developments in improving MLLMs.

#### Weaknesses
I could not observe any significant weaknesses. However I have a concern regarding the inference compute efficiency of the proposed approach. 

1) As the model is reusing its intermediate features via a feedback loop system, this will significantly increase the training and testing time and might not be batch friendly during inference. How does the throughput of this technique compares against previous methods?

#### Questions
Please refer to weakness section.

## Meta Reviews

### Meta Review 1
This paper seeks to enhance the reasoning abilities of Multi-modal Large Language Models (MLLMs) concerning demonstrative instructions, motivated by shortage of existing visual prompt generators usually concentrate solely on primary visual contents only. To solve the problem, this work proposes a new module VPG-C, and a synthetic discrimitive strategy to train VPG-C. During evaluation, a new benchmark DEMON is built for demonstrative instruction understanding. 

On the pro side, the reviewers agree:
1. The proposed new VPG-C module and corresponding training strategy is novel. 
2. The proposed benchmark is a good contribution and could enable more development of MLLMs in the community.
3. The experiments and restyle are strong and convincing. 

On the con side, the reviewers raised concerns about:
1. Inference computation efficiency.
2. Reproducibility 

During the rebuttal phase, the authors responded to these concerns by providing additional details and conducting additional experiments. Furthermore, they illustrated the reliability of the VPG-C component and its applicability to other existing MLLM models, such as MiniGPT4 and LLaVA.

In conclusion, reviewers express positivity towards the paper, acknowledging its effective addressing of a valid problem and finding the results to be convincing.

## Decisions

Decision: Accept (spotlight)

# LLM-CXR: INSTRUCTION-FINETUNED LLM FOR CXR IMAGE UNDERSTANDING AND GENERATION

Suhyeon Lee∗, Won Jun Kim∗, Jinho Chang & Jong Chul Ye

Korea Advanced Institute of Science & Technology,

{suhyeon.lee, wonjun, jinhojsk515, jong.ye}@kaist.ac.kr

## ABSTRACT

Following the impressive development of LLMs, vision-language alignment in LLMs is actively being researched to enable multimodal reasoning and visual input/output. This direction of research is particularly relevant to medical imaging because accurate medical image analysis and generation consist of reasoning based on a combination of visual features and prior knowledge. Many recent works have focused on training adapter networks that serve as an information bridge between image processing (encod ing or generating) networks and LLMs; but presumably, in order to achieve maximum reasoning potential of LLMs on visual information as well as language, image and text features should be allowed to interact more freely. This is especially important in the medical domain because understanding and generating medical images such as chest X-rays (CXR) require not only accurate visual and language-based reasoning but also a more intimate mapping between the two modalities. Thus, taking inspiration from previous work on the transformer and VQ-GAN combination for bidirectional image and text generation, we build upon this approach and develop a method for instruction-tuning an LLM pre-trained only on text to gain vision-language capabilities for medical images. Specifically, we leverage a pretrained LLM’s existing questionanswering and instruction-following abilities to teach it to understand visual inputs by instructing it to answer questions about image inputs and, symmetrically, output both text and image responses appropriate to a given query by tuning the LLM with diverse tasks that encompass image-based text-generation and text-based image-generation. We show that our model, LLM-CXR, trained in this approach shows better image-text alignment in both CXR understanding and generation tasks while being smaller in size compared to previously developed models that perform a narrower range of tasks.

## 1 INTRODUCTION

The last few years have seen remarkable development in the field of Large language models (LLMs). LLMs are considered a different class of AI models because of their ability to flexibly understand/generate natural language and perform language-based reasoning, allowing them to generalize to a variety of given tasks without the need to be explicitly trained for them. As a next step, methods to enable the input of visual information alongside language in LLMs (OpenAI, 2023; Liu et al., 2023; Alayrac et al., 2022; Li et al., 2023) as well as methods that output images from LLMs (Koh et al., 2023a;b) are being actively developed. These models have great potential to be particularly useful in the medical domain, as working with medical images such as chest X-rays (CXRs) requires the ability to understand context, perform reasoning, and communicate conclusions in both image and text forms. The first generation of medical multimodal LLMs has begun to emerge recently (Moor et al., 2023; Thawkar et al., 2023; Xu et al., 2023a).

The main challenge in developing these models is achieving alignment between the pretrained language features of LLMs and the newly introduced image features without catastrophic forgetting of their language abilities. This is a more difficult challenge in the domain of medical images compared to natural images because the model needs to distinguish subtle differences in images or even parts of images (e.g., pneumonia vs. pulmonary edema on CXR) and then provide accurate text descriptions or image generations. Natural images tend to be more diverse than medical images, and each one can be described by a broad range of statements. Medical images, on the other hand, require highly specific yet comprehensive descriptions - making the space for correct answers much smaller and more complex. This means that a medical multimodal LLM requires a more intimate mapping between textual and visual features.

![](images/4818ceb4e2a6960921fc6e4d5012a7cf339896e8b0434012c20f3939f10c7cfc.jpg)  
Figure 1: (a) Example of previous work that indirectly implements multimodal bidirectional LLM by connecting a pretrained image encoder or image generation model to a pretrained LLM with a mapping layer. (b) Example of previous work that implements multimodal bidirectional non-LLM transformer with VQ-GAN trained from scratch (i.e., without learned language features). (c) To enable direct multimodal feature interaction in LLMs pre-trained with text, our method implements (b) through LLM-specific instruction fine-tuning scheme.

Currently, the most popular approach to map visual features to and from an LLM is to train an ‘adapter network’ to act as a mapping layer that translates the output of a pretrained image encoder network to a form that can be understood by an LLM (Alayrac et al., 2022; Li et al., 2023; Zhu et al., 2023) or to connect the output of an LLM to an image-generating network to output images (Koh et al., 2023a;b). In these approaches, LLMs are frozen to prevent forgetting their language and reasoning capabilities. These multimodal LLMs have demonstrated impressive capabilities in vision-language tasks such as image captioning, zero-shot classification, visual question and answering (VQA), image generation, and image retrieval. However, with this common approach of using adapter networks, vision-language alignment may be limited as the adapter network serves as an information bottleneck that can hinder the interplay between visual and language features.

To better bridge the gap between image and text, we take inspiration from the field of vision-language pertaining (VLP) with non-LLM transformers, where there has already been a lot of work on treating images and text in the same token embedding space. Most prominent is the approach that tokenizes images using VQ-GAN (Esser et al., 2021) (VQ-VAE (Van Den Oord et al., 2017)) and generates sequences of both text tokens and image tokens using an autoregressive transformer decoder (Zhang et al., 2021; Lu et al., 2022; Wang et al., 2022a; Lee et al., 2023). These previous works fit well with our view that for better image-text alignment, models should be able to process images and text equally without a separate adapter bottleneck. Moreover, the fine details of the CXR images such as texture are important in medical diagnosis, making the tokens from local image features from VQ encodings preferable targets for alignment than the global descriptions. Hence, in this work, we take advantage of the widely used architectural component VQ-GAN to seamlessly integrate the image-text token space without requiring any structural modifications to the underlying base LLM.

Building on this foundation, we propose a method for achieving better image-text alignment in LLMs for CXR image understanding and generation by leveraging an LLM’s built-in instruction-following abilities. Specifically, we seek to teach the model visual information by giving it diverse instructions surrounding

CXR image analysis and generation and then using the outputs to finetune the LLM. As such, one of our main contributions is the development of this instruction-finetuning method that has been tailored to be suitable for an already-trained LLM to expand its capabilities to input and output images (tokenized by VQ GAN) without modification of model structure or objectives. An important distinction from previous work such as (Zhang et al., 2021; Lu et al., 2022; Wang et al., 2022a; Lee et al., 2023) is that while non-LLM VLP transformers were trained from scratch without a previous understanding of language - meaning there was no concern of forgetting nor the opportunity to take advantage of its language understanding - our contribution is a method that takes a pretrained LLM and adds bidirectional multimodal capabilities by a simple instructionfinetuning process designed for LLMs (further detailed in Section 2). Through this novel approach, we produce a finetuned LLM proficient in bidirectional, multimodal tasks capable of CXR-to-report generation, report-to-CXR generation, and CXR-related VQA. We show that this model has state-of-the-art image-text understanding and generative capabilities by demonstrating that it outperforms previously developed models in each of these tasks even though the other models were specifically designed for only a subset of the tasks.

## 2 LLM-CXR

## 2.1 CLINICAL INFORMATION-PRESERVING CXR TOKENIZATION

For the tokenization process of the images, we used VQ-GAN (Esser et al., 2021), a widely used approach (Wang et al., 2022a; Lu et al., 2022; Zhang et al., 2021; Lee et al., 2023) for tokenizing images in multimodal generation models with transformers. More specifically, we utilize the quantized latent space of the $\mathsf { V Q - G A N }$ model trained on the image domain. $\mathrm { V Q - G A N }$ consists of a frozen encoder $\begin{array} { r } { \dot { E } ( \cdot ) : \mathbb { R } ^ { C \times H \times W }  \{ 1 , 2 , \dots , K _ { i m g } \} ^ { d _ { z } } } \end{array}$ , decoder $\tilde { D ( \cdot ) } : \{ 1 , 2 , . . . , \tilde { K _ { i m g } } \} ^ { d _ { z } }  \mathbb { R } ^ { C \times H \times W }$ , and codebook $C \in \mathbb { R } ^ { K _ { i m g } \times n _ { z } }$ that contains $K _ { i m g }$ codes. With this VQ-GAN, it is possible to obtain tokenized image $z \in \{ 1 , 2 , . . . , K _ { i m g } \} ^ { d _ { z } }$ of length $d _ { z } .$ As shown in Figure 1(c), this allows us to freely convert images into tokens and then back to images similar to an autoencoder (Kramer, 1991). Furthermore, the tokenized images contain more localized information in each token, making them suitable for medical diagnosis purposes where localized and texture information is also critical. The VQ-GAN remains frozen during the training of the LLM. Its sole purpose is to encode and decode images, facilitating their input to and output from the LLM similar to tokenizers for text. Consequently, the LLM operates with images in the form of these image tokens, both for input and output processes.

However, the original VQ-GAN’s reconstruction objective during training only consists of L1 loss and LPIPS loss (Zhang et al., 2018), which causes loss of clinically important information such as characteristics of microscopic lesions in the information bottleneck formed by the quantization process. Therefore, to minimize the loss of such important but subtle information in CXRs, we present another contribution: an additional 1024-dimensional feature L2 reconstruction loss extracted from the CXR encoder model of the TorchXRayVision (Cohen et al., 2022) library that is used when training the VQ-GAN for image tokenization. This clinical information-preserving CXR tokenization leads to performance improvement in both the report-to-CXR task and the CXR-to-report task.

## 2.2 EXPANDING LLM’S TOKEN EMBEDDING SPACE

Non-LLM transformers are trained with both images and text from the beginning. Training multimodal LLMs has a subtle but crucial difference: LLMs are already trained on text, and this text-based training is too expensive to be done again during multimodal training. Thus, the goal is to confer visual capabilities using a fine-tuning process to an LLM previously trained only on the text in a way that the newly introduced visual information is in line with the pre-existing language information. To place image tokens in the same embedding space as text tokens without losing the language abilities of the LLM, we treated the process of adding image tokens to the model for fine-tuning the same as the technique of increasing the special token in the vocabulary $( i . e . ,$ , token type) in language model finetuning for the image retrieval and generation (Koh et al., 2023b;a). Concretely, if the LLM’s original embedding table was R $\backslash K _ { t e x t } \times d _ { e }$ in which the embedding dimension is $d _ { e } ,$ then the embedding table is expanded to $\mathbb { R } ^ { ( K _ { t e x t } + K _ { i m g } ) \times d _ { e } }$ The existing elements are retained and used as initial values for fine-tuning, while the newly expanded parts are initialized randomly. The entire embedding table is trainable during the fine-tuning process.

## 2.3 DATA AUGMENTATION WITH SYNTHETIC VQA

Text reports for CXRs contain a comprehensive, detailed description of the CXR image in question. While these image-text pairs can be used as-is to achieve vision-language alignment, this training can be enhanced by taking the text report and generating visual questions and answers (VQAs) that can be asked about CXR images. This is not only a way to further enhance vision-language alignment but also an important way to ensure that the natural language interaction capability is maintained in the model. We show that utilizing this multi-task instruction-tuning approach improves performance on all fronts (VQA, text-based image generation, and image-based text generation).

![](images/806be5a43036c5d11879ec0899e46049cc3a47eeefffa756bfc3f8bffb879335.jpg)  
Figure 2: Examples of VQA generated from a CXR text report.†

We use LlaMa 2 (Llama2-13b-chat-hf) (Touvron et al., 2023) to generate questions and answers about a chest X-ray as shown in Figure 2. Specifically, about ∼200,000 CXRs that were labeled in the MIMIC-CXR-JPG dataset to be positive for one or more lesions were selected, and LlaMa 2 was prompted to generate a few questions for each CXR. The prompt used to generate these VQAs and more examples of generated VQAs are included in Appendix B.

## 2.4 IMAGE-TEXT BIDIRECTIONAL INSTRUCTION FINE-TUNING

Taking inspiration from previous methods for non-LLM transformers’ multimodal generative methods (Wang et al., 2022a; Lu et al., 2022; Zhang et al., 2021; Lee et al., 2023), we adopt and transform this technique into an instruction finetuning (Wang et al., 2022b; Wei et al., 2021) scheme suitable for LLMs pretrained on a large text corpus. Since this process is simply a fine-tuning process for LLM, no structural or objective changes are made to LLM other than the expansion of the token embedding table, and no additional networks are required. The template for instruction-finetuning uses the template used by the Alpaca family (Taori et al., 2023; Databricks, 2023). Appendix C is the template of the prompt for instruction fine-tuning from the Alpaca family which consists of Instruction, Input, Response sections.

During the fine-tuning process, the LLM is optimized according to the objective function that outputs a response based on the instruction-input pairs in an autoregressive manner. Note that this is an instructiontuning scheme, inheriting but distinct from the training of non-LLM transformer multimodal generation methodologies. The advantage of this scheme will be covered in more detail later in Section 2.4.1.

The tasks used for fine-tuning are categorized into four main types: 1) natural language instructionfollowing (NL-IF), 2) report-to-CXR generation, 3) CXR-to-report generation, and 4) CXR-based vision question answering (CXR-VQA). These are the four primary task types categorized based on input and output modalities; but for the model, they form a rich training environment with a wide spectrum of tasks that are distinguished by Instruction. NL-IF and CXR-VQA training examples provide multi-dimensional tasks so that the model can learn intricately aligned visual and textual features and generalization of tasks instructed in natural language. The report-to-CXR and CXR-to-report generation tasks are used in high volume during training and are important for vision-language alignment, but it must be noted that they are merely two tasks among many. Through the use of Instructions to specify tasks, we add several unseen multimodal task capabilities to the base LLM without overwriting existing language-based interactive capabilities. It also enables simpler yet more general user interaction compared to the existing non-LLM multimodal bidirectional generation models discussed above, as they can only be queried for certain tasks using predefined tokens, while LLM-based models enable queries based on natural language instructions and thus the possibility of generalizing to zero-shot tasks (Wei et al., 2021; Wang et al., 2022b).

NL-IF task. We initialize the base LLM with weights of a pretrained instruction-following LLM (Databricks, 2023). To minimize the risk of forgetting of language proficiency during the fine-tuning process, we concurrently engage in instruction-following tuning using the same NL-IF dataset used to instruction-tune this base LLM.

Report-to-CXR generation. This is a task that aims to generate CXR images that match the Input radiology report as a Response. The Instructions for this task are randomly sampled from 10 versions similar to the instructions in the example below. The LLM directly outputs image tokens in the same way as text tokens due to the utilization of the expanded token space encompassing both text and image tokens. Therefore, CXR image generation does not require an additional network or text-to-image generative model (e.g. stable diffusion) as seen in Wu et al. (2023b); Koh et al. (2023a). Below is an example instruction/input pair used to instruct the LLM to generate a CXR image.

```markdown
### Instruction: Generate a chest X-ray image that corresponds
to the entered free-text radiology reports for the chest X-ray image.
Input: Bilateral, diffuse, confluent pulmonary opacities. Differential
diagnoses include severe pulmonary edema ARDS or hemorrhage.
### Response: <VQ032 VQ015 VQ124 ... VQ054 VQ032>
```

CXR-to-report generation. In this task, tokenized CXR images are the Input. Note that in our model, the image is not processed through a separate network trained with paired vision-language data as in Li et al. (2023); Liu et al. (2023); the tokenized image is directly into the LLM, and the LLM itself learns visual information on top of its language capabilities. It can then be instructed to output a corresponding radiology report to a given image as Response. Instructions are also randomly sampled from ten versions similar to the example below. The following snippet is an example instruction for the CXR-to-report task.

```markdown
### Instruction: Generate radiology reports for the entered CXR image.
Input: <VQ071 VQ057 VQ 402 ... VQ122 VQ002>
### Response: No acute cardiopulmonary process.
```

CXR-VQA task. In this task, questions about an image are given as Instructions, and the model generates an appropriate Response. Questions are about the CXR images given as Input. This not only trains the model to gain VQA capabilities but also improves the performance in the other vision-language tasks as well (i.e., enhancement of vision-language alignment). Below is an example instruction for the CXR-VQA task.

```markdown
### Instruction: What is the size of the pleural effusions?
Input: <VQ121 VQ720 VQ002 ... VQ005 VQ428>
### Response: The bilateral pleural effusions are moderate to large.
```

## 2.4.1 TRAINING OBJECTIVE

The training objective is to generate the entire target paragraph which consists of Instruction, Input, and Response in an autoregressive manner. However, similar to general GPT pre-training (Radford et al., 2018; 2019; Brown et al., 2020), the loss is only applied to the tokens generated after the response key (i.e.. ### Response:), following an instruction-tuning scheme (Taori et al., 2023; Databricks, 2023).

Specifically, for tokenized training paragraph $\left[ x _ { 1 } , x _ { 2 } , . . . , x _ { n _ { x } } , y _ { 1 } , y _ { 2 } , . . . , y _ { n _ { y } } \right]$ where x denotes Instruction and Input sections and y denotes Response section, the training loss is given by:

$$
L _ { i n s t r u c t } = - \mathrm { l o g } p ( { \pmb y } | { \pmb x } ) = \sum _ { i = 1 } ^ { n _ { y } } - \mathrm { l o g } p ( y _ { i } | y _ { i - 1 } , y _ { i - 2 } , . . . , y _ { 1 } , x _ { n _ { x } } , x _ { n _ { x } - 1 } , . . . , x _ { 1 } ) .\tag{1}
$$

Note that this objective is different from the one used to train non-LLM transformers such as in Lee et al. (2023) which uses $L _ { j o i n t } = - \mathrm { l o g } p ( \pmb { x } , \pmb { y } )$ . We hypothesize that instruction-tuning through the use of conditional loss mitigates overfitting to the fine-tuning dataset, particularly when working with limited data, thus promoting a better learning environment that encourages the model to expand its understanding from its pre-existing features rather than memorizing new features.

## 2.4.2 TWO-STAGE FINE-TUNING

Similar to previous works Chambon et al. (2022); Xu et al. (2023b), we place our focus on frontal view (i.e., AP and PA) images and the Impression sections of corresponding reports as they are the most relevant to making diagnoses and more amenable to straightforward comparison of the results. Additionally, we minimize references to prior studies within reports (as we will use just one image at a time during inference and it would not make sense to have reports that refer to prior studies) by pruning the MIMIC-CXR-JPG dataset to only include the first study for each subject.

Drawing inspiration from multi-stage training techniques commonly used in recent LLM fine-tuning methods (Zhu et al., 2023), we follow a similar two-stage training approach. In the first stage, unfiltered high-volume data (i.e., all CXR image-report pairs and findings/impression sections in the MIMIC-CXR dataset) is used to train the model on the entire distribution of new image tokens and the general relationship between image and text tokens. In the second stage, model performance is further enhanced using the pruned dataset (i.e., using only frontal view images, the first study for each patient, and impression sections of text reports) that provides a stronger signal for vision-language alignment.

Implementation details are provided in the Appendix A.

## 3 EXPERIMENTS

We compare the performance of LLM-CXR against similar contemporary models across all tasks performed by LLM-CXR. For CXR-to-report generation, we compare our results with UniXGen (Lee et al., 2023), XrayGPT (Thawkar et al., 2023), RadFM Wu et al. (2023a), IFCC Delbrouck et al. (2022) and R2Gen Chen et al. (2020); for CXR-VQA, with XrayGPT (Thawkar et al., 2023), RadFM Wu et al. (2023a), and ELIXR (Xu et al., 2023a); and for text-to-CXR generation, with UniXGen (Lee et al., 2023) and RoentGen (Chambon et al., 2022). Note that only LLM-CXR is capable of performing all three tasks. For further details regarding the ablation experiments on the design of our method, please refer to Appendix E.

## 3.1 CXR-TO-REPORT GENERATION TASK

We use each model to generate text radiology reports for CXR images in the MIMIC-CXR-JPG dataset using LLM-CXR (Figure 3), UniXGen (Lee et al., 2023), XrayGPT (Thawkar et al., 2023), RadFM Wu et al. (2023a), IFCC Delbrouck et al. (2022), and R2Gen Chen et al. (2020). In order to quantify how well the generated reports reflect the clinically significant radiologic information in the CXR images, we use the CheXpert-labeler (Irvin et al., 2019), which is a rule-based natural language processing tool that reads a text report for a CXR and extracts whether the report mentions the presence or absence of significant radiologic findings (e.g., edema, pleural effusion, etc.), and compare the extracted labels with that of ground-truth reports.

![](images/f9ab355c5977f3919a8cad628afe4d60f71e556dabf8f6b702b61a933ea80a2b.jpg)  
Figure 3: Examples of text report generation for a given CXR image with LLM-CXR. While the generated reports use different wording from the ground-truth reports, LLM-CXR is able to generate reports that capture the gist of the contents of the CXR, demonstrating alignment of vision-language features within the model. In addition, similar to real CXR reports, LLM-CXR often proposes valid causes for certain findings (e.g., suggesting aspiration as the cause of consolidation), demonstrating language-based reasoning ability characteristic of LLMs.†

![](images/e31efca4ca6ae3585a9982373e1b122071cbca906da25c8a7f5e141c1b2f4828.jpg)  
Figure 4: Examples of VQA with LLM-CXR. LLM-CXR understands questions given in natural language and is able to answer with relevant findings.†

To quantify the similarity between generated reports and ground-truth reports, we measured AUROC/F1 (Table 1) and Jaccard similarity index (Table 2) between labels of clinical significance (e.g. pneumonia, cardiomegaly) extracted from both generated and ground-truth reports using the CheXpert labeler (Irvin et al., 2019). Note that LLM-CXR and XrayGPT utilize input images with a resolution of 256×256 and 224×224 pixels respectively. In contrast, the original UniXGen model (UniXGen-512) uses images at a higher resolution of 512×512 pixels. Thus for comparison, we conduct experiments for UniXGen twice - once with its native 512px resolution and once again with 256px resolution images (used for LLM-CXR) upsampled to 512px.

In terms of both metrics, our model demonstrates superior performance when compared to competitors operating at the same resolution. Notably, there is no substantial performance gap observed when compared to UniXGen and RadFM, which operate with images at a higher resolution of 512×512 pixels. LLM-CXR (3B parameters) exhibits stronger accuracy than XrayGPT (based on the Vicuna-7B model). For completeness, we also measure the natural language generation performance metrics: BLEU, ROUGE-L, METEOR, CIDEr; however, because these metrics are less informative in the setting of medical image understanding where precise language is employed, we present them in the Appendix D (Table 5).

Table 1: CXR-to-report generation AUROC and F1.1
<table><tr><td>AUROC ↑</td><td>Atel.</td><td>Cnsl. Pmtx. Edema</td><td></td><td>Eff.</td><td></td><td>Pna. Cmgl.</td><td>Les.</td><td>Frac.</td><td>Opac. ECm.</td><td></td><td>NoF.</td><td>P.O.</td><td>Dev.</td><td></td><td>Micro Macro</td><td>Weighted</td></tr><tr><td>RadFM</td><td>| 0.587 0.498</td><td>0.503</td><td>0.633</td><td>0.657</td><td></td><td>0.504 0.611</td><td></td><td>0.516 0.498</td><td>0.514</td><td>0.502</td><td>0.666</td><td>0.499</td><td>0.597</td><td>0.638</td><td>0.556</td><td>0.596</td></tr><tr><td>UniXGen-512</td><td>0.570 0.533</td><td>0.519</td><td>0.615</td><td>0.682</td><td>0.526</td><td>0.645</td><td></td><td>0.501 0.498</td><td>0.555</td><td>0.510</td><td></td><td>0.676 0.4980.740</td><td></td><td>0.668</td><td>0.576</td><td>0.628</td></tr><tr><td>IFCC</td><td>| 0.479 0.508</td><td>0.486</td><td>0.504</td><td>0.496</td><td>0.486</td><td>0.545</td><td>0.518</td><td>0.498</td><td>0.497</td><td>0.463</td><td>0.497</td><td>0.499</td><td>0.494</td><td>0.543</td><td>0.497</td><td>0.498</td></tr><tr><td>R2Gen</td><td>0.501 0.485</td><td>0.504</td><td>0.500</td><td></td><td>0.503 0.502</td><td>0.505</td><td>0.510 0.500</td><td></td><td>0.501</td><td>0.511</td><td>0.494 0.500 0.498</td><td></td><td></td><td>0.542</td><td>0.501</td><td>0.500</td></tr><tr><td>UniXGen-256</td><td>0.518 0.511</td><td>0.530</td><td>0.542</td><td>0.533</td><td>0.510</td><td>0.524</td><td>0.513</td><td>0.499</td><td>0.519</td><td>0.511</td><td>0.564</td><td>0.527</td><td>0.593</td><td>0.575</td><td>0.528</td><td>0.540</td></tr><tr><td>XrayGPT LLM-CXR</td><td>0.5510.506</td><td>0.511</td><td>0.590</td><td>0.595</td><td>0.519</td><td>0.570</td><td>0.511</td><td>0.499</td><td>0.553</td><td>0.539</td><td>0.592</td><td>0.490</td><td>0.646</td><td>0.617</td><td>0.548</td><td>0.577</td></tr><tr><td></td><td>0.5580.517</td><td>0.496</td><td>0.619</td><td>0.641 0.509</td><td></td><td>0.577</td><td></td><td>0.506 0.494</td><td>0.537</td><td>0.505</td><td>0.6770.498 0.640</td><td></td><td></td><td>0.628</td><td>0.555</td><td>0.597</td></tr><tr><td>F1↑</td><td>Atel. Cnsl. Pmtx. Edema</td><td></td><td></td><td>Eff.</td><td>Pna.</td><td>Cmgl.</td><td>Les.</td><td>Frac.</td><td>Opac.</td><td>ECm.</td><td>NoF.</td><td>P.O.</td><td>Dev.</td><td></td><td>| Micro Macro</td><td>Weighted</td></tr><tr><td>RadFM</td><td>| 0.325 0.024</td><td>0.018</td><td>0.404</td><td></td><td>0.494 0.034</td><td>0.387</td><td>0.065 0.000</td><td></td><td>0.177</td><td>0.026</td><td>0.524</td><td>0.000 0.381</td><td></td><td>0.370</td><td>0.204</td><td>0.341</td></tr><tr><td>UniXGen-512</td><td>0.2980.116</td><td>0.064</td><td>0.374</td><td></td><td>0.530 0.121</td><td>0.423</td><td></td><td>0.014 0.000</td><td>0.317</td><td>0.049</td><td>0.532 0.000 0.586</td><td></td><td></td><td>0.413</td><td>0.245</td><td>0.398</td></tr><tr><td>IFCC</td><td>| 0.1590.083</td><td>0.020</td><td>0.203</td><td></td><td>0.312 0.006</td><td>0.270</td><td>0.068</td><td>0.000</td><td>0.323</td><td>0.042</td><td>0.200 0.000</td><td></td><td>0.292</td><td>0.220</td><td>0.141</td><td>0.225</td></tr><tr><td>R2Gen</td><td>0.168 0.018</td><td>0.020</td><td>0.073</td><td></td><td>0.129 0.034</td><td>0.263</td><td>0.043</td><td>0.000</td><td>0.240</td><td>0.051</td><td>0.289</td><td>0.000</td><td>0.254</td><td>0.201</td><td>0.113</td><td>0.183</td></tr><tr><td>UniXGen-256</td><td>0.1460.072</td><td>0.083</td><td>0.226</td><td></td><td>0.215 0.072</td><td>0.176</td><td>0.055</td><td>0.000</td><td>0.282</td><td>0.047</td><td>0.411</td><td>0.0920.367</td><td></td><td>0.262</td><td>0.160</td><td>0.243</td></tr><tr><td>XrayGPT</td><td>0.279 0.065</td><td>0.049</td><td>0.334</td><td></td><td>0.404 0.110</td><td>0.347</td><td>0.058</td><td>0.016</td><td>0.352</td><td>0.076</td><td>0.371</td><td>0.000</td><td>0.470</td><td>0.326</td><td>0.209</td><td>0.330</td></tr><tr><td>LLM-CXR</td><td>0.272 0.081</td><td>0.013</td><td>0.382</td><td></td><td>0.464 0.084</td><td>0.327</td><td></td><td>0.036 0.000</td><td>0.278</td><td>0.035</td><td>0.535</td><td>0.000</td><td>0.453</td><td>0.360</td><td>0.211</td><td>0.350</td></tr></table>

Table 2: CXR-to-Report generation Jaccard similarity index.1
<table><tr><td>JSI ↑</td><td>Micro</td><td>Macro</td><td>Weighted</td><td>No mention</td><td>Possible</td><td>Negative</td><td>Positive</td></tr><tr><td>RadFM</td><td>0.4894</td><td>0.2367</td><td>0.5568</td><td>0.6525</td><td>0.0123</td><td>0.0552</td><td>0.2270</td></tr><tr><td>UniXGen-512</td><td>0.4716</td><td>0.2520</td><td>0.5464</td><td>0.6323</td><td>0.0423</td><td>00733</td><td>0.2602</td></tr><tr><td>IFCC</td><td>0.4141</td><td>0.1935</td><td>0.4877</td><td>0.5835</td><td>0.0027</td><td>0.0643</td><td>0.1237</td></tr><tr><td>R2Gen</td><td>0.4038</td><td>0.1988</td><td>0.4842</td><td>0.5797</td><td>0.0337</td><td>0.0701</td><td>0.1116</td></tr><tr><td>UniXGen-256</td><td>0.5993</td><td>0.2438</td><td>0.6236</td><td>0.7480</td><td>0.0317</td><td>0.0449</td><td>0.1505</td></tr><tr><td>XrayGPT</td><td>0.4107</td><td>0.2206</td><td>0.4934</td><td>0.5773</td><td>0.0413</td><td>0.0690</td><td>0.1948</td></tr><tr><td>LLM-CXR</td><td>0.6092</td><td>0.2699</td><td>0.6420</td><td>0.7585</td><td>0.0483</td><td>0.0530</td><td>0.2198</td></tr></table>

1 Bold in report-to-CXR task result tables indicates the best performance among models at the same resolution with LLM-CXR (256×256). If the highest performance is achieved at the 512, this is separately underlined.

## 3.2 CXR-VQA TASK

We adopt the VQA performance assessment framework of ELIXR (Xu et al., 2023b) which, in summary, asks about the presence, location, and severity of certain lesions or findings for each CXR image and marks each answer as 0 (the answer is incorrect, internally inconsistent, or irrelevant), 1 (correct), or 0.5 (partially correct or not quite correct but a reasonable explanation for the CXR image). First, as done in ELIXR, we randomly select eight cases that are labeled in MIMIC-CXR with the following diagnoses: ‘No Finding’, ‘Pneumothorax’, ‘Pleural Effusion’, ‘Edema’, ‘Consolidation’ OR ‘Pneumonia’ (considered a single unified class), and ‘Lung Lesion’. We use the same questions and grading rubric used in Xu et al. (2023b). Note that the reported scores for ELIXR are taken from the paper Xu et al. (2023b) as their model is not publicly available, but the scores for XrayGPT and our model (LLM-CXR) were measured by the authors using open-sourced checkpoints.

Table 3: Accuarcy of the CXR-VQA task by topic and label diagnosis. ELIXR (Xu et al., 2023a) does not report its VQA accuracy by label diagnosis.
<table><tr><td colspan="3">Accuracy ↑</td><td>All Presence</td><td></td><td>Location</td><td colspan="2">Size, severity, type</td><td></td></tr><tr><td rowspan="4"></td><td colspan="2">ELIXR XrayGPT</td><td>54.8% 64.5%</td><td></td><td>41.0%</td><td colspan="2">25.0% 20.3%</td><td></td></tr><tr><td rowspan="3">RadFM</td><td>25.2%</td><td>27.4%</td><td>21.9%</td><td colspan="3"></td><td></td></tr><tr><td rowspan="2">LLM-CXR</td><td>32.7%</td><td>34.5%</td><td>31.3%</td><td colspan="2">20.8%</td><td></td></tr><tr><td>44.8%</td><td>41.3%</td><td>50.0%</td><td colspan="3">62.5%</td></tr><tr><td>Accuracy ↑</td><td>All</td><td>Cnsl./Pna.</td><td></td><td>Edema</td><td>Lsn.</td><td>NoF.</td><td>Eff.</td><td>Pmtx.</td></tr><tr><td>XrayGPT</td><td>25.2%</td><td>25.0%</td><td>26.25%</td><td></td><td>17.2%</td><td>42.5%</td><td>20.0%</td><td>18.8%</td></tr><tr><td>RadFM</td><td>32.7%</td><td>34.4%</td><td></td><td>31.3%</td><td>40.6%</td><td>61.3%</td><td>26.3%</td><td>23.8%</td></tr><tr><td>LLM-CXR</td><td>44.8%</td><td>39.1%</td><td></td><td>53.8%</td><td>50.0%</td><td>71.3%</td><td>53.8%</td><td>22.5%</td></tr></table>

An example of VQA performed by LLM-CXR is shown in Figure 4. Accuracies of VQA in comparison with other multimodal LLMs capable of CXR reading are shown in Table 3. ELIXR (Xu et al., 2023a) uses PaLM-2 as the base LLM and uses the framework of BLIP-2 (Li et al., 2023) (i.e., Q-former) for achieving vision-language alignment while XrayGPT Thawkar et al. (2023) uses a Vicuna-7B as the base LLM and uses the MedCLIP image encoder Wang et al. (2022c) and a linear mapping layer for vision-language alignment. Because the VQA task requires a general understanding of language, this task can only be done by the larger, LLM-based models. LLM-CXR holds promise even amongst bigger models.

## 3.3 REPORT-TO-CXR GENERATION TASK

Because our instruction-tuning includes image generation tasks, LLM-CXR is also able to generate matching chest X-rays when given a text report (Figure 5). We measure the quality of generated images with FID (Table 6 in Appendix D), and we measure vision-language alignment (i.e., how well the text used to guide image generation is reflected in the generated image) by calculating the AUROC/F1 (Table 4) against the original CXR images in MIMIC-CXR-JPGs with a pretrained CXR lesion classifier network (Cohen et al., 2022), specifically, densenet121-res224-all. We compare our generated CXRs to RoentGen (Chambon et al., 2022), a stable diffusion-based model that generates CXRs based on text descriptions, and UniXGen (Lee et al., 2023), a bespoke non-LLM transformer-based model trained from scratch to generate CXR images and reports.

As shown in Figure 5, LLM-CXR is able to reflect lesion characteristics, location, and severity in its generated CXR images. Quantitatively, FID indicates that LLM-CXR generates images closer to real CXR images than UniXGen or RoentGen. With regards to alignment with input text in the generated images, AUROC/F1 indicates that LLM-CXR generates images that are most aligned with input texts.

Table 4: CXR generation AUROC and F1.
<table><tr><td>AUROC ↑</td><td>Atel.</td><td>Cnsl.</td><td>Pmtx.</td><td>Edema</td><td>Eff.</td><td>Pna.</td><td>Cmgl.</td><td>Les.</td><td>Frac.</td><td>Opac.</td><td>ECm.</td><td>Micro</td><td>Macro</td><td>Weighted</td></tr><tr><td>RoentGen</td><td>0.7661</td><td>0.7535 0.6078</td><td></td><td>0.7084</td><td>0.8169</td><td></td><td>0.6054 0.7780 0.6283</td><td></td><td></td><td>0.6047 0.7162</td><td>0.7294</td><td>|0.7061</td><td>0.7013</td><td>0.7055</td></tr><tr><td>UniXGen</td><td>0.7982</td><td>0.7509</td><td>0.6640</td><td>0.7876</td><td>0.7725</td><td>0.7065</td><td>0.7610</td><td>0.7200</td><td>0.7121</td><td>0.7867</td><td>0.7893</td><td>0.7435</td><td>0.7499</td><td>0.7518</td></tr><tr><td>LLM-CXR</td><td>0.8054</td><td>0.8263</td><td>0.7540</td><td>0.8111</td><td>0.8155</td><td>0.7722</td><td>0.78460.7852</td><td></td><td>0.7596</td><td>0.8311</td><td>0.8335</td><td>0.7907</td><td>0.7980</td><td>0.7991</td></tr><tr><td>F1↑</td><td>Atel.</td><td>Cnsl.</td><td>Pmtx.</td><td>Edema</td><td>Eff.</td><td>Pna.</td><td>Cmgl.</td><td>Les.</td><td>Frac.</td><td>Opac.</td><td>ECm.</td><td>Micro</td><td>Macro</td><td>Weighted</td></tr><tr><td>RoentGen</td><td>|0.8113</td><td>0.7286</td><td>0.7110</td><td>0.2954</td><td>0.7619</td><td>0.2501</td><td>0.7639</td><td>0.2677</td><td>0.6580</td><td>0.7781</td><td>0.7066</td><td>0.6578</td><td>0.6121</td><td>0.6298</td></tr><tr><td>UniXGen</td><td>0.8648</td><td>0.6903</td><td>0.4981</td><td>0.7378</td><td>0.7008</td><td>0.7213</td><td>0.7598</td><td>0.5606</td><td>0.6424</td><td>0.7794</td><td>0.7958</td><td>0.7164</td><td>0.7046</td><td>0.7082</td></tr><tr><td>LLM-CXR</td><td>0.8777</td><td>0.8283</td><td>0.7024</td><td>0.8061</td><td>0.8183</td><td>0.7529</td><td>0.8372</td><td>0.7678</td><td>0.7753</td><td>0.8342</td><td>0.8274</td><td>0.8065</td><td>0.8025</td><td>0.8054</td></tr></table>

![](images/81b3e8a571f2abafeaf9382df43ea58c50b6bf27b4a074dd943f581786ab8e57.jpg)  
Figure 5: CXR images generated with LLM-CXR using radiology reports as input. (a) Normal CXRs. (b) Words such as “severe” and “mild” allow for the generation of different severities of lesions. (c) Specification of the location of lesions using words such as ‘left’, ‘right’, and ‘bilateral’.

## 4 CONCLUSION

Multimodal LLMs have great potential to assist in the field of diagnostic radiology as they can reason about visual information and express their findings in natural language or images understandable by medical professionals. However, a major challenge is achieving sufficient vision-language alignment in these pretrained LLMs. Most work on vision-language alignment in LLMs has focused on developing adapter networks to connect an image-processing network and a pretrained, frozen LLM. However, this approach has so far fallen short in achieving the level of vision-language alignment needed to accurately describe medical images and is prone to hallucinations despite the use of LLMs with relatively high numbers of parameters. In this work, we proposed a different approach, an instruction-finetuning method for LLMs that enables them to understand and generate visual information, that shows more promise in achieving better-aligned vision and language features. We leveraged the language-understanding capability of LLMs to provide a complex training environment that induces the incorporation of visual features into its language features and shows that it can lead to better visual understanding and generation with LLMs even with a much smaller model.

## 5 LIMITATIONS AND FUTURE WORK

There are a few limitations of this study that could be improved upon. Most importantly, while our method shows better performance than other larger models, there is still much room to be improved in the alignment of visual and language features. For example, generated CXR reports still contain false positives (i.e., they mention findings that are not actually present) and miss diagnoses. This problem could be further mitigated in the future by strengthening the alignment of images and text reports within the model by employing other vision-language techniques, improving the quality/quantity of the training data, or using larger LLMs. For instance, the radiology reports of the MIMIC dataset often refer to previous imaging studies which were unhelpful and act as noise instead of signal in our framework; we anticipate that using each patient’s CXR scans longitudinally, i.e., using the timestamps of each study, can help improve the quality of generated results by properly incorporating this information into the training process.

Furthermore, in our framework, a 256×256 image is translated into 256 image tokens. As a consequence, the resulting sequence contains relatively long token sequences compared to text, resulting in latency ranging from 30 to 60 seconds for image generation tasks and about 10 seconds for text generation tasks with the consumer GPU. Although our model presumably has faster inference times than larger models, it still cannot claim real-time responsiveness. A potential avenue for improvement is adopting techniques that enable dynamic tokenization of images (Jin et al., 2023), as opposed to using fixed-length tokens. This approach could potentially alleviate the latency issues and pave the way for more responsive real-time applications.

## ETHICS

Two important ethical issues at the intersection between medicine and AI are safety and privacy.

AI models will probably play increasingly larger roles in our healthcare systems. It is important that they are adopted in a way that improves patient safety and reliability of the systems already in place. LLMs have known issues with hallucinations and biases, which may be propagated when put into use without proper supervision. While communicative models like this one will potentially serve as a crucial interface between AI systems and human medical professionals so that such problems can be avoided, systems still need to be put in place so as to keep potential biases and hallucinations in check. There will also need to be continuous work to improve and scrutinize these models.

Furthermore, while our model is trained on the deidentified, publicly available MIMIC dataset, generative AI models such as ours raise concerns about privacy as institutions have the potential to develop these models with private patient data. When these multimodal LLMs reach the proficiency to be used in real clinics and become immediately valuable, regulations and technological security measures must be put in place to prevent breaches of patient privacy.

We hope that our model will serve as a step forward in developing reliable AI systems for healthcare.

## REPRODUCIBILITY

The pretrained models and datasets we use are all publicly available (Databricks’ dolly-v2-3b, Imagenetpretrained VQ-GAN, and MIMC-CXR-JPG). We release all code and model checkpoints upon publication along with step-by-step guidance to reproduce the methods explained in Section 2 so that anyone can reproduce our results2.

## ACKNOWLEDGMENTS

This research was supported by the National Research Foundation of Korea(NRF)(RS-2023-00262527); Field-oriented Technology Development Project for Customs Administration funded by the Korean government (the Ministry of Science & ICT and the Korea Customs Service) through the National Research Foundation (NRF) of Korea under Grant NRF2021M3I1A1097910 & NRF2021M3I1A1097938; Korea Medical Device Development Fund grant funded by the Korea government (the Ministry of Science and ICT, the Ministry of Trade, Industry, and Energy, the Ministry of Health & Welfare, the Ministry of Food and Drug Safety) (Project Number: 1711137899, KMDF PR 20200901 0015); Culture, Sports, and Tourism R&D Program through the Korea Creative Content Agency grant funded by the Ministry of Culture, Sports and Tourism in 2023; and Institute of Information & communications Technology Planning & Evaluation (IITP) grant funded by the Korea government(MSIT, Ministry of Science and ICT) (No. 2022-0-00984, Development of Artificial Intelligence Technology for Personalized Plug-and-Play Explanation and Verification of Explanation).

## REFERENCES

Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc, Antoine Miech, Iain Barr, Yana Hasson, Karel Lenc, Arthur Mensch, Katherine Millican, Malcolm Reynolds, et al. Flamingo: a visual language model for few-shot learning. Advances in Neural Information Processing Systems, 35:23716–23736, 2022.

Sid Black, Stella Biderman, Eric Hallahan, Quentin Anthony, Leo Gao, Laurence Golding, Horace He, Connor Leahy, Kyle McDonell, Jason Phang, et al. Gpt-neox-20b: An open-source autoregressive language model. arXiv preprint arXiv:2204.06745, 2022.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

Pierre Chambon, Christian Bluethgen, Jean-Benoit Delbrouck, Rogier Van der Sluijs, Małgorzata Połacin, Juan Manuel Zambrano Chaves, Tanishq Mathew Abraham, Shivanshu Purohit, Curtis P Langlotz, and

Akshay Chaudhari. Roentgen: vision-language foundation model for chest x-ray generation. arXiv preprint arXiv:2211.12737, 2022.

Zhihong Chen, Yan Song, Tsung-Hui Chang, and Xiang Wan. Generating radiology reports via memory-driven transformer. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing, November 2020.

Joseph Paul Cohen, Joseph D. Viviano, Paul Bertin, Paul Morrison, Parsa Torabian, Matteo Guarrera, Matthew P Lungren, Akshay Chaudhari, Rupert Brooks, Mohammad Hashir, and Hadrien Bertrand. TorchXRayVision: A library of chest X-ray datasets and models. In Medical Imaging with Deep Learning, 2022. URL https://github.com/mlmed/torchxrayvision.

Databricks. Free dolly: Introducing the world’s first truly open instruction-tuned llm. https://github.com/databrickslabs/dolly, 2023.

Jean-Benoit Delbrouck, Pierre Chambon, Christian Bluethgen, Emily Tsai, Omar Almusa, and Curtis P. Langlotz. Improving the factual correctness of radiology report generation with semantic rewards, 2022.

Dina Demner-Fushman, Marc D. Kohli, Marc B. Rosenman, Sonya E. Shooshan, Laritza Rodriguez, Sameer Antani, George R. Thoma, and Clement J. McDonald. Preparing a collection of radiology examinations for distribution and retrieval. 2016.

Patrick Esser, Robin Rombach, and Bjorn Ommer. Taming transformers for high-resolution image synthesis. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 12873–12883, 2021.

Jeremy Irvin, Pranav Rajpurkar, Michael Ko, Yifan Yu, Silviana Ciurea-Ilcus, Chris Chute, Henrik Marklund, Behzad Haghgoo, Robyn Ball, Katie Shpanskaya, et al. Chexpert: A large chest radiograph dataset with uncertainty labels and expert comparison. In Thirty-Third AAAI Conference on Artificial Intelligence, 2019.

Yang Jin, Kun Xu, Liwei Chen, Chao Liao, Jianchao Tan, Bin Chen, Chenyi Lei, An Liu, Chengru Song, Xiaoqiang Lei, et al. Unified language-vision pretraining with dynamic discrete visual tokenization. arXiv preprint arXiv:2309.04669, 2023.

Alistair EW Johnson, Tom J Pollard, Seth J Berkowitz, Nathaniel R Greenbaum, Matthew P Lungren, Chih-ying Deng, Roger G Mark, and Steven Horng. Mimic-cxr, a de-identified publicly available database of chest radiographs with free-text reports. Scientific data, 6(1):317, 2019a.

Alistair EW Johnson, Tom J Pollard, Nathaniel R Greenbaum, Matthew P Lungren, Chih-ying Deng, Yifan Peng, Zhiyong Lu, Roger G Mark, Seth J Berkowitz, and Steven Horng. Mimic-cxr-jpg, a large publicly available database of labeled chest radiographs. arXiv preprint arXiv:1901.07042, 2019b.

Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980, 2014.

Jing Yu Koh, Daniel Fried, and Ruslan Salakhutdinov. Generating images with multimodal language models. arXiv preprint arXiv:2305.17216, 2023a.

Jing Yu Koh, Ruslan Salakhutdinov, and Daniel Fried. Grounding language models to images for multimodal inputs and outputs, 2023b.

Mark A Kramer. Nonlinear principal component analysis using autoassociative neural networks. AIChE journal, 37(2):233–243, 1991.

Hyungyung Lee, Wonjae Kim, Jin-Hwa Kim, Tackeun Kim, Jihang Kim, Leonard Sunwoo, and Edward Choi. Unified chest x-ray and radiology report generation model with multi-view chest x-rays. arXiv preprint arXiv:2302.12172, 2023.

Junnan Li, Dongxu Li, Silvio Savarese, and Steven Hoi. Blip-2: Bootstrapping language-image pre-training with frozen image encoders and large language models, 2023.

Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae Lee. Visual instruction tuning, 2023.

Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. arXiv preprint arXiv:1711.05101, 2017.

Jiasen Lu, Christopher Clark, Rowan Zellers, Roozbeh Mottaghi, and Aniruddha Kembhavi. Unified-io: A unified model for vision, language, and multi-modal tasks. arXiv preprint arXiv:2206.08916, 2022.

Michael Moor, Qian Huang, Shirley Wu, Michihiro Yasunaga, Cyril Zakka, Yash Dalmia, Eduardo Pontes Reis, Pranav Rajpurkar, and Jure Leskovec. Med-flamingo: a multimodal medical few-shot learner. arXiv preprint arXiv:2307.15189, 2023.

OpenAI. Introducing chatgpt. https://openai.com/blog/chatgpt, 2022.

OpenAI. Gpt-4 technical report, 2023.

Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever, et al. Improving language understanding by generative pre-training. 2018.

Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos Guestrin, Percy Liang, and Tatsunori B. Hashimoto. Stanford alpaca: An instruction-following llama model. https://github.com/tatsu-lab/stanford\_alpaca, 2023.

Omkar Thawkar, Abdelrahman Shaker, Sahal Shaji Mullappilly, Hisham Cholakkal, Rao Muhammad Anwer, Salman Khan, Jorma Laaksonen, and Fahad Shahbaz Khan. Xraygpt: Chest radiographs summarization using medical vision-language models. arXiv preprint arXiv:2306.07971, 2023.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.

Aaron Van Den Oord, Oriol Vinyals, et al. Neural discrete representation learning. Advances in neural information processing systems, 30, 2017.

Peng Wang, An Yang, Rui Men, Junyang Lin, Shuai Bai, Zhikang Li, Jianxin Ma, Chang Zhou, Jingren Zhou, and Hongxia Yang. Ofa: Unifying architectures, tasks, and modalities through a simple sequence-to-sequence learning framework. In International Conference on Machine Learning, pp. 23318–23340. PMLR, 2022a.

Yizhong Wang, Yeganeh Kordi, Swaroop Mishra, Alisa Liu, Noah A Smith, Daniel Khashabi, and Hannaneh Hajishirzi. Self-instruct: Aligning language model with self generated instructions. arXiv preprint arXiv:2212.10560, 2022b.

Zifeng Wang, Zhenbang Wu, Dinesh Agarwal, and Jimeng Sun. Medclip: Contrastive learning from unpaired medical images and text, 2022c.

Jason Wei, Maarten Bosma, Vincent Y Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M Dai, and Quoc V Le. Finetuned language models are zero-shot learners. arXiv preprint arXiv:2109.01652, 2021.

Chaoyi Wu, Xiaoman Zhang, Ya Zhang, Yanfeng Wang, and Weidi Xie. Towards generalist foundation model for radiology. arXiv preprint arXiv:2308.02463, 2023a.

Shengqiong Wu, Hao Fei, Leigang Qu, Wei Ji, and Tat-Seng Chua. Next-gpt: Any-to-any multimodal llm. arXiv preprint arXiv:2309.05519, 2023b.

Shawn Xu, Lin Yang, Christopher Kelly, Marcin Sieniek, Timo Kohlberger, Martin Ma, Wei-Hung Weng, Atilla Kiraly, Sahar Kazemzadeh, Zakkai Melamed, Jungyeon Park, Patricia MacWilliams, Yun Liu, Chuck Lau, Preeti Singh, Christina Chen, Mozziyar Etemadi, Sreenivasa Raju Kalidindi, Kat Chou, Greg Corrado, Shravya Shetty, Daniel Tse, Shruthi Prabhakara, Daniel Golden, Rory Pilgrim, Krish Eswaran, Andrew Sellergren, and Yossi Matias. Elixr: Towards a general purpose x-ray artificial intelligence system through alignment of large language models and radiology vision encoders. arxiv, 2023a. URL https://arxiv.org/abs/2308.01317.

Shawn Xu, Lin Yang, Christopher Kelly, Marcin Sieniek, Timo Kohlberger, Martin Ma, Wei-Hung Weng, Attila Kiraly, Sahar Kazemzadeh, Zakkai Melamed, et al. Elixr: Towards a general purpose x-ray artificial intelligence system through alignment of large language models and radiology vision encoders. arXiv preprint arXiv:2308.01317, 2023b.

Han Zhang, Weichong Yin, Yewei Fang, Lanxin Li, Boqiang Duan, Zhihua Wu, Yu Sun, Hao Tian, Hua Wu, and Haifeng Wang. Ernie-vilg: Unified generative pre-training for bidirectional vision-language generation. arXiv preprint arXiv:2112.15283, 2021.

Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shechtman, and Oliver Wang. The unreasonable effectiveness of deep features as a perceptual metric. In CVPR, 2018.

Deyao Zhu, Jun Chen, Xiaoqian Shen, Xiang Li, and Mohamed Elhoseiny. Minigpt-4: Enhancing visionlanguage understanding with advanced large language models. arXiv preprint arXiv:2304.10592, 2023.

## SUPPLEMENTARY MATERIAL

## A IMPLEMENTATIONS DETAILS

Dataset We used MIMIC-CXR v2.0.0 (Johnson et al., 2019a) as our dataset of CXR-report pairs. The data set consists of 377,110 CXRs from 227,835 radiology studies. The train-test split used the standard split of MIMIC-CXR-JPG (Johnson et al., 2019b). The test set sizes before and after pruning are 368,960 and 70,403, respectively. The test set was created using only AP/PA views from the raw data set excluding the train set, with a total of 3,530. The original images are files of various sizes, but the images were converted into JPEGs of square 256×256 images.

Training VQ-GAN We trained the VQ-GAN (Esser et al., 2021) on 256×256 MIMIC-CXR train data starting from the pretrained weight and configuration of the imagenet\_f16\_1024 model. For clinical information-preserving loss, 1024-dimensional features were extracted with TorchXRayVision’s (Cohen et al., 2022) densenet121-res224-all model of the target image and the reconstructed image, and then the L2 distance of the two features was used. At this time, the loss was multiplied by 100 as the weight and added to the total loss. The number of indices in the codebook $K _ { i m g }$ is 1024 and the dimension of the codebook embedding $n _ { z }$ is 256. Since a 256×256 image is encoded and quantized with a 16×16 matrix by encoder and quantizer, the dimension of the quantized latent vector (i.e., image tokens) of the image $d _ { z }$ is 256 by flattening it. Model training was performed for 590k steps with the Adam (Kingma & Ba, 2014) optimizer, with a batch size of 2 and a learning rate of 4.5e-6.

Fine-tunning LLM We used the dolly-v2-3b (Databricks, 2023) model, which is fine-tuned for the instruction-following task based on the GPT-NeoX (Black et al., 2022) architecture, as a base model. The model has a total of 2.8 billion parameters and has 50821 token types $( K _ { t e x t } )$ . We have extended the number of entries in the token embedding table to 51845 $( K _ { t e x t } + K _ { i m g } )$ ), as an additional 1024 $( K _ { i m g } )$ new image tokens should be available. For each image token from the VQ-GAN encoder, the value obtained by adding $K _ { t e x t }$ to each image token value is input to the LLM as a token ID. If the token output from the model is treated as an image token if the ID is greater than or equal to $K _ { t e x t } .$ , and each $K _ { t e x t }$ is subtracted and input to the VQ-GAN decoder.

Model training was performed with a learning rate of 5e-6 and a batch size of 16 using the AdamW (Loshchilov & Hutter, 2017) optimizer at all stages. Stage 1 uses 76k steps as 2 epochs and stage 2 uses 9k steps as 1 epoch for training. Training took about 14.5 hours for stage 1 and about 1.5 hours for stage 2 using NVIDIA A100 40GB ×8. The proportions of CXR-to-report, report-to-CXR, CXR-VQA, and NL-IF in the data set are [30%, 30%, 20%, 20%] and [21%, 21%, 63%, 5%], for stage 1 and stage 2, respectively.

## B SYNTHETIC VQA GENERATION

We locally used LlaMa 2 (Llama2-13b-chat-hf) Touvron et al. (2023) to generate the synthetic VQAs. Radiology reports used were filtered from the MIMIC-CXR dataset through the method mentioned in the text, and a total of 27,322 were used. The following prompt was used to generate about 5 questions and answers using a chest X-ray report in MIMIC-CXR.

You are a radiologist asking questions about a chest X-ray image.   
You always give long, detailed explanations as answers.   
You are given a chest X-ray, delimited by triple backticks.   
Create some questions   
about the chest X-ray, each question followed by an appropriate answer.   
Output your questions and answers in JSON format like:   
[{{"question": "<question1>", "answer": "<answer1>"}},   
{{"question": "<question2>", "answer": "<answer2>"}}, ...].   
‘‘‘   
{report}   
III

Note, questions are never   
about any change from the last or previous chest X-ray scans or CTs.   
Questions are also never   
about future plans; questions always focus on the chest X-ray itself.   
Answers are very detailed and   
include explanations without repeating words that are in the question.   
Here are the questions and answers:

We generated a total of 126,795 question-answer pairs using the described method. All question-answer pairs from stage 1, along with 75,100 pairs randomly extracted in stage 2, were employed for training purposes. The train-test split followed the MIMIC-CXR official split to which the source report belongs. Following are some examples of generated VQAs:

Q: What   
is the most likely cause of the subtle opacity at the right lung base?   
A: Early pneumonia is the most likely cause of the subtle opacity   
at the right lung base, as there is no pleural effusion or pneumothorax.   
Q: Is there any pleural effusion?   
A: No, there is no pleural effusion present in the chest X-ray.   
Q: Is there any pneumothorax?   
A: No, there is no pneumothorax present in the chest X-ray.   
Q: What is the appearance of the mediastinal silhouette and hila?   
A: The mediastinal silhouette and hila appear normal in the chest X-ray.   
Q: What is the impression based on the chest X-ray?   
A: The impression based on the chest X-ray is subtle   
opacity at the right lung base, which could represent early pneumonia.

## C TEMPLATE FOR LLM INSTRUCTIONS

Following is the template of the prompt for instruction fine-tuning from the Alpaca family which consists of Instruction, Input, Response sections. This template is employed consistently in both the instruction-following tuning process and the inference process. During inference, the model functions to predict tokens following the response key (### Response:).

Below is an instruction that describes a   
task. Write a response that appropriately completes the request.   
### Instruction:   
{instruction}   
Input:   
{input}   
### Response:   
{response}   
### End

## D ADDITIONAL EXPERIMENT RESULTS

Additional experimental results that were not covered in the main text due to space constraints are shown in Table 5 and Table 6.

Table 5: CXR-to-Report NLG Metrics.
<table><tr><td>↑</td><td>BLEU1</td><td>BLEU2</td><td>BLEU3</td><td>BLEU4</td><td>METEOR</td><td>ROUGE L</td><td>CIDEr</td></tr><tr><td>RadFM</td><td>0.1344</td><td>0.0650</td><td>0.0362</td><td>0.0221</td><td>0.0867</td><td>0.1064</td><td>0.0264</td></tr><tr><td>UniXGen-512</td><td>0.1471</td><td>0.0736</td><td>0.0403</td><td>0.0233</td><td>0.0813</td><td>0.1331</td><td>0.1413</td></tr><tr><td>IFCC</td><td>0.0636</td><td>0.0268</td><td>0.0106</td><td>0.0040</td><td>0.0809</td><td>0.0673</td><td>0.0058</td></tr><tr><td>R2Gen</td><td>0.0898</td><td>0.0359</td><td>0.0134</td><td>0.0057</td><td>0.0822</td><td>0.0734</td><td>0.0104</td></tr><tr><td>UniXGen-256</td><td>0.1287</td><td>0.0570</td><td>0.0264</td><td>0.0137</td><td>0.0725</td><td>0.0893</td><td>0.0399</td></tr><tr><td>XrayGPT</td><td>0.1002</td><td>0.0417</td><td>0.0178</td><td>0.0075</td><td>0.1038</td><td>0.0907</td><td>0.0139</td></tr><tr><td>LLM-CXR</td><td>0.0920</td><td>0.0459</td><td>0.0260</td><td>0.0154</td><td>0.0690</td><td>0.1618</td><td>0.5248</td></tr></table>

Table 6: FID of generated CXRs from reports.3
<table><tr><td>FID</td><td>inception-v3-2048 ↓</td><td>txv-all-1024 ↓</td></tr><tr><td>UniXGen</td><td>78.19</td><td>7.894</td></tr><tr><td>RoentGen</td><td>42.38</td><td>6.039</td></tr><tr><td>LLM-CXR</td><td>22.75</td><td>0.7136</td></tr></table>

## E ABLATION STUDIES AND DISCUSSION

We conducted a comprehensive ablation study to provide a rigorous justification for the design choices made in our method. This ablation analysis specifically focused on the CXR-to-report and report-to-CXR tasks and was evaluated using the same evaluation metrics as those outlined in the main text.

In this ablation study, we systematically removed one element at a time from our method to assess its impact. The factors subjected to ablation included the clinical information-preserving loss (CIP loss), simultaneous training of the CXR-VQA task (CXR-VQA), the use of the entire dataset by the additional training (stage 1 tr.) instead of using only pruned dataset, and the adoption of instruction tuning loss $L _ { i n s t r u c t }$ during fine-tuning as opposed to the joint loss $L _ { j o i n t }$ (instruct tr.).

Table 7: CXR-to-report generation AUROC and F1.
<table><tr><td rowspan="2"></td><td colspan="3">AUROC ↑</td><td colspan="3">F1↑</td></tr><tr><td>Micro</td><td>Macro</td><td>Weighted</td><td>Micro</td><td>Macro</td><td>Weighted</td></tr><tr><td>LLM-CXR</td><td>0.6285</td><td>0.5553</td><td>0.5969</td><td>0.3604</td><td>0.2113</td><td>0.3504</td></tr><tr><td> CIP loss</td><td>0.6170</td><td>0.5495</td><td>0.5853</td><td>0.3418</td><td>0.1994</td><td>0.3260</td></tr><tr><td>CXR-VQA</td><td>0.6143</td><td>0.5492</td><td>0.5846</td><td>0.3378</td><td>0.1945</td><td>0.3173</td></tr><tr><td> stage1 tr.</td><td>0.5770</td><td>0.5242</td><td>0.5435</td><td>0.2659</td><td>0.1347</td><td>0.2253</td></tr><tr><td>instruct tr.</td><td>0.6071</td><td>0.5422</td><td>0.5745</td><td>0.3203</td><td>0.1927</td><td>0.3161</td></tr></table>

The findings from our CXR-to-report ablation study (Table 7) highlight the positive contributions of all ablation factors toward enhancing the model’s performance. Notably, the incorporation of stage 2 training, which involves initially training with the full dataset, and the generation of the CXR-VQA dataset through augmentation, alongside simultaneous CXR-VQA task training, led to a substantial improvement in the alignment between images and reports within the CXR-to-report task.

This improvement can be attributed to several factors. Firstly, the significantly increased volume of image-report pairs during stage 1 training enabled more accurate learning of common image-report relationships, even though the additional dataset may not be directly related to our final tasks. Secondly, the CXR-VQA task provided direct supervision in comprehending and answering specific image characteristics, in contrast to the report generation task, where information about a single image is distributed and represented. Consequently, these results suggest that the capacity to understand and respond to images acquired through the VQA task not only enhanced performance within the VQA task but also improved the overall quality of report generation.

Table 8: Report-to-CXR generation AUROC and F1.
<table><tr><td rowspan="2"></td><td colspan="3">AUROC↑</td><td colspan="3">F1↑</td></tr><tr><td>Micro</td><td>Macro</td><td>Weighted</td><td>Micro</td><td>Macro</td><td>Weighted</td></tr><tr><td>LLM-CXR</td><td>0.8065</td><td>0.8025</td><td>0.8054</td><td>0.7907</td><td>0.7980</td><td>0.7991</td></tr><tr><td> CIP loss</td><td>0.8227</td><td>0.8196</td><td>0.8223</td><td>0.7890</td><td>0.7971</td><td>0.7977</td></tr><tr><td>- CXR-VQA</td><td>0.7505</td><td>0.7433</td><td>0.7465</td><td>0.7841</td><td>0.7871</td><td>0.7876</td></tr><tr><td> stage1 tr.</td><td>0.7213</td><td>0.7125</td><td>0.7167</td><td>0.7217</td><td>0.7224</td><td>0.7231</td></tr><tr><td> instruct tr.</td><td>0.5839</td><td>0.5751</td><td>0.5808</td><td>0.6040</td><td>0.5959</td><td>0.5965</td></tr></table>

In the case of the report-to-CXR task (Table 8), most design choices led to unambiguous improvements. However, the addition of the clinical information-preserving (CIP) loss shows conflicting effects by decreasing AUROC whilst increasing the F1-score. This may be due to better performance for minority classes with smaller support (e.g. pneumonia, enlarged cardiomediastinum) but lower performance for the more common majority classes (e.g. normal, pleural effusion). Taking into account that the incorporation of the CIP loss resulted in a substantial performance boost in the CXR-to-report task, we view this as a favorable trade-off within the constraints of the limited capacity of a small model such as dolly-v2-3b.

Table 9: FID of generated CXRs from reports.3
<table><tr><td>FID ↓</td><td>inception-v3-2048</td><td>txv-all-1024</td></tr><tr><td>LLM-CXR</td><td>22.75</td><td>0.714</td></tr><tr><td>-CIP loss</td><td>20.93</td><td>0.931</td></tr><tr><td>CXR-VQA</td><td>32.55</td><td>1.539</td></tr><tr><td>stagel tr.</td><td>32.05</td><td>1.226</td></tr><tr><td>instruct tr.</td><td>21.51</td><td>1.477</td></tr></table>

We also measure FID score for generated CXR images (Table 9). All design choices lead to a decrease (improvement) in the FID score when measured using a CXR-specific classifier network (txv-all-1024). Certain techniques increase (worsen) the FID score measured using the Inception-V3 network. This is most likely due to the fact that our framework generates images that closely match the distribution of real CXR images so that features extracted from a network trained only on natural images such as the Inception-V3 cannot distinguish the subtleties in the generated images. Therefore, FID scores measured using txv-all-1024 are more appropriate for image quality assessment, and thus all techniques employed in the final model (LLM-CXR) can be interpreted as increasing generated CXR image quality.

## F INSTRUCTIONS FOR MULTIMODAL TASKS

For the diversity of instructions, in the process of training and inference, one instruction is randomly sampled and used from the list of 10 instructions below. The instructions were modulated to 10 using OpenAI’s ChatGPT (OpenAI, 2022) from the basic instruction.

## CXR-to-Report task

• Generate free-text radiology reports for the entered chest X-ray images.

• Use the entered chest X-ray images to create corresponding free-text radiology reports.

• Based on the entered chest X-ray images, produce free-text radiology reports.

• Create free-text radiology reports that correspond to the entered chest X-ray images.

• Utilize the entered chest X-ray images to generate corresponding free-text radiology reports.

• Generate free-text radiology reports in accordance with the entered chest X-ray images.

• Use the entered chest X-ray images to create accurate free-text radiology reports.

• Produce free-text radiology reports that match the entered chest X-ray images.

• Create free-text radiology reports that are consistent with the entered chest X-ray images.

• Utilize the entered chest X-ray images to generate comprehensive free-text radiology reports.

## Report-to-CXR task

• Generate a chest X-ray image that corresponds to the entered free-text radiology reports for the chest X-ray image.

• Use the free-text radiology reports for the chest X-ray image to produce a corresponding chest X-ray image.

• Utilize the entered free-text radiology reports for the chest X-ray image to create a corresponding chest X-ray image.

• Create a chest X-ray image that matches the free-text radiology reports entered for the chest X-ray image.

• Produce a chest X-ray image that is consistent with the free-text radiology reports entered for the chest X-ray image.

• Based on the free-text radiology reports for the chest X-ray image, generate a corresponding chest X-ray image.

• Use the free-text radiology reports entered for the chest X-ray image to create a corresponding chest X-ray image.

• Generate a chest X-ray image that is in accordance with the free-text radiology reports for the chest X-ray image entered.

• Create a chest X-ray image that corresponds to the free-text radiology reports entered for the chest X-ray image.

• Utilize the entered free-text radiology reports for the chest X-ray image to produce a corresponding chest X-ray image.

## G REPOR-TO-CXR: MORE EXAMPLES

Semantic descriptions of pathologies Radiology reports describe the semantic features of pathologies as they appear on the CXR scan. The most common descriptions involve location and severity. Here we show that our model incorporates features described in radiology reports when generating corresponding CXR images (Figure 6).

Artificial devices Artificial devices are frequently captured in CXR images and reports. They have semantic features that are different from physiologic or pathologic features. We show that our model has learned to generate the general appearance of these devices (Figure 7).

![](images/8340722f163cb9f41604222703c5141b9b386e6de1715f5ec9971c0362058c37.jpg)  
Figure 6: CXRs generated for different descriptions of pathologies. The model is able to accurately capture different levels of severity in the generated CXRs (b, c) and generate lesions in specified locations (d, e).

(a)   
"No acute   
cardiopulmonary process. (b)   
A new dual-lead   
pacemaker with lead positioned through the left transvenous   
approach end into the right ventricle and is appropriate."

(c) AICD in correct position."

![](images/6ef99b5d34c86f9c66b13466d30c93cb5e27d822dff8c4e525c5254ab7f5944e.jpg)  
Figure 7: CXRs generated for radiology reports describing various foreign bodies. Reports of normal CXRs (a) and of large features such as pacemakers or AICDs (b, c) are realistically reflected in the generated images. Reports describing smaller, more detailed features such as endotracheal tubes and central venous catheters are represented in the generated CXRs but less accurately (d, e), with deterioration in image quality around the neighborhood of the described feature (e.g., the trachea is not cleanly generated when the input report describes an endotracheal tube in (d)) or imperfect representation of feature itself (e.g., venous catheters are generated but show missing parts in (e)).

## H CXR-TO-REPORT: MORE EXAMPLES

<table><tr><td></td><td>Radiologist&#x27;s Impression (GT)</td><td>Generated Impression (ours)</td></tr><tr><td rowspan="5"></td><td>(a) &quot;“.….Low lung volumes. Areas of</td><td>“Low lung volumes with patchy and streaky opacities most likely</td></tr><tr><td>atelectasis at both left and right lung basis. No pleural effusions. No pneumonia&quot;</td><td>reflective of atelectasis. Infection or aspiration cannot be excluded in the correct clinical setting...&quot;</td></tr><tr><td>(b) &quot;Moderately severe pulmonary edema..&quot;</td><td>Moderate pulmonary edema.&quot;</td></tr><tr><td>(c) Mild pulmonary edema is stable .… Cardiomegaly is accentuated by the low lung volumes.&quot;</td><td>&quot;Enlarged cardiac silhouette and interstitial pulmonary edema.&quot;</td></tr><tr><td>(d) Increased markings bilaterally may be due to the combination of underlying pulmonary fibrosis and moderate pulmonary edema, superimposed infectious process</td><td>&quot;Slight increase in multifocal opacities which could be due to infection or mild pulmonary edema.&quot;</td></tr><tr><td></td><td>cannot be excluded.&quot; (e) “Moderate cardiomegaly with AICD in unchanged position. No evidence of congestive heart failure or pneumonia.&quot;</td><td>Pacer device leads terminating in the expected location of right atrium and right ventricle.&quot;</td></tr></table>

Figure 8: Generated reports contain not only diagnoses but also descriptions of pathologies present in CXR images such as ‘low lung volumes’, and ‘patchy and streaky opacities’ (a). While the exact wording may differ from the ground-truth text report, generated reports are able to often capture the gist of the findings in the CXR images (“moderately severe” vs. “moderate” in (b); “cardiomegaly” vs. “enlarged cardiac silhouette” in (c)). Suggestions for potential pathologic processes that underlie the findings in the CXR also align with ground-truth reports (d). Generated reports also note the presence of artificial devices such as pacemakers (here, an AICD is recognized as a pacemaker as the distinction relies on finer details that would require further training to reliably distinguish (e)).†
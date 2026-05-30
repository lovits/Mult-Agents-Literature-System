# LMRL Gym: Benchmarks for Multi-Turn Reinforcement Learning with Language Models

OpenReview ID: 8cNMMrWRbZ
Decision: Reject

## Abstract
Large language models (LLMs) provide excellent text-generation capabilities, but standard prompting and generation methods generally do not lead to intentional or goal-directed agents and might necessitate considerable prompt tuning. This becomes particularly apparent in multi-turn conversations: even the best current LLMs rarely ask clarifying questions, engage in explicit information gathering, or take actions now that lead to better decisions after multiple turns. Reinforcement learning has the potential to leverage the powerful modeling capabilities of LLMs, as well as their internal representation of textual interactions, to create capable goal-directed language agents. This can enable intentional and temporally extended interactions, such as with humans, through coordinated persuasion and carefully crafted questions, or in goal-directed play through text games to bring about desired final outcomes. However, enabling this requires the community to develop stable and reliable reinforcement learning algorithms that can effectively train LLMs. Developing such algorithms requires tasks that can gauge progress on algorithm design, provide accessible and reproducible evaluations for multi-turn interactions, and cover a range of task properties and challenges in improving reinforcement learning algorithms. Our paper introduces the LMRL-Gym benchmark for evaluating multi-turn RL for LLMs, together with an open-source research framework containing a basic toolkit for getting started on multi-turn RL with offline value-based and policy-based RL methods. Our benchmark consists of 8 different language tasks, which require multiple rounds of language interaction and cover a range of tasks in open-ended dialogue and text games

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper introduces **LMRL-Gym**, consisting of **8 tasks** ranging from simple navigation (Maze) to strategy games (Chess) to negotiation (Car Dealer).

They also provide a **research toolkit** for practitioners to get started with multi-turn RL for LLMs.

This benchmark is created for evaluating RL algorithms in multi-turn language-based interaction tasks using LLMs as agents and simulators.

It provides a research framework and discusses the key challenges and capabilities involved in training RL algorithms for LLMs. 

The goal is to advance the development of more effective RL methods for language-based interactions, including complex decision-making scenarios and conversational interactions, with a focus on accessibility for researchers with varying computational resources.

#### Strengths
1. Present a useful **dataset**: It proposed a novel and significant challenge in the field of reinforcement learning and natural language processing, focusing on the application of RL algorithms to Large Language Models (LLMs) for multi-turn language-based interactions.

2. The **Data Generation Approach** can be used for collecting more data.

3. They designed **8 tasks** in the LMRL-Gym benchmark to **evaluate** the core capabilities that RL can enable in large language models. Their evaluation shows the promise of RL in several tasks, with further room for improvement with a push for better methods. 

4. It provides a **clear explanation** of the motivation behind benchmarking RL algorithms for LLMs and the need for such an evaluation framework.

#### Weaknesses
1. LLM with RL/PPO in this complicated task is very sensitive to the hyper-parameters. I did not find the analysis or report on these. 

2. The Data Generation Approach is a little disappointing. I did not find the details that can replicate this process or any validation of the data. How can I make sure these data can be used to evaluate RL?

3. The baseline results are not convincing enough. PPO Instabilities in GPT-2-small are very obvious. I do not think the results in the benchmark should only use GPT-2-small. Any technique you use here to overcome it?

#### Questions
1. Any details about the hyperparameters for baselines? Thanks.

2. Any validation of the data generation process? How to make sure the game/task you generate is POMDP?

3. How to replicate the data generation process?

4. How did you evaluate the quality of your data?

5. I think I might miss it. You use the data from the GPT-3.5 and create several games for the 8 tasks?

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The authors propose a set of environments that can be used to assess the ability of RL algorithms to fine tune and/or train LLMs. The creation of the benchmark is intended to enable evaluating different RL algorithms on multi-turn, language-based tasks. All environment state and action spaces are expressed solely in language. The set of tasks include a maze, a house-based maze, World, chess, chess endgames, twenty questions, guess my city, and car dealer. The environments are selected/designed to evaluate different capabilities that are expected from a LLM, such as common sense reasoning, credit assignment, reasoning under uncertainty, information seeking behaviors, and trajectory stitching. Where an environment requires dialogue-like interactions (i.e. 20 questions, guess my city, and car dealer), an GPT2 train on environment-specific data is used to provide the environment responses. The environments are designed not to assess the ability of LLM to communicate with humans, but to assess how well they can solve different reasoning tasks.

#### Strengths
- The paper is well written and easy to follow
- The benchmark provides a way to quantitatively measure different LLM reasoning abilities, specifically for several environments, open vocabulary tasks are assessed.

#### Weaknesses
- The authors motivate that a large part of the goal is to assess how well RL algorithms perform on language-based tasks, but they do not provide evidence that RL algorithm performance differences on non-language tasks does not correlate with algorithm performance on language-based tasks. As the environments are on the contrived side, it is not clear they address the challenges associated with training LLMs.
- While the state and action spaces are language-based, it is not clear the extent to which some of the environments assess performance on language-based tasks, such as the maze, chess, and chess endgames. While the environments assess reasoning abilities, they do not assess the full complexity of reasoning abilities a LLM needs nor abilities that are key to LLM success. The reasoning abilities are more general abilities we would want from a RL-train agent. For example, it is important for LLMs to be factual and harmless, which means correcting behavior learned during pretraining.
- It is not clear what safeguards are in place to prevent hacking of the LLM that is part of the environment.

#### Questions
- To what extent does the policy's actions on the environments like 20Qs, car dealer, and guess my city look like reasonable sentences?
- For some of the environments the specific skills addressed are called out. It would be great to highlight the assessed skills for each environment.
- Are there other LLM-specific policy learning algorithms that can be assessed?
- To what extent are the performance differences between RL algorithms proportional to their differences on non-language based tasks?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes a new benchmark of reinforcement learning on language models in multi-turn scenarios. The proposed benchmark called LMRL-Gym includes 8 different tasks, covering open-ended dialogue and text games. These tasks require the five capabilities of LM that can be enabled by RL: complex decision making, complex language, credit assignment, partial observability, and trajectory stitching. The authors applied supervised fine-tuning (defined as behavior cloning (BC) in this paper), value-based offline-RL, and online PPO to form the baselines for the proposed benchmark. The results show that RL can improve BC and still leave room for improvement.

#### Strengths
* This benchmark can be useful for comparison of RL algorithms on multi-turn text generation. This area is less explored compared with single-turn.
* The proposed benchmark considers diverse tasks from text game to open-ended conversation, and considers different dimensions of LM capabilities RL can perhaps help. 
* Most of the writing is clear.

#### Weaknesses
* The benchmark is artificial and quite less natural. Only two of the eight tasks (Car Dealer and Guess My City) is multi-turn conversation or conversational QA with more unbounded state and action space. All other tasks have obvious restrictions, especially, the Chess and Endgames tasks are not natural language generation to me.
* The experiments section can be improved by providing more analysis. For example, the authors can analyze which capability in Section 4.1 is easier or less likely to be improved. Also, the authors can consider how to disentangle the evaluation of capabilities in each task.
* Generated examples by the trained agents can be added. Although the authors have put emphasis on “our goal is not to utilize this approach to benchmark whether LLMs are good at talking to humans, but rather as a way to test RL algorithms with datasets that are sufficiently difficult and complex so as to gauge how effective they might be if they were then trained on data from real humans.“ in Introduction, it is good to see how relevant the obtained rewards and the conversation's naturalness are.
* While the paper claims to focus on LLM, the experiments are conducted on GPT2-small and medium (according to Table3), which may be controversial. I’m also confused by the contradiction in Section 7 and Table3. In Section 7, the authors say they “primarily trained and evaluated models with a maximum 1.5B parameters”, but Table3 shows the experiments are conducted on less than 355M parameters. Therefore, I’m wondering how large is the trained agent in Table2 actually?
* The writing of section 4.1 can be further improved. For now, I can guess the meaning from the terminologies themselves, but I will get confused from the content in each paragraph trying to explain the corresponding terminology.

#### Questions
* Does the timestep in Table 1 mean for one response instead of for one token, and the length mean the number of turns in a conversation?  If so, the wording of timestep and length may be a bit confusing with the terminologies in single-turn text generation, where the timestep often refers to the step of generating a token and the length often refers to how many tokens per response.
* Why the avg length for 20Qs and Guess in Table 1 are negative?
* How many different state-action pairs exist in the dataset for offline training?
* Some details can be moved from Appendix B to section 4.3. For example, the desired capability for every task. For now some are left in the appendix.
* Typos:
  * Is the Twenty Questions task example in Figure 2 needed to exchange the labels of environment and agent? I guess it should be the environment to say yes or no, but not the agent.
  * There is no reference to table in Appendix C (which is mentioned in section 5.1). I guess Appendix C should mention Table 3 in it.
  * Do the authors actually mean “do NOT consider” in Section 2 - 2nd paragraph? The original sentence: “However, many of these works operate in the single-step bandit setting, and do consider multi-turn goal-directed tasks.”
  * Typo: Section 3.1 POMPDP -> POMDP

### Review 4
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper introduces LMRL-Gym, a benchmark for evaluating reinforcement learning (RL) algorithms for training large language models (LLMs) on multi-turn tasks. The benchmark consists of 8 tasks spanning open-ended dialogue, strategic games, and tool use. The tasks are designed to test core capabilities like complex decision making, handling complex language, credit assignment, and partial observability. The authors benchmark training methods like offline RL algorithms (ILQL), online RL algorithms like PPO and supervised fine-tuning (BC) on their tasks.

#### Strengths
- Establishes an accessible benchmark to drive progress on an important open problem - multi-turn RL for language models. This direction for development is timely and much needed. There are no systematic benchmarks available.
- Well motivated, it is easy to follow and clear in writing.
- Tasks are designed in a modular fashion, starting from simple unit tests and building up complexity.
This enables systematic testing of capabilities.
- Provides datasets, evaluation protocols, baseline implementations - lowers barriers to entry for future research.
- The authors make a clear distinction of the purpose of their paper: To test RL methods on sufficiently complex tasks with LLMs
- The authors have a good breadth of methods that they test with the
- Broad set of baseline algorithms are evaluated.

#### Weaknesses
- The reasoning and generalization required on each task needs to be formalized more clearly. What inferences must the model make? How different are test vs training distributions? This formalization will further help understand how the complexity of tasks varies across different tasks.
- An alternative to improve interaction and performance at tasks is to use prompting and factoring of LLM calls. I found a discussion on prompting vs RL training as alternatives to each other missing.
- For complex tests,  20 questions, guess the city, car dealership where the model relies on GPT-3.5 for the initial test and GPT-2 for the env, there need to be evaluations of the text produced by the models.
    - The dependent measure would be non-sensical if the fixed model is not ‘rational’ at interacting with the model being tested.
    - GPT-3.5-turbo could be inconsistent. And the finetuned GPT-2 model could be too!
    - The measure cant be trusted if the environment itself is inconsistent.
    - This further leads to the question if the environment is easily prone to hacking! There should at least be qualitative trajectories that show the measure and the environment are reasonable. A trained model could figure out a weakness of the eval gpt-2 model to gain a higher reward.
- In wordle, i’d love to see a discussion of how the authors deal with the tokenization. Since the models are bad at tasks where individual characters need to be tokenized.
- Why did the authors not choose to start with human data in domains where that was available? Eg: Craigslist dataset, Deal or No Deal
- In the car dealership case App B8, a negotiation setting, the values of the interacting agents are much more interesting than their personalities. I would have loved to see a negotiation setting where the values of the buyers are varied and not just 3 discrete buckets that buyers and sellers are put into.
- There are no error bars for the RL methods. The authors should report least report 5 runs.
- The social/ethical implications section is incomplete: Dual use concerns around persuasion, manipulation, and addictive engagement should be discussed given interactive RL.

#### Questions
Questions and suggestions gave been included in the weaknesses above.

## Meta Reviews

### Meta Review 1
The paper introduces LMRL-Gym, a benchmark for evaluating reinforcement learning algorithms in training LLMs for multi-turn tasks. It encompasses eight diverse tasks, such as open-ended dialogue and strategic games, designed to assess desirable capabilities for RL algorithms, including strategic decision-making and credit assignment. The benchmark evaluates various training methods, including offline and online RL algorithms and supervised fine-tuning. As such, LMRL-Gym could significantly contribute to the community. However, after the reviewer-AC discussion and reviewing the authors' responses, several reviewers remain unconvinced due to the following limitations:

1. The experiments in the paper are relatively lightweight for a benchmarking paper. For instance, there are no error bars in the results, although error bars are crucial in reporting RL results. The authors should ideally report results from at least five runs. While the author response mentioned computational challenges in adding such experiments, this absence is a significant drawback for a paper about benchmarking. The reviewers also found the human study to be relatively small and suggested several improvements to the experimental section.
2. Reward Hacking: It is unclear what safeguards are in place to prevent hacking of the LLM that is part of the environment. Generally, there should be more attempts to demonstrate the environment's robustness against simple reward hacking, especially involving a fine-tuned model that dictates the dependent measure. Although the authors responded to one of the two reviewers who raised concerns about reward hacking, the reviewers remain unconvinced. The next version of the paper should directly address this issue.
3. LMRL-Gym’s focus on artificial tasks: More a restriction than a flaw, LMRL-Gym focuses significantly more on artificial tasks, like Mazes and Chess, than on natural ones, such as open-ended dialogue. Only two tasks (Car Dealer and Guess My City) involve natural multi-turn conversation or conversational QA with more unbounded state and action spaces, and they are domain-specific. This focus makes LMRL-Gym quite artificial compared to other LM-related tasks that the community is already working on using RL.

Considering these limitations and the continued skepticism of some reviewers, I recommend rejecting the paper. However, the reviewers and I generally agree that this work has great potential. If the authors incorporate the reviewers' suggestions, this could become a strong and interesting paper.

## Decisions

Decision: Reject

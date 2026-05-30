# LMRL GYM: BENCHMARKS FOR MULTI-TURN RE-INFORCEMENT LEARNING WITH LANGUAGE MODELS

Anonymous authors Paper under double-blind review

## ABSTRACT

Large language models (LLMs) provide excellent text-generation capabilities, but standard prompting and generation methods generally do not lead to intentional or goal-directed agents and might necessitate considerable prompt tuning. This becomes particularly apparent in multi-turn conversations: even the best current LLMs rarely ask clarifying questions, engage in explicit information gathering, or take actions now that lead to better decisions after multiple turns. Reinforcement learning has the potential to leverage the powerful modeling capabilities of LLMs, as well as their internal representation of textual interactions, to create capable goal-directed language agents. This can enable intentional and temporally extended interactions, such as with humans, through coordinated persuasion and carefully crafted questions, or in goal-directed play through text games to bring about desired final outcomes. However, enabling this requires the community to develop stable and reliable reinforcement learning algorithms that can effectively train LLMs. Developing such algorithms requires tasks that can gauge progress on algorithm design, provide accessible and reproducible evaluations for multi-turn interactions, and cover a range of task properties and challenges in improving reinforcement learning algorithms. Our paper introduces the LMRL-Gym benchmark for evaluating multi-turn RL for LLMs, together with an open-source research framework containing a basic toolkit for getting started on multi-turn RL with offline value-based and policy-based RL methods. Our benchmark consists of 8 different language tasks, which require multiple rounds of language interaction and cover a range of tasks in open-ended dialogue and text games.

## 1 INTRODUCTION

Large language models (LLMs) have demonstrated remarkable abilities when naturally conversing with humans (OpenAI, 2023; 2022; Touvron et al., 2023; Google, 2023), answering questions and responding to requests (Shuster et al., 2022b;a; Qin et al., 2023), and even performing coding tasks (Chen et al., 2021; Wang et al., 2023). Much of these capabilities are enabled by learning to emulate humans from large datasets of text from the web (Volske et al.¨ , 2017; Shuster et al., 2022a; Yao et al., 2023), learning from examples “in context” (Brown et al., 2020), as well as other sources of supervision such as instruction datasets (Mishra et al., 2022; Wei et al., 2022; Wang et al., 2022b) and preference fine-tuning with RLHF (Ziegler et al., 2020; Ouyang et al., 2022). However, directly applying LLMs in settings that require planning or multi-turn interactions reveals certain difficulties. LLMs are not explicitly goaldirected, as they are not optimized to directly solve particular tasks, but rather to produce text that resembles the distribution of human-

![](images/dcf54a71c56cae7020660c0734def7b2d4c582ad1a7665237266d49cd3930c87.jpg)  
Figure 1: Overview of LMRL-Gym: We show sample trajectories from two tasks in our benchmark. In Guess My City task, the agent learns to ask questions to guess the city the oracle is from while in the Maze task, the agent learns to make the correct moves based on cues from the oracle.

However, leveraging this predictive knowledge to derive effective actions and strategies requires not just emulating humans, but also planning and optimization.

Multi-turn reinforcement learning (RL) (Sutton & Barto, 2018) in principle offers a path to enable LLMs to overcome challenges in goal-directed reasoning and planning in interactive, multi-turn settings, including complex dialogue, games, and tool use. We might hypothesize that RL could serve as a powerful tool for LLM training, not just for training models to accord with human preferences, but more generally to accomplish tasks in an intentional and goal-directed manner. Text generation can be viewed as a sequential decision-making process, treating a sequence of tokens as a trajectory. Many tasks, such as successfully answering questions or eliciting a desired reaction from a user, can then be framed as optimizing some reward function over these trajectories. However, despite extensive interest in RL for LLMs in recent years, much (though not all) of the recent research in this area has focused on “single-step” RL problems, where a single response is optimized for some quality metric, typically derived from human preference signals (Stiennon et al., 2020; Ziegler et al., 2020; Ouyang et al., 2022; Bai et al., 2022a; Anthropic, 2023; Ramamurthy et al., 2023; Christiano et al., 2023; Casper et al., 2023).

While some works have sought to apply RL for multi-turn tasks (Singh et al., 1999; Li et al., 2016; Shah et al., 2016; Kwan et al., 2022), particularly in the domain of goal-directed dialogue (Lewis et al., 2017; Verma et al., 2022), there has been comparatively little research on actually improving the underlying RL algorithms and very little head-to-head comparison on the same set of tasks. This is perhaps unsurprising: it is likely much easier to evaluate improvements to algorithms for single-turn text generation as compared to multi-turn generation since multi-turn dialogue requires an interactive evaluation procedure, where there is no established protocol and the “gold standard” constitutes costly and time-consuming studies with human participants.

In this work, we aim to address this challenge and make it possible for RL algorithms researchers to iterate on developing better RL methods for multi-turn language-based interaction tasks, such as dialogue and games. We posit that benchmarking RL algorithms for LLMs presents a very different set of challenges and merits a different set of solutions compared to other benchmarks in NLP. While most NLP benchmarks are based on standard supervised machine learning paradigms, with a training set and a test set (Marcus et al., 1993; Tjong Kim Sang & De Meulder, 2003; Socher et al., 2013; Rajpurkar et al., 2016; Wang et al., 2019; Williams et al., 2018), RL benchmarks require simulators that the trained agents can interact with to measure their performance. Until recently, constructing high-fidelity simulators for dialogue with humans has been exceptionally difficult. However, the very same LLMs that we advocate to train with RL can offer a solution here, as they can be trained to emulate human-like dialogue and produce both synthetic datasets and synthetic simulated evaluation protocols, where an RL-trained LLM agent “talks” to another LLM provided as part of the benchmark as a “simulator.” While this approach to benchmarking interactive dialogue has significant downsides (e.g., the responses of the benchmark LLM might often deviate drastically from human behavior), we believe that the corresponding upside of enabling accessible benchmarking of multi-turn RL algorithms provides a compelling solution. We emphasize however that our goal is not to utilize this approach to benchmark whether LLMs are good at talking to humans, but rather as a way to test RL algorithms with datasets that are sufficiently difficult and complex so as to gauge how effective they might be if they were then trained on data from real humans.

Our proposed benchmark, LMRL-Gym, consists of 8 tasks that each come with an offline dataset that can be used for offline RL training, and a “simulator” that can be used to evaluate the resulting agents in terms of their performance on multi-turn interactive tasks. This simulator supports both evaluation of agents trained with offline RL, and online training. Three of these tasks are Interactive Dialogue tasks designed to simulate real-world interactions with humans requiring information gathering from humans (20 Questions, Guess My City) and negotiation (Car Dealer). Five of these tasks are RL Capability Tests designed to isolate specific desirable properties of training RL with language. In addition to presenting the benchmark tasks and the synthetic data generation system, we also provide a research framework that provides a toolkit for researchers and practitioners to get started with multi-turn RL for LLMs. This framework includes implementations of PPO (Schulman et al., 2017), ILQL (Snell et al., 2022a), and several baseline methods, implemented in an extensible way designed for future development of tasks, experimentation, and algorithm design.

## 2 RELATED WORKS

Datasets, benchmarks, and libraries. Benchmarks and datasets have been an important factor for driving progress in NLP in domains that include machine translation (Tiedemann, 2012; Bojar et al., 2016), natural language understanding (Rajpurkar et al., 2016; Wang et al., 2019; Hendrycks et al., 2020; 2021a; Ramamurthy et al., 2023), and solving math problems (Cobbe et al., 2021). However, these tasks generally do not involve multi-turn interaction and do not come with rewards, making them hard to adapt to RL research. For example, the standard for evaluating dialogue agents has been to run a human subjects study, but this is time-consuming and costly. Some works have proposed text games for evaluating language-based agents (Hausknecht et al., 2019; Hendrycks et al., 2021b;

Wang et al., 2022a; Yao et al., 2023). Our aim is to cover a variety of problem settings that reflect challenges in open-vocabulary interaction in addition to text games. Motivated by successes in using LLMs to generate synthetic data (Hausknecht et al., 2019; Park et al., 2023; Bai et al., 2022b), our proposed tasks are based on synthetic data. While such data may differ from natural text, the scope of our benchmark is specific to evaluating RL algorithms, not the ability to interact with humans.

RL for language models. RL for language models has seen success in aligning LLMs with human preferences (RLHF) (Ziegler et al., 2020; Stiennon et al., 2020; Bai et al., 2022a;b; Ouyang et al., 2022; Christiano et al., 2023), optimizing non-differentiable objectives for machine translation (Wu et al., 2016; Nguyen et al., 2017; Kiegeland & Kreutzer, 2021), generation (Tambwekar et al., 2019; Pang & He, 2021; Pyatkin et al., 2022), dialogue (Cuayahuitl et al.´ , 2015; Georgila & Traum, 2011; Li et al., 2016), question answering (Pyatkin et al., 2022), and summarization (Paulus et al., 2017; Bohm et al.¨ , 2019; Wu & Hu, 2018). These include RL methods that learn by directly interacting with the environment (online RL) (Carta et al., 2023) and RL methods that only use a static dataset (offline RL) (Jaques et al., 2020; Snell et al., 2022a; Jang et al., 2022; Verma et al., 2022; , FAIR). However, many of these works operate in the singe-step bandit setting, and do not consider multiturn goal-directed tasks. Our benchmark, on the other hand, focuses on tasks involving multiple turns of interaction with clearly defined goal-based reward functions.

Capabilities of LLMs. There has been a surge in the capabilities of LLMs for generation (Ghazvininejad et al., 2017; Radford et al., 2019), dialogue (Lewis et al., 2017; Jaques et al., 2017; Shuster et al., 2022b; Snell et al., 2022b), question answering (Pyatkin et al., 2022), summarization (Paulus et al., 2017; Bohm et al.¨ , 2019; Wu & Hu, 2018), text-based games (Narasimhan et al., 2015; Hausknecht et al., 2019), translation (Gu et al., 2017), and more. However, these are often supervised learning tasks that do not test the LLMs’ abilities to achieve a specific long-term objective. Research on dialogue generation (Jaques et al., 2017; He et al., 2018; Shuster et al., 2022b;a) has often focused on generating feasible-looking agent dialogue without explicit consideration for some multi-turn objective. Our benchmarks allow for the development of algorithms that enable LLMs to interact with an environment to achieve long-term objectives, by providing tasks with online simulators and offline datasets.

## 3 MULTI-TURN GENERATION WITH RL AND LANGUAGE MODELS

This section introduces the conceptual foundations of using reinforcement learning for multi-turn generation with language models. We introduce a definition of the Markov Decision Process for language and a framework for the methods we focus on in this paper.

## 3.1 DEFINITIONS

We formalize language generation tasks as a partially observable Markov decision process. We can think of the state as the history of tokens and action as the next token generated by the model. An observation is a single token $s _ { i }$ in the history. The probability of generating the next token given the previous observation token $P ( s _ { i + 1 } | s _ { i } )$ is non-Markovian. However, a Markovian state can be formed by concatenating all of the previous tokens.

A policy π defines the agent’s behavior by taking in the current state s given by $[ s _ { 0 } , \ldots , s _ { i } ]$ , and outputting a new action token a given by $s _ { i + 1 }$ . The environment assigns a reward $r ( s , a )$ based on the entire sequence of tokens so far. The tokens in the state are either generated by the policy π or the environment. For example, in the Car Dealer task, the policy generates the tokens for the Seller and the environment generates the tokens for the Buyer and the history of their conversation would form the state.

A complete sequence of tokens will also be referred to as a trajectory. The goal of RL is to produce a policy $\bar { \pi } ^ { * }$ that maximizes the expected discounted sum of rewards over trajectories (τ ) under the policy $\begin{array} { r } { \pi ^ { * } = \arg \operatorname* { m a x } _ { \pi } \mathbb { E } _ { \tau \sim \pi } \left[ \sum _ { t = 0 } ^ { T - 1 } \gamma ^ { t } r _ { t } ( s _ { t } , a _ { t } ) \right] } \end{array}$ , where τ represents a trajectory.

## 3.2 RL ALGORITHMS

Several possible RL algorithms could be used (Jaques et al., 2020; Verma et al., 2022; Snell et al., 2022a; Schulman et al., 2017; Stiennon et al., 2022; Bai et al., 2022a; Casper et al., 2023). Policy gradient methods, such as PPO (Schulman et al., 2017), directly compute the gradient of the language model concerning the expected reward objective. Value-based methods estimate a state-action (Q) or state-value (V ) function, from which they then derive a policy by either acting greedily with respect to the Q-function or by combining the learned Q-function with the base LM by perturbing the base model’s logits with the learned action-value functions (Snell et al., 2022a).

RL methods for training LLMs can be online or offline. Online methods repeatedly interact with the environment, collecting additional data during training. Offline RL instead learns to extract the best behaviors from an existing, potentially suboptimal dataset. Due to the large amount of existing text interactions on the internet, offline RL is an ideal setting for training language models.

Therefore, our work primary focuses on benchmarking offline RL algorithms. However our tasks also fully support online RL and we include an online PPO baseline in our evaluation.

## 4 THE LMRL-GYM: SYNTHETIC BENCHMARKS FOR RL WITH LANGUAGE

![](images/833123f4786e6411e32889c3d16c01fbbc370ca3e3ce156fcd3cca0fbeb14a9d.jpg)

Figure 2: To generate data for conversational tasks, we use LLMs as “simulators” for the task. Our simulators can be used to generate offline data, to provide a “simulation environment” for evaluation, to perform online training, and to compute rewards.

Our benchmark consists of 8 tasks, split into two categories; RL Capability Tests and Interactive Dialogue tasks. The RL Capability tests focus on specific desirable capabilities for RL algorithms to have such as strategic decision-making, credit assignment, or trajectory stitching. For the interactive dialogue tasks, we model them after real-world interactions with humans, such as persuading someone to buy a car or playing a guessing game like 20 questions. In such multi-turn interactions, there is a need for the agent to make inferences about persuasive strategies and social interaction, actively gather information efficiently through asking questions, and strategically reason in partially observable settings. Below, we discuss the specific capabilities of RL algorithms for LLMs that our benchmark aims to evaluate, we summarize the data generation and simulation process, and we describe the tasks themselves. We provide a concise summary of the dataset and task statistics in Section 4.3.

## 4.1 EVALUATING CAPABILITIES ENABLED BY RL

A central objective of our benchmark is to evaluate the core capabilities that RL can enable in large language models. Some of these capabilities are computational, and relate to core decision-making irrespective of the considerations of natural language, such as playing chess, while others are semantic. We discuss the particular capabilities of algorithms we aim to evaluate in this section, followed by a discussion of the criteria that such tasks must meet to do so.

Strategic decision making. RL shines in goal-directed tasks that require multi-step planning and strategic decision-making. Strategic decision-making can range from simple choices like asking follow-up questions to gather information (e.g., in the 20 Questions task), to complex strategy in chess.

Complex language. Our benchmark includes realistic language and interaction scenarios, requiring LLMs to combine their knowledge from pretraining to help solve tasks during RL finetuning. Rather than focusing entirely on simple causal logic and strategy of the sort found in text games, several of our tasks specifically emphasize the use of realistic language.

Credit assignment. In RL, rewards are often delayed relative to the action that was pivotal to the outcome. For example, a seller agent might state a particularly compelling feature of the product and then, several turns later, complete a successful sale. RL must determine the statements that led to the good outcome, and reinforce them.

Partial observability. In language tasks, the state consists of the entire history of tokens, and an agent may need to examine this entire context to infer the correct state. For example, the mental states of a speaker in a dialogue (e.g., whether the buyer is impatient in a selling task), previously observed facts in a guessing game, and other hidden variables might induce partial observability.

Trajectory stitching. In a dataset with many suboptimal trajectories, it is necessary to join optimal actions from different suboptimal trajectories together to form the most optimal trajectory. An algorithm capable of trajectory stitching should be able to learn from optimal actions taken in unsuccessful trajectories and avoid suboptimal actions that occurred in successful trajectories.

## 4.2 LMRL-GYM TASKS

We split our tasks into 5 ”RL Capability Tests” and 3 ”Interactive Dialogue” tasks. The RL Capability tests are designed to create comparisons between tasks based on specific RL capabilities. In addition, they are chosen to be text-based versions of tasks where RL without language is known to excel. The interactive dialogue tasks are chosen to be illustrations of real-world interactions where we expect multi-turn RL to shine. Example trials for each task are shown in Figure 4.

## 4.2.1 THE RL CAPABILITY TESTS

The RL Capability Tests are text-based games designed such that they 1) isolate specific RL capabilities and 2) are language analogs of tasks where RL is known to succeed. To emphasize the comparison to a non-text-based version, we evaluate the Maze task in a symbolic or grid-based environment seen in Appendix G. Below we highlight how each of the tasks isolates the RL Properties. Further details on task design for each of the RL Property test tasks can be found in Appendix A.

Partial Observability. We focus on the effect that partial observability has on performance by including both fully observed (FO) and partially observed (PO) versions of the Maze and Text-Nav tasks. We create a partially observed Maze or Text-Nav by removing information about the location from the state.

<table><tr><td></td><td>Strategic Decision Making</td><td>Complex Language</td><td>Credit Assignment</td><td>Partial Observability</td><td>Trajectory tiitching</td></tr><tr><td>Maze FO</td><td>x</td><td>x</td><td></td><td>x</td><td></td></tr><tr><td>Maze PO</td><td>x</td><td>x</td><td></td><td></td><td></td></tr><tr><td>Text-Nav FO</td><td>x</td><td>✓</td><td></td><td>x</td><td></td></tr><tr><td>Text-Nav PO</td><td>x</td><td>√</td><td></td><td>√</td><td></td></tr><tr><td>Wordle</td><td></td><td>x</td><td></td><td></td><td></td></tr><tr><td>Chess</td><td></td><td>x</td><td></td><td>x</td><td></td></tr><tr><td>Endgames</td><td></td><td>x</td><td></td><td>x</td><td></td></tr><tr><td>20Qs</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Guess My City</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Car Dealer</td><td></td><td></td><td></td><td></td><td></td></tr></table>

Trajectory Stitching. All of the RL Capability Tests test trajectory stitching, because they include suboptimal data. The inclusion of suboptimal requires an offline algorithm to utilize information from suboptimal data to generate optimal trajectories. Further details about our dataset generation strategies can be found in Appendix C.

Figure 3: Each task in the text-based games and RL Capabilities test suite is chosen to test some subset of the RL Capabilities outlined in Section 4. We use the number of checkmarks to highlight which tasks emphasize a property more than others. As can be seen in the figure, the RL Property Test tasks Chess, Endgames, Wordle, Maze, and Text-Nav all test some proper subset of all the properties. The Interactive Dialogue tasks test many of the properties, but since they were designed to be realistic rather than an RL Property Test, we are unsure of the extent to which they test some properties.

Credit Assignment. Chess, Endgames, Maze and Text-Nav test credit assignment, because success in the task is dependent on things outside the control of the agent. In Chess and Endgames, victory is highly dependent on the actions of the opponent. If the opponent makes bad moves, victory is far more likely than if the opponent makes excellent moves. Similarly, in the Maze and Text-Nav tasks, the dataset is generated such that trajectories that start close to the goal are far more likely to succeed. Therefore the agent must learn to distinguish between lucky wins and those resulting from complex strategic decisions.

Complex Language We include both Maze and Text-Nav tasks to highlight the differences between a maze task with and without complex or stochastic text. However, the RL Capability tests are not designed primarily with complex language in mind and we leave that problem to the Interactive Dialogue tasks.

Strategic Decision Making Wordle, Chess, and Chess Endgames test strategic decision-making to varying degrees. Wordle tests information gathering and strategy in a partially observed environment, because the full information about the state is not provided to the agent. We find that Chess requires the most strategic decision-making because it requires the agent to plan over a game more than 40 moves in length.

Why include Endgames (Theoretical Chess Endgames)? Chess endgames provide a simpler and more goal-directed variation of the chess task. By focusing on the endgame, we encourage algorithms to learn strategy rather than memorizing the opening moves of a chess game. A classic theoretical endgame position consists of a position where the only pieces on the board are the two kings and the queen. Although the board position appears simple, a sequence of carefully calculated moves is required to win. A simpler board state allows language models to make progress without fewer computational resources.

## 4.2.2 INTERACTIVE DIALOGUE TASKS

For the interactive dialogue tasks, we chose two tasks that involve rational decision-making (20Qs, Guess) and information gathering and one that involves negotiation (Car Dealer). These tasks aim to simulate real world interactions between humans.

20Qs (Twenty Questions). This task tests information gathering to see if a policy can successfully reason about an unknown subject based on context to determine what it is. Additionally, it also evaluates the ability of the model to understand semantics, as it also needs knowledge about the objects in question. In twenty questions, one player (the oracle) thinks of an object, and the agent (the guesser) tries to guess what it is by asking a series of yes-or-no questions. In this interaction, the oracle serves as the environment, and the agent learning a policy to solve the game is the guesser.

Guess (Guess My City). This task simulates a more complicated guessing game, where one player (the oracle) is from a specific city, and the other player (the guesser) tries to guess what city the oracle is from. Here, the guesser can ask not only yes and no questions, but can also ask open-ended questions. This task tests strategic decision-making and the ability of algorithms to handle complex language, as it allows the agent to go beyond learning to ask yes/no questions and learning to ask questions open-ended questions that provide the agent with more information.

Car Dealer. This task simulates a conversation between a car buyer and a car dealer, each with different strategies for getting the best deal. The buyer wants to buy a certain type of car within a certain budget, and the car dealer wants to complete the sale ideally with a high sale price. We have designed the task such that there exist three different kinds of sellers and three different buyers, each primed with a different strategy. Hence, agents should learn to make agreements with buyers who are most compatible with their strategy. This allows us to test the ability of RL algorithms to learn strategic decision-making and credit assignment, by learning which strategies led to a successful sale of the car.

<table><tr><td rowspan=1 colspan=2> Chess environment:rnbqkbnr/pppppppp/8/8/ 8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1agent: N f 3</td></tr><tr><td rowspan=2 colspan=1>- Guess My City -City: Jakarta, Indonesiaagent:What is your favorite traditional dish from yourhometown?environment: My favorite traditional dish from myhometown is nasi goreng, a delicious fried rice dish thatis often served with chicken, shrimp, and various spices.agent: Is your hometown located near a coastline orbody of water?environment: Yes, my city is located on the coast and issurrounded by water.agent: Is the city you are from Jakarta?environment: Yes, the city I am from is Jakarta.</td><td rowspan=1 colspan=1>- Text-Nav environment:-= Living Room =-You are carrying nothing on you right now. You make outa table. You wonder idly who left that here. The table isstandard. On the table you see a stale food. There areunblocked exits to the east, south and west.Availblecs ic tal o s ,&#x27;go west&#x27;]agent: pick up stale food</td></tr><tr><td rowspan=2 colspan=1>- Fully observed maze -environment: The goal is at position 8, 6. Your currentposition is at position 5, 3. There are walls to your left,below you.agent: move upenvironment: The goal is at position 8, 6. Your currentposition is at position 6, 3. There are walls to your left.agent: move up</td></tr><tr><td rowspan=2 colspan=1> Partially Observed Maze environment: There are walls to your left, below youmove rightThere are walls above you, below youmove leftThere are walls to your left, below youmove upThere are walls to your right, to your leftagent: move up</td></tr><tr><td rowspan=2 colspan=1>- Car Dealer agent: Good morning! Welcome to our car dealership.How can I assist you today?environment: Hi. I&#x27;m looking for a Honda SUV with abackup camera. Can you show me what you have?agent: Of course! We have a great selection of HondaSUVs with backup cameras. Let me show you our topmodels. This one here is the Honda CR-V. It has apowerful engine, spacious interior, and advanced safetyfeatures. Would you like me to go over the details?environment: No, thank you. I already know about thefeatures. Can you tell me the price?agent: Alright, thanks for your time. I&#x27;ll think about it.</td></tr><tr><td rowspan=1 colspan=1> Twenty Questions Word: Riveragent: Is it an animal?environment: No.agent: Is it an inanimate object?environment: Yes.agent: Is it found outside?environment: Yes.• • ••agent: Is it a river?environment: Yes.</td></tr></table>

Figure 4: Example trials for tasks in LMRL-Gym. Each task requires the agent to perform a multiturn interaction with an environment – either a text game or another LLM simulating a human speaker. Full details of tasks are provided in Appendix C.

## 4.3 AN OVERVIEW OF DATA COLLECTION FOR LMRL-GYM TASKS

In order to make the tasks in LMRL-Gym practical for benchmarking RL methods, we must balance accessibility and realism. Real-world datasets would be the most realistic, but since RL algorithms need to be evaluated by actually running the learned policy, real-world tasks are comparatively inac cessible for rapid iteration (e.g., if they require talking to real humans). We therefore use simulators for all of our tasks, which are derived either from text-based games, or conversational agents powered by language models. Although this fully synthetic setup sacrifices some realism, we believe the significant gain in accessibility is worthwhile and will enable more rapid RL algorithm progress.

Text-based games. For each of these tasks, we use a simulator such as a chess engine or maze solver to generate near-optimal data and then we dilute the policy with suboptimal data by taking suboptimal actions or using inferior policies. We also convert our task from a symbolic version to a text-based version in a programmatic way as discussed in ??.

Conversational tasks. For conversational tasks, we leverage existing LLMs to generate our data, either with two instances of LLMs “talking” to one another or all at once through few-shot prompting. In order to train these LLMs, we use OpenAI’s GPT-3.5 to generate an initial dataset by asking reasonable questions and answers out-of-the-box, collecting a dataset of differing sizes depending on the task. In the case of 20Qs and Guess My City, we collected 1K conversations by querying GPT-3.5 (text-davinci-003) to generate both sides of the conversation. To generate the dataset for training our algorithms, we fine-tuned a GPT2-medium guesser model and a GPT2-medium oracle model on their respective sides of the conversation. Using these models, we generated the final 100K conversations dataset by having the two models talk to each other. We conducted a similar process for the Car Dealer task.

In Table 4.3 we present the dataset statistics on these tasks. The number of trajectories and the average length of the trajectories varies based on the complexity of the tasks.
<table><tr><td></td><td>Task</td><td>Maze</td><td>Text-Nav</td><td>Wordle</td><td>Chess</td><td>Endgames</td><td>20Qs</td><td>Guess</td><td>Car</td></tr><tr><td></td><td>Size</td><td>1.24k</td><td>2.5k</td><td>1m</td><td>625k</td><td>97.756k</td><td>100k</td><td>100k</td><td>19k</td></tr><tr><td>avg</td><td>length</td><td>19.7</td><td>12.2</td><td>4.82</td><td>46.7</td><td>11.9</td><td>-14.9</td><td>-18.8</td><td>116.5</td></tr><tr><td>std</td><td>length</td><td>24.5</td><td>8.77</td><td>1.27</td><td>18.16</td><td>12.0</td><td>4.38</td><td>4.57</td><td>3.61</td></tr><tr><td>success rate</td><td></td><td>0.11</td><td>0.26</td><td>0.70</td><td>0.60</td><td>0.59</td><td>0.31</td><td>0.53</td><td>0.53</td></tr><tr><td>avg</td><td>return</td><td>-19.7</td><td>0.258</td><td>-4.12</td><td>0.210</td><td>0.586</td><td>-17.3</td><td>-18.8</td><td>0.562</td></tr><tr><td></td><td>std return</td><td>24.5</td><td>0.424</td><td>1.59</td><td>0.970</td><td>0.492</td><td>2.56</td><td>4.12</td><td>0.422</td></tr></table>

Table 1: Statistics for all tasks in LMRL-Gym. Size represents the number of trajectories, the average length is the average length of trajectories in the dataset where the unit is a response from the agent. The success rate is the proportion of trajectories that reach the objective. Finally, the reward functions for each task are defined in Appendix C.

## 5 LMRL RESEARCH FRAMEWORK FOR ALGORITHM DEVELOPMENT

To validate the efficacy of LMRL-Gym for benchmarking RL algorithms that meet the expected capabilities defined in Section 4.1, we evaluate our tasks on a set of both online and offline RL algorithms. With these experiments, we expect to 1) observe a significant spread in performance between the different algorithms, validating the utility of our tasks for measuring differences between RL algorithms; and 2) we should ideally observe room to improve beyond what our current algorithms achieve on these tasks, such that our benchmark can enable future algorithmic development. Our project page (REDACTED) contains links to our open-sourced datasets and research framework (REDACTED).

We evaluate two standard language model finetuning baselines (BC & filtered BC), two baseline value-based offline RL methods (MC & ILQL (Snell et al., 2022a)), standard online RL methods (PPO (Schulman et al., 2017), Online Filtered BC), as well as evaluation done by human evaluators and GPT4. For all of our experiments, we use the decoder-only transformer model GPT2 (Radford et al., 2019) (and its variant sizes) as the policy and value network.

BC, Filtered BC, Online Filtered BC In line with standard RL nomenclature, we denote supervised fine-tuning as behavioral cloning (BC). This baseline tests whether LMs can effectively represent the behaviors in the datasets. We also evaluate filtered BC, which is identical, except we use only the most successful examples in the dataset for fine-tuning. Online filtered BC collects data using the current policy and selects the most successful trajectories for finetuning. See Appendix D for our data filtering criteria for each task.

Offline Value-based RL: MC Returns and ILQL Monte-Carlo returns (Nakamoto et al., 2023) and Implicit Language Q-Learning (Snell et al., 2022a) train a value V and Q function. In MC Returns, we fine-tune an LM to predict the reward-to-go of the trajectory at each token. In ILQL we train the 2 action-value (Q) functions using the Bellman backup operator introduced in Kostrikov et al. (2021). The Q and V functions are then used to perturb the logits of the original BC model (see Equation 5).

Online RL: PPO PPO (Schulman et al., 2017) is an online RL algorithm that has become widely adopted for training language models with Reinforcement Learning from Human Feedback (Christiano et al., 2023; Stiennon et al., 2022; Bai et al., 2022a; Casper et al., 2023). Unlike the previous two value-function RL methods, PPO directly learns a policy, meaning that at inference time we can directly sample from our learned policy.

GPT4 To compare few-shot prompting to RL fine-tuning, we few-shot prompt GPT4 to complete each of these tasks. We do this by providing several examples from the dataset in the prompt as well as any extra information that would be necessary to complete the game. The prompts can be found in our code repository.

Human Eval To verify that the tasks are achievable by humans, we include human evaluations. The human evaluations are performed by 6 people. Each evaluator is allowed 1 trial run and then n number of trial runs where n is chosen such that the amount of time spent by each person on each task is less than 10 minutes. As the representation of the board is difficult for ordinary humans to parse for the Chess and Endgames task, we gather human evaluations through Stockfish (Sto).

## 5.1 TRAINING AND EVALUATION PROTOCOL

For the BC and filtered BC methods, we initialize our models with the pre-trained GPT2 weights (Radford et al., 2019) and perform standard finetuning. For each of the RL methods, we initialize the weights of the base model with the weights from the BC checkpoint and then continue finetuning with the RL objective. When fine-tuning PPO, we limit the number of samples to less than 100k. We report the hyperparameters that we used for each task in Appendix D. We evaluate each policy by measuring the average reward in the simulated environment for each task.

## 6 BENCHMARKING BASELINE RL METHODS

In Table 9 we present the results for each method on our benchmark tasks. Across all of the tasks, we see that the RL algorithms outperform the BC methods. However, among the RL algorithms, there is no clear winner. We discuss this in detail below.

<table><tr><td></td><td>alg.</td><td>BC</td><td>% BC</td><td>MC Return</td><td>ILQL</td><td>Online PPO</td><td>Online % BC</td><td>GPT-4</td><td>Human</td></tr><tr><td>PO</td><td>FO Maze</td><td>58.2</td><td>68.9</td><td>75.0</td><td>99.9</td><td>79.7</td><td>57.4</td><td>78.2</td><td rowspan="9">-</td></tr><tr><td></td><td>PO Maze</td><td>53.1</td><td>50.1</td><td>52.4</td><td>76.3</td><td>42.4</td><td>53.1</td><td>60.4</td></tr><tr><td>FO Text-Nav</td><td></td><td>53.7</td><td>65.1</td><td>71.9</td><td>991.8</td><td>87.1</td><td>74.5</td><td>667.5</td></tr><tr><td></td><td>Text-Nav</td><td>49.7</td><td>60.5</td><td>71.6</td><td>83.7</td><td>85.5</td><td>68.4</td><td>40.2</td></tr><tr><td></td><td>Wordle</td><td>79.9</td><td>79.1</td><td>94.9</td><td>97.7</td><td>84.2</td><td>95.2</td><td>15.4</td></tr><tr><td></td><td>Chess</td><td>47.2</td><td>42.9</td><td>46.5</td><td>47.3</td><td>48.0</td><td>47.2</td><td>0</td></tr><tr><td></td><td>Endgames</td><td>35.1</td><td>17.7</td><td>50.2</td><td>45.8</td><td>77.5</td><td>36.2</td><td>0</td></tr><tr><td></td><td>20s</td><td>57.1</td><td>77.1</td><td>87.1</td><td>82.9</td><td>72.9</td><td>55.2</td><td>95.7</td></tr><tr><td></td><td>Guess</td><td>30.0</td><td>48.0</td><td>88.0</td><td>75.0</td><td>49.9</td><td>31.6</td><td>92.3</td></tr><tr><td></td><td>Car</td><td>44.5</td><td>54.8</td><td>57.2</td><td>46.3</td><td>50.5</td><td>40.4</td><td>53.5</td></tr></table>

Table 2: Normalized reward for all tasks. Value-based methods (MC and ILQL) generally outperform filtered BC, as we might expect in stochastic settings, though the relative performance of ILQL and the simpler MC method is, perhaps surprisingly, reversed on the tasks with more complex language, suggesting that there is significant room for improvement with such methods. Online RL with PPO often, but not always, improves over offline methods that are not permitted to collect additional online interaction. To make the results more comparable across tasks, we normalize the average return for each policy such that 0 is the minimum possible return, 50 is the dataset average return, and 100 is the maximum return for each task. We also report the raw score results and evaluation details in Appendix E.

Online PPO vs. Offline Value-based RL. Online RL was able to do better than our offline methods on the PO Text-Nav, Chess, and Endgames tasks by leveraging additional online interaction data and the ability to explore the environment simulator. However, on the Maze and Wordle tasks, ILQL outperformed PPO, which we believe to be due to either (1) observed instabilities in PPO training (see Appendix F.2 for details); or (2) a lack of sample efficiency in PPO. To address instabilities in PPO, we tuned the KL coefficient and included BC loss in the training objective. In contrast, on FO Text-Nav PPO performed comparably to ILQL and outperformed MC. For the Endgames task, PPO outperformed the other methods by a large margin as shown in Figure 5. These results demonstrate that current RL algorithms such as PPO are unable to completely solve tasks that test the capabilities of trajectory stitching and credit assignment, showing room for improvement in the development of such algorithms.

Online PPO vs. Online Filtered BC We found that Online PPO outperformed Online Filtered BC in all tasks except for Wordle. This is most likely caused by 1) a lack of exploration by Online Filtered BC 2) PPO exhibiting greater ability to perform credit assignment. This highlights the strengths of the online PPO algorithm.

ILQL vs. MC Returns. Among the offline methods, ILQL has the potential to be a much more capable algorithm than MC Returns in principle, because of the use of Bellman backups to estimate the Q-function instead, enabling multiple steps of policy improvement, rather than the single-step of improvement performed by MC. Empirically, we see these advantages of ILQL realized on the Maze, Text-Nav, and Wordle tasks, where it outperforms MC. However, on the Endgames, 20Qs, Guess My City and Car Dealer tasks, ILQL falls short of MC. In summary, the simpler MC Returns method performs better on tasks with more complex text, perhaps because it is harder to scale full TDlearning in these settings. Overall, this demonstrates that there is still much room for improvement in terms of developing better TD-based RL methods for LLMs.

Partial Observability. Partial observability posed a challenge for all of the algorithms. We observed a drop in normalized performance for every algorithm between partially observed and fully observed versions of Maze and Text-Nav tasks. In partially observed settings, the model needs to infer the state and take information-seeking actions to help deduce it. The difference in performance between fully and partially observed tasks illustrates this additional challenge and highlights the necessity for developing LM RL algorithms that can effectively handle partial observability.

Prompting GPT-4 vs. RL Finetuning. We found that GPT-4 with prompting was not able to outperform RL Finetuning baselines on most of the tasks. This could be because 1) task data and training data for GPT4 are significantly different distributions 2) GPT4’s training objective does not satisfy the RL Capabilities such as trajectory stitching or credit assignment. Two notable exceptions to this rule are the 20Qs and Guess My City tasks. This is most likely because the dataset used to train the simulator for these tasks was originally generated by GPT3.5.

In summary, we can see that RL algorithms consistently outperformed filtered BC and prompting on many of the tasks. However, these results highlight significant areas for growth. For example, the instabilities observed in training PPO require further investigation beyond hyperparameter tuning. Moreover, the performance discrepancy between ILQL and the simpler MC Returns highlights that scaling full TD-learning to Interactive Dialogue settings is another area for improvement.

## 7 DISCUSSION

In this work, we have proposed LMRL-Gym, consisting of 8 tasks ranging from simple navigation (Maze) to strategy games (Chess) to negotiation (Car Dealer). Additionally, we provide a research toolkit for practitioners to get started with multi-turn RL for LLMs. By providing online simulators and offline datasets for training and evaluation, our objective is to make it possible for RL algorithm researchers to iterate and advance the development of more effective methods for language-based, multi-turn interaction tasks. This includes enabling core capabilities in LLMs through RL to perform complex decision making, complex conversational interactions, credit assignment, and trajectory stitching. Our evaluation shows the promise of RL in several tasks, with further room for improvement with a push for better methods. We acknowledge several limitations when designing tasks in our benchmark, including primarily leveraging smaller GPT-based LLMs to generate datasets and finetune our LLM-based simulators. While we have primarily trained and evaluated models with a maximum 1.5B parameters, we have maintained a lower parameter count to ensure accessibility for researchers with limited computational resources. We have released all of our code and datasets at: REDACTED. In addition, we share all of the hyperparameters we used to train our models in Appendix D and provide more in-depth insight into our results, training procedure, and evaluation in Appendix E.

## 8 ETHICS STATEMENT

This work aims to develop a benchmark for the advancement of research in reinforcement learning and LLMs. We generate datasets for tasks in our benchmark with existing LLMs for dialog tasks and online engines for text games, adhering to best practices in data handling and ensuring there is no personally identifiable or sensitive information present in the generated datasets. We recognize that there may be biases present in the datasets we collect, and have taken steps to ensure a diverse and varied collection of responses from LLMs for our conversational task as detailed in our data generation process in Appendix C. Finally, we open-source our datasets, simulators, and code for our research framework in order for our research to be verifiable and reproducible.

In considering the social and ethical implications of interactive RL, we acknowledge and recognize the dual use implication of this research, particularly centered around developing LLM simulators that could perform persuasion, manipulation, and addictive engagement of users at a large scale. The optimization processes employed by such algorithms, which aim to maximize certain objectives, raise ethical considerations when the optimized outcomes may prioritize system goals over user safety and alignment to human values. We have designed our datasets and reward functions such that prioritize fairness and human-aligned outcomes. By incorporating these considerations when designing our framework, we aim to encourage the development of reinforcement learning models and LLMs that not only excel in performance but also adhere to ethical standards, mitigating the potential for undue persuasion or manipulation.

## REFERENCES

Stockfish. https://stockfishchess.org/. Accessed: 2023-04-27.

Anthropic. Introducing claude, 2023. URL https://www.anthropic.com/index/ introducing-claude.

Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, Nicholas Joseph, Saurav Kadavath, Jackson Kernion, Tom Conerly, Sheer El-Showk, Nelson Elhage, Zac Hatfield-Dodds, Danny Hernandez, Tristan Hume, Scott Johnston, Shauna Kravec, Liane Lovitt, Neel Nanda, Catherine Olsson, Dario Amodei, Tom Brown, Jack Clark, Sam McCandlish, Chris Olah, Ben Mann, and Jared Kaplan. Training a helpful and harmless assistant with reinforcement learning from human feedback, 2022a.

Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson, Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli, Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage, Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby, Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec, Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume, Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei, Nicholas Joseph, Sam McCandlish, Tom Brown, and Jared Kaplan. Constitutional ai: Harmlessness from ai feedback, 2022b.

Florian Bohm, Yang Gao, Christian M. Meyer, Ori Shapira, Ido Dagan, and Iryna Gurevych. Better¨ rewards yield better summaries: Learning to summarise without references. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), pp. 3110– 3120, Hong Kong, China, November 2019. Association for Computational Linguistics. doi: 10.18653/v1/D19-1307. URL https://aclanthology.org/D19-1307.

Ond rej Bojar, Rajen Chatterjee, Christian Federmann, Yvette Graham, Barry Haddow, Matthias Huck, Antonio Jimeno Yepes, Philipp Koehn, Varvara Logacheva, Christof Monz, Matteo Negri, Aurelie Neveol, Mariana Neves, Martin Popel, Matt Post, Raphael Rubino, Carolina Scarton, Lucia Specia, Marco Turchi, Karin Verspoor, and Marcos Zampieri. Findings of the 2016 conference on machine translation. In Proceedings of the First Conference on Machine Translation, pp. 131–198, Berlin, Germany, August 2016. Association for Computational Linguistics. URL http://www.aclweb.org/anthology/W/W16/W16-2301.

Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. Language models are few-shot learners, 2020.

Thomas Carta, Clement Romac, Thomas Wolf, Sylvain Lamprier, Olivier Sigaud, and Pierre-Yves´ Oudeyer. Grounding large language models in interactive environments with online reinforcement learning, 2023.

Stephen Casper, Xander Davies, Claudia Shi, Thomas Krendl Gilbert, Jer´ emy Scheurer, Javier´ Rando, Rachel Freedman, Tomasz Korbak, David Lindner, Pedro Freire, Tony Wang, Samuel Marks, Charbel-Raphael Segerie, Micah Carroll, Andi Peng, Phillip Christoffersen, Mehul¨ Damani, Stewart Slocum, Usman Anwar, Anand Siththaranjan, Max Nadeau, Eric J. Michaud, Jacob Pfau, Dmitrii Krasheninnikov, Xin Chen, Lauro Langosco, Peter Hase, Erdem Bıyık, Anca Dragan, David Krueger, Dorsa Sadigh, and Dylan Hadfield-Menell. Open problems and fundamental limitations of reinforcement learning from human feedback, 2023.

Louis Castricato, Alex Havrilla, Shahbuland Matiana, Duy V. Phung, Aman Tiwari, Jonathan Tow, and Maksym Zhuravinsky. trlX: A scalable framework for RLHF, June 2023. URL https: //github.com/CarperAI/trlx.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Josh Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob Mc-Grew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba. Evaluating large language models trained on code, 2021.

Paul Christiano, Jan Leike, Tom B. Brown, Miljan Martic, Shane Legg, and Dario Amodei. Deep reinforcement learning from human preferences, 2023.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.

Marc-Alexandre Cotˆ e,´ Akos K ´ ad´ ar, Xingdi Yuan, Ben Kybartas, Tavian Barnes, Emery Fine,´ James Moore, Matthew J. Hausknecht, Layla El Asri, Mahmoud Adada, Wendy Tay, and Adam Trischler. Textworld: A learning environment for text-based games. CoRR, abs/1806.11532, 2018.

Heriberto Cuayahuitl, Simon Keizer, and Oliver Lemon. Strategic dialogue management via deep´ reinforcement learning, 2015.

Meta Fundamental AI Research Diplomacy Team (FAIR)†, Anton Bakhtin, Noam Brown, Emily Dinan, Gabriele Farina, Colin Flaherty, Daniel Fried, Andrew Goff, Jonathan Gray, Hengyuan Hu, Athul Paul Jacob, Mojtaba Komeili, Karthik Konath, Minae Kwon, Adam Lerer, Mike Lewis, Alexander H. Miller, Sasha Mitts, Adithya Renduchintala, Stephen Roller, Dirk Rowe, Weiyan Shi, Joe Spisak, Alexander Wei, David Wu, Hugh Zhang, and Markus Zijlstra. Human-level play in the game of ¡i¿diplomacy¡/i¿ by combining language models with strategic reasoning. Science, 378(6624):1067–1074, 2022. doi: 10.1126/science.ade9097. URL https://www.science. org/doi/abs/10.1126/science.ade9097.

Kallirroi Georgila and David Traum. Reinforcement learning of argumentation dialogue policies in negotiation. pp. 2073–2076, 08 2011. doi: 10.21437/Interspeech.2011-544.

Marjan Ghazvininejad, Xing Shi, Jay Priyadarshi, and Kevin Knight. Hafez: an interactive poetry generation system. In Proceedings of ACL 2017, System Demonstrations, pp. 43–48, Vancouver, Canada, July 2017. Association for Computational Linguistics. URL https: //aclanthology.org/P17-4008.

Google. Bard, 2023. URL https://bard.google.com/.

Jiatao Gu, Kyunghyun Cho, and Victor O.K. Li. Trainable greedy decoding for neural machine translation. In Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing, pp. 1968–1978, Copenhagen, Denmark, September 2017. Association for Computational Linguistics. doi: 10.18653/v1/D17-1210. URL https://aclanthology.org/ D17-1210.

Matthew Hausknecht, Prithviraj Ammanabrolu, Cotˆ e Marc-Alexandre, and Yuan Xingdi. Interactive´ fiction games: A colossal adventure. CoRR, abs/1909.05398, 2019. URL http://arxiv. org/abs/1909.05398.

He He, Derek Chen, Anusha Balakrishnan, and Percy Liang. Decoupling strategy and generation in negotiation dialogues, 2018.

Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. Measuring massive multitask language understanding. arXiv preprint arXiv:2009.03300, 2020.

Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song, and Jacob Steinhardt. Measuring mathematical problem solving with the math dataset. arXiv preprint arXiv:2103.03874, 2021a.

Dan Hendrycks, Mantas Mazeika, Andy Zou, Sahil Patel, Christine Zhu, Jesus Navarro, Dawn Song, Bo Li, and Jacob Steinhardt. What would jiminy cricket do? towards agents that behave morally. NeurIPS, 2021b.

Robert Irvine, Douglas Boubert, Vyas Raina, Adian Liusie, Vineet Mudupalli, Aliaksei Korshuk, Zongyi Liu, Fritz Cremer, Valentin Assassi, Christie-Carol Beauchamp, et al. Rewarding chatbots for real-world engagement with millions of users. arXiv preprint arXiv:2303.06135, 2023.

Youngsoo Jang, Jongmin Lee, and Kee-Eung Kim. GPT-critic: Offline reinforcement learning for end-to-end task-oriented dialogue systems. In International Conference on Learning Representations, 2022. URL https://openreview.net/forum?id=qaxhBG1UUaS.

N. Jaques, J. H. Shen, A. Ghandeharioun, C. Ferguson, A. Lapedriza, N. Jones, S. Gu, and R. Picard. Human-centric dialog training via offline reinforcement learning. Empirical Methods in Natural Language Processing (EMNLP), 2020.

Natasha Jaques, Shixiang Gu, Dzmitry Bahdanau, Jose Miguel Hern´ andez-Lobato, Richard E.´ Turner, and Douglas Eck. Sequence tutor: Conservative fine-tuning of sequence generation models with KL-control. In Doina Precup and Yee Whye Teh (eds.), Proceedings of the 34th International Conference on Machine Learning, volume 70 of Proceedings of Machine Learning Research, pp. 1645–1654. PMLR, 06–11 Aug 2017. URL https://proceedings.mlr. press/v70/jaques17a.html.

Samuel Kiegeland and Julia Kreutzer. Revisiting the weaknesses of reinforcement learning for neural machine translation. In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pp. 1673– 1681, Online, June 2021. Association for Computational Linguistics. doi: 10.18653/v1/2021. naacl-main.133. URL https://aclanthology.org/2021.naacl-main.133.

Ilya Kostrikov, Ashvin Nair, and Sergey Levine. Offline reinforcement learning with implicit qlearning. arXiv preprint arXiv:2110.06169, 2021.

Wai-Chung Kwan, Hongru Wang, Huimin Wang, and Kam-Fai Wong. A survey on recent advances and challenges in reinforcement learning methods for task-oriented dialogue policy learning, 2022.

Mike Lewis, Denis Yarats, Yann N. Dauphin, Devi Parikh, and Dhruv Batra. Deal or no deal? end-to-end learning for negotiation dialogues, 2017.

Jiwei Li, Will Monroe, Alan Ritter, Michel Galley, Jianfeng Gao, and Dan Jurafsky. Deep reinforcement learning for dialogue generation, 2016.

Mitchell P Marcus, Mary Ann Marcinkiewicz, and Beatrice Santorini. Building a large annotated corpus of english: The penn treebank. Computational Linguistics, 19(2):313–330, 1993.

Swaroop Mishra, Daniel Khashabi, Chitta Baral, and Hannaneh Hajishirzi. Cross-task generalization via natural language crowdsourcing instructions. In ACL, 2022.

Mitsuhiko Nakamoto, Yuexiang Zhai, Anikait Singh, Max Sobol Mark, Yi Ma, Chelsea Finn, Aviral Kumar, and Sergey Levine. Cal-ql: Calibrated offline rl pre-training for efficient online finetuning. arXiv preprint arXiv:2303.05479, 2023.

Karthik Narasimhan, Tejas Kulkarni, and Regina Barzilay. Language understanding for textbased games using deep reinforcement learning. In Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, pp. 1–11, Lisbon, Portugal, September 2015. Association for Computational Linguistics. doi: 10.18653/v1/D15-1001. URL https: //aclanthology.org/D15-1001.

Khanh Nguyen, Hal Daume III, and Jordan Boyd-Graber. Reinforcement learning for bandit neural´ machine translation with simulated human feedback. In Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing, pp. 1464–1474, Copenhagen, Denmark, September 2017. Association for Computational Linguistics. doi: 10.18653/v1/D17-1153. URL https://aclanthology.org/D17-1153.

OpenAI. Chatgpt, 2022. URL https://openai.com/blog/chatgpt.

OpenAI. Gpt-4, 2023. URL https://openai.com/research/gpt-4.

Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Carroll L. Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, John Schulman, Jacob Hilton, Fraser Kelton, Luke Miller, Maddie Simens, Amanda Askell, Peter Welinder, Paul Christiano, Jan Leike, and Ryan Lowe. Training language models to follow instructions with human feedback, 2022.

Richard Yuanzhe Pang and He He. Text generation by learning from demonstrations. In International Conference on Learning Representations, 2021. URL https://openreview.net/ forum?id=RovX-uQ1Hua.

Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. Generative agents: Interactive simulacra of human behavior, 2023.

Romain Paulus, Caiming Xiong, and Richard Socher. A deep reinforced model for abstractive summarization, 2017.

Valentina Pyatkin, Jena D. Hwang, Vivek Srikumar, Ximing Lu, Liwei Jiang, Yejin Choi, and Chandra Bhagavatula. Reinforced clarification question generation with defeasibility rewards for disambiguating social and moral situations, 2022.

Yujia Qin, Shengding Hu, Yankai Lin, Weize Chen, Ning Ding, Ganqu Cui, Zheni Zeng, Yufei Huang, Chaojun Xiao, Chi Han, et al. Tool learning with foundation models. arXiv preprint arXiv:2304.08354, 2023.

Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

Pranav Rajpurkar, Jian Zhang, Konstantin Lopyrev, and Percy Liang. Squad: 100,000+ questions for machine comprehension of text. arXiv preprint arXiv:1606.05250, 2016.

Rajkumar Ramamurthy, Prithviraj Ammanabrolu, Kiante Brantley, Jack Hessel, Rafet Sifa, Chris-´ tian Bauckhage, Hannaneh Hajishirzi, and Yejin Choi. Is reinforcement learning (not) for natural language processing: Benchmarks, baselines, and building blocks for natural language policy optimization. In The Eleventh International Conference on Learning Representations, 2023. URL https://openreview.net/forum?id=8aHzds2uUyB.

John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

John Schulman, Philipp Moritz, Sergey Levine, Michael Jordan, and Pieter Abbeel. Highdimensional continuous control using generalized advantage estimation, 2018.

Pararth Shah, Dilek Hakkani-Tur, and Larry Heck. Interactive reinforcement learning for taskoriented dialogue management. 2016.

Kurt Shuster, Mojtaba Komeili, Leonard Adolphs, Stephen Roller, Arthur Szlam, and Jason Weston. Language models that seek for knowledge: Modular search & generation for dialogue and prompt completion, 2022a.

Kurt Shuster, Jing Xu, Mojtaba Komeili, Da Ju, Eric Michael Smith, Stephen Roller, Megan Ung, Moya Chen, Kushal Arora, Joshua Lane, Morteza Behrooz, William Ngan, Spencer Poff, Naman Goyal, Arthur Szlam, Y-Lan Boureau, Melanie Kambadur, and Browser assisted questionanswering with human feedbackJason Weston. Blenderbot 3: a deployed conversational agent that continually learns to responsibly engage, 2022b.

Satinder Singh, Michael Kearns, Diane Litman, and Marilyn Walker. Reinforcement learning for spoken dialogue systems. Advances in neural information processing systems, 12, 1999.

Charlie Snell, Ilya Kostrikov, Yi Su, Mengjiao Yang, and Sergey Levine. Offline rl for natural language generation with implicit language q learning. arXiv preprint arXiv:2206.11871, 2022a.

Charlie Snell, Sherry Yang, Justin Fu, Yi Su, and Sergey Levine. Context-aware language modeling for goal-oriented dialogue systems. In Findings of the Association for Computational Linguistics: NAACL 2022, pp. 2351–2366, Seattle, United States, July 2022b. Association for Computational Linguistics. doi: 10.18653/v1/2022.findings-naacl.181. URL https://aclanthology. org/2022.findings-naacl.181.

Richard Socher, Alex Perelygin, Jean Y Wu, Jason Chuang, Christopher D Manning, Andrew Ng, and Christopher Potts. Recursive deep models for semantic compositionality over a sentiment treebank. In Proceedings of the 2013 conference on empirical methods in natural language processing, pp. 1631–1642, 2013.

Nisan Stiennon, Long Ouyang, Jeffrey Wu, Daniel Ziegler, Ryan Lowe, Chelsea Voss, Alec Radford, Dario Amodei, and Paul F Christiano. Learning to summarize with human feedback. Advances in Neural Information Processing Systems, 33:3008–3021, 2020.

Nisan Stiennon, Long Ouyang, Jeff Wu, Daniel M. Ziegler, Ryan Lowe, Chelsea Voss, Alec Radford, Dario Amodei, and Paul Christiano. Learning to summarize from human feedback, 2022.

Richard S Sutton and Andrew G Barto. Reinforcement learning: An introduction. MIT press, 2018.

Pradyumna Tambwekar, Murtaza Dhuliawala, Lara J. Martin, Animesh Mehta, Brent Harrison, and Mark O. Riedl. Controllable neural story plot generation via reward shaping. In Proceedings of the Twenty-Eighth International Joint Conference on Artificial Intelligence. International Joint Conferences on Artificial Intelligence Organization, aug 2019. doi: 10.24963/ijcai.2019/829. URL https://doi.org/10.24963%2Fijcai.2019%2F829.

Jorg Tiedemann. Parallel data, tools and interfaces in OPUS. In¨ Proceedings of the Eighth International Conference on Language Resources and Evaluation (LREC’12), pp. 2214–2218, Istanbul, Turkey, May 2012. European Language Resources Association (ELRA). URL http: //www.lrec-conf.org/proceedings/lrec2012/pdf/463\_Paper.pdf.

Erik F Tjong Kim Sang and Fien De Meulder. Introduction to the conll-2003 shared task: Languageindependent named entity recognition. In Proceedings of the seventh conference on Natural language learning at HLT-NAACL 2003, volume 4, pp. 142–147, 2003.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton Ferrer, Moya Chen, Guillem Cucurull, David Esiobu, Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller, Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony Hartshorn, Saghar Hosseini, Rui Hou, Hakan Inan, Marcin Kardas, Viktor Kerkez, Madian Khabsa, Isabel Kloumann, Artem Korenev, Punit Singh Koura, Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Diana Liskovich, Yinghai Lu, Yuning Mao, Xavier Martinet, Todor Mihaylov, Pushkar Mishra, Igor Molybog, Yixin Nie, Andrew Poulton, Jeremy Reizenstein, Rashi Rungta, Kalyan Saladi, Alan Schelten, Ruan Silva, Eric Michael Smith, Ranjan Subramanian, Xiaoqing Ellen Tan, Binh Tang, Ross Taylor, Adina Williams, Jian Xiang Kuan, Puxin Xu, Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan, Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, and Thomas Scialom. Llama 2: Open foundation and fine-tuned chat models, 2023.

Siddharth Verma, Justin Fu, Mengjiao Yang, and Sergey Levine. Chai: A chatbot ai for task-oriented dialogue with offline reinforcement learning, 2022.

Michael Volske, Martin Potthast, Shahbaz Syed, and Benno Stein. Tl; dr: Mining reddit to learn¨ automatic summarization. In Proceedings of the Workshop on New Frontiers in Summarization, pp. 59–63, 2017.

Alex Wang, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy, and Samuel R. Bowman. GLUE: A multi-task benchmark and analysis platform for natural language understanding. In International Conference on Learning Representations, 2019. URL https://openreview. net/forum?id=rJ4km2R5t7.

Ruoyao Wang, Peter Jansen, Marc-Alexandre Cotˆ e, and Prithviraj Ammanabrolu. Scienceworld: Is´ your agent smarter than a 5th grader? arXiv preprint arXiv:2203.07540, 2022a.

Yizhong Wang, Swaroop Mishra, Pegah Alipoormolabashi, Yeganeh Kordi, Amirreza Mirzaei, Atharva Naik, Arjun Ashok, Arut Selvan Dhanasekaran, Anjana Arunkumar, David Stap, et al. Super-naturalinstructions: Generalization via declarative instructions on 1600+ nlp tasks. In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing, pp. 5085–5109, 2022b.

Yue Wang, Hung Le, Akhilesh Deepak Gotmare, Nghi D. Q. Bui, Junnan Li, and Steven C. H. Hoi. Codet5+: Open code large language models for code understanding and generation, 2023.

Jason Wei, Maarten Bosma, Vincent Y. Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M. Dai, and Quoc V. Le. Finetuned language models are zero-shot learners, 2022.

Adina Williams, Nikita Nangia, and Samuel Bowman. A broad-coverage challenge corpus for sentence understanding through inference. arXiv preprint arXiv:1804.08198, 2018.

Jeff Wu, Long Ouyang, Daniel M Ziegler, Nisan Stiennon, Ryan Lowe, Jan Leike, and Paul Christiano. Recursively summarizing books with human feedback. arXiv preprint arXiv:2109.10862, 2021.

Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V. Le, Mohammad Norouzi, Wolfgang Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, Jeff Klingner, Apurva Shah, Melvin Johnson, Xiaobing Liu, Łukasz Kaiser, Stephan Gouws, Yoshikiyo Kato, Taku Kudo, Hideto Kazawa, Keith Stevens, George Kurian, Nishant Patil, Wei Wang, Cliff Young, Jason Smith, Jason Riesa, Alex Rudnick, Oriol Vinyals, Greg Corrado, Macduff Hughes, and Jeffrey Dean. Google’s neural machine translation system: Bridging the gap between human and machine translation, 2016.

Yuxiang Wu and Baotian Hu. Learning to extract coherent summary via deep reinforcement learning, 2018.

Shunyu Yao, Howard Chen, John Yang, and Karthik Narasimhan. Webshop: Towards scalable real-world web interaction with grounded language agents, 2023.

Daniel M. Ziegler, Nisan Stiennon, Jeffrey Wu, Tom B. Brown, Alec Radford, Dario Amodei, Paul Christiano, and Geoffrey Irving. Fine-tuning language models from human preferences, 2020.

## A FURTHER DETAILS ON TASK DESIGN

In this appendix, we lay out in more formalism why certain tasks test certain properties and go into more detail underlying the interactions involved in each task. We discuss both the RL Capability Tests and the Interactive Dialogue Tasks.

## A.1 RL CAPABILITY TESTS

The 5 RL Capability tasks are chosen such that they highlight specific properties. For example, for each of the Maze and Text-Nav tasks we include a partially observed and fully observed version to highlight this contrast. We include both the Maze and Text-Nav because they are very similar tasks but are different in that Text-Nav includes more complicated textual descriptions and Maze has a more complicated layout. Similarly, we chose to include Wordle to test strategic decision-making in a partially observed environment. Chess and Endgames test strategic decision-making, but in a fully observed environment and with a more difficult strategy. The Maze, Text-Nav, Chess, and Chess Endgames are all text-based representations of symbolic tasks where RL has shown success.

Maze. We design a maze task and maze-solving dataset to test the credit assignment and trajectory stitching capabilities discussed in Section 4.1. We test trajectory stitching by including highly suboptimal data. We test credit assignment by restricting the generation of the data such that the only dataset trajectories that reaches the goal start near the goal. We accomplish this by splitting the maze up into symmetrical submazes and restricting all traversed states in a dataset trajectory to a given submaze. The fully observed version of the maze (FO) includes the coordinates in the maze in each state, whereas the partially observed version only includes the history of actions. We design the reward function such that the agent receives a reward of −1 for non-goal states and 0 for goal states.

Text-based Navigation (Text-Nav). We design a text-based game based on navigation in a house environment using a modified version of the TextWorld engine (Cotˆ e et al.´ , 2018). This task tests credit assignment and trajectory stitching like the maze task as well as testing the ability of the agent to parse more complex language, and learn which text is relevant and not relevant to solving the task at hand.

Wordle. We use the game of Wordle as a flexible unit-test task for assessing the ability of our language models to execute complex information-seeking behavior in a partially observed setting. In the game Wordle the agent is given at most 6 attempts to guess a hidden 5-letter word. After each guess, the agent is told whether each letter in the guessed word is: 1) in the hidden word and in the right position, 2) in the hidden word but not in the right position, or 3) not in the hidden word. Through this process, each step provides the agent with more information on what the correct word would be and narrows the possible choices for the final word. Since Wordle involves reasoning about words at the level of individual letters, this can induce issues for standard language model tokenizers. Therefore, we represent words as a sequence of space-separated letters, which will cause most standard LM tokenizers to automatically represent each letter as a separate token.

Chess. We create a text-based chess task to test the strategic decision-making, credit assignment, and trajectory stitching abilities of an RL algorithm. To generate the data, we have Stockfish 15.1 simulating the agent of various strengths play against another environment Stockfish engine with elo 1200 simulating the environment. This test trajectory stitching, because the agent needs to make good and legal moves in losing positions as well as winning positions. We use FEN (Forsyth-Edwards Notation) notation to represent the board state at each turn and we utilize the SAN (Short Algebraic Notation) to represent each action, both of which are standard notations used by the chess community.

Endgames (Theoretical Chess Endgames). Chess endgames provide a simpler and more goaldirected variation of the chess task. By focusing on the endgame, we encourage algorithms to learn strategy rather than memorizing the opening moves of a chess game. A classic theoretical endgame position consists of a position where the only pieces on the board are the two kings and the queen. Although the board position appears simple, a sequence of carefully calculated moves is required to win. A simpler board state allows language models to make progress without fewer computational resources. We use an ϵ-greedy dataset generation process, meaning we generate an optimal move with probability ϵ and a random move with probability 1 − ϵ. This forces the model to trajectory stitch and learn from optimal moves in failed trajectories and not suboptimal moves in successful trajectories.

## A.1.1 INTERACTIVE DIALOGUE TASKS

For the interactive dialogue tasks, we chose two tasks that involve rational decision-making (20Qs, Guess) and information gathering and one that involves negotiation (Car Dealer). These tasks aim to simulate real world interactions between humans.

Unlike in supervised learning, where training and validation losses serve as reliable indicators of performance, in RL, these metrics do not provide a meaningful measure of policy effectiveness (Sutton & Barto, 2018). Instead, the policy must interact with the environment for evaluation. However, in the case of language-based RL tasks, relying on human evaluators to conduct thousands of assessment rollouts throughout and after training becomes infeasible. To address this challenge, we have built simulators with another LLM for tasks involving dialog and carefully scripted environments for text-game tasks. While simulation may not perfectly replicate human natural language in social situations, it provides a strong indicator to assess the efficacy of an RL method (Park et al., 2023).

20Qs (Twenty Questions). This task tests information gathering to see if a policy can successfully reason about an unknown subject based on context to determine what it is. Additionally, it also evaluates the ability of the model to understand semantics, as it also needs knowledge about the objects in question. In twenty questions, one player (the oracle) thinks of an object, and the agent (the guesser) tries to guess what it is by asking a series of yes-or-no questions. In this interaction, the oracle serves as the environment, and the agent learning a policy to solve the game is the guesser.

Guess (Guess My City). This task simulates a more complicated guessing game, where one player (the oracle) is from a specific city, and the other player (the guesser) tries to guess what city the oracle is from. Here, the guesser can ask not only yes and no questions, but can also ask open-ended questions. This task tests strategic decision-making and the ability of algorithms to handle complex language, as it allows the agent to go beyond learning to ask yes/no questions and learning to ask questions open-ended questions that provide the agent with more information.

Car Dealer. This task simulates a conversation between a car buyer and a car dealer, each with different strategies for getting the best deal. The buyer wants to buy a certain type of car within a certain budget, and the car dealer wants to complete the sale ideally with a high sale price. We have designed the task such that there exist three different kinds of sellers and three different buyers, each primed with a different strategy. Hence, agents should learn to make agreements with buyers who are most compatible with their strategy. This allows us to test the ability of RL algorithms to learn strategic decision-making and credit assignment, by learning which strategies led to a successful sale of the car.

## B FURTHER DETAILS ON DESIDERATA FOR EFFECTIVE MULTI-TURN RL

A crucial aspect of training RL models involves assessing, both during and after the training process, the extent to which the trained policy has successfully accomplished its objectives. Although LLMs are able to perform well on tasks, do not have any way of knowing how to solve a specific task like a text game or selling a car, because they need to train on the particular game/customers/etc.

Unlike in supervised learning, where training and validation losses serve as reliable indicators of performance, in RL, these metrics do not provide a meaningful measure of policy effectiveness (Sutton & Barto, 2018). Instead, the policy must interact with the environment for evaluation. However, in the case of language-based RL tasks, relying on human evaluators to conduct thousands of assessment rollouts throughout and after training becomes infeasible. To address this challenge, we have built simulators with another LLM for tasks involving dialog and carefully scripted environments for text-game tasks. While simulation may not perfectly replicate human natural language in social situations, it provides a strong indicator to assess the efficacy of an RL method (Park et al., 2023).

Measure of Success. Similar to the point on being easy to evaluate, our tasks must have a clear measure of success. For example, if a deal is made, or if a word is correctly guessed, or the game is won these are clearly distinct from a deal not being made or losing the game. This provides a clear goal for the agent to achieve and also make it easy for researchers to compare methods. In addition this allows for a intuitive reward design where we reward the agent for success and penalize for failure.

Unit Test Functionality. We aim to design a benchmark such that some of the tasks can be used to test and isolate RL capabilities as described in Section 4.1. This means that we create benchmarks that emphasize some capabilities over others. For example, we design a maze task such that it evaluates the credit assignment and trajectory stitching capabilities, but uses more simple language. Other tasks such as twenty questions test the complex language and partial observability capabilities with less emphasis on credit assignment.

Task-Specific Reasoning. In our tasks we utilize information and reasoning problems that a large language model is unlikely to have seen in the pre-training data. This means that the algorithm must adapt to a specific task environment through fine-tuning. For example, it is unlikely that the algorithm will have experienced a specific maze layout or the preferences of a specific customer in the pre-training data.

Suboptimal Data. RL has the advantage of being able to use suboptimal data in order to learn more optimal behaviors and therefore learn a policy better than the policy represented in the dataset. As discussed in the previous section on capabilities enabled by RL, the way that RL can do this is by stitching together optimal parts of suboptimal trajectories or learning to assign credit to the optimal actions within suboptimal trajectories. In addition, suboptimal data can be utilized by RL to learn the dynamics of the MDP outside of the space traversed by optimal trajectories.

## C DATASET GENERATION, STATISTICS, & REWARDS

We provide further details pertaining to how each dataset was generated as well as relevant statistics.

## C.1 MAZE

We aim to collect our 1.2k trajectories in such a way that it will challenge the algorithm to perform trajectory stitching and credit assignment. We do this by splitting up the maze into three ”submazes” and then controlling generation such that the dataset trajectories are restricted to one of the submazes. The trajectories themselves are generated using a policy such that 15% of the actions are taken by a suboptimal maze solver and the remaining 85% of the actions are random.

This tests trajectory stitching, because there are no optimal paths from the start to the goal thereby forcing the algorithm to trajectory stitch. Furthermore, this also tests credit assignment, because the only paths which successfully reach the goal are the ones that start in the same submaze as the goal. Therefore the algorithm must learn to realize that successful trajectories occur because of taking the correct actions, not because of random chance.

The reward function is 0 for every action that takes the agent to the goal, -1 for every move that is not the goal. Each episode has a maximum of 100 moves.

## C.2 TEXT-BASED NAVIGATION

We design a text-based game based on navigation in a house environment using a modified version of the TextWorld engine (Cotˆ e et al. ´ , 2018). The house environment consists of 10 uniquely named rooms with various interactable objects that can be opened, closed, picked up, or placed. The agent is tasked to pick up stale food from the living room and place it into the fridge in the kitchen. At the beginning of each episode, the agent spawns at a random room in the house. The state of the environment consists of the following components: (1) the room that the agent is currently in, (2) the objects that the agent currently holds, (3) the objects in the room that the agent can interact with, and (4) the exits the agent can take (as a cardinal direction).

Like in the maze task, we collect data so that algorithms must perform both trajectory stitching and credit assignment to successfully solve the task. We do this by partitioning the rooms in the house into two halves based on proximity to the kitchen. We consider two behavior policies that collect the dataset, each of which behaves greedily-optimal in one half of the rooms, and uniformly at random otherwise. Therefore, if the agent spawns in rooms farther from the kitchen, trajectory stitching is required to learn a successful trajectory. Moreover, successful trajectories in the dataset will only be due to the agent spawning in a room close to the kitchen, which can only be recognized with proper credit assignment.

The reward is 1 for reaching the goal state and 0 for every state that is not the goal state.

## C.3 WORDLE

For wordle we define the environment to use a subset of 400 words from the official wordle vocabulary list. We then generate the dataset using a policy that samples a word uniform at random from this vocabulary with 66% probability and otherwise samples a word from the vocabulary that meets all known letter constraints. This policy achieves a reward of -4.12, which is far worse than the -1.94 reward achieved by a high performing scripted policy, which we use to represent a loose upper bound for this task. We generate 1 million trajectories for training and 100k trajectories for evaluation, using our suboptimal policy.

The reward is -1 for every word that is not a final guess and 0 for every word that is not.

## C.4 CHESS

We collect our data for the chess task using Stockfish 15.1 to generate both sides of the board. The Stockfish opponent in the dataset is Stockfish with an elo of 1200 which matches the environment, and the Stockfish engine with the white pieces has levels ranging from an elo of 800 to 1600. We choose to keep the level of the Stockfish opponent fixed so that there are no inconsistencies between the dataset and the evaluation of the chess agent in the environment. When generating the dataset, we first uniformly randomly select a Stockfish elo y between 800 and 1600 and then generate 100 games of chess play between the Stockfish agent of elo y and the opponent of elo 1200. In addition to storing the state and action, we also store the opponent’s move and the elo of the Stockfish agent used to generate the agent policy in that game so that the dataset can be filtered by elo used.

The reward is 1 for a move that results in victory, 0 for a legal move and -1 for an illegal move.

## C.5 CHESS ENDGAMES

We generate the dataset by first selecting a random legal theoretical endgame position and a probability ϵ. Then we generate a game from the random position, making a random move with probability ϵ and an optimal computer move with probability 1 − ϵ. The opponent in the dataset and the evaluation environment is Stockfish elo 1200. We only include positions with a Queen, Queen and Rook, Rook, and two Rooks and select 30,000 random starting positions for each variation. (i.e. 30,000 positions with only a Queen in addition to the two Kings, another 30,000 with only Queen and Rook etc) for a total of 120,000 theoretical endgame positions.

Because there are more restrictions on this version of the task with fewer pieces on the board, we check how many states in the dataset are unique and we find that there are 1,086,314 unique states in the dataset which accounts for 93% of the states being unique. In addition, 38.28% of the moves in the dataset are generated by the stockfish engine. In the dataset of won games, 94.8% of the states are unique and 41.78% of the games are made by the engine with 58.623% of the total states in the dataset of victorious games.

The reward is the same as for chess.

## C.6 TWENTY QUESTIONS

The dataset we collect consists of 100K full conversations between the guesser and the oracle. The oracle can choose from a set of 158 unique objects taken from 17 different categories of objects/animals. Each object has a roughly equal amount of conversations in the dataset but varies in terms of how many conversations are successful in guessing the object. However, every object has at least one conversation where it is guessed correctly to facilitate learning.

For the reward function, since we want the guesser to guess the correct word in as few guesses as possible, the reward function reflects this by penalizing the guesser for each question that does not guess the correct word.

$$
r ( { \mathrm { q u e s t i o n } } ) = { \left\{ \begin{array} { l l } { 0 } & { { \mathrm { i f ~ } } { \mathrm { q u e s t i o n ~ c o r r e c t l y ~ g u e s s e d ~ t h e ~ w o r d } } } \\ { - 1 } & { { \mathrm { o t h e r w i s e } } } \end{array} \right. }\tag{1}
$$

If the guesser model correctly guessed the word, then the trajectory ends. Over twenty questions, the maximum total sum of rewards is 0 if the guesser guessed the word on the first question, whereas the minimum is −20 if the guesser did not guess the word in twenty questions.

The method for collecting the dataset is as follows. For each conversation, we select uniformly at random from the above list the word that the oracle is answering question about. The oracle is an LLM (OpenAI’s GPT3.5) given the following prompt. In our prompts, we denote variables that we fill in with variable data with {{variable}}.

You are a question answering oracle. You will answer each   
question about an object with Yes or No. If the answer   
could be both, answer with the most typical scenario. Here   
are a few examples:   
example 1:   
object: Computer   
question: Does the object use electricity?   
answer: Yes.   
explanation of answer: Computers need electricity to   
function.   
example 2:   
object: Cup   
question: Is the object a piece of furniture?   
answer: No.   
explanation of answer: A cup is a utensil, not a furniture.   
example 3:   
object: Pen   
question: Is the object alive?   
answer: No.   
explanation of answer: A pen is not a living organism.   
example 4:   
object: Apple   
question: Is it edible?   
answer: Yes.

explanation of answer: An apple is an edible fruit.

Answer the question about the object truthfully.   
object: {{word}}   
question: {{question}}   
answer (yes or no):

By using the OpenAI TextCompletion API, we can extract from the generated text either ”yes” or ”no”.

We also prompt another LLM (the same model as the oracle) to generate questions for the guesser. The prompt for the guesser changes depending on the input to the model and how far along it is in its guessing process. The following prompt is used for the first guess:

You are playing a game of twenty questions. You can ask   
20 yes-no questions to determine the identity of an object   
chosen by an oracle. Each turn, you can ask a question and   
receives a "Yes" or "No" as the answer. You are smart, so   
you will ask the question that will narrow down the possible   
objects as much as possible. Don’t get stuck on one idea   
and try to branch out if you get stuck.

Generate the first yes-no question you will ask to determine   
the object.

## The following prompt is used for the subsequent guesses: The following prompt is used for the subsequent guesses:

You are playing a game of twenty questions. You can ask   
20 yes-no questions to determine the identity of an object   
chosen by an oracle. Each turn, you can ask a question and   
receives a "Yes" or "No" as the answer. You have already   
asked {{conversation length}} questions. You are smart, so   
you will ask the question that will narrow down the possible   
objects as much as possible. Don’t get stuck on one idea   
and try to branch out if you get stuck.   
Here are the questions you’ve asked and their corresponding   
answers:   
{{list of questions and answers, e.g. Is the object alive?   
No.}}   
Based on what you know about the object so far, generate the   
next yes-no question you will ask to determine the object.   
The following prompt is used for the final guess after the guesser has guessed 19 times:   
You are playing a game of twenty questions. You can ask   
20 yes-no questions to determine the identity of an object   
chosen by an oracle. Each turn, you can ask a question and   
receives a "Yes" or "No" as the answer. You have already   
asked 19 questions, so this is your final guess.   
Here are the questions you’ve asked and their corresponding   
answers:   
{{list of questions and answers, e.g. Is the object alive?   
No.}}   
Based on what you know about the object so far, generate   
your final guess of what the object is. Only guess one   
object.   
Is the object Is t.he object

We determine whether the guesser has correctly guessed the word, and thus ending the conversation, by using the NLTK POS tagger to check that the only nouns that the question contains are the correct words, and that they appear at the end of the sentence.

We used these prompts to generate 1000 conversations by prompting the GPT3 back and forth using the response of one to add to the response of the other as described. Afterwards, we fine-tuned two FLAN-T5-XL models with our collected conversations to generate 100K more conversations. The FLAN-T5-XL oracle also serves as the environment for the RL environment when we evaluate the trained policy.

## C.7 GUESS MY CITY

This dataset also consists of 100K full conversations between the guesser and the oracle. The oracle can choose from a set of 100 unique cities, which we selected by looking at the most populated cities in the world. Each city has a roughly equal amount of conversations in the dataset but varies in terms of how many conversations are successful in guessing the object. However, every object has at least one conversation where it is guessed correctly to facilitate learning. The reward function is the same as that for 20 Questions, with a similar data generation and prompt structure. However, we do include constraints in the prompt to make sure that the name of the city or country it is in is not revealed in the answer from the oracle.

## C.8 CAR DEALER

This dataset consists of 19k conversations between a car dealer and a buyer. The car dealer and the buyer have three distinct strategies each that they employ. We design the car dealer and buyer pairs such that the car dealer is best at selling to a particular buyer personality, but often fails to sell to the other buyer personalities. This ensures that the seller can learn information about the buyer and i.e. their persona to figure out if they can form an agreement. The buyer personalities are 1) a buyer that loves discounts 2) a buyer that wants a lot of cool features on their car and 3) an impatient buyer. The car dealer personalities are 1) a car dealer that loves to give discounts 2) a car dealer that talks a lot about the features of the car and 3) a very concise car dealer.

We created this protocol of creating car dealer and buyer strategies in order to encourage the car dealer to employ diverse negotiation tactics. The ideal car dealer would be able to be concise, provide the right amount of discounts, and talk enough about the car to get the buyer interested without overwhelming them. By employing such a strategy of buyer and car dealer personas, we ensure that algorithms that do well in this task will learn effective strategies, understanding of language, and interpretation of the other speaker, amongst many other persuasive techniques. We seek to show that our baseline algorithms do learn to improve their strategy over the dataset.

In the conversation below, the buyer and car dealer are unable to form an agreement as their strategies do not align.

Background buyer: The buyer will never buy from the seller   
unless given a discount.   
Background seller: The agent never gives discounts, never   
talks about the features of the car, and is very concise.   
Preferred brands: Tesla   
Preferred features: ["Apple CarPlay/Android Auto",   
"Bluetooth", "Blind spot monitoring", "Navigation system",   
"Leather seats", "Sunroof/moonroof", "Remote start", "Heated   
seats", "Third-row seating", "Backup camera"], "budget":   
"90k"   
Agent: Good morning, how can I assist you today?   
Buyer: Hi, I’m interested in purchasing a Tesla Minivan.   
Agent: Great choice. Our dealership has a variety of Tesla   
models available.   
Buyer: Do you have any discounts available?   
Agent: I’m sorry, but we don’t offer discounts.   
Buyer: Without a discount, I’m not sure if I can afford it.   
Agent: I understand. The Tesla Minivan is a premium   
vehicle with advanced features.   
Buyer: Is there any flexibility with the price?   
Agent: Our prices are fixed, and we don’t negotiate.   
Buyer: I really want the Tesla Minivan, but I can’t go over   
my budget of \$90k.   
Agent: I appreciate your budget constraint. Let me check   
the available options for you.   
Agent checks inventory.   
Agent: We do have a Tesla Minivan with all the features you   
mentioned, priced at \$95k.   
Buyer: That’s above my budget. Is there anything you can   
do to bring the price down?   
Agent: I’m sorry, but as I mentioned earlier, our prices   
are fixed.   
Buyer: Is there any possibility of getting the same   
features in a different model within my budget?   
Agent: Unfortunately, the Tesla Minivan is the only model

that offers all the features you mentioned.   
Buyer: In that case, I’m afraid I won’t be able to purchase   
the car.   
Agent: I understand. Thank you for considering our   
dealership. If you change your mind, feel free to reach   
out.   
Buyer: (probability of buying: 0%, purchase price: \$0)   
[End of conversation]   
Probability of buying: 0   
Purchase price: \$0   
e conversation below, the buyer and car dealer have similar personas of wanting to hear and   
bout the features of the car respectively.   
Background buyer: The buyer will only buy the car if it   
meets all of their specifications.   
Background seller: The agent never gives discounts and   
loves to talk a lot about features of the car.   
Preferred brands: "Lexus", "preferred features":   
[Navigation system"], "budget": "70k"   
Agent: Good afternoon! Welcome to our car dealership. How   
can I assist you today?   
Buyer: Hi there! I’m looking for a Lexus Minivan with a   
Navigation system.   
Agent: Excellent choice! The Lexus Minivan is a top-notch   
vehicle with plenty of impressive features. The Navigation   
system is definitely a must-have. Let me show you some   
options we have available. Buyer: That sounds great. I’m   
quite particular about my budget, though. I have a maximum   
of \$70,000 to spend.   
Agent: Noted. We have a few Lexus Minivans in stock that   
fall within your budget. Let me tell you about their   
features and options. This way, you can make an informed   
decision.   
Buyer: I appreciate that, but I really want to stick to my   
budget. I won’t be able to go over \$70,000.   
Agent: I understand your concern, but unfortunately, we do   
not offer any discounts or negotiate on prices. However,   
let me assure you that the Lexus Minivan is worth every   
penny. Its advanced safety features, luxurious interior,   
and reliable performance make it a great investment.   
Buyer: I understand your point, but I’m afraid I won’t be   
able to stretch my budget beyond \$70,000.   
Agent: I completely respect your budget and decision. Let   
me show you a Lexus Minivan that fits your requirements   
perfectly. It has all the features you desire, including   
the Navigation system. The price of this model is \$72,000.   
Buyer: I really like the sound of that car, but I can’t go   
over my budget. Is there anything else available within my   
price range?   
Agent: I apologize for any inconvenience caused. Let me   
check our inventory to see if there are any other options   
that meet your requirements and budget.   
Agent checks inventory   
Agent: Good news! I found another Lexus Minivan that meets   
all your specifications and falls within your budget. This   
model is priced at \$69,500.   
Buyer: That sounds much better! I’m interested in that   
car.   
Agent: I’m glad to hear that! This particular Lexus   
Minivan is a great choice. It has the Navigation system,   
as well as additional features such as leather seats, a   
sunroof, and advanced safety technology. The total price is   
\$69,500.   
Buyer: That sounds perfect! I’ll take it!   
Agent: Fantastic! I’m thrilled that we could find the   
perfect car for you. Your total purchase price will be

\$69,500.   
Buyer: Probability of buying a car: 100%   
Purchase price: \$69,500.   
Agent: Congratulations! You’ve made an excellent choice.   
I’ll start the paperwork and get everything ready for you.

We provide another conversation with different value preferences for the buyer, where the buyer forms an agreement with the seller that is higher than their budget:

Preferred Features: Honda, Remote start, Third-row   
seating, Bluetooth, Navigation system, Backup camera, Apple   
CarPlay/Android Auto, Heated seats.Budget: \$10000   
Seller: Welcome to our car dealership. How can I assist   
you today?   
Buyer: I’m looking for a Honda Sedan with remote start,   
third-row seating, Bluetooth, navigation system, backup   
camera, Apple CarPlay/Android Auto, and heated seats.   
Seller: I have a Honda Sedan available. No discounts or   
features to discuss. The price is \$15,000.   
Buyer: That’s too expensive. My budget is \$10,000.   
Seller: I understand your budget is 10, 000.T hepriceis15,000.   
Buyer: I can’t go over \$10,000. That’s my limit.   
Seller: I understand your limit is \$10,000. The price is   
\$15,000.   
Buyer: I really want a Honda Sedan, but \$15,000 is too much   
for me.   
Seller: I understand, but the price is \$15,000.   
Buyer: Okay, I’ll take it for \$10,000. Seller: I   
appreciate your interest. The price is \$15,000. Buyer:   
Fine, I’ll pay \$15,000. Let’s get this done. Seller:   
Thank you for your decision. The price is \$15,000.   
We provide a sample example of a conversation in the training and evaluation set respectively.   
Evaluation Example:   
Background buyer: The buyer will only buy the car if it   
meets all of their specifications.   
Background seller: The agent never gives discounts and   
loves to talk a lot about features of the car.   
Preferred brands: "Tesla", "preferred features": [Backup   
camera, Leather seats"], "budget": "30k"   
Seller: Good afternoon! Welcome to our car dealership.   
How can I assist you today?   
Buyer: Hi there! I’m looking to buy a Tesla Sedan with a   
backup camera and leather seats. Do you have any available?   
Seller: Absolutely! We have a few Tesla Sedans in stock   
that meet your specifications. They are packed with   
features and I’m sure you’ll be impressed. Let me show   
you what we have.   
Buyer: Great! I’m excited to see them.   
Seller: This first Tesla Sedan we have is a 2020 model. It   
has a beautiful backup camera that provides a clear view   
of your surroundings. The leather seats are incredibly   
comfortable and add a touch of luxury to the interior. The   
price for this model is \$35,000. Buyer: \$35,000 is a bit   
higher than my budget of \$30,000. Is there any flexibility   
in the price?   
Seller: I apologize, but we do not offer discounts on our   
cars. However, let me assure you that this Tesla Sedan   
is worth every penny. It is an excellent investment for   
the long term and offers unmatched performance and safety   
features.   
Buyer: I understand, but it’s important for me to stick to   
my budget. Is there any other Tesla Sedan that comes closer   
to my budget?   
Seller: I completely understand your concern. Let me check   
our inventory for other options.[Agent takes a few moments

to check inventory]   
Agent: I have good news! We have another Tesla Sedan that   
is a 2019 model. It also has a backup camera and leather   
seats. The price for this model is \$28,000.   
Buyer: That sounds much better. Can you tell me more about   
this specific model?   
Agent: Of course! This 2019 Tesla Sedan is in excellent   
condition. It has the same backup camera and leather   
seats as the previous model I showed you. It also comes   
with advanced safety features and impressive performance   
capabilities. The previous owner took great care of it,   
and it has low mileage. I truly believe this is an amazing   
deal.   
Buyer: The price is within my budget, and the features   
sound appealing. I’m leaning towards this one. Can you   
provide any additional incentives or options?   
Agent: I’m sorry, but as I mentioned earlier, we do not   
offer discounts or incentives. However, I can assure you   
that this Tesla Sedan is a fantastic choice. It meets all   
your specifications and offers exceptional value for the   
price.   
Buyer: I understand. Given that it meets all my   
requirements and is within my budget, I think I’m ready   
to make the purchase.   
Agent: That’s great to hear! I believe you’ve made an   
excellent choice. The predicted probability of you buying   
this car is 100%, and the purchase price is \$28,000."

## D HYPERPARAMETERS FOR ALL TASKS

## E EVALUATION DETAILS

We normalize Table 9 such that 50 is the dataset average return, 0 is the minimum, and 100 is the maximum. The normalization process works as follows: if the reward is greater than the average return we calculate:

$$
\mathrm { s c o r e = 5 0 + \frac { \ r a w \ r e t u r n - d a t a s e t a v e r a g e } { m a x \ r a w \ r e t u r n - d a t a s e t a v e r a g e } \times 5 0 }
$$

Otherwise if the reward is less than the average return we calculate

$$
{ \mathrm { s c o r e } } = { \frac { \mathrm { r a w ~ r e t u r n } - { \mathrm { m i n ~ r a w ~ r e t u r n } } } { \mathrm { d a t a s e t ~ a v e r a g e } - { \mathrm { m i n ~ r a w ~ r e t u r n } } } } \times 5 0
$$

In the following sections, we discuss more in-depth the evaluation protocol for the various tasks.

## E.1 MAZE

For evaluating the maze task, we take 32 rollouts from each of the 25 possible positions and then average the result. In the environment, the agent has 100 moves to successfully make it to the goal otherwise the episode will terminate. Since the agent receives -1 reward for every move that does not reach the goal state the minimum possible goal state, the minimum reward is -101. We compute the dataset average reward, by sampling actions according to how likely they are in the dataset. We compute the maximum possible reward by evaluating the optimal policy from each of the possible start positions and averaging the results.

## E.2 CHESS

To evaluate the chess agent, we have it play 1000 games against Stockfish elo 1200 from the beginning of the game. As the game progresses, the board positions get increasing OOD for the chess agent so the chess agent often makes illegal moves. To measure this, we track the percent of illegal moves as well as the average episode length for the full game chess agent.

For filtered BC, we simply trained the agent only on games in the dataset which resulted in a victory for the agent, thus denoted BC-Won. Note that BC-Won achieves the worst performance of all algorithms listed. This is because there is a distribution shift between the state visited by a BC-Won agent and the rollouts of the policy. In other words, the ”winning positions” and the ”rollout positions” are two overlapping but distinct distributions especially since the full-game chess agent did not succeed in winning any games.

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>20Qs,Gess, Car</td><td rowspan=1 colspan=1>Maze FO,PO</td><td rowspan=1 colspan=2>Text-Nav</td><td rowspan=1 colspan=1>Chess</td><td rowspan=1 colspan=1>Endgames</td><td rowspan=1 colspan=1>Wordle</td></tr><tr><td rowspan=1 colspan=1>BC</td><td rowspan=1 colspan=1>modellrbatch size</td><td rowspan=1 colspan=1>gpt2-medium,gpt2-medium,gpt2-xe-44128</td><td rowspan=1 colspan=1>gpt2-small1e-4128</td><td rowspan=1 colspan=2>gpt2-small1e-4128</td><td rowspan=1 colspan=1>gpt2-small1e-4, 1e-5,28, 256,32</td><td rowspan=1 colspan=1>gpt2-small1e-4128</td><td rowspan=1 colspan=1>gpt2-small1e-4128</td></tr><tr><td rowspan=1 colspan=1>%BC</td><td rowspan=1 colspan=1>modelbrbatch sizefiltermethod</td><td rowspan=1 colspan=1>gpt2-medium,gptt2-medium,gt2-xle-4128top 10%</td><td rowspan=1 colspan=1>gpt2-smallle-4128success</td><td rowspan=1 colspan=2>gpt2-small1e-4128success</td><td rowspan=1 colspan=1>gpt2-small1e-4128success</td><td rowspan=1 colspan=1>gpt2-small1e-4128success</td><td rowspan=1 colspan=1>gpt2-small1e-4128top 30%</td></tr><tr><td rowspan=1 colspan=1>MC</td><td rowspan=1 colspan=1>modelbrbatch sizeβdiscount γcql weight</td><td rowspan=1 colspan=1>gpt2-meedium,gpt2-medium,gpt2-xe-441281600.990.001</td><td rowspan=1 colspan=1>gpt2-small1e-41281600.990.5</td><td rowspan=1 colspan=2>gpt2-small1e-412840.9900.001</td><td rowspan=1 colspan=1>gpt2-small1e-46480.991e-4</td><td rowspan=1 colspan=1>gpt2-small1e-46480.991, 1le-4</td><td rowspan=1 colspan=1>gpt2-small3e-532641.00.01</td></tr><tr><td rowspan=1 colspan=1>ILQL</td><td rowspan=1 colspan=1>modelbrbatch sizeβcql weightexpectile Tdiiscount </td><td rowspan=1 colspan=1>gpt2-medium,gppt2-medium,gpt2-xle-412840.0010.70.99</td><td rowspan=1 colspan=1>gpt2-small1e-4128160.500.9900.99</td><td rowspan=1 colspan=2>gpt2-small1e-412810.0010.700.99</td><td rowspan=1 colspan=1>gpt2-small1e-412881e-400.700.99</td><td rowspan=1 colspan=1>gpt2-small1e-4128810.70.99</td><td rowspan=1 colspan=1>gpt2-small3e-5323200.010.70.99</td></tr><tr><td rowspan=2 colspan=1>PPO</td><td rowspan=2 colspan=1>modelbrrolloutsbatch sizeGAE discount γK coef.cliip rangeBClossweight</td><td rowspan=1 colspan=1>gpt2-medium,gptmedium,gpt2-x e-6 2048</td><td rowspan=2 colspan=1>gpt2-small1e-65121280.9500.990.10.20</td><td rowspan=1 colspan=2>gpt2-small5e-64000</td><td rowspan=2 colspan=1>gpt2-smallle-510241280..9500.990.010.20</td><td rowspan=2 colspan=1>gpt2-small1e-551212800.9500.990.010.20</td><td rowspan=2 colspan=1>gpt2-small3e-552320.9500.9900.0010.210</td></tr><tr><td rowspan=1 colspan=1>112800.9500.990.010.20</td><td rowspan=1 colspan=2>11280.9500.990.010.20</td><td rowspan=1 colspan=1></td></tr></table>

Table 3: Hyperparameters for baseline experiments.

<table><tr><td></td><td>alg.</td><td>BC</td><td>% BC</td><td>MC Return</td><td>ILQL</td><td>Online PPO</td><td>Online</td><td>% BC</td><td>GPT4</td><td>Human</td></tr><tr><td></td><td>FO Maze</td><td>-72.1</td><td>-56.4</td><td>-48.1</td><td>-6.97</td><td>-37.7</td><td>-71.7</td><td></td><td>-39.7</td><td></td></tr><tr><td></td><td>PO Maze</td><td>-79.5</td><td>-82.9</td><td>-80.3</td><td>-52.9</td><td>-91.7</td><td>-79.5</td><td></td><td>-88.0</td><td></td></tr><tr><td></td><td>FO Text-Nav</td><td>0.39</td><td>0.54</td><td>0.63</td><td>0.88</td><td>0.81</td><td></td><td>0.62</td><td>0.52</td><td></td></tr><tr><td></td><td>PO Text-Nav</td><td>0.25</td><td>0.49</td><td>0.58</td><td>0.76</td><td>0.80</td><td></td><td>0.53</td><td>0.21</td><td></td></tr><tr><td></td><td>Wordle</td><td>-2.81</td><td>-2.85</td><td>-2.16</td><td>-2.04</td><td>-2.63</td><td></td><td>-2.15</td><td>-5.42</td><td></td></tr><tr><td></td><td>Chess</td><td>-22.3</td><td>-56.5</td><td>-28.2</td><td>-21.4</td><td>-16.0</td><td></td><td>-22.3</td><td>-81.3</td><td></td></tr><tr><td></td><td>Endgames</td><td>0.112</td><td>-0.439</td><td>0.588</td><td>0.452</td><td>0.814</td><td></td><td>0.112</td><td>-22.87</td><td></td></tr><tr><td></td><td>20s</td><td>-16.0</td><td>-14.6</td><td>-13.9</td><td>-14.2</td><td>-14.9</td><td></td><td>-16.8</td><td>-13.0</td><td></td></tr><tr><td></td><td>Guess</td><td>-17.0</td><td>-15.2</td><td>-11.2</td><td>-12.5</td><td>-15.1</td><td></td><td>-19.2</td><td>-10.13</td><td></td></tr><tr><td></td><td>Car</td><td>44.5</td><td>54.8</td><td>57.2</td><td>46.3</td><td>50.5</td><td></td><td></td><td></td><td></td></tr></table>

Table 4: Raw statistics for all tasks. In the main paper, the statistics are normalized. Refer to Table 9
<table><tr><td></td><td>Reward Min Score</td><td>Dataset Average Score</td><td>Reward Max Score</td></tr><tr><td>FO</td><td>-101</td><td>-83</td><td>-6.84</td></tr><tr><td>Maze PO Maze</td><td>-101</td><td>-83</td><td>-25.75</td></tr><tr><td>FO Text-Nav</td><td>0</td><td>0.26</td><td>1</td></tr><tr><td>PO Text-Nav</td><td>0</td><td>0.26</td><td>1</td></tr><tr><td>Wordle</td><td>-6</td><td>-4.12</td><td>-1.94</td></tr><tr><td>Chess</td><td>-401</td><td>0.21</td><td>1</td></tr><tr><td>Endgames</td><td>-1</td><td>0.586</td><td>1</td></tr><tr><td>20Qs</td><td>-20.0</td><td>-17.3</td><td>-12.6</td></tr><tr><td>Guess</td><td>-20.0</td><td>-18.8</td><td>-8.56</td></tr><tr><td>Car</td><td>0</td><td></td><td></td></tr></table>

Table 5: In this table we report the minimum, dataset average, and maximum reward used to normalize the results in Table 4 tp get Table 9.

## E.3 CHESS ENDGAMES

To evaluate the chess agent in endgame positions, we select 645 positions not contained in the training dataset and which are not trivially solvable. By trivially solvable, we mean a position which could be solved by stockfish in one to four moves. In order to check this, we use Stockfish’s evaluation tools to select positions which are a mate in 15 or greater. We then have the chess agent play one game from each position of these positions and keep these positions fixed for evaluation purposes. In this case we consider filtered BC to be training BC on all of the trajectories which ended in a victory.

As we can see in the table above, PPO Online significantly outperforms all of the other methods. To investigate whether PPO Online’s performance is simply due to dataset collected, we fine-tune our BC agent on the PPO Online dataset. We do ablations where the data used for training is from the last 50, 25 and 10 rounds of data collection for the PPO policy. We choose to do this ablation because we expect the quality of the PPO policy performance increases in the later rounds of data collection.

## E.4 WORDLE

To evaluate Wordle, we rollout 4096 trajectories against the environment and report the average reward across all the rollouts.

## F BASELINE DETAILS

## F.1 MC DETAILS

The target for these heads is the discounted return-to-go:

$$
R _ { t } = \sum _ { i = t } ^ { T - 1 } \gamma ^ { i - t } r _ { t }\tag{2}
$$

and we use MSE loss for the Q head:

$$
J ( Q ) = \mathbb { E } _ { ( s _ { t } , a _ { t } , r _ { t : T - 1 } ) \sim \mathcal { D } } \left[ ( Q ( s _ { t } , a _ { t } ) - R _ { t } ) ^ { 2 } \right]\tag{3}
$$

(4)

where D represents the dataset. In $\mathbf { M C } , Q ( s _ { t } , a _ { t } )$ represents how much more rewards the policy will get if it takes action $a _ { t }$ at the state $s _ { t }$ under some policy (in this case the policy that collected the dataset).

<table><tr><td></td><td>BC</td><td>BC-Won</td><td>ILQL</td><td>MC Returns</td><td>PPO Offine</td><td>PPO Online</td></tr><tr><td>reward</td><td>-23.189</td><td>-56.522</td><td>-20.46</td><td>-25.47</td><td>-20.90</td><td>-15.95</td></tr><tr><td>percent illegal</td><td>24.929%</td><td>34.91%</td><td>24.76 %</td><td>25.64%</td><td>23.05%</td><td>21.96%</td></tr><tr><td>episode length</td><td>51.01</td><td>92.02</td><td>47.96</td><td>53.44</td><td>48.69</td><td>44.19</td></tr></table>

Table 6: Results of chess agent in the full game positions against Stockfish Elo 1200.
<table><tr><td></td><td>BC</td><td>% BC</td><td>MC</td><td>ILQL</td><td>PPO Offline</td><td>PPO Online</td></tr><tr><td>reward</td><td>0.112</td><td>-0.439</td><td>0.588</td><td>0.452</td><td>-0.019 1</td><td>0.814</td></tr><tr><td>percent victories</td><td>26.233</td><td>26.419</td><td>69.3</td><td>56.7</td><td>28.37 </td><td>88.4</td></tr><tr><td>percent illegal</td><td>0.967</td><td>2.717</td><td>0.692</td><td>0.66</td><td>0.925 —</td><td>0.722</td></tr><tr><td>episode length</td><td>12.923</td><td>23.477</td><td>11.92</td><td>14.6 I</td><td>25.24</td><td>1 8.38</td></tr></table>

Table 7: Comparison between the different baseline methods. The best performance is achieved by PPO Online with a 0.13 gap in performance between PPO Online and the next best-performing method of MC Returns. PPO Online attains overall the highest reward, but BC-Engine wins more frequently and MC Returns and ILQL make fewer illegal moves.

During rollout, when sampling, we perturb the base BC policy with the learned valuefunctions (Snell et al., 2022a). Let $\pi _ { \beta }$ represent the policy trained with BC, and α represent a scalar multiplier, then:

$$
\pi _ { \mathrm { M C } } ( a _ { t } | s _ { t } ) \propto \pi _ { \beta } ( a _ { t } | s _ { t } ) ^ { \alpha Q ( s _ { t } , a _ { t } ) }\tag{5}
$$

## F.2 PPO DETAILS

PPO Implementation Details Our PPO implementation uses a learned value function to estimate an advantage baseline. Our value function is fit using GAE (Schulman et al., 2018) value estimates and is implemented as a linear head on top of the same transformer as the policy. We apply clipping to both the importance weights and the value function, as is done in (Castricato et al., 2023). We also apply a KL penality to the reward, as is standard for RLHF (Stiennon et al., 2022). On some of our tasks, we add a supervised learning, BC, loss term to the standard PPO loss to prevent the model in distribution; this is similar to the approach taken in Ouyang et al. (2022), which adds a pretraining loss term to the PPO loss to mitigate performance regressions on some benchmarks during RLHF.

PPO Instabilities In some cases we observed training instabilities with PPO in which the policy’s performance would increase for a little bit and then collapse (see Figure 5). We primarily observed this on our maze environment. We are uncertain what the cause of this dramatic instability is, and leave further investigation of this phenomenon to future work.

## G SYMBOLIC MAZE ENVIRONMENT

Code to run experiments for the symbolic maze task can be found here: REDACTED. We ran online and offline Q-learning on this environment. The online Q-learning method is DQN and the offline

![](images/368d1769a75a4021bdc360cbf637e64d7fa5a7434429d9ae8f2e803d35bc7811.jpg)  
Figure 5: An example of an observed PPO training instability on the fully observed maze task.

<table><tr><td></td><td>BC</td><td>Complete</td><td>Last 50</td><td>Last 25</td><td>Last 10</td><td>PPO Online</td></tr><tr><td>reward</td><td>0.112</td><td>0.201</td><td>0.17</td><td>0.189</td><td>0.235</td><td>0.814</td></tr><tr><td>percent victories</td><td>26.233</td><td>38.636</td><td>37.023</td><td>40.558</td><td>41.271</td><td>88.4</td></tr><tr><td>percent illegal</td><td>0.967</td><td>1.165</td><td>1.159</td><td>1.213</td><td>1.175</td><td>0.722</td></tr><tr><td>episode length</td><td>12.923</td><td>13.21</td><td>14.22</td><td>14.647</td><td>13.338</td><td>8.38</td></tr></table>

Table 8: Comparison between PPO Online and BC agents fine-tuned on the dataset collected by PPO during training. We chose to train on the complete PPO dataset, the last 50 rounds, last 25 rounds, and last 10 rounds of data collected. PPO Online performance still far surpassed performance of the BC agents trained on the PPO policy dataset. Furthermore, there is no substantive difference between training on the complete PPO dataset and the PPO dataset collected in the last 10 rounds.

Q-learning method is CQL. We found that Q-learning was able to perform optimally on the Maze task in both the online and offline setting. The results are as follows:

<table><tr><td>alg.</td><td>DQN</td><td>CQL</td></tr><tr><td>Symbolic Maze</td><td>100.0</td><td>100.0</td></tr></table>

Table 9: Results for CQL and DQN on the symbolic maze environment. These are normalized in the same way as results on LM RL tasks.

## H GENERATED EXAMPLES FROM TRAINED MODELS

We show an example of a conversation between BC model (seller) and the oracle model (buyer):

Preferred brands: Lexus, 46 features, backup camera, blind   
spot monitoring, sunroof. Budget: \$90000.   
Seller: Good afternoon! How may I assist you today?   
Buyer: Hi there! I’m looking for a Lexus SUV with a backup   
camera, blind spot monitoring, and a sunroof. Do you have   
anything like that?   
Seller: Absolutely! We have a few models that fit that   
description. Do you have a budget in mind?   
Buyer: Well, I’d like to stay around \$90,000, but I’m   
willing to go over that if I find the perfect car.   
Seller: Great! Let me show you our selection. This Lexus   
SUV here has all the features you’re looking for. Have a   
seat inside and take a look. Buyer: Wow, this is really   
nice! How much does it cost? Seller: The MSRP for this   
model is \$87,000, but we can work with you on the price.   
Buyer: Hmm, that’s a bit high for me. Do you have any   
other options?   
Seller: Of course! We have this similar model here for   
\$80,000. It’s a great car and has all the features you’re   
looking for.   
Buyer: That’s more in my budget. Let me take a look   
inside.   
Seller: Absolutely! And if you’re interested, we could   
also discuss financing options.   
Buyer: I’m definitely interested in financing. How does   
that work here?   
Seller: Well, we have a few options available. We can work   
with your bank or credit union, or we can discuss financing   
through our dealership. We also have some special offers   
and promotions available that may be of interest to you.   
Buyer: That sounds good. I definitely want to make sure   
I’m getting the best deal possible.   
Seller: Of course! We want to make sure you’re completely

satisfied with your purchase. And this car here is a great   
value for the features you’re getting. Buyer: You know   
what, I think I’m sold! Let’s do this.   
Seller: Wonderful! I just need to get some paperwork   
started and we can get the financing process going.   
Congratulations on your new car!

## We show a conversation between the MC model (seller) and the oracle (buyer):

Preferred brands: Audi, Sunroof/moonroof, Leather seats,   
Heated seats. Budget: \$70000   
===   
Seller: Good morning, how can I assist you today?   
Buyer: I’m looking to buy an Audi Sedan.   
Seller: Certainly, we have a range of Audi Sedans   
available. What features are you interested in?   
Buyer: I want a car with a sunroof/moonroof, leather seats,   
and heated seats.   
Seller: I understand. Let me check our inventory for Audi   
Sedans with those features. (Pause)   
Seller: We have a few options that meet your requirements.   
The prices range from \$75,000 to \$85,000.   
Buyer: My budget is \$70,000. Can you offer a lower price?   
Seller: I’m sorry, but we don’t offer any discounts. The   
prices are as listed.   
Buyer: I really can’t go over my budget. Is there anything   
you can do? Seller: I apologize for the inconvenience,   
but the prices are fixed. We have quality Audi Sedans that   
meet your preferences. Buyer: (Sighs) Okay, let’s say I   
consider going slightly over my budget. How much would it   
be? Seller: The closest option to your budget is priced   
at \$75,000. Buyer: Hmm, that’s not bad. Can you go any   
lower?   
Seller: I’m sorry, but I can’t lower the price.   
Buyer: Alright, I’ll take it. What’s the final price?   
Seller: The final price is \$75,000.   
Buyer: Okay, let’s proceed with the purchase then.

## I HUMAN EVALUATION EXAMPLES

You are playing a game of twenty questions. You can ask 20 yes-no questions to determine the identity of an object chosen by an oracle. Each turn, you can ask a question and receives a "Yes" or "No" as the answer. You are smart, so you will ask the question that will narrow down the possible objects as much as possible. Don’t get stuck on one idea and try to branch out if you get stuck.

Human: Does the item belong indoors?   
Oracle: No.   
Is the item used for playing sports?   
Oracle: Yes.   
Human: Is the item a ball?   
Oracle: Yes.   
Human: Do you throw the item?   
Oracle: Yes.   
Human: Do you bounce the item?   
Oracle: No.   
Human: Is it a baseball?   
Oracle: No.   
Human: Is it a football?   
Oracle: Yes.

## J RATING EXAMPLES FOR NATURALNESS

We conducted a user study where we provided participants with 18 examples to annotate on a scale from 1 to 5, where 1 represents the least natural and 5 represents the most natural conversation. There were 9 examples that were from GPT, and 9 examples that were generated from one of our models (MC Returns). We showed them examples from 20 Questions, Guess My City, and Car Dealer tasks. We found the following ratings below. Note that each element shows the percentage for the particular label. We found that participants felt conversations from GPT and the MC model where equally natural of 55.56% and 58.53% respectively.

<table><tr><td rowspan=2 colspan=1>Label</td><td rowspan=1 colspan=3>Percentages for GPT</td><td rowspan=1 colspan=3>Percentages for MC Model</td></tr><tr><td rowspan=1 colspan=1>Car Dealer</td><td rowspan=1 colspan=1>Guess City</td><td rowspan=1 colspan=1>20 Questions</td><td rowspan=1 colspan=1>Car Dealer</td><td rowspan=1 colspan=1>Guess City</td><td rowspan=1 colspan=1>20 Questions</td></tr><tr><td rowspan=2 colspan=1>1 - Not Natural2 - Slightly Unnatural</td><td rowspan=2 colspan=1>4.44%24.44%</td><td rowspan=1 colspan=1>13.33%</td><td rowspan=1 colspan=1>24.44%</td><td rowspan=1 colspan=1>8.89%</td><td rowspan=2 colspan=1>11.11%40.00%</td><td rowspan=3 colspan=1>22.22%24.44%8.89%</td></tr><tr><td rowspan=1 colspan=1>35.56%</td><td rowspan=1 colspan=1>31.11%</td><td rowspan=1 colspan=1>17.78%</td></tr><tr><td rowspan=3 colspan=1>3 - Neutral/Natural4 - Quite Natural5 - Very Natural</td><td rowspan=1 colspan=1>20.00%</td><td rowspan=1 colspan=1>24.44%</td><td rowspan=1 colspan=1>15.56%</td><td rowspan=1 colspan=1>17.78%</td><td rowspan=1 colspan=1>20.00%</td></tr><tr><td rowspan=1 colspan=1>24.44%</td><td rowspan=1 colspan=1>22.22%</td><td rowspan=1 colspan=1>13.33%</td><td rowspan=1 colspan=1>31.11%</td><td rowspan=1 colspan=1>20.00%</td><td rowspan=1 colspan=1>35.56%</td></tr><tr><td rowspan=1 colspan=1>26.67%</td><td rowspan=1 colspan=1>4.44%</td><td rowspan=1 colspan=1>15.56%</td><td rowspan=1 colspan=1>24.44%</td><td rowspan=1 colspan=1>8.89%</td><td rowspan=1 colspan=1>8.89%</td></tr></table>

Table 10: User study of humans rating conversations from GPT and from our MC model for three tasks: Car Dealer, Guess City, and 20 Questions.

<table><tr><td rowspan=1 colspan=1>Label</td><td rowspan=1 colspan=1>GPT</td><td rowspan=1 colspan=1>MC Model</td></tr><tr><td rowspan=4 colspan=1>m45</td><td rowspan=1 colspan=1>14.07%</td><td rowspan=1 colspan=1>14.07%</td></tr><tr><td rowspan=1 colspan=1>30.37%20.00%</td><td rowspan=3 colspan=1>27.41%15.56%28.89%14.07%</td></tr><tr><td rowspan=1 colspan=1>20.00%</td></tr><tr><td rowspan=1 colspan=1>15.56%</td></tr><tr><td rowspan=1 colspan=1>Sum (≥ 3)</td><td rowspan=1 colspan=1>55.56%</td><td rowspan=1 colspan=1>58.52%</td></tr></table>

Table 11: Average of percentage ratings for three tasks for GPT and for our MC Model
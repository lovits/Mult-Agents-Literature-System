# B-CODER: VALUE-BASED DEEP REINFORCEMENT LEARNING FOR PROGRAM SYNTHESIS

Zishun Yu∗   
Department of Computer Science   
University of Illinois Chicago   
Chicago, IL 60607   
zyu32@uic.edu Yunzhe Tao, Liyu Chen, Tao Sun & Hongxia Yang ByteDance Inc.   
Seattle, WA 98004   
{yunzhe.tao, liyu.chen1,   
tao.sun, hx.yang}@bytedance.com

## ABSTRACT

Program synthesis aims to create accurate, executable programs from problem specifications, specifically from natural language descriptions in our context. Recent studies have leveraged the power of reinforcement learning (RL) in conjunction with large language models (LLMs), significantly enhancing code generation capabilities. The application of RL focuses on directly optimizing for functional correctness, offering an advantage over conventional supervised methods. Despite policy-based RL methods dominating the literature on RL for program synthesis, the nature of program synthesis tasks hints at a natural alignment with value-based methods. This stems from the rich collection of off-policy programs, including those developed by human programmers and also historical samples, coupled with the straightforward verification of generated programs through automated unit testing, meaning rewards are easy to obtain. Diverging from the dominant use of policy-based algorithms, our work explores the feasibility of value-based approaches, leading to the development of our B-Coder (pronounced Bellman coder). Yet, training value-based methods presents challenges due to the enormous search space inherent to program synthesis. To this end, we introduce an initialization protocol for RL agents utilizing pre-trained LMs and a conservative Bellman operator to reduce training complexities. Moreover, we demonstrate how to leverage the learned value functions as a dual strategy to post-process generated programs. Our empirical evaluations demonstrated B-Coder’s capability in achieving state-of-the-art performance when compared to policy-based methods. Remarkably, this achievement is reached with minimal reward engineering effort, highlighting the effectiveness of value-based RL, independent of reward designs.

## 1 INTRODUCTION

Program synthesis (or code generation) aims to create functionally accurate executable programs from problem specifications, such as input-output (IO) examples (Summers, 1977; Gulwani et al., 2012), constraint-based (Osera & Zdancewic, 2015; Frankle et al., 2016) or natural language descriptions (Hendrycks et al., 2021; Austin et al., 2021), among others. The increasing attention towards this field can be attributed to its potential in transforming the software development paradigm. Notably, AI-powered tools have shown evidence of boosting efficiency within the software industry.

Large language models (LLMs) (Brown et al., 2020; OpenAI, 2023; Anil et al., 2023; Chowdhery et al., 2022; Rae et al., 2021; Hoffmann et al., 2022; Touvron et al., 2023) have garnered substantial interest and shown remarkable achievements. The scheme of pre-training on vast amounts of data has yielded notable successes in natural language generation. This trend extends its influence to program synthesis, where numerous specialized code LLMs (Li et al., 2023; 2022; Nijkamp et al., 2022; Zheng et al., 2023; Fried et al., 2022; Chen et al., 2021a; Wang et al., 2021; 2023; Xu et al., 2023; Roziere et al.\` , 2023) have been introduced to address challenges in program synthesis.

Unlike many free-form natural language generation tasks, where the quality of model’s output is hard to assess, the correctness of synthesized programs can be verified through automated execution with predefined unit tests. This allows for directly optimizing execution outcomes through reinforcement learning (RL), by formulating test outcomes as reward signals. Our discussion focuses on recent RLbased works (Le et al., 2022; Shojaee et al., 2023; Liu et al., 2023) that have achieved remarkable advancements in Python text-to-code generation, evaluated on the challenging benchmarks sourced from Codeforces programming contests (Hendrycks et al., 2021; Li et al., 2022) Notably, these works predominantly favor on-policy policy-based algorithms.

While (on-policy) policy-based methods are favored in existing program synthesis works, they are known to be sample inefficient (Nachum et al., 2017; Gu et al., 2016) due to their inability to use off-policy samples. In contrast, value-based methods, using temporal difference learning, are known to be more sample-efficient (Gu et al., 2016; Nachum et al., 2017; Liu et al., 2020), as they solve a fixed-point iteration which does not explicitly require a specific data distribution, hence offering better compatibility with off-policy data. We defer the technical explanations on on/off-policy data and reasons for the different efficiency to Section 3.2, where we have notations and definitions ready.

In program synthesis, the primary sources of off-policy data include human programs and previously synthesized programs. Both are off-policy as they do not follow the sequence distribution induced by the current model. Current program synthesis works often directly use off-policy samples with onpolicy methods. Unsurprisingly, Shojaee et al. (2023) notices that an increase in off-policy synthetic programs may degrade performance. This occurs as off-policy data lead to biased gradient estimates. Ideally, an objective should be to enhance or at least sustain performance as data volume grows.

To summarize, the reasons that suggest a natural fit for value-based methods in program synthesis are twofold: the availability of (inexpensive) rewards, similar to classical RL tasks like GO and Atari; and the principle compatibility with off-policy data for effectively leveraging human and historical data. However, value-based RL faces challenges such as difficulty in converging in large state-action spaces. To this end, we introduce B-Coder (Bellman coder), with our contributions being threefold:

• We stabilize value-based RL for program synthesis by proposing an initialization protocol for Q-functions and a conservative Bellman operator to mitigate the training complexities.

• We demonstrate how to leverage value functions as a dual strategy to improve generation.

• B-Coder achieves strong empirical performance with minimal reward engineering, providing further insights of RL algorithm design independent of reward function designs.

Paper structure. We introduce related works and notations in Section 2 and 3. Section 4 details our method and the rationale behind our design choices. Specifically, Sections 4.1, 4.2, and 4.3 address the challenges of value function training by: leveraging task structure, providing effective Qfunction initialization, and a conservative operator for stable yet less ambitious updates, respectively. Section 4.5 shows an additional benefit of value functions, and Section 5 shows our empirical results.

## 2 RELATED WORKS

Execution-guided program synthesis. The feasibility of verifying programs through test case outcomes has led to the line of execution-guided works (Chen et al., 2018; Zohar & Wolf, 2018; Chen et al., 2021b). While these efforts leverage execution feedback, they do not directly optimize towards higher execution success rate due to the inherent non-differentiability of execution outcomes.

RL for general sequence modeling. Supervised LM training, using next token predictions (NTP) or masked language modeling (Kenton & Toutanova, 2019), has recognized limitations. One prominent issue is the exposure bias: given that the training is done in a “teacher-forcing” manner (Bengio et al., 2015; Ranzato et al., 2015), errors tend to accumulate during testing due to auto-regressive genera tion. In contrast, prior works (Ranzato et al., 2015; Rennie et al., 2017) have demonstrated the efficacy of RL in addressing exposure bias and optimizing non-differentiable metrics, e.g. BLEU (Pap ineni et al., 2002) and ROUGE (Lin, 2004), by leveraging automatic scoring as reward function.

RL for program synthesis. Supervised losses also fall short when assessing the functional accuracy of synthesized programs (Hendrycks et al., 2021; Chen et al., 2021a). As such, relying solely on supervised learning for program synthesis is not ideal. As RL provides a pathway to directly optimize non-differentiable objectives, plentiful work (Zhong et al., 2017; Simmons-Edler et al., 2018; Ellis et al., 2019; Wang et al., 2022) have studied enhancing code generation through RL. For the works most related to ours: CodeRL (Le et al., 2022) adapted REINFORCE (Williams, 1992), a classic policy gradient (PG) algorithm, along with the baseline trick for variance reduction and a supervisetrained reward model to alleviate the issue of sparse execution signals. In addition, they proposed a critic sampling strategy to refine and repair program based on the example unit tests feedback. PPOCoder (Shojaee et al., 2023) applied proximal policy gradient (Schulman et al., 2017, PPO) to fine-tune pre-trained LMs. In addition, they leverage the syntactic and semantic structure of code, such as syntax trees (Rabinovich et al., 2017) and data-flow graphs (Yasunaga & Liang, 2020), to improve reward function designs. RLTF (Liu et al., 2023) proposed an online training framework for program synthesis using policy gradient with heursitically-designed fine-grained rewards.

Additional discussions. Appendix D lists several RL applications, showing the analogies between program synthesis and tasks that benefit from value-based methods. In C, we extend the discussion on works that extend policy-based methods to an off-policy setting. Such attempts often involve training a value function, further highlighting our motivation for starting with value-based methods.

## 3 PRELIMINARIES

One could formulate the program synthesis task as a sequence-to-sequence generation task, where a model takes a problem description D as input and outputs a program $\hat { W }$ which aims to achieve the functionality specified by $D , \mathbf { A }$ generated program $\hat { W } = ( \hat { w } _ { 0 } , \dots , \hat { w } _ { T } )$ is composed by a sequence of tokens $\hat { w } _ { t } \in \mathcal { V } .$ . For brevity, we use constant T to denote the sequence length although it could be a variable in practice, and W to denote a program in general (both generated and ground truth). Let LM be an instance of LM, $\ell ( ( w _ { < t } , D ) , \cdot )$ be the logits layer (language modelling head) output, and $p ( \cdot | w _ { < t } , D )$ be the probabilistic distribution over the vocabulary $\nu$ (computed by passing $\ell ( \cdot , \cdot )$ through softmax), conditioned on a sequence $w _ { < t }$ and $D .$ . Suppose $W ^ { * }$ is a ground truth program and $\mathcal { D } _ { \mathrm { t r a i n } }$ is the train set, conventionally LMs could be trained by minimizing the cross-entropy loss

$$
\begin{array} { r } { \mathcal { L } _ { \mathrm { c e } } ( p ) = - \mathbb { E } _ { W ^ { * } \sim \mathcal { D } _ { \mathrm { t r a i n } } } \log p ( W ^ { * } | D ) = - \mathbb { E } _ { W ^ { * } \sim \mathcal { D } _ { \mathrm { t r a i n } } } \sum _ { t } \log p ( w _ { t } ^ { * } | w _ { < t } ^ { * } , D ) . } \end{array}\tag{1}
$$

## 3.1 RL NOTATIONS

To make notations easier to interpret, we bridge program synthesis notations to standard RL ones. RL problems are typically formulated as Markov Decision Processes (MDPs) and an MDP M is often composed by a 5-tuple $\mathcal { M } { = } ( S , \mathcal { A } , \mathbb { P } , r , \gamma )$ which are state space, action space, transition function, reward function and discount factor, respectively. The discount factor $\gamma$ discounts future values to emphasize the near futures, and we use $\gamma { = } 0$ .999 (which slightly prefers more concise solution). A (stochastic) transition function $\mathbb { P } : \mathcal { S } \times \mathcal { A }  \Delta ( \mathcal { S } )$ is a distribution over $s$ conditioned on a stateaction pair (s, a). In program synthesis, P is trivial as $s _ { t + 1 } \equiv s _ { t } \circ a _ { t }$ , where ◦ denotes concatenation.

State and action. In code generation context, an action $a _ { t }$ is a token $\hat { w } _ { t }$ . Hence the action space $\mathcal { A }$ is the vocabulary V. As the information used to generate token $\hat { w } _ { t }$ is $( \hat { w } _ { < t } , D )$ , the state is hence defined as $s _ { t } : = ( \hat { w } _ { < t } , D )$ . For a given $D _ { \colon }$ , the state space ${ \boldsymbol { S } } = \nu ^ { T }$ . For brevity, we will mainly use $s _ { t } , a _ { t }$ rather than the $w _ { t }$ notations, and sometimes omit the time index t if it leads to no confusion. We will also use $s ^ { \prime } , a ^ { \prime }$ to denote $s _ { t + 1 } , a _ { t + 1 }$ whenever only the relative temporal position matters.

Policy. A policy $\pi : S  \Delta ( { \mathcal { A } } )$ assigns an action distribution $\Delta ( \mathcal { A } )$ to any state $s \in S$ , meaning predicting a token $\hat { w } _ { t }$ based on current sequence $\hat { w } _ { < t }$ and the problem specification D. Prior works often define $\pi _ { \boldsymbol { \theta } } \equiv p _ { \boldsymbol { \theta } }$ and directly optimize LM parameters θ with PG methods. We however define $\pi : = f ( \theta , \bigsqcup )$ to be a function of θ and other components □, see details in Section 4.

Reward function. A reward function termines reward of taking action $a _ { t }$ at state $s _ { t }$ . We follow the reward design of Le et al. (2022) in equation 2. We may also use shorthand notation $r _ { t } : = r ( s _ { t } , a _ { t } )$ . Note that the reward is determined when the program W is completed at T . Thus $r _ { t } = 0 \mathrm { i f } t \neq T$ otherwise defined as equation 2.

$$
r : S \times { \mathcal { A } } \to \mathbb { R } \ \mathrm { d e } - \quad \quad r ( W ) = r ( s _ { T } , a _ { T } ) =
$$

$$
\left\{ \begin{array} { l l } { + 1 . 0 , \mathrm { i f } W \mathrm { p a s s e d a l l u n i t t e s t s } } \\ { - 0 . 3 , \mathrm { i f } W \mathrm { f a i l e d a n y u n i t t e s t } } \\ { - 0 . 6 , \mathrm { i f } W \mathrm { c a n n o t b e } \mathrm { e x e c u t e d } } \\ { - 1 . 0 , \mathrm { i f } W \mathrm { c a n n o t b e } \mathrm { c o m p i l e d } } \end{array} \right.\tag{2}
$$

Value functions. RL maximizes the discounted returns, $\begin{array} { r } { J ( \pi ) = \mathbb { E } [ \sum _ { t } \gamma ^ { t } r _ { t } | \pi , \mathcal { M } ] } \end{array}$ . The state-action value function $Q ^ { \pi } : S \times { \mathcal { A } } $ R and the state value function $V ^ { \pi } : S \xrightarrow { - } \mathbb { R }$ , are defined recursively as:

$$
\begin{array} { r } { V ^ { \pi } ( s ) : = \mathbb { E } \left[ \sum _ { t = 0 } ^ { \infty } \gamma ^ { t } r _ { t } | \pi , \mathcal { M } , S _ { 0 } = s \right] = \mathbb { E } _ { a \sim \pi ( \cdot | s ) , s ^ { \prime } \sim \mathbb { P } ( \cdot | s , a ) } \left[ r ( s , a ) + \gamma V ^ { \pi } ( s ^ { \prime } ) \right] } \end{array}\tag{3}
$$

$$
\begin{array} { r } { Q ^ { \pi } ( s , a ) : =  { \mathbb { E } \left[ \sum _ { t = 0 } ^ { \infty } \gamma ^ { t } r _ { t } | \pi , \mathcal { M } , S _ { 0 } = s , A _ { 0 } = a \right] } =  { \mathbb { E } _ { s ^ { \prime } \sim  { \mathbb { P } } ( \cdot | s , a ) } } \left[ r ( s , a ) + \gamma Q ^ { \pi } ( s ^ { \prime } , \pi ) \right] , } \end{array}\tag{4}
$$

where $Q ( s , \pi ) : = \mathbb { E } _ { a \sim \pi } Q ( s , a )$ . In addition, the advantage function is $A ^ { \pi } ( s , a ) { \mathrel { \mathop : } } = Q ^ { \pi } ( s , a ) - V ^ { \pi } ( s )$

## 3.2 VALUE-BASED RL AND DUELING DQN

Value-based algorithms especially the Q-learning family (Watkins & Dayan, 1992; Mnih et al., 2013; Van Hasselt et al., 2016; Bellemare et al., 2017) have achieved remarkable successes. A canonical framework of the Q-learning family iterates between policy evaluation and policy improvement:

$$
\mathrm { p o l i c y ~ e v a l u a t i o n ~ ( P E ) } \colon Q _ { k } = \mathrm { a r g } \operatorname* { m i n } _ { Q } \mathbb { E } _ { \mathcal { D } } [ Q _ { k - 1 } ( s , a ) - ( r + \gamma Q _ { k - 1 } ( s ^ { \prime } , \pi _ { k - 1 } ) ) ] ^ { 2 }\tag{5}
$$

policy improvement (PI):

$$
\pi _ { k } = \arg \operatorname* { m a x } _ { \pi } Q _ { k } { \big ( } s , \pi ( s ) { \big ) }\tag{6}
$$

where D is an arbitrary dataset, the PE step estimates the previous policy $\pi _ { k - 1 }$ using the Bellman equation (Bellman, 1966), and the PI step finds an improved $\pi _ { k }$ by maximizing $Q _ { k }$ estimates.

In particular, we build our framework on top of Dueling DQN (Wang et al., 2016, DDQN). In a nutshell, DDQN approximates $V ( s )$ and $A ( s , a )$ with separate heads, and run improvement and evaluation steps with $Q ( s , a ) = \dot { V } ( s ) + A ( \dot { s } , a )$ This bifurcation enables a robust estimation of $V ( s )$ without conflating with the actions, which subsequently ensures a stable learning of $A ( s , a )$ given that it focuses solely on the relative values. As a consequence, DDQN often exhibits enhanced stability in training dynamics and improved generalization. In addition to the prior mentioned advantages, DDQN enables us to leverage a task structure that ground truth programs should attain highest advantages, therefore reducing the searching space, which we will elaborate on in Section 4.1.

Remarks on sample efficiency. We illustrate the inefficiency of policy-based methods using vanilla PG as an example. PG maximizes $\begin{array} { r } { J ( \mu ) : = \mathbb { E } [ \sum _ { t } \gamma ^ { t } r _ { t } | \pi _ { \mu } , \mathbf { \dot { \mathcal { M } } } ] \stackrel { \cdot } { \equiv } \mathbb { E } _ { W \sim \pi _ { \mu } } [ \sum _ { t } \gamma ^ { t } r _ { t } ] } \end{array}$ , with gradient $\nabla _ { \mu } J ( \mu )$ computed using the policy gradient theorem. This method requires training data W drawn from the distribution induced by current policy $\pi _ { \mu } ,$ , hence called on-policy. Therefore, one should in principle generate new data and discard historical data at every update, leading to undesired sample inefficiency. In contrast, policy evaluation as in equation 5 works with arbitrary dataset D.

## 4 ALGORITHMIC DESIGNS - ACCELERATING VALUE-BASED TRAINING

While value-based RL holds great promise, its training can be challenging due to the large action space $\mathbf { \nabla } A = \nu$ and the highdimensional state space $\bar { \mathcal { S } } = \mathcal { V } ^ { T }$ . This leads to a notably large Q-table of size $\mathcal { O } ( | \dot { \mathcal { V } } | ^ { T } )$ . And the cardinality of policy space is $\lvert \mathcal { A } \rvert ^ { \lvert s \rvert } = \mathcal { O } ( \lvert \mathcal { V } \rvert ^ { \lvert \mathcal { V } \rvert ^ { T } } )$ , which grows doubly exponentially. Both challenges from large action spaces and high-dimensional state spaces are pivotal research topics in RL. The action space challenges are discussed by e.g. Dulac-Arnold et al. (2015); Tavakoli et al. (2018); Kalashnikov et al. (2018), while He et al. (2016); Nair et al. (2018), among others, considered the state spaces complexities. In particular, Silver (2015); Duan et al. (2016) commented on that the potentially better training stability of policy-based methods in these scenarios.

![](images/58d5426dc888863accfcea0bfd194d322654b3fe495809232fcf34c5f0ab21e1.jpg)  
Figure 1: Training curves on APPS train set. ■ denotes B-Coder, ⋆ removes our conservative operator, and ▼ is B-Coder without both our operator and initialization.

To address the challenges inherent in training value-based RL for LMs, at a high level, we developed B-Coder considering three key aspects: incorporation of task structure, initialization of Q-function, and backup using a conservative Bellman operator. Figure 1 previews the effectiveness of our algorithmic designs, which shows the training curve of different value-based RL algorithms on the APPS dataset. Due to aforementioned challenges, the performance of the vanilla DDQN continuously decreases even evaluated on the training set. In contrast, both the Q-function initialization and the conservative Bellman operator show benefits in stabilizing and accelerating the training process.

For notational convenience in subsequent sections, we begin with an overview of our notations and parameterizations, summarized in Figure 2. Figure $2 ( \mathrm { a } )$ denotes a pre-trained encoder-decoder LM parameterized by $\theta _ { \mathrm { c k p t } }$ (where subscript ckpt denotes the fact it’s a checkpoint/constant). Figure 2(b) and (c) show the forward graphs of our two different training stages: (b) corresponds to a pre-training stage for $\phi ,$ to provide a good initialization for (c) the subsequent fine-tuning of θ. Motivations and details are deferred to Section 4.2 and 4.3, respectively. As we proceed to the rationale behind our designs, it is encouraged to maintain familiarity with $\theta _ { \mathrm { c k p t } } , \phi , \theta$ and their corresponding products, especially the forward paths to $Q _ { \phi }$ and $Q _ { \theta }$ , to prevent confusion in the subsequent sections.

## 4.1 LEVERAGING TASK STRUCTURES

As noted earlier, a key attribute of program synthesis task is the provision of human solutions, which are guaranteed to be correct. As a result, these solutions should attain the highest Q-values, even if the correct solutions might not be unique. As such, for a ground truth program $W ^ { * } = ( s _ { 0 } ^ { * } , a _ { 0 } ^ { * }$ $\dots , s _ { T } ^ { * } , a _ { T } ^ { * } ) , Q ( s _ { t } ^ { * } , a _ { t } ^ { * } ) \ge Q ( s _ { t } ^ { * } , a )$ holds for all $a \in \nu$ , hence $A ( s _ { t } ^ { * } , a _ { t } ^ { * } ) \geq A ( s _ { t } ^ { * } , a )$

![](images/0b76623e1d78cbd34161d3f433aaaf8a8ed92f1e153391bf08e6a0a509a5b71a.jpg)

To enforce this structure, one could ensure $A ( W ) \leq 0$ and $A ( W ^ { * } ) \approx 0$ , where we abuse the notation and by letting $A ( W ) { : = }$ $\textstyle \sum _ { t = 0 } ^ { T } A ( s _ { t } , a _ { t } )$ . It ensures that $W ^ { * }$ has advantages that are roughly the highest. To this end, suppose $g ( \cdot )$ is a general neural network, we decompose $Q$ as follows,

Figure 2: (a) A forward graph of conventional enc-dec LMs, with a checkpoint $\theta _ { \mathrm { c k p t } } ,$ , where $p$ is a distribution over A and ℓ denotes logits ; (b) Our forward graph for pre-training $\phi ; ( \mathrm { c } )$ Our forward graph for fine-tuning θ. indicates a frozen/constant component.

$$
Q ( s , a ) = \underbrace { g ( s , a ) - \operatorname* { m a x } _ { a } g ( s , a ) } _ { \mathrm { n o n - p o s i t i v e ~ a d v a n t a g e } } + V ( s ) = A ( s , a ) + V ( s ) .\tag{7}
$$

It enforces our first condition that $A ( W ) \leq 0$ . For the second condition $A ( W ^ { * } ) \approx 0$ , we optimize an advantage function A by minimizing an auxiliary advantage loss function, namely ${ \mathcal { L } } _ { \mathrm { a d v } }$

$$
\begin{array} { r } { \mathcal { L } _ { \mathrm { a d v } } ( A ) = \mathbb { E } _ { ( s _ { 0 } ^ { * } , a _ { 0 } ^ { * } , \ldots , s _ { T } ^ { * } , a _ { T } ^ { * } ) \sim \mathcal { D } _ { \mathrm { t r a i n } } } \left[ \sum _ { t = 0 } ^ { T } \lvert A ( s _ { t } ^ { * } , a _ { t } ^ { * } ) \rvert \right] . } \end{array}\tag{8}
$$

We also cap the Q-function with $R _ { \mathrm { m a x } } = 1$ , the maximum total rewards. See Appendix G for details.

## 4.2 Q-FUNCTION INITIALIZATION

Despite the task structures introduced, training the Q-function from scratch remains extremely challenging. While this is not a problem for policy-based learning (given that directly fine-tune pretrained LMs without requiring a Q-function at all), it presents significant challenges in value-based approaches because one often does not have a pre-trained Q-function. To this end, we show that one could initialize a Q-function from the logits output $\ell ( \cdot , \cdot )$ of a pre-trained LM.

Initialization of $Q$ via pre-trained models. Yu & Zhang (2023) considered the fine-tuning of RL agents after offline RL pre-training. Their main idea is to reconstruct a Q-function from the pre-trained policy, for fine-tuning. Drawing inspiration from their approach, one could similarly reconstruct/initialize a Q-function using a pre-trained LM, akin to using a pre-trained policy.

This initialization was motivated by the energy-based policy line of works (Haarnoja et al., 2017;   
2018), where a policy π is the product of passing a Q-function through a softmax transfer function.   
Analogously, in LMs, p - the distribution over $\nu _ { \textrm { - i s } }$ produced by passing logits ℓ through softmax.

$$
\begin{array} { r } { \operatorname { l a n g u a g e \ m o d e l i n g : } \quad p ( a | s ) = \exp { ( \ell ( s , a ) ) } \big / \sum _ { a \in \mathcal { A } } \exp { ( \ell ( s , a ) ) } } \end{array}\tag{9}
$$

$$
\begin{array} { r } { \mathrm { e n e r g y – b a s e d } \pi \mathrm { : \quad } \pi ( a | s ) = \exp \big ( \frac { 1 } { \alpha } Q ( s , a ) \big ) \big / \sum _ { a \in A } \exp \big ( \frac { 1 } { \alpha } Q ( s , a ) \big ) , } \end{array}\tag{10}
$$

where α is a temperature hyper-parameter. One could naturally set $Q ( s , a ) = \alpha \ell ( s , a )$ for initialization. Hence, with aforementioned dueling structure in equation 7 and our pre-defined parameterization, one could set the advantage function as $A _ { \theta _ { \mathrm { c k p t } } } ( s , \dot { a } ) : = \alpha [ \ell _ { \theta _ { \mathrm { c k p t } } } ( s , a ) \dot { - } \operatorname* { m a x } _ { a } \ell _ { \theta _ { \mathrm { c k p t } } } ( s , a ) ]$ leading to $\begin{array} { r } { Q _ { \phi } ( s , a ) : = A _ { \theta _ { \mathrm { c k n t } } } ( s , a ) + V _ { \phi } ( s ) } \end{array}$ . See also our forward pass graph defined in Figure 2b. In a nutshell, this $Q _ { \phi } .$ -function produces a policy $\pi _ { \phi }$ identical to the output distribution $p _ { \theta _ { \mathrm { c k p t } } } \ \mathrm { o f \ L M } _ { \theta _ { \mathrm { c k p t } } } .$

$$
\pi _ { \phi } ( a | s ) = \mathrm { s o f t m a x } [ \frac { 1 } { \alpha } \mathbf { Q } _ { \phi } ( s ) ] [ a ] = \mathrm { s o f t m a x } [ \ell _ { \theta _ { \mathrm { c k p t } } } ( s ) - \operatorname* { m a x } _ { a } \ell _ { \theta _ { \mathrm { c k p t } } } ( s , a ) + \frac { 1 } { \alpha } V _ { \phi } ( s ) ] [ a ] = p _ { \theta _ { \mathrm { c k p t } } } ( a | s ) ,\tag{11}
$$

where $\mathbf { Q } ( s ) : = [ Q ( s , a ) ] _ { a \in \mathcal { A } }$ and $\ell ( s ) : = [ \ell ( s , a ) ] _ { a \in \mathcal { A } }$

Recalling equation $5 - 6 ,$ the Q-learning family can be viewed as iterations between policy evaluation and improvement. We now elaborate on how this $Q _ { \phi }$ function initialization affects both steps.

Policy improvement. One could, informally, consider the operation of taking softmax with respect to ${ \scriptstyle { \frac { 1 } { \alpha } } } { \dot { Q } } _ { \phi }$ as a soft policy improvement (Haarnoja et al., 2018) step with a temperature $\alpha .$ . Therefore, equation 11 can be interpreted as: running soft policy improvement alone with this initialized $Q _ { \phi }$ preserved the performance of pre-trained $\mathbf { \Omega } ^ { \mathrm { L M } } \theta _ { \mathrm { c k p t } } ;$ , offering a good starting point of online fine-tuning.

Policy evaluation. Yet, this $Q _ { \phi }$ function only captures relative values, since we initialized only the advantages $A _ { \theta _ { \mathrm { c k p t } } }$ - the relative information - as shown in equation 11. $V _ { \phi }$ can thereby be an arbitrary function. This would not affect the policy improvement step due to the translation invariance of the softmax function. However, during the policy evaluation step, see e.g. equation 5, the Bellman error can be heavily influenced by the $\breve { V }$ -values. When the V -values is the dominant source of error, the policy evaluation optimization could be largely driven by the state-only V -values. This can lead to a loss of the relative action values, that we intended to preserve in the previous step.

Pre-training of $V _ { \phi }$ . This can be addressed by adding a pre-training phase of $V _ { \phi } ( s )$ , during which we freeze the advantage function $A _ { \theta _ { \mathrm { c k p t } } }$ and train $V _ { \phi }$ by minimizing the temporal difference error (or equivalently doing policy evaluation). In this stage, we optimize the following loss until convergence

$$
\begin{array} { r } { \mathcal { L } _ { V } ( V _ { \phi } ; \ell _ { \theta _ { \mathrm { c h p } } } ) = \frac { 1 } { T } \mathbb { E } _ { ( s _ { t } , a _ { t } , r _ { t } , s _ { t + 1 } ) \sim \mathcal { D } _ { \mathrm { u a l } } } \sum _ { t = 0 } ^ { T } \left[ r _ { t } + \gamma \operatorname { s G } \left( Q _ { \phi } ( s _ { t + 1 } , \hat { a } _ { t + 1 } ) \right) - Q _ { \phi } ( s _ { t } , a _ { t } ) \right] ^ { 2 } , } \end{array}\tag{12}
$$

where SG is a stop gradient operator, $\mathrm { S G } \big ( Q _ { \phi } \big ( s ^ { \prime } , \hat { a } ^ { \prime } \big ) \big )$ follows standard semi-gradient optimization, $\hat { a } _ { t + 1 }$ is a target action (details deferred to section 4.3), and $Q _ { \phi } ( s , a ) = A _ { \theta _ { \mathrm { c k p t } } } ( s , a ) + V _ { \phi } ( s )$

In summary, our initialization steps ensures that, prior to fine-tuning $\theta ,$ our $Q _ { \phi }$ meets two important conditions: it starts with the action distribution $p _ { \theta _ { \mathrm { c k p t } } }$ of a pre-trained $\mathrm { L M } _ { \theta _ { \mathrm { c k p t } } }$ , and it begins with low temporal difference error (because the pre-training of $V _ { \phi }$ in equation 12 directly minimizes it).

## 4.3 A CONSERVATIVE BELLMAN OPERATOR

With a pre-trained state value function $V _ { \phi }$ , we are now ready to learn a good state-action value function via fine-tuning. We parameterize $\begin{array} { r } { Q _ { \theta } ( s , a ) : = A _ { \theta } ( s , a ) + V _ { \theta } ( s ) = \bar { \alpha } [ \ell _ { \theta } ( s , a ) - \operatorname* { m a x } _ { a } \ell _ { \theta } ( s , a ) ] + } \end{array}$ $V _ { \theta } ^ { r } + V _ { \phi }$ , where we define $V _ { \theta } = V _ { \theta } ^ { r } + \dot { V } _ { \phi }$ , and we initialize θ in a way such that $\ell _ { \theta } = \ell _ { \theta _ { \mathrm { c k p t } } }$ and $V _ { \theta } ^ { r } = 0$ It ensures that $Q _ { \theta } = Q _ { \phi }$ on initialization, a good starting point for subsequent fine-tuning on θ. Technically speaking, setting $V _ { \theta } = V _ { \theta } ^ { r } + V _ { \phi }$ is not required, as one could finetune both θ and $\phi .$ We however observed that finetuning a residual head $V _ { \theta } ^ { r }$ , with ϕ frozen, leads to better stability.

Although we avoid training $Q _ { \theta }$ from scratch, optimizing $Q _ { \theta }$ by Q-learning family algorithms can still be challenging. We attribute this to the characteristics of the Bellman optimality operator $B ^ { * }$ that seeks to learn the optimal value function $Q ^ { * }$ and optimal policy $\pi ^ { * }$ , which requires a good data coverage of the state-action space $\mathcal { S } \times \mathcal { A }$ (e.g. Jiang & Huang, 2020; Xie et al., 2021a; Zhan et al., 2022). In program synthesis, however, such assumption can hardly be met due to the large state-action space and the high computational costs of Transformer inference. While conventional Q-learning family relies on the operator $B ^ { * }$ , recent works in RL, especially those considering limited data regime (e.g. Agarwal et al., 2020; Levine et al., 2020), often design “conservative” operators (e.g. Achiam et al., 2017; Kumar et al., 2020; Brandfonbrener et al., 2021) to address difficulties led by $B ^ { * }$

Conservative Bellman operators. The concept behind conservative Bellman operators is to “aim low”. Instead of learning the optimal $Q ^ { * }$ and $\pi ^ { * }$ , these operators typically seeks to learn a policy π that either surpasses a behavior policy (which is used to collect a RL dataset in offline RL literature, see e.g. Achiam et al., 2017; Brandfonbrener et al., 2021) or fine-tune a pre-existing policy (e.g. Xie et al., 2021b; Yu & Zhang, 2023). This is often achieved by introducing a regularizer that penalizes deviations from the behavior/pre-existing policy. In particular, as shown in equation 14, we define our conservative Bellman operator $B ^ { q }$ , which depends on a fixed, pre-defined policy q, as follows:

optimality B: $( \mathcal { B } ^ { * } Q ) ( s , a ) = r ( s , a ) + \gamma \mathbb { E } _ { s ^ { \prime } } [ Q ( s ^ { \prime } , \hat { a } ^ { \prime } ) ]$ , where $\hat { a } ^ { \prime } = \arg \operatorname* { m a x } _ { a } Q ( s ^ { \prime } , a )$

(13)

conservative B: $( \mathcal { B } ^ { q } Q ) ( s , a ) = r ( s , a ) + \gamma \mathbb { E } _ { s ^ { \prime } } [ Q ( s ^ { \prime } , \hat { a } ^ { \prime } ) ]$ , where $\hat { a } ^ { \prime } = \arg \operatorname* { m a x } _ { a } q ( a | s ^ { \prime } )$

(14)

The intuition behind our operator $B ^ { q }$ is that we evaluate the action-value function $Q ^ { q ^ { \uparrow } }$ of a greedified policy $\begin{array} { r } { q ^ { \uparrow } ( a | s ) : = \mathbb { 1 } \{ \bar { a } = \arg \operatorname* { m a x } _ { a } q ( a | s ) \} } \end{array}$ , where 1 is the indicator function. The rationale behind greedification is that $q ^ { \uparrow }$ can be seen as q in a greedy-decoding mode, which usually has better (one-shot) capability than sampling mode (although the latter has better generation diversity). Considering setting $q = p _ { \theta _ { \mathrm { c k p t } } }$ , the operator $B ^ { p _ { \theta _ { \mathrm { c k p t } } } }$ seeks to learn a policy π that outperforms $p _ { \theta _ { \mathrm { c k p t } } } .$

We further comment on some properties of $B ^ { q } { } _ { i }$ : proposition 4.1 shows $B ^ { q }$ is a contraction, meaning there is an unique fixed point. It leads to proposition 4.2, motivating our development of Section 4.5. Proposition 4.1. Bq is γ-contraction in $\ell _ { \infty }$ norm.

Given our conservative Bellman operator, we could define our conservative temporal difference loss,

$$
\begin{array} { r } { \mathcal { L } _ { Q } ( Q _ { \theta } ; q ) = \frac { 1 } { T } \mathbb { E } _ { ( s _ { t } , a _ { t } , r _ { t } , s _ { t + 1 } ) \sim \mathcal { D } _ { \operatorname { t r i n } } } \sum _ { t = 0 } ^ { T } \left[ r _ { t } + \gamma \operatorname { s G } \left( Q _ { \theta } ( s _ { t + 1 } , \hat { a } _ { t + 1 } ) \right) - Q _ { \theta } ( s _ { t } , a _ { t } ) \right] ^ { 2 } , } \end{array}\tag{15}
$$

$$
\begin{array} { r } { \widehat { a } _ { t + 1 } = \arg \operatorname* { m a x } _ { a } { q ( a | s _ { t + 1 } ) } , \mathrm { a n d } Q _ { \theta } ( s , a ) = \alpha \left[ \ell _ { \theta } ( s , a ) - \operatorname* { m a x } _ { a } \ell _ { \theta } ( s , a ) \right] + V _ { \theta } ^ { r } ( s ) + V _ { \phi } ( s ) . } \end{array}
$$

## 4.4 IMPLEMENTATION AND OPTIMIZATION

Architecture and parameterization recap. Following (Le et al., 2022; Shojaee et al., 2023; Liu et al., 2023), we choose T5 (Raffel et al., 2020) as our base architecture for $\theta _ { \mathrm { c k p t } } ,$ ϕ and $\theta ;$ and $\theta _ { \mathrm { c k p t } }$ is initialized with CodeRL checkpoint which is publicly available. Specifically, $\theta _ { \mathrm { c k p t } } ,$ ϕ and θ share a same encoder, and the encoder is frozen throughout, to reduce the amount of learnable parameters.

Two-stage training. As noted earlier, our training are composed with two stages: a pre-training stage of $\phi ,$ namely ϕ-stage, and a fine-tuning stage of $\theta ,$ namely θ-stage. A pseudo-algorithm could be found in Appendix A. In addition, further implementation details are deferred to Appendix H.

ϕ-stage: Given our development of Section 4.2, we pre-train $V _ { \phi }$ function using stochastic gradient descent with $\nabla _ { \phi } \mathcal { L } _ { V } ( V _ { \phi } ; \ell _ { \theta _ { \mathrm { c k p t } } } ^ { * } )$ , with ${ \mathcal { L } } _ { V }$ defined in equation 12.

θ-stage (fine-tuning): In this stage, we seek to optimize $Q _ { \theta }$ to minimize our previously developed losses: ${ \mathcal { L } } _ { \mathrm { a d v } }$ and $\mathcal { L } _ { Q }$ , as defined in equation 8 and 15, respectively. In addition, it is also a common practice to include a cross-entropy loss $\mathcal { L } _ { \mathrm { c e } }$ during fine-tuning. Therefore, we conclude our final loss function as equation 17, and θ is updated using stochastic gradient descent with $\nabla _ { \theta } \mathcal { L } _ { \mathrm { f t } } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c k p t } } } )$

$$
\mathrm { R e c a l l : } Q _ { \theta } ( s , a ) = A _ { \theta } ( s , a ) + V _ { \theta } ( s ) = \alpha \left( \ell _ { \theta } ( s , a ) - \operatorname* { m a x } _ { a } \ell _ { \theta } ( s , a ) \right) + V _ { \theta } ^ { r } ( s ) + V _ { \phi } ( s )\tag{16}
$$

$$
\begin{array} { r } { \mathcal { L } _ { \mathrm { f i } } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c h p t } } } ) = \mathcal { L } _ { Q } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c h p t } } } ) + \beta _ { \mathrm { a d v } } \mathcal { L } _ { \mathrm { a d v } } ( A _ { \theta } ) + \beta _ { \mathrm { c e } } \mathcal { L } _ { \mathrm { c e } } ( \pi _ { \theta } ) , \ \mathrm { w h e r e } \ \pi _ { \theta } = \mathrm { s o f t m a x } \left( \frac { 1 } { \alpha } Q _ { \theta } \right) } \end{array}\tag{17}
$$

## 4.5 A FREE REWARD MODEL

Reward modeling is crucial in language modeling and also in inverse RL (detailed discussions could be found in Appendix C). An intriguing finding from IRL, applicable to our framework, is that a trained Q-function can recover a reward function without additional training. Analogously to Garg et al. (2021), an one-to-one correspondence between $Q$ and reward holds with our conservative Bellman operator Bq. We define the inverse conservative Bellman operator $\mathcal { T } ^ { q } : \mathbb { R } ^ { S \times \mathcal { A } }  \mathbb { R } ^ { S \times \mathcal { A } }$ ,

$$
\begin{array} { r } { ( \mathcal { T } ^ { q } Q ) ( s , a ) = Q ( s , a ) - \gamma \mathbb { E } _ { s ^ { \prime } } Q \left( s ^ { \prime } , \mathrm { a r g m a x } _ { a } q ( a | s ^ { \prime } ) \right) . } \end{array}\tag{18}
$$

Proposition 4.2. The inverse conservative Bellman operator $\mathcal { T } ^ { q }$ is a bijection.

Proposition 4.2 shows that a $Q _ { \theta }$ is uniquely corresponding to a reward function $\tilde { r } _ { \theta } : = \mathcal { T } ^ { q } Q _ { \theta } . ^ { 1 }$ Given the definition of $\mathcal { T } ^ { q }$ we could recover a reward model $\tilde { r } _ { \theta }$ with $Q _ { \theta }$ without additional training:

$$
\begin{array} { r } { \tilde { r } _ { \theta } ( s , a ) = Q _ { \theta } ( s , a ) - \gamma \mathbb { E } _ { s ^ { \prime } } Q _ { \theta } \left( s ^ { \prime } , \mathrm { a r g } \operatorname* { m a x } _ { a } p \theta _ { \mathrm { c k p t } } ( a | s ^ { \prime } ) \right) \approx Q _ { \theta } ( s , a ) - \gamma V _ { \theta } ( s ^ { \prime } ) . } \end{array}\tag{19}
$$

We use the estimation $\begin{array} { r } { \widetilde { r } _ { \theta } ( s , a ) \approx Q _ { \theta } ( s , a ) - \gamma V _ { \theta } ( s ^ { \prime } ) } \end{array}$ in practice, with reasons deferred to Appendix F.

Candidates selection with $\tilde { r } _ { \theta }$ . We leverage our reward model $\tilde { r } _ { \theta }$ to do candidate programs selection, as an example to highlight the additional benefits of value-based RL. We rank generated programs by the cumulative rewards $\begin{array} { r } { \tilde { R } _ { \theta } ( W ) : = \sum _ { t = 0 } ^ { T } \tilde { r } _ { \theta } ( s _ { t } , a _ { t } ) } \end{array}$ , predicted by our reward model ${ \tilde { r } } _ { \theta } .$ , to select the programs that are most likely to be correct. Specifically, for pass@k metrics, we follow the evaluation protocol used in CodeT (Chen et al., 2022), a work that considered program selection via automatic generated tests. This protocol computes pass@k by first generating m programs and select a subset of k programs to evaluate pass@k. In our case, we select the k-sized subset with top-k highest $\tilde { R } _ { \theta } ( \cdot )$ from total m candidates. Our results in Section 5 follow this evaluation protocol.

Table 1: Empirical evaluation on APPS test set. †, ‡ and ‡‡ indicates results duplicated from Le et al. (2022), Shojaee et al. (2023) and Liu et al. (2023), respectively. Bold number indicates the best result and underlined number means our result are the second best. Intro, inter and comp stand for introductory, interview and competition, respectively.
<table><tr><td rowspan="2">Model</td><td rowspan="2"># trainable parameters</td><td colspan="4">Pass@1</td><td colspan="4">Pass@5</td><td colspan="4">Pass@1000</td></tr><tr><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td></tr><tr><td>Codex†</td><td>12B</td><td>4.14</td><td>0.14</td><td>0.02</td><td>0.92</td><td>9.65</td><td>0.51</td><td>0.09</td><td>2.25</td><td>25.02</td><td>3.70</td><td>3.23</td><td>7.87</td></tr><tr><td>AlphaCode†</td><td>1B</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>17.67</td><td>5.24</td><td>7.06</td><td>8.09</td></tr><tr><td> PT3</td><td>175B</td><td>0.20</td><td>0.03</td><td>0.00</td><td>0.06</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>GPT2†</td><td>0.1B</td><td>1.00</td><td>0.33</td><td>0.00</td><td>0.40</td><td>2.70</td><td>0.73</td><td>0.00</td><td>1.02</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>GPT2†</td><td>1.5B</td><td>1.30</td><td>0.70</td><td>0.00</td><td>0.68</td><td>3.60</td><td>1.03</td><td>0.00</td><td>1.34</td><td>25.00</td><td>9.27</td><td>8.80</td><td>12.32</td></tr><tr><td>GPT-Neo†</td><td>2.7B</td><td>3.90</td><td>0.57</td><td>0.00</td><td>1.12</td><td>5.50</td><td>0.80</td><td>0.00</td><td>1.58</td><td>27.90</td><td>9.83</td><td>11.40</td><td>13.76</td></tr><tr><td>GPT-J†</td><td>6B</td><td>5.60</td><td>1.00</td><td>0.50</td><td>1.82</td><td>9.20</td><td>1.73</td><td>1.00</td><td>3.08</td><td>35.20</td><td>13.15</td><td>13.51</td><td>17.63</td></tr><tr><td colspan="10">RL based methods - without using example unit tests</td><td colspan="3"></td></tr><tr><td>CodeRL†</td><td>770M</td><td>6.20</td><td>1.50</td><td>0.30</td><td>2.20</td><td>9.39</td><td>1.90</td><td>0.42</td><td>3.10</td><td>35.30</td><td>13.33</td><td>13.60</td><td>17.78</td></tr><tr><td>PPOCoder</td><td>770M</td><td>5.20</td><td>1.00</td><td>0.50</td><td>1.74</td><td>9.10</td><td>2.50</td><td>1.20</td><td>3.56</td><td>35.20</td><td>13.35</td><td>13.90</td><td>17.77</td></tr><tr><td>RLTF‡‡</td><td>770M</td><td>4.16</td><td>0.97</td><td>0.20</td><td>1.45</td><td>10.12</td><td>2.65</td><td>0.82</td><td>3.78</td><td>38.30</td><td>15.13</td><td>15.90</td><td>19.92</td></tr><tr><td>B-Coder</td><td> $\leq 7 7 0 \mathrm { M / s t a g e } ^ { 3 }$ </td><td>6.70</td><td>1.50</td><td>0.30</td><td>2.30</td><td>10.40</td><td>2.63</td><td>0.70</td><td>3.80</td><td>37.00</td><td>13.67</td><td>12.60</td><td>18.12</td></tr></table>

Remarks on ${ \tilde { r } } _ { \theta } .$ To further explain the motivation of ranking with $\tilde { r } _ { \theta }$ , consider a realistic deployment setting where a fine-tuned model is deployed for end-user applications. Users often provide a language description of their needs but may not include test cases (which can also be challenging for beginners or casual users). Additionally, the model is usually required to offer a single best response instead of a range of options. Therefore, the ability to rank programs without true rewards is a desirable advantage.

To preview the effectiveness of ${ \mathit { \tilde { r } } } _ { \theta } ,$ we show the correlation between environmental reward r and our cumulative reward $\ddot { R } _ { \theta }$ . In Figure 3, green region corresponds to correct programs, and has the highest $\tilde { R } _ { \theta }$ on average. For incorrect programs, those with compile and runtime errors have the lowest and the second lowest $\tilde { R } _ { \theta }$ , respectively. Programs can be executed but fail some tests, have the second highest $\tilde { R } _ { \theta }$ . Hence, it concludes that $\tilde { R } _ { \theta }$ has an evident pos

![](images/eea08bb653ef30c08ca00146a7fe50524541892700a39b4164bcc9469f1eb8e3.jpg)  
Figure 3: Kernel density estimation of $\tilde { R } _ { \theta } ( \cdot )$ evaluated on a collection of generated programs. The x-axis represents the predicted reward given by $\tilde { R } _ { \theta }$ and the y-axis is its density. Color codes the true outcomes defined in equation 2.

## 5 EMPIRICAL EVALUATION

Sampling using $Q _ { \theta }$ . Nucleus sampling (top-p sampling) (Holtzman et al., 2019) with sampling temperature2 (Ackley et al., 1985) has been one of the most important sampling techniques. It can also be easily implemented in our framework. One could simply consider $\mathbf { \bar { \boldsymbol { Q } } } _ { \theta } \mathbf { \bar { \boldsymbol { / } } } \alpha$ as logits and the sampling procedure would remain identical to standard LMs, see Appendix B for details.

APPS benchmark and baselines. In line with prior RL-based works (Le et al., 2022; Shojaee et al., 2023; Liu et al., 2023), we evaluate B-Coder on the challenging code contests benchmark APPS (Hendrycks et al., 2021). It contains 5,000 training and 5,000 testing problems, with three difficulty levels: introductory, interview and competition. We compare our B-Coder with pre-trained or supervise fine-tuned LLM baselines: GPT2 (Radford et al., 2019), GPT3 (Brown et al., 2020), GPT-Neo (Black et al., 2021), GPT-J (Wang & Komatsuzaki, 2021), Codex (Chen et al., 2021a) and AlphaCode (Li et al., 2022); and RL fine-tuned baselines: CodeRL (Le et al., 2022), PPOCoder (Shojaee et al., 2023) and a concurrent work RLTF (Liu et al., 2023).

APPS: without example test outcomes. In the APPS dataset, each problem has several example unit tests (different from the hidden unit tests used for evaluation). These example tests are usually leveraged to refine generated samples. For example, CodeRL and RLTF considers a critic sampling (CS) strategy that refines and repairs generated programs based on the execution outcomes of the example tests. We start with experiments results in which example test outcomes are not used (hence CodeRL and RLTF results in Table 1 are without CS). Table 1 shows that our B-Coder has overall the best pass@k for $k = \{ 1 , 5 \}$ } and achieves second best place for $k = 1 0 0 0$ (best result reported by the concurrent work RLTF). For Table 1 results, we use nucleus sampling with a sampling temperature of 0.6. We set m to 256 for $k = \{ 1 , 5 \}$ and m to 2500 for $k = 1 0 0 0$ , where m is a hyper-parameter of our ranking protocol introduced in Section 4.5 (see Appendix I for an ablation study on m).

APPS: using example test outcomes. Table 2 lists the results using example tests. In addition to the CS strategy that uses example tests to refine/repair programs, Li et al. (2022) and Chen et al. (2021a) consider a filtered setting, in which programs failing example tests are excluded, and the pass@k is evaluated us-

Table 2: APPS results when using example test outcomes.
<table><tr><td rowspan="2">Model</td><td colspan="4">Pass@1</td><td colspan="4">Pass@5</td></tr><tr><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td></tr><tr><td>Codex† filtered</td><td>22.78</td><td>2.64</td><td>3.04</td><td>6.75</td><td>24.52</td><td>3.23</td><td>3.08</td><td>7.46</td></tr><tr><td>AlphaCode† filtered</td><td>-</td><td>-</td><td>-</td><td>-</td><td>14.36</td><td>5.63</td><td>4.58</td><td>7.17</td></tr><tr><td>CodeRL† cs</td><td>6.77</td><td>1.80</td><td>0.69</td><td>2.57</td><td>15.27</td><td>4.48</td><td>2.36</td><td>6.21</td></tr><tr><td>CodeRL† filtered</td><td>16.27</td><td>6.00</td><td>4.27</td><td>7.71</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>CodeRL† cs+filtered</td><td>16.52</td><td>6.16</td><td>4.15</td><td>7.83</td><td>24.49</td><td>8.58</td><td>7.82</td><td>11.61</td></tr><tr><td>RLTF‡‡ cs</td><td>8.40</td><td>2.28</td><td>1.10</td><td>3.27</td><td>18.60</td><td>5.57</td><td>3.70</td><td>7.80</td></tr><tr><td>B-Coder filtered</td><td>18.00</td><td>6.63</td><td>2.30</td><td>8.04</td><td>23.30</td><td>8.83</td><td>6.40</td><td>11.30</td></tr></table>

ing (a subset of) programs that pass example tests (which is also related to the k@m metric (Li et al., 2022), the pass rate using k submissions from m samples). We also test B-Coder in this filtered setting. Similarly, we first exclude programs that fail example tests. Suppose n out of m programs pass; we then follow our ranking protocol to get top-k out of n programs for evaluation. B-Coder outperforms baselines with either CS or filtered setting for $k = \{ 1 , 5 \}$ . The baseline, CodeRL+CS+filtered, incorporated both strategies achieved a slight advantage over B-Coder for pass@5 while being surpassed by B-Coder for pass@1. It worth mentioning that CS is a plug-and-play component, which could also be combined with B-Coder, to further improve pass rate. For the results in Table 2, we use a temperature of 0.4 and m set to 1000, matching the m used in Le et al. (2022).

Generalization ability. In addition, we test the generalization ability of our dual strategy, ranking with $\tilde { R } _ { \theta }$ . We study two aspects: generalization to other models and generalization to different domains. To this end, we designed the following experiments, which confirmed its generalizability in positive.

For the former, we generate (off-policy) programs using CodeRL (with $m = 2 5 6 )$ , and rank those programs by $\tilde { R } _ { \theta }$ . Table 3 shows our ranking strategy leads to improvements in most cases, even though the programs to be ranked are not generated by B-Coder.

Table 3: Generalization to CodeRL. Pass@k evaluated with top-k ranked programs, generated by CodeRL. · indicates absolute improvement achieved by ranking, compared to un-ranked pass@k.

For the latter, we test our dual strategy with another dataset MBPP (Austin et al., 2021) (with m = 512). Table 4 shows consistent improvements for all temperatures and k.

<table><tr><td rowspan="2">k</td><td rowspan="2">Temp.</td><td colspan="4">Pass@k</td></tr><tr><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td></tr><tr><td rowspan="2">1</td><td>0.4</td><td>6.30 1.91</td><td>1.27 0.37</td><td>0.50 0.37</td><td>2.12 0.68</td></tr><tr><td>0.6</td><td> $6 . 0 0 \ 2 . 1 3$ </td><td>1.23 0.42</td><td>0.50 0.36</td><td>2.04 0.75</td></tr><tr><td rowspan="2">5</td><td>0.4</td><td>9.30 -0.2</td><td>2.100.01</td><td>0.70 0.15</td><td>3.260.00</td></tr><tr><td>0.6</td><td>10.20 0.58</td><td>2.57 0.41</td><td>0.80 0.16</td><td>3.74 0.39</td></tr></table>

Table 4: Zero-shot pass@k on MBPP. · indicates absolute improvement achieved by ranking.
<table><tr><td>Temp.</td><td>k=1</td><td>k=5</td><td>k=10</td><td>k=80</td></tr><tr><td>0.7</td><td>20.13 6.61</td><td>37.04 5.61</td><td>44.45 4.63</td><td>64.00 1.41</td></tr><tr><td>0.8</td><td>18.89 6.99</td><td>36.59 7.21</td><td>44.46 6.59</td><td>65.20 4.28</td></tr><tr><td>0.9</td><td>17.32 7.34</td><td>35.04 8.58</td><td>43.15 8.22</td><td>63.20 4.33</td></tr></table>

## 6 CONCLUSION

In this work, we explore the feasibility of value-based RL algorithms for program synthesis task. We demonstrate how to stabilize and accelerate training through Q-function initialization and conservative updates. Moreover, our work is conducted with minimal reward engineering effort, thereby placing an emphasis on the perspective of algorithm designs. While policy-based algorithms remain mainstream in the current program synthesis literature, the question of how to effectively leverage off-policy programs, including historical synthetic samples, in a principled way, might still be under-explored. We are convinced that value-based RL offers a promising direction to address this question, and thereby to scale RL for code generation at large by (re)-using the extensive collection of off-policy programs. Our work could thus serve as an important initial step towards this direction.

## REFERENCES

Pieter Abbeel and Andrew Y Ng. Apprenticeship learning via inverse reinforcement learning. In Proceedings of the twenty-first international conference on Machine learning, pp. 1, 2004.

Joshua Achiam, David Held, Aviv Tamar, and Pieter Abbeel. Constrained policy optimization. In International conference on machine learning, pp. 22–31. PMLR, 2017.

David H Ackley, Geoffrey E Hinton, and Terrence J Sejnowski. A learning algorithm for boltzmann machines. Cognitive science, 9(1):147–169, 1985.

Rishabh Agarwal, Dale Schuurmans, and Mohammad Norouzi. An optimistic perspective on offline reinforcement learning. In International Conference on Machine Learning, pp. 104–114. PMLR, 2020.

Rohan Anil, Andrew M Dai, Orhan Firat, Melvin Johnson, Dmitry Lepikhin, Alexandre Passos, Siamak Shakeri, Emanuel Taropa, Paige Bailey, Zhifeng Chen, et al. Palm 2 technical report. arXiv preprint arXiv:2305.10403, 2023.

Kai Arulkumaran, Antoine Cully, and Julian Togelius. Alphastar: An evolutionary computation perspective. In Proceedings of the genetic and evolutionary computation conference companion, pp. 314–315, 2019.

Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, et al. Program synthesis with large language models. arXiv preprint arXiv:2108.07732, 2021.

Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, et al. Training a helpful and harmless assistant with reinforcement learning from human feedback. arXiv preprint arXiv:2204.05862, 2022a.

Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, et al. Constitutional ai: Harmlessness from ai feedback. arXiv preprint arXiv:2212.08073, 2022b.

Marc G Bellemare, Will Dabney, and Remi Munos. A distributional perspective on reinforcement´ learning. In International conference on machine learning, pp. 449–458. PMLR, 2017.

Richard Bellman. Dynamic programming. Science, 153(3731):34–37, 1966.

Samy Bengio, Oriol Vinyals, Navdeep Jaitly, and Noam Shazeer. Scheduled sampling for sequence prediction with recurrent neural networks. Advances in neural information processing systems, 28, 2015.

Sid Black, Leo Gao, Phil Wang, Connor Leahy, and Stella Biderman. GPT-Neo: Large Scale Autoregressive Language Modeling with Mesh-Tensorflow, March 2021. URL https://doi.org/ 10.5281/zenodo.5297715. If you use this software, please cite it using these metadata.

David Brandfonbrener, Will Whitney, Rajesh Ranganath, and Joan Bruna. Offline rl without offpolicy evaluation. Advances in neural information processing systems, 34:4933–4946, 2021.

Noam Brown and Tuomas Sandholm. Superhuman ai for heads-up no-limit poker: Libratus beats top professionals. Science, 359(6374):418–424, 2018.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

Bei Chen, Fengji Zhang, Anh Nguyen, Daoguang Zan, Zeqi Lin, Jian-Guang Lou, and Weizhu Chen. Codet: Code generation with generated tests. In The Eleventh International Conference on Learning Representations, 2022.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021a.

Xinyun Chen, Chang Liu, and Dawn Song. Execution-guided neural program synthesis. In International Conference on Learning Representations, 2018.

Xinyun Chen, Dawn Song, and Yuandong Tian. Latent execution for neural program synthesis beyond domain-specific languages. Advances in Neural Information Processing Systems, 34: 22196–22208, 2021b.

Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton, Sebastian Gehrmann, et al. Palm: Scaling language modeling with pathways. arXiv preprint arXiv:2204.02311, 2022.

Paul F Christiano, Jan Leike, Tom Brown, Miljan Martic, Shane Legg, and Dario Amodei. Deep reinforcement learning from human preferences. Advances in neural information processing systems, 30, 2017.

Thomas Degris, Martha White, and Richard S Sutton. Off-policy actor-critic. arXiv preprint arXiv:1205.4839, 2012.

Shizhe Diao, Rui Pan, Hanze Dong, Ka Shun Shum, Jipeng Zhang, Wei Xiong, and Tong Zhang. Lmflow: An extensible toolkit for finetuning and inference of large foundation models. arXiv preprint arXiv:2306.12420, 2023.

Yan Duan, Xi Chen, Rein Houthooft, John Schulman, and Pieter Abbeel. Benchmarking deep reinforcement learning for continuous control. In International conference on machine learning, pp. 1329–1338. PMLR, 2016.

Gabriel Dulac-Arnold, Richard Evans, Hado van Hasselt, Peter Sunehag, Timothy Lillicrap, Jonathan Hunt, Timothy Mann, Theophane Weber, Thomas Degris, and Ben Coppin. Deep reinforcement learning in large discrete action spaces. arXiv preprint arXiv:1512.07679, 2015.

Kevin Ellis, Maxwell Nye, Yewen Pu, Felix Sosa, Josh Tenenbaum, and Armando Solar-Lezama. Write, execute, assess: Program synthesis with a repl. Advances in Neural Information Processing Systems, 32, 2019.

Jonathan Frankle, Peter-Michael Osera, David Walker, and Steve Zdancewic. Example-directed synthesis: a type-theoretic interpretation. ACM Sigplan Notices, 51(1):802–815, 2016.

Daniel Fried, Armen Aghajanyan, Jessy Lin, Sida Wang, Eric Wallace, Freda Shi, Ruiqi Zhong, Scott Yih, Luke Zettlemoyer, and Mike Lewis. Incoder: A generative model for code infilling and synthesis. In The Eleventh International Conference on Learning Representations, 2022.

Scott Fujimoto, Herke Hoof, and David Meger. Addressing function approximation error in actorcritic methods. In International conference on machine learning, pp. 1587–1596. PMLR, 2018.

Divyansh Garg, Shuvam Chakraborty, Chris Cundy, Jiaming Song, and Stefano Ermon. Iq-learn: Inverse soft-q learning for imitation. Advances in Neural Information Processing Systems, 34: 4028–4039, 2021.

Shixiang Gu, Timothy Lillicrap, Zoubin Ghahramani, Richard E Turner, and Sergey Levine. Q-prop: Sample-efficient policy gradient with an off-policy critic. arXiv preprint arXiv:1611.02247, 2016.

Caglar Gulcehre, Tom Le Paine, Srivatsan Srinivasan, Ksenia Konyushkova, Lotte Weerts, Abhishek Sharma, Aditya Siddhant, Alex Ahern, Miaosen Wang, Chenjie Gu, et al. Reinforced self-training (rest) for language modeling. arXiv preprint arXiv:2308.08998, 2023.

Sumit Gulwani, William R Harris, and Rishabh Singh. Spreadsheet data manipulation using examples. Communications of the ACM, 55(8):97–105, 2012.

Tuomas Haarnoja, Haoran Tang, Pieter Abbeel, and Sergey Levine. Reinforcement learning with deep energy-based policies. In International conference on machine learning, pp. 1352–1361. PMLR, 2017.

Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, and Sergey Levine. Soft actor-critic: Off-policy maximum entropy deep reinforcement learning with a stochastic actor. In International conference on machine learning, pp. 1861–1870. PMLR, 2018.

Frank S He, Yang Liu, Alexander G Schwing, and Jian Peng. Learning to play in a day: Faster deep reinforcement learning by optimality tightening. In International Conference on Learning Representations, 2016.

Dan Hendrycks, Steven Basart, Saurav Kadavath, Mantas Mazeika, Akul Arora, Ethan Guo, Collin Burns, Samir Puranik, Horace He, Dawn Song, et al. Measuring coding challenge competence with apps. arXiv preprint arXiv:2105.09938, 2021.

Jonathan Ho and Stefano Ermon. Generative adversarial imitation learning. Advances in neural information processing systems, 29, 2016.

Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, et al. Training compute-optimal large language models. arXiv preprint arXiv:2203.15556, 2022.

Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, and Yejin Choi. The curious case of neural text degeneration. In International Conference on Learning Representations, 2019.

Ehsan Imani, Eric Graves, and Martha White. An off-policy policy gradient theorem using emphatic weightings. Advances in Neural Information Processing Systems, 31, 2018.

Alexis Jacq, Matthieu Geist, Ana Paiva, and Olivier Pietquin. Learning from a learner. In International Conference on Machine Learning, pp. 2990–2999. PMLR, 2019.

Nan Jiang and Jiawei Huang. Minimax value interval for off-policy evaluation and policy optimization. Advances in Neural Information Processing Systems, 33:2747–2758, 2020.

Dmitry Kalashnikov, Alex Irpan, Peter Pastor, Julian Ibarz, Alexander Herzog, Eric Jang, Deirdre Quillen, Ethan Holly, Mrinal Kalakrishnan, Vincent Vanhoucke, et al. Scalable deep reinforcement learning for vision-based robotic manipulation. In Conference on Robot Learning, pp. 651– 673. PMLR, 2018.

Alex Kendall, Jeffrey Hawke, David Janz, Przemyslaw Mazur, Daniele Reda, John-Mark Allen, Vinh-Dieu Lam, Alex Bewley, and Amar Shah. Learning to drive in a day. In 2019 International Conference on Robotics and Automation (ICRA), pp. 8248–8254. IEEE, 2019.

Jacob Devlin Ming-Wei Chang Kenton and Lee Kristina Toutanova. Bert: Pre-training of deep bidirectional transformers for language understanding. In Proceedings of NAACL-HLT, pp. 4171– 4186, 2019.

Vijay Konda and John Tsitsiklis. Actor-critic algorithms. Advances in neural information processing systems, 12, 1999.

Aviral Kumar, Aurick Zhou, George Tucker, and Sergey Levine. Conservative q-learning for offline reinforcement learning. Advances in Neural Information Processing Systems, 33:1179–1191, 2020.

Hung Le, Yue Wang, Akhilesh Deepak Gotmare, Silvio Savarese, and Steven Chu Hong Hoi. Coderl: Mastering code generation through pretrained models and deep reinforcement learning. Advances in Neural Information Processing Systems, 35:21314–21328, 2022.

Sergey Levine, Aviral Kumar, George Tucker, and Justin Fu. Offline reinforcement learning: Tutorial, review, and perspectives on open problems. arXiv preprint arXiv:2005.01643, 2020.

Raymond Li, Loubna Ben Allal, Yangtian Zi, Niklas Muennighoff, Denis Kocetkov, Chenghao Mou, Marc Marone, Christopher Akiki, Jia Li, Jenny Chim, et al. Starcoder: may the source be with you! arXiv preprint arXiv:2305.06161, 2023.

Yujia Li, David Choi, Junyoung Chung, Nate Kushman, Julian Schrittwieser, Remi Leblond, Tom ´ Eccles, James Keeling, Felix Gimeno, Agustin Dal Lago, et al. Competition-level code generation with alphacode. Science, 378(6624):1092–1097, 2022.

Chin-Yew Lin. Rouge: A package for automatic evaluation of summaries. In Text summarization branches out, pp. 74–81, 2004.

Jiate Liu, Yiqin Zhu, Kaiwen Xiao, Qiang Fu, Xiao Han, Wei Yang, and Deheng Ye. Rltf: Reinforcement learning from unit test feedback. arXiv preprint arXiv:2307.04349, 2023.

Yao Liu, Adith Swaminathan, Alekh Agarwal, and Emma Brunskill. Off-policy policy gradient with stationary distribution correction. In Uncertainty in artificial intelligence, pp. 1180–1190. PMLR, 2020.

Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In International Conference on Learning Representations, 2018.

Ziyang Luo, Can Xu, Pu Zhao, Qingfeng Sun, Xiubo Geng, Wenxiang Hu, Chongyang Tao, Jing Ma, Qingwei Lin, and Daxin Jiang. Wizardcoder: Empowering code large language models with evol-instruct. arXiv preprint arXiv:2306.08568, 2023.

Volodymyr Mnih, Koray Kavukcuoglu, David Silver, Alex Graves, Ioannis Antonoglou, Daan Wierstra, and Martin Riedmiller. Playing atari with deep reinforcement learning. arXiv preprint arXiv:1312.5602, 2013.

Matej Moravcˇ´ık, Martin Schmid, Neil Burch, Viliam Lisy, Dustin Morrill, Nolan Bard, Trevor \` Davis, Kevin Waugh, Michael Johanson, and Michael Bowling. Deepstack: Expert-level artificial intelligence in heads-up no-limit poker. Science, 356(6337):508–513, 2017.

Ofir Nachum, Mohammad Norouzi, Kelvin Xu, and Dale Schuurmans. Bridging the gap between value and policy based reinforcement learning. Advances in neural information processing systems, 30, 2017.

Ashvin V Nair, Vitchyr Pong, Murtaza Dalal, Shikhar Bahl, Steven Lin, and Sergey Levine. Visual reinforcement learning with imagined goals. Advances in neural information processing systems, 31, 2018.

Andrew Y Ng, Stuart Russell, et al. Algorithms for inverse reinforcement learning. In Icml, volume 1, pp. 2, 2000.

Erik Nijkamp, Bo Pang, Hiroaki Hayashi, Lifu Tu, Huan Wang, Yingbo Zhou, Silvio Savarese, and Caiming Xiong. Codegen: An open large language model for code with multi-turn program synthesis. In The Eleventh International Conference on Learning Representations, 2022.

R OpenAI. Gpt-4 technical report. arXiv, pp. 2303–08774, 2023.

Peter-Michael Osera and Steve Zdancewic. Type-and-example-directed program synthesis. ACM SIGPLAN Notices, 50(6):619–630, 2015.

Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35: 27730–27744, 2022.

Kishore Papineni, Salim Roukos, Todd Ward, and Wei-Jing Zhu. Bleu: a method for automatic evaluation of machine translation. In Proceedings of the 40th annual meeting of the Association for Computational Linguistics, pp. 311–318, 2002.

Maxim Rabinovich, Mitchell Stern, and Dan Klein. Abstract syntax networks for code generation and semantic parsing. arXiv preprint arXiv:1704.07535, 2017.

Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

Jack W Rae, Sebastian Borgeaud, Trevor Cai, Katie Millican, Jordan Hoffmann, Francis Song, John Aslanides, Sarah Henderson, Roman Ring, Susannah Young, et al. Scaling language models: Methods, analysis & insights from training gopher. arXiv preprint arXiv:2112.11446, 2021.

Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D Manning, and Chelsea Finn. Direct preference optimization: Your language model is secretly a reward model. arXiv preprint arXiv:2305.18290, 2023.

Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J Liu. Exploring the limits of transfer learning with a unified text-to-text transformer. The Journal of Machine Learning Research, 21(1):5485–5551, 2020.

Marc’Aurelio Ranzato, Sumit Chopra, Michael Auli, and Wojciech Zaremba. Sequence level training with recurrent neural networks. arXiv preprint arXiv:1511.06732, 2015.

Steven J Rennie, Etienne Marcheret, Youssef Mroueh, Jerret Ross, and Vaibhava Goel. Self-critical sequence training for image captioning. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 7008–7024, 2017.

Baptiste Roziere, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, Xiaoqing Ellen Tan, Yossi\` Adi, Jingyu Liu, Tal Remez, Jer´ emy Rapin, et al. Code llama: Open foundation models for code.´ arXiv preprint arXiv:2308.12950, 2023.

John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

Parshin Shojaee, Aneesh Jain, Sindhu Tipirneni, and Chandan K Reddy. Execution-based code generation using deep reinforcement learning. arXiv preprint arXiv:2301.13816, 2023.

David Silver. Lecture 7: Policy gradient. UCL Course on RL, 2015.

David Silver, Aja Huang, Chris J Maddison, Arthur Guez, Laurent Sifre, George Van Den Driessche, Julian Schrittwieser, Ioannis Antonoglou, Veda Panneershelvam, Marc Lanctot, et al. Mastering the game of go with deep neural networks and tree search. nature, 529(7587):484–489, 2016.

Riley Simmons-Edler, Anders Miltner, and Sebastian Seung. Program synthesis through reinforcement learning guided tree search. arXiv preprint arXiv:1806.02932, 2018.

Nisan Stiennon, Long Ouyang, Jeffrey Wu, Daniel Ziegler, Ryan Lowe, Chelsea Voss, Alec Radford, Dario Amodei, and Paul F Christiano. Learning to summarize with human feedback. Advances in Neural Information Processing Systems, 33:3008–3021, 2020.

Phillip D Summers. A methodology for lisp program construction from examples. Journal of the ACM (JACM), 24(1):161–175, 1977.

Arash Tavakoli, Fabio Pardo, and Petar Kormushev. Action branching architectures for deep reinforcement learning. In Proceedings of the aaai conference on artificial intelligence, volume 32, 2018.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothee´ Lacroix, Baptiste Roziere, Naman Goyal, Eric Hambro, Faisal Azhar, et al. Llama: Open and\` efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023.

Hado Van Hasselt, Arthur Guez, and David Silver. Deep reinforcement learning with double qlearning. In Proceedings of the AAAI conference on artificial intelligence, volume 30, 2016.

Ben Wang and Aran Komatsuzaki. GPT-J-6B: A 6 Billion Parameter Autoregressive Language Model. https://github.com/kingoflolz/mesh-transformer-jax, May 2021.

Xin Wang, Yasheng Wang, Yao Wan, Fei Mi, Yitong Li, Pingyi Zhou, Jin Liu, Hao Wu, Xin Jiang, and Qun Liu. Compilable neural code generation with compiler feedback. In Findings of the Association for Computational Linguistics: ACL 2022, pp. 9–19, 2022.

Yue Wang, Weishi Wang, Shafiq Joty, and Steven CH Hoi. Codet5: Identifier-aware unified pretrained encoder-decoder models for code understanding and generation. In Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing, pp. 8696–8708, 2021.

Yue Wang, Hung Le, Akhilesh Deepak Gotmare, Nghi DQ Bui, Junnan Li, and Steven CH Hoi. Codet5+: Open code large language models for code understanding and generation. arXiv preprint arXiv:2305.07922, 2023.

Ziyu Wang, Tom Schaul, Matteo Hessel, Hado Hasselt, Marc Lanctot, and Nando Freitas. Dueling network architectures for deep reinforcement learning. In International conference on machine learning, pp. 1995–2003. PMLR, 2016.

Christopher JCH Watkins and Peter Dayan. Q-learning. Machine learning, 8:279–292, 1992.

Ronald J Williams. Simple statistical gradient-following algorithms for connectionist reinforcement learning. Machine learning, 8:229–256, 1992.

Tengyang Xie, Ching-An Cheng, Nan Jiang, Paul Mineiro, and Alekh Agarwal. Bellman-consistent pessimism for offline reinforcement learning. Advances in neural information processing systems, 34:6683–6694, 2021a.

Tengyang Xie, Nan Jiang, Huan Wang, Caiming Xiong, and Yu Bai. Policy finetuning: Bridging sample-efficient offline and online reinforcement learning. Advances in neural information processing systems, 34:27395–27407, 2021b.

Can Xu, Qingfeng Sun, Kai Zheng, Xiubo Geng, Pu Zhao, Jiazhan Feng, Chongyang Tao, and Daxin Jiang. Wizardlm: Empowering large language models to follow complex instructions. arXiv preprint arXiv:2304.12244, 2023.

Michihiro Yasunaga and Percy Liang. Graph-based, self-supervised program repair from diagnostic feedback. In International Conference on Machine Learning, pp. 10799–10808. PMLR, 2020.

Zishun Yu and Xinhua Zhang. Actor-critic alignment for offline-to-online reinforcement learning. In Proceedings of the 40th International Conference on Machine Learning, volume 202, pp. 40452– 40474, 2023.

Wenhao Zhan, Baihe Huang, Audrey Huang, Nan Jiang, and Jason Lee. Offline reinforcement learning with realizability and single-policy concentrability. In Conference on Learning Theory, pp. 2730–2775. PMLR, 2022.

Qinkai Zheng, Xiao Xia, Xu Zou, Yuxiao Dong, Shan Wang, Yufei Xue, Zihan Wang, Lei Shen, Andi Wang, Yang Li, et al. Codegeex: A pre-trained model for code generation with multilingual evaluations on humaneval-x. arXiv preprint arXiv:2303.17568, 2023.

Victor Zhong, Caiming Xiong, and Richard Socher. Seq2sql: Generating structured queries from natural language using reinforcement learning. arXiv preprint arXiv:1709.00103, 2017.

Brian D Ziebart, Andrew L Maas, J Andrew Bagnell, Anind K Dey, et al. Maximum entropy inverse reinforcement learning. In Aaai, volume 8, pp. 1433–1438. Chicago, IL, USA, 2008.

Daniel M Ziegler, Nisan Stiennon, Jeffrey Wu, Tom B Brown, Alec Radford, Dario Amodei, Paul Christiano, and Geoffrey Irving. Fine-tuning language models from human preferences. arXiv preprint arXiv:1909.08593, 2019.

Martin Zinkevich, Michael Johanson, Michael Bowling, and Carmelo Piccione. Regret minimization in games with incomplete information. Advances in neural information processing systems, 20, 2007.

Amit Zohar and Lior Wolf. Automatic program synthesis of long programs with a learned garbage collector. Advances in neural information processing systems, 31, 2018.

## A PSEUDO-CODE FOR TRAINING

Algorithm 1 Training Procedure with ϕ- and θ-stages   
Require: $\theta _ { \mathrm { c k p t } } , \phi ,$ and θ with a shared frozen encoder   
1: # pre-training stage, update ϕ only   
2: procedure PRETRAIN $V \mathbf { V } \mathbf { A L U E } ( \bar { \phi } )$ ▷ ϕ-stage   
3: for num iters do   
4: Draw sample $( s , a , r , s ^ { \prime } )$ from dataset   
5: Compute logits $\ell _ { \theta _ { \mathrm { c k p t } } } ( s , \cdot )$   
6: Compute state value $V _ { \phi } ( s )$   
7: Compute loss $\mathcal { L } _ { V } ( V _ { \phi } ; \dot { \ell } _ { \theta _ { \mathrm { c k p t } } } )$ ▷ arguments omitted for brevity   
8: Gradient step with $\nabla _ { \phi } \mathcal { L } _ { V } \overline { { ( V _ { \phi } ; \ell _ { \theta _ { \mathrm { c k p t } } } ) } }$ ▷ equation 12   
9: end for   
10: end procedure   
11: # fine-tuning stage, update θ only   
12: procedure FINETUNE $Q { \mathrm { V A L U E } } ( \theta )$ ▷ θ-stage   
13: for num iters do   
14: Draw sample $( s , a , r , s ^ { \prime } )$ from dataset   
15: Compute residual state-value $V _ { \theta } ^ { r } ( s )$   
16: Compute pre-trained state-value $\dot { V _ { \phi } } ( s )$   
17: Compute state-value $V _ { \theta } ( s ) = V _ { \theta } ^ { r } ( \stackrel { \cdot } { s } ) \stackrel { \cdot } { + } V _ { \phi } ( s )$   
18: Compute advantage $A _ { \theta } ( \tilde { s , \cdot } ) = \mathsf { \bar { \ell } } _ { \theta } ( \tilde { s } , \cdot ) - \operatorname* { m a x } _ { a } \ell _ { \theta } ( s , a )$   
19: Compute $Q _ { \theta } ( s , \cdot ) \bar { = } \alpha \dot { A } _ { \theta } ( \dot { s } , \cdot ) + \dot { V } _ { \theta } ( \dot { s } )$ ▷ equation 16   
20: Compute $\pi _ { \boldsymbol { \theta } } ( \cdot | s ) = \operatorname { s o f t m a x } ( Q _ { \boldsymbol { \theta } } ( s , \cdot ) / \alpha )$   
21: Compute $p _ { \theta _ { \mathrm { c k p t } } } ( \cdot | s )$ ▷ equation 14   
22: Compute $\mathcal { L } _ { Q } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c k p t } } } )$ ▷ equation 15   
23: Compute $\mathcal { L } _ { \mathrm { c e } } ( \pi _ { \theta } )$ and $\mathcal { L } _ { \mathrm { a d v } } ( A _ { \theta } )$ ▷ equation 1 and 8   
24: Compute fine-tune loss $\begin{array} { r } { \mathcal { L } _ { \mathrm { f t } } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c k p t } } } ) = \mathcal { L } _ { Q } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c k p t } } } ) + \beta _ { \mathrm { c e } } \mathcal { L } _ { \mathrm { c e } } ( \pi _ { \theta } ) + \bar { \beta } _ { \mathrm { a d v } } \mathcal { L } _ { \mathrm { a d v } } ( A _ { \theta } ) } \end{array}$   
25: Gradient step with $\nabla _ { \theta } \mathcal { L } _ { \mathrm { f t } } ( Q _ { \theta } ; p _ { \theta _ { \mathrm { c k p t } } } )$   
26: end for   
27: end procedure

## B PSEUDO-CODE FOR SAMPLING

Algorithm 2 Sampling Procedure   
Require: model parameters $\boldsymbol { \theta } , \phi ; \mathrm { S A M P L E R } _ { p , t } ( \cdot ) : \mathbb { R } ^ { 1 \times | \mathcal { V } | }  \mathcal { V }$ that maps a logits vector to a token   
with hyper-parameters p (top-p sampling) and temperature t   
1:   
2: procedure SAMPLEONETOKEN(s)   
3: Obtain current state s   
4: Compute logits vector $\ b \ell _ { \theta } ( s ) \in \mathbb { R } ^ { 1 \times | \mathcal { V } | }$   
5: Compute advantage vector $\begin{array} { r } { \mathbf { A } _ { \theta } ( s ) = \ell _ { \theta } ( s ) - \operatorname* { m a x } _ { a } \ell _ { \theta } ( s ) [ a ] } \end{array}$   
6: Compute $V _ { \theta } ( s ) = \overline { { { V _ { \theta } ^ { r } ( s ) + \dot { V _ { \phi } } ( s ) } } }$   
7: Compute Q vector $\begin{array} { r } { \dot { \bf Q } _ { \theta } ( s ) = \dot { \alpha } \dot { \bf A } _ { \theta } ( s ) + V _ { \theta } ( s ) } \end{array}$   
8: Run $\mathbf { S } \mathbf { A M P L E R } _ { p , t } \left( \mathbf { Q } _ { \theta } ( s ) / \alpha \right)$ ▷ sample with $\mathbf { Q } _ { \theta } ( s ) / \alpha$   
9: end procedure

## C ADDITIONAL RELATED WORKS

Off-policy policy-based methods. One string of off-policy policy-based methods is based on importance ratio. Suppose the data is collected by a behavior policy β, PG with off-policy data can be corrected by $\begin{array} { r } { \nabla _ { \mu } J ( \mu ) = \mathbb { E } _ { \beta } [ \frac { \pi _ { \mu } ( a _ { t } | s _ { t } ) } { \beta ( a _ { t } | s _ { t } ) } ( \sum _ { i = t } ^ { T } \gamma ^ { i - t } r _ { i } ) \nabla _ { \mu } \log \pi _ { \mu } ( a _ { t } | s _ { t } ) ] } \end{array}$ . This allows unbiased gradient even though the data distribution is off-policy. However, computing the ratio $\pi _ { \mu } ( a | s ) / \beta ( a | s )$ is not always feasible as the density function of off-policy data, such as human data, is often unknown. In addition, this correction can lead to high variance due to the product of ratios along trajectories.

While vanilla importance-weighted off-policy PG does not require the approximation of value functions, some advanced ratio-based methods often incorporate value functions, such as (Imani et al., 2018; Liu et al., 2020). Another viable approach is the direct combination of value-based and policybased methods, often referred to as the actor-critic framework, e.g. (Konda & Tsitsiklis, 1999; Degris et al., 2012). Although actor-critic methods are often conisdered as the third category, besides policy-based and value-based, we and some other works (Fujimoto et al., 2018) lean towards categorizing actor-critic to be more value-based, as the major difficulty lies in value function approximations. Nevertheless, both directions of extending policy-based methods to an off-policy setting, largely rely on the value functions. This emphasizes the motivation and significance of our work.

Reward modeling and beyond. Due to the successes of reinforcement learning from human/AI feedback (Christiano et al., 2017; Bai et al., 2022b). Reward modeling and RL fine-tuning with learned reward model has been a popular choice for post-SFT (supervised fine-tuning) refinement (see e.g. Ziegler et al., 2019; Stiennon et al., 2020; Bai et al., 2022a; Ouyang et al., 2022). In particular, in program synthesis, Le et al. (2022) trains a classifier, that predicts unit test outcomes, as their reward model for RL fine-tuning. However, reward models can sometimes be expensive to train and their quality can heavily impact RL fine-tuning performance. Recent works (e.g. Rafailov et al., 2023; Diao et al., 2023) explore preference learning beyond conventional reward model.

Modeling reward function, on the other hand, has been a long-lasting topic in inverse RL or imitation learning (IRL or IL, see e.g. Ng et al., 2000; Abbeel & Ng, 2004; Ziebart et al., 2008; Ho & Ermon, 2016). While conventional IRL/IL often iterates between reward model fitting and RL training stages, recent IL works (Jacq et al., 2019; Garg et al., 2021) also explore beyond explicitly reward modeling to reduce training instability and optimization difficulty, led by the iterative optimization scheme. Specifically, Garg et al. (2021) leverages the one-to-one correspondence between Q-function and reward model, given the soft Bellman operator, to eliminate the reward fitting step.

Candidate selection in program synthesis. Existing works have shown one could improve program pass rate by filtering out programs that are likely to be incorrect. For instance, Chen et al. (2021a) filtered out programs that cannot pass example unit tests given in doc-strings, and Chen et al. (2022) filtered out programs that cannot pass generated unit tests. Furthermore, reward models are also often used to rank candidate programs (see e.g. Gulcehre et al., 2023; Touvron et al., 2023).

## D A SPECTRUM OF RL APPLICATIONS

To conceptually demonstrate the differences between policy-based and value-based methods, and why program synthesis might be well-suited to value-based approaches, Figure 4 presents a spectrum of RL applications. It could be observed that in scenarios where rewards are not expensive to evaluate or there’s plenty of off-policy data (data not generated by the current policy/model) value-based methods tend to be preferred. Consider, for instance, InstructGPT (Ouyang et al., 2022) (policy-based) and AlphaGo (Silver et al., 2016) (value-based). The former relies on human annotators (expensive) to label model-generated (on-policy) responses, while the latter obtains rewards from simulators (cheap), and leverages (1) human expert games (off-policy) during training and (2) re-using historical games (off-policy) through experience reply.

Table 5 provides explanations our application plot of Figure 4. Applications in games typically find it easy to obtain rewards and make extensive use of off-policy data, e.g human games or historical replays. Conversely, InstructGPT obtains its rewards from preferences labeled by human annotators, with the data predominantly generated by the GPT model itself. The self-driving application notable has high cost of gathering rewards, due to the risks of real-world driving. While existing driving data could be utilized, Kendall et al. (2019) specifically choose not to use pre-collected data, leading to their choice of a policy-based algorithm.

![](images/068c4ede7d15e9a29acd06c5a0626f136d2b985b02c35e65322eadac762bbb9e.jpg)  
Figure 4: A collection of RL applications. and represents value-based and policy-based RL, respectively. The x-axis shows the difficulty of obtaining rewards, while the y-axis measures the amount of off-policy data. Tasks that face significant hurdles in gathering rewards or have limited off-policy data typically lean towards policy-based algorithms. Tasks where rewards are more readily obtained or that benefit from a substantial collection of off-policy data favors valuebased methods. See descriptions of each task in Table 5.

In code generation, despite the availability of cheap rewards and the existing collection of off-policy programs, whether human-written or historical synthetic programs, current literature leans towards policy-based methods. We believe that value-based methods could be a promising direction, given their similarity to tasks with simulators.

Table 5: Summary of RL applications.
<table><tr><td rowspan=1 colspan=5>References             | Tpe of RLCosts of Getting Rewards     Available Off-Policy Data</td></tr><tr><td rowspan=1 colspan=1>Atari</td><td rowspan=1 colspan=1>(Mnih et al., 2013)</td><td rowspan=1 colspan=1>value</td><td rowspan=1 colspan=1>cheap: simulator</td><td rowspan=1 colspan=1>extensive: history/human games</td></tr><tr><td rowspan=1 colspan=1>GO</td><td rowspan=1 colspan=1>(Silver et al., 2016)</td><td rowspan=1 colspan=1>value</td><td rowspan=1 colspan=1>cheap: simulator</td><td rowspan=1 colspan=1>extensive: history/human games</td></tr><tr><td rowspan=1 colspan=1>Poker</td><td rowspan=1 colspan=1>(Moravk et al., 2017)(Brown &amp; Sandholm, 2018)</td><td rowspan=1 colspan=1> $\mathrm { v a l u e } ^ { 4 }$ </td><td rowspan=1 colspan=1>cheap: simulator</td><td rowspan=1 colspan=1>extensive: history/human games</td></tr><tr><td rowspan=1 colspan=1>StarCraft I</td><td rowspan=1 colspan=1>(Arulkumaran et al., 2019)</td><td rowspan=1 colspan=1>value</td><td rowspan=1 colspan=1>cheap: simulator</td><td rowspan=1 colspan=1>extensive: history/human games</td></tr><tr><td rowspan=1 colspan=1>InstructGPT</td><td rowspan=1 colspan=1>(Ouyang et al., 2022)</td><td rowspan=1 colspan=1>policy</td><td rowspan=1 colspan=1>expensive: human annotators</td><td rowspan=1 colspan=1>limited: mostly model-generated data</td></tr><tr><td rowspan=1 colspan=1>ImageCaption</td><td rowspan=1 colspan=1>(Ranzato et al., 2015)(Rennie et al., 2017)</td><td rowspan=1 colspan=1>policy</td><td rowspan=1 colspan=1>cheap: automatic metrics</td><td rowspan=1 colspan=1>limited: mostly model-generated data</td></tr><tr><td rowspan=1 colspan=1>Self-driving</td><td rowspan=1 colspan=1>(Kendall et al, 2019)</td><td rowspan=1 colspan=1>policy</td><td rowspan=1 colspan=2>expensive: driving in real-worldlimited: mostly model-generated data</td></tr><tr><td rowspan=1 colspan=1>CodeGeneration</td><td rowspan=1 colspan=1>(Le et al., 2022)(Shojaee et al., 2023)(Liu et al., 2023)</td><td rowspan=1 colspan=1>policy</td><td rowspan=1 colspan=1>cheap: unit testing</td><td rowspan=1 colspan=1>extensive: collection of human programs</td></tr></table>

## E REWARD ENGINEERING COMPARISON

Table 6 shows that ours has the least reward engineering effort. Note that our reward model $\tilde { r } _ { \theta }$ is directly derived from $Q _ { \theta }$ , and is not used for training.

Table 7 shows the results when only basic reward function (defined in equation 2) is used, under no example test outcomes setting. CodeRL and RLTF results are duplicated from their reports.

Table 6: Comparison of reward designs
<table><tr><td>Reward</td><td>Remark</td><td>Ours</td><td>CodeRL</td><td>RLTF</td><td>PPOCoder</td></tr><tr><td>Basic</td><td>equation 2</td><td>√</td><td>&gt;&gt;</td><td>✓</td><td>✓</td></tr><tr><td>Reward Model</td><td>learned reward model</td><td></td><td></td><td></td><td></td></tr><tr><td>Fine-Grained</td><td>fine-grained error type &amp; location of error</td><td></td><td></td><td>✓</td><td></td></tr><tr><td>Adaptive</td><td>ratio of passed tests</td><td></td><td></td><td>✓</td><td></td></tr><tr><td>Syntactic Correctness</td><td>compilable</td><td></td><td></td><td></td><td>✓</td></tr><tr><td>Syntactic Matching</td><td>syntactic similarity to ground truth</td><td></td><td></td><td></td><td></td></tr><tr><td>Semantic Matching</td><td>semantic similarity to ground truth</td><td></td><td></td><td></td><td>✓</td></tr></table>

Table 7: Performance with only basic reward (equation 2). †and ‡‡ indicates results duplicated from Le et al. (2022) and Liu et al. (2023), respectively.
<table><tr><td rowspan="2">Model</td><td colspan="4">Pass@1</td><td colspan="4">Pass@5</td></tr><tr><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td><td>Intro</td><td>Inter</td><td>Comp</td><td>All</td></tr><tr><td>CodeRL†</td><td>4.60</td><td>1.10</td><td>0.20</td><td>1.62</td><td>7.10</td><td>1.57</td><td>0.40</td><td>2.44</td></tr><tr><td>RLTF</td><td>-</td><td>-</td><td>-</td><td>1.37</td><td>-</td><td>-</td><td>-</td><td>3.50</td></tr><tr><td>B-Coder</td><td>6.70</td><td>1.50</td><td>0.30</td><td>2.30</td><td>10.40</td><td>2.63</td><td>0.70</td><td>3.80</td></tr></table>

## F ADVANTAGE OF APPROXIMATE VERSION OF $\tilde { r }$

Recap that our recovered reward r˜ is computed by

$$
\begin{array} { r } { \tilde { r } _ { \theta } ( s , a ) = Q _ { \theta } ( s , a ) - \gamma \mathbb { E } _ { s ^ { \prime } } Q _ { \theta } \left( s ^ { \prime } , \mathrm { a r g } \operatorname* { m a x } _ { a } p _ { \theta _ { \mathrm { c k p t } } } ( a | s ^ { \prime } ) \right) \approx Q _ { \theta } ( s , a ) - \gamma V _ { \theta } ( s ^ { \prime } ) . } \end{array}\tag{20}
$$

Imagining a scenario in which we sample/decode using a trained $Q _ { \theta }$ , the forward pass will compute $Q _ { \theta } ( s , a )$ and $V _ { \theta } ( s )$ for each timestep, because of our dueling architecture. But $p _ { \theta _ { \mathrm { c k p t } } }$ will not be evaluated during generation, because $p _ { \theta _ { \mathrm { c k p t } } }$ is only used when computing $\mathcal { L } _ { Q } ( \cdot ; p _ { \theta _ { \mathrm { c k p t } } } )$ . Computing the exact version $\begin{array} { r } { Q _ { \theta } \big ( s , a \big ) - \gamma \mathbb { E } _ { s ^ { \prime } } Q _ { \theta } \big ( s ^ { \prime } , \operatorname { a r g m a x } _ { a } p _ { \theta _ { \mathrm { c k p t } } } ( a | s ^ { \prime } ) \big ) } \end{array}$ will require additional computation of $p _ { \theta _ { \mathrm { c k p t } } }$ during generation. In contrast, $Q ( s , a )$ and $V ( s )$ are already computed during generation, therefore it requires almost no additional computation to compute $\tilde { r } _ { \theta } ( s , a )$

## G ADDITIONAL IMPLEMENTATION TRICKS

## G.1 UPPER BOUND OF Q-FUNCTION

Given our reward design in equation 2, the cumulative reward is upper bounded by $R _ { \mathrm { m a x } } ~ = ~ 1$ We enforce $Q ( s , a ) \leq R _ { \mathrm { m a x } }$ by transform the state value function as $\bar { V } ( s ) = - \mathrm { s o F T A B S } \left( V ( s ) \right) +$ $R _ { \mathrm { m a x } } \leq R _ { \mathrm { m a x } } ,$ , where SOFTABS(x) := [SOFTPL $\mathrm { J S } ( x ) + \mathrm { S O F T P L U S } ( - x ) ] / 2 + \ln 2$ is a soft absolute function. Given $A ( s , a ) \leq 0$ , enforcing $\mathbf { \bar { \phi } } _ { V ( s ) } \le R _ { \mathrm { m a x } }$ leads to $Q ( s , a ) \leq R _ { \operatorname* { m a x } }$

## G.2 RESIDUAL HEAD INITIALIZATION

In section 4.3, we initialize θ in a way such that $\ell _ { \theta } = \ell _ { \theta _ { \mathrm { c k p t } } }$ and $V _ { \theta } ^ { r } ( s ) = 0$ . The former can be done by simply loading the checkpoint $\theta _ { \mathrm { c k p t } }$ . Adding a residual head $V _ { \theta } ^ { r }$ , that initialized to output zeros, can be done with a simple trick. One can simply add two heads $h _ { 1 }$ and $h _ { 2 }$ , let $h _ { 1 }$ be trainable, and $h _ { 2 }$ be fixed for subsequent fine-tuning, setting $\dot { V } _ { \theta } ^ { r } = h _ { 1 } - h _ { 2 }$ achieves the desired functionality.

## H TRAINING AND EVALUATION DETAILS

In supplement to implementation details in Section 4.4 and 5, we give more low-level details here.

APPS dataset. In addition to the train/test split details described in Section 5, APPS datast, on average, consists of 2 example unit tests, 21 hidden unit tests, and 23 ground truth programs. We follow the same procudure as Hendrycks et al. (2021); Le et al. (2022) to construct prompts for both training and evaluation. Specifically, see Section 3 of Hendrycks et al. (2021).

MBPP dataset. MBPP has 974 instances with a 374/90/500 train/val/test splits and, in addition, 10 problems reserved for few-shot learning. Because we only do zero-shot evaluation on MBPP, only the 500 test problems are used for evaluation. Each problem of MBPP usually comes with three unit tests. In addition, these tests are usually not hidden. Therefore, prior works Le et al. (2022); Shojaee et al. (2023); Liu et al. (2023) often explicitly incorporate the tests into prompt string. We follow WizardCoder (Luo et al., 2023) to construct our input format. Details could be found in this repo.

Pre-trained model. We initialize our model with CodeRL checkpoint publicly available at here, meaning we initialize $\theta _ { \mathrm { c k p t } } ,$ ϕ, and θ from it. Note that we freeze encoder for both ϕ-stage and θ-stage, therefore the encoder is shared during both training and generation. For both training and generation, we set the maximum length to 600 and 512 for source and target sequences, respectively.

Training data preparation. While we use $\mathcal { D } _ { \mathrm { t r a i n } }$ to represent our training dataset, yet we have not elaborated on how it is constructed. In general, we follow the protocol of prior RL-based works that combining all ground truth programs and a set of programs generated by the pre-trained model, for each problem D. Specifically, we generate 256 programs per problem using pre-trained checkpoint. Combined with ground truth programs, there are, on average, 278 programs per problem.

Mini-batch preparation. By prior definition, our dataset $\mathcal { D } _ { \mathrm { t r a i n } }$ now contains both ground truth programs and generated programs. Notably, the volume of generated programs is significantly larger than that of the ground truth programs. This means that if one were to randomly sample from the dataset, generated programs would dominate the mini-batches. To address this, when preparing a mini-batch, we sample $\rho _ { \mathrm { r e a l } } \times B$ ground truth programs and $( 1 - \rho _ { \mathrm { r e a l } } ) \times B$ generated programs, where B is batch size.

ϕ-stage training. In the ϕ-stage, we pre-train state-value function $V _ { \phi } ( s )$ . We conduct our experiment with 4×A100-80G GPUs. Specifically, we use batch size of 16 for each GPU and gradient accumulation step of 4, resulting in a total batch size of 256. For optimizer and scheduler, we use AdamW optimizer (Loshchilov & Hutter, 2018) with a constant learning rate of 1e-5 and a weight decay of 0.05. We train ϕ for 18k gradient steps.

θ-stage training. In the θ-stage, we conduct our experiment with 8×A100-80G GPUs. Specificaly we use batch size of 16 for each GPU and gradient accumulation step of 1, resulting in a total batch size of 128. For optimizer and scheduler, we use AdamW with a peak learning rate 3e-5, a weight decay of 0.05, and a linear decay scheduler with no warmup. We train θ for 10k gradient steps.

Other hyper-parameters. We set the ground truth data ratio $\rho _ { \mathrm { r e a l } } { = } 0 . 5$ and the energy-based policy temperature α = 1 (see equation 10) for all experiments. In θ-stage, we use $\beta _ { \mathrm { a d v } } = 0 . 1$ and $\beta _ { \mathrm { c e } } = 0 . 5$

## I ABLATION ON m

![](images/e40d5b2c9e8087b638167d68969c2e6d9ad638b25017ab98c03f248f9086190a.jpg)  
Figure 5: Ablation on m: our ranking strategy achieves consistent improvements under different budgets m.

Table 5 conduct an ablation study on ranking budgets $m ,$ it can be observed that our ranking strategy achieves consistent improvements under different budgets m.

## J COMMENTS ON $B ^ { q }$ PROPERTIES

## J.1 PROPOSITION 4.1

Proof.

$$
\| { \mathcal { B } } ^ { q } Q _ { 1 } - { \mathcal { B } } ^ { q } Q _ { 2 } \| _ { \infty } = \operatorname* { m a x } _ { s , a } | r ( s , a ) + \gamma \mathbb { E } _ { s ^ { \prime } } Q _ { 1 } \left( s ^ { \prime } , \hat { a } ^ { \prime } \right) - r ( s , a ) - \gamma \mathbb { E } _ { s ^ { \prime } } Q _ { 2 } ( s ^ { \prime } , \hat { a } ^ { \prime } ) |
$$

$$
( \hat { a } ^ { \prime } = \arg \operatorname* { m a x } _ { a } q ( a | s ^ { \prime } ) )
$$

$$
= \operatorname* { m a x } _ { s , a } \gamma \left| \mathbb { E } _ { s ^ { \prime } } \left[ Q _ { 1 } ( s ^ { \prime } , \hat { a } ^ { \prime } ) - Q _ { 2 } ( s ^ { \prime } , \hat { a } ^ { \prime } ) \right] \right|\tag{21}
$$

$$
\leq \operatorname* { m a x } _ { s , a } \gamma \mathbb { E } _ { s ^ { \prime } } \left| Q _ { 1 } ( s ^ { \prime } , \hat { a } ^ { \prime } ) - Q _ { 2 } ( s ^ { \prime } , \hat { a } ^ { \prime } ) \right|\tag{22}
$$

$$
\leq \operatorname* { m a x } _ { s , a } \gamma \mathbb { E } _ { s ^ { \prime } } \operatorname* { m a x } _ { s ^ { \prime } , a ^ { \prime } } | Q _ { 1 } ( s ^ { \prime } , a ^ { \prime } ) - Q _ { 2 } ( s ^ { \prime } , a ^ { \prime } ) |\tag{23}
$$

$$
= \gamma \| Q _ { 1 } - Q _ { 2 } \| _ { \infty }\tag{24}
$$

## J.2 PROPOSITION 4.2

Proof. The proof is similar to Lemma C.3. in Garg et al. (2021). To prove that $\mathcal { T } ^ { p }$ is a bijection, it suffices to show that for any $r : S \times \mathcal { A }  \mathbb { R }$ , there exists a unique $Q : S \times A  \mathbb { R }$ such that $r = \mathcal { T } ^ { p } Q$ . Note that by proposition $4 . 1$ , there exists a unique $Q ^ { p } \doteq B ^ { p } r$ that satisfies $Q ^ { p } ( s , a ) =$ $r ( s , a ) + \gamma \mathbb { E } _ { s ^ { \prime } } Q ^ { p } ( s ^ { \prime }$ , arg maxa p(a|s′)). Rearranging the terms gives $r = \mathcal { T } ^ { p } Q ^ { p }$ . This completes the proof.

## K DISCUSSION ON LIMITATIONS

Table 8: Pass@1 results are evaluated with greedy decoded programs, and pass@{5, 50, 100} are computed by sampled programs using a temperature of 0.4.  
Table 9: Ranking with $\tilde { r }$ compared with filtering with real environmental reward function r, i.e. hidden tests. r˜-ranked results are duplicated from Table 1.
<table><tr><td>Pass@</td><td>CodeRL</td><td>B-Coder</td></tr><tr><td>1</td><td>1.60</td><td>1.60</td></tr><tr><td>5</td><td>3.28</td><td>2.88</td></tr><tr><td>50</td><td>7.16</td><td>7.35</td></tr><tr><td>100</td><td>8.76</td><td>9.18</td></tr></table>

<table><tr><td rowspan="2"></td><td colspan="2">r-ranked</td><td rowspan="2">r-filtered</td></tr><tr><td>pass@ 1</td><td>pass@5</td></tr><tr><td>Intro</td><td>6.70</td><td>10.40</td><td>26.60</td></tr><tr><td>Inter</td><td>1.50</td><td>2.63</td><td>7.87</td></tr><tr><td>Comp</td><td>0.30</td><td>0.70</td><td>5.10</td></tr><tr><td>All</td><td>2.30</td><td>3.80</td><td>11.06</td></tr></table>

While being exploratory, our work admits certain limitations including: additional frozen parameters introduced, and we observe that raw performance (without ranking) is mixed compared to CodeRL (see Table 8) (which we believe is somewhat excusable as we use less reward designs). However, we remark the effectiveness of our overall framework including the dual strategy is non-trivial, especially with limited reward engineering.

It is also informative to show results filtered by the true environmental reward function $^ { r , }$ instead of results ranked by our recovered reward function r˜. Although filtering with r requires using hidden tests, meaning it cannot be implemented in realistic settings, also see discussions in Section 4.5. However, it could serve as an upper limit for our ranking strategy and as a sanity check. (Roughly speaking, if $\therefore \tilde { r } = r .$ , the pass rate of r˜-ranking and r-filtering would be identical.) To this end, we use the same set of candidate programs as those in Table 1, but apply the ground truth reward function r to filter candidates rather than using r˜ for ranking. The corresponding results in Table 9 show that, although r˜-ranking is effective, there remains a large room for improvement.
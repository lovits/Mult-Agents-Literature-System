# A LANGUAGE-AGENT APPROACH TOFORMAL THEOREM-PROVING

Anonymous authors Paper under double-blind review

## ABSTRACT

Language agents, which use a large language model (LLM) capable of in-context learning to interact with an external environment, have emerged as a promising approach to control tasks. We present a language-agent approach that offers stateof-the-art performance in formal theorem-proving. Our method, COPRA, uses a high-capacity, black-box LLM (GPT-4) as part of a policy for a stateful backtracking search. During the search, the policy can select proof tactics and retrieve lemmas and definitions from an external database. Each selected tactic is executed in the underlying proof framework, and the execution feedback is used to build the prompt for the next policy invocation. The search also tracks selected information from its history and uses it to reduce hallucinations and unnecessary LLM queries. We evaluate COPRA on the miniF2F benchmark for Lean and a set of Coq tasks from the Compcert project. On these benchmarks, COPRA is significantly better than one-shot invocations of GPT-4, as well as state-of-the-art models fine-tuned on proof data, at finding correct proofs quickly.

## 1 INTRODUCTION

Automatically proving formal theorems (Newell et al., 1957) is a longstanding challenge in computer science. Autoregressive language models (Polu & Sutskever, 2020; Han et al., 2021; Yang et al., 2023) have recently emerged as an effective approach to this problem. Such models are trained on proofs written in frameworks like Coq (Huet et al., 1997) or Lean (de Moura et al., 2015), which allows proof goals to be iteratively simplified using a set of tactics. Theorem-proving then amounts to generating a sequence of tactics that iteratively “discharges” a given proof goal.

A weakness of this method is that it does not model the interaction between the model and the underlying proof framework. The application of a tactic is an action that changes the state of the proof and the interpretation of future tactics. By ignoring these game-like dynamics, autoregressive models miss out on a valuable source of feedback and end up being more susceptible to hallucinations.

In this paper, we show that the nascent paradigm of large-language-model (LLM) agents (Yao et al., 2022; Wang et al., 2023; Shinn et al., 2023) can help address this weakness. Here, one uses an LLM as a agent that interacts with an external environment. Information gathered through interaction is used to update the LLM’s prompt, eliciting new agent behavior because of in-context learning.

Our approach, called COPRA1 (Figure 1), uses an off-the-shelf, high-capacity LLM (GPT-4 (OpenAI, 2023a)) as part of a policy in that interacts with a proof environment like Coq or Lean. At each time step, the policy consumes a textual prompt and chooses to use an available tactic, or backtrack, or retrieve relevant lemmas and definitions from an external corpus. When the policy selects a tactic, we “execute” it using the underlying proof assistant. The feedback from the execution is used to construct a new prompt for the policy, and the process repeats.

COPRA goes beyond prior language-agent methods in using domain knowledge and information from the search history to use LLM queries frugally. When tactics fail, the policy records this information and uses it to avoid future failures. The policy also has access to a symbolic procedure that checks if one goal is “simpler” than another. A tactic is only used when it simplifies the agent’s proof obligations (ruling out, among other things, cyclic tactic sequences).

![](images/48d23f7c0f9489cc851c889f28b8aa859085b66b610174446152ea0950779dcc.jpg)  
Figure 1: An overview of COPRA. The system implements a policy that interacts with a proof environment (Coq or Lean). Internally, a COPRA policy consists of an LLM (GPT-4), a stackbased backtracking search, a retrieval mechanism, a dictionary tracking past failures, and a prompt serialization protocol that constructs LLM prompts using the stack and environment feedback and parse LLM outputs into actions.

We have integrated COPRA with both the Coq and the Lean environments. We evaluate the system using the miniF2F (Zheng et al., 2021) benchmark for competition-level mathematical reasoning in Lean and a set of Coq proof tasks (Sanchez-Stern et al., 2020) from the Compcert (Leroy, 2009) project on verified compilation. Using a new metric called prove-at-k-guidance-steps, we show that COPRA can converge to correct proofs faster than competing approaches, including the state-of-theart models (Yang et al., 2023; Sanchez-Stern et al., 2020) trained on formal proof data. We also show that when COPRA fails, it fails quicker than the baseline methods.

To summarize our contributions, we offer: (i) The first approach to formal theorem-proving that leverages LLMs while also modeling interactions between the model and the underlying proof framework; (ii) the first language agent, from any domain, to integrate LLM policies with a search that minimizes LLM queries and hallucinations by tracking domain-specific information from the past; and (iii) an implementation of COPRA that interacts with the Coq and Lean proof environments, and an evaluation on two domains — mathematics competition problems and formal verification — that shows COPRA to find proofs faster than competing approaches.

## 2 THEOREM-PROVING AS A CONTROL PROBLEM

## 2.1 BACKGROUND ON THEOREM-PROVING

A formal proof starts with a set of unmet obligations stated in a formal language and applies a sequence of proof tactics to progressively eliminate these obligations. Each obligation o consists of a goal g and a hypothesis h. The goal g consists of the propositions that need to be proved in order to meet o; the hypothesis h captures assumptions that can be made in the proof of g. The prover’s long-term objective is to reduce the obligations to the empty set.

We illustrate this process with the example in Figure 2-(a). This example shows a Lean (de Moura et al., 2015) proof, automatically generated using COPRA, of a basic theorem about modular arithmetic. The proof first applies the intro tactic, which changes a goal $P  Q$ to a hypothesis P and a goal Q. Next, it applies the rw (rewrite) tactic, which gives a way to apply substitutions to goals and hypotheses, several times. It ends with the application of the refl (reflexivity) tactic, which eliminates goals that say that a value is equal to itself.

(a)   
(c)   
theorem mod\_arith\_2   
(x : N) : x % 2 = 0 begin   
→ (x \* x) % 2 = 0 intro h,   
:= have h1 : x = 2 \* (x   
begin / 2)   
intro h, := (nat.   
rw nat.mul\_mod, mul\_div\_cancel' h)   
rw h, .symm,   
rw nat.zero\_mul, rw h1,   
refl, rw nat.mul\_div\_assoc   
end   
(show 2 | 2, from   
(b) dvd\_refl \_),   
rw [mul\_assoc, nat.   
x: N   
mul\_mod\_right],   
h: x % 2 = 0   
end   
⊢ x \* x % 2 = 0

Existing LLM-based approaches to automatic theorem-proving view such proofs as purely syntactic artifacts. However, the rigorous semantics of proofs can be difficult to learn using such an approach, leading to the generation of incorrect proofs. Figure 2-(c)

Figure 2: (a) A Lean theorem and a correct proof found by COPRA. (b) Proof state after the first tactic. (c) An incorrect proof generated by GPT-4.

eration of incorrect proofs. Figure 2-(c) shows a GPT-4-generated incorrect proof of our theorem.

## 2.2 A MARKOV DECISION PROCESS FORMULATION

By contrast, COPRA is based on a view of automatic theorem-proving as a control problem. Like prior work on reinforcement learning (RL) for proof synthesis (Wu et al., 2021), we view a theoremprover as a policy that interacts with a stateful proof environment (e.g., Lean) and model the interaction between the policy and the environment as a deterministic Markov Decision Process (MDP). We depart from prior RL-based work for theorem-proving by imposing a partial order on MDP states, adding execution feedback in error states, and allowing history-dependent policies.

Now we describe the different components of our proof MDP.

States. As before, let an obligation be a pair $( g , h )$ , where g is a goal and h a hypothesis. A state of the MDP is either a special symbol called error or a set $O = \{ o _ { 1 } , \ldots , o _ { k } \}$ of obligations $o _ { i } .$ . The MDP has a unique initial state $o _ { i n }$ with a single obligation $( g _ { i n } , h _ { i n } )$ , where the goal $g _ { i n }$ and the hypothesis $h _ { i n }$ are extracted from the user-provided theorem that we are trying to prove. Its unique final state QED is the empty obligation set. The special error symbol is accompanied by textual feedback in the form of an execution error message, execution feedback, from the proof environment.

Following Sanchez-Stern et al. (2020), we define a partial order ⊑ over states that defines when a state is “at least as hard” than another and use it to avoid actions that do not lead to progress in the proof. Formally, for states $O _ { 1 }$ and $O _ { 2 }$ with $O _ { 1 } \neq$ error and O2 ̸= error , $O _ { 1 } \subseteq O _ { 2 }$ iff

$$
\forall o _ { i } = ( g _ { i } , h _ { i } ) \in O _ { 1 } . \exists o _ { k } = ( g _ { k } , h _ { k } ) \in O _ { 2 } . g _ { k } = g _ { i } \land ( h _ { k } \to h _ { i } ) .
$$

Intuitively, $O _ { 1 } \subseteq O _ { 2 }$ if for every obligation in $O _ { 1 }$ , there is a stronger obligation in $O _ { 2 }$ . We assume we have an efficient symbolic procedure that can check this relationship for any pair of states. The procedure is sound, meaning that if it reports $O _ { 1 } \subseteq O _ { 2 }$ , the relationship actually holds. However, it is incomplete, i.e., it may not detect all relationships of the form $O _ { 1 } \subseteq O _ { 2 }$

Actions and Transitions. The actions in our MDP are the proof environment’s tactics. The transition function $T ( O , a )$ determines the result of applying an action a to a state O. When a is a tactic, we assume the underlying proof environment to return a state $O ^ { \prime }$ that results from applying a to O. If a is a “bad” tactic, then ${ \hat { O } } ^ { \prime }$ equals error ; otherwise, $O ^ { \prime }$ is a new set of obligations. We assume that our agent can evaluate $T ( O , a )$ for any state O and action a. While this assumption is unacceptable in many MDP problems, it is reasonable in the theorem-proving setting.

Rewards. As usual, we assume a reward function $R ( O , a )$ that evaluates an action a at a state O. Concretely, we consider rewards of the form $R ( O , a ) { \dot { = } } { \tilde { r } } ,$ , where r˜ is a very high positive value if

$T ( O , a ) = { \tt Q E D }$ , a high negative value if $T ( O , a ) = e r r o r$ , and a small negative value otherwise.   
The small negative reward on the successful execution of the action incentivises smaller proofs.

Histories and Policies. A history of length N is a sequence

$$
h = \langle ( O _ { 0 } , a _ { 0 } , O _ { 0 } ^ { \prime } , r _ { 0 } ) , ( O _ { 1 } , a _ { 1 } , O _ { 1 } ^ { \prime } , r _ { 1 } ) , \dots , ( O _ { N - 1 } , a _ { N - 1 } , O _ { N } ^ { \prime } , r _ { N } ) \rangle
$$

such that $O _ { 0 } = O _ { i n }$ and for all $i , r _ { i } = R ( O _ { i } , a _ { i } )$ and $O _ { i } ^ { \prime } = T ( O _ { i } , a _ { i } )$ . Intuitively, a history records the interactions between the prover agent and the proof environment up to a point of time. We denote by $h _ { i }$ the i-th prefix of h. For example, $h _ { 0 } = \langle \rangle , \dot { h } _ { 1 } = \langle ( O _ { 0 } , a _ { 0 } , O _ { 0 } ^ { \prime } , \dot { r } _ { 0 } ) \rangle$ , and so on.

A policy is a probabilistic function π that maps histories to distributions over pairs $( O , a )$ , where O is a state and a is an action. Intuitively, at each point, the policy determines the next query to make to the proof environment. A policy can have an internal state as well as access to external knowledge (specifically, a lemma database). A trajectory of a policy π is a history h as above such that for each i, ${ \bf P r } [ \pi ( h _ { i } ) = ( O _ { i } , a _ { i } ) ] > 0$ Letting each $r _ { i } = \tilde { r _ { i } }$ , the reward from a trajectory is simply the average $\textstyle { \frac { 1 } { N } } \sum _ { i } { \tilde { r _ { i } } }$ . We define the aggregate reward of π as the expected reward from trajectories sampled from π.

Language Agents. Given our setup, one can naturally pose the problem of reinforcement-learning a policy with optimal aggregate reward. In this paper, we do not take on this problem. Instead, we consider a fixed policy — a wrapper around a pretrained LLM (GPT-4) that can learn in-context — and show that this policy can achieve a high reward. It is this policy that defines our language agent.

## 3 THE COPRA AGENT

A COPRA policy has access to an LLM (in practice, GPT-4) and performs a depth-first search. During the search, it records information about failed actions. It also uses the ⊑ relation over states to checks that it is making progress on the proof.

Figure 3 shows pseudocode for such a policy. The policy maintains a stack of MDP states and a “failure dictionary” Bad that maps a state to a set of actions that are known to be “unproductive” at the state. At each search step, the algorithm pushes the current state on the stack and retrieves external lemmas and definitions relevant to the state. After this, it repeatedly serializes the stack and $B a d ( O )$ into a prompt and feeds it to the LLM. The LLM’s output is parsed into an action, and the agent executes it in the environment.

One outcome of the action could be that the agent arrives at QED. Alternatively, the new state could be an error or represent obligations that are at least as hard as what is currently on the stack (for example, this could be because of a cycle

COPRA(O)   
1 PUSH(st, O)   
2 ρ ← RETRIEVE(O)   
3 for j ← 1 to t   
4 do p ← PROMPTIFY(st, Bad(O), ρ, r)   
5 a ∼ PARSEACTION(LLM(p))   
6 $O ^ { \prime } \gets T ( O , a ) , r \gets \tilde { R } ( O , a )$   
7 if O′ = QED   
8 then terminate successfully   
9 else if O′ = error or   
$\exists O ^ { \prime \prime } \in s t . O ^ { \prime \prime } \subseteq O ^ { \prime }$   
10 then add a to Bad(O)   
11 else COPRA(O′)   
12 POP(st)

Figure 3: The search procedure in COPRA. T is the environment’s transition function and R is the reward function. st is a stack, initialized to be empty. Bad (O) is a set of actions, initialized to ∅, that are known to be bad at O. LLM is an LLM, PROMPTIFY generates a prompt, PARSEACTION parses the output of the LLM into an action (repeatedly querying the LLM in case there are formatting errors in its output), and RETRIEVE gathers relevant lemmas and definitions from an external source. The procedure is initially called with argument $O _ { i n }$

in a tactic). In this case, the agent rejects the new state. Otherwise, it recursively continues the proof from the new state. After issuing a few queries to the LLM, the agent backtracks.

Prompt Serialization Protocol. The routines PROMPTIFY and PARSEACTION together constitute the prompt serialization protocol and are critical to the success of the policy. Now we elaborate on these procedures.

<table><tr><td rowspan=1 colspan=1>Agent PromptState)</td><td rowspan=1 colspan=3>Goals to prove:GOALS]GOAL]1x*x %2 = 0[HYPOTHESES] 1HYPOTHESIS]x:N[HYPOTHESIS] h : x % 2 = 0</td><td rowspan=1 colspan=1>Goals to prove:GOALS]GOAL] 1x % 2 * (x % 2) % 2 = 0[HYPOTHESÉS] 1HYPOTHESIS]xN[HYPOTHESIS] h : x % 2 = 0</td></tr><tr><td rowspan=1 colspan=1>Agent Prompt(Stack)</td><td rowspan=1 colspan=1>[LASTSTEP]intro h,</td><td rowspan=1 colspan=1>[STEPS][STEP] intro h,[LAST STEP]rw h,</td><td rowspan=1 colspan=1>[STEPS][STEP] intro h,[INCORRECT STEPS]STEP] rw h,[LAST STEP]apply nat.mul_mod_right,</td><td rowspan=1 colspan=1>[STEPS][STEP] intro h,[LAST STEP]rw nat.mul_mod,</td></tr><tr><td rowspan=1 colspan=1>Agent Prompt(Reward)</td><td rowspan=1 colspan=1>[SUCCESS]END]</td><td rowspan=1 colspan=1>[ERROR MESSAGE]Got error in &#x27;rw h,&#x27;:error: rewrite tactic failed,did not find instance of thepattern in the targetexpression % 2END</td><td rowspan=1 colspan=1>[ERROR MESSAGE]Got error in &#x27;applynat.mul_mod_right,:error: invalid apply tactic, failedtoounifyxx%2 = 0with&quot;?m_1 *?m_2%?m_1 = 0END]</td><td rowspan=1 colspan=1>[SUCCESS][END]</td></tr><tr><td rowspan=1 colspan=1>↑ Requests #↓Response#</td><td rowspan=1 colspan=1>Seq # 1</td><td rowspan=1 colspan=1>Seq # 2</td><td rowspan=1 colspan=1>Seq # 3</td><td rowspan=1 colspan=1>Seq # 4</td></tr><tr><td rowspan=1 colspan=1>LLMResponse</td><td rowspan=1 colspan=1>[RUNACTIC]rw h,END]</td><td rowspan=1 colspan=1>[RUN TACTIC]apply nat.mul_mod_right,[END]</td><td rowspan=1 colspan=1>[RUN TACTIC]iw nat.mul_mod,END]</td><td rowspan=1 colspan=1>[RUN TACTIC]rw h,ND]</td></tr></table>

Figure 4: We highlight the different parts of the prompts to show how we use the state stack and the execution feedback from the environment. This figure shows the low-level details of the interactions between COPRA and LLM as shown in Figure 1

PROMPTIFY carefully places the different pieces of information relevant to the proof in the prompt. It also includes logic for trimming this information to fit the most relevant parts in the LLM’s context window. Every prompt has two parts: the “system prompt” and the “agent prompt.”

The agent prompts are synthetically generated using a context-free grammar and contain information about the state stack (including the current proof state), the execution feedback for the previous action, and the set of actions we know to avoid at the current proof state.

The system prompt describes the rules of engagement for the LLM. It contains a grammar (distinct from the one for agent prompts) that we expect the LLMs to follow when it proposes a course of action. The grammar carefully incorporates cases when the response is incomplete because of the LLM’s token limits. We parse partial responses to extract the next action using the PARSEACTION routine. PARSEACTION also identifies formatting errors (if any) in the LLM’s responses, possibly communicating with the LLM multiple times until these errors are resolved. Figure 4 shows an example back-and-forth between COPRA and LLM, highlighting the low-level details of the use of state stack, execution feedback from ITP, etc.

## 4 EVALUATION

Our findings about COPRA are that: (i) the approach can find proofs significantly quicker than the state-of-the-art finetuning-based baselines, both in terms of number of LLM queries and wall-clock time; (ii) in problems where all current methods fail, COPRA fails faster; (iii) the use of GPT-4, as opposed to GPT-3.5, within the agent is essential for success; and (iv) backtracking significantly improves the system’s performance on harder problems. Now we elaborate on our experimental methodology and these results.

Implementing COPRA. Our implementation of COPRA can have GPT-3.5, GPT-4, GPT-4-turbo (OpenAI, 2023b) or CodeLlama (Roziere et al., 2023) as the underlying LLM and can interact with both the Lean and the Coq proof environments. Because of the substantial cost of GPT-4 queries, we cap the number of LLM queries that COPRA can make by 60. To further reduce costs, COPRA first tries to prove its theorems in a single LLM query (one-shot prompting), and then it invokes the agent behavior when it fails to find a proof via one-shot prompting. At first, the retrieval mechanism is not used by the agent to keep the prompts smaller and cost-effective, but if the agent fails to find the proofs then retrieval is used to enrich the proof state before prompting the LLM. More details about the setup can be found in Appendix A.1.1.

The “system prompt” in the one-shot approach is slightly different than that for COPRA, containing instructions to generate a proof in one go rather than step by step. For both COPRA and the one-shot baselines, the prompt contains a single proof example that clarifies how proofs need to be formatted. This proof example remains the same for all test cases.

![](images/fbc50f4c69bf9a7329ab47a434f4c04009da1fc0202cbb08a863c5b6a1722ebf.jpg)  
Figure 5: COPRA vs. REPROVER on the miniF2F benchmark

Benchmarks. We evaluate our approach on two domains: (i) miniF2F (Zheng et al., 2021), a collection of 244 Lean formalizations of mathematics competition problems, solved using a range of techniques such as induction, algebraic manipulation, and contradiction; and (ii) a set of Coq problems from the CompCert compiler verification project (Leroy, 2009) that was previously used to evaluate the PROVERBOT9001 system Sanchez-Stern et al. (2020).

Baselines. We compare with one-shot invocations of GPT-3.5 and GPT-4 in both the miniF2F and the Compcert domains. We also consider an ablation of COPRA that uses GPT-3.5 as its LLM and another that does not use backtracking. Additionally, we also consider GPT-4- turbo, and CodeLLama models for miniF2F domain. For the miniF2F dataset, we also have additional baselines

with models like GPT-4-turbo (OpenAI, 2023b) and CodeLlama (Roziere et al., 2023), and ablations with COPRA’s retrieval capabilities disabled. As for fine-tuned baselines, a challenge is that all existing open-source theorem-proving systems only target a single-proof environment. As a result, we had to choose different baselines for the Lean (miniF2F) and Coq (Compcert) domains.

Our fine-tuned baseline for the miniF2F domain is REPROVER, a state-of-the-art open-source prover that is part of the Leandojo project (Yang et al., 2023). We use BM25 search on Lean’s mathlib library for retrieval of relevant lemmas.

In the Compcert domain, we compare with PROVERBOT9001 (Sanchez-Stern et al., 2020), which, while not LLM-based, is the best publicly available model for Coq. Unlike miniF2F, this benchmark comes with a large training set as well as a test set, and we use the training set for retrieving relevant lemmas and definitions. Our retrieval mechanism, in this case, is a simple BM25 search.

![](images/a695aeb5fda813a91394f8392818db5d68eb8bc3dc63fefd71dacac16c7273f1.jpg)  
Figure 6: COPRA vs. PROVER-BOT9001 on the Compcert benchmark.

For cost reasons, our evaluation for Compcert uses 118 out the 501 theorems used in the original evaluation of PROVERBOT9001 Sanchez-Stern et al. (2020). For fairness, we include all the 98 theorems proved by PROVER-BOT9001 in our subset. The remaining theorems are randomly sampled.

Metric: pass@k-guidance-steps. The standard metric for evaluating theorem-provers is pass@k (Lample et al., 2022; Yang et al., 2023). In this metric, a prover is given a budget of k proof attempts; the method is considered successful if one of these attempts leads to success. However, a key objective of our research is to discover proofs quickly, with fewer LLM queries and lower wall-clock time. The pass@k metric does not evaluate this characteristic as it does not quantify the number of LLM queries or amount of time needed by a proof attempt.

Under review as a conference paper at ICLR 2024
<table><tr><td rowspan=1 colspan=1>Approach</td><td rowspan=1 colspan=4># Theoremsproved/# Theorems</td><td rowspan=1 colspan=1>%proved</td><td rowspan=1 colspan=1>Avg.GuidanceStepsin Total</td><td rowspan=1 colspan=3>Avg.GuidanceStepson Failure</td><td rowspan=1 colspan=1>Avg.GuidanceStepson Pass</td></tr><tr><td rowspan=1 colspan=11>miniF2F Test Dataset</td></tr><tr><td rowspan=6 colspan=1>CodeLlama One ShotGPT 3.5 One ShotCOPRA (CodeLlama)GPT 4 One ShotGPT 4-turbo One ShotCOPRA (GPT-3.5) (without retrieval)ReProver (without retrieval)COPRA (GPT-4) (without retrieval)ReProver (with retrieval)ReProver (with retrieval) (official)COPRA (GPT-4-turbo) (with retrieval)</td><td rowspan=1 colspan=4>0/244</td><td rowspan=1 colspan=1>0.0%</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=3>1</td><td rowspan=5 colspan=1>014.78112.45</td></tr><tr><td rowspan=2 colspan=3>7/24414/24426/244</td><td rowspan=1 colspan=1></td><td></td><td rowspan=1 colspan=1>2.8%</td><td rowspan=1 colspan=1>1</td><td rowspan=3 colspan=3>111.9611</td></tr><tr><td rowspan=1 colspan=3></td><td rowspan=1 colspan=1>5.73%10.6%</td><td rowspan=2 colspan=1>11.5511</td></tr><tr><td rowspan=1 colspan=1>29/244</td><td rowspan=1 colspan=3></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>11.88%</td></tr><tr><td rowspan=1 colspan=2>29/244</td><td rowspan=1 colspan=2></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>11.89%</td><td rowspan=1 colspan=1>12.83</td><td rowspan=1 colspan=2>14.23</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=4>54/24457/24461/24467/244</td><td rowspan=1 colspan=1>22.13%23.36%24.9%26.5%27.45%</td><td rowspan=1 colspan=1>350.720.941015.3239.42</td><td rowspan=1 colspan=3>427.2426.791312.8952.67</td><td rowspan=1 colspan=1>81.61.75122.624.41</td></tr><tr><td rowspan=1 colspan=11>CompCert Test Dataset</td></tr><tr><td rowspan=3 colspan=1>GPT 3.5 One-ShotGPT 4 One-ShotProverbotCOPRA (GPT-4)</td><td rowspan=1 colspan=4>10/118</td><td rowspan=1 colspan=1>8.47%</td><td rowspan=2 colspan=1>11</td><td rowspan=3 colspan=3>11256.810.9</td><td rowspan=3 colspan=1>11170.016.57</td></tr><tr><td rowspan=1 colspan=4>36/118</td><td rowspan=1 colspan=1>30.51%</td></tr><tr><td rowspan=1 colspan=4>98/11876/118</td><td rowspan=1 colspan=1>83.05%64.41%</td><td rowspan=1 colspan=1>184.712.9</td></tr></table>

Table 1: Aggregate statistics for COPRA and the baselines on miniF2F and Compcert
<table><tr><td>Approach</td><td colspan="6">Avg. Time In Seconds</td></tr><tr><td></td><td colspan="3">Per Proof</td><td colspan="3">Per Guidance Step</td></tr><tr><td></td><td>On Pass</td><td>On Fail</td><td>All</td><td>On Pass</td><td>On Fail</td><td>All</td></tr><tr><td>ReProver (on CPU) (without retrieval)</td><td>279.19</td><td>618.97</td><td>543.78</td><td>3.42</td><td>1.45</td><td>1.55</td></tr><tr><td>ReProver (on GPU) (without retrieval)</td><td>267.94</td><td>601.35</td><td>520.74</td><td>2.06</td><td>0.44</td><td>0.48</td></tr><tr><td>ReProver (on GPU) (with retrieval)</td><td>301.19</td><td>605.29</td><td>529.27</td><td>2.45</td><td>0.46</td><td>0.52</td></tr><tr><td>COPRA (GPT-3.5)</td><td>39.13</td><td>134.26</td><td>122.21</td><td>15.97</td><td>9.43</td><td>9.53</td></tr><tr><td>COPRA (GPT-4) (without retrieval)</td><td>30.21</td><td>191.73</td><td>140.86</td><td>17.26</td><td>7.16</td><td>6.73</td></tr><tr><td>COPRA (GPT-4-turbo) (with retrieval)</td><td>68.38</td><td>598.66</td><td>450.88</td><td>15.50</td><td>11.36</td><td>11.43</td></tr></table>

Table 2: Average time taken by our approach (COPRA) and ReProver on miniF2F dataset.

To address this concern, we introduce a new metric, pass@k-guidance, and evaluate COPRA and its competitors using this metric. Here, we measure the number of correct proofs that a prover can generate with a budget of k or fewer guidance steps from the LLM or any neural model. For LLMs, one guidance step is a single inference query. One challenge here is that we want this metric to be correlated with the number of correct proofs that the prover produces within a wall-clock time budget; however, the cost of an inference query is proportional to the number of responses generated per query. To maintain the correlation between the number of inference queries and wallclock time, we restrict each inference on LLM to a single response. (more details about the metric is in Appendix A.1.3)

Results Figure 5 shows our comparison results for the miniF2F domain. As we see, COPRA outperforms REPROVER, completing, within just 60 guidance steps, problems that REPROVER could not solve even after a thousand guidance steps. This is remarkable given that COPRA is based on a black-box foundation model and REPROVER was fine-tuned for at least a week on a dataset derived from Lean’s Mathlib library. For fairness, we ran REPROVER multiple times with 16, 32, and 64 (default) as the maximum number of guidance steps per proof step. We obtained the highest success rates with 64 guidance steps.

Figure 6 shows a comparison between COPRA and PROVERBOT9001.
<table><tr><td rowspan=1 colspan=1>Approach</td><td rowspan=1 colspan=1># Theoremsproved/# Theorems</td><td rowspan=1 colspan=1>%proved</td></tr><tr><td rowspan=1 colspan=1>miniF2F</td><td rowspan=1 colspan=2>Test Dataset</td></tr><tr><td rowspan=1 colspan=1>CoPra (GPT-4)w/o backtrackingCOPra (GPT-4)</td><td rowspan=1 colspan=1>56/24457/244</td><td rowspan=1 colspan=1>22.95%23.36%</td></tr><tr><td rowspan=1 colspan=1>CompCert</td><td rowspan=1 colspan=1>Test Dataset</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>COPRa (GPT-4)w/o backtrackingCOPRA (GPT-4)</td><td rowspan=1 colspan=1>52/11876/118</td><td rowspan=1 colspan=1>44.06%64.41%</td></tr></table>

Table 3: Ablation showing the effectiveness of backtracking

We find that COPRA is significantly faster than PROVERBOT9001. Since we put a cap of 60 guidance steps on COPRA, it cannot prove all the theorems that PROVERBOT9001 eventually proves. However, as shown in the figure, COPRA proves many more theorems than PROVERBOT9001 if only 60 guidance steps are allowed. Specifically, we prove 77.5% of the proofs found by PROVERBOT9001 in less than 60 steps.

Aggregate statistics for the two approaches, as well as a comparison with the one-shot GPT-3.5 and GPT-4 baselines (details of baseline setup are mentioned in Appendix A.1.2), appear in Table 1. It is clear from this data that the languageagent approach offers a significant advantage over the one-shot approach. For example, COPRA solves more than twice as many problems as the one-shot GPT-4 baseline, which indicates that it does not just rely on GPT-4 recalling the proof from its memory (we discuss this in more details in Appendix A.1.5). Also, the use of GPT-4 as opposed to GPT-3.5 seems essential.

theorem algebra\_sqineq\_at2malt1   
(a : R) :   
a \* (2 - a) ≤ 1 :=   
begin   
have h : ∀ (x : R), 0 ≤ (1 - x) ˆ 2,   
from λ x, pow\_two\_nonneg (1 - x),   
calc a \* (2 - a)   
= 1 - (1 - a) ˆ 2 : by ring   
... ≤ 1 : sub\_le\_self \_ (h a),   
end  
Figure 7: A theorem in the ‘algebra’ category that CO-PRA could prove but REPROVER could not.

We establish the correlation between the number of guidance steps needed for a proof and wall clock time in Table 2 (more details are discussed in Appendix A.1.4). Although the average time per guidance step is higher for COPRA, COPRA still finds proofs almost 9x faster than REPROVER. This can explained by the fact that our search is more effective as it uses 46x fewer guidance steps than REPROVER. These guidance steps not only contain the average time spent on generating responses from LLM but at times have some contribution corresponding to the execution of the tactic on the Lean environment itself.

Table 2 also offers data on when the different approaches report failures. Since REPROVER uses a timeout for all theorems, we also use a timeout of 10 minutes while considering failures in Table 2. The data indicates that COPRA is comparatively better at giving up when the problem is too hard to solve. We also note that less time is spent per guidance step in case of failure for all approaches.

We show the impact of ablating the backtracking feature of COPRA in Table 3. We note that backtracking has a greater positive impact in the Compcert domain. We hypothesize that this is because the Compcert problems are more complex and backtracking helps more when the proofs are longer.

Finally, we offer an analysis of the different categories of miniF2F problems solved by COPRA and REPROVER in Figure 8. We see that certain kinds of problems, for example, International Mathematics Olympiad (IMO) problems and theorems that require induction, are difficult for all approaches. However, Figure 8b shows that COPRA takes fewer steps consistently across various categories of problems in miniF2F.

From our qualitative analysis, there are certain kinds of problems where the language-agent approach seems especially helpful. For instance, Figure 7 shows a problem in the ‘algebra’ category that REPROVER could not solve. More examples of interesting Coq and Lean proofs that COPRA found appear in the appendix.

## 5 RELATED WORK

Supervised Learning for Theorem-Proving. There is a sizeable literature on search-based theorem-proving techniques based on supervised learning. These methods train a model to predict the next proof step at each point in a proof. This model is then used to guide a search technique, e.g., best-first or depth-limited search, that synthesizes a proof. Earlier methods of this sort used small-scale neural networks (Yang & Deng, 2019; Sanchez-Stern et al., 2020; Huang et al., 2019) as predictors. More recent methods, such as GPT-f (Polu & Sutskever, 2020), PACT (Han et al., 2021), HyperTree Proof Search (Lample et al., 2022), and REPROVER (Yang et al., 2023), have used LLMs. COPRA has some resemblance with the latter approaches. However, it departs from these prior methods in using execution feedback and a more sophisticated search algorithm.

The recent Draft-Sketch-Proof (Jiang et al., 2022) method relies on informal proofs to generate formal proofs. Other methods like Baldur (First et al., 2023) generate the whole proof in one shot using an LLM and then repair it. The main ideas in these efforts — the use of informal proofs and repair models — are orthogonal to our approach (we discuss this in more detail in Appendix A.1.6).

![](images/8795b15f9db071e7ee893eb42e60fe62d328b1dfb942d48eb70613c50cd433a4.jpg)  
(a) Problems solved in different categories

![](images/ed2155e972e0eccd3893441bc646d86a4652e8d2b54d2ebf56015c02db17d785.jpg)  
(b) Number of guidance steps in different categories  
Figure 8: Breakdown of theorems proved in various categories

Reinforcement Learning for Theorem-Proving. Kaliszyk et al. (2018) pioneered the use of RL in theorem-proving; subsequently, Wu et al. (2021) gave TacticZero, a deep RL approach to the problem. TacticZero does not use LLMs, thus missing out on a key source of generic mathematical knowledge. Also, COPRA has retrieval capabilities that TacticZero lacks.

Language Agents. Several distinct LLM agent architectures have been proposed over the last year (Significant-Gravitas, 2023; Yao et al., 2022; Shinn et al., 2023; Wang et al., 2023). These models combine an LLM’s capability to use tools Schick et al. (2023), decompose a task into subtasks (Wei et al., 2022; Yao et al., 2023), and self-reflect (Shinn et al., 2023) However, we are the first to offer an LLM agent for theorem-proving. We also distinguish ourselves from prior work along these lines by introducing a more efficient stateful search in the policy.

## 6 CONCLUSION

We have presented COPRA, the first LLM-agent approach to formal theorem-proving. The approach departs from prior LLM-based theorem-proving techniques by explicitly modeling the interaction between the prover and the proof environment. It also goes beyond prior language-agent approaches for any domain in using a stateful backtracking search within the policy.

Many questions remain open. First, we gave our GPT-4 a budget of a maximum of 60 inferences per problem for cost reasons. Whether the learning dynamics would drastically change with a much larger inference budget remains to be seen. A related question is whether a GPT-4-scale model is truly essential for our task. We have shown that the cheaper GPT-3.5 agent is not competitive against our GPT-4 agent; however, it is possible that a different, more affordable foundation model would have done better. Finally, our proof MDP also enables approaches where an LLM policy is finetuned using RL. It remains to be seen how such an approach, done by necessity with smaller-scale models, would compare with our in-context-learning approach.

## 7 REPRODUCIBILITY STATEMENT

We are releasing all the code needed to run COPRA as supplementary material. The code contains all “system prompts” described in Section A.4 and Section A.3, along with any other relevant data needed to run COPRA. However, to use our code, one must use their own OpenAI API keys. An issue with reproducibility in our setting is that the specific models served via the GPT-4 and GPT-

3.5 APIs may change over time. In our experiments, we set the “temperature” parameter to zero to ensure the LLM outputs are as deterministic as possible.

## REFERENCES

Leonardo de Moura, Soonho Kong, Jeremy Avigad, Floris Van Doorn, and Jakob von Raumer. The Lean theorem prover (system description). In Automated Deduction-CADE-25: 25th International Conference on Automated Deduction, Berlin, Germany, August 1-7, 2015, Proceedings 25, pp. 378–388. Springer, 2015.

Emily First, Markus N Rabe, Talia Ringer, and Yuriy Brun. Baldur: whole-proof generation and repair with large language models. arXiv preprint arXiv:2303.04910, 2023.

Jesse Michael Han, Jason Rute, Yuhuai Wu, Edward W Ayers, and Stanislas Polu. Proof artifact co-training for theorem proving with language models. arXiv preprint arXiv:2102.06203, 2021.

Daniel Huang, Prafulla Dhariwal, Dawn Song, and Ilya Sutskever. Gamepad: A learning environment for theorem proving. In ICLR, 2019.

Gerard Huet, Gilles Kahn, and Christine Paulin-Mohring. The coq proof assistant a tutorial. ´ Rapport Technique, 178, 1997.

Albert Q Jiang, Sean Welleck, Jin Peng Zhou, Wenda Li, Jiacheng Liu, Mateja Jamnik, Timothee´ Lacroix, Yuhuai Wu, and Guillaume Lample. Draft, sketch, and prove: Guiding formal theorem provers with informal proofs. arXiv preprint arXiv:2210.12283, 2022.

Cezary Kaliszyk, Josef Urban, Henryk Michalewski, and Miroslav Olsˇak. Reinforcement learning ´ of theorem proving. Advances in Neural Information Processing Systems, 31, 2018.

Guillaume Lample, Timothee Lacroix, Marie-Anne Lachaux, Aurelien Rodriguez, Amaury Hayat, Thibaut Lavril, Gabriel Ebner, and Xavier Martinet. Hypertree proof search for neural theorem proving. Advances in Neural Information Processing Systems, 35:26337–26349, 2022.

Xavier Leroy. Formal verification of a realistic compiler. Communications of the ACM, 52(7): 107–115, 2009.

Allen Newell, John Clifford Shaw, and Herbert A Simon. Empirical explorations of the logic theory machine: a case study in heuristic. In Papers presented at the February 26-28, 1957, western joint computer conference: Techniques for reliability, pp. 218–230, 1957.

OpenAI. Gpt-4 technical report, 2023a.

OpenAI, 2023b. URL https://platform.openai.com/docs/models/ gpt-4-and-gpt-4-turbo.

Stanislas Polu and Ilya Sutskever. Generative language modeling for automated theorem proving. arXiv preprint arXiv:2009.03393, 2020.

Baptiste Roziere, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, Xiaoqing Ellen Tan, Yossi Adi, Jingyu Liu, Tal Remez, Jer´ emy Rapin, et al. Code llama: Open foundation models for code.´ arXiv preprint arXiv:2308.12950, 2023.

Alex Sanchez-Stern, Yousef Alhessi, Lawrence Saul, and Sorin Lerner. Generating correctness proofs with neural networks. In Proceedings of the 4th ACM SIGPLAN International Workshop on Machine Learning and Programming Languages, pp. 1–10, 2020.

Timo Schick, Jane Dwivedi-Yu, Roberto Dess\`ı, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach themselves to use tools. arXiv preprint arXiv:2302.04761, 2023.

Noah Shinn, Federico Cassano, Beck Labash, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. Reflexion: Language agents with verbal reinforcement learning. arXiv preprint arXiv:2303.11366, 2023.

Significant-Gravitas. Autogpt. https://github.com/Significant-Gravitas/Auto-GPT, 2023.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothee´ Lacroix, Baptiste Roziere, Naman Goyal, Eric Hambro, Faisal Azhar, et al. Llama: Open and\` efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023.

Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima Anandkumar. Voyager: An open-ended embodied agent with large language models. arXiv preprint arXiv:2305.16291, 2023.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou, et al. Chain-of-thought prompting elicits reasoning in large language models. Advances in Neural Information Processing Systems, 35:24824–24837, 2022.

Minchao Wu, Michael Norrish, Christian Walder, and Amir Dezfouli. Tacticzero: Learning to prove theorems from scratch with deep reinforcement learning. Advances in Neural Information Processing Systems, 34:9330–9342, 2021.

Kaiyu Yang and Jia Deng. Learning to prove theorems via interacting with proof assistants. In International Conference on Machine Learning, pp. 6984–6994. PMLR, 2019.

Kaiyu Yang, Aidan M Swope, Alex Gu, Rahul Chalamala, Peiyang Song, Shixing Yu, Saad Godil, Ryan Prenger, and Anima Anandkumar. Leandojo: Theorem proving with retrieval-augmented language models. arXiv preprint arXiv:2306.15626, 2023.

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629, 2022.

Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L Griffiths, Yuan Cao, and Karthik Narasimhan. Tree of thoughts: Deliberate problem solving with large language models. arXiv preprint arXiv:2305.10601, 2023.

Kunhao Zheng, Jesse Michael Han, and Stanislas Polu. Minif2f: a cross-system benchmark for formal olympiad-level mathematics. arXiv preprint arXiv:2109.00110, 2021.

## A APPENDIX

## CONTENTS

A.1 Evaluation Details . . 12   
A.1.1 COPRA Implementation Setup Details 12   
A.1.2 One-shot Baseline Setup Details 12   
A.1.3 Metric: pass@k-guidance-steps 12   
A.1.4 pass@k-guidance-steps versus wall-clock time 13   
A.1.5 Data Leakage in GPT-4 . 13   
A.1.6 Comparison with methods using informal proofs 14   
A.2 Example Proofs generated For miniF2F 15   
A.3 System Prompts For miniF2F . 15   
A.4 System Prompts For CompCert . 19   
A.5 Example Proofs generated For CompCert 19

Under review as a conference paper at ICLR 2024
<table><tr><td>Approach</td><td># Theorems proved /# Theorems</td><td>% proved</td><td>Avg. Guidance Steps in Total</td><td>Avg. Guidance Steps on Failure</td><td>Avg. Guidance Steps on Pass</td></tr><tr><td colspan="6">miniF2F Test Dataset</td></tr><tr><td>GPT 4-turbo One Shot</td><td>29/244</td><td>11.88%</td><td>1</td><td>1</td><td>1</td></tr><tr><td>COPRA (GPT-4-turbo) (agent + retrieval)</td><td>56/244</td><td>22.95%</td><td>18.75</td><td>23.63</td><td>2.35</td></tr><tr><td>CoPRA (GPT-4-turbo) (agent)</td><td>60/244</td><td>24.59%</td><td>21.64</td><td>27.47</td><td>3.76</td></tr><tr><td>COPRA (GPT-4-turbo) (agent + one-shot)</td><td>62/244</td><td>25.40%</td><td>22.58</td><td>28.57</td><td>3.70</td></tr><tr><td>COPRA (GPT-4-turbo) (agent + one-shot + retrieval)</td><td>67/244</td><td>27.45%</td><td>39.42</td><td>52.67</td><td>4.41</td></tr></table>

Table 4: Aggregate statistics for COPRA capabilities and COPRA ensemble on miniF2F

## A.1 EVALUATION DETAILS

## A.1.1 COPRA IMPLEMENTATION SETUP DETAILS

We introduce a common proof environment for COPRA, which can also be used by any other approach for theorem proving. The proof environment is agnostic of language and domain, having a common interface that makes COPRA work seamlessly for both Lean and Coq. As per our knowledge, this is the first language and domain-agnostic interface that can allow training or testing of various neural theorem-proving approaches. In the future, we plan to support more proof languages. We also have support for various LLMs other than GPTs, including open LLMs like Llama 2 (Touvron et al., 2023), Code Llama (Roziere et al., 2023), etc. All the theorems are searched within a timeout of 10 minutes and with a maximum of 60 LLM inference calls (whichever exhausts first). To make it comparable across various LLMs, only one response is generated for one inference. All these responses are generated with the temperature set to zero, which ensures that the responses generated are more deterministic, focussed, and comparable.

We use GPT-3.5, GPT-4, GPT-4-turbo (OpenAI, 2023b), and CodeLLama (Roziere et al., 2023) to test the capabilities of COPRA. We find that it is best to use COPRA’s different capabilities in an ensemble, which makes it not only more accurate but enhances its performance. Therefore, we first use one-shot prompting to find the proof, then we use COPRA without retrieval upon failure and then run COPRA with retrieval only when we fail again. To ensure fairness in comparison, we make sure that the number of guidance steps is capped at 60 and the 10-minute timeout is spread across all these three executions. From Table 4, it is clear that despite the significant overlap between the three executions, the ensemble covers more cases. One possible reason could be that the addition of extra information from retrieval can sometimes be misleading because the retriever is not perfect and it can find lemmas that are not completely relevant to proving the goal. Nevertheless, sometimes these extra lemmas are handy, so we can best use the different capabilities as an ensemble.

## A.1.2 ONE-SHOT BASELINE SETUP DETAILS

We run the one-shot GPT-4 baseline by calling the LLM exactly once. Additional queries are only used when the response is incomplete or ill-formatted. To ensure a fair comparison of one-shot baseline with GPT-4 COPRA agent with 60 inference calls allowed, we always set the temperature parameter as zero for all LLM queries.

## A.1.3 METRIC: pass@k-guidance-steps

The main motivation behind the pass@k-guidance-steps is to assess the speed of the proposed approach and the effectiveness of the LLM or neural network to guide the proof search. It is a reasonable metric because it does a more even-handed trade-off in accounting for the time taken to complete a proof and at the same time ignores very low-level hardware details.

Different approaches need a different amount of guidance from a neural model to find the right proof. For example, approaches like Baldur (First et al., 2023), DSP (Jiang et al., 2022), etc., generate the whole proof all at once. On the other hand, GPT-f (Polu & Sutskever, 2020), PACT (Han et al., 2021), REPROVER (Yang et al., 2023), Proverbot (Sanchez-Stern et al., 2020), or our approach generate the proofs step by step. We argue that pass@k-guidance-steps is a fairer metric to compare these different types of approaches because it correlates with the effectiveness of the proof-finding algorithm in an implementation-agnostic way. Since the exact time might not always be a good reflection of the effectiveness because of hardware differences, network throttling, etc., it makes sense to not compare directly on metrics like pass@k-minutes or pass@k-seconds. Not only these metrics will be brittle and very sensitive to the size, hardware, and other implementation details of the model, but not every search implementation will be based on a timeout. For example, Proverbot does not use timeout-based search (and hence we don’t compare on the basis of time with Proverbot9001).

![](images/b0838f551dc2cf640b1185735c8a4df604c304805c20c408f33d8b73b8b3678e.jpg)  
Figure 9: COPRA vs. REPROVER on the miniF2F benchmark

## A.1.4 pass@k-guidance-steps VERSUS WALL-CLOCK TIME

We show that pass@k-guidance, correlates very well with wall-clock time for finding proofs by using the metric pass@k-seconds. pass@k-seconds measures the number of proofs that an approach can find in less than k seconds. The plot in Figure 9 shows that pass@k-seconds follows the same trend as pass@k-guidance-steps as shown in Figure 5.

We can use the comparison of COPRA with REPROVER (Yang et al., 2023) on the miniF2F dataset to explain the correlation between finding proofs fast and pass@k-guidance-steps. From Table 2, we know that on average the time taken per guidance (which includes time taken to execute the proof steps on ITP as well) is around 1.55 seconds for REPROVER and 6.73 seconds for COPRA. Given that REPROVER’s guidance LLM is small, we can assume that REPROVER doesn’t take any time (zero time) to query its LLM and spends most of the 1.55 seconds running the proof steps on ITP. Now, we can reasonably estimate GPT-4 average response time to be 5 seconds (6.73 - 1.55) from Table 2. However, we see that the number of guidance used by REPROVER is about 46x higher on success. This interestingly shows up in the wall clock time too which is around 9x higher ( 46x/5) for REPROVER on success, so there is a tradeoff between the two, but the number of guidance steps dominates when the guidance model is not good. So, if the guidance model is good (it may be as big as GPT), we can empirically argue that asymptotically the search will converge to proof faster (given that it can be found using that guidance model).

## A.1.5 DATA LEAKAGE IN GPT-4

With LLM pretraining data getting larger and larger, it is hard to know if there is any accidental leakage of the evaluation set in the training data of the LLM itself. The data leakage problem is applicable to all generative AI approaches based on large pretrained models, whose pretraining data is rarely publicly accessible. For coding and language generation tasks, which have been studied in more depth, the use of large pretrained LLMs has now become standard, simply because the benefits of scale are simply too significant to ignore. We believe that AI-for-math is also taking a similar trajectory.

Data leakages can be direct or indirect hints to solve the evaluation set. Even with open LLMs like Llama (Touvron et al., 2023), it is computationally hard to detect these hints in the pertaining data given the LLMs are trained on trillions of tokens. However, after a thorough analysis of the proofs generated by COPRA on the miniF2F dataset, we can safely conclude that data leakage isn’t a significant contributor to our results, for several reasons.

First, we note that COPRA significantly outperforms one-shot invocations of GPT-4. If the results on COPRA were significantly tainted by data leakage, we would have expected better performance from one-shot GPT-4.

Second, not all the formal proofs of the miniF2F test dataset are available online (only 80 proofs are available in Lean). It is highly unlikely that GPT-4 has been trained on proof-state and tactic pair generated by hooking up the Lean Interactive Theorem Prover (ITP). Moreover, since the ground truth of miniF2F test for Lean is still not available, even if it were trained on proof-states one still needs to manually annotate ground truth tactics. Given that GPT-4 is a general-purpose LLM, it is highly unlikely that while training GPT-4 the miniF2F dataset was first manually annotated, and then proof-state and tactic pair information was collected by hooking up the Lean ITP.

Also, in our agent interactions, we limit ourselves only to the goal at that point. There is no mention of the original theorem anywhere (except for the very first proof-state), so the chances that GPT-4 can correlate any intermediate state with the original theorem are very low unless it can somehow manage to simulate Lean’s interactive theorem proving within itself. It is also improbable that GPT-4 has seen the proof-state in the same format that we use, let alone using the execution feedback which has not been used in any known previous works.

One could hypothesize that some of the one-shot GPT-4 proofs might be influenced by potential training on the miniF2F dataset. However, this doesn’t seem to be true because we see that most of the proofs we generated were either not mentioned in the miniF2F test dataset or completely different from the manually written proofs in the miniF2F test dataset (including the first step mismatch). Table 5 shows the detailed analysis of proofs generated by COPRA and the proofs mentioned in miniF 2F test dataset for Lean. From the Table 5, it is clear that most of the proofs generated by COPRA are different from the proofs mentioned in the miniF 2F . The ones that are exactly the same are simple single-tactic proofs that just use exactly one of the linarith, nlinarith, or norm num tactics without any arguments. If we set aside these straightforward simple cases, then about 92% of the proofs generated by COPRA are either different from the proofs mentioned in the miniF2F or do not have a proof mentioned in the miniF2F dataset. Out of all proofs generated by COPRA about 25.37% proofs are for theorems that have no proofs mentioned in the miniF2F test dataset as compared to 22.95% for REPROVER. Some of the proofs generated by our approach as compared to proofs mentioned in the miniF2F test dataset are shown in Figure 10.

Finally, the ability of agent interactions to enhance the basic LLM approach seems to transcend OpenAI’s LLMs. We ran COPRA on the recently released CodeLLama LLM. From Table 1, CO-PRA improved CodeLlama’s capabilities to prove theorems by about 5% on miniF2F dataset. This indicates that the in-context learning capabilities that we build are transferable and LLM-agnostic.

## A.1.6 COMPARISON WITH METHODS USING INFORMAL PROOFS

A formal proof is something that can be automatically verified using an Interactive Theorem Prover (ITP), whereas an informal proof can only be verified by a human. ITP is a software tool to assist with the development of formal proofs by human-machine collaboration. This involves some sort of interactive proof editor, or other interfaces, with which a human can guide the search for proofs. Often formal proofs are much more rigorous and pedantic than informal proofs. So informal proof can be loosely considered as a proof sketch based on which one can write rigorous machine-checkable formal proofs.

Methods that use DSP (Jiang et al., 2022) pipeline that uses informal proofs to find the formal proofs work very well on datasets like miniF2F which have problems from math competitions. However, real-world math formulations are not necessarily math competition problems with well known informal proofs. Certain domains like software verification like CompCert don’t have any notion of informal proofs. It is important to note that having access to informal proofs (humanwritten or LLM-generated) simplifies the problem of synthesizing the formal proof into more of a translation problem, and that is one of the reasons why DSP-like approaches perform well on miniF2F dataset. These approaches will work very well if the LLM can use its memory component to effectively recall the informal proof of a well-known math competition problem. However, a lot of formal theorem proving happens on a completely new set of formalizations which are heavily customized depending on the domain. For example, in the field of software verification, we will have a custom mathematical model defined for the software which has no informal proofs or definitions which can be recalled from memory by the LLMs. It is also important to note that the accuracy numbers in (Jiang et al., 2022) are not directly comparable to ours because they use different proof languages. Isabelle is used in DSP-like approaches which have powerful automatic reasoning tools like Sledgehammer, unlike Lean.

<table><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=6>ProofsinminiF2F</td><td rowspan=1 colspan=1>ProofsNOT inminiF2F</td><td rowspan=1 colspan=1>Total</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=3>Single-TacticSimple Proofs</td><td rowspan=1 colspan=1>Two-TacticProofs</td><td rowspan=1 colspan=1>LongerComplexProofs</td><td rowspan=1 colspan=1>Total</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Tactics UsedProof Count</td><td rowspan=1 colspan=1>linarith</td><td rowspan=1 colspan=1>norm_num</td><td rowspan=1 colspan=1>nlinarith</td><td rowspan=1 colspan=1>two tactics</td><td rowspan=1 colspan=1>&gt; 2 tacticsOR1 tacticmulti-args</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>sorry</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>miniF2FProofCount</td><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>16</td><td rowspan=1 colspan=1>39</td><td rowspan=1 colspan=1>80</td><td rowspan=1 colspan=1>164</td><td rowspan=1 colspan=1>244</td></tr><tr><td rowspan=1 colspan=1>ExactMatchCOPRACount</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>21</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>21</td></tr><tr><td rowspan=1 colspan=1>1st TacticMatchCOpPRACount</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>25</td></tr><tr><td rowspan=1 colspan=1>DistinctCOPRACount</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>29</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>46 / 6768.65%</td></tr><tr><td rowspan=1 colspan=1>DistinctCOPRACountexSingle-Tactic</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>29</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>46 / 5092%</td></tr><tr><td rowspan=1 colspan=1>AllCOPRACount</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1>17</td><td rowspan=1 colspan=1>67</td></tr></table>

Table 5: Analysis of proof generated by COPRA on miniF2F test dataset for Lean.

Our approach is generic and can work for any domain where formal theorem proving is used. It is one of the first methods which is domain and proof language agnostic.

## A.2 EXAMPLE PROOFS GENERATED FOR MINIF2F

Fig. 11 shows some other interesting proofs generated by our approach on miniF2F dataset.

## A.3 SYSTEM PROMPTS FOR MINIF2F

Parts of the ‘system prompt’ used by COPRA for theorem proving in Lean are shown in Fig. 12.

(a.1)   
theorem algebra\_sqineq\_at2malt1 (a.2)   
(a : R) : theorem algebra\_sqineq\_at2malt1   
a \* (2 - a) ≤ 1 := (a : R) :   
begin a \* (2 - a) ≤ 1 :=   
suffices: 0 ≤ aˆ2 - 2\*a + 1, nlinarith, begin   
suffices: 0 ≤ (a - 1)ˆ2, nlinarith,   
nlinarith, -- We will complete the square to   
end show that the expression is at most   
1.   
(b.1) have h : a \* (2 - a) = 1 - (1 - a)ˆ2,   
theorem mathd\_algebra\_270 { ring },   
(f : R → R) rw h,   
(h0 : ∀ x ̸= -2, f x = 1 / (x + 2)) : -- Now we show that (1 - a)ˆ2 is non  
f (f 1) = 3/7 := negative, which implies 1 - (1 - a)ˆ2   
begin is at most 1.   
rw [h0, h0], apply sub\_le\_self,   
norm\_num, apply pow\_two\_nonneg,   
linarith, end   
rw h0, (b.2)   
norm\_num,   
linarith, theorem mathd\_algebra\_270   
end (f : R → R)   
(h : ∀ x ̸= -2, f x = 1 / (x + 2)) :   
(c.1) f (f 1) = 3/7 :=   
theorem mathd\_numbertheory\_229 : begin   
(5ˆ30) % 7 = 1 := have h1 : f 1 = 1 / (1 + 2) := h0 1 (   
begin by linarith),   
have five\_to\_thirty\_is\_one : rw h1,   
(5ˆ30 : zmod 7) = 1 := rw h0,   
begin field\_simp,   
have five\_to\_the\_six\_is\_one : (5ˆ6 : ring,   
zmod 7) = 1, by dec\_trivial, apply ne\_of\_gt,   
have break\_power : (5ˆ30 : zmod 7) = norm\_num,   
(5ˆ6)ˆ5, by norm\_num, end   
rw break\_power, (c.2)   
rw five\_to\_the\_six\_is\_one,   
norm\_num, theorem mathd\_numbertheory\_229 :   
end, (5ˆ30) % 7 = 1 :=   
change 5ˆ30 ≡ 1 [MOD 7], begin   
rw ←zmod.eq\_iff\_modeq\_nat, norm\_num,   
exact\_mod\_cast five\_to\_thirty\_is\_one, end   
end  
Figure 10: Some proofs found by COPRA as compared to the proofs mentioned in the miniF2F test dataset. It is interesting to see that the proofs generated by COPRA are different from the proofs mentioned in the repository. This is especially true when the proofs are longer. It is also worth noting that occasionally COPRA can find very simple proofs for longer proofs mentioned in miniF2F test dataset. (a.1), (b.1), and (c.1) show the proofs as mentioned in the miniF2F dataset, while (a.2), (b.2), and (c.2) show the corresponding proofs generated by COPRA.

```julia
(a)
(c)
theorem
mathd_algebra_246 theorem mathd_algebra_44 (e)
(a b : R) (s t : R)
(f : R → R) $( { \mathsf { h } } _ { 0 } ~ : ~ { \mathsf { s } } ~ = ~ 9 ~ - ~ 2 ~ \star ~ { \mathsf { t } } )$ theorem mathd_algebra_107
(h0 : ∀ x, f x = a * xˆ4 (h1 : t = 3 * s + 1) : (x y : R)
- b * xˆ2 + x + 5) s = 1 ∧ t = 4 := $( \ln _ { 0 } ^ { - } : \times ^ { - } 2 + 8 \star x + y ^ { - } 2 - 6 x$
(h2 : f (-3) = 2) : begin $y ~ = ~ 0 )$
f 3 = 8 := split, $( x + 4 ) \div 2 + ( y - 3 ) \div 2 = 5 \div 2 : =$
begin { begin
rw h0, rw h0 at h1, rw pow_two at h0,
rw h0 at ${ \mathsf { h } } _ { 2 } ,$ linarith rw add_assoc at h ,
$\mathsf { r i n g \_ n f } ,$ $\} ,$ rw add_comm (x * x) (8 *
linarith, rw h0 at h1, x + y ˆ 2) at h0,
end rw h1 at h0, rw add_comm (8 * x) (y ˆ
linarith, 2) at h0,
(b) end rw add_assoc at h0,
theorem (d) rw add_comm (y ˆ 2) (8 *x + x * x) at h ,
(n : N) theorem amc12b_2002_p2 rw add_assoc at h0,
(h : (3 * n) % 2 = 11) (x : Z) ring_nf at h0,
: (h0 : x = 4) : rw pow_two,
n % 11 = 8 := (3 * x - 2) * (4 * x + rw pow_two,
begin $1 ) \texttt { - } ( 3 \texttt { + x - } 2 )$ ring_nf,
cases (nat. (4 * x) + 1 = 11 := rw ←add_assoc,
mod_two_eq_zero_or_one begin rw h0,
(3 * n)), ring_nf, linarith,
exfalso, rw h0, end
linarith, ring,
linarith, end
end
```  
Figure 11: Some other interesting proofs generated for miniF2F by COPRA. The length of the proofs generated shows that interaction with the environment helps in fixing the errors encountered while writing long proofs. These long sequences of rewrites are not easy to synthesize without knowing the exact execution feedback from the environment which often contains the hint to fix the rewrites.

![](images/f354e77cfdd6779c40d302c698df2662ecbee7007085b21cab84d2be0651ad54.jpg)  
Figure 12: Parts of ‘system prompt’ used by COPRA for Lean

## A.4 SYSTEM PROMPTS FOR COMPCERT

Parts of the ‘system prompt’ used by COPRA for theorem proving in Coq are shown in Fig. 13.

## A.5 EXAMPLE PROOFS GENERATED FOR COMPCERT

Fig. 14 shows some interesting proofs generated by our approach on the CompCert dataset.

![](images/eb610c506d8f7ff4519c8d1c2ca91eb54e9b8566b6473ae081c5c42869bf72e1.jpg)  
Figure 13: Parts of ‘system prompt’ used by COPRA for Coq

(a)   
gss :   
forall l v m,   
(set l v m) l = match l with R (c)   
,→ r => disjoint\_cons\_right   
v | S sl ofs ty => ,→ : (e)   
Val.load\_result forall a l1 l2,   
set\_locals\_lessdef   
,→ (chunk\_of\_type ty) v,→ end. disjoint l1 (a :: l2) -> disjoint,→ ,→ e2, : forall e1   
Proof. intros l v m.destruct l as [r | s o t]. Proof. l1 l2.,→ ,→ ,→ env\_lessdef e1 e2 -> il, forall   
- unfold set. ,→ H. ,→ env\_lessdef   
destruct (Loc.eq (R r) (R unfold   
,→ (set\_locals il   
r)); [reflexivity |,→ ,→ disjoint. ,→ e1)   
,→ contradiction]. intros x1 x2 H1 → (set\_locals il   
- unfold set. ,→ H2.   
,→ e2).   
destruct (Loc.eq (S s o t) apply H. Proof.   
(S s o t));,→ assumption. intros e1 e2 H.   
,→ [reflexivity right. induction il as   
,→ contradiction]. assumption. ,→ [| a il'].   
Qed. Qed. - apply H.   
(b) (d) - intros.   
eq : forall (p q: loc), {p = eq\_int\_type : apply   
,→ q} + {p <> q}. ,→ forall (x y: ,→ set\_var\_lessdef.   
Proof. int\_type),,→ apply IHil'.   
decide equality. ,→ {x=y} + {x<>y}. apply   
- apply mreg\_eq. Proof. ,→ Val.lessdef\_refl.   
- decide equality. decide Qed.   
- decide equality. ,→ equality.   
apply Pos.eq\_dec. Qed.   
decide equality.   
- decide equality.   
Qed.  
Figure 14: Some other interesting proofs generated for CompCert by COPRA. We can see that these proofs are long, and often use ‘apply’ tactic which shows that COPRA can effectively use the retrieved information to discharge the current proof state.
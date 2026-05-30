# A Language-Agent Approach to Formal Theorem-Proving

OpenReview ID: XCMbagV0No
Decision: Reject

## Abstract
Language agents, which use a large language model (LLM) capable of in-context learning to interact with an external environment, have emerged as a promising approach to control tasks. We present a language-agent approach that offers state-of-the-art performance in formal theorem-proving. Our method, COPRA, uses a high-capacity, black-box LLM (GPT-4) as part of a policy for a stateful backtracking search. During the search, the policy can select proof tactics and retrieve lemmas and definitions from an external database. Each selected tactic is executed in the underlying proof framework, and the execution feedback is used to build the prompt for the next policy invocation. The search also tracks selected information from its history and uses it to reduce hallucinations and unnecessary LLM queries.

We evaluate COPRA on the miniF2F benchmark for Lean and a set of Coq tasks from the Compcert project. On these benchmarks, COPRA is significantly better than one-shot invocations of GPT-4, as well as state-of-the-art models fine-tuned on proof data, at finding correct proofs quickly.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper introduces COPRA, an approach to theorem proving that uses off-the-shelf, high-capacity LLM (GPT-4 in this case) as part of a policy that interacts with a proof environment. 
At each step, the policy consumes a textual prompt by using the underlying proof assistant, or backtrack, or retrieve relevant lemmas and definitions from an external corpus. 
The feedback from the execution is used toconstruct a new prompt for the policy, and the process reiterates.
The proposed approach is evaluated empirically.

#### Strengths
1) The problem is rigorously formalised as a Markov decision process in reinforcement learning. 

2) The proposed approach compares favourably wrt the state of the art, but the differences between the different baselines make the comparison a bit opaque.

#### Weaknesses
1) The problem is formalised as an RL task, but then the authors say "In this paper, we do not take on this problem. Instead, we consider a fixed policy - a wrapper around a pretrained LLM (GPT-4) that can learn in-context - and show that this policy can achieve a high reward".
See question below.

2) The structure of the framework proposed is not very clear. The algorithm in Fig. 3 is quite high-level. The calls and interactions with the LLMs are not discussed in much detail.

3) on p. 9, the authors say: "However, [COPRA] departs from these prior methods in using execution feedback and a more sophisticated search algorithm."
It is not clear to me what this more sophisticate search algorithm is, specifically why it is sophisticate.

#### Questions
1) Why defining the problem as an RL task, if this is not used in the methodology proposed?

2) What is sophisticate about the search algorithm used in COPRA?

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper introduces COPRA, a language-agent framework that leverages the LLM GPT-4 for state-of-the-art performance in formal theorem-proving tasks. COPRA employs GPT-4 within a policy guiding a stateful backtracking search, where it selects proof tactics and retrieves relevant lemmas and definitions from an external database. The agent executes each tactic within a proof framework, using feedback to refine subsequent prompts, thus improving the decision-making process. Additionally, the system intelligently tracks search history to minimize errors and redundant queries to the language model. The experiments on two datasets verify the effectiveness of the proposed COPRA.

#### Strengths
1. The paper is well organized with good language.
2. The addressed problem is interesting because it is a practical application of LLM. 
3. The authors ensure the reproducibility of COPRA by providing detailed implementation details.

#### Weaknesses
1. The method 'Decomposing the Enigma' [1], released in May 2023, appears to outperform COPRA on the miniF2F dataset, with a pass rate of 45.5% compared to COPRA's 23.36% [1]. More notably, 'Decomposing the Enigma' [1] achieves this using only ChatGPT-3.5, which raises questions about COPRA's claim to being 'state of the art.' Furthermore, COPRA's performance falls short when compared to Proverbot on the CompCert dataset.

2. It is unfair to compare the number of inferences made with REPROVER in Figure 5, as COPRA utilizes GPT-4 to prove theorems, while REPROVER employs a much smaller LLM. One query from GPT-4 is far more powerful than a single inference from REPROVER's LLM.

3. The authors seem to overstate their claim of having 'the first LLM-agent approach' with 'state-of-the-art' performance.

[1] Zhao, Xueliang, Wenda Li, and Lingpeng Kong. "Decomposing the Enigma: Subgoal-based Demonstration Learning for Formal Theorem Proving." arXiv preprint arXiv:2305.16366 (2023).

#### Questions
1. Can you explain the performance gap mentioned in point 1 of the weaknesses?

2. Why does GPT-3.5 perform better than GPT-4 as indicated in Table 2? Does this suggest that there might be overfitting of prompts for different LLMs?

3. How can it be verified that theorems are proved sufficiently?

4. Why is COPRA claimed to be "the first LLM-agent approach to formal theorem-proving" when previous works like REPROVER and Decomposing the Enigma [1] might also be considered as LLM-agent approaches?

5. The reference page should begin on a new page (page 10).

6. What is the average API cost for COPRA per proven theorem? 




[1] Zhao, Xueliang, Wenda Li, and Lingpeng Kong. "Decomposing the Enigma: Subgoal-based Demonstration Learning for Formal Theorem Proving." arXiv preprint arXiv:2305.16366 (2023).

### Review 3
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper introduces COPRA, a language-agent approach that prompts a large language model (LLM), specifically GPT-4, for formal theorem-proving. COPRA enhances the theorem-proving process by employing a stateful backtracking  policy search using language model. In particular, during the search, the policy selects proof tactics and retrieves essential information such as lemmas and definitions from an external database. Execution feedback and historical search data are then prompted again for policy update.  The authors tested COPRA on benchmarks like miniF2F and Coq tasks.

#### Strengths
Formal theorem proving is a less explored application domain. This paper provides positive results for such an application.

#### Weaknesses
1. Novelty. It seems that the method is similar to retrieval-based LLM in the sense that the policy uses an external database. It would be great if the authors could compare with this line of works in detail, especially the ReProver paper. 

2. It seems that the proposed method does not significantly outperform ReProver. 

3. Ablation studies might be needed to understand the role played by the RL component.

#### Questions
1. Is there a difference between formal and informal theorem proving? It seems that there are some recent works that this work (LYRA: ORCHESTRATING DUAL CORRECTION IN AUTOMATED THEOREM PROVING) has a much higher score on miniF2F. 

2. What is the role played by the RL part? I understand that you formulate the problem as an MDP and then the language-agent essentially mimics an RL algorithm. What is this particular RL algorithm? How to handle exploration-exploitation tradeoff?

3. Is RL really essential here? Can you replace it with other planning methods such as tree search, or even a close-loop planning method such as ReAct?

### Review 4
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The paper attacks the problem of tactic based theorem proving. Given a starting (goal,hypothesis) pair, we use *lean* to apply a *tactic* to it. This either yields a set of new goals, all of which need to be proved, or an error, or it directly proves the goal. The new set of goals are then handled recursively.

The paper proposes to choose the tactics by prompting an llm, and to embed this in a search algorithm which effectively does back tracking. The llm prompt includes *execution feedback* allowing the llm to improve on earlier failures. 

The search is also guided by a way of pruning sets of (goal,hypothesis) pairs that are strictly harder to prove than existing ones.

More detailed comments:

Section 1

Some of the text in fig 1 is too small / blurry.

Sec 2.

The use of Sanchez-Stern's pruning method is cool.

It seems highly restrictive to only allow the model to choose tactics. Why not use prompting to ask the model the most promising partial prove to attack next?

The discussion of *Rewards* and *Histories and Policies* seems confusing and maybe erroneous. Detailed questions around that:
- Why are both scalar rewards and text feedbacks formalised as part of the reward ? How does this compare to traditional RL / MDP setups? Why the departure from that?
- Where is the scalar reward actually used? Apologies if I missed it but I couldn't quite see where the $r_i$ are used by the algorithm.
- What is the point of the sentence "A trajectory of a policy $\pi$ is a history ... ? 

The use of execution feedback is nice, and it is nice to see this idea brought into theorem proving. The literature for program synthesis and other areas could be mentioned apropos this.

Seciton 3

Please fix the indentation of the pseudo-code in Fig. 3.

Fig. 4 was appreciated and seems helpful but it is slightly confusing in the current form ... Is this entire protocol repeated up to $k$ times, or is this all within one value of $j$ in your pseudo-code?

Section 4

End of page 5: including one shot prompting in copra dilutes what we can say about the method. Why not include an ablation where you only do the search, no one shot?

I'm not sure about removing ReProver's retrieval mechanism, could this not be done similarly to them? The code is available, and the agent system mentions a Lemma repository, which should be crucial to their model.

If you could integrate the lemma/retriever for MiniF2F the results should be even stronger, not sure why this couldn't be done, the explanation was unclear since you can access ReProver's code for MiniF2F and get the set of relevant premises from there (even just using BM25).

General comment: the results look fishy. I suspect GPT was trained on these datasets, and this would make all of the absolute comparisons with other methods hard to interpret. Please convince me otherwise. The passage on page 7 with paragraph heading "results" also strongly indicates this.

Pass @ k inferences is not intuitive to me:
-  why not use pass @ k tactic applications ? isn't this the main bottleneck? As it is structured, since each inference is restricted to a single response, they are essentially the same in this setup, but I think it's worth emphasising you are mostly restricted by the environment.
- doesn't this make the comparisons unfair also because GPT is more expensive than the other models (i.e. your Fig 6 x-axis is not comparable)? in the pass @ k inferences, why not use wall clock time then ?

Looking closely at Fig 6, why does proverbot have y value > 0 at x value = 0 ? 

General comment: if we discount the absolute comparisons since GPT may have seen these datasets, how can we answer the research question "does the search strategy work". It seems like what might be missing is an answer to the questions "how does running Copra with k = 1 repeatedly with i.i.d. sampling of the LLM compare to copra with k > 1, normalised for number of tactic applications?". 

In table 3:
- how does the "w/o backtracking" work, precisely?
- are these numbers comparable in terms of computational work? e.g. with number of tactic calls held constant?

Typos

- Page 7 typo (correlated [with the] number of correct proofs..)
- Typo in results (if only 60 inferences [are] allowed)

#### Strengths
See the summary.

#### Weaknesses
See the summary.

#### Questions
Can you address the concerns? I like the paper and want to raise the score, but it feels like it might not be ready yet, if those concerns can't be reasonably addressed.

## Meta Reviews

### Meta Review 1
This paper considers theorem proving as a reinforcement learning problem here a proof is viewed as a sequence of actions that either close the proof (succeed) or fail.  The standard metric of pass@k used to evaluate automated provers os modified to pass@q where q is the number of calls to an LLM to propose a next action.

This paper got four ratings of 5.  I expect I would have rated it higher on the grounds that the use of LLMs. A main complaint of the reviewers is that the performance seems to be worse or equivalent to other systems.  The paper is using a new metric of pass@q which makes comparisons hard.  But they should have made an attempt to evaluate pass@k for comparison purposes.

## Decisions

Decision: Reject

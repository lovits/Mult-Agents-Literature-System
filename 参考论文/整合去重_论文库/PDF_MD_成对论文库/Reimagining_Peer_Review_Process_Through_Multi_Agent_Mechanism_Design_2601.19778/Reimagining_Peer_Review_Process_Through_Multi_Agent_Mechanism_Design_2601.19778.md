---
pdf: Reimagining_Peer_Review_Process_Through_Multi_Agent_Mechanism_Design_2601.19778.pdf
source: MinerU API
batch_id: d6e8dbb5-b049-4ed8-8c56-40ee66b039f6
data_id: Reimagining_Peer_Review_Process_Through_Multi_Agent_Mechanism_Design_2601.19778
parsed_at: 2026-05-23
---

# Reimagining Peer Review Process Through Multi-Agent Mechanism Design

Ahmad Farooq

University of Arkansas at Little Rock

Little Rock, Arkansas, USA

afarooq@ualr.edu

ORCID: 0009-0002-3684-5876

Kamran Iqbal

University of Arkansas at Little Rock

Little Rock, Arkansas, USA

kxiqbal@ualr.edu

ORCID: 0000-0001-8375-290X

Abstract—The software engineering research community faces a systemic crisis: peer review is failing under growing submissions, misaligned incentives, and reviewer fatigue. Community surveys reveal that researchers perceive the process as “broken.” This position paper argues that these dysfunctions are mechanism design failures amenable to computational solutions. We propose modeling the research community as a stochastic multi-agent system and applying multi-agent reinforcement learning to design incentive-compatible protocols. We outline three interventions: a credit-based submission economy, MARL-optimized reviewer assignment, and hybrid verification of review consistency. We present threat models, equity considerations, and phased pilot metrics. This vision charts a research agenda toward sustainable peer review.

Index Terms—Peer Review, Mechanism Design, Multi-agent Systems, Reinforcement Learning

## I. INTRODUCTION

The ICSE 2026 Future of Software Engineering call opens with a sobering observation: beneath thriving conferences lies “an undercurrent of grumbling” suggesting “our community may not be doing so well.” Among the complaints, one dominates: “Peer review is broken.” 1

This is not hyperbole. The NeurIPS 2014 duplicate-review consistency experiment found that 57% of papers accepted by one committee were rejected by the other, highlighting substantial outcome instability [1], [2]. Studies document that 6.5–16.9% of AI conference reviews show substantial LLM involvement [3], and that, in LLM-based agent simulations of peer review, up to 37.1% of variance in decisions is attributable to modeled reviewer biases [4]. The “publish or perish” culture has created a tragedy of the commons: researchers maximize submissions while minimizing review effort [5].

The conventional response treats these as social problems requiring cultural change. This position paper offers a different perspective: the peer review crisis is a mechanism design problem, and mechanism design problems yield to engineering [6].

We propose reconceptualizing the research community as a stochastic multi-agent system where agents pursue individual objectives. Current dysfunction arises because reward structures incentivize individually rational but collectively misaligned behaviors. Multi-agent reinforcement learning (MARL) provides tools to redesign these incentives [7], [8].

![](images/aaaf81a582596351989849ca16a9bf0bca07d6227ae4d03e137c1f64e9e785a1.jpg)  
Fig. 1. Three-pillar architecture. Note the feedback loop: review quality verification (Pillar 3) directly informs credit issuance and price dynamics (Pillar 1), creating a closed-loop adaptive system.

This paper outlines three interventions (Figure 1) and a phased research agenda. We do not claim these are proven solutions; rather, we argue they constitute a principled framework warranting systematic investigation.

## II. TAKING STOCK: THE MECHANISM FAILURE

## A. The Tragedy of the Review Commons

The fundamental problem is economic: publishing yields rewards (tenure, promotion), while reviewing yields almost none [9].

This creates a classic commons tragedy. The “reviewer attention budget” is finite, but depletion costs are externalized. Overburdened reviewers produce rushed evaluations, leading to “reviewer roulette” [10].

Scientific publishing volume increased by about 47% between 2016 and 2022, intensifying strain on editorial and reviewer capacity [11]. Reviewer invitation acceptance rates have declined, so editors may need multiple invitations to secure each completed review [9].

## B. The LLM Amplification Effect

Large language models are increasingly used in scientific writing [12] and can reduce the effort required to draft and revise manuscripts. They also enable superficially coherent but substantively hollow reviews. There are growing concerns that LLM assistance may shift review tone and scoring, while detection remains unreliable [13].

## C. Related Mechanisms

Prior work corroborates our approach. Peer prediction methods elicit truthful reports by rewarding agreement with reference raters [14]; information-theoretic variants offer stronger incentive guarantees [15]. Strategyproof mechanisms [16] provide theoretical rationing guarantees. Isotonic mechanisms use multi-submission knowledge for calibration [17].

Recent market-based alternatives like Impact Market [18] propose decoupling dissemination from credentialing entirely. While promising, our framework seeks to repair the existing workflow rather than replace it, minimizing disruption. Similarly, endogenous matching models have explored linking effort to future assignment probabilities [19].

Unlike auction-based rationing mechanisms (e.g., VCG combined with peer-prediction [20]), which clear the market in single-shot rounds, our Credit Economy introduces a persistent, transferable asset. This allows researchers to smooth their labor across time (reviewing now to submit later), addressing the “bursty” nature of conference deadlines. Our framework synthesizes these insights, prioritizing practical deployability.

## III. A MULTI-AGENT FRAMEWORK

## A. The Community as a Stochastic Game

We model the research community as a stochastic multi-agent system $\langle \mathcal { A } , \mathcal { S } , \mathcal { T } , \mathcal { R } \rangle$ where agents pursue individual objectives. Currently, $R _ { \mathrm { r e v } } \approx 0$ while $R _ { \mathrm { p u b } } > 0$ . The solution reshapes rewards so quality reviewing becomes individually rational [6].

## B. Credit-Based Submission Economy

We propose a “Review Credit” (RC) system where submissions cost RC and quality reviews earn RC.

Price Dynamics. Prices follow a closed-loop update rule: $p _ { t + 1 } = p _ { t } + \gamma ( D _ { t } - S _ { t } )$ clipped to $[ p _ { \mathrm { m i n } } , p _ { \mathrm { m a x } } ]$ . Here, $D _ { t }$ represents the rolling average of submission volume (demand for review slots), and $S _ { t }$ represents the cleared review capacity (supply) over epoch t. To prevent oscillations $( \mathrm { e . g . }$ , credit runs), updates occur at fixed monthly epochs with adaptive damping γ [21]. To ensure long-term budget balance and prevent deflationary spirals, the system employs an adaptive issuance policy: if the total credit supply drops below a safety threshold (velocity $< V _ { \mathrm { m i n } } )$ , the protocol temporarily subsidizes review rewards from a central reserve.

Stability. Heterogeneous agent strategies (e.g., hoarding) pose stability risks. We propose monitoring the Credit Velocity $\begin{array} { r } { \dot { V } ~ = ~ \frac { \sum \mathrm { T r a n s a c t i o n s } } { \mathrm { T o t a l ~ S u p p l y } } } \end{array}$ and employing Lyapunov-based control policies to adjust issuance rates if system volatility exceeds safety margins.

Supply Policy. RC issuance occurs through review completion; sinks include submission fees and expiration. Caps prevent hoarding.

Quality Measurement. Review quality combines: blinded author ratings, meta-reviewer consistency, and specificity metrics. Information-theoretic scoring [15] offers stronger incentive properties and should be evaluated as a primary method.

Newcomer Support. First-time submitters receive initial endowments; hardship waivers address career breaks; mentoringlinked credit earning provides alternative pathways.

Governance Model. Credits are centrally ledgered by the venue. Disputes are adjudicated by program chairs with escalation to a standing ethics committee; clawbacks require documented misconduct with appeal rights.

## C. MARL-Optimized Reviewer Assignment

Current algorithms optimize primarily for topic match [22]. Classical OR methods (min-cost flow, MIP with fairness constraints) excel at static allocation [23] but fail to capture dynamic reviewer fatigue.

We propose a Constrained Multi-Agent Reinforcement Learning (CMARL) approach [24].

• State $( s _ { t } ) \colon$ Reviewer load, historical lateness, recent decline patterns, and topic embedding distance.

• Action $( a _ { t } ) \colon$ The assignment matrix subject to hard constraints (COIs, max load).

• Reward (rt): A multi-objective function combining timeliness, specificity score, and fairness penalties.

Counterfactuals. Offline RL on historical logs suffers from confounding (we only observe outcomes for realized matches). To mitigate this, we propose using Doubly Robust Estimators or Causal Bandits to estimate the potential reward of counterfactual assignments during the training phase.

Learning Setup. Learning adds value when reviewer behavior is non-stationary or when latent features (past timeliness, decline patterns) improve predictions beyond static matching. Minimum effect sizes (e.g., >10% timeliness improvement) justify added complexity.

## D. Hybrid Verification

Combining structured checklists [25] with argumentation frameworks [26]: reviewers complete rubrics; review text is parsed into claims.

To ensure scalability, we adopt an “Agent-as-a-Judge” paradigm [27]. An LLM-based verifier extracts claims and checks for stance consistency against the paper content. We acknowledge that LLM verifiers may encode biases or succumb to Goodhart’s law (authors writing for the bot). To mitigate this, our pilot employs a “human-in-the-loop” audit where a random 10% of verifications are manually adjudicated, calibrating the agent against expert judgment. Future iterations may also leverage cryptographic watermarking or provenance attestations to verify human authorship, subject to community governance and consent.

Target overhead: under 5 minutes additional time per review.

TABLE I  
THREAT-MITIGATION MAPPING
<table><tr><td>Component</td><td>Threat</td><td>Mitigation</td></tr><tr><td>Credit Econ- omy</td><td>Review rings</td><td>Network analysis; randomized audits</td></tr><tr><td></td><td>Credit hoarding</td><td>Expiration; caps; adaptive pricing</td></tr><tr><td></td><td>Quality gaming</td><td>Multi-signal scoring; outlier detection</td></tr><tr><td>Assignment</td><td>Bias amplification</td><td>Fairness constraints; offine evaluation</td></tr><tr><td></td><td>Strategic declines</td><td>Decline patterns in assignment weights</td></tr><tr><td>Verification</td><td>LLM-generated re- views</td><td>Disclosure requirements; specificity scoring</td></tr><tr><td></td><td>Shallow reviews</td><td>Argumentation coverage; human triage</td></tr><tr><td>Cross-cutting</td><td>Sybil attacks</td><td>ORCID + institutional verification</td></tr><tr><td></td><td>Retaliation</td><td>Blinded ratings; temporal smoothing</td></tr></table>

## IV. THREAT MODEL AND MITIGATIONS

Table I summarizes threats and mitigations for each component.

## A. Equity and Privacy

Credit systems risk disadvantaging researchers with fewer opportunities. Fairness safeguards include initial endowments and earning multipliers [28]. Equity Measurement: Pilots will track credit Gini disaggregated by region, institution type, and career stage; corrective levers address emerging disparities. Privacy-preserving attestations can reconcile auditability with anonymity.

## V. RESEARCH AGENDA

## A. Phase 0: Simulation & Foundations (2025–2026)

Before real-world credit deployment, we will develop an Agent-Based Model (ABM) of the conference ecosystem. This simulation will stress-test price stability against strategic behaviors (e.g., collusion rings, free-riding) and calibrate γ (damping factors) using historical OpenReview data.

Simultaneously, we deploy lightweight interventions: reviewer accreditation, bi-directional feedback, and structured review templates. These gather empirical baselines and build community acceptance.

## B. Phase 1: Pilot Credit System (2026–2027)

Target venue: ICSE workshop (single-venue, centralized ledger). Methodology: Randomized Controlled Trial (RCT). To prevent contamination, the unit of randomization will be the Program Committee Area rather than individual authors. A power analysis will determine the sample size required to detect a 0.5σ shift in review timeliness with α = 0.05. Metrics: Completion rates (>90%), credit Gini (<0.3), newcomer participation.

## C. Phase 2: MARL Assignment (2027–2028)

Shadow mode comparing learning methods against ILP baselines. Metrics: Timeliness (>10% improvement), load balance, fairness across demographics.

## D. Phase 3: Verification and Federation (2028–2029)

Hybrid verification deployment. Workshop pilots expand to co-located conferences, then main venues. Cross-venue federation requires SIG coordination with explicit policies against arbitrage.

## E. Governance and Sustainability

Success requires recognizing review contributions [29]. We recommend sunset clauses, opt-out pathways, transparent audit reports, and annual assessments.

## VI. DISCUSSION

This vision faces challenges. Credit systems can be gamed; learning-based assignments may inadvertently embed biases; and verification risks may incur unnecessary overhead. Agentbased simulations and formal equilibrium analyses are needed before deployment. The mechanisms we propose are starting points, and integration with complementary approaches (information-theoretic scoring, isotonic calibration) merits investigation.

## VII. CONCLUSION

The peer review crisis arises from misaligned incentives, not moral failure. By applying engineering rigor to governance, we can design mechanisms that make good behavior individually rational. We invite the reviewer community to pursue this research agenda.

## REFERENCES

[1] E. S. Brezis and A. Birukou, “Arbitrariness in the peer review process,” Scientometrics, vol. 123, no. 1, pp. 393–411, 2020.

[2] C. Cortes and N. D. Lawrence, “Inconsistency in conference peer review: Revisiting the 2014 neurips experiment,” arXiv preprint arXiv:2109.09774, 2021.

[3] W. Liang, Z. Izzo, Y. Zhang, H. Lepp, H. Cao, X. Zhao, L. Chen, H. Ye, S. Liu, Z. Huang et al., “Monitoring ai-modified content at scale: A case study on the impact of chatgpt on ai conference peer reviews,” arXiv preprint arXiv:2403.07183, 2024.

[4] Y. Jin, Q. Zhao, Y. Wang, H. Chen, K. Zhu, Y. Xiao, and J. Wang, “Agentreview: Exploring peer review dynamics with llm agents,” arXiv preprint arXiv:2406.12708, 2024.

[5] H. Horta and J. Jung, “The crisis of peer review: Part of the evolution of science,” Higher Education Quarterly, vol. 78, no. 4, p. e12511, 2024.

[6] T. Roughgarden, “Algorithmic game theory,” Communications of the ACM, vol. 53, no. 7, pp. 78–86, 2010.

[7] P. Hernandez-Leal, B. Kartal, and M. E. Taylor, “A survey and critique of multiagent deep reinforcement learning,” Autonomous Agents and Multi-Agent Systems, vol. 33, no. 6, pp. 750–797, 2019.

[8] S. Gronauer and K. Diepold, “Multi-agent deep reinforcement learning: a survey,” Artificial Intelligence Review, vol. 55, no. 2, pp. 895–943, 2022.

[9] D. Routledge, N. Pariente, and P. B. S. Editors, “On improving the sustainability of peer review,” p. e3003127, 2025.

[10] Y. Liu, K. Yang, Y. Liu, and M. G. Drew, “The shackles of peer review: Unveiling the flaws in the ivory tower,” arXiv preprint arXiv:2310.05966, 2023.

[11] M. A. Hanson, P. G. Barreiro, P. Crosetto, and D. Brockington, “The strain on scientific publishing,” Quantitative Science Studies, vol. 5, no. 4, pp. 823–843, 2024.

[12] W. Liang, Y. Zhang, Z. Wu, H. Lepp, W. Ji, X. Zhao, H. Cao, S. Liu, S. He, Z. Huang et al., “Mapping the increasing use of llms in scientific papers,” arXiv preprint arXiv:2404.01268, 2024.

[13] M. Naddaf, “Ai is transforming peer review—and many scientists are worried,” Nature, vol. 639, no. 8056, pp. 852–854, 2025.

[14] N. Miller, P. Resnick, and R. Zeckhauser, “Eliciting informative feedback: The peer-prediction method,” Management Science, vol. 51, no. 9, pp. 1359–1373, 2005.

[15] Y. Kong and G. Schoenebeck, “An information theoretic framework for designing information elicitation mechanisms that reward truth-telling,” ACM Transactions on Economics and Computation (TEAC), vol. 7, no. 1, pp. 1–33, 2019.

[16] Y. Xu, H. Zhao, X. Shi, J. Zhang, and N. B. Shah, “On strategyproof conference peer review,” arXiv preprint arXiv:1806.06266, 2018.

[17] W. Su, “You are the best reviewer of your own papers: An owner-assisted scoring mechanism,” Advances in Neural Information Processing Systems, vol. 34, pp. 27 929–27 939, 2021.

[18] K. Sankaralingam, “The impact market to save conference peer review: Decoupling dissemination and credentialing,” arXiv preprint arXiv:2512.14104, 2025.

[19] Y. Xiao, F. Dorfler, and M. van der Schaar, “Incentive design in¨ peer review: rating and repeated endogenous matching,” arXiv preprint arXiv:1411.2139, 2014.

[20] S. Srinivasan and J. Morgenstern, “Auctions and peer prediction for academic peer review,” arXiv preprint arXiv:2109.00923, 2021.

[21] K. Kousha and M. Thelwall, “Artificial intelligence to support publishing and peer review: A summary and review,” Learned Publishing, vol. 37, no. 1, pp. 4–12, 2024.

[22] J. Jovanovic and E. Bagheri, “Reviewer assignment problem: A scoping review,” arXiv preprint arXiv:2305.07887, 2023.

[23] L. Charlin and R. Zemel, “The toronto paper matching system: an automated paper-reviewer assignment system,” 2013.

[24] J. Achiam, D. Held, A. Tamar, and P. Abbeel, “Constrained policy optimization,” in International conference on machine learning. PMLR, 2017, pp. 22–31.

[25] D. Spadini, G. C¸ alikli, and A. Bacchelli, “Primers or reminders? the effects of existing review comments on code review,” in Proceedings of the ACM/IEEE 42nd International Conference on Software Engineering, 2020, pp. 1171–1182.

[26] P. M. Dung, “On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games,” Artificial intelligence, vol. 77, no. 2, pp. 321–357, 1995.

[27] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. Xing et al., “Judging llm-as-a-judge with mt-bench and chatbot arena,” Advances in neural information processing systems, vol. 36, pp. 46 595–46 623, 2023.

[28] J. Chen, N. Kallus, X. Mao, G. Svacha, and M. Udell, “Fairness under unawareness: Assessing disparity when protected class is unobserved,” in Proceedings of the conference on fairness, accountability, and transparency, 2019, pp. 339–348.

[29] B. Aczel, A.-S. Barwich, A. B. Diekman, A. Fishbach, R. L. Goldstone, P. Gomez, O. E. Gundersen, P. T. von Hippel, A. O. Holcombe, S. Lewandowsky et al., “The present and future of peer review: Ideas, interventions, and evidence,” Proceedings of the National Academy of Sciences, vol. 122, no. 5, p. e2401232121, 2025.
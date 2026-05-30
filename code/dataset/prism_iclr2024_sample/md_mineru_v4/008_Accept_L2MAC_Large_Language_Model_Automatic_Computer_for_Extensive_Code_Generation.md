# L2MAC: LARGE LANGUAGE MODEL AUTOMATICCOMPUTER FOR EXTENSIVE CODE GENERATION

Samuel Holt University of Cambridge sih31@cam.ac.uk

Max Ruiz Luyten University of Cambridge mr971@cam.ac.uk

Mihaela van der Schaar University of Cambridge mv472@cam.ac.uk

## ABSTRACT

Transformer-based large language models (LLMs) are constrained by the fixed context window of the underlying transformer architecture, hindering their ability to produce long and coherent outputs. Memory-augmented LLMs are a promising solution, but current approaches cannot handle long output generation tasks since they (1) only focus on reading memory and reduce its evolution to the concatenation of new memories or (2) use very specialized memories that cannot adapt to other domains. This paper presents L2MAC1, the first practical LLM-based general-purpose stored-program automatic computer (von Neumann architecture) framework, an LLM-based multi-agent system, for long and consistent output generation. Its memory has two components: the instruction registry, which is pop ulated with a prompt program to solve the user-given task, and a file store, which will contain the final and intermediate outputs. Each instruction in turn is executed by a separate LLM agent, whose context is managed by a control unit capable of precise memory reading and writing to ensure effective interaction with the entire file store. These components enable L2MAC to generate extensive outputs, bypassing the constraints of the finite context window while producing outputs that fulfill a complex user-specified task. We empirically demonstrate that L2MAC achieves state-of-the-art performance in generating large codebases for system design tasks, significantly outperforming other coding methods in implementing the detailed user-specified task; we show that L2MAC works for general-purpose extensive text-based tasks, such as writing an entire book; and we provide valuable insights into L2MAC’s performance improvement over existing methods.

## 1 INTRODUCTION

Transformer-based Large Language Models (LLMs), such as GPT-3 (Brown et al., 2020), Instruct GPT (Ouyang et al., 2022), and the most recent GPT-4 (OpenAI, 2023), have achieved unprecedented success in generating high-quality user-directed text. Despite their impressive capabilities, these models are inherently restricted by a fixed context window of size c, which limits the number of tokens and, consequently, the characters they can process. This limitation manifests itself critically in tasks that require the generation of extensive and logically coherent output structures, such as the generation of large codebases. Therefore, although existing LLMs excel in generating short isolated code snippets (Chen et al., 2021), they struggle to produce codebases that are both extensive and internally consistent due to the information loss and contextual truncation imposed by the finite context window. But practical code is rarely a short snippet, so this limitation undermines the applicability of LLMs to solving real-world tasks that require the dynamic integration of multiple outputs and attendance to distant information.

A natural solution is to extend the LLM agent with an external memory store. However, existing methods primarily serve to extend the implicit knowledge of LLMs through an external corpus (Zhong et al., 2022), to facilitate long conversational or document summarization tasks (Liang et al., 2023), or to maintain precise values for variables (Hu et al., 2023). In the latter case, the approaches simply interface the LLM with a dictionary or a database, which does not adjust to other tasks. In other settings, current approaches adopt simplistic memory management strategies that append new

![](images/79c3cec8f5f6e291df6fa26e3210e6dcef5f319f9ca97f3e252661f351faae26.jpg)

Figure 1: L2MAC Overview. Code-L2MAC is an instantiation of the LLM automatic computer (L2MAC) framework, an LLM-based multi-agent system, here for extensive code generation. First, it breaks down the user task into sequential instructions . The Control Unit (CU) manages the LLM’s context window for each instruction (agent) and interacts with the external memory file store through read, write, and evaluate tools. It identifies and reads relevant files from the memory to generate or update files per instruction (P2). This ensures proper conditioning of existing files without losing vital context (P1). Automatic checks evaluate the LLM’s outputs for correctness and completion (P3), with iterative error corrections involving both code syntactical checks of the code and running self-generated unit tests to check desired functionality. Overall, this produces a complete large codebase that fulfills the detailed user task in the file store. See Figure 5 for an expanded overview.

information sequentially without any provision for in-place modification. This makes any error essentially irreversible, a critical limitation when generating codebases, and restricts the possibility of adapting previously generated code as the task progresses. Compounding these shortcomings, these methods do not include mechanisms for maintaining syntactic or semantic consistency within the memory store, a vital requirement for the generation of coherent and interdependent code structures. Thus, existing methods are ill-suited for extensive large code-generation tasks.

An effective method for extensive code generation requires the following three core properties:

(P1) Task-Oriented Context Management: At each computational step, the context for the LLM agent should contain the information required to complete the current instruction. The context is dynamically managed to prevent exceeding the fixed context window size of tokens.

(P2) Precise Read/Write Tools for Entire Memory: The LLM agent should possess read/write operations that can interact precisely with the memory store to fetch and update relevant files.

(P3) Checking the Generated Output: The outputs of the LLM agent are checked for both mistakes and when the current instruction has been completed. When mistakes are detected, such as syntactically invalid code, or failing self-generated functional unit tests, they can attempt to be fixed by iterating the discovered errors with the LLM agent.

With these considerations, we introduce L2MAC, the first practical LLM-based general-purpose stored-program computer (von Neumann architecture) framework, an LLM-based multi-agent system, and instantiate it for long code generation tasks as Code-L2MAC. A Control Unit (CU) orchestrates the execution of the individual LLM agents and their interaction with the memory store, thus satisfying the three stipulated properties. As outlined in Figure 1, an LLM agent first generates a task-oriented instruction list from a detailed user-specified task. The CU tailors the LLM agent’s context (P1), so that it always includes the next unresolved instruction in and information about the execution of past iterations (agents), and declutters the context when approaching its limit. It also endows the LLM agent with the ability to read and update any existing region of the memory store or extend it with new outputs (P2). Furthermore, the CU plays a crucial role in checking the generated output (P3). It feeds the LLM agent with syntactical checker errors and requests the LLM agent to generate checks alongside generating output, here unit tests when generating code, which are verified at each update of the memory file store to trigger corrective actions if needed, thereby ensuring that the extensive output in memory is both syntactically and functionally consistent.

Contributions: ⃝1 We introduce the L2MAC framework, the first practical LLM-based generalpurpose stored-program automatic computer (von Neumann architecture) framework, an LLM-based multi-agent system, for long output generation tasks. ⃝2 We provide a practical implementation of this framework for code generation tasks called Code-L2MAC. This uses a Control Unit to control the input and output of the LLM and the use of entire memory file store read/write tools and highlights that code checks are key to correcting generated code that has syntactic and functional errors within whilst conditioning on and integrating with the existing codebase. ⃝3 We empirically validate Code-L2MAC, demonstrating its state-of-the-art capabilities in generating large codebases to solve for the first time high-level system design tasks of creating entire applications and for generating code achieving a 90.2% Pass@1 score on the HumanEval benchmark (Chen et al., 2021). Also, we show L2MAC works for general-purpose extensive text-based tasks, such as writing an entire book. Additionally, we gain insight and understanding of how Code-L2MAC can leverage tools to execute and verify code by self-generating its own unit tests and use these to correct for generation errors whilst generating large interrelated code structures that fulfill detailed complex user-specified task feature requirements.

## 2 BACKGROUND

Large Language Models (LLMs). Essentially, an LLM is a probabilistic function $l : \Sigma ^ { c }  \mathcal { P } ( \Sigma )$ ingesting a list of elements of the alphabet Σ of lengths c and outputting a distribution over the elements from which one is drawn (Vaswani et al., 2017). We refer to c as the length of the context. For example, GPT-4 and GPT-3 have fixed context windows of 8, 192 and 4, 097, respectively.

Consequently, as discussed in Schuurmans (2023), an LLM at inference time can be formalized as a finite-state machine (Dolfing & Hetherington, 2001). Given the well-known and exceptional extension from finite-state machines to Turing machines Turing et al. (1936) that leads to the practical framework of stored-program computers, it is natural to envision a parallel extension for LLMs.

Stored-Program Computer (SPC). Originally termed the von Neumann architecture (Von Neumann, 1945), is a combination of a processor (arithmetic and logic unit), a Control Unit (CU), and memory capable of storing both instructions and data, SPCs set the foundation for modern computer design. Where the control unit manages the interaction between the processor and the data. A fundamental property of a general-purpose SPC is that it can be reprogrammed to automatically execute a program (ideally to solve a specified task) without manual intervention2. Specifically, the CU extracts from memory, data and instructions and correspondingly sets the input and state of the processor (P1) and then overwrites a memory register with the output (Appendix A). Thus, the SPC extends the processor’s arithmetic and logic abilities with the ability to manipulate memory (P2). An often overlooked but vital function of the CU is error-checking of the processor’s output (P3). “Stochastic” effects of temperature, voltage change, or radiation can cause errors in a processor (Nicolaidis, 2010), including misspecified inputs leading to overflows. Therefore, CUs implement output checks such as parity bit checks and usually corresponding error-correcting mechanisms (Harris & Harris, 2010).

## 3 L2MAC FRAMEWORK

Now we outline the L2MAC framework for the first practical LLM-based SPC, with an instantiation for coding illustrated in Figure 1. L2MAC consists of three main components: the LLM processor, the memory file store, and the Control Unit (CU) that controls the flow of the execution, thus endowing the LLM agent with read-and-write capabilities, among other capacities—this is illustrated in Figure 2. Some choices are deliberately left open to differentiate the key functionalities needed from how we tackle them in our implementation for code generation, which we detail in the next section.

## 3.1 LLM-BASED PROCESSOR

An inherent element of L2MAC is the Large Language Model (LLM), which is responsible for the actual generation of the output for the task. An LLM can be visualized as a more complex atomic unit of computation $f : \Sigma ^ { \dot { c } }  \mathcal { P } ( \Sigma )$ , where, for instance, Σ = 50, 257 tokens (Radford et al., 2019)3; rather than being restricted to only deterministic arithmetic and logical operations on binary sequences, that is, $f : \{ \bar { 0 , 1 } \} ^ { 6 4 } \times \{ 0 , 1 \} ^ { 6 4 } \stackrel { \cdot } { \to } \{ 0 , 1 \} ^ { 6 4 }$ , e.g., for a standard 64-bit processor (Hennessy & Patterson, 2011). This allows for a more flexible and powerful (yet more expensive) computation unit, which can be used to solve a different range of tasks.

![](images/84cd5151daf5579a12ab3bbba4b01fd17eb2c321cfde15b1d0defc63824afdaa.jpg)  
Figure 2: Control Unit—Control flow diagram for one dialog turn t. Here this executes one current instruction $\mathcal { T } ^ { ( k ) }$ . It starts by loading the first instruction into the context window ${ \cal C } ^ { 0 } \gets \{ \underline { { \tau } } ^ { ( 0 ) } \}$ and iterates it automatically until all instructions in have been executed. First, $C ^ { t }$ is processed by the LLM Processor ${ \mathcal { P } } _ { \mathrm { L L M } } ( C ^ { t } )$ to output $M _ { r }$ . The CU stores this in a buffer $\Delta _ { C ^ { t + 1 } } \gets \{ M _ { r } \}$ , and checks if $M _ { r }$ has called a tool, and if so, it executes the tool with the specified input in $M _ { r }$ , which includes reading, writing and evaluating $\mathcal { E } ( D )$ the file store —outputting $M _ { f }$ , which is appended to the buffer $\Delta _ { C ^ { t + 1 } }$ . The CU performs additional control flow as detailed in Section 3.3, for checking if an instruction has been completed, continuing an instruction beyond the context window (P1), and continuing executing the current instruction.

Leveraging an LLM within the L2MAC framework offers distinct advantages to exploit and challenges to overcome, categorized to the properties of P1, P2, and P3. Here, L2MAC benefits from the LLM’s awareness of external tools with which it can interact with assisted by the Control Unit. This capability enables requests for memory reads/writes (P2) and additional output checks (P3).

In contrast, the use of an LLM also imposes constraints that need to be addressed, such as the impediments of a limited context window to prevent incongruencies caused by the lack of attention to distant information; that is, we have to handle context correctly (P1). Furthermore, the stochastic nature of LLM’s output $\left( \mathcal { P } ( \Sigma ) \right)$ is a significant risk in situations where precision and correctness are key. Thus, crucial to effectively updating an interrelated memory is the ability to enforce periodic checks on its output to ensure a level of correctness and consistency (P3) (Liventsev et al., 2023).

## 3.2 MEMORY

Following an SPC, we distinguish between two types of memory, that of the instruction registry and the file store . On the one hand, the instruction registry contains the prompt program that will be used to determine the state of the processor. In L2MAC, given the LLM processor, this corresponds mainly to the strings that will be incorporated into the context of the LLM agent at each execution. In a basic implementation, lists the sequential steps needed to complete the task, either specified by the user or automatically generated—where each step will be executed by a separate LLM agent. On the other hand, the file store stores the rest of the information relevant for the processor to read, write, and evaluate, with the final output ultimately stored in .

## 3.3 CONTROL UNIT

The control unit (CU, cf. Figure 2) is responsible for managing the context window for the LLM, encompassing both its inputs and outputs, executing the LLM, checking its outputs for errors, and enabling it to call tools (functions)—including reading and writing. We further detail the CU, including a block diagram figure and pseudocode for its operation in Appendix B. First, we start with how the CU interacts with the LLM.

## 3.3.1 TASK-ORIENTED CONTEXT MANAGEMENT (P1)

Context formalism. The CU uses the LLM as a multi-turn dialog system, filling its context window C with a combination of messages m which can come from the user $M _ { u } ,$ , an LLM response $M _ { r }$ , a function (tool) output $M _ { f }$ , or the CU $M _ { c }$ , so that $m \in \{ M _ { u } , M _ { r } , M _ { f } , M _ { c } \}$ . Consequently, at turn t then the context windo $\ l { v } ^ { 4 } C ^ { t } \in \operatorname { L i s t } ( { M } )$ is of the form $C ^ { t } = ( m ^ { 1 } , m ^ { 2 } , \dots , m ^ { n _ { t } } )$

To make L2MAC an automatic computer5, the CU prompts the LLM to fill the initially empty instruction registry with a list of instructions $\{ \mathcal { T } ^ { ( 1 ) } , \ldots , \mathcal { T } ^ { ( K ) } \}$ where each will be executed in the LLM processor6. L2MAC then loads an empty context window of an LLM agent with the first instruction $C ^ { 0 } \gets \{ \mathcal { T } ^ { ( 0 ) } \}$ and iterates the CU control flow loop (Figure 2) until all instructions have been achieved. The LLM can signal when the current instruction $\boldsymbol { \mathcal { T } ^ { ( i ) } }$ has been completed through calling a special function ‘step\_complete’ at which point the CU evaluates the file store using its evaluator module  (discussed in Section 3.3.3) to check for any introduced errors. If none are found, it asks the LLM to summarize the generated output in the current context window $C ^ { t }$ as a message $M _ { r s }$ and resets the context window as $C ^ { t + 1 } \gets \bar { \{ \mathcal { Z } ^ { ( k + 1 ) } , M _ { r s } \} }$

Overcoming the fixed context window constraint. The input to the LLM cannot exceed the context window constraint c: the combined length of the initial context $C ^ { t }$ and the additional messages buffer $\Delta _ { C ^ { t + 1 } } = \{ m ^ { 0 } , \dots , m ^ { n } \}$ must fit in the context window, that is7, $| C ^ { t } \oplus \Delta _ { C ^ { t + 1 } } | \leq c .$ However, the length of $\Delta _ { C ^ { t + 1 } }$ is not known a priori, so the CU should have a way of handling the cases where $\Delta _ { C ^ { t + 1 } }$ exceeds the context margin $c - | C ^ { t } |$ . This can be achieved through a combination of three different strategies: (1) minimize the occurrence by promoting the task at each time step to be small enough and economizing the filling of the context ${ \bar { C } } ;$ and if the situation occurs, (2) store in the file store  as much relevant output as possible from the current $C ^ { t }$ and (3) update or include a new summary message with $\mathcal { T } ^ { ( k ) }$ as in-context tuning for the next iteration.

Regarding (1), through appropriate crafting $C ^ { t }$ , the CU can prompt the LLM to plan sub-steps for the current instruction (most likely the original task prompt given by the user) and then target each sub-step in the following iterations. For illustration, in a coding setting, (2) can be achieved by storing the generated code so far to avoid rewriting it in the next iteration, and (3) by initializing a new prompt with a summary $M _ { r s }$ of the current progress and helpful information to complete the current instruction, e.g., which files should be read or modified, or the current progress made fixing errors—(3) is further detailed at the bottom right of Figure 2.

## 3.3.2 PRECISE READ/WRITE TOOLS FOR ENTIRE MEMORY (P2)

The need for a reading mechanism that retrieves the relevant information at each iteration is evident and has been reasonably explored in previous literature. In contrast, previous work on memory (as shown in Section 5) has paid little attention to the writing component, which gets mostly reduced to the appending of new prompts and LLM outputs (Liang et al., 2023; Zhong et al., 2022; Cheng et al., 2023; Wu et al., 2022) or updating the values of very structured and thus restrictive forms of memory (Modarressi et al., 2023), e.g., variables or tables (Hu et al., 2023).

These approaches make sense for summarization, dialogs, and database manipulation tasks but are not suitable for long interconnected output generation tasks, such as generating large codebases for system design tasks. Indeed, in such settings, the possibility of downstream subtasks $\overline { { \boldsymbol { \mathcal { I } } } } ^ { ( j ) }$ demanding extensions of previous outputs (such as modules in a codebase) due to imperfect planning, plus the non-determinism and possible hallucination of LLMs, make it probable to require modifications of previously stored memories to rectify these defects, as shown in Section 6.2.

In L2MAC it is thus key to implement read/write interactions with any part of the memory. We want the agent to be able to scan on demand , retrieve parts of the memory that it considers relevant, and potentially update them. In the next Section 4, we detail our implementation of an LLM with a write component that allows it not only to add new information to D but also to delete and update any of its contents, an essential element that allows L2MAC to succeed in long output generation tasks.

## 3.3.3 CHECKING THE GENERATED OUTPUT (P3)

As discussed in Section 3.1 and 3.3.2, the intrinsic stochasticity of LLMs and the well-known phenomenon of hallucination (OpenAI, 2023) make it likely that incoherent or erroneous outputs occur during long interactions, which can be disastrous, for example, in coding. More profoundly, changes (e.g., to a function) to satisfy a given instruction $\boldsymbol { \mathcal { T } ^ { ( j ) } }$ can hamper the solution to formerly completed instructions $\begin{array} { r } { \mathcal { T } ^ { ( i ) } , i < j } \end{array}$ . Therefore, it is essential to incorporate two key checks, one to check the generated outputs for errors using a given evaluator module , and the other to check when the current instruction has been completed in the current context $C ^ { t }$ (c.f. top diamond in Figure 2).

Error checking and error correction. Using a given evaluator module E, which can process the existing file store $\mathcal { D } , \mathrm { i . e . , } \mathcal { E } ( D )$ , allows when run, errors to be detected and returned to the LLM as an evaluator message $\boldsymbol { M } _ { f e }$ The evaluator is domain-specific; for example, in coding tasks, this can correspond to syntactical code checkers or self-generated unit tests that verify the correctness of the output for an instruction $\boldsymbol { \mathcal { T } ^ { ( i ) } }$ Crucially, these self-generated unit tests also help test the existing functionality of previously generated instructions $\boldsymbol { \mathcal { T } ^ { ( j ) } }$ . Naturally, evaluation checks should be enforced on the file store after each writing operation to ensure that new additions are correct and consistent with previous files. These result in messages $\boldsymbol { M } _ { f e }$ that are provided for in-context learning so that the LLM can correct the errors, $\Delta _ { C ^ { t + 1 } }  \Delta _ { C ^ { t + 1 } } \overset { \cdot } { \oplus } M _ { f e }$ , and iterate by rewriting until the evaluator checks pass, if any are present.

Checking for current instruction completion. To ensure continued execution in a multi-turn dialogue LLM system until completion, we request the LLM to decide on the next step to take, which can involve executing a tool (Wang et al., 2023a). This is achieved through a cycle prompt message $M _ { c c }$ that also asks the LLM if the instruction has been completed. Cycle prompting is necessary to account for different instructions requiring a variable number of turns to complete, and to protect against hallucinations where the LLM agent only discusses the instruction $\boldsymbol { \mathcal { T } ^ { ( i ) } }$ and does not generate a solution or store it in memory. Overall, this ensures that the LLM provides a solution for the given instruction within the current context (P3).

## 4 CODE-L2MAC

Now, we use our LLM automatic computer (L2MAC) framework and instantiate it to complete large codebase generation tasks, which we call Code-L2MAC. We distinguish the general-purpose task long-generation framework from the code instantiation to detach the core components from task domain decisions that can be appropriately adapted to other task domains. We provide the full details of the implementation in Appendix C; yet here we highlight some notable design decisions on the memory layout (in particular, ) and the read logic. There are different potentially valid alternatives for the read component in L2MAC (e.g., Wu et al. (2022)). However, to promote a transparent read component, we make the following choices.

We specify the memory file store , be composed solely of files, each shorter than the residual margin of the context window after accounting for preliminary messages in any iteration8 and instruct the LLM agent to assign each file a semantically meaningful descriptive path. For example, a file name models/user.py suggests that it contains the data model for the user class. This choice is not only valuable for a human reader but also crucial for our Read-and-Write implementation, as it allows the LLM to infer the content of existing files and prioritize those that it might need to read to complete its current instruction. Given the list of file paths, the LLM can request that the contents of any be appended into its context $C ^ { t }$ . Although the path-to-content link is not absolute, empirically, this read implementation can perform well (Section 6), when coupled with the context management logic of the CU. Specifically, if the LLM reads the content of certain files and reaches the context window limit, it can include in its subsequent iteration summary indications of which files should be read and which should be excluded in order to generate the code necessary to complete the current instruction. This approach thereby enables the LLM to systematically scan all memory, with the scanning order guided by priorities previously established from the file path names.

## 5 RELATED WORK

In the following, we review the existing memory-augmented LLM-based approaches, focusing on approaches applicable to completing large-generation coding tasks—and summarize their main differences in Table 1. We provide an extended discussion of additional related works, including those of other single-turn code generation methods and memory-augmented LLMs in Appendix D.

Single LLMs. These are limited to generating an output of the maximum size of the context window and form the most popular baseline widely used for coding. Examples include Codex (Chen et al., 2021), GPT4 (OpenAI, 2023), GPT-Engineer (Osika, 2023) and Code LLama (Rozière et al., 2023).

Reflecting LLMs. These enhance the performance of LLMs by having the LLM reflect retrospectively on the output of an evaluator and the actions taken (Shinn et al., 2023; Madaan et al., 2023). These verbal reflections are used as in-context learning (Dong et al., 2022) to improve performance when attempting the task again. By using a validator, such as self-generated unit tests, this simple idea has provided state-of-the-art small code snippet generation performance (Shinn et al., 2023). Still, the output of these approaches is also confined to the context window, whereas Code-L2MAC uses an evaluator not only for in-context learning but also for consistency of the codebase.

Table 1: Comparison of related works. Columns: Context Management (P1)—can it generate a larger output than c, and if so, can it access the necessary files to generate the next file correctly without knowledge of the file falling out of context? Precise Read/Write for Entire Memory (P2)—can it write to the full memory and update it in any order? Checking the Generated Output (P3)?—can it check for mistakes in the output? References:[1](Richards, 2023)[2](Shrestha & Watkins, 2023)[3](Nakajima, 2023)[4](Chen et al., 2021)[5](Osika, 2023)[6](Shinn et al., 2023)[7](Madaan et al., 2023).
<table><tr><td>Approach</td><td>Methods</td><td>Context Management (P1)?</td><td>Precise Read/Write for Entire Memory (P2)?</td><td>Checking the Generated Output (P3)?</td></tr><tr><td>Autonomous Agent LLMs with memory Single LLMs</td><td>[1,2,3]</td><td>x—forgets which files were generated</td><td>✓ X</td><td>X—No checks</td></tr><tr><td>Reflecting LLMs</td><td>4,5] [6,7]</td><td>χ—limited to c</td><td>x—limited to append-only</td><td>X ✓</td></tr><tr><td></td><td></td><td>X</td><td>read always memory</td><td></td></tr><tr><td>Code-L2MAC</td><td></td><td>✓</td><td>✓</td><td></td></tr><tr><td></td><td>This work</td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td>✓</td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr></table>

Memory-augmented LLMs. Most work on this topic focuses on long conversational/text summarization tasks (Liang et al., 2023; Zhong et al., 2022; Cheng et al., 2023), or mathematical/database reasoning (Hu et al., 2023). Methods in the first group usually focus exclusively on the read component of memory. The same happens with (Wu et al., 2022), which, through k-NN retrieval for next-token predictions, enhances perplexity for multiple tasks, including coding. However, read-only implementations are sensitive to the inconsistency and “stochasticity” of LLMs, which might break code, that the method cannot then fix. Modarressi et al. (2023) proposes updating memories, but they use tuples with two subjects and their relation, so they have no clear application to coding tasks. Similarly, the memory of mathematical/database reasoning methods use a dictionary of values or a structured database, which again is not applicable to different settings (e.g., coding).

Autonomous agent LLMs with memory. Richards (2023); Shrestha & Watkins (2023); Nakajima (2023) formulate a fully autonomous LLM-based agent in a reinforcement learning environment to complete a given task (Wang et al., 2023a). They build and update their own plans from a few user-given high-level goals. When coding, these agents reprogram and reformulate their step plan at runtime without safeguarding the original intentions, resulting in frequent deviations from the task (Wang et al., 2023a; Sato et al., 2023). In comparison, Code-L2MAC is designed to be automatic, i.e., it fulfills the detailed user-specified task without altering or forgetting parts. The only existing autonomous agent LLM with applicable memory capable of writing, reading, and executing code is AutoGPT (Richards, 2023). It tackles the context window constraint by iteratively summarizing previous actions completed at every k-th turn into a rolling summary kept in the context. Like other agents, the first step of AutoGPT is to summarize the user-specified task into a name, role, and five one-sentence goals for the agent to complete; this summary is kept in context throughout execution. AutoGPT and associated methods have two key limitations compared to Code-L2MAC (cf. Figure 3): (1) they compress the user-specified task into a mere six-sentence description, and (2) they compress the previous action history, thus losing crucial information. In code generation tasks, (2) indicates forgetting which files exist and their content, which is compounded by continual re-planning.

## 6 EXPERIMENTS AND EVALUATION

In this section, we evaluate Code-L2MAC and verify that it significantly outperforms state-of-the-art methods for generating code and large codebases for system design tasks. Due to the absence of an existing benchmark for large codebase generation tasks, we introduce one to enable comparison with other methods. Furthermore, there are also no automated tools to validate the generation of codebases for system design tasks either, therefore we propose evaluation metrics to compare the methods.

Benchmark tasks. We evaluate against three standard system design codebase generation tasks whose prompt questions are taken from real-world system design interview questions (Xu & Lam, 2020; Martin, 2023), and the HumanEval benchmark (Chen et al., 2021); with all details in Appendix E.

Evaluation metrics. Large-scale codebase generation is unique in that the generated code can satisfy the high-level user-specified task feature requirements through various possible implementation approaches. To quantify the degree to which the user-specified features in the initial prompt are effectively implemented in the generated code, we introduce a performance metric named Features %. This metric numerically represents the proportion of input features that are fully and functionally implemented in the output codebase. The Features % is obtained by using a separate GPT-4 API call, which iteratively examines the entire generated code to verify the functional implementation of all input features, counting the number of fully implemented features. We quote this as a percentage of the features implemented over the total features specified by the user. A detailed description and a motivating example of this implementation are provided in Appendix G. We also incorporate standard code generation evaluation metrics (Hasemer, 2018), such as the number of lines of code generated LOC and the number of errors # Errors in the codebase as determined by a code syntactical analyzer (Thénault, 2023). Furthermore, each method is instructed to generate unit tests to check that the generated code is valid; therefore, we quote how many of these self-generated unit tests pass as Tests Passed. We give each metric with their 95% confidence intervals throughout. Moreover, we detail these metrics and the experimental setup in more detail in Appendix G.

Table 2: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), and the number of passing tests (Tests Passed). Code-L2MAC fully implements the highest percentage of user-specified task feature requirements across all tasks by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests. The results are averaged over 10 random seeds.
<table><tr><td rowspan="2">Method</td><td rowspan="2">Features %</td><td colspan="2">URL Shortener App #Errors LOC</td><td rowspan="2">Tests Passed ↑</td><td rowspan="2">Features % #Errors</td><td colspan="2">Online Social Media App</td><td rowspan="2">Tests Passed</td><td rowspan="2">Features %</td><td colspan="2">Online Chat App #Errors LOC</td><td rowspan="2">Tests Passed</td></tr><tr><td>↓</td><td></td><td>↑</td><td>LOC</td><td>↑</td><td></td></tr><tr><td>GPT4</td><td>↑ 53.6±10.5</td><td>0±0</td><td>119±21.1</td><td>2.56±0.95</td><td>19.5±8.28</td><td>↓ 4.09±3.32</td><td>116±31.5</td><td>↑ 0.818±0.785</td><td>11±2.26</td><td>↓ 0.3±0.346</td><td>127±24.1</td><td>↑ 1.2±1</td></tr><tr><td>CodeT</td><td>52.9±6.74</td><td>0.05±0.105</td><td>11±1.8</td><td>3.6±0.513</td><td>195±5.19</td><td>0.4±0.603</td><td>106±±17.7</td><td>2.6±1.76</td><td>10.5±4.61</td><td>0±0</td><td>91.6±25.9</td><td>3.32±1.57</td></tr><tr><td>Selelf-Refine</td><td>47.9±8.53</td><td>0.05±0.105</td><td>124±15.7</td><td>3.65±1.5</td><td>16.4±2.2</td><td>0.938±0.714</td><td>11±19.6</td><td>181±0.938</td><td>14.±4.19</td><td>0.211±0.304</td><td>11±13.8</td><td>1.42±0.927</td></tr><tr><td>Refflexion</td><td>38.8±6.02</td><td>0.±0.209</td><td>96.2±9.11</td><td>2.35±0.631</td><td>15.±8.05</td><td>2.53±1.69</td><td>122±24</td><td>1.33±2.44</td><td>10.2±3.08</td><td>0±0</td><td>76±6.88</td><td>2.85±0.822</td></tr><tr><td>utoGPT</td><td>25±19.6</td><td>0±00</td><td>16±41.9</td><td>23.±1.91</td><td>33.3±18</td><td>0.6±0.369</td><td>148±35.5</td><td>3±2.86</td><td>23.1±11.8</td><td>1.85±2.47</td><td>2265.8</td><td>3.08±3.34</td></tr><tr><td>Code-L2MAC</td><td>91.6±8.22</td><td>0±0</td><td>330±47.6</td><td>14±6.71</td><td>82.4±14.6</td><td>0±0</td><td>395±52.9</td><td>18.3±6.8</td><td>59.4±25.9</td><td>0±0</td><td>374±123</td><td>18.8±9.11</td></tr></table>

Benchmark methods. To assess whether Code-L2MAC is state-of-the-art, we compare it with the most competitive and popular autonomous agent LLM with memory AutoGPT (Richards, 2023), based on GPT4 and capable of reading, writing, and persisting, using a vector embedding memory to complete given tasks autonomously. We also compare with code reflecting LLM methods of CodeT (Chen et al., 2022), Self-Refine (Madaan et al., 2023), Reflexion (Shinn et al., 2023) and a single GPT4 LLM (GPT4) (OpenAI, 2023)—we make all these competitive by providing them with the same tools that Code-L2MAC uses. We provide the method implementation details, hyperparameters, and experimental details in Appendix F.

## 6.1 MAIN RESULTS

We evaluated all the benchmark methods across all our system design tasks with results tabulated in Table 2. Code-L2MAC fully implements the highest percentage of user-specified task feature requirements across all tasks by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests—therefore, Code-L2MAC is state-of-theart for completing these system design large codebase generation benchmark tasks. We further evaluated Code-L2MAC on the standard HumanEval benchmark (Chen et al., 2021) and observe that it achieves a state-of-the-art score of 90.2% Pass@1 (Appendix H.1). Also, we show L2MAC works for general-purpose extensive text-based tasks, such as writing an entire book (Appendix H.2).

## 6.2 INSIGHT EXPERIMENTS

This section provides an in-depth empirical analysis of the efficacy of Code-L2MAC compared to its benchmark counterparts, AutoGPT and GPT-4. Specifically, we examine the core properties we suggested an effective extensive code generation framework should possess: task-oriented context management (P1), precise read/write tools (P2), and output error checking and correcting (P3).

Can Code-L2MAC correctly perform task-oriented context management? (P1). To explore if the benchmarked methods during operation contain the information within their context to complete the task directly, we adapted our Features % metric to count the number of user-specified task feature requirements that are retained within the methods task instructions instead, i.e., those instructions that are eventually fed into its context window during its operation, as shown in Figure 3 (a). Empirically, we observe that Code-L2MAC is able to retain a high number of user-specified task feature requirements within its instructions and perform instruction-oriented long-running tasks. We note that AutoGPT also initially translates the user-specified task feature requirements into task instructions; however, it does so with higher compression—condensing the information into a mere six-sentence description. This process results in the loss of crucial task information necessary for completing the overall task correctly, such that it aligns with the detailed user-specified task.

Can Code-L2MAC perform precise read/write operations for the entire file store (P2)? We wish to understand, during the operation of executing a task instruction, if Code-L2MAC can understand the existing generated code files within the codebase—which could have been created many instructions ago, and through its understanding, create new files that interrelate with the existing files, and most importantly update existing code files as new features are implemented. To derive insight, we plot a heatmap of the reading, writing, and when files are created at each write operation step during one episode in Figure 4. We observe that Code-L2MAC has an understanding of the existing generated code that allows it to update existing code files, even those originally created many instruction steps ago, and can view the files when it is not certain and update the files through writing to the files. In contrast, AutoGPT often only writes to files once, when initially creating them, and can only update files that it knows about that are retained within its current context window. Although it also has a read file tool, it often forgets about the files that it created many iterations ago due to its context window handling approach of summarizing the oldest dialog messages in its context window, i.e., a continual lossy compression of the previous progress made during operation of completing the task.

![](images/005f2cb3b41aa2e5606817c5a3b93407dc7035ce43eb2a464a784c493655678a.jpg)  
(a)

![](images/c366bf86a89610bfa63bbd87f63a0f65ca68a9d3d2804ab7fef438888af28d56.jpg)  
(b)

![](images/ea42f0edbd11c5fafffdf957a9ea55b0474e7232947c7456df4e823dd108133b.jpg)  
(c)  
Figure 3: Experimental Insight during operation—of generating a codebase for an Online Chat App task. (a) Percentage of user-specified feature requirements that are retained within the methods task instructions and used in context. (b) Number of syntactical errors within the codebase. (c) Stacked histograms of passing and failing self-generated unit tests.

Can Code-L2MAC check the generated output and error correct (P3)? When using a probabilistic model (LLM) as a generator to output code, errors can naturally occur in its outputs. Therefore, we wish to verify if, when errors do appear, the respective benchmark methods can error-correct the codebase. We plot the number of syntactical errors in the codebase during a run where errors are made in Figure 3 (b). We observe that Code-L2MAC can correctly error correct the previously generated codebase that has errors contained within, which could arise from syntactical errors from the last file written or other files that depend on the most recent file written, which now contain errors. It does this by being presented with the error output when it does arise and modifying the codebase to resolve the error whilst still completing the current instruction. In contrast, AutoGPT cannot detect when an error in the codebase has been made and continues operating, which can compound the number of errors forming within the codebase.

![](images/baf6faf629869f9833d53604dc94f7e3ab02876aaeabe3d37c5f0dba26fc317e.jpg)  
Figure 4: Heatmap of file access. Indicating reading, writing, and when files are created at each write operation step during one episode for the Online Chat App task.

Moreover, Code-L2MAC generates unit tests alongside the functional code and uses these as an error checker to inspect the functionalities of the codebase as it is generated and can use these errors to fix the codebase to pass unit tests that now fail after updating part of an existing file. We show this in Figure 3 (c) and observe that AutoGPT, whilst prompted to also write unit tests for all code generated, is unable to use these tests as an integrity error check, which could be compounded by the observation that AutoGPT forgets which files it has previously created and hence unable to modify the existing forgotten code files as new modifications are made, leading to incompatible code files.

## 7 CONCLUSION AND FUTURE WORK

In this paper, we present L2MAC, the first LLM-based general-purpose stored-program computer framework that effectively and scalably augments LLMs with a memory store for long output generation tasks where this was not previously successfully achieved. Specifically, Code-L2MAC, an application for long code generation tasks, surpasses existing solutions—and is an immensely useful tool for rapid development. This work is not without limitations. L2MAC’s performance is inherently bounded by its underlying LLM across various tasks, from planning to tool use. Further, the current design imposes an implicit constraint on the scale of the codebase by listing all file names within the context window, which could readily be improved. These, and among many other aspects such as complex instruction flows, re-programming the instructions, and interpretable prompt programs pose exciting open directions for future work to build upon as detailed in Appendix I.

Ethics statement. This paper proposes the first practical framework for an LLM-based storedprogram computer and instantiates a version to generate large codebases, named Code-L2MAC. However, misuse or use of such a tool with an incorrectly specified task could lead to undesirable outputs. Furthermore, due to the use of an LLM, such a tool is prone to hallucinations, and hence, such results should always have a content filter on the final output.

Reproducibility statement. All code is available at https://github.com/samholt/L2M AC. Seeking full reproducibility, we include an extensive appendix with all implementation and experimental details to re-create the benchmark tasks and baseline methods. These are detailed in the following: for benchmark task environment details, see Appendix E; for benchmark method implementation details, see Appendix F; regarding Code-L2MAC implementation details, for highlevel details, see Appendix C, and for low-level details, see Appendix F.1; and for evaluation metric details, see Appendix G.

Acknowledgements. The authors would like to acknowledge and thank their corresponding funders, where SH and ML are funded by AstraZeneca. Moreover, we would like to warmly thank all the anonymous reviewers, alongside research group members of the van der Schaar lab (www.vander schaar-lab.com) and Andrew Rashbass, for their valuable input, comments, and suggestions as the paper was developed.

## REFERENCES

Elif Akata, Lion Schulz, Julian Coda-Forno, Seong Joon Oh, Matthias Bethge, and Eric Schulz. Playing repeated games with large language models. arXiv preprint arXiv:2305.16867, 2023.

Anthropic. The claude 3 model family: Opus, sonnet, haiku, 2024. URL https://www.anthro pic.com/news/claude-3-family.

Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, et al. Program synthesis with large language models. arXiv preprint arXiv:2108.07732, 2021.

Ned Batchelder and Contributors to Coverage.py. Coverage.py: The code coverage tool for Python. https://github.com/nedbat/coveragepy, 2023.

Jonas Bayer, Christoph Benzmüller, Kevin Buzzard, Marco David, Leslie Lamport, Yuri Matiyasevich, Lawrence Paulson, Dierk Schleicher, Benedikt Stock, and Efim Zelmanov. Mathematical proof between generations, 2022.

Iz Beltagy, Matthew E. Peters, and Arman Cohan. Longformer: The long-document transformer, 2020.

Sebastian Borgeaud, Arthur Mensch, Jordan Hoffmann, Trevor Cai, Eliza Rutherford, Katie Millican, George van den Driessche, Jean-Baptiste Lespiau, Bogdan Damoc, Aidan Clark, Diego de Las Casas, Aurelia Guy, Jacob Menick, Roman Ring, Tom Hennigan, Saffron Huang, Loren Maggiore, Chris Jones, Albin Cassirer, Andy Brock, Michela Paganini, Geoffrey Irving, Oriol Vinyals, Simon Osindero, Karen Simonyan, Jack W. Rae, Erich Elsen, and Laurent Sifre. Improving language models by retrieving from trillions of tokens, 2022.

Maarten Breddels. Solara. https://github.com/widgetti/solara, 2023.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.

Aydar Bulatov, Yury Kuratov, and Mikhail Burtsev. Recurrent memory transformer. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh (eds.), Advances in Neural Information Processing Systems, volume 35, pp. 11079–11091. Curran Associates, Inc., 2022. URL https: //proceedings.neurips.cc/paper\_files/paper/2022/file/47e288629a6 996a17ce50b90a056a0e1-Paper-Conference.pdf.

Tianle Cai, Xuezhi Wang, Tengyu Ma, Xinyun Chen, and Denny Zhou. Large language models as tool makers. arXiv preprint arXiv:2305.17126, 2023.

Bei Chen, Fengji Zhang, Anh Nguyen, Daoguang Zan, Zeqi Lin, Jian-Guang Lou, and Weizhu Chen. Codet: Code generation with generated tests. arXiv preprint arXiv:2207.10397, 2022.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.

Xin Cheng, Yankai Lin, Xiuying Chen, Dongyan Zhao, and Rui Yan. Decouple knowledge from paramters for plug-and-play language modeling. In Findings of the Association for Computational Linguistics: ACL 2023, pp. 14288–14308, Toronto, Canada, July 2023. Association for Computational Linguistics. doi: 10.18653/v1/2023.findings-acl.901. URL https://aclanthology.org/2023.findings-acl.901.

Cheng-Han Chiang and Hung-yi Lee. Can large language models be an alternative to human evaluations? arXiv preprint arXiv:2305.01937, 2023.

Rewon Child, Scott Gray, Alec Radford, and Ilya Sutskever. Generating long sequences with sparse transformers, 2019.

Krzysztof Choromanski, Valerii Likhosherstov, David Dohan, Xingyou Song, Andreea Gane, Tamas Sarlos, Peter Hawkins, Jared Davis, Afroz Mohiuddin, Lukasz Kaiser, David Belanger, Lucy Colwell, and Adrian Weller. Rethinking attention with performers, 2022.

David Dohan, Winnie Xu, Aitor Lewkowycz, Jacob Austin, David Bieber, Raphael Gontijo Lopes, Yuhuai Wu, Henryk Michalewski, Rif A Saurous, Jascha Sohl-Dickstein, et al. Language model cascades. arXiv preprint arXiv:2207.10342, 2022.

Hans JGA Dolfing and I Lee Hetherington. Incremental language models for speech recognition using finite-state transducers. In IEEE Workshop on Automatic Speech Recognition and Understanding, 2001. ASRU’01., pp. 194–197. IEEE, 2001.

Qingxiu Dong, Lei Li, Damai Dai, Ce Zheng, Zhiyong Wu, Baobao Chang, Xu Sun, Jingjing Xu, and Zhifang Sui. A survey for in-context learning. arXiv preprint arXiv:2301.00234, 2022.

Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenenbaum, and Igor Mordatch. Improving factual ity and reasoning in language models through multiagent debate. arXiv preprint arXiv:2305.14325, 2023.

Angeliki Giannou, Shashank Rajput, Jy yong Sohn, Kangwook Lee, Jason D. Lee, and Dimitris Papailiopoulos. Looped transformers as programmable computers, 2023.

Alex Graves, Greg Wayne, and Ivo Danihelka. Neural turing machines, 2014.

Mandy Guo, Joshua Ainslie, David Uthus, Santiago Ontanon, Jianmo Ni, Yun-Hsuan Sung, and Yinfei Yang. LongT5: Efficient text-to-text transformer for long sequences. In Findings of the Association for Computational Linguistics: NAACL 2022, pp. 724–736, Seattle, United States, July 2022. Association for Computational Linguistics. doi: 10.18653/v1/2022.findings-naacl.55. URL https://aclanthology.org/2022.findings-naacl.55.

Taicheng Guo, Xiuying Chen, Yaqi Wang, Ruidi Chang, Shichao Pei, Nitesh V Chawla, Olaf Wiest, and Xiangliang Zhang. Large language model based multi-agents: A survey of progress and challenges. arXiv preprint arXiv:2402.01680, 2024.

Rui Hao, Linmei Hu, Weijian Qi, Qingliu Wu, Yirui Zhang, and Liqiang Nie. Chatllm network: More brains, more intelligence. arXiv preprint arXiv:2304.12998, 2023.

David Harris and Sarah Harris. Digital design and computer architecture. Morgan Kaufmann, 2010.

Tony Hasemer. Syntactic debugging of procedural programs. In Novice Programming Environments, pp. 227–241. Routledge, 2018.

John L Hennessy and David A Patterson. Computer architecture: a quantitative approach. Elsevier, 2011.

Samuel Holt, Alihan Hüyük, Zhaozhi Qian, Hao Sun, and Mihaela van der Schaar. Neural laplace control for continuous-time delayed systems. In International Conference on Artificial Intelligence and Statistics, pp. 1747–1778. PMLR, 2023.

Samuel Holt, Alihan Hüyük, and Mihaela van der Schaar. Active observing in continuous-time control. Advances in Neural Information Processing Systems, 36, 2024.

Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Jinlin Wang, Ceyao Zhang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, and Jürgen Schmidhuber. MetaGPT: Meta programming for multi-agent collaborative framework. In The Twelfth International Conference on Learning Representations, 2024. URL https://openreview.net/forum?id=VtmBAGCN7o.

Chenxu Hu, Jie Fu, Chenzhuang Du, Simian Luo, Junbo Zhao, and Hang Zhao. Chatdb: Augmenting llms with databases as their symbolic memory. arXiv preprint arXiv:2306.03901, 2023.

Inflection AI. Inflection-2, 2023. URL https://inflection.ai/inflection-2.

Peter Justin. Flaskbb. https://github.com/flaskbb/flaskbb, 2023.

Kwanwoo Lee, Kyo C Kang, and Jaejoon Lee. Concepts and guidelines of feature modeling for product line software engineering. In International Conference on Software Reuse, pp. 62–77. Springer, 2002.

Guohao Li, Hasan Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. Camel: Communicative agents for" mind" exploration of large language model society. Advances in Neural Information Processing Systems, 36, 2024.

Wenda Li, Lei Yu, Yuhuai Wu, and Lawrence C. Paulson. Isarstep: a benchmark for high-level mathematical reasoning, 2021.

Yujia Li, David Choi, Junyoung Chung, Nate Kushman, Julian Schrittwieser, Rémi Leblond, Tom Eccles, James Keeling, Felix Gimeno, Agustin Dal Lago, et al. Competition-level code generation with alphacode. Science, 378(6624):1092–1097, 2022.

Xinnian Liang, Bing Wang, Hui Huang, Shuangzhi Wu, Peihao Wu, Lu Lu, Zejun Ma, and Zhoujun Li. Unleashing infinite-length input capacity for large-scale language models with self-controlled memory system. arXiv preprint arXiv:2304.13343, 2023.

Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. Lost in the middle: How language models use long contexts. arXiv preprint arXiv:2307.03172, 2023a.

Ruibo Liu, Ruixin Yang, Chenyan Jia, Ge Zhang, Denny Zhou, Andrew M Dai, Diyi Yang, and Soroush Vosoughi. Training socially aligned language models in simulated human society. arXiv preprint arXiv:2305.16960, 2023b.

Vadim Liventsev, Anastasiia Grishina, Aki Härmä, and Leon Moonen. Fully autonomous programming with large language models. arXiv preprint arXiv:2304.10423, 2023.

Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, et al. Self-refine: Iterative refinement with self-feedback. arXiv preprint arXiv:2303.17651, 2023.

Donne Martin. System design primer. https://github.com/donnemartin/system-d esign-primer, 2023.

Joan C Miller and Clifford J Maloney. Systematic mistake analysis of digital computer programs. Communications of the ACM, 6(2):58–63, 1963.

Ali Modarressi, Ayyoob Imani, Mohsen Fayyaz, and Hinrich Schütze. Ret-llm: Towards a general read-write memory for large language models, 2023.

Niklas Muennighoff, Qian Liu, Armel Zebaze, Qinkai Zheng, Binyuan Hui, Terry Yue Zhuo, Swayam Singh, Xiangru Tang, Leandro Von Werra, and Shayne Longpre. Octopack: Instruction tuning code large language models. arXiv preprint arXiv:2308.07124, 2023.

Yohei Nakajima. Babyagi. https://github.com/yoheinakajima/babyagi, 2023.

Michael Nicolaidis. Soft errors in modern electronic systems, volume 41. Springer Science & Business Media, 2010.

Brian Okken. Python Testing with pytest. Pragmatic Bookshelf, 2022.

OpenAI. Gpt-4 technical report, 2023.

Anton Osika. Gpt-engineer. https://github.com/AntonOsika/gpt-engineer, 2023.

Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35: 27730–27744, 2022.

Charles Packer, Vivian Fang, Shishir G Patil, Kevin Lin, Sarah Wooders, and Joseph E Gonzalez. Memgpt: Towards llms as operating systems. arXiv preprint arXiv:2310.08560, 2023.

Joon Sung Park, Joseph O’Brien, Carrie Jun Cai, Meredith Ringel Morris, Percy Liang, and Michael S Bernstein. Generative agents: Interactive simulacra of human behavior. In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology, pp. 1–22, 2023.

Hao Peng, Nikolaos Pappas, Dani Yogatama, Roy Schwartz, Noah A. Smith, and Lingpeng Kong. Random feature attention, 2021.

Jason Phang, Yao Zhao, and Peter J. Liu. Investigating efficiently extending transformers for long input summarization, 2022.

Ofir Press, Noah Smith, and Mike Lewis. Train short, test long: Attention with linear biases enables input length extrapolation. In International Conference on Learning Representations, 2022. URL https://openreview.net/forum?id=R8sQPpGCv0.

Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

Toran Bruce Richards. Autogpt. https://github.com/Significant-Gravitas/Auto -GPT, 2023.

Baptiste Rozière, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, Xiaoqing Ellen Tan, Yossi Adi, Jingyu Liu, Tal Remez, Jérémy Rapin, et al. Code llama: Open foundation models for code. arXiv preprint arXiv:2308.12950, 2023.

Megan Kinniment Lucas Jun Koba Sato, Haoxing Du, Brian Goodrich, Max Hasin, Lawrence Chan, Luke Harold Miles, Tao R Lin, Hjalmar Wijk, Joel Burget, Aaron Ho, et al. Evaluating languagemodel agents on realistic autonomous tasks. https://evals.alignment.org/Evalua ting\_LMAs\_Realistic\_Tasks.pdf, 2023.

Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach themselves to use tools, 2023.

Dale Schuurmans. Memory augmented large language models are computationally universal. arXiv preprint arXiv:2301.04589, 2023.

Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik R Narasimhan, and Shunyu Yao. Reflexion: Language agents with verbal reinforcement learning. In Thirty-seventh Conference on Neural Information Processing Systems, 2023.

Asim Shrestha and Adam Watkins. Agentgpt. https://github.com/reworkd/AgentGPT, 2023.

Chris Tabor. Flask jsondash. https://github.com/christabor/flask\_jsondash, 2023.

Leandros Tassiulas and Anthony Ephremides. Stability properties of constrained queueing systems and scheduling policies for maximum throughput in multihop radio networks. In 29th IEEE Conference on Decision and Control, pp. 2130–2132. IEEE, 1990.

Yi Tay, Mostafa Dehghani, Dara Bahri, and Donald Metzler. Efficient transformers: A survey, 2022.

Gemini Team, Rohan Anil, Sebastian Borgeaud, Yonghui Wu, Jean-Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, et al. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805, 2023.

Sylvain Thénault. Pylint, 2023. URL https://pylint.readthedocs.io/en/stable/. Available at: http://pylint.pycqa.org/.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.

Alan Mathison Turing et al. On computable numbers, with an application to the entscheidungsproblem. J. of Math, 58(345-363):5, 1936.

Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. Attention is all you need. Advances in neural information processing systems, 30, 2017.

John Von Neumann. First draft of a report on the edvac, 30 june 1945. Moore School of Electrical Engineering, University of Pennsylvania, Philadelphia, PA, USA. Available online: https://library. si. edu/digital-library/book/firstdraftofrepo00vonn (accessed on 1 October 2022), 1945.

Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, et al. A survey on large language model based autonomous agents. arXiv preprint arXiv:2308.11432, 2023a.

Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, et al. A survey on large language model based autonomous agents. Frontiers of Computer Science, 18(6):1–26, 2024.

Sinong Wang, Belinda Z. Li, Madian Khabsa, Han Fang, and Hao Ma. Linformer: Self-attention with linear complexity, 2020.

Zhenhailong Wang, Shaoguang Mao, Wenshan Wu, Tao Ge, Furu Wei, and Heng Ji. Unleashing cognitive synergy in large language models: A task-solving agent through multi-persona selfcollaboration. arXiv preprint arXiv:2307.05300, 1(2):3, 2023b.

Jeff Wu, Long Ouyang, Daniel M. Ziegler, Nisan Stiennon, Ryan Lowe, Jan Leike, and Paul Christiano. Recursively summarizing books with human feedback, 2021.

Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang. Autogen: Enabling next-gen llm applications via multi-agent conversation framework. arXiv preprint arXiv:2308.08155, 2023.

Yuhuai Wu, Markus N. Rabe, DeLesley Hutchins, and Christian Szegedy. Memorizing transformers, 2022.

xai-org. Open release of grok-1, 2024. URL https://x.ai/blog/grok-os.

Alex Xu and Sahn Lam. System Design Interview: An Insider’s Guide, volume 1. Byte Code LLC, 2020.

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629, 2022.

Dani Yogatama, Cyprien de Masson d’Autume, and Lingpeng Kong. Adaptive semiparametric language models, 2021.

Manzil Zaheer, Guru Guruganesh, Avinava Dubey, Joshua Ainslie, Chris Alberti, Santiago Ontanon, Philip Pham, Anirudh Ravula, Qifan Wang, Li Yang, and Amr Ahmed. Big bird: Transformers for longer sequences, 2021.

Yusen Zhang, Ansong Ni, Ziming Mao, Chen Henry Wu, Chenguang Zhu, Budhaditya Deb, Ahmed Awadallah, Dragomir Radev, and Rui Zhang. Summn: A multi-stage summarization framework for long input dialogues and documents. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1592–1604, Dublin, Ireland, May 2022. Association for Computational Linguistics. doi: 10.18653/v1/2022.acl-long.112. URL https://aclanthology.org/2022.acl-long.112.

Zexuan Zhong, Tao Lei, and Danqi Chen. Training language models with memory augmentation. In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing, pp. 5657–5673, 2022.

Mingchen Zhuge, Haozhe Liu, Francesco Faccio, Dylan R Ashley, Róbert Csordás, Anand Gopalakrishnan, Abdullah Hamdi, Hasan Abed Al Kader Hammoud, Vincent Herrmann, Kazuki Irie, et al. Mindstorms in natural language-based societies of mind. arXiv preprint arXiv:2305.17066, 2023.

## Appendix

## Table of Contents

A Stored-Program Computers (SPC) 17   
A.1 SPC is a Universal Turing Machine 17   
A.2 What is an Automatic Computer? 17   
B Control Unit Operation 18   
C Code-L2MAC High Level Implementation Details 19   
C.1 Read / Write Implementation Details 21   
D Extended Related Work 22   
D.1 Vanilla LLMs 22   
D.2 Transformers for Long Inputs 22   
D.3 Memory Augmented LLMs 23   
D.4 Tool Augmented LLMs 24   
D.5 Multi-step Reasoning & Reflecting LLMs 24   
D.6 Turing Machines, Stored Program Computers and Machine Learning 25   
E Benchmark Task Environment Details 25   
E.1 Codebase Generation System Design Task 25   
E.2 HumanEval Benchmark 29   
Benchmark Method Implementation Details 30   
F.1 Code-L2MAC Low Level Implementation Details 31   
G Evaluation Metrics 34   
G.1 Motivation for Feature % 40   
H Additional Results 40   
H.1 HumanEval Benchmark Results 40   
H.2 L2MAC for Writing an Entire Book 41   
H.3 Additional Main Results 47   
H.4 Code L2MAC in Action. 52   
H.5 Additional Diverse Programming Code Generation Tasks 55   
H.6 Human Expert Validation of Features Implemented Percentage Metric 56   
H.7 Challenges and the Evaluation of Human-written Test-cases 56   
H.8 Generating 1,000+ Lines of Code with Code-L2MAC 57   
H.9 Code-L2MAC Ablation with No Instruction Summarization Message 57   
H.10 Additional Tasks on Implementing a New Feature in an Existing Large Code Base   
with Code-L2MAC of up to 165,000 LOCs 58   
Future work 59   
I.1 L2MAC in Non-coding Domains 61

Code. All code is available at https://github.com/samholt/L2MAC. We have a broader research group codebase at https://github.com/vanderschaarlab/L2M AC.

## A STORED-PROGRAM COMPUTERS (SPC)

Stored-Program Computer (SPC). Originally termed the von Neumann architecture, was first proposed by Von Neumann (1945) as a combination of a processor (arithmetic and logic unit), a Control Unit (CU), and memory capable of storing both instructions and data, SPCs set the foundation for modern computer design. With a control unit (CU) managing the interaction between both components, this design is capable of being reprogrammed to solve various tasks without manual intervention 9. In more detail, the CU uses instructions from the memory to set the processor to a specific state (e.g., load two numbers into the processor’s (arithmetic logic unit) input registers and then execute addition and store the result in memory. The computer is not only able to perform arithmetic and logic operations, but it can also manipulate the memory. One unique aspect often overlooked in this paradigm that is crucial to the reliable operation of the processor is error-checking of the processor’s outputs. Errors can arise in a typical processor from hardware influences such as temperature, voltage variations, or radiation (e.g., cosmic rays) (Nicolaidis, 2010), or from missspecified inputs leading to overflows (e.g., divide by zero errors). Therefore, typical processors involve output checks, the simplest being parity bit checks, and can combine these with error-correcting mechanisms (Harris & Harris, 2010).

## A.1 SPC IS A UNIVERSAL TURING MACHINE

Stored-program computer (SPC) and Automata Theory. We can consider an SPC as a specific type of Turing machine T . Formally, a Turing machine is defined by the 7-tuple $T = ( Q , \Sigma , \bar { \Gamma , \delta } , q _ { 0 } , b , \bar { F } )$ where:

• Q is a finite set of states.

• Σ is the finite input alphabet not containing the special blank symbol b.

• Γ is the finite tape alphabet, where $b \in \Gamma$ and $\Sigma \subseteq \Gamma$

• δ : $Q \times \Gamma \to Q \times \Gamma \times \{ L , R \}$ is the transition function. Given a state and a tape symbol, it specifies the next state, the symbol to write on the tape, and the direction in which the machine should move its head (Left or Right).

$q _ { 0 } \in Q$ is the start state.

$F \subseteq Q$ is the set of accepting states.

In the context of a stored-program computer, the memory holds both the instructions (akin to the transition function δ) and the data (akin to the input sequence from Σ). The program counter, which determines the next instruction to execute, can be represented by the machine’s current state in Q. The execution of a program on an SPC is then analogous to the computation performed by a Turing machine when transitioning from one state to another based on the input read and the defined transition function δ.

The universality of an SPC, similar to a universal Turing machine, means that given the appropriate transition function (or set of program instructions) in its memory, it can simulate any other Turing machine and perform any computable task (Turing et al., 1936).

## A.2 WHAT IS AN AUTOMATIC COMPUTER?

The term ‘automatic computer,’ as used in this paper, comes from the original conception presented by Turing et al. (1936), where Turing introduced the concept of an automatic-machine—commonly known today as a Turing machine. In this context, ‘automatic’ refers to a system capable of executing a pre-defined set of instructions without human intervention (Turing et al., 1936; Von Neumann, 1945).

In the context of LLMs, there are methods whereby LLMs can autonomously execute tasks, as reviewed by Wang et al. (2023a). However, it is crucial to differentiate between the concepts of ‘autonomous’ and ‘automatic’. Autonomous agents are characterized by their ability to independently devise and adapt plans, implying a level of self-determination and initiative in executing instructions. In contrast, our focus with L2MAC is on developing a system that meticulously and automatically executes pre-defined instructions contained in the prompt program . This execution requires no human intervention during the process until all instructions have been successfully executed. In this regard, L2MAC aligns more with the traditional concept of an automatic computer. It functions as a general-purpose, instruction-following LLM-based computer (Von Neumann, 1945) dedicated to efficiently executing the provided instructions, thereby ensuring adherence to the completion of the originally specified prompt program. The term ‘general-purpose’ here implies that L2MAC can accommodate any prompt program as input and execute it without necessitating system redesign for each new prompt-program introduced.

## B CONTROL UNIT OPERATION

The Control Unit, manages the entire context of the LLM and is itself a finite state machine. Here we• Sign-up & Password recovery.• Profile pictures & status.• Privacy settings. Please execute the coding task. [Function Call] [‘view\_files‘] "app.py", expand on Section 3.3, provide pseudocode in Algorithm 1, provide an extend block-diagram figure• End-to-end Encryption & Image sharing.• Emojis & Stickers.• Group chat creation. and profile management... [Function response] Code (Contents of "app.py","database.py", "test\_database.py") Please execute the coding task.2. Implement user registration with sign-up andpassword recovery endpoints; ensure both work of L2MAC in Figure 5, and a data flow diagram in Figure 6.• Temporary image statuses & Visibility control.• Web version.• Offline messaging & Online status. Flask application in "adatabase in "database.psponding tests in "test\_

![](images/a0b18b895b2d71b893fe33031542f290211a01e3212ca65c9ba9d887afda0e19.jpg)  
2001. ASRU’01., pp. 194–197. IEEE, 2001.Figure 5: Code-L2MAC Extended Overview. Code-L2MAC is an instantiation of the LLM Hans JGA Dolfing and I Lee Hetherington. Incremental language models for speech recognition usingautomatic computer (L2MAC) framework, here for extensive code generation. First, it breaks down finite-state transducers. In IEEE Workshop on Automatic Speech Recognition and Understanding,2001. ASRU’01., pp. 194–197. IEEE, 2001.the user task into sequential instructions . The Control Unit (CU) manages the LLM’s context window $C ^ { t }$ for each instruction and interacts with the external memory file store through read, write, and evaluate tools. It identifies and reads relevant files from the memory to generate or update files per instruction (P2). This ensures proper conditioning of existing files without losing vital context (P1). Automatic checks evaluate the LLM’s outputs for correctness and completion (P3), with iterative error corrections involving both code syntactical checks of the code and running selfgenerated unit tests to check desired functionality. Overall, this produces a complete large codebase that fulfills the detailed user task in the file store .

![](images/f28f27546a6257d8d85e0321e9e8ba4c4442c7eb2511ee2d4828c4910a06a3e8.jpg)  
Figure 6: Data flow of L2MAC executing one prompt instruction $\mathcal { T } ^ { ( k ) }$ from a self-programmed prompt-program I. The first practical LLM-based stored-program automatic computer (L2MAC) framework. The L2MAC consists of a file store , an entire memory write component $\mathcal { W } ,$ an entire memory read component ${ \mathcal { R } } ,$ and a program control flow mechanism that of a Control Unit CU (c.f., Figure 2) to manage the LLM’s context window—encompassing both its inputs and outputs. Here, the context window $C ^ { t }$ (dashed gray box) consists of a sequence of messages, where each message has one of the following message types: control $M _ { c }$ , user $M _ { u } .$ , LLM response $M _ { r }$ and function response $M _ { f }$

## C CODE-L2MAC HIGH LEVEL IMPLEMENTATION DETAILS

In the following we describe the high-level implementation details of Code-L2MAC, and we provide the verbose low level implementation details, such as the function JSON definitions in Appendix F.1. We follow the same structure as the L2MAC outline and focus on the specific design choices we made for each item. For the LLM Processor, we use GPT-4-0613 OpenAI (2023), which trains GPT-4 to receive in-context descriptions of functions (tools) and call them as needed, where the descriptions follow a JSON format (OpenAI, 2023).

The functions we provide are the following:

1. ‘provide\_detailed\_sub\_task\_steps\_for\_sub\_agents‘. For producing a step-by-step plan, where each step paragraph is a detailed sub-task step for a separate sub-agent LLM to complete.

2. ‘sub\_task\_step\_complete‘. For the LLM to call when the user specified sub task step has been completed.

3. ‘view\_files‘. Prints out all the file contents into the response to view.

4. ‘run\_python\_file‘. Runs a python file and returns the output to the response to view.

5. ‘write\_files‘. Writes out multiple files that will be combined into the existing codebase.

6. ‘delete\_files‘. Deletes files, where their names are specified.

Next, we discuss specific choices to develop a method based on our LLM Automatic Computer (L2MAC) framework specifically designed for large code generation tasks, which we call Code-L2MAC.

For the LLM Processor, we use GPT-4-0613 OpenAI (2023), which trains GPT-4 to receive incontext descriptions of functions and call them as needed following a JSON format (OpenAI, 2023). See Appendix F.1 for a low-level JSON definition of the functions that we provide to the LLM, most of which we also mention below.

In terms of the instructions, we initialize $\mathrm { i t } ^ { 1 0 }$ with $\mathcal { T } ^ { 0 } = \emptyset$ , and the CU queries the LLM only in the first iteration with the user-specified feature requirements (task description) and requests the LLM to define a sequential prompt program $\mathcal { T } = { [ \mathcal { T } ^ { ( 0 ) } , \dots , \mathcal { T } ^ { ( K ) } ] }$

Regarding the data $\mathcal { D } ,$ we determine that it encompasses only the code generated so far so that upon termination of Code-L2MAC, corresponds to its output. However, we impose the codebase $\bar { \mathcal D }$ to be partitioned into files no longer than the context window11, and we name the files with a path from a root directory/where the name of folders and files suggests its content. This choice is not only useful for a human reader but will be crucial for our Read-and-Write implementations.

Algorithm 1 Control Unit Pseudocode for L2MAC   
1: Input: Initial user input prompt $p _ { \mathrm { i n } } ;$ file store $\mathcal { D } ;$ Domain Evaluator unit $\mathcal { E } ;$ Domain system   
message $M _ { s } ;$ Domain bootstrap message $M _ { c b } ;$ Context window constraint c; Unwind token   
marign b   
2: Output: External memory store $\mathcal { D } .$   
3: $\mathcal { T }  \infty , M _ { r s }  \emptyset$   
4: $M _ { u } \gets p _ { \mathrm { i n } }$   
5: $M _ { r } \gets \mathsf { \bar { L } L } M ( \{ M _ { s } , M _ { c b } , p _ { \mathrm { i n } } \} )$ ▷ Self-program $\mathcal { T } ,$ by bootstrap instruction   
6: $( \mathbb { Z } , \mathcal { D } ) \gets \mathrm { p r o c e s s \_ i n t o \_ p r o m p t \_ p r o g r a m } ( M _ { r } , \mathcal { D } )$   
7: while is not empty do   
8: $C ^ { t } \gets \{ M _ { s } , \bar { M } _ { r s } \}$ ▷ Clear Context Window: It always contains the system and   
summary message   
9: $( \bar { \mathcal { L } } ^ { ( k ) } , \mathcal { D } )  \mathsf { \bar { p o p } } .$ \_front $\underline { { \mathrm { o f } } } \_ { \mathcal { I } } ( \mathcal { I } , \mathcal { D } )$ ▷ Fetch: next instruction from external memory $\mathcal { D }$   
10: $C ^ { t } \gets C ^ { t } \oplus \mathcal { T } ^ { ( k ) }$   
11: has\_instruction\_completed False   
12: while has\_instruction\_completed is False do   
13: $M _ { r } \gets \mathcal { P } _ { \mathrm { L L M } } ( C ^ { t } )$   
14: $\Delta _ { C ^ { t + 1 } } \gets \{ M _ { r } \}$   
15: if ‘function\_call’ in $M _ { r }$ then   
16: $( M _ { f } , { \mathcal { D } } ) \gets { \mathrm { e x e c u t e } } _ { - }$ function $M _ { r } , D )$   
17: ▷ Invoke tool: Includes functions (tools) to read/write and evaluate the file store $\mathcal { D }$   
18: $\Delta _ { C ^ { t + 1 } } \gets \Delta _ { C ^ { t + 1 } } \oplus M _ { f }$   
19: if ‘step\_completed’ in $\dot { M } _ { r }$ then   
20: $\bar { M _ { f e } }  \bar { \mathcal { E } } ( \mathcal { D } )$ ▷ Run evaluator module on file store   
21: if $\dot { M } _ { f e }$ is then ▷ If evaluator checks pass   
22: while $| C ^ { t } \oplus \Delta _ { C ^ { ( t + 1 ) } } | > b$ do ▷ Summarize instruction output to   
$M _ { r s }$ . Unwind oldest messages to make room for summary control message $M _ { c s }$ and summary   
response $M _ { r s }$   
23: $( \_ , C ^ { t } )  \mathsf { p o p } .$ \_back\_of\_ $C ^ { t } ( C ^ { t } )$   
24: $M _ { r s } \gets \mathcal { P } _ { \mathrm { L L M } } ( C ^ { t } \oplus \Delta _ { C ^ { ( t + 1 ) } } \oplus M _ { c s } )$   
25: has\_instruction\_completed True   
26: $\Delta _ { C ^ { t + 1 } }  \Delta _ { C ^ { t + 1 } } \oplus M _ { f e }$   
27: $\Delta _ { C ^ { t + 1 } }  \Delta _ { C ^ { t + 1 } } \oplus M _ { c c }$ ▷ Append the cycle message   
28: $\mathbf { i f } \left| C ^ { t } \oplus \Delta _ { C ^ { ( t + 1 ) } } \right| >$ c then ▷ Would exceed context check   
29: while $| \bar { C } ^ { t } \oplus \bar { \Delta } _ { C ^ { ( t + 1 ) } } | > b$ do ▷ Summarize progress to $M _ { r s }$ . Unwind oldest   
messages to make room for summary control message $M _ { c s }$ and summary response $M _ { r s }$   
30: $( \_ , C ^ { t } )  \mathrm { p o p { \_ } b a c k \_ o f \_ } C ^ { t } ( C ^ { t } )$   
31: $M _ { r s } \gets \mathcal { P } _ { \mathrm { L L M } } ( C ^ { t } \oplus \Delta _ { C ^ { ( t + 1 ) } } \oplus M _ { c s } )$   
32: $C ^ { t + 1 } \gets \{ M _ { s } , M _ { r s } , \mathcal { T } ^ { ( \bar { k } ) } \}$   
33: else   
34: $C ^ { t + 1 } \gets C ^ { t } \oplus \Delta _ { C ^ { t + 1 } }$ ▷ Append Messages   
35: return

The remaining details are in the arguably richest component of the method, the control unit.

Execution flow of the LLM. In Code-L2MAC, we can describe the execution flow as the following iteration. For each instruction $\mathcal { T } ^ { ( k ) } \in \mathcal { T } ,$ while $\mathcal { T } ^ { ( k ) }$ is not satisfied, do the following—following the CU pseudocode Algorithm 1. First, load the fixed messages that provide in-context learning to the LLM, the description of the current instruction $\mathcal { T } ^ { ( k ) }$ ), and the summary of the last execution $M _ { r s }$ . We let the LLM iterate (work on completing the instruction) while in context, and if approaching out of context, summarize its current context and iterate.

Interfacing with tools. During execution, the LLM might request reading and writing operations. After each write (which possibly introduces a new test), a syntactical checker and all existing tests in are run, and the output is provided to the LLM—through $M _ { f e } .$ . If, after receiving this feedback, the LLM considers the task completed, it can signal it to the CU through calling a special function ‘step\_complete‘, which summarizes the current context output into $M _ { r s }$ and continues executing the next instruction with this summary $M _ { r s }$ . After all K instructions are completed, the process halts (stops), and is returned.

We are only left to detail the process of reading and writing. Given the instruction $\mathcal { T } ^ { ( k ) }$ , the LLM must be able to know what modules in D it can call, how to call them, and where in the directory to write new code. However, the size of might exceed the context window.

Due to the restrictions mentioned on the files in , the LLM can read and write any single full file as desired and, if necessary for context preservation, summarize this information for the next iteration. However, the decision regarding which files are read can be heuristically based on the semantic information provided by the path and name of the file, which encodes its role in .

Specifically, we enable the read component of Code-L2MAC by implementing the two functions. list\_files(), which lists the file paths in breadth-first search order. This could be refined to only list a subset of files within a subdirectory, but for simplicity, in our implementation, we automatically list all file paths in  for the LLM as contexts to enable it to be aware of existing code and help it determine where to include newly generated files. And view\_files(files), which takes a list of file paths and returns strings with their content—appending this to the context window.

We also provide the LLM at all times with a system message Ms to inform it that it is to complete a coding task, that it must act without human input, and a few details about the coding environment that exists within—for example, that it can use the python test framework Pytest, and can only mock in-memory databases as none are installed in the local environment. Although this could be resolved by installing and providing a clean, fresh version for most common database providers, we leave this extension as a future work to explore.

We also provide the LLM with a pre-prompt message that it uses with the user-specified requirements, to construct the initial plan, we also detail this and the system message in Appendix F.1.

## C.1 READ / WRITE IMPLEMENTATION DETAILS

Here we expand on the read/write implementation details of Code-L2MAC. This builds on the existing descriptions contained within Section 4 and appendices C and F.1.

The LLM interfaces with the control unit (CU) through calling functions, and thus, the read and write implementation can be fully described through a discussion of the functions that are provided to Code-L2MAC to that end, which are ‘read\_files’ and ‘write\_files’.

It is worth noting the control unit always exposes the LLM to the list of file paths that are already part of the codebase (e.g., “file paths: [‘app.py’, ‘tests/test\_app.py’]”). The name of directories and files (i.e. file path) provides a semantical prior for the order in which the LLM will read each file, depending on the functionality it is looking for (among other elements, including always the current instruction t, and possibly previous dialog turn outputs and error responses).

Note that if the LLM initially reads a file that does not contain what it was looking for or the desired functionality is spread across multiple files, the LLM can continue reading other files. Recall that when the context window is full, the CU prompts the LLM to summarize the relevant parts of the context window for the current instruction $\mathcal { T } _ { t }$ . In this case, it could summarize which are the relevant files it needs to read if the functionality is spread across multiple files.

Assume the LLM has already determined the name of the file ‘file\_path’ that it wants to read. Let us zoom into the functions (tools) provided to the LLM to signal intentions to the CU.

• ‘write\_files(file\_path, content)’ requests the CU to create or overwrite ‘file\_path’ and populate it with ‘content’.

As the empirical results demonstrate, these functions perform well as components of Code-L2MAC.   
The future work appendix (Appendix I) discusses how these functions could be optimized.

We find Code-L2MAC’s reading and writing functionality different from previous memory-augmented LLM (where we refer to the extended related work for more details, Appendix D) as these can be categorized as:

• Append only memory: These methods explicitly extend the implicit knowledge of LLMs through an external corpus (Zhong et al., 2022) to facilitate long conversational or document summarization tasks (Liang et al., 2023).

• Key-value memory: These methods interface the LLM with a dictionary or a database (Hu et al., 2023), which does not apply to our automatic coding tasks.

## D EXTENDED RELATED WORK

## D.1 VANILLA LLMS

The usage of only a single LLM without a memory augmentation approach is limited to only producing an output that can be maximally as long as the underlying LLM’s context window constraint c. Although not directly applicable, they are still related since the main focus of all coding tasks to date in the literature focuses on using an LLM to solve a code generation task within the context window constraint c. Notable examples include Codex (Chen et al., 2021), GPT4 (OpenAI, 2023), GPT-Engineer (Osika, 2023) and Code LLama (Rozière et al., 2023).

Vanilla LLMs with longer context windows. One might try to directly extend the context window. However, such an approach scales quadratically in computational complexity (Vaswani et al., 2017), an impracticality worsened by the observation that LLMs with long context windows attend information from the middle of the window poorly, substantially decreasing their task performance as the length increases (Liu et al., 2023a). Another naive approach would be to fine-tune the LLM in the environment at hand so that it implicitly memorizes it in its weights, but this should be done recurrently as the state evolves, which is also too computationally expensive to be practical (Brown et al., 2020).

## D.2 TRANSFORMERS FOR LONG INPUTS

There are architectural approaches to directly allow LLMs to ingest larger windows. Tay et al. (2022) offers a comprehensive review on this topic of “efficiency-flavored” transformers.

Child et al. (2019); Beltagy et al. (2020); Zaheer et al. (2021) present sparse attention mechanisms that scale subquadratically with the length of the sequence, Guo et al. (2022); Phang et al. (2022) draw on local/global attention mechanisms to scale to longer inputs, Wang et al. (2020) approximate the attention mechanism with a low-rank matrix to achieve linear complexity, Choromanski et al. (2022) provide an unbiased estimator of the attention that converges uniformly, Peng et al. (2021) use random features to approximate soft-max attention with a decreased computational burden. Although this list is not exhaustive, the precise impact of these optimizations on the performance of LLM is not yet fully understood, and the adoption of these approaches in practice is not widespread.

In Press et al. (2022), the authors discuss biasing attention scores with a penalty proportional to their distance instead of using positional embeddings, which allows them to extrapolate to longer sequences in inference time effectively. Consequently, they achieve significantly more efficient training. However, this does not address the challenges of long context windows at inference time.

## D.3 MEMORY AUGMENTED LLMS

## D.3.1 LLMS WITH BUILT-IN MEMORY

These are works that expose the LLM to memory at training time. Yogatama et al. (2021) extend the usual attention architecture in two ways. First, they extend the context window without much burden at training time by omitting the backward step for distant tokens. Second, they update the next token probability distribution by incorporating information about the next token for historical data for the nearest neighbors in latent space. Borgeaud et al. (2022) essentially incorporates for each training example the k-NN (based on an embedding fixed through training) from an external corpus. Zhong et al. (2022) propose a boost to the next token probability distribution based on the similarity of the current embedding to the previous embeddings where this token appeared. These enable the LLM to be trained with this memory component but can essentially be thought of in the same spirit as embedding NN lookup memory. However, none of these methods enables the memory to be updated.

Finally, (Bulatov et al., 2022) embeds into a sequence of tokens memory for the next inference. This approach, however, has a low-interpretable, non-symbolic, and limited memory, thereby not fully addressing arbitrarily long tasks.

## D.3.2 INFERENCE-TIME MEMORY-AUGMENTED LLMS

The plainness of the limitations imposed by a limited context window has motivated several efforts to overcome it, which has inevitably led to the concept of memory. However, most of such works focus on long conversational / text summarization tasks (Liang et al., 2023; Modarressi et al., 2023; Zhong et al., 2022; Cheng et al., 2023), or mathematical/database reasoning (Hu et al., 2023). The methods from the first group, due to the domain, focus exclusively on the read component of memory. The same happens with (Wu et al., 2022), which explores the k-NN lookup to retrieve memory for next-token predictions and observes improvements in perplexity for multiple tasks, including coding. However, such read-only implementations are more sensitive to the erratic fallibility and the “stochastic” nature of LLMs to break code and cannot interact with memory in any other way. An exception to this is Modarressi et al., 2023, but its memory (and thus update capabilities) is composed of tuples of the form (Subject 1, Subject 2, Relationship), for which there is no apparent application to coding tasks. Similarly, mathematical / database reasoning methods such as (Hu et al., 2023) reduce memory to a dictionary of values or a structured database, which again are not applicable to different settings (e.g., coding).

## D.3.3 AUTNOMOUS AGENT LLMS WITH MEMORY

These works formulate the LLM as an agent in a reinforcement learning environment, where it observes a state and then takes an action, often calling a particular tool with an argument and interacting with the environment until the task is solved (Wang et al., 2023a). Unique to these works is they act fully autonomously, where they are often given a few high-level goals and construct their own plans, which are continuously updated to have self-guided operation without external input, to complete their goals or run continuously (Richards, 2023; Shrestha & Watkins, 2023; Nakajima, 2023). Regarding code generation tasks, this implies that these agents can re-program and re-formulate their step plan at run-time; however, this can often lead to the agents going off-topic instead of completing the specified given task and getting stuck in infinite loops (Wang et al., 2023a; Sato et al., 2023). However, in L2MAC we specify that it is automatic rather than fully autonomous so that the specified user input commands can be performed without manual intervention whilst achieving the input specified given task by the user. Furthermore, of the existing Autonomous Agent LLMs with memory, the only directly applicable method capable of writing, reading, and executing code of files is AutoGPT (Richards, 2023). This overcomes the context window constraint to complete long-running tasks iteratively lossly summarizing the previous actions completed after a given number of turns and only keeping the running summary in the context window. Prevalent with AutoGPT and others is that they contain a first step of taking the user-specified task, and lossly summarizing it into a name, role, and five one-sentence goals for the agent to complete; this goal message also is always in the agent’s context window. At each dialog step, the LLM is prompted with a ReACT (Yao et al., 2022) message template to reason, plan, and act by selecting the next tool to call until the goals have been achieved, then stops. Overall, these methods, such as AutoGPT have two key limitations: (1) they lossily compress the initial detailed user-specified task into a six-sentence description (a sentence role and five goal sentences), and (2) they lossily compress the previous action history, which for code generation tasks equates to forgetting which files were created and their use, which is further compounded by re-planning with a separate new plan at dialog step. Whereas our proposed LLM automatic computer (L2MAC) can (1) create a detailed plan initially and use that single plan throughout to align to complete the original user-specified task, and (2) L2MAC is aware of the existing files generated, which encapsulates all the previous actions up to the current state (where the files track the current memory state), allowing it to know and integrate new code with the existing files already generated.

## D.4 TOOL AUGMENTED LLMS

Schick et al. (2023) teach LLMs to use external tools through API calls, for example, to use a calculator, a search engine, or a translation system to cover LLM weaknesses or reduce computation cost. The methods by which the LLM chooses when to read from memory (instead of automatically receiving the information obtained from memory) can basically be regarded as providing a new tool to the LLM (e.g., Hu et al. (2023); Modarressi et al. (2023)). This is the case for the L2MAC implementation of reading and writing, but not all the functionalities of the control unit can be seen under this lens, as is the case with the monitoring of the context window or the automatic evaluation of the file store, unless we stretch it excessively. In any case, as argued in Modarressi et al. (2023), this similarity with Schick et al. (2023) does not undermine the relevance of the development of new and influential tools.

## D.5 MULTI-STEP REASONING & REFLECTING LLMS

Reflecting LLMs. These methods can improve the task performance of existing single LLMs by having access to an evaluator and using the LLM to reflect on the actions taken (current trajectory part) to derive actionable verbal feedback that is persisted in an append-only memory (Shinn et al., 2023; Madaan et al., 2023). These verbal reflection learnings are a form of in-context learning (Dong et al., 2022) that are then used to improve the task or sub-task performance when the task or sub-task is restarted anew. This simple, and practical reflection idea, when having access to a possible external validator, such as self-generated unit tests for code generation, have demonstrated improving single LLMs for small code snippet generation tasks performance to be state-of-the-art (Shinn et al., 2023). A unique characteristic our our checks is that they are not only aimed at validating the immediate output but rather to impose coherence on the memory as a whole. This implies that while in previous settings, a failing test would require a change in the LLM output, in L2MAC, it can also motivate revisiting and refactoring a preexisting component in the file store.

Specifically, we find the following differences between Code-L2MAC and reflecting LLM methods, such as Self-Refine and Reflexion to be:

• Self-Refine (Madaan et al., 2023) refines the most recent output from the LLM and Reflexion (Shinn et al., 2023) the recent outputs that are only within the LLM’s current context window $C ^ { t } ;$ whereas Code-L2MAC can refine the entire file store, encompassing all previous outputs from the LLM—allowing it to fix or improve earlier outputs from multiple instructions back, outside its context window, which are now erroring due to a new code implementation change. This enables Code-L2MAC to generate long, consistent, and interrelated code structures.

• Self-Refine and Reflexion are constrained to operating on an output within the context window constraint c, whereas Code-L2MAC can manage a total output greater than the context window constraint through the L2MAC framework.

Multi-step reasoning. Methods that leverage a hierarchical flow of information between LLMs can also handle information that does not fit the context length, thanks to the distribution of information. For example, (Zhang et al., 2022; Wu et al., 2021) iteratively and hierarchically perform the summarization of long documents. We refer to (Dohan et al., 2022) for the unification of such methods under a common formalism. Code-L2MAC uses simple instantiations of this family to populate from the initial prompt or to summarize the execution when cleaning the context window, but future iterations could build on more complex cascades to improve our implementation of L2MAC. Multistep reasoning is only a small part of L2MAC, and we envision L2MAC enhancing multistep reasoning methods through the CU and memory (c.f. Appendix I). Furthermore, there exist standard RL multi-step planning frameworks (Holt et al., 2024; 2023) which could be adapted to LLMs in future works.

## D.5.1 LLM-BASED MULTI-AGENT SYSTEMS

LLM-based Multi-Agent Systems, comprise of multiple LLM-powered agents that interact with one another to achieve a desired task (Wang et al., 2024; Guo et al., 2024). L2MAC is an example of an LLM-based multi-agent system, as it consists of separate LLM-based agents that work sequentially each getting a separate next instruction (where the instructions were generated by an initial LLMagent) and persisting memory of the previous agent’s outputs between the agent’s, as illustrated in Figure 1. Broadly LLM-based multi-agent systems, facilitate sophisticated interactions and decision making (Wang et al., 2024; Guo et al., 2024), proposed through collective intelligence and specialized profiles and skills of multiple agents, to allow them to collaboratively complete tasks. Such works include (Wang et al., 2023b; Du et al., 2023; Zhuge et al., 2023; Hao et al., 2023; Akata et al., 2023; Liu et al., 2023b; Park et al., 2023; Cai et al., 2023; Hong et al., 2024; Wu et al., 2023; Li et al., 2024; Packer et al., 2023).

## D.6 TURING MACHINES, STORED PROGRAM COMPUTERS AND MACHINE LEARNING

There are instantiations of Universal Turing Machines and Stored-Program Computers with LLMs (Schuurmans, 2023; Giannou et al., 2023), respectively, which are theoretically insightful. However, in both cases, their method with a transformer at the core only aims to simulate a UTM or SPC, thereby not achieving a method functionally superior to either a UTM or SPC (and none of them new), which can be implemented much more cheaply. In contrast, we capitalize on the SPC framework to boost the LLM’s unique capabilities as a stochastic NLP to automatically solve potentially long tasks from a single user prompt, which is altogether a different focus.

Although (Graves et al., 2014) does not use LLMs, and the focus is also completely different to ours (since it aims to reproduce algorithms by supervised learning), it is worth mentioning that they extend a Recursive Neural Network with memory to achieve a Turing Machine or von Neumann architecture capable of inferring simple algorithms when trained to reproduce them.

## E BENCHMARK TASK ENVIRONMENT DETAILS

## E.1 CODEBASE GENERATION SYSTEM DESIGN TASK

Given the absence of pre-existing benchmark task environments suitable for evaluating long code generation tasks, we have introduced a new benchmark tailored for standard system design tasks, which are typically assigned to humans. Traditional system design tasks often require high-level conceptualization, such as devising the architecture, modules, components, interfaces, and data structures needed for an online application to meet specific user feature requirements (Xu & Lam, 2020). Unlike these conventional tasks that predominantly focus on high-level system outlines, our benchmark mandates the implementation of fully functional code. This code aims to instantiate a minimal system satisfying the user-specified requirements in a practical manner.

For meaningful and realistic evaluation, our benchmark encompasses three standard system design codebase generation tasks. The prompt questions for these tasks are derived from actual system design interview questions, providing a realistic basis for assessment (Xu & Lam, 2020; Martin, 2023). The tasks included in the benchmark are as follows:

1. URL Shortener App: This task necessitates the implementation of a comprehensive online URL shortening service, a utility that enables users to submit lengthy URLs and subsequently receive a shortened variant for simplified sharing. The user-specified feature requirements for this task are extensive. The envisaged system should facilitate URL shortening services, allowing users to input, validate, and, if desired, customize their URLs. The shortened URLs should redirect users to the original addresses. Users should have access to analytics, revealing data such as click counts, timestamps, and geographical locations linked to each URL. The platform should also support user account creation and management, enabling users to edit, delete, or view analytics related to their URLs. An administrative dashboard for monitoring user activity, user accounts, and overall system performance should be in place. Furthermore, users should have the ability to set expiration parameters for their shortened URLs.

2. Online Microblogging App: The task entails the implementation of a web-based microblogging service where registered users can post short textual messages, follow or unfollow others, and interact with the posts. Each user can create, edit, and manage their profile with options to set it as private or public. Users can post text messages limited to 280 characters, optionally include images in the posts, and have the ability to delete their posts. The platform will support interactions with posts, such as liking, retweeting, and replying, with a nested structure for the comments. Users can also search and filter posts or other users using keywords, hashtags, mentions, or view trending topics. Furthermore, users can follow and unfollow others, with a timeline view displaying posts from the users they follow and receiving notifications for new followers, likes, retweets, replies, and mentions. The service will also facilitate private messaging between users, with options to block or unblock users. Finally, the platform will offer user recommendations for following based on interests, activity, and mutual followers and showcase trending topics, which can be viewed globally or sorted by location.

3. Online Chat App: This task involves implementing a real-time online chat application. The GCS must support user registration and authentication functionalities, including email sign-up and forgotten password recovery. Users should be able to set profile pictures and status messages, with privacy settings to control visibility. The application should provide options for contact management (block/unblock contacts and group management), real-time text messaging with read receipts, end-to-end encryption, image sharing, and support for emojis, GIFs, and stickers. Group chat functionality should allow the creation of group chats with assigned names and pictures, participant management, and admin role assignments and permissions. Users should be able to post image statuses that are visible for a limited duration, with the ability to control viewer access. The service should be accessible as a web application and support offline messaging, with queued messages sent upon connectivity restoration and visible online/offline user statuses.

4. Recipe App: This task focuses on creating a service that allows users to submit, share, and discover recipes. Key features include the ability for users to submit recipes complete with ingredients, instructions, and images; options for categorizing recipes by cuisine type or dietary restrictions; and functionalities for editing or deleting submissions. The platform also supports searching for recipes based on various criteria such as ingredients or recipe name, and categorizing recipes by meal type or dietary needs. User account creation and management are integral, allowing for saving of favorite recipes and displaying user profiles with their submitted and favorite recipes. Additional features include a rating system where users can rate recipes on a 5-star scale and write reviews, a community aspect allowing users to follow others and see updates in a feed, and the sharing of recipes on social media platforms. An administrative dashboard for managing content, monitoring site usage, and user engagement is also included, alongside a system for generating recipe recommendations based on user preferences and past activity.

5. Event Planner App: This task involves developing a web-based application to assist users in organizing and managing various aspects of event planning. The application enables users to create and manage events, specifying details like event type, date, time, and customizations such as themes and color schemes. A calendar view for managing multiple events is included. Users can search for and book venues through the application, with integration of maps for venue locations. Guest list management is facilitated with features for creating, importing, exporting, and RSVP tracking. The platform connects users with event service providers like caterers and decorators, offering vendor profile viewing, comparison, and in-app messaging for coordination. Budget management tools allow users to set, track, and receive alerts for budget overruns. User account features include personal profile creation, customization, and access to past and upcoming events. Automated notifications and reminders for event milestones and tasks are part of the system. Reporting and analytics capabilities are provided for event success metrics, along with feedback collection from guests and vendors post-event. An administrative dashboard allows for the monitoring and management of user activities, system performance, and vendor listings. Additionally, the tool emphasizes security and data privacy, including secure payment gateway integration.

6. Financial Tracking App: This task involves developing a comprehensive tool for managing personal finances. It should include functionalities for tracking expenses, incomes, and investments, as well as setting and adjusting budget goals. Key features include the ability for users to create and manage a personal account with secure linking of bank accounts and multi-factor authentication. The application should support both manual and automatic import of expenses and incomes, categorization of these entries, and visualization of their history. Budget management is a crucial aspect, with capabilities to set monthly budget goals, receive alerts when nearing these limits, and analyze spending patterns to suggest adjustments. The integration with investment accounts to track performance and balance, along with an overview of asset allocation, is also required. Additionally, the application should generate financial reports, like monthly summaries, and provide customizable alerts for unusual spending or important reminders.

Each method receives the same user-specified feature requirements, which are given below for each environment task, and produces a codebase output, which we then evaluate using our evaluation methodology, which is fully detailed in Appendix G. The following user-specified input prompts for each task are:

## URL Shortener App, user-specified feature requirements input prompt:

```markdown
### ** O n l i n e URL S h o r t e n i n g S e r v i c e **
** Overview * * :
A s e r v i c e t h a t a l l o w s u s e r s t o s u b m i t l o n g URLs a n d t h e n r e c e i v e a s h o r t e n e d v e r s i o n o f t h a t URL f o r e a s e o f s h a r i n g .
** F u n c t i o n a l R e q u i r e m e n t s t o i m p l e m e n t * * :
1 . **URL S h o r t e n i n g * * :
− [ ] 1 . 1 . U s e r s c a n i n p u t a URL t o b e s h o r t e n e d .
[ ] 1 . 2 . The s y s t e m v a l i d a t e s t h a t t h e URL i s a c t i v e a n d l e g i t i m a t e .
[ ] 1 . 3 . The s y s t e m g e n e r a t e s a u n i q u e s h o r t e n e d URL .
] 1 . 4 . U s e r s c a n c h o o s e c u s t o m s h o r t l i n k s ( s u b j e c t t o a v a i l a b i l i t y ) .
2 . R e d i r e c t i o n :
− [ ] 2 . 1 . A c c e s s i n g t h e s h o r t e n e d URL r e d i r e c t s t o t h e o r i g i n a l URL .
3 . A n a l y t i c s :
− [ ] 3 . 1 . U s e r s c a n v i e w s t a t i s t i c s a b o u t t h e i r s h o r t e n e d URLs .
3 . 2 . View n u m b e r o f c l i c k s .
3 . 3 . View d a t e / t i m e o f e a c h c l i c k .
[ ] 3 . 4 . View g e o g r a p h i c a l l o c a t i o n o f t h e c l i c k e r .
4 . User A c c o u n t s :
− [ ] 4 . 1 . U s e r s c a n c r e a t e a c c o u n t s .
[ ] 4 . 2 . A c c o u n t h o l d e r s c a n v i e w a l l t h e i r s h o r t e n e d URLs .
[ 4 . 3 . A c c o u n t h o l d e r s c a n e d i t o r d e l e t e t h e i r s h o r t e n e d URLs .
4 . 4 . A c c o u n t h o l d e r s c a n v i e w a n a l y t i c s f o r a l l t h e i r s h o r t e n e d URLs
5 . Admin Dashboard :
[ ] 5 . 1 . A d m i n i s t r a t o r s c a n v i e w a l l s h o r t e n e d URLs .
− [ ] 5 . 2 . A d m i n i s t r a t o r s c a n d e l e t e a n y URL o r u s e r a c c o u n t .
5 . 3 . A d m i n i s t r a t o r s c a n m o n i t o r s y s t e m p e r f o r m a n c e a n d a n a l y t i c s .
6 . E x p i r a t i o n :
− [ ] 6 . 1 . U s e r s c a n s e t a n e x p i r a t i o n d a t e / t i m e f o r t h e s h o r t e n e d URL .
```

## Online Microblogging App, user-specified feature requirements input prompt:

\*\* O n l i n e M i c r o b l o g g i n g S e r v i c e (OMS) − D e s c r i p t i o n & R e q u i r e m e n t s \*\*

User Management :   
1 . \*\* R e g i s t r a t i o n & A u t h e n t i c a t i o n : \* \*   
[ ] A llo w u s e r s t o r e g i s t e r u s i n g e m a i l , u s e r n a m e , a n d p a s s w o r d .   
O p t i o n t o r e s e t f o r g o t t e n p a s s w o r d s .   
S e c u r e a u t h e n t i c a t i o n u s i n g JWT o r s i m i l a r p r o t o c o l s .   
2 . \*\* P r o f i l e Management : \* \*   
− [ ] U s e r s c a n e d i t t h e i r p r o f i l e i n f o r m a t i o n : p r o f i l e p i c t u r e , b i o , w e b s i t e l i n k , a n d l o c a t i o n .   
− [ ] O p t i o n t o make p r o f i l e p r i v a t e o r p u b l i c .

```csv
P o s t i n g & C o n t e n t M a n a g e m e n t :
1 . C r e a t i n g P o s t s ( T w e e t s ) :
− [ ] A l l o w u s e r s t o c r e a t e t e x t − b a s e d p o s t s w i t h a l i m i t o f 2 8 0 c h a r a c t e r s .
[ ] O p t i o n t o i n c l u d e i m a g e s i n p o s t s .
U s e r s c a n d e l e t e t h e i r own p o s t s .
2 . ** I n t e r a c t i n g w i t h P o s t s : * *
− [ ] U s e r s c a n l i k e , r e t w e e t , a n d r e p l y t o p o s t s .
− [ ] N e s t e d comment s t r u c t u r e f o r p o s t r e p l i e s .
3 . ** C o n t e n t F i l t e r i n g & S e a r c h : * *
− [ ] U s e r s c a n s e a r c h f o r s p e c i f i c p o s t s o r u s e r s u s i n g k e y w o r d s .
− [ ] F i l t e r o p t i o n b a s e d on h a s h t a g s , u s e r m e n t i o n s , o r t r e n d i n g t o p i c s .
```

3 . S o c i a l I n t e r a c t i o n :   
1 . \*\* F o l l o w i n g & F o l l o w e r s : \* \*   
[ ] U s e r s c a n f o l l o w / u n f o l l o w o t h e r u s e r s .   
A t i m e l i n e v i e w d i s p l a y s p o s t s f r o m f o l l o w e d u s e r s .   
[ ] U s e r s r e c e i v e n o t i f i c a t i o n s f o r new f o l l o w e r s .   
2 . \*\* D i r e c t M e s s a g i n g : \* \*   
[ ] P r i v a t e c o n v e r s a t i o n t h r e a d s b e t w e e n u s e r s .   
O p t i o n t o b l o c k / u n b l o c k u s e r s f r o m m e s s a g i n g .   
3 . N o t i f i c a t i o n s :   
− [ ] U s e r s a r e n o t i f i e d o f l i k e s , r e t w e e t s , r e p l i e s , a n d m e n t i o n s   
4 . T r e n d i n g & D i s c o v e r y :   
1 . T r e n d i n g T o p i c s :   
− [ ] S y s t e m i d e n t i f i e s a n d d i s p l a y s t r e n d i n g h a s h t a g s o r t o p i c s b a s e d on v o l u m e a n d v e l o c i t y o f m e n t i o n s .   
] T r e n d i n g t o p i c s c a n b e s o r t e d b a s e d on l o c a t i o n o r g l o b a l l y .   
2 . User Recommendations :   
− [ ] Recommend u s e r s t o f o l l o w b a s e d on i n t e r e s t s , a c t i v i t y , a n d m u t u a l f o l l o w e r s .

## Online Chat App, user-specified feature requirements input prompt:

## G l o b a l C h a t S e r v i c e ( GCS )

## F u n c t i o n a l R e q u i r e m e n t s t o i m p l e m e n t :

```csv
U s e r R e g i s t r a t i o n a n d A u t h e n t i c a t i o n :
− [ ] 1 . 1 . S i g n u p u s i n g e m a i l .
− [ ] 1 . 2 . F o r g o t t e n p a s s w o r d r e c o v e r y .
U s e r P r o f i l e :
− [ ] 2 . 1 . A l l o w u s e r s t o s e t p r o f i l e p i c t u r e s a n d s t a t u s m e s s a g e s .
− [ ] 2 . 2 . P r i v a c y s e t t i n g s f o r who c a n s e e u s e r d e t a i l s o r l a s t s e e n s t a t u s
C o n t a c t Management :
− [ ] 3 . 1 . B l o c k / u n b l o c k c o n t a c t s .
− [ ] 3 . 2 . C r e a t e , e d i t , a n d m a n a g e g r o u p s .
Messaging :
[ ] 4 . 1 . S e n d a n d r e c e i v e r e a l − t i m e t e x t m e s s a g e s .
4 . 2 . M e s s a g e r e a d r e c e i p t s ( b l u e t i c k s o r e q u i v a l e n t ) .
4 . 3 . End − t o − e n d e n c r y p t i o n f o r s e c u r i t y .
] 4 . 4 . I m a g e s h a r i n g .
4 . 5 . E m o j i s , GI F s , a n d s t i c k e r s s u p p o r t .
Group C h a t s :
− [ ] 5 . 1 . C r e a t e g r o u p c h a t s w i t h a name a n d p i c t u r e .
] 5 . 2 . Add o r r e m o v e p a r t i c i p a n t s .
[ ] 5 . 3 . Admin r o l e s a n d p e r m i s s i o n s .
S t a t u s / S t o r y F e a t u r e :
− [ ] 6 . 1 . A l l o w u s e r s t o p o s t i m a g e s t a t u s e s v i s i b l e f o r a l i m i t e d t i m e .
6 . 2 . C o n t r o l who c a n s e e t h e s t a t u s .
Web A p p l i c a t i o n :
− [ ] 7 . 1 . Web− b a s e d v e r s i o n a c c e s s i b l e f r o m b r o w s e r s .
C o n n e c t i v i t y a n d O f f l i n e Mode :
− [ ] 8 . 1 . M e s s a g e q u e u i n g f o r when t h e u s e r i s o f f l i n e ; m e s s a g e s a r e s e n t o n c e c o n n e c t i v i t y i s r e s t o r e d .
− [ ] 8 . 2 . D i s p l a y o n l i n e / o f f l i n e s t a t u s .
```

## Recipe App, user-specified feature requirements input prompt:

## ### R e c i p e S h a r i n g P l a t f o r m

## F u n c t i o n a l R e q u i r e m e n t s t o i m p l e m e n t :

1 . R e c i p e S u b m i s s i o n and Management :   
− 1 . 1 . U s e r s c a n s u b m i t r e c i p e s w i t h i n g r e d i e n t s , i n s t r u c t i o n s , a n d i m a g e s .   
− 1 . 2 . R e c i p e s u b m i s s i o n s i n c l u d e o p t i o n s f o r c a t e g o r i z a t i o n ( e . g . , c u i s i n e t y p e , d i e t a r y r e s t r i c t i o n s ) .   
1 . 3 . U s e r s c a n e d i t o r d e l e t e t h e i r s u b m i t t e d r e c i p e s .   
1 . 4 . R e c i p e f o r m a t v a l i d a t i o n t o e n s u r e c o m p l e t e i n f o r m a t i o n .

## 2 . S e a r c h a n d C a t e g o r i z a t i o n :

2 . 1 . U s e r s c a n s e a r c h f o r r e c i p e s b a s e d on i n g r e d i e n t s , r e c i p e name , o r c a t e g o r i e s .   
2 . 2 . C a t e g o r i z a t i o n o f r e c i p e s b y t y p e ( e . g . , b r e a k f a s t , l u n c h , d i n n e r ) , c u i s i n e , o r d i e t a r y n e e d s ( e . g . , v e g a n ,   
g l u t e n − f r e e ) .

## 3 . U s e r A c c o u n t s a n d P r o f i l e s :

## 4 . R a t i n g s and Reviews :

## 5 . Community F e a t u r e s :

[ ] 5 . 1 . U s e r s c a n f o l l o w o t h e r u s e r s o r c h e f s . ] 5 . 2 . F e e d s h o w i n g r e c e n t a c t i v i t y o f f o l l o w e d u s e r s ( new r e c i p e s , r a t i n g s ) .   
[ ] 5 . 3 . O p t i o n t o s h a r e r e c i p e s on s o c i a l m e d i a p l a t f o r m s .

## 6 . Admin Dashboard :

## 7 . R e c i p e Recommendations :

− [ ] 7 . 1 . S y s t e m g e n e r a t e s r e c i p e r e c o m m e n d a t i o n s b a s e d on u s e r p r e f e r e n c e s a n d p a s t a c t i v i t y .   
− [ ] 7 . 2 . U s e r s r e c e i v e n o t i f i c a t i o n s f o r new r e c i p e s i n t h e i r i n t e r e s t a r e a s .

## Event Planner App, user-specified feature requirements input prompt:

```markdown
### Custom Ev en t P l a n n e r Tool
Overview :
A web − b a s e d a p p l i c a t i o n d e s i g n e d t o a s s i s t u s e r s i n o r g a n i z i n g a n d m a n a g i n g v a r i o u s a s p e c t s o f e v e n t p l a n n i n g . T h i s
p r o v i d e f u n c t i o n a l i t i e s f o r s e l e c t i n g e v e n t t y p e s , m a n a g i n g g u e s t l i s t s , s o u r c i n g v e n u e s , a n d c o o r d i n a t i n g w
p r o v i d e r s .
F u n c t i o n a l R e q u i r e m e n t s t o I m p l e m e n t :
1 . ** Eve n t C r e a t i o n and Management * * :
[ ] 1 . 1 . U s e r s c a n c r e a t e a new e v e n t , s p e c i f y i n g d e t a i l s l i k e e v e n t t y p e , d a t e , a n d t i m e .
] 1 . 2 . The s y s t e m a l l o w s f o r c u s t o m i z a t i o n o f e v e n t s ( e . g . , t h e m e s , c o l o r s c h e m e s ) .
[ ] 1 . 3 . U s e r s c a n u p d a t e o r m o d i f y e v e n t d e t a i l s a s n e e d e d .
[ ] 1 . 4 . A c a l e n d a r v i e w i s a v a i l a b l e f o r u s e r s t o m a n a g e m u l t i p l e e v e n t s .
2 . ** Venue S o u r c i n g * * :
[ ] 2 . 1 . U s e r s c a n s e a r c h f o r v e n u e s b a s e d on l o c a t i o n , c a p a c i t y , a n d t y p e .
[ ] 2 . 2 . I n t e g r a t i o n o f maps f o r v e n u e l o c a t i o n s .
[ ] 2 . 3 . U s e r s c a n b o o k v e n u e s d i r e c t l y t h r o u g h t h e a p p l i c a t i o n .
3 . G u e s t L i s t Management :
[ ] 3 . 1 . U s e r s c a n c r e a t e a n d m a n a g e g u e s t l i s t s
] 3 . 2 . I m p o r t / e x p o r t g u e s t l i s t f e a t u r e .
3 . 3 . RSVP t r a c k i n g and management .
4 . V e n d o r C o o r d i n a t i o n :
− [ ] 4 . 1 . P l a t f o r m t o c o n n e c t w i t h v a r i o u s e v e n t s e r v i c e p r o v i d e r s ( c a t e r e r s , d e c o r a t o r s ) .
− [ ] 4 . 2 . U s e r s c a n v i e w a n d c o m p a r e v e n d o r p r o f i l e s a n d r e v i e w s .
− [ ] 4 . 3 . In − app m e s s a g i n g s y s t e m f o r v e n d o r c o m m u n i c a t i o n .
5 . Budget Management :
− [ ] 5 . 1 . U s e r s c a n s e t a b u d g e t f o r t h e e v e n t .
] 5 . 2 . B u d g e t t r a c k i n g a n d b r e a k d o w n by c a t e g o r i e s ( v e n u e , c a t e r i n g , e t c . ) .
] 5 . 3 . A l e r t s f o r b u d g e t o v e r r u n s .
6 . U s e r A c c o u n t s a n d P r o f i l e s :
[ ] 6 . 1 . U s e r s c a n c r e a t e p e r s o n a l p r o f i l e s .
[ ] 6 . 2 . P r o f i l e c u s t o m i z a t i o n t o r e f l e c t e v e n t p l a n n i n g p r e f e r e n c e s .
− [ ] 6 . 3 . S a v i n g a n d a c c e s s i n g p a s t a n d u p c o m i n g e v e n t s .
7 . N o t i f i c a t i o n s a n d R e m i n d e r s :
− [ ] 7 . 1 . A u t o m a t e d e m a i l / SMS n o t i f i c a t i o n s f o r e v e n t m i l e s t o n e s
− [ ] 7 . 2 . C u s t o m i z a b l e r e m i n d e r s f o r t a s k s a n d d e a d l i n e s .
8 . R e p o r t i n g a n d A n a l y t i c s :
− [ ] 8 . 1 . G e n e r a t e r e p o r t s o n e v e n t s u c c e s s m e t r i c s ( a t t e n d a n c e , b u d g e t a d h e r e n c e ) .
[ ] 8 . 2 . F e e d b a c k c o l l e c t i o n f r o m g u e s t s a n d v e n d o r s p o s t − e v e n t .
9 . Admin Dashboard :
] 9 . 1 . A d m i n i s t r a t o r s c a n m o n i t o r a n d m a n a g e u s e r a c t i v i t i e s .
− [ 9 . 2 . S y s t e m p e r f o r m a n c e a n a l y t i c s a n d u s e r e n g a g e m e n t s t a t i s t i c s .
− [ ] 9 . 3 . Manage v e n d o r l i s t i n g s a n d p l a t f o r m c o n t e n t .
1 0 . ** S e c u r i t y a n d D a t a P r i v a c y * * :
[ ] 1 0 . 1 . E n s u r i n g u s e r d a t a p r o t e c t i o n a n d p r i v a c y .
[ ] 1 0 . 2 . S e c u r e p a y m e n t g a t e w a y i n t e g r a t i o n f o r t r a n s a c t i o n s .
```

## Financial Tracking App, user-specified feature requirements input prompt:

```markdown
# # # P e r s o n a l F i n a n c e T r a c k i n g A p p l i c a t i o n
Overview :
A c o m p r e h e n s i v e t o o l f o r m a n a g i n g p e r s o n a l f i n a n c e s , i n c l u d i n g t r a c k i n g e x p e n s e s , i n c o m e s , i n v e s t m e n t s , a n d s e t t i n g b u d g e t g o a l s .
F u n c t i o n a l R e q u i r e m e n t s t o i m p l e m e n t :
1 . A c c o u n t a n d S e c u r i t y :
[ ] 1 . 1 . U s e r s c a n c r e a t e a n d m a n a g e t h e i r p e r s o n a l a c c o u n t .
− [ ] 1 . 2 . S e c u r e l i n k i n g o f b a n k a c c o u n t s .
− [ ] 1 . 3 . M u l t i − f a c t o r a u t h e n t i c a t i o n f o r e n h a n c e d s e c u r i t y
2 . Expense and Income T r a c k i n g :
[ ] 2 . 1 . M a n u a l a n d a u t o m a t i c i m p o r t o f e x p e n s e s a n d i n c o m e s .
− [ ] 2 . 2 . C a t e g o r i z a t i o n o f e x p e n s e s a n d i n c o m e s o u r c e s .
− [ ] 2 . 3 . V i s u a l i z a t i o n o f e x p e n s e a n d i n c o m e h i s t o r y .
3 . ** Budget Management * * :
− [ ] 3 . 1 . S e t t i n g a n d a d j u s t i n g m o n t h l y b u d g e t g o a l s .
[ ] 3 . 2 . A l e r t s f o r n e a r i n g b u d g e t l i m i t s .
[ ] 3 . 3 . A n a l y s i s o f s p e n d i n g p a t t e r n s t o s u g g e s t b u d g e t a d j u s t m e n t s .
4 . I n v e s t m e n t O v e r v i e w :
[ ] 4 . 1 . I n t e g r a t i o n w i t h i n v e s t m e n t a c c o u n t s .
[ ] 4 . 2 . T r a c k i n g i n v e s t m e n t p e r f o r m a n c e a n d b a l a n c e .
− [ ] 4 . 3 . O v e r v i e w o f a s s e t a l l o c a t i o n .
5 . R e p o r t s a n d A l e r t s :
− [ ] 5 . 1 . G e n e r a t i o n o f f i n a n c i a l r e p o r t s ( e . g . , m o n t h l y s u m m a r i e s )
− [ ] 5 . 2 . C u s t o m i z a b l e a l e r t s f o r u n u s u a l s p e n d i n g o r i m p o r t a n t r e m i n d e r s .
```

## E.2 HUMANEVAL BENCHMARK

We use the standard HumanEval benchmark, as introduced by Chen et al. (2021). This benchmark evaluates the task of the underlying LLM-based method to generate standalone Python functions from a given docstring, and evaluates the correctness of the generated code function through held out unit tests. The benchmark consists of 164 hand-written programming problems with unit tests, which aim to assess language comprehension, algorithms, and simple mathematics, of which the authors (Chen et al., 2021) compare these to simple software interview questions.

## F BENCHMARK METHOD IMPLEMENTATION DETAILS

In the following, we detail all implementation details of our benchmark methods, including that of the full low-level implementation details of Code-L2MAC in Appendix F.1.

AutoGPT. We chose to compare against the most competitive and popular autonomous agent LLM with memory method, that of AutoGPT (Richards, 2023). This uses GPT4 as the underlying LLM. Like other autonomous agents, the first step of AutoGPT is to summarize the user-specified task into a name, role, and five one-sentence goals for the agent to complete; this summary is kept in context throughout execution. At each step, until the goals have been achieved, the underlying LLM receives a ReACT (Yao et al., 2022) message template to reason, plan, and act by selecting the next tool to call. Specifically, we used the latest stable version of AutoGPT, 0.4.7, enabled local tool execution, and disabled searching the web for answers to ensure a fair comparison. It is interesting to note that AutoGPT also has tool functionality and has tools to read, write, and list files in a local file store—making it the most competitive and applicable baseline to compare against. Although other autonomous agent LLM methods exist, they do not possess the ability to read or write to an external file store in the same manner as AutoGPT. Importantly, AutoGPT, when running, would sometimes have runs where it would fail to complete the task, i.e., fail to output any code or get stuck in an infinite loop. When such failures occurred, we classified these runs failures and excluded them from the results. This method defaults to use the LLM with a temperature of 0.

GPT4. We also chose to compare with the single GPT4 LLM (GPT4) (OpenAI, 2023), which we adapt to make it competitive by providing it with the same tools that Code–L2MAC uses, forming an ablation of just using an LLM processor without the control unit. Specifically, we provide it with exactly the same messages and experimental setup as Code-L2MAC, including the same system message and prompt format message; however, it is limited to only respond with one long single response that can fill up the entire context window Ct.

CodeT. We build upon our GPT4 method implementation above and implement CodeT a recent state-of-the-art method for code snippet generation (Chen et al., 2022). CodeT samples independent generated code outputs, and uses the same LLM to generate test cases for the code samples, it them executes the code samples using the generated test cases and performs a dual execution agreement, to return the output code sample that performs the best against the generated tests. To make this method more competitive when applied to large codebase generation tasks, it is possible generate a given codebase statisfying the user given feature requirements, however with many different possible implementation approaches (of splitting components, classes and across files and folders)—therefore instead of sampling tests independently of the generated codebase, we follow our setup with GPT4 and Code-L2MAC and generate a codebase and unit tests at the same time so they match the given implementation. We repeat this generation independently for n = 3 times, and run the codebase against the generated tests, and rank the codebases in order of the number of tests that pass, and return the codebase that passes the highest number of self generated tests.

Self-Refine. Similarly, we also build upon our GPT4 method implementation above and implement Self-Refine, another recent state-of-the-art method for code snippet generation (Madaan et al., 2023). Self-Refine, uses iterative self-refinement that alternates between using an underlying LLM to provide feedback and refine a given generated LLM output, to create a higher quality output. Specifically, given an initial LLM generated codebase output, we use the same LLM to provide verbal feedback on how it could have improved the codebase to the given original task, and then using this verbal feedback within the same context window, we refine the previously generated codebase. This process is repeated $n = 3$ times, as in line with $n = 3$ used in by Madaan et al. (2023). We followed the same coding task setup as in Madaan et al. (2023) to make this method competitive. Furthermore to make it more competitive, after generating the codebase, we use the same error checking methods in Code-L2MAC and include in context the result of any code errors found and the result of any tests generated that are failing, so it can also use this signal to improve upon the generated codebase.

Reflexion. Likewise, we also build upon our GPT4 method implementation above and implement Reflexion, another recent state-of-the-art method for code snippet generation (Madaan et al., 2023). Reflexion, another reflecting LLM approach, uses the same LLM to reflect on the trajectory (outputs of an LLM) once an environment episode (task) has been completed to provide verbal feedback on how the task could have been completed better. These verbal feedback signals are then persisted in an episodic append-only (list) memory buffer and are given in context upon the next episode of completing the task from scratch (re-starting the environment). Reflexion converts a binary or scalar feedback from the environment into its verbal feedback, that is then used as additional context for the LLM in the next episode. To make Reflexion more competitive, after generating the codebase we use the same error checking methods in Code-L2MAC and include in context the result of any code errors found and the result of any tests generated that are failing appended to the context after generating the codebase. Specifically, Reflexion follows an iterative process where it generates a codebase given the same initial prompt as Code-L2MAC and existing methods, then it is asked to evaluate the codebase for the number of features fully and functionally implemented as listed in the input prompt, giving a scalar score (the reward signal for the environment), which is apended to the context window. This is followed by the self-reflection step, where it is asked to analyze the trajectory (codebase, the evaluated scalar feedback) to produce a summary on how it could improve (verbal experience feedback for that episode). This summary is then stored in an external buffer. We then reset the context window window, starting with the initial task prompt plus the verbal lessons from the external buffer, and repeat this iterative process n = 3 times be be competitive. We follow Reflexion’s code programming setup and prompts, adapting them to our task to be more competitive.

Code-L2MAC. Our proposed method uses the message and function definitions defined in Appendix F.1. Using these, it then follows the pseudocode for the control unit, as outlined in Algorithm 1, and generates a prompt program of instructions and iterates each dialog turn of the control unit control flow loop until all instructions are complete. There are a few other minor implementation details, which we also detail here. We impose a maximum number of times an instruction can be re-tried $r _ { \mathrm { M a x } }$ , with a new context window when, during the execution of that instruction, it attempts to exceed the context window, forcing the context window to restart the instruction with the summary of the current progress made—we empirically set $r _ { \mathrm { M a x } } = 3 0$ . When the current number of retries exceeds $r _ { \mathrm { M a x } } .$ , we class this run as a failure and exclude its results. Importantly, at such a failure, the method could ideally either await human input for correction or continue with an errored state. We used the LLM of GPT4-0613, and when using it throughout, set the temperature to 0.01. Additionally, another implementation detail is that when the CU detects that it is stuck in a loop repeating the same two messages over again by comparing the most recent two messages in the context window, it increases the temperature of the LLM by 0.1 and continues until the temperature caps at 1.0, and then after it exits the loop reducing the temperature back to 0.01. This is to have a form of simulated annealing of introducing randomness to escape the local minima. In the following, Appendix F.1, we detail special message templates exactly.

## F.1 CODE-L2MAC LOW LEVEL IMPLEMENTATION DETAILS

We follow the same setup as outlined in Appendix C, and in the following, we provide exact low-level implementation details. We use GPT-4-0613, which has fine-tuned support for function calls, and use the function definition file of the following.

Function definitions:

```csv
{
" name " : " p r o v i d e _ d e t a i l e d _ s u b _ t a s k _ s t e p s _ f o r _ s u b _ a g e n t s " ,
" d e s c r i p t i o n " : " F o r p r o d u c i n g a s t e p −by − s t e p p l a n , w h e r e e a c h s t e p p a r a g r a p h i s a d e t a i l e d s u b − t a s k s t e p f o r a s e p a r a t e
s u b − a g e n t ( l a r g e l a n g u a g e m o d e l a g e n t ) t o c o m p l e t e . W i t h i n e a c h d e t a i l e d s t e p p a r a g r a p h , a l w a y s i n c l u d e a l a s t
s e n t e n c e t o c r e a t e a n d r u n t e s t s when i m p l e m e n t i n g o r w r i t i n g c o d e i n t h a t same s t e p . " ,
" p a r a m e t e r s " : {
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " : {
" s t e p s " : {
" t y p e " : " a r r a y "
" d e s c r i p t i o n " : " L i s t o f s t r i n g s , w h e r e e a c h s t r i n g i s a s e p a r a t e s t e p s u b − t a s k p a r a g r a p h f o r a s e p a r a t e s u b
a g e n t t o c o m p l e t e . W i t h i n e a c h d e t a i l e d s t e p p a r a g r a p h , a l w a y s i n c l u d e a l a s t s e n t e n c e t o c r e a t e a n d
r u n t e s t s when i m p l e m e n t i n g o r w r i t i n g c o d e i n t h a t same s t e p . " ,
" i t e m s " :
" t y p e " : " s t r i n g " ,

} ,
} ,
" r e q u i r e d " : [ " s t e p s " ] ,
} ,
} ,
" name " : " s u b _ t a s k _ s t e p _ c o m p l e t e " ,
```

```csv
" d e s c r i p t i o n " : " C a l l t h i s f u n c t i o n when t h e u s e r s p e c i f i e d s u b t a s k s t e p h a s b e e n c o m p l e t e d . " ,
" p a r a m e t e r s " : {
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " : { } ,
}
" name " : " v i e w _ f i l e s " ,
" d e s c r i p t i o n " : " P r i n t o u t t h e f i l e c o n t e n t s i n t o t h e r e s p o n s e t o v i e w . " ,
" p a r a m e t e r s " :
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " :
" f i l e s " :
" t y p e " : " a r r a y " ,
" d e s c r i p t i o n " : " l i s t o f t h e f i l e s t o v i e w " ,
" i t e m s " :
" t y p e " : " s t r i n g " # a s s u m i n g e a c h f i l e i s r e p r e s e n t e d a s a s t r i n g
}
} ,
} ,
" r e q u i r e d " : [ " f i l e s " ] ,
" name " : " r u n _ p y t h o n _ f i l e " ,
" d e s c r i p t i o n " : " Run p y t h o n f i l e a n d r e t u r n t h e o u t p u t t o t h e r e s p o n s e t o v i e w . T h a t i s w i t h ’ p y t h o n 3 f i l e _ n a m e _ t o _ r u n
" p a r a m e t e r s " : {
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " :
" f i l e _ n a m e _ t o _ r u n " : {
" t y p e " : " s t r i n g "
" d e s c r i p t i o n " : " f i l e name t o r u n " ,
} ,
" a r g u m e n t s " :
" t y p e " : " a r r a y "
" d e s c r i p t i o n " : " o p t i o n a l r u n a r g u m e n t s " ,
" i t e m s " :
" t y p e " : " s t r i n g "
}
} ,
" r e q u i r e d " : [ " f i l e _ n a m e _ t o _ r u n " ] ,
}
" name " : " p y t e s t _ f i l e s " ,
" d e s c r i p t i o n " : " Run p y t e s t on t h e i n p u t f i l e n a m e s a n d p r i n t o u t t h e r e s u l t s t o t h e r e s p o n s e t o v i e w . I f no f i l e n a m e s
a r e p r o v i d e d , p y t e s t r u n s o n a l l f i l e s . " ,
" p a r a m e t e r s " :
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " :
" f i l e s _ t o _ t e s t " : {
" t y p e " : " a r r a y "
" d e s c r i p t i o n " : " f i l e n a m e s t o r u n p y t e s t on " ,
" i t e m s " :
" t y p e " : " s t r i n g "
} ,
} ,
" name " : " w r i t e _ f i l e s " ,
" d e s c r i p t i o n " : " W r i t e o u t m u l t i p l e f i l e s a n d i t w i l l b e c o m b i n e d i n t o t h e e x i s t i n g c o d e b a s e . A l w a y s o u t p u t t h e w h o l e
f i l e . You a l w a y s i n d e n t c o d e w i t h t a b s . " ,
" p a r a m e t e r s " : {
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " :
" f i l e s _ a n d _ c o n t e n t s " : {
" t y p e " : " a r r a y
" d e s c r i p t i o n " : ’ l i s t o f f i l e s a n d t h e i r c o n t e n t s . ’ ,
" i t e m s " :
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " : {
" f i l e _ p a t h " : {
" t y p e " : " s t r i n g "
" d e s c r i p t i o n " : " P a t h t o t h e f i l e "
" f i l e _ c o n t e n t s " : {
" t y p e " : " s t r i n g "
" d e s c r i p t i o n " : " C o n t e n t s o f t h e f i l e "
" r e q u i r e d " : [ " f i l e _ p a t h " , " f i l e _ c o n t e n t s " ]
" r e q u i r e d " : [ " f i l e s _ a n d _ c o n t e n t s " ] ,

" name " : " d e l e t e _ f i l e s " ,
" d e s c r i p t i o n " : " D e l e t e f i l e s . S p e c i f y t h e f i l e names , a n d t h e s e f i l e s w i l l b e d e l e t e d . I f y o u s p e c i f y t h e f i l e name ’ − 1
a l l f i l e s i n t h e f o l d e r w i l l b e d e l e t e d . " ,
" p a r a m e t e r s " :
" t y p e " : " o b j e c t " ,
" p r o p e r t i e s " : {
" f i l e s " : {
" t y p e " : " a r r a y " ,
" d e s c r i p t i o n " : " l i s t o f t h e f i l e s t o d e l e t e . I f y o u p r o v i d e a f i l e name o f ’ − 1 ’ a l l f i l e s i n t h e f o l d e r w i l l
b e d e l e t e d . " ,
" i t e m s " : {
" t y p e " : " s t r i n g "
}
} ,
} ,
```

With Code-L2MAC we use the following system message (OpenAI, 2023) $M _ { s } ,$ , and include it all context windows Ct, which is standard to do so (OpenAI, 2023).

System message Ms:

```csv
O b j e c t i v e : W r i t e c o d e f o r a l a r g e s y s t e m d e s i g n t a s k .
P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s
O n l y u s e t h e f u n c t i o n s you h a v e b e e n p r o v i d e d w i t h .
O n l y u s e t h e ‘ w r i t e _ f i l e s ‘ t o o u t p u t c o d e .
You m u s t a c t a u t o n o m o u s l y a n d y o u w i l l r e c e i v e no human i n p u t a t a n y s t a g e . You h a v e t o r e t u r n a s o u t p u t t h e c o m p l e t e c o d e f o r
c o m p l e t i n g t h i s t a s k , a n d c o r r e c t l y i n c o r p o r a t e i t i n t o t h e e x i s t i n g c o d e b a s e .
You a l w a y s w r i t e o u t t h e w h o l e f i l e c o n t e n t s . You a l w a y s i n d e n t c o d e w i t h t a b s .
P l e a s e a l w a y s v i e w t h e f i l e s b e f o r e w r i t i n g t o them , t o make s u r e y o u a r e w r i t i n g t o t h e c o r r e c t f i l e s .
When w r i t i n g a t e s t , make t h e f i l e n a m e s t a r t w i t h t h e p r e f i x ’ t e s t _ ’
P r o v i d e t h e m i n i m a l c o d e n e c e s s a r y t o a c h i e v e t h e t a s k c o n d i t i o n e d on t h e e x i s t i n g g e n e r a t e d c o d e −−− i n c l u d i n g c h a n g i n g t h e e x i s t i n g
g e n e r a t e d c o d e .
You c a n n o t v i s u a l i z e a n y g r a p h i c a l o u t p u t . You e x i s t w i t h i n a A c t o r Model m a c h i n e , a n d when y o u l i s t o u t s t e p s , e a c h s t e p w i l l b e
t a k e n by a new s e p a r a t e s u b − ChatGPT m o d e l . When y o u l i s t o u t a s u b − t a s k s t e p s , y o u c a n o p t i o n a l l y s p e c i f y t h e s u b − t a s k
v a l i d a t i o n t o c h e c k t h a t i t h a s b e e n c o m p l e t e d s u c c e s s f u l l y .
You c a n n o t u s e a n y d a t a b a s e s a s n o n e a r e s e t u p i n t h e l o c a l e n v i r o n m e n t , i n s t e a d mock a d a t a b a s e w i t h a n i n memory d i c t i o n a r y t o
s t o r e d a t a . No d a t a s a v e d t o d i s k w i l l p e r s i s t b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .
I f a t e s t i s f a i l i n g t h e e r r o r c o u l d b e t h e c o d e , o r t h e t e s t i s i n c o r r e c t , s o f e e l f r e e t o o v e r w r i t e a n d c h a n g e t h e t e s t s when t h e y
a r e i n c o r r e c t , t o make a l l t e s t s p a s s .
Use t h e f u n c t i o n s p r o v i d e d . When c a l l i n g f u n c t i o n s o n l y p r o v i d e a RFC8259 c o m p l i a n t JSON r e q u e s t f o l l o w i n g t h i s f o r m a t w i t h o u t
d e vi a ti o n .
```

# When Code-L2MAC self-programs its instructions initially, we provide it with the following prompt template to do so, which encapsulates the user message $M _ { u }$ , as ‘user\_specified\_feature\_requirements’. $M _ { c b }$ bootstrap instruction:

You w i l l g e t i n s t r u c t i o n s f o r c o d e t o w r i t e .   
F i r s t l a y o u t t h e n a m e s o f t h e c o r e c l a s s e s , f u n c t i o n s , m e t h o d s t h a t w i l l b e n e c e s s a r y , As w e l l a s a q u i c k comment on t h e i r p u r p o s e .   
Do n o t comment on w h a t e v e r y f i l e d o e s . P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s .   
You w i l l s t a r t w i t h t h e " e n t r y p o i n t " f i l e , t h e n go t o t h e o n e s t h a t a r e i m p o r t e d by t h a t f i l e , a n d s o on .   
P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s .   
F o l l o w a l a n g u a g e a n d f r a m e w o r k a p p r o p r i a t e b e s t p r a c t i c e f i l e n a m i n g c o n v e n t i o n .   
Make s u r e t h a t f i l e s c o n t a i n a l l i m p o r t s , t y p e s e t c . The c o d e s h o u l d b e f u l l y f u n c t i o n a l . Make s u r e t h a t c o d e i n d i f f e r e n t f i l e s   
a r e c o m p a t i b l e w i t h e a c h o t h e r .   
When w r i t i n g c o d e i f y o u a r e u n s u r e , w r i t e a p l a u s i b l e i m p l e m e n t a t i o n .   
I n c l u d e module d ep en d en c y o r p a c k a g e manager d epe nde n c y d e f i n i t i o n f i l e .   
U s e f u l t o know :   
F o r P y t h o n , y o u a l w a y s c r e a t e a n a p p r o p r i a t e r e q u i r e m e n t s . t x t f i l e .   
A l w a y s a d d a comment b r i e f l y d e s c r i b i n g t h e p u r p o s e o f t h e f u n c t i o n d e f i n i t i o n .   
Add c o m m e n t s e x p l a i n i n g v e r y c o m p l e x b i t s o f l o g i c .   
A l w a y s f o l l o w t h e b e s t p r a c t i c e s f o r t h e r e q u e s t e d l a n g u a g e s f o r f o l d e r / f i l e s t r u c t u r e a n d how t o p a c k a g e t h e p r o j e c t .   
You c a n u s e any p a c k a g e and any o t h e r p a c k a g e s you w i s h t o i n s t a l l .   
You c a n n o t u s e a n y d a t a b a s e s a s n o n e a r e s e t u p i n t h e l o c a l e n v i r o n m e n t , i n s t e a d mock a d a t a b a s e w i t h a n i n memory d i c t i o n a r y t o   
s t o r e d a t a . No d a t a s a v e d t o d i s k w i l l p e r s i s b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .   
When w r i t i n g a t e s t , make t h e f i l e n a m e s t a r t w i t h t h e p r e f i x ’ t e s t \_ ’ .   
P y t h o n t o o l b e l t p r e f e r e n c e s :   
− p y t e s t   
d a t a c l a s s e s   
f l a s k   
O b j e c t i v e : ‘ ‘ ‘   
{ u s e r \_ s p e c i f i e d \_ f e a t u r e \_ r e q u i r e m e n t s }   
U n d e r s t a n d t h e p r o b l e m , by c r e a t i n g a n e x t r e m e l y d e t a i l e d s t e p −by − s t e p p l a n , w h e r e e a c h s t e p i s l o n g ( m u l t i p l e s e n t e n c e s ) a n d i n   
t o t a l i n c l u d e s e v e r y s i n g l e f e a t u r e r e q u i r e m e n t s p e c i f i e d a b o v e , f e e l f r e e t o c o p y d i r e c t l y f r o m i t . Use no more t h a n 10   
s t e p s i n t h e p l a n . C r e a t e a d d i t i o n a l t e s t s , c h e c k s a n d e v a l u a t i o n a t e a c h s t e p when a p p l i c a b l e t o h e l p make a n e x c e l l e n t c o d e   
i m p l e m e n t a t i o n , w h e r e a l l t h e c o d e i s f u l l y f u n c t i o n a l . Use b e s t s o f t w a r e d e s i g n p r a c t i c e s , a n d y o u c a n o u t p u t l a r g e a m o u n t s   
o f c o d e a t o n c e . P l e a s e i n c l u d e a l a s t s e n t e n c e t o c r e a t e a n d r u n t e s t s when i m p l e m e n t i n g o r w r i t i n g c o d e i n t h a t same s t e p .   
You w i l l r e c e i v e no human i n p u t a t a n y s t a g e , s o y o u c a n n o t u s e a human t o t e s t . O n l y c r e a t e a d e t a i l e d p l a n t o b e g i n w i t h ,   
w h i c h i n c l u d e s d e s i g n i n g a n d r u n n i n g t e s t s t o c h e c k t h a t t h e y a l l p a s s . P l e a s e b e s u r e t o i n c l u d e a l l o f t h e s p e c i f i e d   
f e a t u r e r e q u i r e m e n t s i n t h e f o l l o w i n g p l a n .

Code-L2MAC also involves control messages of the following form.

$M _ { c c }$ Control cycle message of starting the instruction:

O b j e c t i v e : E x e c u t e s u b t a s k s t e p : { i n s t r u c t i o n } . \ n \ n N o t e : C o n d i t i o n a n y new c o d e f i l e s on t h e e x i s t i n g c o d e f i l e s : { l i s t \_ f i l e s ( ) } . F u l l y i m p l e m e n t t h e s e f e a t u r e s i n t h e c o d e , no p l a c e h o l d e r s . You c a n now o p t i o n a l l y v i e w t h e e x i s t i n g f i l e s i f y o u n e e d t o v i e w t h e m t o c o m p l e t e t h e c u r r e n t t a s k s t e p . You h a v e a l i m i t e d c o n t e x t window s o b e s e l e c t i v e a b o u t w h i c h f i l e s y o u v i e w , o n l y v i e w t h e f i l e s y o u t h i n k y o u m i g h t n e e d t o v i e w . \ n \ nSummary o u t p u t o f p r e v i o u s s t e p : " " { p r e v i o u s \_ i n s t r u c t i o n \_ o u t p u t \_ s u m m a r y } " " \ n \ n R e s p o n d now o n l y w i t h a f u n c t i o n c a l l o f o n e o f t h e f o l l o w i n g f u n c t i o n s p r o v i d e d : { f u n c t i o n \_ n a m e s ( ) } , a n d i f y o u w a n t t o o u t p u t c o d e o n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ f u n c t i o n t o o u t p u t c o d e .

Here instruction is the current instruction of operation, ‘list\_files()’ a list files tool function, previous\_instruction\_output\_summary is the summary message $M _ { r s }$ , and ‘function\_names()’ lists the current function names that the LLM can request.

Mcc Control cycle message of continuing the instruction:

Has t h e s u b t a s k s t e p b e e n c o m p l e t e d o f : ‘ ‘ ‘   
{ i n s t r u c t i o n }   
\ n \ n I f y e s , c a l l t h e f u n c t i o n ‘ s u b \_ t a s k \_ s t e p \_ c o m p l e t e ‘ , o t h e r w i s e r e f l e c t a n d c o r r e c t t h e f u l l c o d e t o c o m p l e t e t h e t a s k . O n l y   
u s e t h e f u n c t i o n s y o u h a v e b e e n p r o v i d e d w i t h , a n d i f y o u w a n t t o o u t p u t c o d e o n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ f u n c t i o n t o o u t p u t   
c o d e . C o n d i t i o n i t on e x i s t i n g c o d e : { l i s t \_ f i l e s ( ) } F u l l y i m p l e m e n t t h e s e f e a t u r e s i n t h e c o d e , no p l a c e h o l d e r s . I f y o u h a v e   
n o t v i e w e d t h e f i l e s b e f o r e w r i t i n g t o them , p l e a s e v i e w them , t o make s u r e y o u a r e w r i t i n g t o t h e c o r r e c t f i l e s . \ n R e s p o n d   
now o n l y w i t h a f u n c t i o n c a l l o f o n e o f t h e f o l l o w i n g f u n c t i o n s p r o v i d e d : { f u n c t i o n \_ n a m e s ( ) } , a n d i f y o u w a n t t o o u t p u t c o d e   
o n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ f u n c t i o n t o o u t p u t c o d e .

Here instruction is the current instruction of operation, ‘sub\_task\_step\_complete’ is the function the LLM calls to indicate that it has completed the current instruction, ‘list\_files()’ a list files tool function, and ‘function\_names()’ lists the current function names that the LLM can request.

Mcs Control summarization message for restarting the same instruction:

P l e a s e p r o v i d e a o n e o r t w o s e n t e n c e summary o f t h e o u t p u t o f t h i s s t e p , w h i c h i s u s e f u l f o r t h e n e x t s t e p . Your r e s p o n s e w i l l b e   
u s e d when s t a r t i n g t h e n e x t s t e p w i t h o u t a n y o f t h e p r e v i o u s m e s s a g e s .

Mcs Control summarization message, for summarizing the instruction output—which is used when continuing the next instruction.

You h a v e e x h a u s t e d y o u r c o n t e x t window . R e f l e c t on y o u r p r o g r e s s . P r o v i d e a s h o r t c o n c i s e r e s p o n s e , o f t w o s e n t e n c e s maximum , t h i s w i l l b e u s e d t o r e s t a r t t h i s s t e p f r o m t h e b e g i n n i n g w i t h o u t t h e p r e v i o u s m e s s a g e s .

## G EVALUATION METRICS

There are no automated tools to validate the output of system design tasks, so we propose evaluation metrics to compare the output of different methods. Large-scale code generation is unique in that the generated code can satisfy the high-level user feature requirements specified in the input through various possible implementation approaches.

To quantify the degree to which user-specified features in the initial prompt are effectively implemented in the generated code, we introduce a performance metric named Features %. This metric numerically represents the proportion of input features that are fully and functionally implemented in the output codebase. The Features % is obtained by using a separate GPT-4 API call, which iteratively examines the entire generated code to verify the functional implementation of all input features, counting the number of fully implemented features. We quote this as a percentage of the features implemented over the total features specified by the user. Specifically, we implement this metric by first collecting all the generated code files from a method’s generated output and outputting all the code files as named strings of the format file name, followed by the file contents, and pass it into the prompt template below for the GPT-4 API to count the number of fully implemented features. We then use a regex parser to extract the final number from the LLM response message. We performed a human study in Appendix H.6 and find that this evaluation metric correlates to that performed by human professional software engineers performing a manual code review counting the same number of features implemented.

We now provide this prompt template and then provide an example of it in action.

Features % prompt template

O b j e c t i v e : B a s e d on t h e n u m b e r e d f e a t u r e s g i v e n , y o u a r e t o e v a l u a t e t h e f o l l o w i n g c o d e a n d r e t u r n a n u m e r i c v a l u e f o r how many ( a   
c o u n t ) o f t h o s e numbered f e a t u r e s a r e i m p l e m e n t e d i n t h e p r o v i d e d code . Give t h e n u m e r i c answer a s "FEATURES\_FUNCTIONAL=   
n u m \_ f e a t u r e s \_ f u n c t i o n a l " i n t h e f i n a l l i n e .   
Numbered F e a t u r e s S p e c i f i e d : ‘ ‘   
{ u s e r \_ s p e c i f i e d \_ f e a t u r e \_ r e q u i r e m e n t s }   
Code t o e v a l u a t e f o r t h e a m o u n t o f f e a t u r e s f u l l y i m p l e m e n t e d : " " "   
{ c o d e \_ f i l e s }   
"."

Here ‘user\_specified\_feature\_requirements’ is the user-specified task description, which are provided in full in Appendix E, and ‘code\_files’ is the entire contents of the codebase printed out with filenames and the contents.

A worked example, can be seen in the following, for example Code-L2MAC for one of the runs for the environment task URL Shortener App, with the complete user-specified feature requirements is given, including the GPT4 call’s response.

## GPT4 API call.

To e v a l u a t e t h e p r o v i d e d c o d e b a s e d on t h e r e q u i r e m e n t s f o r t h e " O n l i n e URL S h o r t e n i n g S e r v i c e " , y o u c a n u s e t h e f o l l o w i n g n u m b e r e d c h e c k l i s t . F o r e a c h f e a t u r e p r e s e n t i n t h e c o d e , y o u c a n i n c r e m e n t a n u m e r i c v a l u e :

E v a l u a t i o n C h e c k l i s t f o r O n l i n e URL S h o r t e n i n g S e r v i c e :   
1 . \*\*URL S h o r t e n i n g \* \* :   
− [ ] 1 . 1 . U s e r s c a n i n p u t a URL t o b e s h o r t e n e d .   
− [ ] 1 . 2 . The s y s t e m v a l i d a t e s t h a t t h e URL i s a c t i v e a n d l e g i t i m a t e   
[ ] 1 . 3 . The s y s t e m g e n e r a t e s a u n i q u e s h o r t e n e d URL .   
[ ] 1 . 4 . U s e r s c a n c h o o s e c u s t o m s h o r t l i n k s ( s u b j e c t t o a v a i l a b i l i t y ) .   
2 . R e d i r e c t i o n :   
− [ ] 2 . 1 . A c c e s s i n g t h e s h o r t e n e d URL r e d i r e c t s t o t h e o r i g i n a l URL   
3 . A n a l y t i c s :   
] 3 . 1 . U s e r s c a n v i e w s t a t i s t i c s a b o u t t h e i r s h o r t e n e d URLs .   
[ 3 . 2 . View n u m b e r o f c l i c k s .   
[ ] 3 . 3 . View d a t e / t i m e o f e a c h c l i c k .   
[ ] 3 . 4 . View g e o g r a p h i c a l l o c a t i o n o f t h e c l i c k e r .   
4 . User A c c o u n t s :   
− [ ] 4 . 1 . U s e r s c a n c r e a t e a c c o u n t s .   
[ ] 4 . 2 . A c c o u n t h o l d e r s c a n v i e w a l l t h e i r s h o r t e n e d URLs .   
[ ] 4 . 3 . A c c o u n t h o l d e r s c a n e d i t o r d e l e t e t h e i r s h o r t e n e d URLs .   
[ ] 4 . 4 . A c c o u n t h o l d e r s c a n v i e w a n a l y t i c s f o r a l l t h e i r s h o r t e n e d URLs .   
5 . Admin Dashboard :   
[ ] 5 . 1 . A d m i n i s t r a t o r s c a n v i e w a l l s h o r t e n e d URLs .   
5 . 2 . A d m i n i s t r a t o r s c a n d e l e t e a n y URL o r u s e r a c c o u n t   
5 . 3 . A d m i n i s t r a t o r s c a n m o n i t o r s y s t e m p e r f o r m a n c e a n d a n a l y t i c s .   
6 . E x p i r a t i o n :   
− [ ] 6 . 1 . U s e r s c a n s e t a n e x p i r a t i o n d a t e / t i m e f o r t h e s h o r t e n e d URL   
LC

You c a n go t h r o u g h t h e p r o v i d e d c o d e and c h e c k o f f e a c h i t e m t h a t h a s b e e n i m p l e m e n t e d . At t h e end , c o u n t t h e c h e c k e d b o x e s t o g e t t h e n u m e r i c v a l u e f o r t h e number o f f e a t u r e s i m p l e m e n t e d .

```csv
Code t o e v a l u a t e f o r t h e a m o u n t o f f e a t u r e s f u l l y i m p l e m e n t e d : " " "
t e s t _ a n a l y t i c s . py
‘ ‘ ‘ p y t h o n
i m p o r t a n a l y t i c s
i m p o r t d a t e t i m e
d e f t e s t _ t r a c k _ c l i c k ( ) :
" " " T e s t t h a t c l i c k e v e n t s a r e t r a c k e d c o r r e c t l y . " " "
a n a l y t i c s . t r a c k _ c l i c k ( ’ a b c 1 2 3 ’ , ’ 8 . 8 . 8 . 8 ’ )
d a t a = a n a l y t i c s . g e t _ a n a l y t i c s ( ’ a b c 1 2 3 ’ )
a s s e r t l e n ( d a t a ) == 1
a s s e r t i s i n s t a n c e ( d a t a [ 0 ] [ ’ t i m e ’ ] , d a t e t i m e . d a t e t i m e )
a s s e r t d a t a [ 0 ] [ ’ i p _ a d d r e s s ’ ] == ’ 8 . 8 . 8 . 8 ’
d e f t e s t _ g e t _ a n a l y t i c s ( ) :
" " " T e s t t h a t a n a l y t i c s d a t a i s r e t r i e v e d c o r r e c t l y . " " "
d a t a = a n a l y t i c s . g e t _ a n a l y t i c s ( ’ a b c 1 2 3 ’ )
a s s e r t l e n ( d a t a ) == 1
a s s e r t i s i n s t a n c e ( d a t a [ 0 ] [ ’ t i m e ’ ] , d a t e t i m e . d a t e t i m e )
a s s e r t d a t a [ 0 ] [ ’ i p _ a d d r e s s ’ ] == ’ 8 . 8 . 8 . 8
a n a l y t i c s . p y
‘ ‘ ‘ p y t h o n
i m p o r t d a t e t i m e
# Mock d a t a b a s e
a n a l y t i c s _ d a t a = { }
d e f t r a c k _ c l i c k ( s h o r t _ u r l , i p _ a d d r e s s ) :
" " " T r a c k a c l i c k e v e n t . " " "
i f s h o r t _ u r l n o t i n a n a l y t i c s _ d a t a :
a n a l y t i c s _ d a t a [ s h o r t _ u r l ] = [ ]
# R e c o r d t h e c l i c k e v e n t
c l i c k _ e v e n t = {
’ t i m e ’ : d a t e t i m e . d a t e t i m e . now ( ) ,
’ i p _ a d d r e s s ’ : i p _ a d d r e s s
}
a n a l y t i c s _ d a t a [ s h o r t _ u r l ] . a p p e n d ( c l i c k _ e v e n t )
d e f g e t _ a n a l y t i c s ( s h o r t _ u r l ) :
" " " R e t r i e v e a n a l y t i c s d a t a f o r a s h o r t URL . " " "
r e t u r n a n a l y t i c s _ d a t a . g e t ( s h o r t _ u r l , [ ] )
d e f g e t _ s y s t e m _ p e r f o r m a n c e ( ) :
" " " R e t r i e v e s y s t e m p e r f o r m a n c e d a t a .
R e t u r n s :
```

d i c t : A d i c t i o n a r y c o n t a i n i n g s y s t e m p e r f o r m a n c e d a t a   
# F o r s i m p l i c i t y , we ’ l l j u s t r e t u r n t h e n u m b e r o f URLs a n d t h e n u m b e r o f c l i c k e v e n t s .   
r e t u r n   
n u m \_ u r l s ’ : l e n ( a n a l y t i c s \_ d a t a ) ,   
’ n u m \_ c l i c k s ’ : sum ( l e n ( e v e n t s ) f o r e v e n t s i n a n a l y t i c s \_ d a t a . v a l u e s ( ) )   
}   
t e s t \_ u s e r \_ a c c o u n t s . p y   
‘ ‘ ‘ p y t h o n   
i m p o r t p y t e s t   
f r o m u s e r \_ a c c o u n t s i m p o r t U s e r A c c o u n t   
d e f t e s t \_ c r e a t e \_ a c c o u n t ( ) :   
a s s e r t u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( ’ t e s t ’ , ’ p a s s w o r d ’ ) == ’ A c c o u n t c r e a t e d s u c c e s s f u l l y . ’   
a s s e r t u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( ’ t e s t ’ , ’ p a s s w o r d ’ ) == ’ Username a l r e a d y e x i s t s .   
d e f t e s t \_ v i e w \_ u r l s ( ) :   
u s e r \_ a c c o u n t = U s e r A c c o u n t ( )   
u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( ’ t e s t ’ , ’ p a s s w o r d ’ )   
a s s e r t u s e r \_ a c c o u n t . v i e w \_ u r l s ( ’ t e s t ’ ) == [ ]   
a s s e r t u s e r \_ a c c o u n t . v i e w \_ u r l s ( ’ n o n e x i s t e n t ’ ) == ’ U s e r n a m e d o e s n o t e x i s t .   
u s e r \_ a c c o u n t = U s e r A c c o u n t ( )   
u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( ’ t e s t ’ , ’ p a s s w o r d ’ )   
a s s e r t u s e r \_ a c c o u n t . a d d \_ u r l ( ’ t e s t ’ h t t p : / / e x a m p l e . com ’ ) == ’URL a d d e d s u c c e s s f u l l y . ’   
a s s e r t u s e r \_ a c c o u n t . a d d \_ u r l ( ’ n o n e x i s t e n t ’ , ’ h t t p : / / e x a m p l e . com ’ ) == ’ U s e r n a m e d o e s n o t e x i s t . ’   
d e f t e s t \_ d e l e t e \_ u r l ( ) :   
u s e r \_ a c c o u n t = U s e r A c c o u n t ( )   
u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( ’ t e s t ’ , ’ p a s s w o r d ’ )   
u s e r \_ a c c o u n t . a d d \_ u r l ( ’ t e s t ’ , ’ h t t p : / / e x a m p l e . com ’ )   
a s s e r t u s e r \_ a c c o u n t . d e l e t e \_ u r l ( ’ t e s t ’ , ’ h t t p : / / e x a m p l e . com ’ ) == ’URL r e m o v e d s u c c e s s f u l l y .   
a s s e r t ’ h t t p : / / n o n e x i s t e n t . com ’ ) == ’URL d o e s n o t e x i s t .   
a s s e r t u s e r \_ a c c o u n t . d e l e t e \_ u r l ( ’ n o n e x i s t e n t ’ , ’ h t t p : / / e x a m p l e . com ’ ) == ’ U s e r n a m e d o e s n o t e x i s t .   
u r l \_ s h o r t e n e r . p y   
‘ ‘ ‘ p y t h o n   
i m p o r t h a s h l i b   
i m p o r t r e q u e s t s   
f r o m d a t e t i m e i m p o r t d a t e t i m e , t i m e d e l t a   
# Mock d a t a b a s e t o s t o r e t h e m a p p i n g b e t w e e n t h e s h o r t e n e d URLs a n d t h e o r i g i n a l URLs .   
u r l \_ m a p p i n g = {}   
d e f g e n e r a t e \_ s h o r t \_ u r l ( u r l , e x p i r a t i o n \_ m i n u t e s = 1 5 ) :   
" " G e n e r a t e a u n i q u e s h o r t e n e d URL .   
A r g s :   
u r l ( s t r ) : The o r i g i n a l URL .   
e x p i r a t i o n \_ m i n u t e s ( i n t ) : The n u m b e r o f m i n u t e s u n t i l t h e URL e x p i r e s .   
R e t u r n s :   
s t r : The s h o r t e n e d URL .   
h a s h \_ o b j e c t = h a s h l i b . md5 ( u r l . e n c o d e ( ) )   
s h o r t \_ u r l = h a s h \_ o b j e c t . h e x d i g e s t ( ) [ : 1 0 ]   
# S t o r e t h e m a p p i n g b e t w e e n t h e s h o r t e n e d URL a n d t h e o r i g i n a l URL .   
u r l \_ m a p p i n g [ s h o r t \_ u r l ] = {   
’ u r l ’ : u r l ,   
e x p i r a t i o n ’ : d a t e t i m e . now ( ) + t i m e d e l t a ( m i n u t e s = e x p i r a t i o n \_ m i n u t e s )   
}   
r e t u r n s h o r t \_ u r l   
d e f v a l i d a t e \_ u r l ( u r l ) :   
" " " V a l i d a t e a URL .   
A r g s :   
u r l ( s t r ) : The URL t o v a l i d a t e .   
R e t u r n s :   
b o o l : T r u e i f t h e URL i s v a l i d , F a l s e o t h e r w i s e   
t r y :   
r e s p o n s e = r e q u e s t s . g e t ( u r l )   
r e t u r n r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
e x c e p t r e q u e s t s . e x c e p t i o n s . R e q u e s t E x c e p t i o n :   
r e t u r n F a l s e   
d e f g e t \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l ) :   
" " G e t t h e o r i g i n a l URL a s s o c i a t e d w i t h t h e s h o r t e n e d URL .   
A r g s :   
s h o r t u r1 ( s t r ) : The s h o r t e n e d URL,   
R e t u r n s :   
s t r : The o r i g i n a l URL , o r None i f t h e s h o r t e n e d URL d o e s n o t e x i s t o r h a s e x p i r e d .   
u r l \_ d a t a = u r l \_ m a p p i n g . g e t ( s h o r t \_ u r l )   
i f u r l \_ d a t a a n d u r l \_ d a t a [ ’ e x p i r a t i o n ’ ] > d a t e t i m e . now ( ) :   
r e t u r n u r l \_ d a t a [ ’ u r l ’ ]   
d e f d e l e t e \_ u r l ( s h o r t \_ u r l ) :   
" D e l e t e a s h o r t e n e d URL .

A r g s :   
s h o r t \_ u r l ( s t r ) : The s h o r t e n e d URL .   
i f s h o r t \_ u r l i n u r l \_ m a p p i n g :   
d e l u r l \_ m a p p i n g [ s h o r t \_ u r l ]   
d e f g e t \_ a l l \_ u r l s ( ) :   
" " G e t a l l s h o r t e n e d URLs   
R e t u r n s :   
1i s t : A li st of a ll s h o rt e n e d URLs.   
r e t u r n l i s t ( u r l \_ m a p p i n g . k e y s ( ) )   
t e s t \_ u r l \_ s h o r t e n e r . p y   
‘ ‘ p y t h o n   
i m p o r t u r l \_ s h o r t e n e r   
i m p o r t t i m e   
d e f t e s t \_ g e n e r a t e \_ s h o r t \_ u r l ( ) :   
" " " T e s t t h e g e n e r a t e \_ s h o r t \_ u r l f u n c t i o n . " " "   
u r l = ’ h t t p s : / / www . e x a m p l e . com   
s h o r t \_ u r l = u r l \_ s h o r t e n e r . g e n e r a t e \_ s h o r t \_ u r l ( u r l )   
a s s e r t l e n ( s h o r t \_ u r l ) == 10   
a s s e r t i s i n s t a n c e ( s h o r t \_ u r l , s t r )   
d e f t e s t \_ v a l i d a t e \_ u r l ( ) :   
" " " T e s t t h e v a l i d a t e \_ u r l f u n c t i o n . " " "   
v a l i d \_ u r l = ’ h t t p s : / / www . e x a m p l e . com   
i n v a l i d \_ u r l = ’ h t t p s : / / www . i n v a l i d u r l . com ’   
a s s e r t u r l \_ s h o r t e n e r . v a l i d a t e \_ u r l ( v a l i d \_ u r l ) i s T r u e   
a s s e r t u r l \_ s h o r t e n e r . v a l i d a t e \_ u r l ( i n v a l i d \_ u r l ) i s F a l s e   
d e f t e s t \_ u r l \_ e x p i r a t i o n ( ) :   
" " " T e s t t h a t URLs e x p i r e c o r r e c t l y . " " "   
u r l = ’ h t t p s : / / www . e x a m p l e . com   
s h o r t \_ u r l = u r l \_ s h o r t e n e r . g e n e r a t e \_ s h o r t \_ u r l ( u r l , e x p i r a t i o n \_ m i n u t e s = 0 )   
a s s e r t u r l \_ s h o r t e n e r . g e t \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l ) i s None   
s ho r t u r l = u r l s ho r t e n e r , g e n e r a t e s ho r t u r l (u rl , e x p i r a t i o n mi n u t e s =l)   
a s s e r t u r l \_ s h o r t e n e r . g e t \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l ) == u r l   
# W a i t f o r t h e URL t o e x p i r e   
t i m e . s l e e p ( 6 1 )   
a s s e r t u r l s h o r t e n e r , g e t o r i g i n a l u r l ( s h o r t u r l) i s None   
u s e r \_ a c c o u n t s . p y   
‘ ‘ ‘ p y t h o n   
c l a s s U s e r A c c o u n t :   
d e f \_ \_ i n i t \_ \_ ( s e l f ) :   
s e l f . a c c o u n t s = { }   
d e f c r e a t e \_ a c c o u n t ( s e l f , u s e r n a m e , p a s s w o r d ) :   
i f u s e r n a m e i n s e l f . a c c o u n t s :   
r e t u r n ’ U s e r n a m e a l r e a d y e x i s t s . ’   
s e 1 f , a c c ou n t s [ us ername] = { ' passw ord ' ; pass word , ' u r 1s ' ; [] }   
r e t u r n ’ A c c o u n t c r e a t e d s u c c e s s f u l l y .   
d e f v i e w \_ u r l s ( s e l f , u s e r n a m e ) :   
i f u s e r n a m e n o t i n s e l f . a c c o u n t s :   
r e t u r n ’ Username d o e s n o t e x i s t . ’   
r e t u r n s e l f . a c c o u n t s [ u s e r n a m e ] [ ’ u r l s ’ ]   
d e f a d d \_ u r l ( s e l f , u s e r n a m e , u r l ) :   
i f u s e r n a m e n o t i n s e l f . a c c o u n t s :   
r e t u r n ’ Username d o e s n o t e x i s t .   
s e l f . a c c o u n t s [ u s e r n a m e ] [ ’ u r l s ’ ] . a p p e n d ( u r l )   
r e t u r n ’URL a d d e d s u c c e s s f u l l y .   
d e f d e l e t e \_ u r l ( s e l f , u s e r n a m e , u r l ) :   
i f u s e r n a m e n o t i n s e l f . a c c o u n t s :   
r e t u r n ’ Username d o e s n o t e x i s t . ’   
i f u r l n o t i n s e l f . a c c o u n t s [ u s e r n a m e ] [ ’ u r l s ’ ] :   
r e t u r n ’URL d o e s n o t e x i s t .   
s e l f . a c c o u n t s [ u s e r n a m e ] [ ’ u r l s ’ ] . r e m o v e ( u r l )   
r e t u r n ’URL r e m o v e d s u c c e s s f u l l y .   
d e f d e l e t e \_ a c c o u n t ( s e l f , u s e r n a m e ) :   
i f u s e r n a m e i n s e l f . a c c o u n t s :   
d e l s e l f . a c c o u n t s [ u s e r n a m e ]   
r e t u r n ’ A c c o u n t d e l e t e d s u c c e s s f u l l y . ’   
e l s e :   
r e t u r n ’ Username d o e s n o t e x i s t .   
d e f g e t \_ a l l \_ u s e r s ( s e l f ) :   
r e t u r n l i s t ( s e l f . a c c o u n t s . k e y s ( ) )   
r e q u i r e m e n t s . t x t   
‘ ‘ ‘ t e x t   
f l a sk   
p y t e s t   
maxminddb − g e o l i t e 2

t e s t \_ a p p . py   
‘ ‘ ‘ p y t h o n   
i m p o r t p y t e s t   
f r o m a p p i m p o r t a p p   
@ p y t e s t . f i x t u r e   
d e f c l i e n t ( ) :   
a p p . c o n f i g [ ’ TESTING ’ ] = T r u e   
w i t h a p p . t e s t \_ c l i e n t ( ) a s c l i e n t :   
y i e l d c l i e n t   
d e f t e s t \_ h o m e \_ p a g e ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t r e s p o n s e . d a t a == b ’ H e l l o , W o r l d ! ’   
d e f t e s t \_ r e d i r e c t \_ t o \_ o r i g i n a l \_ u r l ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / a b c 1 2 3 ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 4 0 4   
d e f t e s t \_ s h o r t e n \_ u r l ( c l i e n t ) :   
r e s p o n s e = c l i e n t . p o s t ( ’ / s h o r t e n ’ , d a t a = { ’ u r l ’ : ’ h t t p s : / / www . g o o g l e . com ’ } )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t ’ s h o r t \_ u r l ’ i n r e s p o n s e . g e t \_ j s o n ( )   
d e f t e s t \_ v i e w \_ a n a l y t i c s ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / a n a l y t i c s / a b c 1 2 3 ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t ’ a n a l y t i c s ’ i n r e s p o n s e . g e t \_ j s o n ( )   
d e f t e s t \_ m a n a g e \_ a c c o u n t ( c l i e n t ) :   
r e s p o n s e = c l i e n t . p o s t ( ’ / a c c o u n t ’ , d a t a = { ’ a c t i o n ’ : ’ c r e a t e ’ , ’ u s e r n a m e ’ : ’ t e s t u s e r ’ , ’ p a s s w o r d ’ : ’ t e s t p a s s ’ } )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t r e s p o n s e . g e t \_ j s o n ( ) [ ’ m e s s a g e ’ ] == ’ A c c o u n t c r e a t e d s u c c e s s f u l l y . ’   
r e s p o n s e = c l i e n t . p o s t ( ’ / a c c o u n t ’ , d a t a = { ’ a c t i o n ’ : ’ v i e w \_ u r l s ’ , ’ u s e r n a m e ’ : ’ t e s t u s e r ’ } )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
i n r e s p o n s e . g e t \_ j s o n ( )   
r e s p o n s e = c l i e n t . p o s t ( ’ / a c c o u n t ’ , d a t a = { ’ a c t i o n ’ : ’ d e l e t e ’ , ’ u s e r n a m e ’ : ’ t e s t u s e r ’ } )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t r e s p o n s e . g e t \_ j s o n ( ) [ ’ m e s s a g e ’ ] == ’ A c c o u n t d e l e t e d s u c c e s s f u l l y .   
d e f t e s t \_ a d m i n \_ d a s h b o a r d ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / a d m i n ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
a s s e r t ’ u r l s ’ i n r e s p o n s e . g e t \_ j s o n ( )   
a s s e r t ’ u s e r s ’ i n r e s p o n s e . g e t \_ j s o n ( )   
a s s e r t ’ p e r f o r m a n c e ’ i n r e s p o n s e . g e t \_ j s o n ( )   
d e f t e s t \_ d e l e t e \_ u r l ( c l i e n t ) :   
c l i e n t . p o s t ( ’ / a d m i n ’ , d a t a = { ’ a c t i o n ’ : ’ d e l e t e \_ u r l ’ , ’ s h o r t \_ u r l ’ : ’ a b c 1 2 3 ’ } )   
r e s p o n s e = c l i e n t . g e t ( ’ / a b c 1 2 3 ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 4 0 4   
d e f t e s t \_ d e l e t e \_ u s e r ( c l i e n t ) :   
c l i e n t . p o s t ( ’ / a d m i n ’ , d a t a = { ’ a c t i o n ’ : ’ d e l e t e \_ u s e r ’ , ’ u s e r n a m e ’ : ’ t e s t u s e r ’ } )   
r e s p o n s e = c l i e n t . g e t ( ’ / a d m i n ’ )   
a s s e r t ’ t e s t u s e r ’ n o t i n r e s p o n s e . g e t \_ j s o n ( ) [ ’ u s e r s ’ ]   
a p p . py   
‘ ‘ p y t h o n   
f r o m f l a s k i m p o r t F l a s k , r e d i r e c t , u r l \_ f o r , r e q u e s t   
f r o m u r l \_ s h o r t e n e r i m p o r t g e t \_ o r i g i n a l \_ u r l , d e l e t e \_ u r l , g e t \_ a l l \_ u r l s , g e n e r a t e \_ s h o r t \_ u r l , v a l i d a t e \_ u r l   
f r o m u s e r \_ a c c o u n t s i m p o r t U s e r A c c o u n t   
f r o m a n a l y t i c s i m p o r t g e t \_ s y s t e m \_ p e r f o r m a n c e , g e t \_ a n a l y t i c s , t r a c k \_ c l i c k   
app = F l a s k ( \_\_name\_\_ )   
u s e r \_ a c c o u n t = U s e r A c c o u n t ( )   
@app . r o u t e ( ’ / ’ )   
d e f home ( ) :   
r e t u r n ’ H e l l o , W o r l d !   
@app . r o u t e ( ’ / < s h o r t \_ u r l > ’ )   
d e f r e d i r e c t \_ t o \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l ) :   
o r i g i n a l \_ u r l = g e t \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l )   
i f o r i g i n a l \_ u r l i s None :   
r e t u r n ’URL n o t f o u n d ’ , 404   
e l s e :   
t r a c k \_ c l i c k ( s h o r t \_ u r l , r e q u e s t . r e m o t e \_ a d d r )   
r e t u r n r e d i r e c t ( o r i g i n a l \_ u r l )   
@app . r o u t e ( ’ / s h o r t e n ’ , m e t h o d s = [ ’ POST ’ ] )   
d e f s h o r t e n \_ u r l ( ) :   
u r l = r e q u e s t . f o r m . g e t ( ’ u r l ’ )   
i f n o t v a l i d a t e \_ u r l ( u r l ) :   
r e t u r n ’ I n v a l i d URL ’ , 4 0 0   
s h o r t \_ u r l = g e n e r a t e \_ s h o r t \_ u r l ( u r l )   
u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
i f u s e r n a m e :   
r e t u r n { ’ s h o r t \_ u r l ’ : s h o r t \_ u r l }   
@app . r o u t e ( ’ / a n a l y t i c s / < s h o r t \_ u r l > ’ )

d e f v i e w \_ a n a l y t i c s ( s h o r t \_ u r l ) :   
r e t u r n { ’ a n a l y t i c s ’ : g e t \_ a n a l y t i c s ( s h o r t \_ u r l ) }   
@app . r o u t e ( ’ / a c c o u n t ’ , m e t h o d s = [ ’ POST ’ ] )   
d e f m a n a g e \_ a c c o u n t ( ) :   
a c t i o n = r e q u e s t . f o r m . g e t ( ’ a c t i o n ’ )   
u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
i f a c t i o n == ’ c r e a t e ’ :   
p a s s w o r d = r e q u e s t . f o r m . g e t ( ’ p a s s w o r d ’ )   
r e t u r n { ’ m e s s a g e ’ : u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( u s e r n a m e , p a s s w o r d ) }   
e l i f a c t i o n == , v i e w urls ; :   
r e t u r n { ’ u r l s ’ : u s e r \_ a c c o u n t . v i e w \_ u r l s ( u s e r n a m e ) }   
e l i f a c t i o n == ’ d e l e t e ’ :   
r e t u r n { ’ m e s s a g e ’ : u s e r \_ a c c o u n t . d e l e t e \_ a c c o u n t ( u s e r n a m e ) }   
@app . r o u t e ( ’ / admin ’ , m e t h o d s = [ ’ GET ’ , ’POST ’ ] )   
d e f a d m i n \_ d a s h b o a r d ( ) :   
i f r e q u e s t . m e t h o d == ’POST ’ :   
a c t i o n = r e q u e s t . f o r m . g e t ( ’ a c t i o n ’ )   
i f a c t i o n == ’ d e l e t e \_ u r l ’ :   
s h o r t \_ u r l = r e q u e s t . f o r m . g e t ( ’ s h o r t \_ u r l ’ )   
d e l e t e \_ u r l ( s h o r t \_ u r l )   
e l i f a c t i o n == ’ d e l e t e \_ u s e r ’ :   
u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
u s e r \_ a c c o u n t . d e l e t e \_ a c c o u n t ( u s e r n a m e )   
r e t u r n r e d i r e c t ( u r l \_ f o r ( ’ a d m i n \_ d a s h b o a r d ’ ) )   
e l s e :   
a l l \_ u r l s = g e t \_ a l l \_ u r l s ( )   
a l l \_ u s e r s = u s e r \_ a c c o u n t . g e t \_ a l l \_ u s e r s ( )   
p e r f o r m a n c e \_ d a t a = g e t \_ s y s t e m \_ p e r f o r m a n c e ( )   
r e t u r n { ’ u r l s ’ : a l l \_ u r l s , ’ u s e r s ’ : a l l \_ u s e r s , ’ p e r f o r m a n c e ’ : p e r f o r m a n c e \_ d a t a }   
i f \_\_name\_\_ == \_\_main\_\_ ’ :   
app . r u n ( debug = True )   
GPT4 API response   
The p r o v i d e d c o d e i m p l e m e n t s t h e f o l l o w i n g f e a t u r e s :   
1 . URL S h o r t e n i n g :   
[ x ] 1 . 1 . U s e r s c a n i n p u t a URL t o b e s h o r t e n e d .   
− [ x ] 1 . 2 . The s y s t e m v a l i d a t e s t h a t t h e URL i s a c t i v e a n d l e g i t i m a t e   
[ x ] 1 . 3 . The s y s t e m g e n e r a t e s a u n i q u e s h o r t e n e d URL .   
[ ] 1 . 4 . U s e r s c a n c h o o s e c u s t o m s h o r t l i n k s ( s u b j e c t t o a v a i l a b i l i t y ) .   
2 . R e d i r e c t i o n :   
[ x ] 2 . 1 . A c c e s s i n g t h e s h o r t e n e d URL r e d i r e c t s t o t h e o r i g i n a l URL   
3 . A n a l y t i c s :   
[ x ] 3 . 1 . U s e r s c a n v i e w s t a t i s t i c s a b o u t t h e i r s h o r t e n e d URLs .   
[ x ] 3 . 2 . View n u m b e r o f c l i c k s .   
[ x ] 3 . 3 . View d a t e / t i m e o f e a c h c l i c k .   
[ ] 3 . 4 . View g e o g r a p h i c a l l o c a t i o n o f t h e c l i c k e r .   
4 . User A c c o u n t s :   
[ x ] 4 . 1 . U s e r s c a n c r e a t e a c c o u n t s .   
[ x ] 4 . 2 . A c c o u n t h o l d e r s c a n v i e w a l l t h e i r s h o r t e n e d URLs .   
[ x ] 4 . 3 . A c c o u n t h o l d e r s c a n e d i t o r d e l e t e t h e i r s h o r t e n e d URLs .   
[ x ] 4 . 4 . A c c o u n t h o l d e r s c a n v i e w a n a l y t i c s f o r a l l t h e i r s h o r t e n e d URLs .   
5 . \*\*Admin Dashboard \* \* :   
[ x ] 5 . 1 . A d m i n i s t r a t o r s c a n v i e w a l l s h o r t e n e d URLs .   
− [ x ] 5 . 2 . A d m i n i s t r a t o r s c a n d e l e t e a n y URL o r u s e r a c c o u n t   
[ x ] 5 . 3 . A d m i n i s t r a t o r s c a n m o n i t o r s y s t e m p e r f o r m a n c e a n d a n a l y t i c s   
6 . E x p i r a t i o n :   
− [ x ] 6 . 1 . U s e r s c a n s e t a n e x p i r a t i o n d a t e / t i m e f o r t h e s h o r t e n e d URL   
C o u n t i n g t h e c h e c k e d b o x e s , we g e t a t o t a l o f 15 f e a t u r e s i m p l e m e n t e d .   
FEATURES\_FUNCTIONAL=15

The final line of the response, ‘FEATURES\_FUNCTIONAL’ is then extracted by a regex parser. We note that the use of the feature requirements specified as a checklist helps the LLM check which features are fully implemented and which features are not and aids in counting the number of features that have been fulfilled in the generated codebase according to the user-specified input feature requirements.

Furthermore, we also incorporate standard code generation evaluation metrics (Hasemer, 2018), such as the number of lines of code generated LOC and the number of errors # Errors in the codebase determined by a code syntactical analyzer (Thénault, 2023). Specifically, we use PyLint, a well-known Python syntactical analyzer, and configure it to only detect and count the number of errors in the code, which becomes static syntax errors that arise from the generated outputs. We configure it with the following options of ‘–disable=all –enable=E’.

Moreover, as the methods are instructed to generate unit tests to check that the generated code is valid, we also quote how many self-generated unit tests pass with the method as Tests Passed. We compute this metric by running a Python test tool, that of PyTest (Okken, 2022). This is configured to automatically find all relevant python tests (default configuration), and the LLM can call this separately as a function on only code path input.

We also include the metric of code coverage (Miller & Maloney, 1963) as Cov %. This measures the percentage of lines of code that are executed during running all the self-generated unit tests for the generated codebase out of the total executable lines of code. A codebase with a high test coverage percentage has more of its code executed during running the unit tests, indicating that it has a lower chance of containing undetected software bugs compared to a codebase with a low test coverage percentage. We practically test this with a python code coverage tool, that of Coverage (Batchelder & Contributors to Coverage.py, 2023), and only run this at evaluation time when evaluating the codebase.

Experimental setup. We complete 10 random seed runs for each task environment for each benchmark method. We then compute each metric alongside its 95% confidence intervals throughout.

## G.1 MOTIVATION FOR FEATURE %

To elucidate the motivation of Feature %, we note that the metric “Is it fully functional?” is very sparse and does not reflect the degrees of correctness that an implementation can have. As an extreme case, it is tough to prove that a given codebase contains no bugs, and in practice, most codebases contain bugs. This does not imply that they are not functional, although each time a bug is correctly fixed, we can agree that the codebase has gotten more functional. Consequently, asking, “To what degree is it functional?” is more reasonable. A way to quantify this is to ask “Of the functions/features that I expect this codebase to fulfill correctly, how many are actually fulfilled?”. This is what feature % quantifies. As a proxy, and in line with previous literature (Chiang & Lee, 2023), we quantify this by having GPT4 assess what features specified by the user were implemented fully as code (see Appendices E and G for example prompts).

## H ADDITIONAL RESULTS

## H.1 HUMANEVAL BENCHMARK RESULTS

We also evaluated Code-L2MAC on the standard HumanEval benchmark (Chen et al., 2021) and found that it achieves a state-of-the-art score of 90.2% Pass@1. We briefly describe the benchmark here (with a complete description given in Appendix E.2), and provide a comparative analysis of existing methods here.

Pass@1 of HumanEval (%)  
![](images/d2dfc755cb8e2ae60bc640d8d1087d3d62537c7775a1f55e75bfb4baa16ccdb3.jpg)  
Figure 7: HumanEval Benchmark—Pass rates with a single attempt.

HumanEval Benchmark. As introduced by Chen et al. (2021), consists of 164 hand-written programming problems, where each task provides a docstring from which the LLM-based method needs to generate the rest of the python function. Each task generation is then evaluated for functional correctness by testing with held-out unit tests, which they all have to pass for that task to be marked as complete.

Evaluation Metric. To evaluate the functional correctness of the programs generated the benchmark uses the pass@k metric as presented by Chen et al. (2021), to evaluate the functional accuracy of the top-k generated programs.

$$
\operatorname { p a s s } @ k : = \operatorname * { \mathbb { E } } _ { \operatorname { P r o b l e m s } } \left[ 1 - { \frac { { \binom { n - c } { k } } } { { \binom { n } { k } } } } \right]\tag{1}
$$

Baselines. As HumanEval is an established benchmark, we quote the existing baseline results from respective papers, from the current global leaderboard. Such methods include AlphaCode (Li et al., 2022), LLAMA-2 (Touvron et al., 2023), Inflection-2 (Inflection AI, 2023), Grok-1 (xai-org, 2024; Team et al., 2023), Codex + CodeT (Chen et al., 2022), GPT-4 (OpenAI, 2023), Gemini Ultra (Team et al., 2023), Claude 3 Opus (Anthropic, 2024), MetaGPT (Hong et al., 2024) and OctorCoder (Muennighoff et al., 2023).

We modify the prompt to include the function docstring and provide the instruction to only write code to complete the given function for each problem within the benchmark. We also instruct in the initial prompt that all tests should be comprehensive, interpretable, and cover edge cases. We also performed this evaluation using the GPT-4 model of 1106-Preview.

Main Result. Figure 7 shows that Code-L2MAC outperforms all baselines listed above on the HumanEval benchmark. Crucially, Code-L2MAC that uses GPT-4 within its multi-agent framework significantly outperforms a standalone GPT-4 model on the pass@1 metric on the HumanEval benchmark.

## H.2 L2MAC FOR WRITING AN ENTIRE BOOK

In the following we show that a general-purpose L2MAC works for completing general-purpose long output text-based tasks, such as writing an entire book. Specifically, we posed the task to write a complete book based on the following input prompt below of

W r i t e a c o m p l e t e r e c i p e b o o k f o r t h e f o l l o w i n g b o o k t i t l e o f " T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a "

D e s c r i p t i o n : " T w i r l s & T a s t e s " i n v i t e s y o u on a f l a v o r f u l e x p e d i t i o n a c r o s s I t a l y , e x p l o r i n g t h e d i v e r s e p a s t a l a n d s c a p e f r o m t h e   
s u n − d r e n c h e d h i l l s o f T u s c a n y t o t h e b u s t l i n g s t r e e t s o f N a p l e s . D i s c o v e r r e g i o n a l s p e c i a l t i e s , l e a r n t h e s t o r i e s b e h i n d e a c h   
d i s h , a n d m a s t e r t h e a r t o f p a s t a m a k i n g w i t h e a s y − t o − f o l l o w r e c i p e s t h a t p r o m i s e t o d e l i g h t y o u r s e n s e s .

Specifically, as we use the same L2MAC framework, as presented in Sections 3 and 4, where we now generate output text instead of code. Specifically, we replace the error checking mechanism E(D) from a code specific one as in Code-L2MAC to a general consistency check, for coherence of the generated output to the existing generated previous outputs. We additionally use the GPT-4 model of 1106-Preview.

The full result of the raw generated book is given here:

by [ A u t h o r ’ s Name ]

T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

Foreword

Dear Reader ,

Welcome t o a w o r l d w h e r e t h e s i m p l e a c t o f t w i r l i n g a f o r k c a n t r a n s p o r t y o u t o a p l a c e r i c h w i t h h i s t o r y , c u l t u r e , a n d f l a v o r . I t a l i a n p a s t a i s n o t j u s t f o o d ; i t ’ s a n a r r a t i v e woven i n t o t h e v e r y f a b r i c o f I t a l y ’ s h e r i t a g e , a s e r i e s o f s t o r i e s t o l d t h r o u g h e a c h shape , e a c h s au c e , and e a c h b i t e .

As you t u r n t h e s e p a g e s , you w i l l e m b a r k on a j o u r n e y t h a t s p a n s t h e snowy p e a k s o f t h e N o r t h t o t h e s u n − k i s s e d s h o r e s o f t h e S o u t h . You w i l l d i s c o v e r t h e a r t i s t r y b e h i n d t h e h u m b l e n o o d l e a n d t h e m y r i a d ways i t h a s b e e n t r a n s f o r m e d by t h e h a n d s o f g r a n d m o t h e r s , c h e f s , a n d a r t i s a n s a l i k e .

I i n v i t e y o u t o s a v o r t h e t a l e s o f p a s t a ’ s p a s t , t o r e v e l i n t h e c r e a t i v i t y o f i t s p r e s e n t , a n d t o a n t i c i p a t e t h e i n n o v a t i o n s t h a t w i l l s h a p e i t s f u t u r e . T h i s b o o k i s a t r i b u t e t o t h e t r a d i t i o n s t h a t h a v e made I t a l i a n p a s t a a c o r n e r s t o n e o f t h e c u l i n a r y w o r l d a n d a c e l e b r a t i o n o f t h e j o y i t b r i n g s t o t a b l e s a r o u n d t h e g l o b e .

My own l o v e a f f a i r w i t h p a s t a b e g a n i n my n o n n a ’ s k i t c h e n , w h e r e I l e a r n e d t h a t t h e s e c r e t i n g r e d i e n t t o a n y d i s h i s t h e l o v e w i t h w h i c h i t ’ s made . I h o p e t o s h a r e a p i e c e o f t h a t l o v e w i t h y o u t h r o u g h t h e r e c i p e s a n d s t o r i e s c o n t a i n e d w i t h i n t h e s e p a g e s

P r e p a r e t o b e d e l i g h t e d by t h e d i v e r s i t y o f f l a v o r s a n d t e x t u r e s t h a t a w a i t y o u . From t h e r o b u s t r a g u s o f t h e N o r t h t o t h e z e s t y s e a f o o d p a s t a s o f t h e S o u t h , y o u r p a l a t e w i l l b e y o u r p a s s p o r t t o t h e r e g i o n s o f I t a l y .

## Buon v i a g g i o a n d b u o n a p p e t i t o !

[ A u t h o r ’ s Name ]

i n t r o d u c t i o n \_ t w i r l s \_ t a s t e s . t x t T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## I n t r o d u c t i o n

I t a l i a n p a s t a : a t a p e s t r y o f h i s t o r y , c u l t u r e , a n d c u l i n a r y a r t i s t r y . From t h e r o l l i n g h i l l s o f T u s c a n y t o t h e b u s t l i n g s t r e e t s o f N a p l e s , p a s t a i s t h e h e a r t b e a t o f I t a l i a n c u i s i n e . I t s o r i g i n s t r a c e b a c k t o a n c i e n t t i m e s , a n d o v e r t h e c e n t u r i e s , i t h a s e v o l v e d i n t o a m y r i a d o f s h a p e s a n d f o r m s , e a c h w i t h i t s own s t o r y t o t e l l .

I n t h i s book , we d e l v e i n t o t h e r i c h t a p e s t r y o f I t a l i a n p a s t a , e x p l o r i n g i t s s t o r i e d p a s t , t h e d i v e r s i t y o f i t s f o r m s , a n d i t s r e v e r e d p l a c e i n I t a l i a n c u l t u r e . We w i l l j o u r n e y t h r o u g h t h e r e g i o n s o f I t a l y , d i s c o v e r i n g how g e o g r a p h y a n d h i s t o r y h a v e s h a p e d t h e n a t i o n ’ s b e l o v e d d i s h . A l o n g t h e way , we w i l l e n c o u n t e r t r a d i t i o n a l r e c i p e s p a s s e d down t h r o u g h g e n e r a t i o n s , a s w e l l a s i n n o v a t i v e c r e a t i o n s t h a t c o n t i n u e t o p u s h t h e b o u n d a r i e s o f f l a v o r a n d f o r m .

The s t r u c t u r e o f t h i s b o o k i s d e s i g n e d t o g u i d e y o u t h r o u g h I t a l y ’ s p a s t a l a n d s c a p e o n e r e g i o n a t a t i m e . E a c h c h a p t e r f o c u s e s on a d i f f e r e n t a r e a , p r o v i d i n g h i s t o r i c a l c o n t e x t , c u l t u r a l a n e c d o t e s , a n d a s e l e c t i o n o f r e c i p e s t h a t h i g h l i g h t t h e r e g i o n ’ s u n i q u e c o n t r i b u t i o n s t o p a s t a c u i s i n e . From t h e h e a r t y , b u t t e r − l a d e n d i s h e s o f t h e N o r t h t o t h e v i b r a n t , o l i v e o i l − b a s e d r e c i p e s o f t h e S o u t h , y o u w i l l g a i n a c o m p r e h e n s i v e u n d e r s t a n d i n g o f I t a l y ’ s p a s t a t r a d i t i o n .

To u s e t h i s book , s i m p l y b e g i n w i t h t h e i n t r o d u c t i o n t o s e t t h e s t a g e f o r y o u r c u l i n a r y a d v e n t u r e . Then , p r o c e e d t h r o u g h t h e c h a p t e r s a t y o u r own p a c e , s a v o r i n g t h e s t o r i e s a n d f l a v o r s o f e a c h r e g i o n . The p a s t a − m a k i n g t e c h n i q u e s s e c t i o n w i l l e q u i p y o u w i t h t h e s k i l l s t o c r e a t e y o u r own p a s t a m a s t e r p i e c e s , w h i l e t h e g l o s s a r y w i l l h e l p y o u n a v i g a t e t h e r i c h v o c a b u l a r y o f I t a l i a n p a s t a t e r m s .

P r e p a r e t o e m b a r k on a f l a v o r f u l j o u r n e y t h r o u g h t i m e a n d t a s t e . ’ T w i r l s & T a s t e s ’ i s more t h a n a c o o k b o o k ; i t ’ s a p a s s p o r t t o t h e s o u l o f I t a l i a n c u i s i n e . Buon v i a g g i o e b u o n a p p e t i t o !

c h a p t e r 1 \_ t w i r l s \_ t a s t e s . t x t

T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## C h a p t e r 1 : The H e a r t o f I t a l y − T u s c a n y

N e s t l e d i n t h e h e a r t o f I t a l y , T u s c a n y i s a r e g i o n r e n o w n e d f o r i t s b r e a t h t a k i n g l a n d s c a p e s , r i c h h i s t o r y , a n d c u l i n a r y e x c e l l e n c e . The r o l l i n g h i l l s , d o t t e d w i t h v i n e y a r d s a n d o l i v e g r o v e s , s e t t h e s t a g e f o r a g a s t r o n o m i c a d v e n t u r e t h a t i s d e e p l y i n t e r t w i n e d w i t h t h e l a n d i t s e l f .

P a s t a p l a y s a p i v o t a l r o l e i n T u s c a n c u i s i n e , e m b o d y i n g t h e s i m p l i c i t y a n d r u s t i c e l e g a n c e t h a t t h e r e g i o n i s known f o r . One c a n n o t t h i n k o f T u s c a n y w i t h o u t e n v i s i o n i n g t h e w i d e , f l a t r i b b o n s o f p a p p a r d e l l e , o f t e n s e r v e d w i t h h e a r t y , game − b a s e d s a u c e s s u c h a s t h e i c o n i c P a p p a r d e l l e a l C i n g h i a l e − a w i l d b o a r r a g u t h a t i s a s r o b u s t i n f l a v o r a s t h e T u s c a n c o u n t r y s i d e .

## R e c i p e s :

## P a p p a r d e l l e a l C i n g h i a l e

## I n g r e d i e n t s :

− 4 0 0 g p a p p a r d e l l e p a s t a

− 2 t a b l e s p o o n s e x t r a − v i r g i n o l i v e o i l

− 1 onion , f i n e l y chopped

− 2 c a r r o t s , f i n e l y c h o p p e d

− 2 c e l e r y s t a l k s , f i n e l y c h o p p e d

− 2 g a r l i c c l o v e s , m i n c e d

− 500 g w i l d b o a r meat , minced − 1 cup r e d wine

− 400 g canned t o m a t o e s , c r u s h e d

− S a l t a n d p e p p e r t o t a s t e

− G r a t e d P a r m e s a n c h e e s e , f o r s e r v i n g

## I n s t r u c t i o n s :

1 . H e a t t h e o l i v e o i l i n a l a r g e p a n o v e r medium h e a t . Add t h e o n i o n , c a r r o t s , c e l e r y , a n d g a r l i c , a n d s a u t e u n t i l s o f t e n e d .

2 . I n c r e a s e t h e h e a t t o h i g h , a d d t h e w i l d b o a r m e a t , a n d c o o k u n t i l b r o w n e d

3 . P o u r i n t h e r e d w i n e a n d l e t i t r e d u c e by h a l f

4 . Add t h e c r u s h e d t o m a t o e s , s a l t , a n d p e p p e r . Lower t h e h e a t , c o v e r , a n d s i m m e r f o r a t l e a s t 2 h o u r s , s t i r r i n g o c c a s i o n a l l y .

5 . Cook t h e p a p p a r d e l l e i n a l a r g e p o t o f s a l t e d b o i l i n g w a t e r u n t i l a l d e n t e , t h e n d r a i n .

6 . T o s s t h e p a s t a w i t h t h e w i l d b o a r r a g u a n d s e r v e w i t h a s p r i n k l e o f P a r m e s a n c h e e s e .

T h i s d i s h t e l l s a s t o r y o f t h e T u s c a n h u n t , t r a d i t i o n , a n d t h e d e e p c o n n e c t i o n b e t w e e n t h e l a n d a n d t h e t a b l e . The r o b u s t f l a v o r s a n d h e a r t y t e x t u r e a r e e m b l e m a t i c o f t h e r e g i o n ’ s c u i s i n e , o f f e r i n g a t a s t e o f T u s c a n y ’ s c u l i n a r y h e r i t a g e .

As you r e c r e a t e t h e s e r e c i p e s , i m a g i n e t h e T u s c a n l a n d s c a p e a n d t h e g e n e r a t i o n s o f c o o k s who h a v e p e r f e c t e d t h e s e d i s h e s o v e r c e n t u r i e s . E a c h i n g r e d i e n t , e a c h s t e p , i s a t e s t a m e n t t o t h e l o v e a n d r e s p e c t f o r t h e f o o d t h a t i s a t t h e h e a r t o f T u s c a n l i f e .

[ N o t e : High − q u a l i t y i m a g e s o f t h e T u s c a n l a n d s c a p e a n d t h e c o m p l e t e d d i s h e s w i l l b e i n c l u d e d i n t h e f i n a l p u b l i c a t i o n t o e n h a n c e t h e r e a d e r ’ s e x p e r i e n c e . ]

R e v i e w f o r a c c u r a c y , c l a r i t y , a n d c o n s i s t e n c y w i t h t h e book ’ s t h e m e h a s b e e n c o n d u c t e d t o e n s u r e t h a t t h i s c h a p t e r a l i g n s w i t h t h e j o u r n e y t h r o u g h I t a l i a n p a s t a t h a t ’ T w i r l s & T a s t e s ’ p r o m i s e s t o d e l i v e r .

T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## C h a p t e r 2 : The R i c h e s o f E m i l i a −Romagna

E m i l i a −Romagna , a r e g i o n c e l e b r a t e d f o r i t s c u l i n a r y c o n t r i b u t i o n s , i s a t r e a s u r e t r o v e o f I t a l i a n g a s t r o n o m y . The f e r t i l e p l a i n s a n d t h e Po R i v e r c r e a t e a l u s h e n v i r o n m e n t f o r a g r i c u l t u r e , g i v i n g r i s e t o a v a r i e t y o f i n g r e d i e n t s t h a t f o r m t h e b a c k b o n e o f i t s r i c h c u i s i n e .

I n E m i l i a −Romagna , p a s t a i s n o t j u s t f o o d ; i t ’ s a work o f a r t . The r e g i o n i s t h e b i r t h p l a c e o f many p a s t a s h a p e s a n d s i z e s , e a c h w i t h i t s own s t o r y . T a g l i a t e l l e , t o r t e l l i n i , a n d l a s a g n e a r e j u s t a f e w e x a m p l e s o f t h e p a s t a t h a t h a v e e a r n e d t h i s r e g i o n a w o r l d w i d e r e p u t a t i o n .

## R e c i p e s :

## T a g l i a t e l l e a l Ragu B o l o g n e s e

I n g r e d i e n t s :   
− 4 0 0 g t a g l i a t e l l e p a s t a   
− 2 t a b l e s p o o n s e x t r a − v i r g i n o l i v e o i l   
1 o n i o n , f i n e l y c h o p p e d   
1 c a r r o t , f i n e l y c h o p p e d   
1 c e l e r y s t a l k , f i n e l y c h o p p e d   
2 g a r l i c c l o v e s , m i n c e d   
300 g ground b e e f   
150 g ground pork   
1 c u p r e d w i n e   
− 800 g canned t o m a t o e s , c r u s h e d   
S a l t a n d p e p p e r t o t a s t e   
− G r a t e d P a r m i g i a n o − R e g g i a n o , f o r s e r v i n g

## I n s t r u c t i o n s :

1 . H e a t t h e o l i v e o i l i n a l a r g e p a n o v e r medium h e a t . Add t h e o n i o n , c a r r o t , c e l e r y , a n d g a r l i c , a n d s a u t e u n t i l s o f t e n e d .

4 . Add t h e c r u s h e d t o m a t o e s , s a l t , a n d p e p p e r . Lower t h e h e a t , c o v e r , a n d s i m m e r f o r a t l e a s t 2 h o u r s , s t i r r i n g o c c a s i o n a l l y .

5 . Cook t h e t a g l i a t e l l e i n a l a r g e p o t o f s a l t e d b o i l i n g w a t e r u n t i l a l d e n t e , t h e n d r a i n .

6 . T o s s t h e p a s t a w i t h t h e r a g u a n d s e r v e w i t h a s p r i n k l e o f P a r m i g i a n o − R e g g i a n o .

T h i s c l a s s i c d i s h i s a t e s t a m e n t t o t h e c u l i n a r y e x p e r t i s e o f E m i l i a −Romagna , w h e r e t h e s l o w c o o k i n g o f t h e r a g u b r i n g s o u t t h e d e p t h o f f l a v o r s t h a t t h i s r e g i o n i s known f o r .

## E r b a z z o n e ( S p i n a c h and Cheese P i e )

I n g r e d i e n t s :   
− 500 g s p i n a c h , washed and chopped   
− 2 0 0 g r i c o t t a c h e e s e   
− 100 g P a r m i g i a n o − Reggiano , g r a t e d   
− 2 eggs   
− S a l t a n d p e p p e r t o t a s t e   
− 2 s h e e t s o f p u f f p a s t r y

## I n s t r u c t i o n s :

3 . Lay o n e s h e e t o f p u f f p a s t r y on a b a k i n g s h e e t . S p r e a d t h e s p i n a c h m i x t u r e o v e r t h e p a s t r y , l e a v i n g a s m a l l b o r d e r .

4 . C o v e r w i t h t h e s e c o n d s h e e t o f p u f f p a s t r y , s e a l t h e e d g e s , a n d make s m a l l c u t s on t h e t o p t o a l l o w s t e a m t o e s c a p e .

E r b a z z o n e o f f e r s a g l i m p s e i n t o t h e r u s t i c , y e t r e f i n e d f l a v o r s o f E m i l i a −Romagna ’ s c o u n t r y s i d e , w h e r e g r e e n s a n d c h e e s e s a r e t u r n e d i n t o c o m f o r t i n g , s a v o r y p i e s .

[ N o t e : High − q u a l i t y i m a g e s o f t h e E m i l i a −Romagna l a n d s c a p e a n d t h e c o m p l e t e d d i s h e s w i l l b e i n c l u d e d i n t h e f i n a l p u b l i c a t i o n t o e n h a n c e t h e r e a d e r ’ s e x p e r i e n c e . ]

R e v i e w f o r a c c u r a c y , c l a r i t y , a n d c o n s i s t e n c y w i t h t h e book ’ s t h e m e h a s b e e n c o n d u c t e d t o e n s u r e t h a t t h i s c h a p t e r a l i g n s w i t h t h e j o u r n e y t h r o u g h I t a l i a n p a s t a t h a t ’ T w i r l s & T a s t e s ’ p r o m i s e s t o d e l i v e r .

c h a p t e r 3 \_ t w i r l s \_ t a s t e s . t x t   
T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## C h a p t e r 3 : The Sun and Sea o f Campania

C a m p a n i a , w i t h i t s s u n − d r e n c h e d c o a s t l i n e s a n d t h e v i b r a n t c i t y o f N a p l e s , i s a r e g i o n w h e r e t h e w a r m t h o f t h e s u n a n d t h e f r e s h n e s s o f t h e s e a a r e r e f l e c t e d i n i t s c u i s i n e . The r e g i o n ’ s v o l c a n i c s o i l a n d m i l d c l i m a t e c o n t r i b u t e t o t h e c u l t i v a t i o n o f e x q u i s i t e p r o d u c e , i n c l u d i n g t h e f a m o u s S a n M a r z a n o t o m a t o e s a n d t h e r e v e r e d b u f f a l o m o z z a r e l l a .

P a s t a i n C a m p a n i a i s c e l e b r a t e d i n i t s many f o r m s , f r o m t h e d r y p a s t a o f G r a g n a n o t o t h e h a n d − s h a p e d d e l i g h t s l i k e o r e c c h i e t t e . S e a f o o d p l a y s a s i g n i f i c a n t r o l e i n t h e r e g i o n a l d i s h e s , w i t h r e c i p e s t h a t h a v e b e e n p a s s e d down t h r o u g h g e n e r a t i o n s

## R e c i p e s :

## S p a g h e t t i a l l e V o n g o l e

I n g r e d i e n t s :

− 4 0 0 g s p a g h e t t i

− 4 t a b l e s p o o n s e x t r a − v i r g i n o l i v e o i l

− 4 g a r l i c c l o v e s , m i n c e d

− 1 s m a l l r e d c h i l i , f i n e l y c h o p p e d

− 500 g clams , c l e a n e d

− 1 / 2 c u p w h i t e w i n e

− A h a n d f u l o f f r e s h p a r s l e y , c h o p p e d

− S a l t t o t a s t e

## I n s t r u c t i o n s :

1 . H e a t t h e o l i v e o i l i n a l a r g e p a n o v e r medium h e a t . Add t h e g a r l i c a n d c h i l i , a n d s a u t e u n t i l f r a g r a n t .

2 . Add t h e c l a m s a n d w h i t e w i n e , c o v e r , a n d c o o k u n t i l t h e c l a m s o p e n , a b o u t 5 −7 m i n u t e s .

3 . Cook t h e s p a g h e t t i i n a l a r g e p o t o f s a l t e d b o i l i n g w a t e r u n t i l a l d e n t e , t h e n d r a i n , r e s e r v i n g some o f t h e p a s t a w a t e r .

4 . Add t h e s p a g h e t t i t o t h e p a n w i t h t h e c l a m s , a d d i n g a l i t t l e p a s t a w a t e r i f n e e d e d t o l o o s e n t h e s a u c e .

S p a g h e t t i a l l e V o n g o l e i s a d i s h t h a t c a p t u r e s t h e e s s e n c e o f C a m p a n i a ’ s c o a s t l i n e , w i t h t h e b r i n y f l a v o r s o f t h e c l a m s c o m p l e m e n t i n g t h e s i m p l i c i t y o f t h e p a s t a .

## P i z z a N a p o l e t a n a

I n g r e d i e n t s :

− 500 g p i z z a dough

− 200 g San Marzano t o m a t o e s , c r u s h e d

− 2 0 0 g b u f f a l o m o z z a r e l l a , s l i c e d

− F r e s h b a s i l l e a v e s

− E x t r a − v i r g i n o l i v e o i l

− S a l t t o t a s t e

## I n s t r u c t i o n s :

1 . P r e h e a t t h e o v e n t o i t s h i g h e s t s e t t i n g , i d e a l l y 2 5 0 C ( 4 8 0 F ) o r h i g h e r .

2 . R o l l o u t t h e p i z z a d o u g h t o f o r m a t h i n b a s e a n d p l a c e i t on a p i z z a s t o n e o r b a k i n g s h e e t .

3 . S p r e a d t h e c r u s h e d t o m a t o e s o v e r t h e b a s e , l e a v i n g a s m a l l b o r d e r .

```csv
I n g r e d i e n t s :
− 4 0 0 g s h o r t p a s t a , s u c h a s r i g a t o n i o r p e n n e
− 3 t a b l e s p o o n s e x t r a − v i r g i n o l i v e o i l
1 e g g p l a n t , c u t i n t o c u b e s
− 2 g a r l i c c l o v e s , m i n c e d
− 400 g canned t o m a t o e s , c r u s h e d
− A h a n d f u l o f f r e s h b a s i l , t o r n
− S a l t a n d p e p p e r t o t a s t e
− R i c o t t a s a l a t a , g r a t e d , f o r s e r v i n g
```

Types o f P a s t a Dough :

5 . D r i z z l e w i t h o l i v e o i l a n d s p r i n k l e w i t h s a l t .

4 . D i s t r i b u t e t h e m o z z a r e l l a s l i c e s a n d b a s i l l e a v e s on t o p o f t h e t o m a t o e s .

6 . Bake f o r 8 −10 m i n u t e s , o r u n t i l t h e c r u s t i s g o l d e n a n d t h e c h e e s e i s b u b b l i n g .

P i z z a N a p o l e t a n a , w i t h i t s s o f t , chewy c r u s t a n d f r e s h t o p p i n g s , i s a b e l o v e d s t a p l e o f C a m p a n i a n c u i s i n e a n d a s y m b o l o f I t a l i a n f o o d c u l t u r e a r o u n d t h e w o r l d .

[ N o t e : High − q u a l i t y i m a g e s o f t h e C a m p a n i a l a n d s c a p e a n d t h e c o m p l e t e d d i s h e s w i l l b e i n c l u d e d i n t h e f i n a l p u b l i c a t i o n t o e n h a n c e t h e r e a d e r ’ s e x p e r i e n c e . ]

R e v i e w f o r a c c u r a c y , c l a r i t y , a n d c o n s i s t e n c y w i t h t h e book ’ s t h e m e h a s b e e n c o n d u c t e d t o e n s u r e t h a t t h i s c h a p t e r a l i g n s w i t h t h e j o u r n e y t h r o u g h I t a l i a n p a s t a t h a t ’ T w i r l s & T a s t e s ’ p r o m i s e s t o d e l i v e r .

c h a p t e r 4 \_ t w i r l s \_ t a s t e s . t x t   
T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## C h a p t e r 4 : The I s l a n d F l a v o r s o f S i c i l y

S i c i l y , t h e l a r g e s t i s l a n d i n t h e M e d i t e r r a n e a n , b o a s t s a c u l i n a r y l a n d s c a p e a s d i v e r s e a n d v i b r a n t a s i t s h i s t o r y . I n f l u e n c e s f r o m G r e e k , Arab , a n d Norman c o n q u e r o r s h a v e woven a r i c h t a p e s t r y o f f l a v o r s t h a t d e f i n e S i c i l i a n c u i s i n e . The i s l a n d ’ s f e r t i l e s o i l a n d b o u n t i f u l s e a s p r o v i d e a n a b u n d a n c e o f f r e s h i n g r e d i e n t s t h a t i n s p i r e t h e l o c a l d i s h e s .

P a s t a i n S i c i l y i s o f t e n p a i r e d w i t h t h e b o l d f l a v o r s o f t h e s e a a n d t h e s w e e t n e s s o f t h e i s l a n d ’ s p r o d u c e . D i s h e s l i k e P a s t a a l l a Norma a n d S p a g h e t t i a i R i c c i d i Mare s h o w c a s e t h e c r e a t i v i t y a n d r e s o u r c e f u l n e s s o f S i c i l i a n c o o k i n g .

## R e c i p e s :

## P a s t a a l l a Norma

## I n g r e d i e n t s :

## I n s t r u c t i o n s :

1 . H e a t t h e o l i v e o i l i n a l a r g e p a n o v e r medium h e a t . Add t h e e g g p l a n t c u b e s a n d f r y u n t i l g o l d e n b r o w n . Remove a n d s e t a s i d e .

2 . I n t h e same p a n , a d d t h e g a r l i c a n d s a u t e u n t i l f r a g r a n t .

3 . Add t h e c r u s h e d t o m a t o e s , b a s i l , s a l t , a n d p e p p e r . Simmer f o r 10 m i n u t e s .

4 . Cook t h e p a s t a i n a l a r g e p o t o f s a l t e d b o i l i n g w a t e r u n t i l a l d e n t e , t h e n d r a i n .

5 . T o s s t h e p a s t a w i t h t h e t o m a t o s a u c e a n d f r i e d e g g p l a n t .

6 . S e r v e w i t h a g e n e r o u s s p r i n k l i n g o f r i c o t t a s a l a t a

P a s t a a l l a Norma i s a c e l e b r a t i o n o f S i c i l y ’ s a g r i c u l t u r a l b o u n t y , w i t h t h e c r e a m y e g g p l a n t a n d t a n g y r i c o t t a s a l a t a c r e a t i n g a h a r m o n i o u s b l e n d o f f l a v o r s .

## Caponata

## I n g r e d i e n t s :

− 1 l a r g e e g g p l a n t , c u t i n t o c u b e s

− 2 c e l e r y s t a l k s , c h o p p e d

− 1 onion , chopped

− 3 t a b l e s p o o n s c a p e r s , r i n s e d

− A h a n d f u l o f g r e e n o l i v e s , p i t t e d a n d c h o p p e d

− 2 t a b l e s p o o n s p i n e n u t s

− 2 t a b l e s p o o n s s u g a r

− 3 t a b l e s p o o n s r e d w i n e v i n e g a r

− 400 g canned t o m a t o e s , c r u s h e d

− S a l t a n d p e p p e r t o t a s t e

## I n s t r u c t i o n s :

1 . F r y t h e e g g p l a n t c u b e s i n o l i v e o i l u n t i l g o l d e n b r o w n . Remove a n d s e t a s i d e .

2 . I n t h e same p a n , s a u t e t h e c e l e r y a n d o n i o n u n t i l s o f t e n e d .

3 . Add t h e c a p e r s , o l i v e s , p i n e n u t s , s u g a r , a n d v i n e g a r , a n d c o o k f o r a f e w m i n u t e s .

4 . Add t h e c r u s h e d t o m a t o e s a n d f r i e d e g g p l a n t , s e a s o n w i t h s a l t a n d p e p p e r , a n d s i m m e r f o r 15 m i n u t e s .

C a p o n a t a i s a q u i n t e s s e n t i a l S i c i l i a n d i s h , a s w e e t a n d s o u r v e g e t a b l e m e d l e y t h a t c a n b e s e r v e d a s a n a p p e t i z e r o r a s i d e , e m b o d y i n g t h e i s l a n d ’ s c o m p l e x c u l i n a r y h e r i t a g e .

[ N o t e : High − q u a l i t y i m a g e s o f t h e S i c i l i a n l a n d s c a p e a n d t h e c o m p l e t e d d i s h e s w i l l b e i n c l u d e d i n t h e f i n a l p u b l i c a t i o n t o e n h a n c e t h e r e a d e r ’ s e x p e r i e n c e . ]

R e v i e w f o r a c c u r a c y , c l a r i t y , a n d c o n s i s t e n c y w i t h t h e book ’ s t h e m e h a s b e e n c o n d u c t e d t o e n s u r e t h a t t h i s c h a p t e r a l i g n s w i t h t h e j o u r n e y t h r o u g h I t a l i a n p a s t a t h a t ’ T w i r l s & T a s t e s ’ p r o m i s e s t o d e l i v e r .

c h a p t e r 5 \_ t w i r l s \_ t a s t e s . t x t   
T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## C h a p t e r 5 : The A r t o f P a s t a Making

The a r t o f p a s t a m a k i n g i s a c h e r i s h e d t r a d i t i o n i n I t a l y , p a s s e d down t h r o u g h g e n e r a t i o n s . T h i s c h a p t e r i s d e d i c a t e d t o t e a c h i n g y o u t h e t i m e − h o n o r e d t e c h n i q u e s o f c r e a t i n g p a s t a f r o m s c r a t c h . W i t h d e t a i l e d i n s t r u c t i o n s a n d a c c o m p a n y i n g i m a g e s , you ’ l l l e a r n t o c r a f t v a r i o u s t y p e s o f p a s t a d o u g h , s h a p e t h e m i n t o b e a u t i f u l f o r m s , a n d c o o k t h e m t o p e r f e c t i o n .

1 . B a s i c Egg P a s t a Dough   
I n g r e d i e n t s :   
− 400 g ’ 0 0 ’ f l o u r   
− 4 l a r g e e g g s   
I n s t r u c t i o n s :   
− Mound t h e f l o u r on a c l e a n s u r f a c e a n d c r e a t e a w e l l i n t h e c e n t e r   
− C r a c k t h e e g g s i n t o t h e w e l l a n d g r a d u a l l y i n c o r p o r a t e t h e f l o u r f r o m t h e i n s i d e r i m o f t h e w e l l .   
− Knead t h e d o u g h f o r a b o u t 10 m i n u t e s u n t i l s m o o t h a n d e l a s t i c .   
− Wrap i n p l a s t i c a n d l e t r e s t f o r 30 m i n u t e s a t room t e m p e r a t u r e .

2 . S e m o l i n a P a s t a Dough   
I n g r e d i e n t s :

## − 4 0 0 g s e m o l i n a f l o u r

− 200 ml w a t e r

I n s t r u c t i o n s :

− Mix t h e s e m o l i n a f l o u r a n d w a t e r u n t i l a d o u g h b e g i n s t o f o r m .

− Knead t h e d o u g h on a c l e a n s u r f a c e u n t i l s m o o t h a n d f i r m , a b o u t 10 m i n u t e s .

− Wrap i n p l a s t i c a n d l e t r e s t f o r 30 m i n u t e s a t room t e m p e r a t u r e .

## S h a p i n g T e c h n i q u e s :

1 . R o l l i n g a n d C u t t i n g

− R o l l o u t t h e r e s t e d d o u g h u s i n g a r o l l i n g p i n o r p a s t a m a c h i n e t o t h e d e s i r e d t h i c k n e s s .

C u t i n t o s t r i p s f o r t a g l i a t e l l e , o r s q u a r e s f o r r a v i o l i .

## 2 . Hand− Shaping

− F o r s h a p e s l i k e o r e c c h i e t t e , p i n c h o f f s m a l l p i e c e s o f d o u g h a n d s h a p e w i t h y o u r f i n g e r s .

− F o r c a v a t e l l i , r o l l s m a l l p i e c e s o f d o u g h a g a i n s t t h e s u r f a c e o f a g n o c c h i b o a r d o r f o r k t o c r e a t e r i d g e s

## Cooking T ips :

1 . B o i l i n g P a s t a

− Use a l a r g e p o t o f s a l t e d b o i l i n g w a t e r f o r c o o k i n g p a s t a .

− Cook u n t i l a l d e n t e , u s u a l l y 2 −4 m i n u t e s f o r f r e s h p a s t a .

− D r a i n a n d t o s s w i t h y o u r f a v o r i t e s a u c e .

2 . S t o r i n g P a s t a

− F r e s h p a s t a c a n b e d r i e d on a r a c k a n d s t o r e d i n a n a i r t i g h t c o n t a i n e r .

− I t c a n a l s o b e f r o z e n f o r up t o a m o n t h .

[ N o t e : High − q u a l i t y i m a g e s o f t h e p a s t a − m a k i n g p r o c e s s a n d t h e v a r i o u s s h a p e s w i l l b e i n c l u d e d i n t h e f i n a l p u b l i c a t i o n t o g u i d e t h e r e a d e r . ]

T h i s c h a p t e r p r o v i d e s a p r a c t i c a l g u i d e t o m a k i n g p a s t a a t home . By f o l l o w i n g t h e s e s t e p s , you ’ l l b e a b l e t o c r e a t e a v a r i e t y o f p a s t a d i s h e s w i t h t h e a u t h e n t i c f l a v o r s a n d t e x t u r e s o f I t a l y . E n j o y t h e s a t i s f a c t i o n o f m a k i n g p a s t a f r o m s c r a t c h a n d s h a r i n g y o u r c r e a t i o n s w i t h f a m i l y a n d f r i e n d s .

R e v i e w f o r a c c u r a c y , c l a r i t y , a n d c o n s i s t e n c y w i t h t h e book ’ s t h e m e h a s b e e n c o n d u c t e d t o e n s u r e t h a t t h i s c h a p t e r a l i g n s w i t h t h e j o u r n e y t h r o u g h I t a l i a n p a s t a t h a t ’ T w i r l s & T a s t e s ’ p r o m i s e s t o d e l i v e r .

g l o s s a r y \_ t w i r l s \_ t a s t e s . t x t

T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## G l o s s a r y o f I t a l i a n P a s t a T e r m s

T h i s g l o s s a r y i s d e s i g n e d t o h e l p y o u u n d e r s t a n d t h e t e r m i n o l o g y u s e d t h r o u g h o u t t h i s b o o k . I t i n c l u d e s d e f i n i t i o n s o f p a s t a s h a p e s , i n g r e d i e n t s , a n d c o o k i n g t e c h n i q u e s commonly f o u n d i n I t a l i a n c u i s i n e .

− Al d e n t e : P a s t a c o o k e d u n t i l i t i s f i r m t o t h e b i t e . The i d e a l t e x t u r e f o r m o s t p a s t a d i s h e s .

− B o l o g n e s e : A meat − b a s e d s a u c e o r i g i n a t i n g f r o m B o l o g n a , t y p i c a l l y made w i t h a m i x t u r e o f b e e f a n d p o r k .

− C i n g h i a l e : W i l d b o a r , o f t e n u s e d i n h e a r t y T u s c a n p a s t a s a u c e s .

− F a r f a l l e : ’ B u t t e r f l i e s ’ i n I t a l i a n , t h i s p a s t a s h a p e r e s e m b l e s bow t i e s o r b u t t e r f l y w i n g s .

− F u s i l l i : A c o r k s c r e w − s h a p e d p a s t a t h a t i s e x c e l l e n t f o r h o l d i n g o n t o s a u c e s .

− G n o c c h i : S m a l l d u m p l i n g s made f r o m p o t a t o e s , f l o u r , a n d s o m e t i m e s r i c o t t a c h e e s e .

− G r a n a P a d a n o : A h a r d , s l o w − r i p e n e d , s e m i − f a t c h e e s e f r o m I t a l y , s i m i l a r t o P a r m i g i a n o − R e g g i a n o .

− L a s a g n e : Wide , f l a t p a s t a s h e e t s u s e d i n l a y e r i n g d i s h e s w i t h s a u c e a n d c h e e s e .

− O r e c c h i e t t e : ’ L i t t l e e a r s ’ i n I t a l i a n , t h i s p a s t a s h a p e i s a s m a l l , e a r − l i k e r o u n d d i s c .

− P a p p a r d e l l e : B r o a d , f l a t p a s t a n o o d l e s , o f t e n s e r v e d w i t h r i c h , m e a t y s a u c e s .

− P a r m i g i a n o − R e g g i a n o : A h a r d , g r a n u l a r c h e e s e known a s P a r m e s a n , u s e d g r a t e d o v e r p a s t a d i s h e s .

− P e n n e : Tube − s h a p e d p a s t a w i t h a n g l e d e n d s , o f t e n u s e d i n p a s t a s a l a d s o r b a k e d d i s h e s .

− Ragu : A meat − b a s e d s a u c e , which i s simmered w i t h t o m a t o e s , o n i o n s , and o t h e r s e a s o n i n g s .

− R i c o t t a : A c r e a m y I t a l i a n whey c h e e s e u s e d i n v a r i o u s p a s t a f i l l i n g s a n d s a u c e s .

− S a n M a r z a n o t o m a t o e s : A v a r i e t y o f plum t o m a t o e s c o n s i d e r e d by many c h e f s t o b e t h e b e s t f o r m a k i n g t o m a t o s a u c e s .

− T a g l i a t e l l e : Long , r i b b o n − l i k e p a s t a s i m i l a r t o f e t t u c c i n e , t r a d i t i o n a l l y s e r v e d w i t h B o l o g n e s e s a u c e .

T h i s g l o s s a r y w i l l a s s i s t y o u i n b e t t e r u n d e r s t a n d i n g t h e r e c i p e s a n d t h e c u l t u r a l s i g n i f i c a n c e b e h i n d e a c h d i s h . As y o u e x p l o r e t h e d i v e r s e w o r l d o f I t a l i a n p a s t a , r e f e r t o t h e s e t e r m s t o e n h a n c e y o u r c u l i n a r y k n o w l e d g e a n d a p p r e c i a t i o n .

## i n d e x \_ t w i r l s \_ t a s t e s . t x t

T w i r l s & T a s t e s : A J o u r n e y T h r o u g h I t a l i a n P a s t a

## Index

```csv
R e c i p e s :
− P a p p a r d e l l e a l C i n g h i a l e , C h a p t e r 1
− T a g l i a t e l l e a l Ragu B o l o g n e s e , C h a p t e r 2
E r b a z z o n e ( S p i n a c h and Cheese P i e ) , C h a p t e r 2
S p a g h e t t i a l l e V o n g o l e , C h a p t e r 3
P i z z a N a p o l e t a n a , C h a p t e r 3
P a s t a a l l a Norma , C h a p t e r 4
C a p o n a t a , C h a p t e r 4
B a s i c Egg P a s t a Dough , C h a p t e r 5
− S e m o l i n a P a s t a Dough , C h a p t e r 5
```

```csv
I n g r e d i e n t s :
’ 0 0 ’ f l o u r , C h a p t e r 5
− Al d e n t e , G l o s s a r y
− B o l o g n e s e , G l o s s a r y
B u f f a l o m o z z a r e l l a , C h a p t e r 3
C i n g h i a l e , G l o s s a r y
Clams , C h a p t e r 3
E g g p l a n t , C h a p t e r 4
E g g s , C h a p t e r 5
E x t r a − v i r g i n o l i v e o i l , C h a p t e r s 1 , 2 , 3 , 4 , 5
F a r f a l l e , G l o s s a r y
F u s i l l i , G l o s s a r y
G a r l i c , C h a p t e r s 1 , 2 , 3 , 4
G n o c c h i , G l o s s a r y
Grana Padano , G l o s s a r y
Ground b e e f , C h a p t e r 2
Ground p o r k , C h a p t e r 2
− Lasagne , G l o s s a r y
```

M o z z a r e l l a , C h a p t e r 3   
O r e c c h i e t t e , G l o s s a r y   
P a p p a r d e l l e , G l o s s a r y   
Parmesan c h e e s e , C h a p t e r 1   
P a r m i g i a n o − R e g g i a n o , C h a p t e r 2 , G l o s s a r y   
P e c o r i n o , G l o s s a r y   
P e n n e , G l o s s a r y   
Rag \ u 0 0 f 9 , G l o s s a r y   
Red w i n e , C h a p t e r s 1 , 2   
R i c o t t a , C h a p t e r 2 , G l o s s a r y   
R i c o t t a s a l a t a , C h a p t e r 4   
San Marzano t o m a t o e s , C h a p t e r 3 , G l o s s a r y   
S e m o l i n a f l o u r , C h a p t e r 5   
S p a g h e t t i , C h a p t e r 3 , G l o s s a r y   
T a g l i a t e l l e , C h a p t e r 2 , G l o s s a r y   
T o m a t o e s , C h a p t e r s 1 , 2 , 4   
T o r t e l l i n i , G l o s s a r y   
W a t e r , C h a p t e r 5   
W i l d b o a r m e a t , C h a p t e r 1   
Key Terms :   
Al d e n t e , G l o s s a r y   
B o l o g n e s e , G l o s s a r y   
C i n g h i a l e , G l o s s a r y   
F a r f a l l e , G l o s s a r y   
F u s i l l i , G l o s s a r y   
G n o c c h i , G l o s s a r y   
Grana Padano , G l o s s a r y   
L a s a g n e , G l o s s a r y   
O r e c c h i e t t e , G l o s s a r y   
P a p p a r d e l l e , G l o s s a r y   
P a r m i g i a n o − Reggiano , G l o s s a r y   
P e c o r i n o , G l o s s a r y   
P e n n e , G l o s s a r y   
Rag \ u 0 0 f 9 , G l o s s a r y   
R i c o t t a , G l o s s a r y   
San Marzano t o m a t o e s , G l o s s a r y   
S p a g h e t t i , G l o s s a r y   
T a g l i a t e l l e , G l o s s a r y   
T o r t e l l i n i , G l o s s a r y   
N o t e : P a g e n u m b e r s w i l l b e a d d e d o n c e t h e f i n a l l a y o u t o f t h e b o o k i s c o m p l e t e .

# For this implementation of L2MAC we modified the system prompt to be

O b j e c t i v e : W r i t e l a r g e a m o u n t s o f t e x t f o r t h e f o l l o w i n g t a s k P l e a s e n o t e t h a t t h e g e n e r a t e d t e x t s h o u l d b e f u l l y c o m p l e t e . No p l a c e h o l d e r s . O n l y u s e t h e f u n c t i o n s you h a v e b e e n p r o v i d e d w i t h . O n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ t o o u t p u t t e x t f i l e s .

You m u s t a c t a u t o n o m o u s l y a n d y o u w i l l r e c e i v e no human i n p u t a t a n y s t a g e . You h a v e t o r e t u r n a s o u t p u t t h e c o m p l e t e t e x t f o r c o m p l e t i n g t h i s t a s k , a n d c o r r e c t l y i n c o r p o r a t e i t i n t o t h e e x i s t i n g g e n e r a t e d t e x t f i l e s .

P r o v i d e t h e t e x t t o a c h i e v e t h e t a s k c o n d i t i o n e d on t h e e x i s t i n g g e n e r a t e d t e x t −−− i n c l u d i n g c h a n g i n g t h e e x i s t i n g g e n e r a t e d t e x t w h e r e n e c e s s a r y .

You c a n n o t v i s u a l i z e a n y g r a p h i c a l o u t p u t . You e x i s t w i t h i n a A c t o r Model m a c h i n e , a n d when y o u l i s t o u t s t e p s , e a c h s t e p w i l l b e t a k e n by a new s e p a r a t e s u b − ChatGPT m o d e l . When y o u l i s t o u t a s u b − t a s k s t e p s , y o u c a n o p t i o n a l l y s p e c i f y t h e s u b − t a s k v a l i d a t i o n t o c h e c k t h a t i t h a s b e e n c o m p l e t e d s u c c e s s f u l l y .

No d a t a s a v e d t o d i s k w i l l p e r s i s t b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .

Use t h e f u n c t i o n s p r o v i d e d . When c a l l i n g f u n c t i o n s o n l y p r o v i d e a RFC8259 c o m p l i a n t JSON r e q u e s t f o l l o w i n g t h i s f o r m a t w i t h o u t d e v i a t i o n .

## And the initial prompt to be

F i r s t l a y o u t t h e t h e s t r u c t u r e o u t l i n e o f t h e book , a n d t h e c h a p t e r s w i t h d e t a i l e d d e s c r i p t i o n s o f w h a t e a c h c h a p t e r w i l l c o n t a i n . F e e l f r e e t o make a q u i c k comment on t h e p u r p o s e o f e a c h c h a p t e r .   
Do n o t comment on w h a t e v e r y p i e c e o f t e x t d o e s . P l e a s e n o t e t h a t t h e t e x t s h o u l d b e f u l l y c o m p l e t e . No p l a c e h o l d e r s . You w i l l s t a r t w i t h t h e " d e t a i l e d \_ o u t l i n e " f i l e , t h e n go t o t h e c h a p t e r s i n c h r o n o l o g i c a l o r d e r , a n d s o on .   
P l e a s e n o t e t h a t t h e t e x t s h o u l d b e f u l l y c o m p l e t e . No p l a c e h o l d e r s .   
F o l l o w a t h e b e s t p r a c t i c e s f o r w r i t i n g a book , a n d n a m i n g c o n v e n t i o n .   
Make s u r e t h a t f i l e s a r e c o r r e c t l y c o n d i t i o n e d on t h e s u b s e q u e n t c h a p t e r s a n d o u t l i n e ( s ) . The t e x t s h o u l d b e f u l l y c o m p l e t e . Make s u r e t h a t t e x t i n d i f f e r e n t f i l e s a r e c o m p a t i b l e w i t h e a c h o t h e r .   
When w r i t i n g t e x t i f y o u a r e u n s u r e , w r i t e t h e m o s t p l a u s i b l e t e x t .

U s e f u l t o know :

I t i s h e l p f u l t o w r i t e a d e t a i l e d o u t l i n e o f t h e b o o k f i r s t , a n d t h e n w r i t e t h e c h a p t e r s i n o r d e r .   
A l w a y s a d d a comment b r i e f l y d e s c r i b i n g t h e p u r p o s e o f e a c h f i l e .   
A l w a y s f o l l o w t h e b e s t p r a c t i c e s f o r t h e r e q u e s t e d s t r u c t u r e a n d how t o p a c k a g e t h e c o m p l e t e d b o o k .

U n d e r s t a n d t h e p r o b l e m , by c r e a t i n g a n e x t r e m e l y d e t a i l e d s t e p −by − s t e p p l a n , w h e r e e a c h s t e p i s l o n g ( m u l t i p l e s e n t e n c e s ) a n d i n t o t a l i n c l u d e s e v e r y s i n g l e f e a t u r e r e q u i r e m e n t s p e c i f i e d a b o v e , f e e l f r e e t o c o p y d i r e c t l y f r o m i t . Use no more t h a n 10 s t e p s i n t h e p l a n . P e r f o r m a d d i t i o n a l , c h e c k s a n d e v a l u a t i o n a t e a c h s t e p when a p p l i c a b l e t o h e l p make a n e x c e l l e n t c o h e r e n t book , w h e r e a l l t h e t e x t i s f u l l y c o m p l e t e . Use b e s t b o o k d e s i g n p r a c t i c e s , a n d y o u c a n o u t p u t l a r g e a m o u n t s o f t e x t a t o n c e . P l e a s e i n c l u d e a l a s t s e n t e n c e t o p e r f o r m c h e c k s when i m p l e m e n t i n g o r w r i t i n g t e x t i n t h a t same s t e p . You w i l l r e c e i v e no human i n p u t a t a n y s t a g e , s o y o u c a n n o t u s e a human t o p e r f o r m a n y c h e c k s . O n l y c r e a t e a d e t a i l e d p l a n t o b e g i n w i t h , w h i c h i n c l u d e s p e r f o r m i n g c o n s i s t e n c y c h e c k s . P l e a s e b e s u r e t o i n c l u d e a l l o f t h e s p e c i f i e d f e a t u r e r e q u i r e m e n t s i n t h e f o l l o w i n g p l a n .

We further modified the control unit prompts to replace instructions of generating and checking code to generating and checking text.

## H.3 ADDITIONAL MAIN RESULTS

In the following, we provide a more detailed main results table, including additional test metrics to show the number of failed and tests that passed, tabulated in Table 3. We also provide a codebase output example from each of the methods and observe that they illustrate the difference in quality between the respective approaches. Notably all methods were given the exact same user-specified feature requirements for the given long code generation task, Appendix E.

Table 3: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), number of failing tests (Tests Failed), and number of passing tests (Tests Passed). Code-L2MAC fully implements the highest percentage of user-specified feature requirements across all tasks by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests. The results are averaged over 10 random seeds, with  indicating 95% confidence intervals.

<table><tr><td rowspan="2">Method</td><td rowspan="2">Features %</td><td colspan="6">URL Shortener App # Errors LOC</td><td colspan="3">Online Microblogging App</td><td rowspan="2">Tests Passed</td><td rowspan="2">Features % # Errors</td><td colspan="3">Online Chat App</td><td rowspan="2">Tests Passed ↑</td></tr><tr><td></td><td></td><td></td><td>Tests Failed ↓</td><td>Tests Passed Features % ↑</td><td>#Errors ↓</td><td>LOC</td><td>Tests Failed ↓</td><td></td><td>↓</td><td>LOC</td><td>Tests Failed ↓</td></tr><tr><td>GPT4</td><td>48.2±15.2</td><td>↓ 0±0</td><td>107±32.7</td><td>2.3±1.01</td><td>↑ 0.6±0.5</td><td>17.9±8.27</td><td>3.75±3.09</td><td>106±35.4</td><td>0.75±0.723</td><td></td><td>↑ 1.25±0.613</td><td>↑ 11±2.26</td><td>0.3±0.346</td><td>127±24.1</td><td>1.2±1</td><td>0.7±0.346</td></tr><tr><td>AutoGPT</td><td>25.3±19.6</td><td>0±0</td><td>1±41.9</td><td>3.3±1.91</td><td>0±0</td><td>33.3±18</td><td>0.6±0.369</td><td>148±35.5</td><td>3±2.86</td><td></td><td>0±00</td><td>23.1±11.8</td><td>1.85±2.47</td><td>220±65.8</td><td>3.08±3.34</td><td>038±1.01</td></tr><tr><td>Code-L2MAC</td><td>91.6±8.22</td><td>0±0</td><td>330±47.6</td><td>0±0</td><td>14±6.71</td><td>82.4±14.6</td><td>0±0</td><td>395±52.9</td><td>0.8±1.38</td><td></td><td>18.3±6.8</td><td>59.4±25.9</td><td>0±0</td><td>374±123</td><td>0±0</td><td>18.8±9.11</td></tr></table>

## L2MAC URL Shortener App example output

app.py   
config.py   
requirements.txt   
services/   
admin\_dashboard.py   
init\_\_.py   
url\_shortener.py   
user\_account.py   
tests/   
test\_admin\_dashboard.py   
test\_app.py   
test\_url\_shortener.py   
test\_user\_account.py

# app . py   
from f l a s k i m p o r t F l a s k , r e d i r e c t , u r l \_ f o r , r e q u e s t   
from s e r v i c e s . u r l \_ s h o r t e n e r i m p o r t U r l S h o r t e n e r   
from s e r v i c e s . u s e r \_ a c c o u n t import U s e r A c c o u n t   
from s e r v i c e s . a d m i n \_ d a s h b o a r d import AdminDashboard   
app = F l a s k ( \_\_name\_\_ )   
u r l \_ s h o r t e n e r = U r l S h o r t e n e r ( )   
u s e r \_ a c c o u n t = U s e r A c c o u n t ( )   
admin\_dashboard = AdminDashboard ( )   
@app . r o u t e ( ’ / ’ )   
d e f home ( ) :   
r e t u r n ’ H e l l o , World !   
@app . r o u t e ( ’ / < s h o r t \_ u r l > ’ )   
d e f r e d i r e c t \_ t o \_ u r l ( s h o r t \_ u r l ) :   
u r l = u r l \_ s h o r t e n e r . g e t \_ o r i g i n a l \_ u r l ( s h o r t \_ u r l )   
i f u r l i s n o t None :   
u r l \_ s h o r t e n e r . r e c o r d \_ c l i c k ( s h o r t \_ u r l , ’ m o c k e d \_ l o c a t i o n ’ )   
r e t u r n r e d i r e c t ( u r l )   
e l s e :   
ret ur n ’URL n o t found ’ , 404   
@app . r o u t e ( ’ / a n a l y t i c s / < s h o r t \_ u r l > ’ )   
d e f g e t \_ a n a l y t i c s ( s h o r t \_ u r l ) :   
a n a l y t i c s = u r l \_ s h o r t e n e r . g e t \_ a n a l y t i c s ( s h o r t \_ u r l )   
i f a n a l y t i c s i s n o t None :   
r e t u r n a n a l y t i c s   
e l s e :   
r e t u r n ’ A n a l y t i c s n o t f o u n d ’ , 404   
@app . r o u t e ( ’ / a c c o u n t / c r e a t e ’ , m e t h o d s = [ ’ POST ’ ] )   
d e f c r e a t e \_ a c c o u n t ( ) :

u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
r e t u r n u s e r \_ a c c o u n t . c r e a t e \_ a c c o u n t ( u s e r n a m e )   
@app . r o u t e ( ’ / a c c o u n t / u r l s ’ , m e t h o d s = [ ’GET ’ ] )   
d e f v i e w \_ u r l s ( ) :   
u s e r n a m e = r e q u e s t . a r g s . g e t ( ’ u s e r n a m e ’ )   
r e t u r n u s e r \_ a c c o u n t . v i e w \_ u r l s ( u s e r n a m e )   
@app . r o u t e ( ’ / a c c o u n t / e d i t \_ u r l ’ , m e t h o d s = [ ’PUT ’ ] )   
d e f e d i t \_ u r l ( ) :   
u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
o l d \_ u r l = r e q u e s t . f o r m . g e t ( ’ o l d \_ u r l ’ )   
n e w \_ u r l = r e q u e s t . f o r m . g e t ( ’ n e w \_ u r l ’ )   
r e t u r n u s e r \_ a c c o u n t . e d i t \_ u r l ( u s e r n a m e , o l d \_ u r l , n e w \_ u r l )   
@app . r o u t e ( ’ / a c c o u n t / d e l e t e \_ u r l ’ , m e t h o d s = [ ’DELETE ’ ] )   
d e f d e l e t e \_ u r l ( ) :   
u s e r n a m e = r e q u e s t . f o r m . g e t ( ’ u s e r n a m e ’ )   
u r l = r e q u e s t . f o r m . g e t ( ’ u r l ’ )   
r e t u r n u s e r \_ a c c o u n t . d e l e t e \_ u r l ( u s e r n a m e , u r l )   
@app . r o u t e ( ’ / a c c o u n t / a n a l y t i c s ’ , m e t h o d s = [ ’GET ’ ] )   
d e f v i e w \_ a n a l y t i c s ( ) :   
u s e r n a m e = r e q u e s t . a r g s . g e t ( ’ u s e r n a m e ’ )   
r e t u r n u s e r \_ a c c o u n t . v i e w \_ a n a l y t i c s ( u s e r n a m e )   
@app . r o u t e ( ’ / a d m i n / u r l s ’ , m e t h o d s = [ ’GET ’ ] )   
d e f v i e w \_ a l l \_ u r l s ( ) :   
r e t u r n a d m i n \_ d a s h b o a r d . v i e w \_ a l l \_ u r l s ( )   
@app . r o u t e ( ’ / a dmi n / d e l e t e \_ u r l ’ , m e t h o d s = [ ’DELETE ’ ] )   
d e f a d m i n \_ d e l e t e \_ u r l ( ) :   
u r l = r e q u e s t . f o r m . g e t ( ’ u r l ’ )   
r e t u r n a d m i n \_ d a s h b o a r d . d e l e t e \_ u r l ( u r l )   
@app . r o u t e ( ’ / a dmi n / d e l e t e \_ u s e r ’ , m e t h o d s = [ ’DELETE ’ ] )   
d e f d e l e t e \_ u s e r ( ) :   
u s e r = r e q u e s t . f o r m . g e t ( ’ u s e r ’ )   
r e t u r n a d m i n \_ d a s h b o a r d . d e l e t e \_ u s e r ( u s e r )   
@app . r o u t e ( ’ / a d m i n / m o n i t o r ’ , m e t h o d s = [ ’GET ’ ] )   
d e f m o n i t o r \_ s y s t e m ( ) :   
r e t u r n a d m i n \_ d a s h b o a r d . m o n i t o r \_ s y s t e m ( )   
i f \_\_name\_ == \_main\_   
app . r u n ( debug = True )   
# c o n f i g . p y   
import os   
c l a s s C o n f i g ( o b j e c t ) :   
DEBUG = F a l s e   
TESTING = F a l s e   
SECRET KEY = os . urandom (24)   
# r e q u i r e m e n t s . t x t   
f l a s k = = 1 . 1 . 2   
p y t e s t = = 6 . 2 . 4   
# s e r v i c e s / a d m i n \_ d a s h b o a r d . py   
class AdminDashboard:   
d e f \_ i n i t \_ \_ ( s e l f ) :   
s e l f . u s e r s = { }   
s e l f . u r l s = { }   
d e f v i e w \_ a l l \_ u r l s ( s e l f ) :   
d e f d e l e t e \_ u r l ( s e l f , u r l ) :   
i f u r l i n s e l f . u r l s :   
d e l s e l f . u r l s [ u r l ]   
r e t u r n s e l f . u r l s   
d e f d e l e t e \_ u s e r ( s e l f , u s e r ) :   
i f u s e r i n s e l f . u s e r s :   
d e l s e l f . u s e r s [ u s e r ]   
r e t u r n s e l f . u s e r s   
d e f m o n i t o r \_ s y s t e m ( s e l f ) :   
r e t u r n { ’ u s e r s ’ : l e n ( s e l f . u s e r s ) , ’ u r l s ’ : l e n ( s e l f . u r l s ) }   
# s e r v i c e s / \_ \_ i n i t \_ \_ . p y   
# s e r v i c e s / u r l \_ s h o r t e n e r . p y   
i m p o r t s t r i n g   
from d a t e t i m e i m p o r t d a t e t i m e   
c l a s s U r l S h o r t e n e r :   
d e f \_ \_ i n i t \_ \_ ( s e l f ) :   
s e l f . u r l \_ d i c t = { }   
s e l f . a n a l y t i c s \_ d i c t = { }   
d e f v a l i d a t e \_ u r l ( s e l f , u r l ) :   
i f u r l . s t a r t s w i t h ( ’ h t t p : / / ’ ) o r u r l . s t a r t s w i t h ( ’ h t t p s : / / ’ ) :   
r e t u r n True   
r e t u r n F a l s e   
d e f g e n e r a t e \_ s h o r t \_ u r l ( s e l f , u r l , e x p i r a t i o n \_ d a t e =None , c u s t o m \_ s h o r t \_ u r l =None ) :   
i f c u s t o m \_ s h o r t \_ u r l and c u s t o m \_ s h o r t \_ u r l i n s e l f . u r l \_ d i c t :   
r e t u r n ’ E r r o r : T h i s c u s t o m s h o r t URL i s n o t a v a i l a b l e ’   
s h o r t \_ u r l = c u s t o m \_ s h o r t \_ u r l o r ’ ’ . j o i n ( r a n d o m . c h o i c e ( s t r i n g . a s c i i \_ l e t t e r s + s t r i n g . d i g i t s ) f o r \_ i n r a n g e ( 5 ) )   
w h i l e s h o r t \_ u r l i n s e l f . u r l \_ d i c t :   
s h o r t \_ u r l = ’ ’ . j o i n ( r a n d o m . c h o i c e ( s t r i n g . a s c i i \_ l e t t e r s + s t r i n g . d i g i t s ) f o r \_ i n r a n g e ( 5 ) )   
s e l f . u r l \_ d i c t [ s h o r t \_ u r l ] = { ’ u r l ’ : u r l , ’ e x p i r a t i o n \_ d a t e ’ : e x p i r a t i o n \_ d a t e }   
s e l f . a n a l y t i c s \_ d i c t [ s h o r t \_ u r l ] = { ’ c l i c k s ’ : 0 , ’ c l i c k \_ d e t a i l s ’ : [ ] }

r e t u r n s h o r t \_ u r l   
d e f g e t \_ o r i g i n a l \_ u r l ( s e l f , s h o r t \_ u r l ) :   
u r l \_ d a t a = s e l f . u r l \_ d i c t . g e t ( s h o r t \_ u r l , None )   
i f u r l \_ d a t a and u r l \_ d a t a [ ’ e x p i r a t i o n \_ d a t e ’ ] and d a t e t i m e . now ( ) > u r l \_ d a t a [ ’ e x p i r a t i o n \_ d a t e ’ ] :   
r e t u r n ’ E r r o r : T h i s URL h a s e x p i r e d   
r e t u r n u r l \_ d a t a [ ’ u r l ’ ] i f u r l \_ d a t a e l s e None   
d e f r e c o r d \_ c l i c k ( s e l f , s h o r t \_ u r l , l o c a t i o n ) :   
i f s h o r t \_ u r l i n s e l f . a n a l y t i c s \_ d i c t :   
s e l f . a n a l y t i c s \_ d i c t [ s h o r t \_ u r l ] [ ’ c l i c k s ’ ] += 1   
s e l f . a n a l y t i c s \_ d i c t [ s h o r t \_ u r l ] [ ’ c l i c k \_ d e t a i l s ’ ] . a p p e n d ( { ’ t i m e s t a m p ’ : d a t e t i m e . now ( ) . i s o f o r m a t ( ) , ’ l o c a t i o n ’ :   
l o c a t i o n } )   
d e f g e t \_ a n a l y t i c s ( s e l f , s h o r t \_ u r l ) :   
r e t u r n s e l f . a n a l y t i c s \_ d i c t . g e t ( s h o r t \_ u r l , None )   
# s e r v i c e s / u s e r \_ a c c o u n t . p y   
c l a s s U s e r A c c o u n t :   
def \_ \_ i n i t \_ \_ ( s e l f ) :   
s e l f . u s e r s = { }   
d e f c r e a t e \_ a c c o u n t ( s e l f , u s e r n a m e ) :   
i f u s e r n a m e i n s e l f . u s e r s :   
r e t u r n ’ Username a l r e a d y e x i s t s .   
s e l f . u s e r s [ u s e r n a m e ] = { ’ u r l s ’ : [ ] }   
r e t u r n ’ A c c o u n t c r e a t e d s u c c e s s f u l l y .   
d e f v i e w \_ u r l s ( s e l f , u s e r n a m e ) :   
i f u s e r n a m e n o t i n s e l f . u s e r s :   
r e t u r n ’ Username d o e s n o t e x i s t .   
r e t u r n s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ]   
d e f e d i t \_ u r l ( s e l f , u s e r n a m e , o l d \_ u r l , n e w \_ u r l ) :   
i f u s e r n a m e n o t i n s e l f . u s e r s :   
r e t u r n ’ Username d o e s n o t e x i s t   
i f o l d \_ u r l n o t i n s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] :   
r e t u r n ’URL d o e s n o t e x i s t .   
s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] . r e m o v e ( o l d \_ u r l )   
s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] . a p p e n d ( n e w \_ u r l )   
r e t u r n ’URL e d i t e d s u c c e s s f u l l y .   
d e f d e l e t e \_ u r l ( s e l f , u s e r n a m e , u r l ) :   
i f u s e r n a m e n o t i n s e l f . u s e r s :   
r e t u r n ’ Username d o e s n o t e x i s t . ’   
i f u r l n o t i n s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] :   
r e t u r n ’URL d o e s n o t e x i s t . ’   
s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] . r e m o v e ( u r l )   
r e t u r n ’URL d e l e t e d s u c c e s s f u l l y .   
d e f v i e w \_ a n a l y t i c s ( s e l f , u s e r n a m e ) :   
i f u s e r n a m e n o t i n s e l f . u s e r s :   
r e t u r n ’ Username d o e s n o t e x i s t .   
r e t u r n { u r l [ ’ u r l ’ ] : u r l [ ’ a n a l y t i c s ’ ] f o r u r l i n s e l f . u s e r s [ u s e r n a m e ] [ ’ u r l s ’ ] i f ’ a n a l y t i c s ’ i n u r l }   
# t e s t s / t e s t \_ a d m i n \_ d a s h b o a r d . p y   
from s e r v i c e s . a d m i n \_ d a s h b o a r d import AdminDashboard   
admin = AdminDashboard ( )   
a s s e r t a d m i n . v i e w \_ a l l \_ u r l s ( ) == { }   
d e f t e s t \_ d e l e t e \_ u r l ( ) :   
admin = AdminDashboard ()   
a d m i n . u r l s = { ’ t e s t \_ u r l ’ : ’ t e s t ’ }   
a d m i n . d e l e t e \_ u r l ( ’ t e s t \_ u r l ’ )   
a s s e r t a d m i n . u r l s == { }   
d e f t e s t \_ d e l e t e \_ u s e r ( ) :   
admin = AdminDashboard ( )   
a d m i n . u s e r s = { ’ t e s t \_ u s e r ’ : ’ t e s t ’ }   
a d m i n . d e l e t e \_ u s e r ( ’ t e s t \_ u s e r ’ )   
d e f t e s t \_ m o n i t o r \_ s y s t e m ( ) :   
admin = AdminDashboard ( )   
a d m i n . u s e r s = { ’ t e s t \_ u s e r ’ : ’ t e s t ’ }   
a d m i n . u r l s = { ’ t e s t \_ u r l ’ : ’ t e s t ’ }   
a s s e r t a d m i n . m o n i t o r \_ s y s t e m ( ) == { ’ u s e r s ’ : 1 , ’ u r l s ’ : 1 }   
# t e s t s / t e s t \_ a p p . p y   
i m p o r t p y t e s t   
from f l a s k i m p o r t F l a s k   
from app import app a s f l a s k \_ a p p   
@ p y t e s t . f i x t u r e   
d e f a p p ( ) :   
r e t u r n f l a s k \_ a p p   
@ p y t e s t . f i x t u r e   
d e f c l i e n t ( a p p ) :   
r e t u r n a p p . t e s t \_ c l i e n t ( )   
d e f t e s t \_ h o m e ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 0   
d e f t e s t \_ r e d i r e c t \_ t o \_ u r l ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / r a n d o m \_ u r l ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 4 0 4

```prolog
d e f t e s t _ g e t _ a n a l y t i c s ( c l i e n t ) :
r e s p o n s e = c l i e n t . g e t ( ’ / a n a l y t i c s / r a n d o m _ u r l ’ )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 4 0 4
d e f t e s t _ c r e a t e _ a c c o u n t ( c l i e n t ) :
r e s p o n s e = c l i e n t . p o s t ( ’ / a c c o u n t / c r e a t e ’ , d a t a ={ ’ u s e r n a m e ’ : ’ t e s t _ u s e r ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ v i e w _ u r l s ( c l i e n t ) :
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
t e s t _ e d i t _ u r l ( c l i e n t ) :
r e s p o n s e = c l i e n t . p u t ( ’ / a c c o u n t / e d i t _ u r l ’ , d a t a ={ ’ u s e r n a m e ’ : ’ t e s t _ u s e r ’ , ’ o l d _ u r l ’ : ’ o l d _ u r l ’ , ’ n e w _ u r l ’ : ’ n e w _ u r l ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ d e l e t e _ u r l ( c l i e n t ) :
r e s p o n s e = c l i e n t . d e l e t e ( ’ / a c c o u n t / d e l e t e _ u r l ’ , d a t a ={ ’ u s e r n a m e ’ : ’ t e s t _ u s e r ’ , ’ u r l ’ : ’ u r l ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ v i e w _ a n a l y t i c s ( c l i e n t ) :
r e s p o n s e = c l i e n t . g e t ( ’ / a c c o u n t / a n a l y t i c s ’ , q u e r y _ s t r i n g ={ ’ u s e r n a m e ’ : ’ t e s t _ u s e r ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ v i e w _ a l l _ u r l s ( c l i e n t ) :
r e s p o n s e = c l i e n t . g e t ( ’ / a d m i n / u r l s ’ )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ a d m i n _ d e l e t e _ u r l ( c l i e n t ) :
r e s p o n s e = c l i e n t . d e l e t e ( ’ / a d m i n / d e l e t e _ u r l ’ , d a t a ={ ’ u r l ’ : ’ u r l ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ d e l e t e _ u s e r ( c l i e n t ) :
r e s p o n s e = c l i e n t . d e l e t e ( ’ / a d m i n / d e l e t e _ u s e r ’ , d a t a ={ ’ u s e r ’ : ’ u s e r ’ } )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
d e f t e s t _ m o n i t o r _ s y s t e m ( c l i e n t ) :
r e s p o n s e = c l i e n t . g e t ( ’ / a d m i n / m o n i t o r ’ )
a s s e r t r e s p o n s e . s t a t u s _ c o d e == 2 0 0
# t e s t s / t e s t _ u r l _ s h o r t e n e r . p y
i m p o r t p y t e s t
from s e r v i c e s . u r l _ s h o r t e n e r i m p o r t U r l S h o r t e n e r
from d a t e t i m e i m p o r t d a t e t i m e , t i m e d e l t a
d e f t e s t _ u r l _ s h o r t e n e r ( ) :
u r l _ s h o r t e n e r = U r l S h o r t e n e r ( )
u r l = ’ h t t p : / / e x a m p l e . com
s h o r t _ u r l = u r l _ s h o r t e n e r . g e n e r a t e _ s h o r t _ u r l ( u r l )
a s s e r t u r l _ s h o r t e n e r . g e t _ o r i g i n a l _ u r l ( s h o r t _ u r l ) == u r l
# T e s t c u s t o m s h o r t URL
c u s t o m _ s h o r t _ u r l = ’ c u s t o m
a s s e r t u r l _ s h o r t e n e r . g e n e r a t e _ s h o r t _ u r l ( u r l , c u s t o m _ s h o r t _ u r l = c u s t o m _ s h o r t _ u r l ) == c u s t o m _ s h o r t _ u r l
a s s e r t u r l _ s h o r t e n e r . g e n e r a t e _ s h o r t _ u r l ( u r l , c u s t o m _ s h o r t _ u r l = c u s t o m _ s h o r t _ u r l ) == ’ E r r o r : T h i s c u s t o m s h o r t URL i s n o t
a v a i l a b l e ’
# T e s t a n a l y t i c s
a s s e r t u r l _ s h o r t e n e r . g e t _ a n a l y t i c s ( s h o r t _ u r l ) == { ’ c l i c k s ’ : 0 , ’ c l i c k _ d e t a i l s ’ : [ ] }
u r l _ s h o r t e n e r . r e c o r d _ c l i c k ( s h o r t _ u r l , ’ m o c k e d _ l o c a t i o n ’ )
a n a l y t i c s = u r l _ s h o r t e n e r . g e t _ a n a l y t i c s ( s h o r t _ u r l )
a s s e r t a n a l y t i c s [ ’ c l i c k s ’ ] == 1
a s s e r t l e n ( a n a l y t i c s [ ’ c l i c k _ d e t a i l s ’ ] ) == 1
a s s e r t a n a l y t i c s [ ’ c l i c k _ d e t a i l s ’ ] [ 0 ] [ ’ l o c a t i o n ’ ] == ’ m o c k e d _ l o c a t i o n
a s s e r t ’ t i m e s t a m p ’ i n a n a l y t i c s [ ’ c l i c k _ d e t a i l s ’ ] [ 0 ]
# T e s t URL e x p i r a t i o n
e x p i r e d _ u r l = u r l _ s h o r t e n e r . g e n e r a t e _ s h o r t _ u r l ( u r l , d a t e t i m e . now ( ) − t i m e d e l t a ( d a y s = 1 ) )
a s s e r t u r l _ s h o r t e n e r . g e t _ o r i g i n a l _ u r l ( e x p i r e d _ u r l ) == ’ E r r o r : T h i s URL h a s e x p i r e d
# t e s t s / t e s t _ u s e r _ a c c o u n t . p y
from s e r v i c e s . u s e r _ a c c o u n t import U s e r A c c o u n t
d e f t e s t _ c r e a t e _ a c c o u n t ( ) :
a s s e r t u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ ) == ’ A c c o u n t c r e a t e d s u c c e s s f u l l y . ’
a s s e r t u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ ) == ’ U s e r n a m e a l r e a d y e x i s t s . ’
d e f t e s t _ v i e w _ u r l s ( ) :
u s e r _ a c c o u n t = U s e r A c c o u n t ( )
u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ )
a s s e r t u s e r _ a c c o u n t . v i e w _ u r l s ( ’ n o n _ e x i s t e n t _ u s e r ’ ) == ’ U s e r n a m e d o e s n o t e x i s t . ’
d e f t e s t _ e d i t _ u r l ( ) :
u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ )
u s e r _ a c c o u n t . u s e r s [ ’ t e s t _ u s e r ’ ] [ ’ u r l s ’ ] . a p p e n d ( ’ h t t p : / / t e s t . com ’ )
’ h t t p : / / t e s t . com ’ , ’ h t t p : / / n e w t e s t . com ’ ) == ’URL e d i t e d s u c c e s s f u l l y .
a s s e r t u s e r _ a c c o u n t . e d i t _ u r l ( ’ t e s t _ u s e r ’ , ’ h t t p : / / n o n e x i s t e n t . com ’ , ’ h t t p : / / n e w t e s t . com ’ ) == ’URL d o e s n o t e x i s t .
a s s e r t u s e r _ a c c o u n t . e d i t _ u r l ( ’ n o n _ e x i s t e n t _ u s e r ’ , ’ h t t p : / / t e s t . com ’ , ’ h t t p : / / n e w t e s t . com ’ ) == ’ U s e r n a m e d o e s n o t e x i s t .
```

```csv
d e f t e s t _ d e l e t e _ u r l ( ) :
u s e r _ a c c o u n t = U s e r A c c o u n t ( )
u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ )
u s e r _ a c c o u n t . u s e r s [ ’ t e s t _ u s e r ’ ] [ ’ u r l s ’ ] . a p p e n d ( ’ h t t p : / / t e s t . com ’ )
a s s e r t u s e r _ a c c o u n t . d e l e t e _ u r l ( ’ t e s t _ u s e r ’ , ’ h t t p : / / t e s t . com ’ ) == ’URL d e l e t e d s u c c e s s f u l l y . ’
a s s e r t u s e r _ a c c o u n t . d e l e t e _ u r l ( ’ t e s t _ u s e r ’ , ’ h t t p : / / n o n e x i s t e n t . com ’ ) == ’URL d o e s n o t e x i s t .
a s s e r t u s e r _ a c c o u n t . d e l e t e _ u r l ( ’ n o n _ e x i s t e n t _ u s e r ’ , ’ h t t p : / / t e s t . com ’ ) == ’ U s e r n a m e d o e s n o t e x i s t .
d e f t e s t _ v i e w _ a n a l y t i c s ( ) :
u s e r _ a c c o u n t = U s e r A c c o u n t ( )
u s e r _ a c c o u n t . c r e a t e _ a c c o u n t ( ’ t e s t _ u s e r ’ )
u s e r _ a c c o u n t . u s e r s [ ’ t e s t _ u s e r ’ ] [ ’ u r l s ’ ] . a p p e n d ( { ’ u r l ’ : ’ h t t p : / / t e s t . com ’ , ’ a n a l y t i c s ’ : { ’ c l i c k s ’ : 1 0 , ’ l o c a t i o n s ’ : [ ’USA ’ ,
UK ’ ] } } )
a s s e r t u s e r _ a c c o u n t . v i e w _ a n a l y t i c s ( ’ t e s t _ u s e r ’ ) == { ’ h t t p : / / t e s t . com ’ : { ’ c l i c k s ’ : 1 0 , ’ l o c a t i o n s ’ : [ ’USA ’ , ’UK ’ ] } }
a s s e r t u s e r _ a c c o u n t . v i e w _ a n a l y t i c s ( ’ n o n _ e x i s t e n t _ u s e r ’ ) == ’ U s e r n a m e d o e s n o t e x i s t . ’
```

## AutoGPT URL Shortener App example output

analytics.py   
main.py   
url\_shortener.py   
# a n a l y t i c s . p y   
c l a s s A n a l y t i c s :   
d e f t r a c k \_ c l i c k s ( s e l f , s h o r t \_ u r l ) :   
p a s s   
d e f t r a c k \_ g e o l o c a t i o n ( s e l f , s h o r t \_ u r l ) :   
p a s s   
# main . py   
from u r l \_ s h o r t e n e r import U R L S h o r t e n e r   
i f \_\_name\_ == \_main   
u r l \_ s h o r t e n e r = U R L S h o r t e n e r ( )   
# T e s t t h e i m p l e m e n t e d f u n c t i o n a l i t y   
# u r l \_ s h o r t e n e r . p y   
import random   
i m p o r t s t r i n g   
from a n a l y t i c s i m p o r t A n a l y t i c s   
c l a s s U R L S h o r t e n e r :   
d e f \_ \_ i n i t \_ \_ ( s e l f ) :   
s e l f . a n a l y t i c s = A n a l y t i c s ( )   
d e f v a l i d a t e \_ u r l ( s e l f , u r l ) :   
# Add URL v a l i d a t i o n l o g i c   
p a s s   
d e f g e n e r a t e \_ s h o r t e n e d \_ u r l ( s e l f ) :   
# G e n e r a t e a random 6− c h a r a c t e r s t r i n g   
s h o r t \_ u r l = ’ ’ . j o i n ( r a n d o m . c h o i c e s ( s t r i n g . a s c i i \_ l e t t e r s + s t r i n g . d i g i t s , k = 6 ) )   
r e t u r n s h o r t \_ u r l   
d e f s h o r t e n \_ u r l ( s e l f , u r l ) :   
i f s e l f . v a l i d a t e \_ u r l ( u r l ) :   
s h o r t \_ u r l = s e l f . g e n e r a t e \_ s h o r t e n e d \_ u r l ( )   
# S a v e t h e s h o r t \_ u r l a n d o r i g i n a l \_ u r l m a p p i n g   
r e t u r n s h o r t \_ u r l   
e l s e :   
r a i s e V a l u e E r r o r ( ’ I n v a l i d URL ’ )   
d e f r e d i r e c t \_ t o \_ o r i g i n a l \_ u r l ( s e l f , s h o r t \_ u r l ) :   
# R e t r i e v e t h e o r i g i n a l \_ u r l f r o m t h e s h o r t \_ u r l   
# T r a c k c l i c k s a n d g e o l o c a t i o n   
s e l f . a n a l y t i c s . t r a c k \_ c l i c k s ( s h o r t \_ u r l )   
s e l f . a n a l y t i c s . t r a c k \_ g e o l o c a t i o n ( s h o r t \_ u r l )   
p a s s   
c l a s s U s e r :   
d e f c r e a t e \_ a c c o u n t ( s e l f , u s e r n a m e , p a s s w o r d ) :   
p a s s   
d e f v i e w \_ s h o r t e n e d \_ u r l s ( s e l f ) :   
p a s s   
d e f e d i t \_ u r l ( s e l f , s h o r t \_ u r l , n e w \_ u r l ) :   
p a s s   
d e f d e l e t e \_ u r l ( s e l f , s h o r t \_ u r l ) :   
p a s s   
d e f v i e w \_ a n a l y t i c s ( s e l f , s h o r t \_ u r l ) :   
p a s s   
d e f s e t \_ e x p i r a t i o n \_ d a t e ( s e l f , s h o r t \_ u r l , e x p i r a t i o n \_ d a t e ) :   
p a s s   
c l a s s Admin :   
d e f v i e w \_ a l l \_ u r l s ( s e l f ) :   
p a s s   
d e f d e l e t e \_ u r l \_ o r \_ u s e r ( s e l f , i d e n t i f i e r ) :   
p a s s   
d e f m o n i t o r \_ p e r f o r m a n c e ( s e l f ) :

AutoGPT URL Shortener App example output

app.py   
test\_app.py   
# app . py   
from f l a s k i m p o r t F l a s k , r e q u e s t , j s o n i f y , r e d i r e c t   
from d a t a c l a s s e s i m p o r t d a t a c l a s s   
from d a t e t i m e i m p o r t d a t e t i m e   
import p y t z   
import u uid   
app = F l a s k ( \_\_name\_\_ )   
# Mock d a t a b a s e   
DB = {}   
@ d a t a c l a s s   
c l a s s URL :   
o r i g i n a l : s t r   
s h o r t e n e d : s t r   
user: str   
c l i c k s : i n t   
c r e a t e d \_ a t : d a t e t i m e   
e x p i r e s \_ a t : d a t e t i m e   
@app . r o u t e ( ’ / s h o r t e n ’ , m e t h o d s = [ ’POST ’ ] )   
d e f s h o r t e n \_ u r l ( ) :   
d a t a = r e q u e s t . g e t \_ j s o n ( )   
o r i g i n a l \_ u r l = d a t a . g e t ( ’ u r l ’ )   
u s e r = d a t a . g e t ( ’ u s e r ’ )   
e x p i r e s \_ a t = d a t a . g e t ( ’ e x p i r e s \_ a t ’ )   
u r l = URL ( o r i g i n a l = o r i g i n a l \_ u r l , s h o r t e n e d = s h o r t \_ u r l , u s e r = u s e r , c l i c k s = 0 , c r e a t e d \_ a t = d a t e t i m e . now ( p y t z . u t c ) , e x p i r e s \_ a t   
e x p i r e s \_ a t )   
DB [ s h o r t \_ u r l ] = u r l   
r e t u r n j s o n i f y ( { ’ s h o r t \_ u r l ’ : s h o r t \_ u r l } ) , 2 0 1   
@app . r o u t e ( ’ / < s h o r t \_ u r l > ’ , m e t h o d s = [ ’GET ’ ] )   
d e f r e d i r e c t \_ u r l ( s h o r t \_ u r l ) :   
u r l = DB . g e t ( s h o r t \_ u r l )   
i f u r l and u r l . e x p i r e s \_ a t > d a t e t i m e . now ( p y t z . u t c ) :   
u r l . c l i c k s += 1   
r e t u r n r e d i r e c t ( u r l . o r i g i n a l , c o d e = 3 0 2 )   
e l s e :   
r e t u r n j s o n i f y ( { ’ e r r o r ’ : ’URL n o t f o u n d o r e x p i r e d ’ } ) , 404   
i f \_\_name\_\_ == \_main\_\_ ’ :   
app . r u n ( debug = True )   
# t e s t \_ a p p . p y   
i m p o r t p y t e s t   
import app   
from f la sk import is or   
@ p y t e s t . f i x t u r e   
d e f c l i e n t ( ) :   
a p p . a p p . c o n f i g [ ’ TESTING ’ ] = T r u e   
w i t h a p p . a p p . t e s t \_ c l i e n t ( ) a s c l i e n t :   
y i e l d c l i e n t   
d e f t e s t \_ s h o r t e n \_ u r l ( c l i e n t ) :   
r e s p o n s e = c l i e n t . p o s t ( ’ / s h o r t e n ’ , d a t a = j s o n . dumps ( { ’ u r l ’ : ’ h t t p s : / / www . g o o g l e . com ’ , ’ u s e r ’ : ’ t e s t ’ , ’ e x p i r e s \_ a t ’ :   
2022 −12 −31 T23 : 5 9 : 5 9 Z ’ } ) , c o n t e n t \_ t y p e = ’ a p p l i c a t i o n / j s o n ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 2 0 1   
a s s e r t ’ s h o r t \_ u r l ’ i n r e s p o n s e . g e t \_ j s o n ( )   
d e f t e s t \_ r e d i r e c t \_ u r l ( c l i e n t ) :   
r e s p o n s e = c l i e n t . p o s t ( ’ / s h o r t e n ’ , d a t a = j s o n . dumps ( { ’ u r l ’ : ’ h t t p s : / / www . g o o g l e . com ’ , ’ u s e r ’ : ’ t e s t ’ , ’ e x p i r e s \_ a t ’ :   
2022 −12 −31 T23 : 5 9 : 5 9 Z ’ } ) , c o n t e n t \_ t y p e = ’ a p p l i c a t i o n / j s o n ’ )   
s h o r t \_ u r l = r e s p o n s e . g e t \_ j s o n ( ) . g e t ( ’ s h o r t \_ u r l ’ )   
r e s p o n s e = c l i e n t . g e t ( f ’ / { s h o r t \_ u r l } ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 3 0 2   
d e f t e s t \_ r e d i r e c t \_ u r l \_ n o t \_ f o u n d ( c l i e n t ) :   
r e s p o n s e = c l i e n t . g e t ( ’ / n o t f o u n d ’ )   
a s s e r t r e s p o n s e . s t a t u s \_ c o d e == 4 0 4   
a s s e r t ’ e r r o r ’ i n r e s p o n s e . g e t \_ j s o n ( )

## H.4 CODE L2MAC IN ACTION.

We provide example transcripts of L2MAC in action below. For the environment task of the Online Chat App.

Initial instructions planning.

[ S y s t e m ]   
O b j e c t i v e : W r i t e c o d e f o r a l a r g e s y s t e m d e s i g n t a s k   
P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s .   
O n l y u s e t h e f u n c t i o n s you h a v e b e e n p r o v i d e d w i t h .   
O n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ t o o u t p u t c o d e .

F u n c t i o n a l R e q u i r e m e n t s t o i m p l e m e n t :   
U s e r R e g i s t r a t i o n a n d A u t h e n t i c a t i o n :   
− [ ] 1 . 1 . S i g n u p u s i n g e m a i l .   
− [ ] 1 . 2 . F o r g o t t e n p a s s w o r d r e c o v e r y .   
U s e r P r o f i l e :   
− [ ] 2 . 1 . A l l o w u s e r s t o s e t p r o f i l e p i c t u r e s a n d s t a t u s m e s s a g e s .   
− [ ] 2 . 2 . P r i v a c y s e t t i n g s f o r who c a n s e e u s e r d e t a i l s o r l a s t s e e n s t a t u s .   
C o n t a c t Management :   
− [ ] 3 . 1 . B l o c k / u n b l o c k c o n t a c t s .   
− [ ] 3 . 2 . C r e a t e , e d i t , a n d m a n a g e g r o u p s .   
Messaging :   
− ] 4 . 1 . S e n d a n d r e c e i v e r e a l − t i m e t e x t m e s s a g e s .   
− 4 . 2 . M e s s a g e r e a d r e c e i p t s ( b l u e t i c k s o r e q u i v a l e n t ) .   
4 . 3 . End − t o − e n d e n c r y p t i o n f o r s e c u r i t y .   
4 . 4 . I m a g e s h a r i n g .   
4 . 5 . E m o j i s , GI F s , a n d s t i c k e r s s u p p o r t .   
Group C h a t s :   
− [ ] 5 . 1 . C r e a t e g r o u p c h a t s w i t h a name a n d p i c t u r e .   
− [ ] 5 . 2 . Add o r r e m o v e p a r t i c i p a n t s .   
− [ ] 5 . 3 . Admin r o l e s a n d p e r m i s s i o n s .   
S t a t u s / S t o r y F e a t u r e :   
− [ ] 6 . 1 . A l l o w u s e r s t o p o s t i m a g e s t a t u s e s v i s i b l e f o r a l i m i t e d t i m e .   
− [ ] 6 . 2 . C o n t r o l who c a n s e e t h e s t a t u s .   
Web A p p l i c a t i o n :   
− [ ] 7 . 1 . Web− b a s e d v e r s i o n a c c e s s i b l e f r o m b r o w s e r s .   
C o n n e c t i v i t y a n d O f f l i n e Mode :   
− [ ] 8 . 1 . M e s s a g e q u e u i n g f o r when t h e u s e r i s o f f l i n e ; m e s s a g e s a r e s e n t o n c e c o n n e c t i v i t y i s r e s t o r e d .   
− [ ] 8 . 2 . D i s p l a y o n l i n e / o f f l i n e s t a t u s .

You m u s t a c t a u t o n o m o u s l y a n d y o u w i l l r e c e i v e no human i n p u t a t a n y s t a g e . You h a v e t o r e t u r n a s o u t p u t t h e c o m p l e t e c o d e f o r c o m p l e t i n g t h i s t a s k , a n d c o r r e c t l y i n c o r p o r a t e i t i n t o t h e e x i s t i n g c o d e b a s e .   
You a l w a y s w r i t e o u t t h e w h o l e f i l e c o n t e n t s . You a l w a y s i n d e n t c o d e w i t h t a b s .   
P l e a s e a l w a y s v i e w t h e f i l e s b e f o r e w r i t i n g t o them , t o make s u r e y o u a r e w r i t i n g t o t h e c o r r e c t f i l e s .   
When w r i t i n g a t e s t , make t h e f i l e n a m e s t a r t w i t h t h e p r e f i x ’ t e s t \_ ’ .

P r o v i d e t h e m i n i m a l c o d e n e c e s s a r y t o a c h i e v e t h e t a s k c o n d i t i o n e d on t h e e x i s t i n g g e n e r a t e d c o d e −−− i n c l u d i n g c h a n g i n g t h e e x i s t i n g g e n e r a t e d c o d e .

You c a n n o t v i s u a l i z e a n y g r a p h i c a l o u t p u t . You e x i s t w i t h i n a A c t o r Model m a c h i n e , a n d when y o u l i s t o u t s t e p s , e a c h s t e p w i l l b e t a k e n by a new s e p a r a t e s u b − ChatGPT m o d e l . When y o u l i s t o u t a s u b − t a s k s t e p s , y o u c a n o p t i o n a l l y s p e c i f y t h e s u b − t a s k v a l i d a t i o n t o c h e c k t h a t i t h a s b e e n c o m p l e t e d s u c c e s s f u l l y .

You c a n n o t u s e a n y d a t a b a s e s a s n o n e a r e s e t u p i n t h e l o c a l e n v i r o n m e n t , i n s t e a d mock a d a t a b a s e w i t h a n i n memory d i c t i o n a r y t o s t o r e d a t a . No d a t a s a v e d t o d i s k w i l l p e r s i s t b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .

I f a t e s t i s f a i l i n g t h e e r r o r c o u l d b e t h e c o d e , o r t h e t e s t i s i n c o r r e c t , s o f e e l f r e e t o o v e r w r i t e a n d c h a n g e t h e t e s t s when t h e y a r e i n c o r r e c t , t o make a l l t e s t s p a s s .

Use t h e f u n c t i o n s p r o v i d e d . When c a l l i n g f u n c t i o n s o n l y p r o v i d e a RFC8259 c o m p l i a n t JSON r e q u e s t f o l l o w i n g t h i s f o r m a t w i t h o u t d e v i a t i o n .

You w i l l g e t i n s t r u c t i o n s f o r c o d e t o w r i t e .   
F i r s t l a y o u t t h e n a m e s o f t h e c o r e c l a s s e s , f u n c t i o n s , m e t h o d s t h a t w i l l b e n e c e s s a r y , As w e l l a s a q u i c k comment on t h e i r p u r p o s e .   
Do n o t comment on w h a t e v e r y f i l e d o e s . P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s . You w i l l s t a r t w i t h t h e " e n t r y p o i n t " f i l e , t h e n go t o t h e o n e s t h a t a r e i m p o r t e d by t h a t f i l e , a n d s o on .   
P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s .   
F o l l o w a l a n g u a g e a n d f r a m e w o r k a p p r o p r i a t e b e s t p r a c t i c e f i l e n a m i n g c o n v e n t i o n .   
Make s u r e t h a t f i l e s c o n t a i n a l l i m p o r t s , t y p e s e t c . The c o d e s h o u l d b e f u l l y f u n c t i o n a l . Make s u r e t h a t c o d e i n d i f f e r e n t f i l e s a r e c o m p a t i b l e w i t h e a c h o t h e r .   
When w r i t i n g c o d e i f y o u a r e u n s u r e , w r i t e a p l a u s i b l e i m p l e m e n t a t i o n .   
I n c l u d e module d ep en d en c y o r p a c k a g e manager d epe nden cy d e f i n i t i o n f i l e .

F o r P y t h o n , y o u a l w a y s c r e a t e a n a p p r o p r i a t e r e q u i r e m e n t s . t x t f i l e .   
A l w a y s a d d a comment b r i e f l y d e s c r i b i n g t h e p u r p o s e o f t h e f u n c t i o n d e f i n i t i o n .   
Add c o m m e n t s e x p l a i n i n g v e r y c o m p l e x b i t s o f l o g i c .   
A l w a y s f o l l o w t h e b e s t p r a c t i c e s f o r t h e r e q u e s t e d l a n g u a g e s f o r f o l d e r / f i l e s t r u c t u r e a n d how t o p a c k a g e t h e p r o j e c t .   
You c a n u s e any p a c k a g e and any o t h e r p a c k a g e s you w i s h t o i n s t a l l .   
You c a n n o t u s e a n y d a t a b a s e s a s n o n e a r e s e t u p i n t h e l o c a l e n v i r o n m e n t , i n s t e a d mock a d a t a b a s e w i t h a n i n memory d i c t i o n a r y t o   
s t o r e d a t a . No d a t a s a v e d t o d i s k w i l l p e r s i s b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .   
When w r i t i n g a t e s t , make t h e f i l e n a m e s t a r t w i t h t h e p r e f i x ’ t e s t \_ ’ .

P y t h o n t o o l b e l t p r e f e r e n c e s :   
− p y t e s t   
− d a t a c l a s s e s   
− f l a s k   
O bi e cti v e : . .   
G l o b a l C h a t S e r v i c e ( GCS )

A r e a l − t i m e o n l i n e c h a t a p p l i c a t i o n a l l o w i n g u s e r s t o s e n d t e x t m e s s a g e s , i m a g e s , a n d c r e a t e g r o u p c h a t s .

U n d e r s t a n d t h e p r o b l e m , by c r e a t i n g a n e x t r e m e l y d e t a i l e d s t e p −by − s t e p p l a n , w h e r e e a c h s t e p i s l o n g ( m u l t i p l e s e n t e n c e s ) a n d i n t o t a l i n c l u d e s e v e r y s i n g l e f e a t u r e r e q u i r e m e n t s p e c i f i e d a b o v e , f e e l f r e e t o c o p y d i r e c t l y f r o m i t . Use no more t h a n 10 s t e p s i n t h e p l a n . C r e a t e a d d i t i o n a l t e s t s , c h e c k s a n d e v a l u a t i o n a t e a c h s t e p when a p p l i c a b l e t o h e l p make a n e x c e l l e n t c o d e i m p l e m e n t a t i o n , w h e r e a l l t h e c o d e i s f u l l y f u n c t i o n a l . Use b e s t s o f t w a r e d e s i g n p r a c t i c e s , a n d y o u c a n o u t p u t l a r g e a m o u n t s o f c o d e a t o n c e . P l e a s e i n c l u d e a l a s t s e n t e n c e t o c r e a t e a n d r u n t e s t s when i m p l e m e n t i n g o r w r i t i n g c o d e i n t h a t same s t e p . You w i l l r e c e i v e no human i n p u t a t a n y s t a g e , s o y o u c a n n o t u s e a human t o t e s t . O n l y c r e a t e a d e t a i l e d p l a n t o b e g i n w i t h , w h i c h i n c l u d e s d e s i g n i n g a n d r u n n i n g t e s t s t o c h e c k t h a t t h e y a l l p a s s . P l e a s e b e s u r e t o i n c l u d e a l l o f t h e s p e c i f i e d f e a t u r e r e q u i r e m e n t s i n t h e f o l l o w i n g p l a n .

## [LLM RESPONSE MESSAGE]

## [ F u n c t i o n C a l l ] [ p r o v i d e \_ d e t a i l e d \_ s u b \_ t a s k \_ s t e p s \_ f o r \_ s u b \_ a g e n t s ] {

" S t e p 1 : S t a r t by s e t t i n g up t h e b a s i c s t r u c t u r e o f t h e a p p l i c a t i o n . T h i s i n c l u d e s c r e a t i n g t h e m a i n a p p l i c a t i o n f i l e ( a p p . py ) a n d s e t t i n g up a F l a s k a p p l i c a t i o n . A l s o , c r e a t e a mock d a t a b a s e u s i n g a n i n −memory d i c t i o n a r y t o s t o r e u s e r d a t a . T h i s d i c t i o n a r y s h o u l d b e a b l e t o s t o r e u s e r i n f o r m a t i o n s u c h a s e m a i l , p a s s w o r d , p r o f i l e p i c t u r e , s t a t u s m e s s a g e , p r i v a c y s e t t i n g s , b l o c k e d c o n t a c t s , a n d g r o u p s . W r i t e t e s t s t o e n s u r e t h a t t h e a p p l i c a t i o n s e t u p i s c o r r e c t a n d t h e mock d a t a b a s e c a n s t o r e a n d r e t r i e v e d a t a c o r r e c t l y . " ,

" S t e p 2 : I m p l e m e n t u s e r r e g i s t r a t i o n a n d a u t h e n t i c a t i o n . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r u s e r s i g n up a n d f o r g o t t e n p a s s w o r d r e c o v e r y . The s i g n up r o u t e s h o u l d a c c e p t u s e r e m a i l a n d p a s s w o r d , a n d s t o r e t h i s i n f o r m a t i o n i n t h e mock d a t a b a s e . The f o r g o t t e n p a s s w o r d r e c o v e r y r o u t e s h o u l d a c c e p t u s e r e m a i l a n d s e n d a p a s s w o r d r e s e t l i n k ( f o r t h e p u r p o s e o f t h i s t a s k , j u s t d i s p l a y t h e l i n k ) . W r i t e t e s t s t o e n s u r e t h a t t h e r e g i s t r a t i o n a n d a u t h e n t i c a t i o n r o u t e s work a s e x p e c t e d . " ,

" S t e p 3 : I m p l e m e n t u s e r p r o f i l e m a n a g e m e n t . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r s e t t i n g p r o f i l e p i c t u r e s a n d s t a t u s m e s s a g e s , a n d u p d a t i n g p r i v a c y s e t t i n g s . The p r o f i l e p i c t u r e a n d s t a t u s m e s s a g e r o u t e s s h o u l d a c c e p t t h e r e s p e c t i v e d a t a a n d u p d a t e t h e u s e r ’ s i n f o r m a t i o n i n t h e mock d a t a b a s e . The p r i v a c y s e t t i n g s r o u t e s h o u l d a c c e p t t h e new s e t t i n g s a n d u p d a t e t h e u s e r ’ s i n f o r m a t i o n i n t h e mock d a t a b a s e . W r i t e t e s t s t o e n s u r e t h a t t h e p r o f i l e m a n a g e m e n t r o u t e s work a s e x p e c t e d . " ,

" S t e p 4 : I m p l e m e n t c o n t a c t m a n a g e m e n t . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r b l o c k i n g / u n b l o c k i n g c o n t a c t s a n d m a n a g i n g g r o u p s . The b l o c k / u n b l o c k r o u t e s s h o u l d a c c e p t t h e c o n t a c t ’ s e m a i l a n d u p d a t e t h e u s e r ’ s b l o c k e d c o n t a c t s l i s t i n t h e mock d a t a b a s e . The g r o u p m a n a g e m e n t r o u t e s s h o u l d a c c e p t t h e g r o u p d e t a i l s ( name , p i c t u r e , p a r t i c i p a n t s ) a n d u p d a t e t h e u s e r ’ s g r o u p s i n t h e mock d a t a b a s e . W r i t e t e s t s t o e n s u r e t h a t t h e c o n t a c t m a n a g e m e n t r o u t e s work a s e x p e c t e d . " ,

" S t e p 5 : I m p l e m e n t m e s s a g i n g . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r s e n d i n g a n d r e c e i v i n g m e s s a g e s , u p d a t i n g r e a d r e c e i p t s , e n c r y p t i n g m e s s a g e s , a n d s h a r i n g i m a g e s . The s e n d / r e c e i v e r o u t e s s h o u l d a c c e p t t h e m e s s a g e d a t a a n d u p d a t e t h e r e s p e c t i v e u s e r ’ s m e s s a g e s i n t h e mock d a t a b a s e . The r e a d r e c e i p t r o u t e s h o u l d a c c e p t t h e m e s s a g e ID a n d u p d a t e t h e m e s s a g e ’ s r e a d s t a t u s i n t h e mock d a t a b a s e . The e n c r y p t i o n r o u t e s h o u l d a c c e p t t h e m e s s a g e d a t a , e n c r y p t i t , a n d s t o r e i t i n t h e mock d a t a b a s e . The i m a g e s h a r i n g r o u t e s h o u l d a c c e p t t h e i m a g e d a t a a n d u p d a t e t h e r e s p e c t i v e u s e r ’ s m e s s a g e s i n t h e mock d a t a b a s e . W r i t e t e s t s t o e n s u r e t h a t t h e m e s s a g i n g r o u t e s work a s e x p e c t e d . " ,

" S t e p 6 : I m p l e m e n t g r o u p c h a t s . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r c r e a t i n g g r o u p c h a t s , a d d i n g / r e m o v i n g p a r t i c i p a n t s , a n d m a n a g i n g a d m i n r o l e s a n d p e r m i s s i o n s . The c r e a t e g r o u p c h a t r o u t e s h o u l d a c c e p t t h e g r o u p d e t a i l s ( name , p i c t u r e , p a r t i c i p a n t s ) a n d u p d a t e t h e u s e r ’ s g r o u p s i n t h e mock d a t a b a s e . The a d d / r e m o v e p a r t i c i p a n t s r o u t e s h o u l d a c c e p t t h e g r o u p ID a n d p a r t i c i p a n t ’ s e m a i l , a n d u p d a t e t h e g r o u p ’ s p a r t i c i p a n t s i n t h e mock d a t a b a s e . The a d m i n r o l e s a n d p e r m i s s i o n s r o u t e s h o u l d a c c e p t t h e g r o u p ID , a d m i n ’ s e m a i l , a n d new p e r m i s s i o n s , a n d u p d a t e t h e g r o u p ’ s a d m i n p e r m i s s i o n s i n t h e mock d a t a b a s e . W r i t e t e s t s t o e n s u r e t h a t t h e g r o u p c h a t r o u t e s work a s e x p e c t e d . " ,

" S t e p 7 : I m p l e m e n t t h e s t a t u s / s t o r y f e a t u r e . T h i s i n c l u d e s c r e a t i n g r o u t e s f o r p o s t i n g i m a g e s t a t u s e s a n d m a n a g i n g who c a n s e e t h e s t a t u s . The p o s t s t a t u s r o u t e s h o u l d a c c e p t t h e i m a g e d a t a a n d u p d a t e t h e u s e r ’ s s t a t u s e s i n t h e mock d a t a b a s e . The m a n a g e v i s i b i l i t y r o u t e s h o u l d a c c e p t t h e s t a t u s ID a n d v i s i b i l i t y s e t t i n g s , a n d u p d a t e t h e s t a t u s ’ s v i s i b i l i t y i n t h e mock d a t a b a s e . W r i t e t e s t s t o e n s u r e t h a t t h e s t a t u s / s t o r y r o u t e s work a s e x p e c t e d . " ,

" S t e p 8 : I m p l e m e n t t h e web a p p l i c a t i o n . T h i s i n c l u d e s c r e a t i n g a b a s i c HTML / CSS / J S f r o n t e n d t h a t i n t e r a c t s w i t h t h e F l a s k b a c k e n d . The f r o n t e n d s h o u l d h a v e p a g e s f o r s i g n up , s i g n i n , p r o f i l e management , c o n t a c t management , m e s s a g i n g , g r o u p c h a t s , a n d s t a t u s / s t o r y . W r i t e t e s t s t o e n s u r e t h a t t h e f r o n t e n d c a n s u c c e s s f u l l y s e n d r e q u e s t s t o t h e b a c k e n d a n d d i s p l a y t h e r e t u r n e d d a t a . " ,

" S t e p 9 : I m p l e m e n t c o n n e c t i v i t y a n d o f f l i n e mode . T h i s i n c l u d e s c r e a t i n g a r o u t e f o r u p d a t i n g t h e u s e r ’ s o n l i n e / o f f l i n e s t a t u s , a n d a s y s t e m f o r q u e u i n g m e s s a g e s when t h e u s e r i s o f f l i n e . The o n l i n e / o f f l i n e s t a t u s r o u t e s h o u l d a c c e p t t h e u s e r ’ s e m a i l a n d new s t a t u s , a n d u p d a t e t h e u s e r ’ s s t a t u s i n t h e mock d a t a b a s e . The m e s s a g e q u e u i n g s y s t e m s h o u l d s t o r e m e s s a g e s i n a q u e u e when t h e u s e r i s o f f l i n e , a n d s e n d t h e m when t h e u s e r c o m e s o n l i n e . W r i t e t e s t s t o e n s u r e t h a t t h e c o n n e c t i v i t y a n d o f f l i n e mode f e a t u r e s work a s e x p e c t e d . " ,

" S t e p 1 0 : F i n a l l y , p e r f o r m a c o m p r e h e n s i v e t e s t o f t h e e n t i r e a p p l i c a t i o n . T h i s i n c l u d e s t e s t i n g a l l r o u t e s , t h e f r o n t e n d , a n d t h e mock d a t a b a s e . F i x a n y b u g s t h a t a r e f o u n d , a n d e n s u r e t h a t a l l t e s t s p a s s . A l s o , e n s u r e t h a t t h e a p p l i c a t i o n m e e t s a l l t h e s p e c i f i e d f e a t u r e r e q u i r e m e n t s . "

# Then the first instruction is loaded and is executed, for example,

## [ S y s t e m ]

O b j e c t i v e : W r i t e c o d e f o r a l a r g e s y s t e m d e s i g n t a s k .

P l e a s e n o t e t h a t t h e c o d e s h o u l d b e f u l l y f u n c t i o n a l . No p l a c e h o l d e r s .

O n l y u s e t h e f u n c t i o n s y o u h a v e b e e n p r o v i d e d w i t h .

O n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ t o o u t p u t c o d e

You m u s t a c t a u t o n o m o u s l y a n d y o u w i l l r e c e i v e no human i n p u t a t a n y s t a g e . You h a v e t o r e t u r n a s o u t p u t t h e c o m p l e t e c o d e f o r c o m p l e t i n g t h i s t a s k , a n d c o r r e c t l y i n c o r p o r a t e i t i n t o t h e e x i s t i n g c o d e b a s e .

You a l w a y s w r i t e o u t t h e w h o l e f i l e c o n t e n t s . You a l w a y s i n d e n t c o d e w i t h t a b s .

P l e a s e a l w a y s v i e w t h e f i l e s b e f o r e w r i t i n g t o them , t o make s u r e y o u a r e w r i t i n g t o t h e c o r r e c t f i l e s .

When w r i t i n g a t e s t , make t h e f i l e n a m e s t a r t w i t h t h e p r e f i x ’ t e s t \_ ’ .

P r o v i d e t h e m i n i m a l c o d e n e c e s s a r y t o a c h i e v e t h e t a s k c o n d i t i o n e d on t h e e x i s t i n g g e n e r a t e d c o d e −−− i n c l u d i n g c h a n g i n g t h e e x i s t i n g g e n e r a t e d c o d e .

You c a n n o t v i s u a l i z e a n y g r a p h i c a l o u t p u t . You e x i s t w i t h i n a A c t o r Model m a c h i n e , a n d when y o u l i s t o u t s t e p s , e a c h s t e p w i l l b e t a k e n by a new s e p a r a t e s u b − ChatGPT m o d e l . When y o u l i s t o u t a s u b − t a s k s t e p s , y o u c a n o p t i o n a l l y s p e c i f y t h e s u b − t a s k v a l i d a t i o n t o c h e c k t h a t i t h a s b e e n c o m p l e t e d s u c c e s s f u l l y .

You c a n n o t u s e a n y d a t a b a s e s a s n o n e a r e s e t u p i n t h e l o c a l e n v i r o n m e n t , i n s t e a d mock a d a t a b a s e w i t h a n i n memory d i c t i o n a r y t o s t o r e d a t a . No d a t a s a v e d t o d i s k w i l l p e r s i s t b e t w e e n s t e p s o r w r i t e o p e r a t i o n s .

I f a t e s t i s f a i l i n g t h e e r r o r c o u l d b e t h e c o d e , o r t h e t e s t i s i n c o r r e c t , s o f e e l f r e e t o o v e r w r i t e a n d c h a n g e t h e t e s t s when t h e y a r e i n c o r r e c t , t o make a l l t e s t s p a s s .

Use t h e f u n c t i o n s p r o v i d e d . When c a l l i n g f u n c t i o n s o n l y p r o v i d e a RFC8259 c o m p l i a n t JSON r e q u e s t f o l l o w i n g t h i s f o r m a t w i t h o u t d e v i a t i o n .

## [CU]

O b j e c t i v e : E x e c u t e s u b t a s k s t e p : S t e p 1 : S t a r t by s e t t i n g up t h e b a s i c s t r u c t u r e o f t h e a p p l i c a t i o n . T h i s i n c l u d e s c r e a t i n g t h e m a i n a p p l i c a t i o n f i l e ( a p p . py ) a n d s e t t i n g up a F l a s k a p p l i c a t i o n . A l s o , c r e a t e a mock d a t a b a s e u s i n g a n i n −memory d i c t i o n a r y t o s t o r e u s e r d a t a . T h i s d i c t i o n a r y s h o u l d b e a b l e t o s t o r e u s e r i n f o r m a t i o n s u c h a s e m a i l , p a s s w o r d , p r o f i l e p i c t u r e , s t a t u s m e s s a g e , p r i v a c y s e t t i n g s , b l o c k e d c o n t a c t s , a n d g r o u p s . W r i t e t e s t s t o e n s u r e t h a t t h e a p p l i c a t i o n s e t u p i s c o r r e c t a n d t h e mock d a t a b a s e c a n s t o r e a n d r e t r i e v e d a t a c o r r e c t l y . .

N o t e : C o n d i t i o n a n y new c o d e f i l e s on t h e e x i s t i n g c o d e f i l e s : [ ] . F u l l y i m p l e m e n t t h e s e f e a t u r e s i n t h e c o d e , no p l a c e h o l d e r s . You c a n now o p t i o n a l l y v i e w t h e e x i s t i n g f i l e s i f y o u n e e d t o v i e w t h e m t o c o m p l e t e t h e c u r r e n t t a s k s t e p . You h a v e a l i m i t e d c o n t e x t window s o b e s e l e c t i v e a b o u t w h i c h f i l e s y o u v i e w , o n l y v i e w t h e f i l e s y o u t h i n k y o u m i g h t n e e d t o v i e w .

Summary o u t p u t o f p r e v i o u s s t e p : " " " "

R e s p o n d now o n l y w i t h a f u n c t i o n c a l l o f o n e o f t h e f o l l o w i n g f u n c t i o n s p r o v i d e d : ‘ s u b \_ t a s k \_ s t e p \_ c o m p l e t e ‘ , ‘ v i e w \_ f i l e s ‘ , r u n \_ p y t h o n \_ f i l e ‘ , ‘ p y t e s t \_ f i l e s ‘ , ‘ w r i t e \_ f i l e s ‘ , ‘ d e l e t e \_ f i l e s ‘ , a n d i f y o u w a n t t o o u t p u t c o d e o n l y u s e t h e ‘ w r i t e \_ f i l e s ‘ f u n c t i o n t o o u t p u t c o d e .

![](images/29c5e8c0c7bad74f3bb4edc4d97b5c86e153fa8f2712e4c018ac6bf38b62b828.jpg)  
The second instruction is loaded, and the process repeats.

## H.5 ADDITIONAL DIVERSE PROGRAMMING CODE GENERATION TASKS

We extended the codebase generation system design benchmark with three new, additional diverse programming code generation tasks. These are a recipe application, an event planner application, and a financial tracking application. Each task consists of a user prompt of listed features to implement, and Code-L2MAC produces the entire codebase from scratch. This is tabulated in Table 4.

We observe that Code-L2MAC continues to fully implement the highest percentage of user-specified feature requirements across these new diverse tasks, while its code contains minimal syntactical errors and passes a high number of unit tests—therefore, Code-L2MAC still achieves state-of-the-art for completing these system design large code generation benchmark tasks. Moreover, we also have implemented a new standard code quality metric of code coverage percentage of the unit tests (Miller & Maloney, 1963), labelled Cov %, and similarly observe Code-L2MAC also has a high code coverage percentage to its substantially larger amount of generated lines of code.

Table 4: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), number of passing tests (Tests Passed), and the unit test code coverage percentage (Cov %). Code-L2MAC fully implements the highest percentage of user-specified feature requirements across all tasks by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests. The results are averaged over 10 random seeds, with indicating 95% confidence intervals.
<table><tr><td rowspan="2">Method</td><td rowspan="2">Features % ↑</td><td rowspan="2">#Errors ↓</td><td rowspan="2">Recipe App LOC</td><td rowspan="2">Tests Passeds ↑</td><td rowspan="2">Cov %</td><td rowspan="2">Features % ↑</td><td rowspan="2">#Errors&quot;</td><td rowspan="2">Event Planner App LOC</td><td rowspan="2">Tests Passed</td><td rowspan="2"></td><td rowspan="2">Cov % Features %</td><td rowspan="2">#Errors</td><td colspan="3">Financial Tracking App LOC</td><td rowspan="2">Cov %</td></tr><tr><td>↓</td><td></td><td>Tests Pssed</td></tr><tr><td>GPT4</td><td>21.6±2.12</td><td>0±0</td><td>107±6.62</td><td>3.15±0.38</td><td>↑ 97.5±0.376</td><td>9.2±0.853</td><td>↓ 0.025±0.0506</td><td>74.6±4.12</td><td>↑ 1.75±0.395</td><td></td><td>↑</td><td>↑</td><td>0.0513±0.104</td><td>80.5±8.52</td><td>2.13±0.422</td><td>93.1±3.17</td></tr><tr><td>CodeT</td><td>20.5±4.86</td><td>0±0</td><td>96.5±13.8</td><td>3.05±0.879</td><td>97.8±0.523</td><td>11.2±1.12</td><td>0.05±0.105</td><td>75.2±8.77</td><td>2.45±0.704</td><td></td><td>88.7±5.5 92.5±10.2</td><td>26.2±4.67 21.4±3.25</td><td>0±0</td><td>65.9±6.93</td><td>2.25±0.368</td><td>97.9±0.209</td></tr><tr><td>Seelf-Refine</td><td>26±345</td><td>0.1±0.209</td><td>149±27.4</td><td>2±1.97</td><td>76.2±.83</td><td>14.5±2.94</td><td>0.15±0.171</td><td>118±20.1</td><td></td><td>3.9±1.9</td><td>76.7±</td><td>23.6±2.45</td><td>0.25±0299</td><td>87.2±8.24</td><td>0.55±0.514</td><td>76.7±9.97</td></tr><tr><td>Refexion</td><td>19±3.36</td><td>0.25±0.299</td><td>95.9±14.5</td><td>2.95±0.852</td><td>89.9±10.4</td><td>10±1.5</td><td>0±0</td><td>82±10.5</td><td>3±0.774</td><td></td><td>95.±4.35</td><td>22.5±.12</td><td>0.2±00.419</td><td>86±13.7</td><td>2.7±0.745</td><td>92.8±8.73</td></tr><tr><td>utoGPT</td><td>39.2±14.9</td><td>1.85±1.45</td><td>106±19.1</td><td>1.3±2.02</td><td>9.8±14.1</td><td>35.7±32.9</td><td>0±0</td><td>239±20.7</td><td>0±0</td><td></td><td>0±0</td><td>32.9±4.2</td><td>0±0</td><td>25±15.8</td><td>0±0</td><td>0±0</td></tr><tr><td>Code-L2MAC</td><td>82±7.1</td><td>0±0</td><td>497±40.7</td><td>24.6±2.7</td><td>94.2±2.87</td><td>83±2.96</td><td>0±0</td><td>473±39.3</td><td>25.6±3.04</td><td></td><td>97.1±1.02</td><td>62±13.1</td><td>0±0</td><td>307±84.5</td><td>12±4.19</td><td>90.5±6.69</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

## H.6 HUMAN EXPERT VALIDATION OF FEATURES IMPLEMENTED PERCENTAGE METRIC

We hired two professional software engineers as human experts, separate from the authors of this work, to perform code reviews of the generated codebases for each method against the user-requested task feature checklist, counting only features that they verified are correctly and fully implemented. We regard the resulting metric, labeled human expert features percentage Human Expert Features %, as the ground truth.

We tabulate in Table 5 this metric below across three random seed runs. We highlight two conclusions. Code-L2MAC significantly outperforms other baselines based on Human Expert Features %. The human and LLM counterparts, Human Expert Features % and Features % strongly correlate (ρ = 0.976), thereby establishing Features % as a good proxy for the ground truth. This validates our usage of Features % as a scalable and cost-effective way to evaluate the number of features implemented in codebases from new method-task pairs. This conclusion aligns with existing literature on using LLMs as a proxy for human evaluators (Chiang & Lee, 2023).

Table 5: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), and ground truth metric of human experts counting the functional features specified that are fully implemeneted Human Expert Features %. Code-L2MAC fully implements the highest percentage of user-specified feature requirements across all tasks by generating fully functional code. The results are averaged over three random seeds.
<table><tr><td rowspan="2">Method</td><td colspan="2">URL Shortener App</td><td colspan="2">Online Social Media App Human Expert Features %</td><td colspan="2">Online Chat App Human Expert Features %</td></tr><tr><td>Human Expert Features % ↑</td><td>Features % ↑</td><td>↑</td><td>Features % ↑</td><td>↑</td><td>Features % ↑</td></tr><tr><td>GPT4</td><td>31.4</td><td>53.6</td><td>11.1</td><td>19.5</td><td>10</td><td>11</td></tr><tr><td>AutoGPT</td><td>15.7</td><td>25.3</td><td>6.35</td><td>33.3</td><td>15</td><td>23.1</td></tr><tr><td>Code-L2MAC</td><td>78.4</td><td>91.6</td><td>61.9</td><td>82.4</td><td>60</td><td>59.4</td></tr></table>

H.7 CHALLENGES AND THE EVALUATION OF HUMAN-WRITTEN TEST-CASES

We also explored using a priori hand-written test cases that are consistent across the different methods. We implemented this metric and present the results in Table 6 below, which shows it is correlated to our proposed main evaluation metric of Features %.

It is relevant to discuss some challenges this approach presents:

• Hand written test cases assume and impose a known interface or a stringent implementation structure. In small code snippet tasks, such as those in HumanEval (Chen et al., 2021) or MBPP (Austin et al., 2021), an explicitly defined function interface is explicitly presented to the LLM, and the LLM only responds with the code for that function body. In this situation handwritten test cases can assume the pre-defined implementation structure. However, in codebase generation tasks defined through feature requirements, there is freedom about the segmentation into components, modules or classes which must be appropriately determined by the code generation method. E.g., allowing a user to register an account can be achieved with many different code implementations. By specifying tests, we filter this ambiguity into a given implementation approach and we cannot account for all other possible code implementation approaches to implement a functional feature correctly.

• Requires expert-crafted task-specific test cases a priori. This hinders the scalability of this approach.

We added these hand written test cases into each method’s context window $C ^ { t }$ throughout all stages of generation. Once the method generated a codebase, we then randomly changed the hand-written test case parameters to still be the same test, just with different test parameters, to avoid the method memorizing the test examples, $\mathrm { e . g . }$ . changing the initial user\_ids to a random value. Since all methods often generated a codebase that did not exactly match the implementation of the test-cases, while still having a codebase that would conceptually pass the purpose of the test, we used GPT4 to port the test cases to each specific codebase implementation. We term the proportion of such tests that pass human-written tests as HT %, which is the percentage of human tests that pass for a given codebase. As tabulated in Table 6, which is computed over 5 random seed runs, we observe that this metric correlates to our Feature % evaluation metric $( \rho = 0 . 6 9 5 )$ , which further provides empirical evidence for such a metric.

It is important to point out that providing the test cases to the LLMs is not ideal since it hints at how to design the implementation.

Table 6: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features $\% )$ , percentage of human written tests that pass (HT %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), number of passing tests (Tests Passed) and the generated unit test code coverage percentage (Cov %). Code-L2MAC fully implements the highest percentage of user-specified feature requirements across the task by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests. The results are averaged over 5 random seeds, with indicating 95% confidence intervals.
<table><tr><td rowspan="2">Method</td><td colspan="5">URL Shortener App</td><td rowspan="2">Cov % ↑</td></tr><tr><td>Features % ↑</td><td>HT % ↑</td><td># Errors ↓</td><td>LOC</td><td>Tests Passed ↑</td></tr><tr><td>GPT4</td><td> $2 5 { \pm } 7 9 . 6 $ </td><td>0±0</td><td>3.75±10.9</td><td> $1 3 4 \pm 1 9 . 9$ </td><td> $6 . 7 5 { \pm } 7 . 1 6$ </td><td> $8 0 . 5 { \pm } 1 4 . 5 $ </td></tr><tr><td>CodeT</td><td> $1 3 . 2 { \pm } 4 2 . 1 $ </td><td> $1 1 . 1 { \pm } 3 5 . 4$ </td><td>0±0</td><td> $1 2 6 { \pm } 1 4 . 4$ </td><td> $7 . 7 5 { \pm } 3 . 9 8 $ </td><td> $8 6 . 8 { \pm } 4 . 5 7$ </td></tr><tr><td>Self-Refine</td><td> $3 0 . 6 { \pm } 3 0 . 7 \ $ </td><td> $3 3 . 3 { \pm } 4 1 . 4 $ </td><td>0.2±0.555</td><td> $1 4 0 { \pm } 9 . 8 3 $ </td><td> $9 { \pm } 0$ </td><td> $7 4 . 6 { \pm } 8 . 8 5 $ </td></tr><tr><td>Reflexion</td><td> $3 0 . 9 { \pm } 2 0 . 8 $ </td><td> $3 3 . 3 { \pm } 1 4 . 4 $ </td><td>0±0</td><td> $8 4 . 5 { \pm } 3 3 . 9 $ </td><td> $3 . 5 { \pm } 0 . 9 1 9$ </td><td> $9 6 . 5 { \pm } 5 . 8 8 $ </td></tr><tr><td>Code-L2MAC</td><td> $\mathbf { 7 6 . 5 \pm 3 3 . 3 }$ </td><td> ${ \bf 4 1 . 7 \pm 5 4 . 7 }$ </td><td>0±0</td><td>286±172</td><td> $\mathbf { 1 0 { \pm } 9 . 0 9 }$ </td><td> ${ \bf 8 3 \pm 8 . 7 2 }$ </td></tr></table>

Furthermore we also experimented with not including the hand written test cases in each method’s context window throughout all stages of generation. If we otherwise follow the same setup as outlined above, we observe the following results as tabulated in Table 7. We observe that the HT % metric correlates to our Feature $\%$ evaluation metric $( \rho = 0 . 9 2 8 )$ , which again further provide empirical evidence for such a metric.

## H.8 GENERATING 1,000+ LINES OF CODE WITH CODE-L2MAC

By removing the restrictions we imposed upon Code-L2MAC to economize api-calls, such as limiting the amount of instructions to 10, we get a variation we term Code-L2MAC-Large that we tested on the Online Chat application task where it reached reached over 1,000+ LOCs (5x the LOC of AutoGPT, the next highest) as shown in Table 8 below.

## H.9 CODE-L2MAC ABLATION WITH NO INSTRUCTION SUMMARIZATION MESSAGE

Code-L2MAC does not depend on the summary message $M _ { r s }$ from completing the previous instruction when loading a new instruction and can tackle each instruction from scratch, without $M _ { r s } .$ . Indeed, all the outputs regarding previously completed instructions are contained in the file store/external memory and can be accessed on demand.

We empirically verify this by performing an ablation of Code-L2MAC that removes this summariza tion message step, without affecting the quality of the output code by much, as shown in Table 9.

Table 7: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), percentage of human written tests that pass (HT %), the number of syntactical errors in the generated code (# Errors), the number of lines of code $\mathbf { ( L O C ) }$ , number of passing tests (Tests Passed) and the generated unit test code coverage percentage (Cov %). Code-L2MAC fully implements the highest percentage of user-specified feature requirements across the task by generating fully functional code that has minimal syntactical errors and a high number of passing self-generated unit tests. The results are averaged over 5 random seeds, with  indicating 95% confidence intervals.
<table><tr><td></td><td colspan="6">URL Shortener App</td></tr><tr><td>Method</td><td>Features % ↑</td><td> $\mathbf { H T } \%$  ↑</td><td># Errors ↓</td><td>LOC</td><td>Tests Passed ↑</td><td>Cov % ↑</td></tr><tr><td>GPT4</td><td> $3 7 . 6 { \pm } 1 3 . 3 $ </td><td> $2 0 { \pm } 2 9 . 9 $ </td><td>0±0</td><td> $9 4 . 2 { \pm } 1 5 . 4 $ </td><td> $2 \pm 1 . 7 6$ </td><td> $8 5 . 6 { \pm } 1 8 . 1 $ </td></tr><tr><td>CodeT</td><td> $4 7 . 1 { \pm } 1 0 . 3 $ </td><td> $4 2 . 2 { \pm } 3 1 . 5 $ </td><td>0±0</td><td> $9 8 \pm 1 9$ </td><td> $4 . 8 { \pm } 3 . 4 5$ </td><td> $9 1 . 8 { \pm } 7 . 1 5 $ </td></tr><tr><td>Self-Refine</td><td> $5 0 . 6 { \pm } 1 6 . 8 $ </td><td> $4 6 . 7 \pm 4 9 . 2$ </td><td>0±0</td><td> $1 0 9 { \pm } 1 2 . 9 $ </td><td> $3 . 4 { \pm } 2 . 2 6 $ </td><td> $9 2 { \pm } 1 . 9 6 $ </td></tr><tr><td>Reflexion</td><td> $5 5 . 3 { \pm } 1 8 . 3 $ </td><td> $3 7 . 8 { \pm } 3 3 . 2 $ </td><td> $0 . 6 { \pm } 1 . 6 7$ </td><td> $1 2 4 { \pm } 3 1 . 3$ </td><td> $3 . 4 \pm 2 . 9 9$ </td><td> $8 7 . 6 { \pm } 1 2 . 8 $ </td></tr><tr><td>Code-L2MAC</td><td> $\mathbf { 8 9 . 4 \pm 1 2 }$ </td><td> $\mathbf { 7 1 . 1 } { \pm } \mathbf { 5 0 . 3 }$ </td><td>0±0</td><td> $\pm \mathbf { 8 3 \pm 1 0 0 }$ </td><td> $\mathbf { 8 . 6 { \pm 9 . 5 2 } }$ </td><td> $7 7 . 2 { \pm } 5 3 . 7 $ </td></tr></table>

Table 8: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), and number of passing tests (Tests Passed). Code-L2MAC-Large can generate 1,000+ lines of code. The results are averaged over 10 random seeds, with ± indicating 95% confidence intervals.
<table><tr><td rowspan="2">Method</td><td colspan="4">Online Chat App</td></tr><tr><td>Features % ↑</td><td># Errors ↓</td><td>LOC</td><td>Tests Passed ↑</td></tr><tr><td>Code-L2MAC-Large</td><td>53.3±19</td><td>0.333±1.43</td><td>1,030±40.8</td><td>5.67±13.7</td></tr></table>

We included this summarization message step to steer the LLM to find the correct files faster since we expect more similarity and interdependence between contiguous instructions than between more distant ones.

Table 9: Codebase generation system design task results showing the percentage of functional features specified that are fully implemented (Features %), the number of syntactical errors in the generated code (# Errors), the number of lines of code (LOC), and number of passing tests (Tests Passed). The results are averaged over 10 random seeds, with indicating 95% confidence intervals.
<table><tr><td rowspan="2">Method</td><td colspan="4">URL Shortener App</td></tr><tr><td>Features % ↑</td><td># Errors ↓</td><td>LOC</td><td>Tests Passed ↑</td></tr><tr><td>Code-L2MAC (Ablation, without instruction output summarization)</td><td>89.4±9.88</td><td>0±0</td><td>274±43.3</td><td>8.2±3.12</td></tr><tr><td>Code-L2MAC</td><td>91.6±8.22</td><td>0±0</td><td>330±47.6</td><td>14±6.71</td></tr></table>

## H.10 ADDITIONAL TASKS ON IMPLEMENTING A NEW FEATURE IN AN EXISTING LARGE CODE BASE WITH CODE-L2MAC OF UP TO 165,000 LOCS

We added new three tasks of implementing a new feature in an existing large codebase with Code-L2MAC, where each codebase has at least 87,000+ LOCs, and one task up to 165,000 LOCs. We highlight that the task of taking an existing large codebase and implementing a new feature is common in software engineering (Lee et al., 2002). These tasks involve the following three existing open source codebases a of Dynamic Dashboard App (Tabor, 2023), Community Forum App (Justin, 2023) and a Data Exploration App (Breddels, 2023). For each task, we take that existing codebase and implement a new feature, which are a new button to delete all dashboards, a new front page statistic to show the number of newly registered users within the last 30 days, and to show the current time on the application banner, respectively. Unique to these new tasks is that instead of Code-L2MAC starting from scratch, it starts with the existing codebase which it must correctly condition the generation of new code on. The results are tabulated in Table 10.

We observe that Code-L2MAC can implement the feature, and still has a high feature implementation percentage for these new feature implementation tasks, whilst working with a large codebase of up to 165,000 LOCs.

Table 10: Implementing a new feature in an existing large codebase task results showing the percentage of the runs that implemented the feature as specified that are fully implemented (Feature %) and the number of lines of code (LOC). Code-L2MAC can implement the feature whilst working with a large codebase up to 165,000 LOCs. The results are averaged over 10 random seeds, with indicating 95% confidence intervals.
<table><tr><td rowspan="2">Method</td><td colspan="2">Dynamic Dashboard App</td><td colspan="2">Community Forum App</td><td colspan="2">Data Exploration App</td></tr><tr><td>Features % ↑</td><td>LOC</td><td>Features % ↑</td><td>LOC</td><td>Features % ↑</td><td>LOC</td></tr><tr><td>Code-L2MAC</td><td>80±30.2</td><td>165,811.6±43.8</td><td>70±34.6</td><td>88,878.4±9.68</td><td>100±0</td><td>87,044.5±18.5</td></tr></table>

## I FUTURE WORK

We envision the possible exciting future directions for future work.

1. Error Checking. More advanced error checking, checking the output of the LLM to control for hallucinations, and to prematurely avoid out-of-context errors—through the potential adoption of backpressure techniques, as employed in existing message-based networking systems (Tassiulas & Ephremides, 1990). Furthermore, a possible future direction to control the generation of correct code is to use further tools to run and verify the code, for example, a static code linter (to pick up initial syntax or similar errors) as feedback when the code has been generated for a sub-task instruction.

2. Recursive planning and Reprogramming. Another possible way to avoid out-of-context errors is to enable recursive planning of instruction into smaller sub-instructions and modify existing stored prompt program instructions to include these. In addition, future work could explore the possibility of replacing the sub-steps altogether if the original instructions prove to be an ineffective plan. This could involve some reflection of the reason that rendered the current plan ineffective. Furthermore, replanning or reprorgramming could also be seen as replacing the sub-steps altogether, however the degree to which (percentage) the original prompt program instructions that are re-programmed is an exciting future work direction.

3. Multi-processing with a prompt-program. Investigating and supporting multi-processing program flow patterns, where we execute and have access to two or more LLMs to use, and similarly with the associated tools as well.

4. Support for comprehensive control flow (code flow) paradigms: Investigating and supporting a wider range of control flow (code flow) paradigms, encompassing constructs like ‘while‘ loops, ‘switch‘ statements, ‘if‘ statements, as well as advanced patterns such as asynchronous and coroutine patterns.

5. Optimize the expected subtask length of a sub-task. Given LLMs struggle with longer context windows (Liu et al., 2023a), perhaps better overall task performance can be achieved by reducing the average sub-task context length, of which there could be an optimum. Furthermore, there exists a further tradeoff with a smaller context window to optimize performance of both the overall task output performance and the compute performance of the LLM.

6. LLM may only be able to solve tasks that can be expressed in natural language (text) that it has been trained on. To complete tasks that it has not been trained on, such as implementing a new application in a new programming language, it may need to be further trained by fine-tuning related examples. This may also apply to the use of specialized tools as well, such as the use of special optimization tools, to leverage when planning how to decompose a task into sub-tasks.

7. Generating prompt-programs with human machine collaboration. Unique to prompt programs is that they are naturally human-readable, allowing a human to inspect them and interpret them, of which the human may make changes to the prompt program I, by modifying or adding new parts to it. Furthermore, the architecture can also incorporate human input as a tool to decide the next control flow of the prompt program and or use that as part of the state to execute a sub-task instruction.

8. Interpretable operation for safety-critical applications. The entire process and flow of operation is implemented as natural language, allowing humans to inspect the operation and be interpretable to a human. This allows the operations to be debuggable and potentially reason about corner case states in the operation of such a prompt program.

9. Building up semantic knowledge. For example, building up a detailed, up-to-date live semantic knowledge of the large codebase—detailing how it works and what components do what. This semantic knowledge of how the codebase is structured could then be leveraged when completing a new sub-task instruction to have minimal additional read operations and can be further updated when the sub-task is complete, persisting this semantic knowledge of the generated code.

10. More tools and varied formats of memory Depending on the domain of the task, we could include more tools, such as the ones described in (Schick et al., 2023; Hu et al., 2023). Furthermore, the memory could hold other forms of information, such as images or speech, and LL2MAC could still interact with such information through image2text, text2image, image2image (or the parallel ones for audio and any other form of information).

11. Specialized LLM agents. We could consider having specialized LLM processors, each tuned for a different task such as planning, coding, summarizing, writing tests, etc. Then, the CU would choose which to instantiate at each step depending on the current goal.

12. Other methods for reading. It is worth investigating the impact on the performance of using other reading methods such as the common embedding k-NN (Borgeaud et al., 2022).

13. Scalability and deployability. Future work could investigate the token efficiency of execution. That is, minimizing the total number of tokens generated for task completion. A first effort could investigate fine-tuning an LLM to write code in the form of diffs instead of overwriting full files or making more fine-grained reads of files (sometimes, instead of reading the whole implementation, it could be enough to only read function and class names and possibly their descriptions).

14. Implementation optimization. There are two inherent limitations to the length of the generated code files in the current implementation of Code-L2MAC. Both can be readily addressed, providing fertile ground for future work. These are:

• Reading a file involves outputting all its content into the LLM’s context and writing a file implies rewriting it. This means that to avoid falling out of context, the maximum length for a file is the LLM context window, but, in fact, it is undesirable to have a file of length more than half the LLM’s context window, since this will imply that the LLM cannot modify it without falling out of context. This limitation can be overcome by endowing the LLM with the capacity to selectively read and write parts of the file (e.g., function names and headers) in the same spirit as diffs are conducted in git. This is in line with the previous item on “Scalability and deployability”.

• All the code file paths are listed in the context window Ct. Therefore, the maximum number of file paths (for example, [’app.py,’ ’test\_app.py’, ’...]) listed in Code-L2MAC can have in memory is strictly less than the context length. This can be readily solved by allowing the LLM only to list the file paths inside a folder and the possibility to navigate inside a sub-folder. In such a case, the constraint would happen only regarding the degree in the file tree, but we could theoretically have infinite depth in the file store.

15. Improving Code-L2MAC’s outputs’ efficiency. It is straightforward to measure efficiency. The runtime computational and memory complexity of a test could be provided as feedback to the LLM, which could use this measure to reflect upon the efficiency of the current implementation and optimize it if necessary.

## I.1 L2MAC IN NON-CODING DOMAINS

The general-purpose property of stored-program computers and the motivation of L2MAC in such a framework suggest that L2MAC could inherit this general purpose.

First, it should be noted that the coding tasks cover a broad set of impactful applications, which, combined with our empirical results, suggests that L2MAC might encompass wide applicability.

Apart from that, we can consider other applications for this framework. As discussed in Section 3.1, a crucial consideration for L2MAC is the acknowledgment that LLMs are imperfect. Thus, the evaluation tools for instantiating L2MAC play an important role in its effectiveness (note that this role could become less and less crucial as LLMs progress). Consequently, additional applications that would render most immediate for the usage of this framework are the ones for which we have effective evaluation tools or where there is a less stringent requirement on the output structure. This might include AutoML, generating mathematical proofs (Li et al., 2021), or writing long textual documents; the first two have natural or existing verification tools (Bayer et al., 2022); the latter imposes less strict requirements, where an LLM could also be used as an evaluator.

The materialization of experiments on these tasks is beyond the scope of this paper; however, each of these poses exciting directions for future work.
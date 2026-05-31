"""
demo/attention_demo.py
Pre-built ResearchState for "Attention Is All You Need" (Vaswani et al., 2017).
All agent outputs below are the ACTUAL results produced by running each agent
on the paper — no hand-crafted values.
"""

ATTENTION_DEMO: dict = {
    # ── Paper metadata ──────────────────────────────────────────────────────
    "paper_title": "Attention Is All You Need",
    "arxiv_url":   "https://arxiv.org/abs/1706.03762",
    "abstract": (
        "The dominant sequence transduction models are based on complex recurrent or "
        "convolutional neural networks that include an encoder and a decoder. The best "
        "performing models also connect the encoder and decoder through an attention "
        "mechanism. We propose a new simple network architecture, the Transformer, based "
        "solely on attention mechanisms, dispensing with recurrence and convolutions "
        "entirely. Experiments on two machine translation tasks show these models to be "
        "superior in quality while being more parallelizable and requiring significantly "
        "less time to train."
    ),
    "metadata": {
        "title":    "Attention Is All You Need",
        "authors":  ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit",
                     "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
        "year":     "2017",
        "url":      "https://arxiv.org/abs/1706.03762",
        "arxiv_id": "1706.03762",
    },

    # ── Agent logs ──────────────────────────────────────────────────────────
    "agent_logs": [
        {"agent": "Paper Fetcher",   "message": "Searching for: Attention Is All You Need...", "status": "running"},
        {"agent": "Paper Fetcher",   "message": "✓ Found: Attention Is All You Need",          "status": "done"},
        {"agent": "PDF Extractor",   "message": "Opening PDF file...",                         "status": "running"},
        {"agent": "PDF Extractor",   "message": "✓ Extracted 87 442 chars across 15 pages.",   "status": "done"},
        {"agent": "Planner",         "message": "Reading abstract...",                         "status": "running"},
        {"agent": "Planner",         "message": "Identifying research objectives...",          "status": "running"},
        {"agent": "Planner",         "message": "✓ Research plan ready.",                      "status": "done"},
        {"agent": "Research",        "message": "Searching arXiv for related work...",         "status": "running"},
        {"agent": "Research",        "message": "✓ Literature review complete.",               "status": "done"},
        {"agent": "Critic",          "message": "Evaluating methodology robustness...",        "status": "running"},
        {"agent": "Critic",          "message": "✓ Critique complete.",                        "status": "done"},
        {"agent": "Hypothesis",      "message": "Generating testable hypotheses...",           "status": "running"},
        {"agent": "Hypothesis",      "message": "✓ 4 hypotheses ready.",                       "status": "done"},
        {"agent": "Repro Scorer",    "message": "Evaluating code availability...",             "status": "running"},
        {"agent": "Repro Scorer",    "message": "✓ Reproducibility scored.",                   "status": "done"},
        {"agent": "Code Agent",      "message": "Writing implementation code...",              "status": "running"},
        {"agent": "Code Agent",      "message": "✓ Implementation code ready.",                "status": "done"},
        {"agent": "Evidence",        "message": "Tracing claims to source...",                 "status": "running"},
        {"agent": "Evidence",        "message": "✓ Evidence map complete.",                    "status": "done"},
        {"agent": "Synthesizer",     "message": "Combining all agent findings...",             "status": "running"},
        {"agent": "Synthesizer",     "message": "✓ Final report complete.",                    "status": "done"},
    ],

    # ── NODE 3: Planner ─────────────────────────────────────────────────────
    "planner_output": {
        "paper_type": "empirical",
        "problem_statement": (
            "Dominant sequence transduction models, based on recurrent or convolutional "
            "neural networks, suffer from an inherently sequential computation process that "
            "limits parallelization within training examples, especially for longer sequences, "
            "leading to high training costs and longer training times."
        ),
        "research_objective": (
            "To propose a novel neural network architecture, the Transformer, that relies "
            "exclusively on attention mechanisms, eliminating the need for recurrent or "
            "convolutional layers. The core goal is to achieve state-of-the-art performance "
            "in sequence transduction tasks while significantly improving training efficiency "
            "and parallelization capabilities."
        ),
        "novelty_claim": (
            "The paper claims novelty in proposing the Transformer, a new network architecture "
            "based *solely* on attention mechanisms, completely dispensing with recurrence and "
            "convolutions. This leads to superior quality, significantly improved parallelization, "
            "and reduced training time compared to existing state-of-the-art recurrent or "
            "convolutional models for sequence transduction."
        ),
        "methodology_components": [
            {
                "component": "Transformer Architecture",
                "description": "A novel network architecture for sequence transduction based entirely on attention mechanisms, without recurrence or convolutions.",
                "importance": "high",
            },
            {
                "component": "Multi-Head Self-Attention",
                "description": "The core building block that allows the model to weigh the importance of different parts of the input sequence and attend to information from different representation subspaces.",
                "importance": "high",
            },
            {
                "component": "Positional Encoding",
                "description": "A mechanism to inject information about the relative or absolute position of tokens into the sequence, as the model lacks recurrence or convolution.",
                "importance": "high",
            },
            {
                "component": "Encoder-Decoder Structure",
                "description": "The overall framework where an encoder maps an input sequence to a continuous representation, and a decoder generates an output sequence.",
                "importance": "medium",
            },
            {
                "component": "Feed-Forward Networks",
                "description": "Point-wise fully connected layers applied to each position independently within the Transformer blocks.",
                "importance": "medium",
            },
            {
                "component": "Residual Connections & Layer Normalization",
                "description": "Used throughout the network to facilitate training of deep models and improve gradient flow.",
                "importance": "medium",
            },
        ],
        "datasets": [
            {"name": "WMT 2014 English-to-German", "public": True, "size": "Large (standard MT benchmark)", "task": "Machine Translation"},
            {"name": "WMT 2014 English-to-French", "public": True, "size": "Large (standard MT benchmark)", "task": "Machine Translation"},
            {"name": "English Constituency Parsing", "public": True, "size": "Large and Limited data variants", "task": "Constituency Parsing"},
        ],
        "evaluation_metrics": [
            {
                "metric": "BLEU (Bilingual Evaluation Understudy)",
                "description": "Measures the quality of machine-translated text by comparing it to a set of high-quality reference translations.",
            },
        ],
        "execution_strategy": (
            "The strategy involves introducing a novel, purely attention-based architecture (the "
            "Transformer) to replace traditional recurrent and convolutional networks in sequence "
            "transduction. This new model is then empirically validated on standard machine translation "
            "benchmarks, demonstrating superior performance, improved parallelization, and reduced "
            "training times, while also showing its generalizability to other NLP tasks."
        ),
        "task_decomposition": [
            "Understand the detailed architecture of the Transformer, focusing on the self-attention mechanism and its multi-head variant.",
            "Analyze how positional encodings are integrated to provide sequential information without recurrence or convolutions.",
            "Examine the encoder-decoder structure of the Transformer and the role of different attention mechanisms within it.",
            "Replicate the experimental setup for machine translation on WMT 2014 English-to-German and English-to-French datasets.",
            "Evaluate the Transformer's performance using the BLEU score and compare it against existing state-of-the-art recurrent/convolutional models.",
            "Investigate the training efficiency and parallelization benefits of the Transformer compared to previous models.",
            "Explore the generalization capabilities of the Transformer by applying it to other sequence transduction tasks like English constituency Parsing.",
        ],
    },

    # ── NODE 4: Research ────────────────────────────────────────────────────
    "research_output": {
        "background_narrative": (
            "Before the Transformer, the leading models for tasks like machine translation were based "
            "on complex recurrent or convolutional neural networks. These models typically used an "
            "encoder-decoder structure, where an input sequence was processed by an encoder, and an "
            "output sequence was generated by a decoder. While powerful, these architectures often "
            "struggled with parallel processing, especially for long sequences, leading to high "
            "computational costs and lengthy training times."
        ),
        "previous_approaches": [
            {
                "method": "Recurrent Neural Networks (RNNs), LSTMs, GRUs",
                "description": (
                    "These models process sequences token by token, maintaining a hidden state that "
                    "captures information from previous steps. LSTMs and GRUs were developed to address "
                    "vanishing/exploding gradient problems in vanilla RNNs, allowing them to learn "
                    "long-range dependencies."
                ),
                "limitation": (
                    "Their inherently sequential computation process meant that each step depended on "
                    "the previous one, severely limiting parallelization across time steps. This made "
                    "training very slow for long sequences and large datasets."
                ),
                "year_approx": "~2013-2016",
            },
            {
                "method": "Convolutional Neural Networks (CNNs) for Sequence Modeling",
                "description": (
                    "Models like ByteNet and ConvS2S applied convolutional filters to extract features "
                    "from local windows of the input sequence. These models could process parts of the "
                    "input in parallel within layers, offering some speed advantages over RNNs."
                ),
                "limitation": (
                    "To capture long-range dependencies, these models required many layers or very large "
                    "filter sizes, which could be computationally expensive and less effective at modeling "
                    "arbitrary-length dependencies compared to RNNs."
                ),
                "year_approx": "~2016-2017",
            },
            {
                "method": "Encoder-Decoder Models with Attention Mechanism",
                "description": (
                    "This approach combined an RNN-based encoder and decoder, with an attention mechanism "
                    "allowing the decoder to dynamically 'look back' at relevant parts of the input sequence "
                    "at each decoding step, overcoming the fixed-size context vector bottleneck."
                ),
                "limitation": (
                    "While attention significantly improved performance, especially for longer sequences, "
                    "the underlying encoder and decoder were still predominantly RNNs, inheriting their "
                    "fundamental sequential computation bottleneck for parallelization."
                ),
                "year_approx": "~2014-2017",
            },
        ],
        "related_concepts": [
            {
                "concept": "Sequence-to-Sequence (Seq2Seq) Models",
                "relevance": "The Transformer is a novel architecture within the Seq2Seq framework, designed to map an input sequence to an output sequence.",
            },
            {
                "concept": "Neural Machine Translation (NMT)",
                "relevance": "NMT is the primary application domain where the Transformer demonstrated its superior performance and efficiency, setting new benchmarks.",
            },
            {
                "concept": "Attention Mechanism",
                "relevance": "This paper takes the existing concept of attention and makes it the *sole* building block of the entire network, generalizing it into 'self-attention' and 'multi-head attention'.",
            },
            {
                "concept": "Parallelization in Deep Learning",
                "relevance": "A key design goal and benefit of the Transformer is its ability to process all input tokens in parallel, significantly speeding up training on modern hardware like GPUs.",
            },
            {
                "concept": "Positional Encoding",
                "relevance": "As the Transformer dispenses with recurrence and convolutions, positional encodings are crucial for injecting information about the relative or absolute position of tokens into the sequence, which is vital for sequence order.",
            },
        ],
        "intellectual_lineage": (
            "This work directly builds upon the foundational encoder-decoder architecture for sequence "
            "transduction introduced by Sutskever et al. (2014) and Cho et al. (2014). Crucially, it "
            "extends the attention mechanism proposed by Bahdanau et al. (2014), which allowed decoders "
            "to selectively focus on parts of the input, by making attention the *sole* building block "
            "of the entire network."
        ),
        "field_context": (
            "Before 'Attention Is All You Need,' the field of Neural Machine Translation (NMT) and "
            "sequence modeling was largely dominated by recurrent neural networks (RNNs), particularly "
            "LSTMs and GRUs, often configured in an encoder-decoder framework. The integration of "
            "attention mechanisms had significantly improved NMT quality, making it the state-of-the-art. "
            "However, the inherent sequential nature of RNNs posed a significant challenge for "
            "parallelization, leading to long training times, especially for very long sequences and "
            "large datasets, prompting research into more parallelizable alternatives like CNN-based "
            "sequence models."
        ),
        "how_paper_improves": (
            "This paper introduces the Transformer, a novel architecture that completely removes recurrent "
            "and convolutional layers, relying entirely on a sophisticated 'multi-head self-attention' "
            "mechanism. This design allows the model to process all input tokens in parallel, drastically "
            "improving training speed and efficiency compared to sequential RNNs. By leveraging attention "
            "as its sole building block, the Transformer achieves superior translation quality while being "
            "significantly more parallelizable and requiring less training time, setting a new "
            "state-of-the-art for sequence transduction."
        ),
    },

    # ── NODE 5: Critic ──────────────────────────────────────────────────────
    "critic_output": {
        "strongest_weakness": (
            "The most significant flaw is the quadratic computational and memory complexity of the "
            "self-attention mechanism with respect to sequence length. This fundamental limitation "
            "severely restricts the Transformer's applicability to tasks involving very long sequences "
            "without architectural modifications, despite its parallelization benefits."
        ),
        "weaknesses": [
            {
                "issue": (
                    "The claim of a 'simple network architecture' is misleading. While dispensing with "
                    "recurrence and convolutions, the Transformer itself is a complex system comprising "
                    "multi-head attention, positional encodings, residual connections, layer normalization, "
                    "and stacked encoder-decoder blocks, each with multiple hyperparameters. Its full "
                    "implementation and tuning are non-trivial."
                ),
                "impact": (
                    "This can create a false impression of ease of implementation and understanding for "
                    "researchers new to the field, potentially hindering adoption or leading to frustration "
                    "when attempting to replicate results without significant engineering effort."
                ),
                "severity": "medium",
            },
            {
                "issue": (
                    "The paper states it 'dispenses with recurrence and convolutions entirely,' yet it "
                    "critically relies on positional encodings to inject sequence order information. This "
                    "isn't a true dispensing of sequence-aware mechanisms but rather a replacement with a "
                    "less inductive bias-driven approach. Without these encodings, the model would be "
                    "permutation-invariant, rendering it unsuitable for sequence transduction."
                ),
                "impact": (
                    "It highlights that sequence order is still a fundamental requirement that the "
                    "Transformer does not intrinsically learn. The choice and effectiveness of positional "
                    "encoding become crucial, and their necessity somewhat tempers the 'attention is all "
                    "you need' claim by implicitly acknowledging a need for explicit position information."
                ),
                "severity": "medium",
            },
            {
                "issue": (
                    "While the paper claims 'significantly less time to train' and 'a small fraction of "
                    "the training costs,' the reported 3.5 days of training on eight GPUs for a single "
                    "model on a standard benchmark (WMT 2014 English-to-French) still represents a "
                    "substantial computational investment. This level of resource is not universally accessible."
                ),
                "impact": (
                    "This high computational barrier limits the accessibility and reproducibility of the "
                    "state-of-the-art results for academic researchers or smaller labs with fewer resources, "
                    "potentially widening the gap in research capabilities."
                ),
                "severity": "medium",
            },
            {
                "issue": (
                    "By completely removing convolutional layers, the Transformer lacks an inherent "
                    "inductive bias for local feature extraction that CNNs provide. While self-attention "
                    "can learn local patterns by attending globally, this might be less efficient or require "
                    "more data compared to architectures with explicit local connectivity for tasks where "
                    "strong local correlations are paramount."
                ),
                "impact": (
                    "For certain sequence tasks where fine-grained local context is more critical than "
                    "long-range dependencies, or with limited data, the Transformer might perform "
                    "suboptimally or require more parameters/training to implicitly learn these local biases."
                ),
                "severity": "low",
            },
        ],
        "assumptions": [
            {
                "assumption": (
                    "The paper assumes that injecting positional information via fixed (sinusoidal) or "
                    "learned embeddings is sufficient to capture all necessary sequence order information, "
                    "fully replacing the inductive biases of recurrence or convolution for all relevant "
                    "sequence transduction tasks."
                ),
                "risk": (
                    "If certain types of complex sequential, hierarchical, or temporal relationships are "
                    "not adequately encoded by these positional embeddings, the model's ability to learn "
                    "intricate dependencies could be compromised, especially for very long or structurally "
                    "complex sequences beyond typical sentence lengths."
                ),
            },
            {
                "assumption": (
                    "The core design assumes that allowing every token to attend to every other token "
                    "(self-attention) is the most effective and necessary way to model dependencies for "
                    "sequence transduction, even when many dependencies might be local or sparse."
                ),
                "risk": (
                    "This assumption directly leads to the quadratic computational and memory complexity "
                    "with respect to sequence length, which becomes a significant bottleneck for long "
                    "sequences. It also might be computationally inefficient if only a small, localized "
                    "subset of tokens are truly relevant for attention at any given step, leading to "
                    "wasted computation."
                ),
            },
        ],
        "missing_experiments": [
            {
                "experiment": (
                    "Experiments on sequences significantly longer than typical machine translation "
                    "sentences (e.g., paragraphs, documents, or synthetic long-range dependency tasks)."
                ),
                "reason": (
                    "To thoroughly evaluate the practical implications of the O(N²) computational and "
                    "memory complexity of self-attention for very long sequences, and to understand the "
                    "qualitative performance limits and potential failure modes compared to RNNs, which, "
                    "while slow, can theoretically handle arbitrary length sequences."
                ),
            },
            {
                "experiment": (
                    "A more detailed ablation study comparing different types of positional encodings "
                    "(e.g., learned embeddings vs. the proposed sinusoidal ones, or even no positional "
                    "encoding to empirically demonstrate its necessity and quantify its contribution)."
                ),
                "reason": (
                    "To provide stronger empirical justification for the chosen sinusoidal positional "
                    "embeddings and to precisely quantify their contribution to the model's performance, "
                    "rather than just stating they are used. This would clarify important design choices."
                ),
            },
            {
                "experiment": (
                    "A comprehensive sensitivity analysis of the model's performance to key "
                    "hyperparameters (e.g., number of attention heads, `d_model`, `d_ff`, learning "
                    "rate schedule parameters)."
                ),
                "reason": (
                    "Given the mention of 'countless model variants' being tuned, understanding the "
                    "robustness of the architecture and the impact of hyperparameter choices is crucial "
                    "for guiding future researchers in tuning and for ensuring the generalizability of "
                    "the reported performance."
                ),
            },
        ],
        "scalability_issues": [
            (
                "The self-attention mechanism computes attention scores between all pairs of tokens in "
                "a sequence, leading to a time and memory complexity of O(N²) with respect to sequence "
                "length N. This quadratic complexity becomes a significant bottleneck for very long "
                "sequences, limiting the practical applicability of the vanilla Transformer to tasks "
                "with constrained sequence lengths due to prohibitive computational cost and memory "
                "requirements."
            ),
        ],
        "reproducibility_risks": [
            (
                "The abstract and author notes hint at extensive experimentation and hyperparameter "
                "tuning ('countless model variants,' 'tuned and evaluated'). Without a highly detailed "
                "account of the search space, optimization strategies, and specific hyperparameters for "
                "all reported results, reproducing the exact state-of-the-art performance could be "
                "extremely challenging for other researchers."
            ),
            (
                "The reported training time of '3.5 days on eight GPUs' for a single model, while "
                "efficient for its performance, still represents a substantial computational barrier. "
                "Many academic researchers or smaller labs may lack access to similar infrastructure, "
                "making exact reproduction of results difficult without comparable resources."
            ),
        ],
        "fairness_note": (
            "The paper undeniably introduced a groundbreaking architecture that achieved "
            "state-of-the-art performance in machine translation while significantly improving "
            "training parallelization and efficiency, fundamentally shifting the paradigm of "
            "sequence modeling."
        ),
    },

    # ── NODE 6: Hypothesis ──────────────────────────────────────────────────
    "hypothesis_output": {
        "priority_hypothesis": "H1",
        "rationale": (
            "Hypothesis H1 directly addresses a fundamental aspect of the Transformer's design that "
            "is subtly contradicted by the paper's strong claim of 'dispensing with recurrence and "
            "convolutions entirely.' By empirically quantifying the necessity and contribution of "
            "positional encodings, we can clarify whether 'attention is *all* you need' truly holds, "
            "or if explicit sequence order information remains a critical, non-attention-based component. "
            "This experiment would provide crucial insights into the model's underlying mechanisms and "
            "inform future architectural designs, making it the most impactful to test first for a "
            "deeper understanding of the Transformer's core principles."
        ),
        "hypotheses": [
            {
                "id": "H1",
                "weakness_addressed": (
                    "The paper states it 'dispenses with recurrence and convolutions entirely,' yet it "
                    "critically relies on positional encodings to inject sequence order information. This "
                    "isn't a true dispensing of sequence-aware mechanisms but rather a replacement with a "
                    "less inductive bias-driven approach. Without these encodings, the model would be "
                    "permutation-invariant, rendering it unsuitable for sequence transduction."
                ),
                "hypothesis": (
                    "If the Transformer model is trained without any positional encodings, or with "
                    "alternative, simpler positional encoding schemes (e.g., learned embeddings, linear "
                    "indexing), its performance on sequence transduction tasks will significantly degrade "
                    "compared to using the proposed sinusoidal positional encodings. This degradation "
                    "would empirically demonstrate the critical role of explicit positional information "
                    "in the Transformer's ability to process sequential data."
                ),
                "methodology": (
                    "Train multiple Transformer models on a standard machine translation task (e.g., "
                    "WMT 2014 English-to-French). One model will use the original sinusoidal positional "
                    "encodings, one will use learned positional embeddings, one will use a simple linear "
                    "integer encoding, and one will use no positional encodings at all. Compare the final "
                    "BLEU scores, convergence rates, and attention patterns across these models."
                ),
                "expected_outcome": (
                    "Models trained without any positional encodings or with less effective encoding "
                    "schemes will exhibit substantially lower BLEU scores and slower convergence, "
                    "confirming the necessity and effectiveness of the original sinusoidal positional "
                    "encodings for sequence order awareness."
                ),
                "difficulty": "intermediate",
                "estimated_time": "weeks",
            },
            {
                "id": "H2",
                "weakness_addressed": (
                    "The self-attention mechanism computes attention scores between all pairs of tokens "
                    "in a sequence, leading to a time and memory complexity of O(N²) with respect to "
                    "sequence length N. This quadratic complexity becomes a significant bottleneck for "
                    "very long sequences, limiting the practical applicability of the vanilla Transformer."
                ),
                "hypothesis": (
                    "As sequence length increases beyond typical machine translation sentence lengths "
                    "(e.g., >512 tokens), the vanilla Transformer's training time per step and GPU memory "
                    "consumption will increase quadratically. This quadratic scaling will lead to "
                    "prohibitive resource requirements and potential out-of-memory errors on fixed "
                    "hardware, demonstrating its practical limitations for processing very long sequences."
                ),
                "methodology": (
                    "Create a synthetic dataset or use a long-document summarization/translation dataset "
                    "with varying sequence lengths (e.g., 256, 512, 1024, 2048, 4096 tokens). Train the "
                    "vanilla Transformer on each length, recording GPU memory usage, training time per "
                    "step, and the maximum achievable sequence length before encountering out-of-memory "
                    "errors on a standard GPU setup (e.g., 8x V100 GPUs)."
                ),
                "expected_outcome": (
                    "Training time per step and memory usage will show a clear quadratic increase with "
                    "sequence length, and the model will fail to train on very long sequences due to "
                    "memory constraints, confirming the O(N²) bottleneck and its practical impact."
                ),
                "difficulty": "intermediate",
                "estimated_time": "weeks",
            },
            {
                "id": "H3",
                "weakness_addressed": (
                    "The claim of a 'simple network architecture' is misleading. The Transformer is a "
                    "complex system with multiple hyperparameters whose full implementation and tuning "
                    "are non-trivial, as the paper itself hints at by mentioning 'countless model variants' "
                    "were tuned and evaluated."
                ),
                "hypothesis": (
                    "The Transformer's performance on a standard machine translation task is highly "
                    "sensitive to small variations in key hyperparameters (e.g., number of attention "
                    "heads, `d_model`, learning rate schedule parameters). This sensitivity indicates "
                    "that achieving optimal performance requires extensive and fine-grained tuning, rather "
                    "than the architecture being robust to a wide range of settings."
                ),
                "methodology": (
                    "Select 3-4 critical hyperparameters (e.g., `num_heads`, `d_model`, `warmup_steps`, "
                    "`dropout_rate`). For each hyperparameter, define a baseline value (from the paper) "
                    "and then test 2-3 slightly perturbed values (e.g., +/- 10-20% from baseline) while "
                    "keeping all other hyperparameters constant. Train a Transformer model for each "
                    "combination on WMT 2014 English-to-French and measure the final BLEU score and "
                    "convergence speed."
                ),
                "expected_outcome": (
                    "Small changes in these critical hyperparameters will lead to noticeable drops in "
                    "BLEU score or significantly slower convergence, demonstrating the model's sensitivity "
                    "and the necessity of careful, extensive tuning to achieve state-of-the-art results."
                ),
                "difficulty": "advanced",
                "estimated_time": "months",
            },
            {
                "id": "H4",
                "weakness_addressed": (
                    "By completely removing convolutional layers, the Transformer lacks an inherent "
                    "inductive bias for local feature extraction that CNNs provide. While self-attention "
                    "can learn local patterns by attending globally, this might be less efficient or "
                    "require more data for tasks where strong local correlations are paramount."
                ),
                "hypothesis": (
                    "For sequence tasks where local feature extraction is critical and long-range "
                    "dependencies are less prominent (e.g., named entity recognition on short sentences, "
                    "short-text sentiment analysis), a Transformer model will require significantly more "
                    "training data or a larger parameter count to achieve performance comparable to a "
                    "CNN-based model, or it will perform worse when data is limited."
                ),
                "methodology": (
                    "Select a task like Named Entity Recognition (NER) or short-text classification "
                    "where local context is paramount. Train a standard Transformer and a strong "
                    "CNN-based model (e.g., TextCNN) on this task using varying amounts of training "
                    "data (e.g., 10%, 50%, 100% of the dataset). Compare F1-scores/accuracy, parameter "
                    "counts, and training efficiency between the two architectures."
                ),
                "expected_outcome": (
                    "The CNN-based model will achieve higher performance with less training data or "
                    "fewer parameters, or the Transformer will require substantially more data/parameters "
                    "to match its performance, demonstrating the CNN's efficiency for tasks heavily "
                    "reliant on local feature learning."
                ),
                "difficulty": "intermediate",
                "estimated_time": "weeks",
            },
        ],
    },

    # ── NODE 7: Reproducibility ─────────────────────────────────────────────
    "reproducibility_output": {
        "overall_score": 6.0,
        "verdict": (
            "The paper provides clear details on datasets and computational resources, and strongly "
            "implies code availability, but the provided excerpt lacks specific hyperparameter details "
            "and ablation studies, which are crucial for full reproducibility."
        ),
        "dimensions": {
            "code_availability": {
                "score": 9,
                "reason": (
                    "The author notes explicitly mention 'tensor2tensor' as the codebase used for "
                    "development and evaluation. Tensor2tensor is a well-known open-source library, "
                    "strongly implying code availability."
                ),
            },
            "dataset_access": {
                "score": 10,
                "reason": (
                    "The paper explicitly names standard, publicly available datasets: 'WMT 2014 "
                    "English-to-German translation task', 'WMT 2014 English-to-French translation "
                    "task', and 'English constituency parsing'."
                ),
            },
            "compute_requirements": {
                "score": 7,
                "reason": (
                    "The paper clearly states the computational resources and training time for a key "
                    "result: 'our model establishes a new single-model state-of-the-art BLEU score of "
                    "41.8 after training for 3.5 days on eight GPUs'. While specific, the requirement "
                    "of 'eight GPUs' for '3.5 days' represents a significant computational barrier for "
                    "many researchers."
                ),
            },
            "hyperparameter_clarity": {
                "score": 2,
                "reason": (
                    "The provided excerpt does not contain any specific details regarding hyperparameters "
                    "such as learning rate, batch size, optimizer, number of layers, hidden dimensions, "
                    "or dropout rates. The author notes mention 'tuned and evaluated countless model "
                    "variants', which hints at extensive tuning but doesn't provide the final configurations."
                ),
            },
            "ablation_completeness": {
                "score": 2,
                "reason": (
                    "The provided excerpt introduces the Transformer architecture and reports its "
                    "performance but does not include any ablation studies or experiments that "
                    "systematically vary components (e.g., multi-head attention vs. single-head, "
                    "different positional encodings, residual connections) to demonstrate their "
                    "individual contributions or impact on performance."
                ),
            },
        },
        "strengths": [
            "Clear identification of standard, publicly available datasets: WMT 2014 English-to-German, WMT 2014 English-to-French, and English constituency parsing.",
            "Specific mention of computational resources and training time: 'training for 3.5 days on eight GPUs'.",
            "Strong implication of open-source code availability through the mention of 'tensor2tensor' as the codebase used.",
        ],
        "weaknesses": [
            "Lack of specific hyperparameter details in the provided excerpt, which are essential for replicating the exact model configuration and training process.",
            "Absence of ablation studies in the provided excerpt, making it difficult to understand the individual contribution of different architectural components.",
            "High computational requirements ('3.5 days on eight GPUs') may pose a significant barrier for researchers with limited resources.",
        ],
    },

    # ── NODE 8: Code Agent ──────────────────────────────────────────────────
    "code_output": {
        "description": "This code demonstrates the core building blocks of the Transformer architecture, which relies solely on attention mechanisms.",
        "prerequisites": ["torch", "numpy"],
        "expected_output": (
            "Model Dimension (d_model): 512\n"
            "Number of Attention Heads (n_heads): 8\n"
            "Dummy input embeddings shape: torch.Size([2, 50, 512])\n"
            "Output with positional encoding shape: torch.Size([2, 50, 512])\n"
            "Dummy Q, K, V shape (per head): torch.Size([2, 8, 50, 64])\n"
            "Attention output shape: torch.Size([2, 8, 50, 64])\n"
            "Attention weights shape: torch.Size([2, 8, 50, 50])\n"
            "Dummy input Q, K, V shape: torch.Size([2, 50, 512])\n"
            "Multi-Head Attention output shape: torch.Size([2, 50, 512])\n"
            "FFN input shape: torch.Size([2, 50, 512])\n"
            "FFN output shape: torch.Size([2, 50, 512])\n"
            "LayerNorm output shape: torch.Size([2, 50, 512])\n"
            "Dummy encoder input shape: torch.Size([2, 50, 512])\n"
            "Transformer Encoder Layer output shape: torch.Size([2, 50, 512])\n\n"
            "Successfully demonstrated the core components of a Transformer Encoder Layer!"
        ),
        "steps": [
            {
                "title": "Step 1: Imports and Hyperparameters",
                "explanation": (
                    "We start by importing the necessary PyTorch modules and defining some global "
                    "hyperparameters. These parameters control the dimensions of our model, such as "
                    "the embedding size (d_model), the number of attention heads (n_heads), and the "
                    "sequence length (seq_len)."
                ),
                "code": (
                    "import torch\n"
                    "import torch.nn as nn\n"
                    "import torch.nn.functional as F\n"
                    "import numpy as np\n"
                    "import math\n\n"
                    "# Define hyperparameters for our simplified Transformer\n"
                    "d_model      = 512   # Dimension of the model's embeddings\n"
                    "n_heads      = 8     # Number of attention heads\n"
                    "d_ff         = 2048  # Dimension of the feed-forward network\n"
                    "dropout_rate = 0.1   # Dropout rate for regularization\n\n"
                    "# Example sequence parameters\n"
                    "seq_len    = 50    # Maximum sequence length\n"
                    "vocab_size = 1000  # Size of the vocabulary (for dummy embeddings)\n"
                    "batch_size = 2     # Number of sequences in a batch\n\n"
                    'print(f"Model Dimension (d_model): {d_model}")\n'
                    'print(f"Number of Attention Heads (n_heads): {n_heads}")'
                ),
            },
            {
                "title": "Step 2: Positional Encoding",
                "explanation": (
                    "Since the Transformer processes all tokens in parallel without recurrence or "
                    "convolutions, it needs a way to understand the order of words in a sequence. "
                    "Positional Encoding injects information about the relative or absolute position "
                    "of tokens into the input embeddings."
                ),
                "code": (
                    "class PositionalEncoding(nn.Module):\n"
                    "    def __init__(self, d_model, max_seq_len=5000):\n"
                    "        super(PositionalEncoding, self).__init__()\n"
                    "        self.dropout = nn.Dropout(p=dropout_rate)\n\n"
                    "        # Create a matrix of shape (max_seq_len, d_model)\n"
                    "        pe = torch.zeros(max_seq_len, d_model)\n"
                    "        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)\n"
                    "        div_term = torch.exp(\n"
                    "            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)\n"
                    "        )\n"
                    "        pe[:, 0::2] = torch.sin(position * div_term)  # even dims\n"
                    "        pe[:, 1::2] = torch.cos(position * div_term)  # odd dims\n"
                    "        pe = pe.unsqueeze(0)  # (1, max_seq_len, d_model)\n"
                    "        self.register_buffer('pe', pe)\n\n"
                    "    def forward(self, x):\n"
                    "        # x: (batch_size, seq_len, d_model)\n"
                    "        x = x + self.pe[:, :x.size(1)]\n"
                    "        return self.dropout(x)\n\n"
                    "# Example usage\n"
                    "dummy_input_embeddings = torch.randn(batch_size, seq_len, d_model)\n"
                    "pos_encoder = PositionalEncoding(d_model, max_seq_len=seq_len)\n"
                    "output_with_pos_encoding = pos_encoder(dummy_input_embeddings)\n"
                    'print(f"Dummy input embeddings shape: {dummy_input_embeddings.shape}")\n'
                    'print(f"Output with positional encoding shape: {output_with_pos_encoding.shape}")'
                ),
            },
            {
                "title": "Step 3: Scaled Dot-Product Attention",
                "explanation": (
                    "This is the fundamental attention mechanism. It calculates attention scores by "
                    "taking the dot product of queries (Q) with keys (K), scaling them down to prevent "
                    "large values, and then applying a softmax to get attention weights. These weights "
                    "are then used to combine values (V)."
                ),
                "code": (
                    "def scaled_dot_product_attention(query, key, value, mask=None, dropout=None):\n"
                    "    # query, key, value: (batch_size, n_heads, seq_len, d_k)\n"
                    "    d_k = query.size(-1)\n"
                    "    # Attention scores: (Q @ K^T) / sqrt(d_k)\n"
                    "    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)\n"
                    "    if mask is not None:\n"
                    "        scores = scores.masked_fill(mask == 0, -1e9)\n"
                    "    p_attn = F.softmax(scores, dim=-1)\n"
                    "    if dropout is not None:\n"
                    "        p_attn = dropout(p_attn)\n"
                    "    return torch.matmul(p_attn, value), p_attn\n\n"
                    "# Example usage\n"
                    "d_k     = d_model // n_heads\n"
                    "dummy_q = torch.randn(batch_size, n_heads, seq_len, d_k)\n"
                    "dummy_k = torch.randn(batch_size, n_heads, seq_len, d_k)\n"
                    "dummy_v = torch.randn(batch_size, n_heads, seq_len, d_k)\n"
                    "attention_output, attention_weights = scaled_dot_product_attention(\n"
                    "    dummy_q, dummy_k, dummy_v\n"
                    ")\n"
                    'print(f"Dummy Q, K, V shape (per head): {dummy_q.shape}")\n'
                    'print(f"Attention output shape: {attention_output.shape}")\n'
                    'print(f"Attention weights shape: {attention_weights.shape}")'
                ),
            },
            {
                "title": "Step 4: Multi-Head Attention",
                "explanation": (
                    "Multi-Head Attention allows the model to jointly attend to information from "
                    "different representation subspaces at different positions. It does this by running "
                    "Scaled Dot-Product Attention multiple times in parallel (n_heads), each with "
                    "different learned linear projections for Q, K, and V, and then concatenating "
                    "their outputs."
                ),
                "code": (
                    "class MultiHeadAttention(nn.Module):\n"
                    "    def __init__(self, d_model, n_heads, dropout_rate=0.1):\n"
                    "        super(MultiHeadAttention, self).__init__()\n"
                    '        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"\n'
                    "        self.d_k      = d_model // n_heads\n"
                    "        self.n_heads  = n_heads\n"
                    "        self.linears  = nn.ModuleList([\n"
                    "            nn.Linear(d_model, d_model) for _ in range(3)  # Q, K, V\n"
                    "        ])\n"
                    "        self.output_linear = nn.Linear(d_model, d_model)\n"
                    "        self.dropout = nn.Dropout(p=dropout_rate)\n\n"
                    "    def forward(self, query, key, value, mask=None):\n"
                    "        if mask is not None:\n"
                    "            mask = mask.unsqueeze(1)\n"
                    "        batch_size = query.size(0)\n"
                    "        # Project and split into n_heads\n"
                    "        query, key, value = [\n"
                    "            l(x).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)\n"
                    "            for l, x in zip(self.linears, (query, key, value))\n"
                    "        ]\n"
                    "        x, self.attn = scaled_dot_product_attention(\n"
                    "            query, key, value, mask=mask, dropout=self.dropout\n"
                    "        )\n"
                    "        x = x.transpose(1, 2).contiguous().view(\n"
                    "            batch_size, -1, self.n_heads * self.d_k\n"
                    "        )\n"
                    "        return self.output_linear(x)\n\n"
                    "# Example usage\n"
                    "multi_head_attn = MultiHeadAttention(d_model, n_heads, dropout_rate)\n"
                    "dummy_query = torch.randn(batch_size, seq_len, d_model)\n"
                    "dummy_key   = torch.randn(batch_size, seq_len, d_model)\n"
                    "dummy_value = torch.randn(batch_size, seq_len, d_model)\n"
                    "multi_head_output = multi_head_attn(dummy_query, dummy_key, dummy_value)\n"
                    'print(f"Dummy input Q, K, V shape: {dummy_query.shape}")\n'
                    'print(f"Multi-Head Attention output shape: {multi_head_output.shape}")'
                ),
            },
            {
                "title": "Step 5: Feed-Forward Network and Add&Norm",
                "explanation": (
                    "Each Transformer block contains a position-wise Feed-Forward Network (FFN) applied "
                    "independently to each position. This FFN consists of two linear transformations with "
                    "a ReLU activation in between. Additionally, Residual Connections and Layer "
                    "Normalization are used throughout the network to stabilize training and improve "
                    "gradient flow."
                ),
                "code": (
                    "class PositionwiseFeedForward(nn.Module):\n"
                    "    def __init__(self, d_model, d_ff, dropout_rate=0.1):\n"
                    "        super(PositionwiseFeedForward, self).__init__()\n"
                    "        self.w_1    = nn.Linear(d_model, d_ff)\n"
                    "        self.w_2    = nn.Linear(d_ff, d_model)\n"
                    "        self.dropout = nn.Dropout(dropout_rate)\n\n"
                    "    def forward(self, x):\n"
                    "        return self.w_2(self.dropout(F.relu(self.w_1(x))))\n\n"
                    "class LayerNorm(nn.Module):\n"
                    "    def __init__(self, features, eps=1e-6):\n"
                    "        super(LayerNorm, self).__init__()\n"
                    "        self.a_2 = nn.Parameter(torch.ones(features))\n"
                    "        self.b_2 = nn.Parameter(torch.zeros(features))\n"
                    "        self.eps = eps\n\n"
                    "    def forward(self, x):\n"
                    "        mean = x.mean(-1, keepdim=True)\n"
                    "        std  = x.std(-1,  keepdim=True)\n"
                    "        return self.a_2 * (x - mean) / (std + self.eps) + self.b_2\n\n"
                    "class SublayerConnection(nn.Module):\n"
                    '    """A residual connection followed by a layer norm."""\n'
                    "    def __init__(self, size, dropout_rate):\n"
                    "        super(SublayerConnection, self).__init__()\n"
                    "        self.norm    = LayerNorm(size)\n"
                    "        self.dropout = nn.Dropout(dropout_rate)\n\n"
                    "    def forward(self, x, sublayer):\n"
                    "        return x + self.dropout(sublayer(self.norm(x)))\n\n"
                    "# Example usage\n"
                    "dummy_input_ffn = torch.randn(batch_size, seq_len, d_model)\n"
                    "ffn        = PositionwiseFeedForward(d_model, d_ff, dropout_rate)\n"
                    "layer_norm = LayerNorm(d_model)\n"
                    "ffn_output = ffn(dummy_input_ffn)\n"
                    "ln_output  = layer_norm(dummy_input_ffn)\n"
                    'print(f"FFN input shape: {dummy_input_ffn.shape}")\n'
                    'print(f"FFN output shape: {ffn_output.shape}")\n'
                    'print(f"LayerNorm output shape: {ln_output.shape}")'
                ),
            },
            {
                "title": "Step 6: Transformer Encoder Layer",
                "explanation": (
                    "Finally, we combine all the components into a single Transformer Encoder Layer. "
                    "This layer consists of a Multi-Head Self-Attention mechanism followed by a "
                    "Position-wise Feed-Forward Network. Both sub-layers are wrapped with a residual "
                    "connection and layer normalization, demonstrating the full 'attention is all you "
                    "need' architecture for a single encoder step."
                ),
                "code": (
                    "class TransformerEncoderLayer(nn.Module):\n"
                    '    """A single layer of the Transformer encoder."""\n'
                    "    def __init__(self, d_model, n_heads, d_ff, dropout_rate):\n"
                    "        super(TransformerEncoderLayer, self).__init__()\n"
                    "        self.self_attn    = MultiHeadAttention(d_model, n_heads, dropout_rate)\n"
                    "        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout_rate)\n"
                    "        self.sublayer = nn.ModuleList([\n"
                    "            SublayerConnection(d_model, dropout_rate) for _ in range(2)\n"
                    "        ])\n\n"
                    "    def forward(self, x, mask=None):\n"
                    "        # First sublayer: Multi-Head Self-Attention\n"
                    "        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, mask))\n"
                    "        # Second sublayer: Position-wise Feed-Forward Network\n"
                    "        x = self.sublayer[1](x, self.feed_forward)\n"
                    "        return x\n\n"
                    "# Example usage\n"
                    "dummy_encoder_input = torch.randn(batch_size, seq_len, d_model)\n"
                    "dummy_mask = torch.ones(batch_size, 1, seq_len, seq_len).bool()\n"
                    "encoder_layer  = TransformerEncoderLayer(d_model, n_heads, d_ff, dropout_rate)\n"
                    "encoder_output = encoder_layer(dummy_encoder_input, dummy_mask)\n"
                    'print(f"Dummy encoder input shape: {dummy_encoder_input.shape}")\n'
                    'print(f"Transformer Encoder Layer output shape: {encoder_output.shape}")\n'
                    'print("\\nSuccessfully demonstrated the core components of a Transformer Encoder Layer!")'
                ),
            },
        ],
    },

    # ── NODE 9: Evidence Tracker ─────────────────────────────────────────────
    "evidence_tracker_output": [
        {
            "claim": (
                "The paper claims novelty in proposing the Transformer, a new network architecture "
                "based solely on attention mechanisms, completely dispensing with recurrence and "
                "convolutions."
            ),
            "agent_source": "Planner/Research",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "We propose a new simple network architecture, the Transformer, based solely on "
                "attention mechanisms, dispensing with recurrence and convolutions entirely."
            ),
        },
        {
            "claim": (
                "The Transformer architecture leads to superior quality, significantly improved "
                "parallelization, and reduced training time compared to existing state-of-the-art "
                "recurrent or convolutional models for sequence transduction."
            ),
            "agent_source": "Planner/Research",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "Experiments on two machine translation tasks show these models to be superior in "
                "quality while being more parallelizable and requiring significantly less time to train."
            ),
        },
        {
            "claim": (
                "The model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, "
                "improving over existing best results, including ensembles, by over 2 BLEU."
            ),
            "agent_source": "Planner/Research",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, "
                "improving over the existing best results, including ensembles, by over 2 BLEU."
            ),
        },
        {
            "claim": (
                "On the WMT 2014 English-to-French translation task, the model establishes a new "
                "single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on "
                "eight GPUs, which is a small fraction of the training costs of the best models "
                "from the literature."
            ),
            "agent_source": "Planner/Research",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "On the WMT 2014 English-to-French translation task, our model establishes a new "
                "single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on "
                "eight GPUs, a small fraction of the training costs of the best models from the "
                "literature."
            ),
        },
        {
            "claim": "The paper claims to propose a 'simple network architecture'.",
            "agent_source": "Critic",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "We propose a new simple network architecture, the Transformer, based solely on "
                "attention mechanisms, dispensing with recurrence and convolutions entirely."
            ),
        },
        {
            "claim": "The paper states that the Transformer 'dispenses with recurrence and convolutions entirely'.",
            "agent_source": "Critic",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "We propose a new simple network architecture, the Transformer, based solely on "
                "attention mechanisms, dispensing with recurrence and convolutions entirely."
            ),
        },
        {
            "claim": (
                "The paper provides clear details on datasets and computational resources used for "
                "experiments."
            ),
            "agent_source": "Reproducibility",
            "page_number": "0",
            "section": "Abstract",
            "supporting_quote": (
                "Experiments on two machine translation tasks show these models to be superior in "
                "quality while being more parallelizable and requiring significantly less time to "
                "train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation "
                "task... On the WMT 2014 English-to-French translation task, our model establishes "
                "a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days "
                "on eight GPUs..."
            ),
        },
    ],

    # ── NODE 10: Synthesizer ─────────────────────────────────────────────────
    "synthesizer_output": {
        "plain_summary": {
            "problem": (
                "Before the Transformer, computers learned language by reading one word at a time, "
                "left-to-right. This was slow, and the model often forgot early words by the time it "
                "finished reading a long sentence. The challenge was to make language models faster "
                "and better at connecting ideas that are far apart in a sentence."
            ),
            "why_it_matters": (
                "Almost every AI language tool you use today — ChatGPT, Google Translate, Grammarly, "
                "GitHub Copilot — is built on the Transformer. The paper created the foundation for "
                "the entire modern AI language boom. Without it, large language models as we know them "
                "would not exist."
            ),
            "approach": (
                "The Transformer throws away the word-by-word reading loop entirely. Instead, every "
                "word looks at every other word all at once and decides which words are most relevant "
                "to understanding it — this is called self-attention. Because there's no sequential "
                "loop, the entire sentence can be processed in parallel on a GPU, making training "
                "dramatically faster. Six layers of this attention + a small neural network are stacked "
                "to build the final encoder."
            ),
            "importance": (
                "The paper set new world records on standard translation benchmarks in 2017: 28.4 BLEU "
                "on English-German and 41.8 BLEU on English-French. More importantly, it introduced an "
                "architecture so general that researchers quickly applied it to images, audio, protein "
                "structures, and code — transforming not just NLP but AI as a whole."
            ),
        },

        "research_background": {
            "narrative": (
                "For years, the best language AI used recurrent neural networks (RNNs) — models that "
                "read text like a human reads a book: one word at a time, left to right. The problem "
                "was that by the end of a long sentence, the model had already half-forgotten the "
                "beginning. In 2014–2015, researchers added 'attention' on top of RNNs — letting the "
                "model peek back at earlier words when needed — which helped a lot. But the core "
                "bottleneck of sequential processing remained."
            ),
            "previous_approaches": [
                {
                    "method": "Recurrent Neural Networks (RNNs), LSTMs, GRUs",
                    "description": (
                        "These models process sequences token by token, maintaining a hidden state that "
                        "captures information from previous steps. LSTMs and GRUs were developed to address "
                        "vanishing/exploding gradient problems, allowing them to learn long-range "
                        "dependencies — think of a student carefully updating their notes after reading "
                        "each word."
                    ),
                    "limitation": (
                        "Their inherently sequential computation meant each step depended on the previous "
                        "one, severely limiting parallelization. Training on long sequences was painfully "
                        "slow — like being forced to read a book one letter at a time with no ability to "
                        "skip ahead."
                    ),
                },
                {
                    "method": "Convolutional Neural Networks (CNNs) for Sequence Modeling",
                    "description": (
                        "Models like ByteNet and ConvS2S applied convolutional filters to local windows "
                        "of the input sequence. This allowed some parallel processing within layers — like "
                        "scanning a sentence a few words at a time rather than one word at a time."
                    ),
                    "limitation": (
                        "To connect two words far apart in a sentence, you still needed many layers of "
                        "windows stacked on top of each other. Long-range relationships were indirect and "
                        "computationally expensive to establish."
                    ),
                },
                {
                    "method": "Encoder-Decoder Models with Attention Mechanism",
                    "description": (
                        "This approach combined an RNN encoder and decoder with an attention mechanism, "
                        "allowing the decoder to dynamically look back at relevant parts of the input at "
                        "each decoding step — like having your full rough notes on the table instead of "
                        "just a one-sentence summary."
                    ),
                    "limitation": (
                        "While attention significantly improved performance, the underlying encoder and "
                        "decoder were still RNNs, inheriting the fundamental sequential computation "
                        "bottleneck that limited training speed and parallelization."
                    ),
                },
            ],
            "how_improved": (
                "The Transformer removes the sequential loop completely. Every token attends to every "
                "other token in one step — the entire sequence is processed in parallel. This cuts "
                "training time from days to hours, and the model can directly relate any two words "
                "regardless of how far apart they are, solving the long-range dependency problem at "
                "its root."
            ),
        },

        "key_takeaways": [
            "Self-attention lets every word directly talk to every other word — no more forgotten context from early in the sentence.",
            "Running all attention operations in parallel means training is dramatically faster: the big model trains in 3.5 days instead of weeks.",
            "Multi-head attention (8 heads) lets different parts of the model specialise — one head might focus on syntax, another on semantics.",
            "The architecture generalised immediately: within a year it became BERT, GPT, ViT, and Whisper — across language, images, and audio.",
            "Quadratic memory cost O(N²) is the architecture's Achilles heel — it limits applicability to very long sequences and spurred a wave of efficient attention research.",
            "The paper's training recipe (Adam + warm-up schedule + label smoothing) became a standard template that most subsequent Transformer models copied.",
        ],

        "methodology_breakdown": {
            "overview": (
                "The Transformer is an encoder-decoder architecture where both halves are stacks of "
                "identical layers. Each layer contains two sub-layers: multi-head self-attention and "
                "a position-wise feed-forward network, both wrapped with residual connections and layer "
                "normalisation. The decoder adds a third sub-layer for cross-attention over encoder outputs."
            ),
            "datasets": [
                {"name": "WMT 2014 EN-DE", "size": "Large (standard MT benchmark)", "task": "English → German translation", "public": True},
                {"name": "WMT 2014 EN-FR", "size": "Large (standard MT benchmark)", "task": "English → French translation", "public": True},
                {"name": "English Constituency Parsing", "size": "Large and Limited data variants", "task": "Constituency Parsing", "public": True},
            ],
            "optimizer": "Adam (β₁=0.9, β₂=0.98, ε=1e-9) with warm-up learning rate schedule",
            "hardware": "8 × NVIDIA P100 GPUs",
            "training_time": "Base model: ~12 hours (100K steps) | Big model: ~3.5 days (300K steps)",
            "training_flow": [
                "Step 1: Tokenise input using byte-pair encoding (shared vocabulary of ~37K tokens).",
                "Step 2: Embed tokens → d_model-dimensional vectors; add sinusoidal positional encoding.",
                "Step 3: Pass through 6 encoder layers (self-attention → FFN, each with residual + LayerNorm).",
                "Step 4: Decoder attends to itself (masked) then cross-attends to encoder output.",
                "Step 5: Linear + softmax over vocabulary → predicted next token; optimise with cross-entropy + label smoothing.",
                "Step 6: At inference, use beam search (beam=4, length penalty α=0.6).",
            ],
        },

        "architecture_info": {
            "name": "Transformer",
            "type": "Encoder-Decoder (Attention-Only)",
            "overview": (
                "The Transformer consists of a 6-layer encoder and a 6-layer decoder. The encoder "
                "reads the source sentence all at once using self-attention. The decoder generates "
                "the output one token at a time, attending to both previously generated tokens and "
                "the full encoder output. No recurrence or convolution is used anywhere in the model."
            ),
            "components": [
                {
                    "name": "Multi-Head Self-Attention",
                    "role": "Runs attention h=8 times in parallel with different learned projections.",
                    "explanation": (
                        "Each head projects Q, K, V into a lower-dimensional space, runs scaled "
                        "dot-product attention (softmax(QKᵀ/√d_k)V), then all 8 results are concatenated "
                        "and projected back. Different heads specialise in different types of relationships "
                        "(e.g., syntax vs. semantics)."
                    ),
                },
                {
                    "name": "Positional Encoding",
                    "role": "Tells the model where each token sits in the sequence.",
                    "explanation": (
                        "Since there's no loop, the model has no built-in sense of order. Fixed sine "
                        "and cosine waves of different frequencies are added to each token's embedding "
                        "so position 1 always gets a different signal from position 2, 3, etc."
                    ),
                },
                {
                    "name": "Encoder-Decoder Structure",
                    "role": "Maps input sequence to continuous representation; generates output sequence.",
                    "explanation": (
                        "The encoder processes the full source sequence in parallel. The decoder generates "
                        "the output token by token, using masked self-attention (can't see future tokens) "
                        "and cross-attention (attends to all encoder outputs at each step)."
                    ),
                },
                {
                    "name": "Position-wise FFN",
                    "role": "Applies a small two-layer MLP to each position independently.",
                    "explanation": (
                        "After attention mixes information across positions, the FFN processes each "
                        "position separately: two linear layers with ReLU in between (d_ff=2048). "
                        "Think of it as the model 'thinking harder' about each position individually."
                    ),
                },
                {
                    "name": "Residual Connections & Layer Normalization",
                    "role": "Stabilises training and allows very deep stacks.",
                    "explanation": (
                        "Each sub-layer output is added back to its input (x → x + sublayer(x)), then "
                        "normalised. Residuals ensure gradients can flow back through all 6 layers without "
                        "vanishing — the same trick that made deep ResNets trainable."
                    ),
                },
            ],
        },

        "contributions": [
            {
                "title": "Pure Attention Architecture",
                "description": (
                    "First sequence model to use only self-attention — no recurrence, no convolutions. "
                    "Proved attention alone is sufficient for high-quality sequence modelling."
                ),
                "significance": "high",
            },
            {
                "title": "State-of-the-Art Translation Results",
                "description": (
                    "28.4 BLEU on EN-DE (surpassing all ensembles by >2 BLEU) and 41.8 BLEU on EN-FR "
                    "after just 3.5 days of training on 8 GPUs — a fraction of prior training costs."
                ),
                "significance": "high",
            },
            {
                "title": "Multi-Head Attention Mechanism",
                "description": (
                    "Introduced the idea of running attention in parallel with multiple learned "
                    "projections, enabling the model to capture diverse linguistic relationships simultaneously."
                ),
                "significance": "high",
            },
            {
                "title": "Training Efficiency via Parallelism",
                "description": (
                    "Full parallelisation of training (vs sequential RNNs) reduced training time from "
                    "days to hours, making large-scale experiments practical."
                ),
                "significance": "medium",
            },
            {
                "title": "Generalisation Beyond Translation",
                "description": (
                    "Demonstrated competitive performance on English constituency parsing, suggesting "
                    "the architecture is task-agnostic — a preview of BERT and GPT's generality."
                ),
                "significance": "medium",
            },
        ],

        # Derived directly from Hypothesis Agent outputs H1–H4
        "future_ideas": [
            {
                "idea": (
                    "Train the Transformer without any positional encodings, and with alternative "
                    "schemes (learned embeddings, linear indexing). If performance degrades significantly, "
                    "it empirically proves that explicit sequence order information is a critical, "
                    "non-attention-based component — clarifying whether 'attention is *all* you need' "
                    "or if the sinusoidal positional encodings are doing essential hidden work."
                ),
                "why": (
                    "Directly tests a subtle contradiction in the paper's headline claim and informs "
                    "future architectural designs about the true necessity of positional encodings."
                ),
                "difficulty": "intermediate",
            },
            {
                "idea": (
                    "Benchmark the vanilla Transformer on sequences of increasing length (256 → 4096 "
                    "tokens) to empirically map the O(N²) memory wall. Then design sparse attention "
                    "patterns (local windows + a few global tokens) to bring the complexity down to "
                    "linear — unlocking Transformers for long documents, audio, and genomics."
                ),
                "why": (
                    "Removes the single biggest practical limitation of the architecture. The quadratic "
                    "bottleneck is the reason the paper cannot claim true general-purpose applicability."
                ),
                "difficulty": "intermediate",
            },
            {
                "idea": (
                    "Run a systematic hyperparameter sensitivity study: perturb `num_heads`, `d_model`, "
                    "`warmup_steps`, and `dropout_rate` by ±10–20% from the paper's values and measure "
                    "the BLEU impact. This maps out how robust (or fragile) the architecture truly is, "
                    "and provides practical tuning guidance that the original paper omits."
                ),
                "why": (
                    "The paper mentions 'countless model variants' were tuned but provides no sensitivity "
                    "analysis — essential for reproducibility and adoption by researchers without large "
                    "compute budgets."
                ),
                "difficulty": "advanced",
            },
            {
                "idea": (
                    "Test the Transformer against a CNN-based model (e.g., TextCNN) on tasks where "
                    "local context dominates — named entity recognition, short-text sentiment analysis "
                    "— using varying amounts of training data (10%, 50%, 100%). This quantifies the "
                    "cost of having no inductive bias for locality and shows where a hybrid "
                    "CNN-Transformer architecture would be most beneficial."
                ),
                "why": (
                    "Addresses the Transformer's known data-hunger on locally-structured tasks and "
                    "directly motivates hybrid architectures for data-scarce settings."
                ),
                "difficulty": "intermediate",
            },
        ],

        "agent_debate": [
            {
                "agent": "Research Agent",
                "message": (
                    "The Transformer's self-attention is the most important algorithmic breakthrough in NLP "
                    "in a decade. The O(1) path length between any two positions fundamentally solves the "
                    "long-range dependency problem that crippled RNNs. The 28.4 BLEU on EN-DE benchmark "
                    "isn't just an improvement — it's a 2+ point jump over the best ensembles, and the "
                    "41.8 BLEU on EN-FR at a fraction of prior training cost is equally impressive."
                ),
                "side": "pro",
            },
            {
                "agent": "Critic Agent",
                "message": (
                    "The O(1) path comes at the cost of O(N²) memory — making the architecture "
                    "completely unusable on sequences longer than a few thousand tokens. The paper only "
                    "tests on short translation sentences. Calling this a general-purpose sequence "
                    "architecture without testing on long documents or genomics is overclaiming. And the "
                    "claim to be 'simple' is undermined by the non-trivial hyperparameter sensitivity "
                    "that Hypothesis H3 exposes."
                ),
                "side": "con",
            },
            {
                "agent": "Research Agent",
                "message": (
                    "The quadratic cost is real, but the paper explicitly acknowledges it and suggests "
                    "restricted attention as a future direction. For the lengths where NMT operates "
                    "(≤512 tokens), memory is not a constraint. The community response proved the point — "
                    "Longformer, BigBird, and FlashAttention all fixed the scaling issue while keeping "
                    "the same architectural foundation."
                ),
                "side": "pro",
            },
            {
                "agent": "Critic Agent",
                "message": (
                    "Hypothesis H1 raises the deeper issue: the paper claims to dispense with recurrence "
                    "entirely, yet positional encodings are doing the sequential work that recurrence used "
                    "to do. Without an ablation showing what happens without them, the claim that "
                    "'attention is ALL you need' is empirically unproven in the paper itself."
                ),
                "side": "con",
            },
            {
                "agent": "Planner Agent",
                "message": (
                    "Both sides are right, and neither invalidates the paper's core contribution. "
                    "The architectural insight — attention alone is sufficient — is correct and generative. "
                    "The practical recommendations: (1) test H1 (positional encoding ablation) first to "
                    "understand the architecture's true inductive biases; (2) use sparse attention for "
                    "sequences >2K tokens; (3) treat the warm-up schedule as a required hyperparameter, "
                    "not optional. The reproducibility score of 6.0/10 reflects real gaps the community "
                    "should address."
                ),
                "side": "mediate",
            },
        ],
    },

    # ── Errors ───────────────────────────────────────────────────────────────
    "errors": [],
}

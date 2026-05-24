"""
app/utils/demo_data.py — Pre-built demo results for "Attention Is All You Need".

Click the amber "Run Demo" button in the nav to load this instantly.
No Gemini API call, no arXiv call — works even when the API is exhausted.
"""

DEMO_RESULT = {
    "status":        "ok",
    "mode":          "demo",
    "query":         "Attention Is All You Need",
    "refined_query": "transformer self-attention neural machine translation",

    # ── Papers ───────────────────────────────────────────────────────────────
    "papers": [
        {
            "title":      "Attention Is All You Need",
            "authors":    ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
            "abstract":   "We propose the Transformer, a model based entirely on attention mechanisms — "
                          "no recurrence, no convolutions. It's faster to train, easier to parallelise, "
                          "and beats every previous model on English-to-German and English-to-French "
                          "translation. Training took 12 hours on 8 GPUs instead of weeks.",
            "url":        "https://arxiv.org/abs/1706.03762",
            "published":  "2017-06-12",
            "categories": ["cs.CL", "cs.LG"],
        },
        {
            "title":      "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors":    ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            "abstract":   "BERT takes the Transformer and pre-trains it on a huge amount of text "
                          "using two tasks: predict a hidden word, and predict whether sentence B "
                          "follows sentence A. The resulting model, fine-tuned on 11 different tasks, "
                          "beats every existing approach — often by a wide margin.",
            "url":        "https://arxiv.org/abs/1810.04805",
            "published":  "2018-10-11",
            "categories": ["cs.CL", "cs.LG"],
        },
        {
            "title":      "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "authors":    ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov"],
            "abstract":   "What if we just cut an image into patches and feed them to a Transformer "
                          "like words in a sentence? That's Vision Transformer (ViT). When trained on "
                          "enough data it matches or beats the best convolutional networks — and it "
                          "doesn't need any image-specific design choices baked in.",
            "url":        "https://arxiv.org/abs/2010.11929",
            "published":  "2020-10-22",
            "categories": ["cs.CV", "cs.LG"],
        },
        {
            "title":      "Longformer: The Long-Document Transformer",
            "authors":    ["Iz Beltagy", "Matthew E. Peters", "Arman Cohan"],
            "abstract":   "Standard Transformers can't handle documents longer than ~512 tokens because "
                          "attention costs grow quadratically. Longformer fixes this with a sliding-window "
                          "attention that looks at nearby words plus a handful of global tokens. "
                          "Result: you can process thousands of tokens without running out of memory.",
            "url":        "https://arxiv.org/abs/2004.05150",
            "published":  "2020-04-10",
            "categories": ["cs.CL", "cs.LG"],
        },
        {
            "title":      "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "authors":    ["Tri Dao", "Daniel Y. Fu", "Stefano Ermon", "Atri Rudra"],
            "abstract":   "The bottleneck in running Transformers isn't the computation — it's moving "
                          "data between GPU memory levels. FlashAttention reorganises the attention "
                          "calculation to minimise that data movement. Same result as standard attention, "
                          "but 2-4× faster and using far less memory.",
            "url":        "https://arxiv.org/abs/2205.14135",
            "published":  "2022-05-27",
            "categories": ["cs.LG", "cs.AR"],
        },
    ],

    # ── Critique ─────────────────────────────────────────────────────────────
    "critique": (
        "**The memory wall nobody talks about:** Every paper here uses full attention or "
        "an approximation of it. None of them addresses what happens when you want to run "
        "these models on a phone or in a hospital with no GPU. Edge deployment is a real "
        "problem, and it's completely ignored.\n\n"
        "**They only test on translation and classification:** BERT and the original Transformer "
        "were mostly tested on sentence-level tasks. Real documents — legal contracts, research "
        "papers, medical records — are thousands of tokens long. Longformer tries, but only "
        "partially. Nobody tests on truly messy, real-world text.\n\n"
        "**We don't know what the attention heads actually learned:** Papers report benchmark "
        "numbers, but nobody shows *why* certain attention heads work better. There's no "
        "experiment that says 'if we remove heads 4 and 7, this specific capability breaks.' "
        "Without that, we're just guessing.\n\n"
        "**The carbon footprint conversation is missing:** Training BERT from scratch costs "
        "thousands of GPU-hours and produces real CO2. None of these papers mentions energy "
        "use. For researchers at smaller institutions, that's a huge practical barrier that's "
        "being swept under the rug.\n\n"
        "**ViT needs Google-scale data to shine:** Vision Transformer only beats CNNs when "
        "pre-trained on JFT-300M — a proprietary Google dataset nobody else can access. "
        "That makes the headline result unverifiable for most researchers."
    ),

    # ── Hypotheses (refined — iteration 2) ───────────────────────────────────
    "hypotheses": [
        "H: What if we could run these powerful AI language models on a regular phone "
        "instead of an expensive server? Right now they need a lot of computing power, "
        "but if we quietly cut out the parts that seem to do the least useful work, "
        "the model might still give great answers — just much faster and cheaper.",

        "H: What if a small AI trained only on medical records could beat a huge "
        "general-purpose AI at understanding doctor notes? Most AI tools today learned "
        "from the whole internet — not specifically from medicine. Teaching a smaller, "
        "cheaper model using real hospital data might make it smarter where it counts.",

        "H: What if we could get the same impressive image-recognition results without "
        "using Google's private photo collection that nobody else can access? "
        "Running the same experiment with only publicly available images would show "
        "whether the technique truly works — or whether it just needed more data.",

        "H: What if the speed trick used in one paper could also make handling very "
        "long documents far less memory-hungry? Today, processing a full research paper "
        "or legal contract in one go pushes even powerful computers to their limits — "
        "combining two clever ideas might fix this and open the door to much longer texts.",

        "H: What if we could figure out which parts of the AI are actually doing the "
        "useful thinking, and which parts are just dead weight? Nobody has done a "
        "careful test where you remove pieces one by one and measure what breaks. "
        "Knowing the answer would help us build much smaller, faster, and cheaper models.",
    ],

    # ── Key findings ─────────────────────────────────────────────────────────
    "key_findings": [
        "• Replacing recurrent layers with attention cuts training time by 8× — "
        "the Transformer proved you don't need sequential processing to understand language.",

        "• Pre-training on huge text corpora then fine-tuning is dramatically more "
        "efficient than training task-specific models from scratch — BERT showed this "
        "works across 11 completely different NLP tasks.",

        "• The 'attention is all you need' idea works outside NLP too — ViT shows "
        "that images can be treated like sequences of patches, removing the need for "
        "convolutional inductive biases when you have enough data.",

        "• Quadratic attention complexity is a real engineering problem — Longformer's "
        "linear-complexity windowed attention makes it practical to process "
        "full research papers or legal documents in one forward pass.",

        "• The GPU memory bottleneck matters more than raw FLOPs — FlashAttention "
        "proved you can get 2-4× speedups just by thinking carefully about where "
        "data lives on the chip, without changing the math at all.",

        "• Open-sourcing code and naming your datasets is strongly correlated with "
        "reproducibility — the papers in this area that shared everything score 8-9/10, "
        "while API-only releases are essentially unverifiable by the community.",
    ],

    # ── Repro scores ─────────────────────────────────────────────────────────
    "repro_scores": [
        {
            "title":            "Attention Is All You Need",
            "score":            8,
            "reasoning":        "Code on GitHub (tensor2tensor), WMT datasets are public, "
                                "training details fully in the appendix. Slightly docked because "
                                "the original training setup required 8 P100s for 12 hours.",
            "code_mentions":    ["github.com/tensorflow/tensor2tensor"],
            "dataset_mentions": ["WMT 2014 English-German", "WMT 2014 English-French"],
        },
        {
            "title":            "BERT: Pre-training of Deep Bidirectional Transformers",
            "score":            9,
            "reasoning":        "Full model weights released, fine-tuning scripts included, "
                                "all 11 benchmarks are public. One of the most reproducible "
                                "large-scale NLP papers ever published.",
            "code_mentions":    ["github.com/google-research/bert"],
            "dataset_mentions": ["GLUE", "SQuAD", "Wikipedia", "BooksCorpus"],
        },
        {
            "title":            "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "score":            6,
            "reasoning":        "Code and pre-trained weights are available, but the headline "
                                "result requires JFT-300M — a proprietary Google dataset. "
                                "Most researchers can only partially reproduce the main claim.",
            "code_mentions":    ["github.com/google-research/vision_transformer"],
            "dataset_mentions": ["ImageNet", "CIFAR-10", "CIFAR-100"],
        },
        {
            "title":            "Longformer: The Long-Document Transformer",
            "score":            8,
            "reasoning":        "Full code and pre-trained models on GitHub (allenai/longformer), "
                                "all benchmarks use public datasets. Very easy to build on.",
            "code_mentions":    ["github.com/allenai/longformer"],
            "dataset_mentions": ["WikiHop", "TriviaQA", "IMDB"],
        },
        {
            "title":            "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "score":            9,
            "reasoning":        "CUDA kernel fully open-sourced, detailed benchmarks on A100 and V100, "
                                "now integrated directly into HuggingFace Transformers and PyTorch. "
                                "Essentially impossible not to reproduce.",
            "code_mentions":    ["github.com/Dao-AILab/flash-attention"],
            "dataset_mentions": ["C4", "The Pile"],
        },
    ],

    # ── Model profiles ────────────────────────────────────────────────────────
    "model_profiles": [
        {
            "paper":          "Attention Is All You Need",
            "architecture":   "Transformer (Encoder-Decoder)",
            "key_components": ["Multi-Head Self-Attention", "Positional Encoding", "Feed-Forward sublayers"],
            "parameters":     "65M (base) · 213M (large)",
            "training_data":  "WMT 2014 — 4.5M English-German sentence pairs",
            "compute":        "8× NVIDIA P100 GPUs · 12 hours (base) to 3.5 days (large)",
            "framework":      "TensorFlow (tensor2tensor)",
        },
        {
            "paper":          "BERT: Pre-training of Deep Bidirectional Transformers",
            "architecture":   "Transformer Encoder only (bidirectional)",
            "key_components": ["Masked Language Modelling", "Next Sentence Prediction", "WordPiece tokeniser"],
            "parameters":     "110M (base) · 340M (large)",
            "training_data":  "English Wikipedia (2.5B words) + BooksCorpus (800M words)",
            "compute":        "4× TPU v3 Pods · 4 days",
            "framework":      "TensorFlow",
        },
        {
            "paper":          "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "architecture":   "Vision Transformer (Encoder only, treats image patches as tokens)",
            "key_components": ["Patch Embedding", "Position Embedding", "Multi-Head Attention", "MLP head"],
            "parameters":     "86M (ViT-B/16) · 307M (ViT-L/16)",
            "training_data":  "JFT-300M (proprietary) · ImageNet-21K (public alternative)",
            "compute":        "TPU v3-512 · 7 days on JFT-300M",
            "framework":      "JAX/Flax",
        },
        {
            "paper":          "Longformer: The Long-Document Transformer",
            "architecture":   "Transformer with windowed + global attention (replaces full attention)",
            "key_components": ["Sliding-Window Attention (local)", "Global Attention tokens", "Dilated Attention"],
            "parameters":     "149M (longformer-base) · 435M (longformer-large)",
            "training_data":  "RoBERTa checkpoint continued on long documents",
            "compute":        "8× V100 GPUs · 2 days",
            "framework":      "PyTorch (HuggingFace)",
        },
        {
            "paper":          "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "architecture":   "Drop-in CUDA kernel replacing standard attention (no new model architecture)",
            "key_components": ["IO-aware tiling", "SRAM/HBM memory management", "Recomputation during backward pass"],
            "parameters":     "Applies to any Transformer — tested on GPT-2 (117M) to GPT-3-scale",
            "training_data":  "The Pile, C4 (tested on various benchmarks)",
            "compute":        "1× A100 · 2-4× faster than baseline PyTorch attention",
            "framework":      "CUDA C++ (wrappable from PyTorch)",
        },
    ],

    # ── Code snippet ─────────────────────────────────────────────────────────
    "code_snippet": """\
# What this shows: Scaled Dot-Product Attention — the core idea of every Transformer.
# Run this with: pip install torch  then  python this_file.py

import torch
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    \"\"\"
    The fundamental operation inside every Transformer.

    Q = Queries  (what am I looking for?)
    K = Keys     (what does each word offer?)
    V = Values   (what information does each word carry?)

    Step 1: Score how relevant each word is to each query (Q × K^T)
    Step 2: Scale down so gradients don't explode (÷ √d_k)
    Step 3: Softmax so scores sum to 1 (attention weights)
    Step 4: Weighted sum of Values
    \"\"\"
    d_k = Q.size(-1)

    # Step 1 + 2: relevance scores, scaled
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    # Step 3: optional mask (used in decoder to hide future tokens)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # Step 4: turn scores into probabilities
    attention_weights = F.softmax(scores, dim=-1)

    # Step 5: weighted sum of Values
    output = torch.matmul(attention_weights, V)
    return output, attention_weights


# ── Try it with a small example ───────────────────────────────────────────────
batch, heads, seq_len, d_k = 1, 1, 5, 8  # 5 words, 8-dim keys

# Random Q, K, V — in a real model these come from linear projections
Q = torch.rand(batch, heads, seq_len, d_k)
K = torch.rand(batch, heads, seq_len, d_k)
V = torch.rand(batch, heads, seq_len, d_k)

output, weights = scaled_dot_product_attention(Q, K, V)

print("Input sequence length  :", seq_len)
print("Attention weight matrix :", weights.shape)   # (1, 1, 5, 5)
print("Output shape            :", output.shape)    # (1, 1, 5, 8)
print()
print("Attention weights (how much each word attends to every other word):")
print(weights[0, 0].detach().numpy().round(3))
print()
print("Each row sums to 1.0:", weights[0, 0].sum(dim=-1).detach().numpy().round(4))
""",

    # ── Synthesis ─────────────────────────────────────────────────────────────
    "synthesis": """\
## What's the big picture?

The Transformer — introduced in 2017 — quietly replaced recurrence and convolution
as the default way to process sequences. It turns out that if you let every word
look at every other word simultaneously (that's attention), and you have enough data
and compute, you can outperform years of carefully engineered architectures.
The research since 2017 has mostly been: applying this idea everywhere else,
and fixing the practical problems that came with it.

## What we actually learned

• Replacing recurrent layers with attention cuts training time by 8× — the Transformer proved you don't need sequential processing to understand language.

• Pre-training on huge text corpora then fine-tuning is dramatically more efficient than training task-specific models from scratch — BERT showed this works across 11 completely different NLP tasks.

• The 'attention is all you need' idea works outside NLP too — ViT shows that images can be treated like sequences of patches, removing the need for convolutional inductive biases when you have enough data.

• Quadratic attention complexity is a real engineering problem — Longformer's linear-complexity windowed attention makes it practical to process full research papers or legal documents in one forward pass.

• The GPU memory bottleneck matters more than raw FLOPs — FlashAttention proved you can get 2-4× speedups just by thinking carefully about where data lives on the chip, without changing the math at all.

• Open-sourcing code and naming your datasets is strongly correlated with reproducibility — the papers in this area that shared everything score 8-9/10, while API-only releases are essentially unverifiable.

## What's broken or missing

**The memory wall nobody talks about:** Every paper uses full attention or an approximation. None addresses running these models on a phone or in a hospital with no GPU. Edge deployment is a real problem that's completely ignored.

**They only test on translation and classification:** Real documents — legal contracts, medical records — are thousands of tokens long. Longformer tries, but only partially. Nobody tests on truly messy, real-world text.

**We don't know what the attention heads actually learned:** Papers report benchmark numbers, but nobody shows *why* certain heads work better. Without that kind of ablation, we're just guessing.

**The carbon footprint conversation is missing:** Training BERT from scratch costs thousands of GPU-hours. None of these papers mentions energy use — a huge practical barrier for smaller institutions.

## What someone should do next

Try this: Prune the bottom 30% of attention heads by gradient magnitude and measure the speed/accuracy tradeoff on SQuAD 2.0. This would tell us which heads are actually doing useful work.

Try this: Train a small Transformer on clinical notes with a domain-specific tokeniser and compare it directly to GPT-3.5 zero-shot on medical coding — realistic, actionable, and fundable.

Try this: Replicate ViT on ImageNet-21K only (no JFT-300M) and publish the full compute and energy cost. This makes the research accessible and adds a fairness benchmark the community actually needs.

## How trustworthy is this research?

Pretty good overall — average score is **8/10**. FlashAttention and BERT are the gold standard: everything is open, reproducible, and has been independently verified by thousands of practitioners. Vision Transformer is the exception — its main claim requires a private Google dataset, so you'll have to take their word for it or use the weaker ImageNet-21K setup. For building on this work, start with BERT or FlashAttention — you'll actually be able to verify your baselines.
""",

    # ── Methodology breakdown ─────────────────────────────────────────────────
    "methodology": [
        {
            "paper":      "Attention Is All You Need",
            "approach":   "They replaced all recurrent and convolutional layers with a mechanism "
                          "that lets every word look at every other word at the same time — called self-attention.",
            "how_tested": "Measured translation quality using a standard score (BLEU) on two large "
                          "English-to-German and English-to-French benchmarks, and tracked training speed.",
            "steps": [
                "Stack 6 encoder layers and 6 decoder layers, each built entirely from attention",
                "Add positional encodings so the model knows word order without reading left-to-right",
                "Train on 4.5 million sentence pairs for 12 hours on 8 GPUs and compare to previous models",
            ],
        },
        {
            "paper":      "BERT: Pre-training of Deep Bidirectional Transformers",
            "approach":   "Pre-train a Transformer on two self-supervised tasks — predict a hidden word, "
                          "and predict whether two sentences follow each other — then fine-tune it on 11 downstream tasks.",
            "how_tested": "Compared fine-tuned BERT to the previous state-of-the-art on each of 11 "
                          "standard NLP benchmarks and reported whether it beat or matched the best result.",
            "steps": [
                "Train on English Wikipedia and BooksCorpus (3.3 billion words) for 4 days on TPUs",
                "Randomly mask 15% of words during training and teach the model to predict them",
                "Fine-tune the pre-trained model separately on each task with a simple classification head",
            ],
        },
        {
            "paper":      "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "approach":   "Cut each image into a grid of fixed-size patches, flatten each patch into a vector, "
                          "and feed the sequence of patches directly into a standard Transformer.",
            "how_tested": "Measured image classification accuracy on ImageNet and four other benchmarks, "
                          "comparing against the best convolutional networks of the time.",
            "steps": [
                "Split a 224×224 image into 196 patches of 16×16 pixels each",
                "Add a learnable class token to the sequence and train with positional embeddings",
                "Pre-train on JFT-300M (Google's internal dataset) then fine-tune on each benchmark",
            ],
        },
        {
            "paper":      "Longformer: The Long-Document Transformer",
            "approach":   "Replace the expensive full attention (where every word looks at every other word) "
                          "with a sliding window that only looks locally, plus a few special global tokens.",
            "how_tested": "Tested on tasks that require reading long documents — question answering over "
                          "Wikipedia articles and multi-hop reasoning — and measured accuracy vs. memory use.",
            "steps": [
                "Apply a window of fixed size (e.g. 512 tokens) around each word for local attention",
                "Allow a small set of special tokens (e.g. [CLS]) to attend to the entire document globally",
                "Continue pre-training from a RoBERTa checkpoint on long documents to adapt the weights",
            ],
        },
        {
            "paper":      "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "approach":   "Rewrite the attention calculation in a way that minimises how often data "
                          "moves between the slow and fast parts of the GPU, getting the same answer but faster.",
            "how_tested": "Measured wall-clock training time, peak GPU memory, and final model accuracy "
                          "on language modelling tasks, comparing to standard PyTorch attention.",
            "steps": [
                "Tile the attention computation into blocks that fit in the GPU's fast on-chip memory (SRAM)",
                "Avoid saving the full attention matrix to slow memory by recomputing it on the backward pass",
                "Verify the output is mathematically identical to standard attention (no approximation)",
            ],
        },
    ],

    # ── Assumptions ───────────────────────────────────────────────────────────
    "assumptions": [
        {
            "paper": "Attention Is All You Need",
            "assumptions": [
                "Translation quality (BLEU score) is a reliable stand-in for general language understanding.",
                "The same architecture that wins at translation will generalise to other language tasks.",
                "More attention heads always help — but they only compared up to 8 heads.",
            ],
        },
        {
            "paper": "BERT: Pre-training of Deep Bidirectional Transformers",
            "assumptions": [
                "The more text you pre-train on, the better the model gets — without a clear upper limit.",
                "The two pre-training tasks (masked words, sentence order) are a good proxy for language understanding.",
                "Fine-tuning a large pre-trained model on a small task-specific dataset won't cause overfitting.",
            ],
        },
        {
            "paper": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "assumptions": [
                "Splitting an image into square patches and treating them like words is a reasonable way to represent visual information.",
                "Pre-training on enough images removes the need for the special inductive biases built into convolutional networks.",
                "Results on Google's private JFT-300M dataset are representative of what you'd see on public data.",
            ],
        },
        {
            "paper": "Longformer: The Long-Document Transformer",
            "assumptions": [
                "Most of the useful information in a long document is locally concentrated — words mainly relate to nearby words.",
                "A small set of global tokens is enough to capture document-level meaning.",
                "Continuing pre-training from an existing checkpoint is sufficient to adapt to longer sequences.",
            ],
        },
        {
            "paper": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "assumptions": [
                "The main bottleneck in Transformer training is data movement, not raw computation.",
                "Recomputing attention weights during the backward pass is cheaper than storing and retrieving them.",
                "The speedups will hold across different GPU generations and model sizes.",
            ],
        },
    ],

    # ── Weaknesses ────────────────────────────────────────────────────────────
    "weaknesses": [
        {
            "paper": "Attention Is All You Need",
            "weaknesses": [
                "Attention cost grows quadratically with sequence length — processing documents longer than ~512 tokens is prohibitively slow.",
                "Only tested on machine translation; no evidence at the time that it works well on other language tasks.",
                "Training required 8 expensive GPUs for up to 3.5 days — inaccessible to most academic researchers.",
            ],
        },
        {
            "paper": "BERT: Pre-training of Deep Bidirectional Transformers",
            "weaknesses": [
                "The pre-training required enormous compute (TPU pods for 4 days) that most research teams can't afford.",
                "The model is encoder-only and cannot generate text natively, limiting its use for tasks like summarisation.",
                "Next Sentence Prediction was later shown to be a weak training signal — subsequent models dropped it.",
            ],
        },
        {
            "paper": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "weaknesses": [
                "The headline results depend on JFT-300M — a proprietary Google dataset that no one outside Google can access.",
                "Without massive pre-training data, ViT performs significantly worse than convolutional networks.",
                "Using fixed square patches loses fine-grained spatial relationships that convolutions naturally capture.",
            ],
        },
        {
            "paper": "Longformer: The Long-Document Transformer",
            "weaknesses": [
                "The fixed local window size is a design choice that may not suit all documents — code or legal contracts may have long-range dependencies the window misses.",
                "The global attention tokens must be chosen manually per task, which requires domain expertise.",
                "Evaluated mainly on reading-comprehension tasks; performance on tasks like summarisation is less established.",
            ],
        },
        {
            "paper": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
            "weaknesses": [
                "The implementation is written in low-level CUDA C++, making it hard for non-experts to modify or debug.",
                "Speedups vary considerably by GPU model and sequence length — real gains depend heavily on your hardware.",
                "The recomputation trick increases FLOPs on the backward pass, which can offset savings on compute-bound workloads.",
            ],
        },
    ],

    # ── Phase 5 loop telemetry ────────────────────────────────────────────────
    "hypothesis_iterations": 2,
    "evaluator_feedback": (
        "First batch was rejected because the ideas were too vague — phrases like "
        "'improve performance' without naming a specific metric or baseline. "
        "Second attempt named concrete models (BERT-base, ViT-B/16), specific datasets "
        "(SQuAD 2.0, MIMIC-III), and measurable numbers (35% speedup, 15% F1 gain), "
        "which passed all four quality checks."
    ),

    "errors": [],
}

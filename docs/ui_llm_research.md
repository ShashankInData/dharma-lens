# Dharma Lens UI + Open-Source LLM Research

Date: 2026-06-29

## Goal

Improve Dharma Lens from a basic Gradio form into a clean, niche chat experience with history, retrieval status, source cards, and optional open-source LLM synthesis.

The app must still stay grounded in retrieved Bhagavad Gita verses. The LLM should improve fluency and typo tolerance, not become an uncited spiritual authority.

## Current problem

The deployed UI is technically correct but visually weak:

- It looks like a default Gradio demo.
- The answer feels stitched/extractive.
- There is no chat memory visible to the user.
- The retrieval process is not visible, so the answer appears pasted rather than generated.
- Sources are shown, but not in a polished source-card/chat pattern.

## UI direction

Recommended direction: **clean ChatGPT-style chat with citation cards**.

### Requirements

- Chat history visible in the main area.
- User message and Dharma Lens answer appear as conversation turns.
- Response can stream in stages:
  1. `Reading your question...`
  2. `Retrieving relevant verses...`
  3. `Composing grounded reflection...`
  4. Final answer.
- Retrieved sources shown as expandable cards below the answer.
- Simple, calm, niche aesthetic.
- No complicated controls.
- Strong first-screen clarity: what it is, what it is not, and how to start.
- No permanent user Q&A storage.

### Gradio feasibility

The installed Gradio version is `6.19.0`.

Useful Gradio capabilities checked locally:

- `gr.ChatInterface` supports:
  - `save_history`
  - `theme`
  - `css`
  - `examples`
  - `additional_outputs`
  - `show_progress`
  - `fill_height`
- `gr.Chatbot` supports:
  - `layout='bubble'`
  - `height`
  - `placeholder`
  - `render_markdown`
  - copy buttons
- Streaming can be implemented with a generator function that yields intermediate chat updates.

Recommendation: use `gr.Blocks` with `gr.Chatbot`, not plain `ChatInterface`, because we need custom source cards and staged retrieval status.

## LLM research

### GLM-5.2

Hugging Face model: `zai-org/GLM-5.2`

Metadata checked through Hugging Face API:

- License: MIT.
- Pipeline: text-generation.
- Public: yes.
- Parameter metadata: about 753B parameters.

Conclusion: not practical for free/CPU Hugging Face Spaces or local testing. It is a serious open model, but too large for this deployment path.

### Candidate open-source models checked

| Model | License | Gated | Approx params from metadata | Notes |
|---|---:|---:|---:|---|
| `Qwen/Qwen2.5-1.5B-Instruct` | Apache-2.0 | No | 1.54B | Best practical default. Fast enough, good typo correction, works through HF provider when specified. |
| `Qwen/Qwen2.5-3B-Instruct` | Other | No | 3.09B | Better language than 1.5B, but license is not as clean as Apache in metadata. |
| `Qwen/Qwen2.5-7B-Instruct` | Apache-2.0 | No | 7.62B | Better quality, but heavier and less safe for free/low-resource path. |
| `Qwen/Qwen3-1.7B` | Apache-2.0 | No | 2.03B | Works, but output included `<think>` reasoning text in the quick test. Not ideal for public v1 unless controlled carefully. |
| `Qwen/Qwen3-4B` | Apache-2.0 | No | 4.02B | Likely better but heavier. Needs prompt control to avoid reasoning leakage. |
| `microsoft/Phi-3.5-mini-instruct` | MIT | No | 3.82B | Good license, reasonable quality, but quick provider tests were less straightforward. |
| `microsoft/Phi-4-mini-instruct` | MIT | No | 3.84B | Good license and quality candidate. Works with provider test, but heavier than Qwen 1.5B. |
| `google/gemma-2-2b-it` | Gemma | Manual gated | 2.61B | Gated/license friction, avoid for v1. |
| `google/gemma-3-1b-it` | Gemma | Manual gated | 1.0B | Gated/license friction, avoid for v1. |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | Apache-2.0 | No | 1.71B | Good lightweight fallback, but likely weaker answer quality. |

### Live feasibility test

Using `huggingface_hub.InferenceClient` with `provider='auto'` failed for several models with:

`model_not_supported`

Using `provider='featherless-ai'` worked for `Qwen/Qwen2.5-1.5B-Instruct`.

Typo test prompt:

`Rewrite clearly in one sentence: i am anxius abot work reslts`

Result from `Qwen/Qwen2.5-1.5B-Instruct`:

`I am anxious about the results of my work.`

Grounded synthesis test with Bhagavad Gita 2.47 also worked. Qwen 2.5 1.5B and 3B produced concise grounded answers. Qwen3 leaked reasoning-style `<think>` text in the quick test, so avoid Qwen3 for now unless we add stricter handling.

## Recommended model path

Recommended v1 LLM synthesis model:

`Qwen/Qwen2.5-1.5B-Instruct` through Hugging Face Inference Providers with `provider='featherless-ai'`.

Why:

- Open-source friendly license: Apache-2.0.
- Small enough for fast responses.
- Good enough for typo normalization and answer smoothing.
- Worked in a live provider test.
- Does not require self-hosting on the Space CPU.

Fallback:

- Keep deterministic extractive synthesis if HF provider call fails.
- Never let provider failure break the app.

Possible upgrade later:

- `Qwen/Qwen2.5-3B-Instruct` if answer quality needs improvement and licensing is acceptable.
- `microsoft/Phi-4-mini-instruct` if we want MIT license and better reasoning, but test latency and provider availability first.

## Secret needed for deployed Space

The Space will need a secret for provider calls:

`HF_TOKEN`

CLI command after code is ready:

```bash
hf spaces secrets add ShashhankIndata/dharma-lens -s HF_TOKEN
```

This should use the existing Hugging Face auth. The token will be stored as a Space secret, not committed to GitHub.

## Architecture recommendation

Keep the pipeline split:

1. User asks question.
2. Lightweight query normalization for spelling/grammar if LLM enabled.
3. Retrieve verses with existing vector index and theme boost.
4. Build strict context prompt from retrieved chunks.
5. LLM writes fluent answer using only retrieved citations.
6. Citation validator checks every citation.
7. If invalid citation appears, block generated answer and use deterministic fallback.
8. UI streams status and final answer.

## UI implementation plan

### Phase 1 - Local chat UI

- Replace current form-style UI with `gr.Blocks` + `gr.Chatbot`.
- Add a minimal header:
  - `Dharma Lens`
  - `Bhagavad Gita-grounded reflection, with citations.`
- Add example chips:
  - work/results anxiety
  - anger control
  - focus/mind wandering
  - calm during conflict
- Add chat history in browser session only.
- Add staged status messages.
- Add source cards in a side or lower panel.

### Phase 2 - LLM synthesis

- Add `src/llm.py`.
- Add tests for:
  - typo normalization
  - model fallback
  - citation validation after LLM answer
  - no token required for deterministic fallback
- Add env vars:
  - `DHARMA_LENS_USE_LLM=true/false`
  - `DHARMA_LENS_LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct`
  - `DHARMA_LENS_LLM_PROVIDER=featherless-ai`
- Use `HF_TOKEN` from environment for deployed Space.

### Phase 3 - Deploy

- Test locally.
- Set Space secret `HF_TOKEN`.
- Push to GitHub.
- Upload/redeploy Hugging Face Space.
- Run live API smoke test.

## Decision

Build the chat UI first with deterministic answer and simulated status. Then add LLM synthesis behind a feature flag. This keeps the app stable while improving the feel.

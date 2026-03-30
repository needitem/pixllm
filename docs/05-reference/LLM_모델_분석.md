# 오픈소스 LLM 종합 분석 (2026년 2월 기준)

> ⚠️ **폐쇄망(Air-gapped) 환경 전용** - 오프라인 로컬 배포 가이드

---

## 🧠 범용 LLM (문서 분석 / 추론 / 맥락 파악)

### 📊 범용 벤치마크 비교

| 모델 | MMLU | 추론 | 컨텍스트 | 4-bit VRAM | 특징 |
|------|:----:|:----:|:--------:|:----------:|------|
| **Qwen3-235B** | ~88% | ⭐⭐⭐ | **1M** | ~120GB | 다국어, 한국어 |
| **Llama 3.3 70B** | 86% | ⭐⭐⭐ | 128K | ~36GB | 범용 최강 |
| **DeepSeek-R1** | ~85% | ⭐⭐⭐⭐ | 164K | ~380GB | 추론 특화 |
| **Qwen3-72B** | ~85% | ⭐⭐⭐ | 128K | ~36GB | 균형 잡힘 |
| **GLM-4.6** | ~84% | ⭐⭐⭐ | 200K | ~100GB | 긴 컨텍스트 |

### 📄 문서 분석 (VLM) 추천

| 모델 | 용도 | 4-bit VRAM |
|------|------|:----------:|
| **Qwen2.5-VL-72B** | 문서 OCR, 표 추출 | ~36GB |
| **GLM-4.5V** | 이미지+문서 분석 | ~40GB |
| **DeepSeek-VL2** | 시각 추론 | ~25GB |

### 🎯 폐쇄망 GPU별 범용 LLM 추천

| GPU | 추천 모델 | 용도 |
|-----|----------|------|
| **A30 24GB** | Qwen3-32B (4-bit) | 기본 추론 |
| **A100 80GB** | Llama 3.3 70B (FP16) | 범용 최적 |
| **H100 × 2+** | Qwen3-235B (4-bit) | 1M 컨텍스트 |

---

## 💻 코딩용 LLM

---

## 🔥 유료 vs 오픈소스 성능 비교

### 📊 종합 벤치마크 비교 (2026년 2월)

| 모델 | 유형 | SWE-Bench | HumanEval | LiveCodeBench | 컨텍스트 |
|------|:----:|:---------:|:---------:|:-------------:|:--------:|
| **Claude Opus 4.5** | 💰 유료 | **80.9%** | 94.2% | ~88% | 200K |
| **GPT-5.2 Codex** | 💰 유료 | 80.0% | 91.7% | ~87% | 400K |
| **Gemini 3 Pro** | 💰 유료 | 77.4% | ~90% | 81.7% | 1M |
| **Claude Sonnet 4.5** | 💰 유료 | ~72% | ~88% | ~82% | 200K |
| --- | --- | --- | --- | --- | --- |
| **DeepSeek V3.2 Speciale** | 🆓 오픈 | ~72% | ~84% | **89.6%** | 128K |
| **GLM-4.7 (Thinking)** | 🆓 오픈 | ~68% | ~80% | **89.4%** | 128K |
| **Kimi K2.5** | 🆓 오픈 | ~65% | ~82% | 85.3% | 256K |
| **Qwen3-Coder-32B** | 🆓 오픈 | 66% | ~81% | ~78% | 32K |
| **Devstral Small 2** | 🆓 오픈 | 68% | ~75% | ~70% | 256K |

### 💡 성능 격차 분석

| 벤치마크 | 유료 최고 | 오픈소스 최고 | 격차 |
|----------|----------|--------------|:----:|
| **SWE-Bench** | Claude Opus 4.5 (80.9%) | DeepSeek V3.2 (72%) | **-8.9%** |
| **HumanEval** | Claude Opus 4.5 (94.2%) | DeepSeek V3 (82.6%) | **-11.6%** |
| **LiveCodeBench** | Opus 4.5 (~88%) | DeepSeek V3.2 (89.6%) | **+1.6%** 🏆 |

> ⚡ **결론**: LiveCodeBench에서는 오픈소스가 유료를 추월! SWE-Bench는 아직 ~9% 격차.

### 🔄 오픈소스 = 어느 유료 모델 수준?

| 오픈소스 모델 | SWE-Bench | ≈ 동등 유료 모델 | 비고 |
|--------------|:---------:|-----------------|------|
| **DeepSeek V3.2** | 72% | **Claude Sonnet 4.5** (72%) | 동급! H100×6 필요 |
| **Devstral Small 2** | 68% | Claude Sonnet 4 ~ GPT-4 (2023) | A30 24GB 가능 |
| **Qwen3-Coder-32B** | 66% | Claude Sonnet 4 | A30 24GB 가능 |
| **Kimi K2.5** | 65% | GPT-4o (구버전) | H200×8 필요 |

```
[SWE-Bench 점수 시각화]

82% ─ Claude Sonnet 5 (2026.02)
81% ─ Claude Opus 4.5
80% ─ GPT-5.2 Codex
77% ─ Gemini 3 Pro
     ────────────────────── 유료 vs 오픈소스 경계
72% ─ DeepSeek V3.2 ≈ Claude Sonnet 4.5 ⬅️
68% ─ Devstral Small 2 ≈ Claude Sonnet 4 ⬅️
66% ─ Qwen3-Coder-32B ≈ Claude Sonnet 4 ⬅️
61% ─ Claude Sonnet 4 (2025)
55% ─ GPT-4 (2023)
```

### 🎯 폐쇄망 환경 시나리오별 추천

| 시나리오 | 추천 모델 | 이유 |
|----------|----------|------|
| A30 24GB 1장 | 🆓 Devstral Small 2 | 12GB, 68% SWE-Bench |
| A100 80GB 1장 | 🆓 Qwen3-Coder-32B | 다국어, 범용 |
| 최고 성능 | 🆓 GLM-4.7/DeepSeek V3.2 | H100 × 6+ 필요 |
| 한국어 코드 | 🆓 Qwen3-Coder | 한국어 강점 |
| 긴 컨텍스트 | 🆓 Kimi K2.5 | 256K, H200 × 8 필요 |

> ⚠️ **폐쇄망 환경**에서는 유료 API 사용 불가. 모든 추천은 **오프라인 로컬 배포** 기준.

---

## 📊 벤치마크 순위 종합

### 🏆 LiveCodeBench 순위 (코드 생성)

| 순위 | 모델 | 점수 | 파라미터 | 아키텍처 |
|:----:|------|:----:|:--------:|:--------:|
| 1 | **Kimi K2.5 (Reasoning)** | ~92% | 1T (32B 활성) | MoE |
| 2 | **GLM-4.7 (Thinking)** | 89% | 355B | Dense |
| 3 | **DeepSeek V3.2** | 86% | 685B (37B 활성) | MoE |
| 4 | **Qwen3-Coder-480B** | ~85% | 480B (35B 활성) | MoE |
| 5 | **MiniMax-M2.1** | ~82% | 230B (10B 활성) | MoE |
| 6 | **Qwen3-Coder-32B** | ~78% | 32B | Dense |
| 7 | **DeepSeek Coder V2.5** | ~75% | 236B (21B 활성) | MoE |

### 🛠️ SWE-Bench Verified 순위 (소프트웨어 엔지니어링)

| 순위 | 모델 | 점수 | 특징 |
|:----:|------|:----:|------|
| 1 | Claude Opus 4.5 | 80.9% | 유료 API |
| 2 | **DeepSeek-V3.2-Speciale** | ~72% | 오픈소스 |
| 3 | **Qwen3-Max-Instruct** | 69.6% | 오픈소스 |
| 4 | **Devstral Small 2** | 68.0% | 24B, 경량 |
| 5 | **Qwen3-Coder-32B** | 66% | 범용 |
| 6 | **Kimi-Dev-72B** | ~65% | 개발 특화 |

### 💻 HumanEval 순위 (코드 완성)

| 순위 | 모델 | 점수 |
|:----:|------|:----:|
| 1 | **DeepSeek V3** | 82.6% |
| 2 | **Qwen3-Coder-32B** | ~81% |
| 3 | **GLM-4.7** | ~80% |
| 4 | StarCoder2-15B | ~72% |

---

## 🖥️ GPU VRAM 요구사항

### 소형 모델 (24GB GPU: A30, RTX 4090)

| 모델 | FP16 | 8-bit | 4-bit | 권장 |
|------|:----:|:-----:|:-----:|:----:|
| **DeepCoder-14B** | 28GB | 14GB | **7GB** | ⭐ |
| **StarCoder2-15B** | 30GB | 15GB | **8GB** | ⭐ |
| **Devstral Small 2 (24B)** | 48GB | 24GB | **12GB** | ⭐⭐⭐ |
| **Qwen3-Coder-32B** | 64GB | 32GB | **16GB** | ⭐⭐ |

### 중형 모델 (80GB GPU: A100-80GB, H100)

| 모델 | FP16 | 8-bit | 4-bit | 권장 |
|------|:----:|:-----:|:-----:|:----:|
| **Qwen3-Coder-32B** | **64GB** | 32GB | 16GB | ⭐⭐⭐ |
| **Devstral Small 2** | **48GB** | 24GB | 12GB | ⭐⭐⭐ |
| **GLM-4.7-Flash (30B)** | **60GB** | 30GB | 18GB | ⭐⭐⭐ |
| **Qwen3-Coder-Next (80B MoE)** | 170GB | 85GB | **46GB** | ⭐⭐ |
| **Kimi-Dev-72B** | 144GB | 72GB | **36GB** | ⭐⭐ |

### 대형 모델 (멀티 GPU 필요)

| 모델 | 4-bit VRAM | 권장 GPU 구성 |
|------|:----------:|--------------|
| **GLM-4.7 (355B)** | ~200GB | H100 80GB × 3 |
| **DeepSeek V3.2 (685B)** | ~380GB | H100 80GB × 6 |
| **Kimi K2.5 (1T)** | ~630GB | H200 80GB × 8 |
| **Qwen3-Coder-480B** | ~490GB | H100 80GB × 7 |

---

## 📈 모델별 상세 분석

### 1. Devstral Small 2 (24B) ⭐ A30 최적

| 항목 | 내용 |
|------|------|
| **개발사** | Mistral AI |
| **파라미터** | 24B |
| **컨텍스트** | 256K 토큰 |
| **SWE-Bench** | 68.0% |
| **4-bit VRAM** | ~12GB |
| **장점** | 코딩 특화, 가벼움, 긴 컨텍스트 |
| **단점** | 범용성 낮음 |

### 2. Qwen3-Coder-32B ⭐⭐ 가장 범용적

| 항목 | 내용 |
|------|------|
| **개발사** | Alibaba (Qwen) |
| **파라미터** | 32B |
| **SWE-Bench** | 66% |
| **LiveCodeBench** | ~78% |
| **4-bit VRAM** | ~16GB |
| **장점** | 다국어(한국어), 안정적, 범용 |
| **단점** | 최신 모델보다 낮은 점수 |

### 3. GLM-4.7 (Thinking) ⭐⭐⭐ 최고 성능

| 항목 | 내용 |
|------|------|
| **개발사** | Zhipu AI |
| **파라미터** | 355B (Full), 30B (Flash) |
| **LiveCodeBench** | 89% |
| **FP16 VRAM (Full)** | 756GB |
| **4-bit VRAM (Flash)** | ~18GB |
| **장점** | 오픈소스 최고 성능 |
| **단점** | Full 버전은 매우 무거움 |

### 4. DeepSeek V3.2 ⭐⭐ 효율적 MoE

| 항목 | 내용 |
|------|------|
| **개발사** | DeepSeek |
| **파라미터** | 685B (37B 활성) |
| **LiveCodeBench** | 86% |
| **HumanEval** | 82.6% |
| **4-bit VRAM** | ~380GB |
| **장점** | MoE로 효율적, 높은 성능 |
| **단점** | 여전히 매우 무거움 |

### 5. Kimi K2.5 ⭐⭐⭐ 오픈소스 1위

| 항목 | 내용 |
|------|------|
| **개발사** | Moonshot AI |
| **파라미터** | 1T (32B 활성) |
| **LiveCodeBench** | ~92% |
| **4-bit VRAM** | ~630GB |
| **장점** | 오픈소스 최강, 에이전트 강점 |
| **단점** | 엄청난 VRAM 요구량 |

### 6. DeepCoder-14B ⭐ 가장 가벼움

| 항목 | 내용 |
|------|------|
| **개발사** | Agentica + Together AI |
| **파라미터** | 14B |
| **LiveCodeBench** | 60.6% |
| **4-bit VRAM** | ~7GB |
| **장점** | 매우 가벼움, 코드 추론 특화 |
| **단점** | 성능 낮음 |

---

## 🎯 GPU별 최적 모델 추천

### A30 24GB

| 순위 | 모델 | 양자화 | 용도 |
|:----:|------|:------:|------|
| 🥇 | **Devstral Small 2** | 4-bit | 범용 코딩 |
| 🥈 | **Qwen3-Coder-32B** | 4-bit | 다국어 |
| 🥉 | **DeepCoder-14B** | 8-bit | 가벼운 추론 |

### A100 40GB

| 순위 | 모델 | 양자화 | 용도 |
|:----:|------|:------:|------|
| 🥇 | **Devstral Small 2** | FP16 | 최고 품질 |
| 🥈 | **Qwen3-Coder-32B** | 8-bit | 균형 |
| 🥉 | **GLM-4.7-Flash** | 8-bit | 고성능 |

### A100 80GB

| 순위 | 모델 | 양자화 | 용도 |
|:----:|------|:------:|------|
| 🥇 | **Qwen3-Coder-32B** | FP16 | 최고 품질 |
| 🥈 | **GLM-4.7-Flash** | FP16 | 고성능 |
| 🥉 | **Qwen3-Coder-Next 80B** | 4-bit | 에이전트 |

### H100 80GB × 4+

| 순위 | 모델 | 양자화 | 용도 |
|:----:|------|:------:|------|
| 🥇 | **GLM-4.7 (355B)** | 4-bit | 최강 성능 |
| 🥈 | **DeepSeek V3.2** | 4-bit | MoE 효율성 |
| 🥉 | **Kimi K2.5** | 4-bit | 오픈소스 1위 |

---

## ✅ 최종 결론

| 질문 | 답변 |
|------|------|
| **A30 24GB 최고는?** | **Devstral Small 2** (SWE-Bench 68%) |
| **A100 80GB 최고는?** | **Qwen3-Coder-32B** (FP16, 범용) |
| **오픈소스 절대 1위는?** | **Kimi K2.5** (H200 × 8 필요) |
| **현실적 엔터프라이즈?** | **GLM-4.7-Flash** + **DeepSeek V3.2** (H100 클러스터) |

---

## 📚 참고 자료 및 벤치마크 사이트

### 벤치마크 리더보드

| 벤치마크 | 링크 | 설명 |
|----------|------|------|
| **LiveCodeBench** | [livebench.ai](https://livebench.ai) | 코드 생성 능력 평가 |
| **SWE-Bench** | [swebench.com](https://www.swebench.com) | 실제 GitHub 버그 해결 |
| **HumanEval** | [GitHub](https://github.com/openai/human-eval) | OpenAI 코드 완성 벤치마크 |
| **Aider Polyglot** | [aider.chat/leaderboard](https://aider.chat/docs/leaderboards/) | 다국어 코드 편집 |
| **UGI Leaderboard** | [HuggingFace](https://huggingface.co/spaces/DontPlanToEnd/UGI-Leaderboard) | 종합 LLM 평가 |

### LLM 분석 사이트

| 사이트 | 링크 | 설명 |
|--------|------|------|
| **WhatLLM** | [whatllm.org](https://whatllm.org) | LLM 순위 및 비교 |
| **Artificial Analysis** | [artificialanalysis.ai](https://artificialanalysis.ai) | 성능/비용 분석 |
| **Vellum AI** | [vellum.ai/llm-leaderboard](https://www.vellum.ai/llm-leaderboard) | 종합 리더보드 |
| **LLM Stats** | [llm-stats.com](https://llm-stats.com) | VRAM 요구량 계산기 |

### 모델 공식 페이지

| 모델 | HuggingFace |
|------|-------------|
| **Qwen3-Coder** | [Qwen/Qwen3-Coder-32B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-32B-Instruct) |
| **Devstral Small 2** | [mistralai/devstral-small-2](https://huggingface.co/mistralai/devstral-small-2-2505) |
| **GLM-4.7** | [THUDM/GLM-4.7](https://huggingface.co/THUDM) |
| **DeepSeek V3** | [deepseek-ai/DeepSeek-V3](https://huggingface.co/deepseek-ai/DeepSeek-V3) |

---

> 📅 마지막 업데이트: 2026년 2월 6일

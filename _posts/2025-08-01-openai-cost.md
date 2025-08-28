---
layout: post
title:  OpenAI model comparison
categories: [LLM, OpenAI]
excerpt: Because the way OpenAI name their models are confusing af
---

<style>
#cost-comparison + table {
  width: 100%;
}
#cost-comparison + table th:nth-child(1),
#cost-comparison + table td:nth-child(1) {
  width: 20%;

}
#cost-comparison + table th:nth-child(2),
#cost-comparison + table td:nth-child(2) {
  width: 12%;

}
#cost-comparison + table th:nth-child(3),
#cost-comparison + table td:nth-child(3) {
  width: 12%;

}
#cost-comparison + table th:nth-child(4),
#cost-comparison + table td:nth-child(4) {
  width: 56%;
}
</style>

Notes for myself

# o‑series reasoning models
* o3: flagship reasoning model with private chain-of-thought.
* o3-mini, o3-mini-high: compact versions with varying reasoning effort levels.
* o3-pro: highly compute‑intensive variant for maximum reliability.
* o4-mini and o4-mini-high: successors to o3-mini, released April 2025; support images and tool‑calling within chain‑of‑thought.
* o3-2025-04-16 is ranked high in LM Arena across various categories.

# GPT-4.x
* Multimodal: handles text, images, audio natively.
* Supports tool‑calling and web search within Responses API
* Includes gpt-4o and lightweight gpt-4o-mini variants
* Includes gpt-4.1, gpt-4.1-mini, and ultra‑fast gpt-4.1-nano
* chatgpt-4o-latest-20250326 ranks just below  o3-2025-04-16 on LM Arena

# Cost Comparison

| Model             | Input ($/M tokens) | Output ($/M tokens) | Notes                                                                  |
| ----------------- | ------------------ | ------------------- | ---------------------------------------------------------------------- |
| GPT-4o            | ~$2.50             | ~$10.00             |                                                                        |
| GPT-4o-mini       | $0.15              | $0.60               | ([Reuters][1])                                                         |
| GPT-4.1           | $2.00              | $8.00               | ([Zapier][2], [OpenAI Community][3])                                   |
| GPT-4.1-mini      | $0.40              | $1.60               | ([Zapier][2])                                                          |
| GPT-4.1-nano      | $0.10              | $0.40               | ([Zapier][2])                                                          |
| **o3-mini**       | $1.10              | $4.40               | ([Inc.com][4], [API.chat][5])                                          |
| **o3-mini-high**  | $1.10              | $4.40               | High-effort variant, same pricing tiers ([Wikipedia][6], [Inc.com][4]) |
| **o3 (standard)** | $2.00              | $8.00               | Matches GPT-4.1 pricing now ([Zapier][2], [OpenAI Community][7])       |
| **o3-pro**        | $20.00             | $80.00              | Pro reasoning tier ([Zapier][2], [OpenAI Community][7])                |
| **o4-mini**       | $1.10              | $4.40               | ([OpenAI Platform Compare][8])                                         |


[1]: https://www.reuters.com/technology/artificial-intelligence/openai-unveils-cheaper-small-ai-model-gpt-4o-mini-2024-07-18/?utm_source=chatgpt.com "OpenAI unveils cheaper small AI model GPT-4o mini"
[2]: https://zapier.com/blog/openai-o1/?utm_source=chatgpt.com "What are OpenAI o3 and o4? - Zapier"
[3]: https://community.openai.com/t/is-the-api-pricing-for-gpt-4-1-mini-and-o3-really-identical-now/1286911?utm_source=chatgpt.com "Is the API pricing for GPT-4.1 mini and o3 really identical now?"
[4]: https://www.inc.com/ben-sherry/openai-just-released-o3-mini-its-most-cost-efficient-model-yet/91141869?utm_source=chatgpt.com "OpenAI Just Released o3-mini, Its Most Cost-Efficient Model Yet"
[5]: https://api.chat/models/chatgpt-o3-mini/price/?utm_source=chatgpt.com "OpenAI ChatGPT o3-mini Price - API.chat"
[6]: https://en.wikipedia.org/wiki/OpenAI_o3?utm_source=chatgpt.com "OpenAI o3"
[7]: https://community.openai.com/t/o3-is-80-cheaper-and-introducing-o3-pro/1284925?utm_source=chatgpt.com "O3 is 80% cheaper and introducing o3-pro - Announcements"
[8]: https://platform.openai.com/docs/models/compare
import os
import asyncio
import pickle
import random
from llama_parse import LlamaParse
from llama_index.llms.groq import Groq
from aiohttp import ClientSession
from llama_index.llms.deepinfra import DeepInfraLLM
import openai
import json

# Initialize LlamaParse and Groq
LlamaParseAPIKeys = os.environ["LLAMA_PARSE_API_KEYS"].split(",")
GroqAPIKeys = os.environ["DEEPINFRA_API_KEYS"].split(",")
ModelName = "microsoft/WizardLM-2-8x22B"

llama_parsers = [
    LlamaParse(api_key=k, result_type="markdown") for k in LlamaParseAPIKeys
]
llms = [
    openai.OpenAI(
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=k,
    )
    for k in GroqAPIKeys
]


def generate_distill_prompt(contents, max_tokens=50000):
    truncated_contents = truncate_contents(
        [content.text for content in contents], max_tokens - 1000
    )  # Reserve tokens for the prompt

    prompt = f"""
You are an AI assistant tasked with analyzing a financial research paper and providing ONLY and ONLY a JSON list of any trading strategies mentioned in it that you have extracted. The strategies you identify will be used as inputs to an agentic framework that generates alpha expressions.

Your task is to thoroughly review the research paper provided in the following Markdown-formatted documents, delineated by [PAPER]:

[PAPER]
{truncated_contents}
[PAPER]

Please provide your analysis in a clear and structured manner, as ONLY and ONLY a JSON list (in the format {'{"trading_strategy": "name_of_trading_strategy", "description": "your_trading_strategy"}'}, in the following way ONLY:
- If the research paper does not explicitly discuss any trading strategies, please simply return an empty JSON list ([]) and nothing else.
- For each trading strategy identified, provide a detailed summary of the idea of the trading alpha and detailed implementation details that includes the following elements:
1. Specific trading strategies or approaches discussed in the paper. This included:
   - Long/short strategies
   - Factor-based strategies
   - Statistical arbitrage strategies
   - Momentum or mean-reversion strategies
   - Any other novel or unique trading strategies introduced in the paper
2. Important details about the implementation of the trading strategies, including:
   - Required data inputs or signals
   - Timeframes or holding periods
   - Portfolio construction or risk management techniques
   - Backtesting or simulation results
3. Any and all other relevant information that could be useful for translating the trading strategies into executable alpha expressions. If you can include mathematical formulas, do so.

Remember, the ultimate goal is to use the extracted strategies as inputs for generating alpha expressions. So, aim to provide a comprehensive and actionable summary that captures the essential elements of any trading strategies present in the paper.

Please write the JSON list ONLY below:
"""
    return prompt.strip()


def create_alphas_from_paper(content):
    res = random.choice(llms).chat.completions.create(
        messages=[{"role": "user", "content": generate_distill_prompt(content)}],
        model="microsoft/WizardLM-2-8x22B",
        response_format={"type": "json_object"},
        tool_choice="auto",
        temperature=0.3,
        max_tokens=5000,
    )
    json_text = res.choices[0].message.content
    substring = json_text[json_text.find("[") : json_text.rfind("]") + 1]
    print("Alphas identified")
    print(substring)
    return json.loads(substring, strict=False)


def create_alphas_from_strategy(txtpath):
    with open(txtpath, "r") as f:
        content = f.read()

    return {
        "trading_strategy": txtpath.split("/")[-1].split("\\")[-1],
        "description": content,
    }


def truncate_contents(contents, max_tokens):
    truncated_contents = []
    token_count = 0

    for content in contents:
        content_tokens = len(content.split())
        if token_count + content_tokens <= max_tokens:
            truncated_contents.append(content)
            token_count += content_tokens
        else:
            remaining_tokens = max_tokens - token_count
            truncated_content = " ".join(content.split()[:remaining_tokens])
            truncated_contents.append(truncated_content)
            break

    return "\n".join(truncated_contents)

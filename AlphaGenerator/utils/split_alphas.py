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
GroqAPIKeys = os.environ["DEEPINFRA_API_KEYS"].split(",")

llms = [
    openai.OpenAI(
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=k,
    )
    for k in GroqAPIKeys
]
map = {
    "fundamental": ["industry"],
    "analyst": ["industry"],
    "model": ["industry", "subindustry", "sector", "market"],
    "news": ["subindustry"],
    "price-volume": ["market", "sector"],
    "social-media": ["industry", "subindustry"],
    "sentiment": ["industry", "subindustry"],
    "earnings": ["industry"],
    "macro": ["market", "sector", "industry"],
}


def generate_neutralization_prompt(alpha, max_tokens=50000):

    prompt = f"""
You are an AI assistant tasked with analyzing a financial alpha and the datasets used in it and providing ONLY and ONLY a JSON object of classifying the financial alpha into one of a few categories.

Your task is to thoroughly review the alpha given deliated by [ALPHA]:

[ALPHA]
{alpha[0]}
[ALPHA]

You need to categorize it into one of the following categories, in the format {'{"category": "<category>"}'}:
{map.keys()}

Please write the JSON object ONLY below:
"""

    return prompt.strip()


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


def prune_datasets(alphas):
    new_alphas = []
    for alpha in alphas:
        dts = []
        for data in alpha["datasets"]:
            if data["field"] in alpha["code"]:
                dts.append(data)
        alp = alpha
        alp["datasets"] = dts
    return new_alphas


def split_alphas_neut(alphas):
    appended_alphas = []
    for alpha in alphas:
        prompt = generate_neutralization_prompt([alpha])
        res = random.choice(llms).chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/Mistral-7B-Instruct-v0.3",
            response_format={"type": "json_object"},
            tool_choice="auto",
            temperature=0.2,
            max_tokens=1000,
        )
        json_text = res.choices[0].message.content
        substring = json_text[json_text.find("{") : json_text.rfind("}") + 1]
        datasets = json.loads(substring, strict=False)
        print("Neutralizations classified")
        print(substring)
        alphak = alpha
        alphak["neutralizations"] = map[datasets["category"]]
        appended_alphas.append(alphak)
    return appended_alphas


def split_alphas_region(alphas):
    new_alphas = []
    for alpha in alphas:
        alphak = alpha
        alphak["region"] = "CHN"
        new_alphas.append(alphak)

        # alphak = alpha
        # alphak["region"] = "USA"
        # new_alphas.append(alpha)
    return new_alphas

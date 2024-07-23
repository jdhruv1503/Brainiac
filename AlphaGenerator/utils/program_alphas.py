import os
import json
from llama_parse import LlamaParse
from llama_index.llms.groq import Groq
from aiohttp import ClientSession
from llama_index.llms.deepinfra import DeepInfraLLM
import openai
import random
import asyncio

# Initialize LlamaParse and Groq
GroqAPIKeys = os.environ["DEEPINFRA_API_KEYS"].split(",")

llms = [
    openai.OpenAI(
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=k,
    )
    for k in GroqAPIKeys
]

# Assuming the initialization of LlamaParse, Groq, and LLMs is done similarly as in distill_alphas.py


def generate_dataset_prompt(alphas, max_tokens=50000):
    if alphas[0]["region"] == "CHN":
        dataset = "utils\\BrainKnowledgebaseSyntax\\datasets_chn.md"
    else:
        dataset = "utils\\BrainKnowledgebaseSyntax\\datasets_usa.md"
    with open(dataset, "r") as f:
        table = f.read()

    truncated_alphas = truncate_alphas(
        [alpha["description"] for alpha in alphas], max_tokens - 1000
    )  # Reserve tokens for the prompt

    prompt = f"""
    You are an AI assistant tasked with analyzing a trading strategy and providing ONLY a JSON list of datasets from a predefined list that are relevant to the strategy. Your task is to thoroughly review the strategy provided below, delineated by [ALPHA]:

    [ALPHA]
    {truncated_alphas[0]}
    [ALPHA]

    Here is the predefined list of datasets you can choose from:
    {table}

    Please provide your analysis in a clear and structured manner, as ONLY a JSON list (in the format {'{"field": "field", "description": "description", "dataset": "dataset"}'}, in the following way ONLY:
    - Have a maximum of 10-15 most relevant datasets, and minimize redundant datasets.
    - The datasets should be directly related to the strategy's implementation or testing - look for financial keywords.
    - For each strategy, identify and list the datasets that are relevant based on the strategy's description.
    - Include datasets that could be used to implement or test the strategy, focusing on the data inputs or signals mentioned.
    - If a strategy does not require specific datasets or if the relevance is unclear, you may omit it from your response.

    Remember, the goal is to use the extracted datasets as inputs for generating alpha expressions. So, aim to provide a comprehensive and actionable summary that captures the essential datasets present in the strategy descriptions.

    Please write the JSON list ONLY below:
    """
    return prompt.strip()


def truncate_alphas(alphas, max_tokens):
    truncated_alphas = []
    token_count = 0

    for alpha in alphas:
        alpha_tokens = len(alpha.split())
        if token_count + alpha_tokens <= max_tokens:
            truncated_alphas.append(alpha)
            token_count += alpha_tokens
        else:
            remaining_tokens = max_tokens - token_count
            truncated_alpha = " ".join(alpha.split()[:remaining_tokens])
            truncated_alphas.append(truncated_alpha)
            break

    return "\n".join(truncated_alphas)


def find_datasets_from_alphas(alphas):
    # appended_alphas = []
    # for alpha in alphas:
    #     prompt = generate_dataset_prompt([alpha])
    #     res = random.choice(llms).chat.completions.create(messages=[{"role": "user", "content": prompt}], model="mistralai/Mixtral-8x22B-Instruct-v0.1",
    #                                            response_format={"type": "json_object"},
    #                                            tool_choice="auto",
    #                                            temperature=0.2,
    #                                            max_tokens=1500)
    #     json_text = (res.choices[0].message.content)
    #     substring = json_text[json_text.find("["):json_text.rfind("]") + 1]
    #     datasets =  json.loads(substring,strict=False)
    #     print("Datasets Found")
    #     print(substring)
    #     alphak = alpha
    #     alphak["datasets"] = datasets
    #     appended_alphas.append(alphak)
    # return appended_alphas
    return alphas


def generate_code_prompt(alphas, max_tokens=50000):
    with open(
        os.path.join("utils", "BrainKnowledgebaseSyntax", "syntax.md"),
        "r",
        errors="ignore",
        encoding="utf-8",
    ) as f:
        syntax = f.read()

    if alphas[0]["region"] == "CHN":
        dataset = os.path.join("utils", "BrainKnowledgebaseSyntax", "datasets_chn.md")
    else:
        dataset = os.path.join("utils", "BrainKnowledgebaseSyntax", "datasets_usa.md")
    with open(dataset, "r") as f:
        table = f.read()

    prompt = f"""
    You are an AI assistant tasked with analyzing a trading strategy and providing ONLY a JSON object with the code to the alpha in WorldQuant Fast Expression Language. Your task is to thoroughly review the strategies provided below, delineated by [ALPHA]:

    [ALPHA]
    {alphas[0]}
    [ALPHA]

    IMPORTANT: Here are the exhaustive list of datasets you are allowed to use, along with coverage (higher is better) and the number of people using it in their alphas:
    {table}

    Here is an overview of the operators of the language you have to use:
    {syntax}

    Please provide your code, as ONLY a JSON object (in the format {'{"code": "<your code>"}'}, in the following way ONLY:
    - Use the relevant datasets I have given you as part of the alpha. However, only use the datasets you need. Remember, keep the alpha simple and use only the operators and dataset you need.
    - VERY IMPORTANT: ONLY use the given datasets as variables. No other variables are allowed.
    - In simple terms, BRAIN platform uses an Alpha to create a vector of weights, with each weight corresponding to one of the stocks in the selected universe. This creates a portfolio for each day in the simulation period, which can then be used to calculate that day's Profit and Loss (PnL).

    Please write the JSON with the code ONLY below:
    """
    return prompt.strip()


def create_code_from_alphas(alphas):
    appended_alphas = []
    for alpha in alphas:
        prompt = generate_code_prompt([alpha])
        res = random.choice(llms).chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/Mixtral-8x22B-Instruct-v0.1",
            response_format={"type": "json_object"},
            tool_choice="auto",
            temperature=0.13,
            max_tokens=1000,
        )
        json_text = res.choices[0].message.content
        substring = json_text[json_text.find("{") : json_text.rfind("}") + 1]
        if substring == "":
            print("Code not generated")
            continue
        print("Code Generated")
        print(substring)
        try:
            datasets = json.loads(substring, strict=False)
        except:
            print("Error in JSON")
            continue
        alphak = alpha
        alphak["code"] = datasets["code"]
        appended_alphas.append(alphak)
    return appended_alphas

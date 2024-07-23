import os
import asyncio
import json
import pickle
import random
from aiohttp import ClientSession
from utils.distill_alphas import create_alphas_from_strategy
from utils.program_alphas import create_code_from_alphas, find_datasets_from_alphas
from utils.split_alphas import split_alphas_region, split_alphas_neut
import nest_asyncio
nest_asyncio.apply()


async def process_txt(txt_path, session):

    base_name = (txt_path).replace('.pdf', '')

    if os.path.exists(base_name + '.alphas.json'):
        with open(base_name + '.alphas.json', 'r') as f:
            alphas = json.load(f)
            return alphas

    
    if os.path.exists(base_name + '.alphas_init.json'):
        with open(base_name + '.alphas_init.json', 'r') as f:
            alphas = json.load(f)
    else:
        alphas = [create_alphas_from_strategy(txt_path)]
        print("splitting", alphas)
        alphas = split_alphas_region(alphas)
        with open(base_name + '.alphas_init.json', 'w') as f:
            json.dump(alphas, f)
    
    if os.path.exists(base_name + '.datasets_from_alphas.json'):
        with open(base_name + '.datasets_from_alphas.json', 'r') as f:
            alphas = json.load(f)
    else:
        alphas = find_datasets_from_alphas(alphas)
        with open(base_name + '.datasets_from_alphas.json', 'w') as f:
            json.dump(alphas, f)

    if os.path.exists(base_name + '.code_from_alphas.json'):
        with open(base_name + '.code_from_alphas.json', 'r') as f:
            alphas = json.load(f)
    else:
        alphas = create_code_from_alphas(alphas)
        with open(base_name + '.code_from_alphas.json', 'w') as f:
            json.dump(alphas, f)
    
    if os.path.exists(base_name + '.alphas.json'):
        with open(base_name + '.alphas.json', 'r') as f:
            alphas = json.load(f)
    else:
        alphas = split_alphas_neut(alphas)
        with open(base_name + '.alphas.json', 'w') as f:
            json.dump(alphas, f)
    
    return alphas

async def strategies_main():
    pdf_dir = "Strategies"
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.txt')]
    
    async with ClientSession() as session:
        tasks = [process_txt(pdf, session) for pdf in pdf_files]
        alphas = await asyncio.gather(*tasks)
        
        # Output alphas to a text file
        with open("alphas.jsonl", "a") as file:
            for alpha in alphas:
                for alp in alpha:
                    file.write(str(alp).replace("'",'"')+"\n")

if __name__ == "__main__":
    asyncio.run(strategies_main())
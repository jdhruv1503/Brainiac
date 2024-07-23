import os
import asyncio
import json
import pickle
import random
from llama_parse import LlamaParse
from aiohttp import ClientSession
from utils.distill_alphas import create_alphas_from_paper
from utils.program_alphas import create_code_from_alphas, find_datasets_from_alphas
from utils.split_alphas import split_alphas_region, split_alphas_neut
import nest_asyncio
nest_asyncio.apply()

# Initialize LlamaParse and Groq
LlamaParseAPIKeys = ["llx-rYKXT1N6DHvtNcuCNBiOOsq9529SpE5hZnmk8Wr6QSkVmkxz"]

llama_parsers = [LlamaParse(api_key=k,
    result_type="markdown") for k in LlamaParseAPIKeys]


async def process_pdf(pdf_path, session):

    base_name = (pdf_path).replace('.pdf', '')

    if os.path.exists(base_name + '.alphas.json'):
        with open(base_name + '.alphas.json', 'r') as f:
            alphas = json.load(f)
            return alphas

    # Check if pdf was processed
    if os.path.exists(pdf_path.replace('.pdf', '.pkl').replace('.PDF', '.pkl')):
        with open(pdf_path.replace('.pdf', '.pkl').replace('.PDF', '.pkl'), 'rb') as f:
            content = pickle.load(f)
            print("Found parsed pdf")
    else:
        # Parse PDF
        content = random.choice(llama_parsers).load_data(pdf_path)
        if os.path.exists(pdf_path.replace('.pdf', '.txt').replace('.PDF', '.txt')):
            with open(pdf_path.replace('.pdf', '.txt').replace('.PDF', '.txt'), 'r', errors="ignore") as f:
                content[0].text = "THE MAIN IDEA FOR ALPHAS FOR THIS RESEARCH PAPER:\n" + f.read() + "\n-----------\n" + content[0].text
        with open(pdf_path.replace('.pdf', '.pkl').replace('.PDF', '.pkl'), 'wb') as f:
            print("Parsed pdf")
            pickle.dump(content, f)

    if os.path.exists(base_name + '.alphas_init.json'):
        with open(base_name + '.alphas_init.json', 'r') as f:
            alphas = json.load(f)
    else:
        alphas = create_alphas_from_paper(content)
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

async def research_main() -> None:
    pdf_dir = "ResearchPDFs"
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    async with ClientSession() as session:
        tasks = [process_pdf(pdf, session) for pdf in pdf_files]
        alphas = await asyncio.gather(*tasks)
        
        # Output alphas to a text file
        with open("alphas.jsonl", "w") as file:
            for alpha in alphas:
                for alp in alpha:
                    file.write(str(alp).replace("'",'"')+"\n")

if __name__ == "__main__":
    asyncio.run(research_main())
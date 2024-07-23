import json
import os

import requests

def simsend():
    with open("alphas.jsonl", "r", errors="ignore", encoding='cp1252') as file:
        alphas = file.readlines()

    if os.path.exists("done_alphas.jsonl"):
        with open("done_alphas.jsonl", "r", encoding="cp1252", errors="ignore") as file:
            done_alphas = file.readlines()
    else:
        done_alphas = []

    def safe_load_json(entry):
        """Attempt to load JSON from an entry, returning None on failure."""
        try:
            return json.loads(entry)
        except (json.JSONDecodeError, ValueError):
            return None

    # Filter and load valid JSON entries
    alphas = [safe_load_json(alpha) for alpha in alphas if alpha.strip()!= "" and alpha not in done_alphas and safe_load_json(alpha) is not None]

    # Now, valid_alphas contains only successfully parsed JSON objects

    newalphas = []
    for alpha in alphas:
        newalphas_temp = []
        
        if alpha['region'] == 'CHN':
            universes = ['TOP2000', 'TOP3000']
        else:
            universes = ['TOP200', 'TOP500', 'TOP1000', 'TOP3000']
        
        for universe in universes:
            for neut in alpha['neutralizations']:
                tempalpha = {
                    'code': alpha['code'],
                    'delay': 1,
                    'universe': universe,
                    'truncation': 0.1,
                    'region': alpha['region'],
                    'decay': 3,
                    'neutralization': neut.upper(),
                    'pasteurization': 'ON',
                    'nanHandling': 'OFF'
                }
                newalphas_temp.append(tempalpha)
        
        newalphas.extend(newalphas_temp)

    try:
        a = requests.post('http://localhost:8000/add_alphas', json=newalphas)
        print(json.dumps(newalphas))
        print(a.json())
        if not os.path.exists("done_alphas.jsonl"):
            with open("done_alphas.jsonl", "w") as file:
                file.write("\n".join([str(alp).replace("'",'"') for alp in alphas]))
        else:
            with open("done_alphas.jsonl", "a") as file:
                file.write("\n".join([str(alp).replace("'",'"') for alp in alphas]))
        
        os.remove("alphas.jsonl")

        print("Sent to simulator")

    except Exception as e:
        print("fuck")
        print(e)

if __name__=="__main__":
    simsend()
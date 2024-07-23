import subprocess
import asyncio
from generate_from_research_pdfs import research_main
from generate_from_strategies import strategies_main
from send_to_simulation import simsend as simulation_send

async def scheduler():
    while True:
        print("Pulling latest")
        try:
            # Perform git pull
            subprocess.check_call(['git', 'pull'])
            
            print("Git pull completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute git pull: {e}")


        # Execute the main function from generate_from_research_pdfs.py
        print("Making from papers")
        await research_main()
        
        # Execute the main function from generate_from_strategies.py
        print("Making from strat")
        await strategies_main()

        print("Sending to sim")
        simulation_send()
        
        # Wait for 60 seconds before executing again
        print("Waiting for 60")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scheduler())
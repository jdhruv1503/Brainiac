.PHONY: setup smoke demo

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

smoke:
	. .venv/bin/activate && python -m compileall AlphaGenerator Simulation
	. .venv/bin/activate && python -c "import sys; sys.path.append('Simulation'); import main as simulation_main; print('simulation import ok')"
	. .venv/bin/activate && python -c "import sys; sys.path.append('AlphaGenerator'); import send_to_simulation; print('alpha sender import ok')"

demo: setup smoke
	@echo "Demo prerequisites are ready."
	@echo "1) Copy .env.example to .env and export variables"
	@echo "2) Put credential JSON files in Simulation/creds"
	@echo "3) Run: cd Simulation && python main.py"
	@echo "4) Run: cd AlphaGenerator && python watchdog.py"

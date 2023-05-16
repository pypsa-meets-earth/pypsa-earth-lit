# Makefile

get_data:
	echo "Load pypsa-earth test data"
	python pypsa-earth-lit/app/repo.py
	echo "Download successful. Stored in tauritron-project/pypsa-earth"

install_env:
	pip install -r pypsa-earth-lit/requirements.txt

run_app:
	streamlit run pypsa-earth-lit/app/index.py
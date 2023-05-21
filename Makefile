# Makefile

get_data:
	echo "Load pypsa-earth test data"
	python pypsa-earth-lit/app/repo.py
	echo "Download successful. Stored in tauritron-project/pypsa-earth"

run_app:
	streamlit run app/index.py
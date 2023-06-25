# pypsa-earth-lit

Testing streamlit module that works along a stable pypsa-earth package version

## Test setup

For building up to interface on a PyPSA-Earth test version, I precompiled a couple of pypsa-earth results and shared them on zenodo. We will download the whole pypsa-earth folder with the results for testing purpose.

Follow the following commands line by line to setup everything. In particular, the commands will retrieve data, setup the environment and run the app:

```bash
mkdir tauritron-project
cd tauritron-project
git clone https://github.com/pypsa-meets-earth/pypsa-earth-lit.git

# depending on what you need. Recommended order.
make -f ./pypsa-earth-lit/Makefile get_data
conda env create -f ./pypsa-earth-lit/env.yaml
conda activate pypsa-earth-lit
cd pypsa-earth-lit
pip install -e .
make -f ./Makefile run_app
```

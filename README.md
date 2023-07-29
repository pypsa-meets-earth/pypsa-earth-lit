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

This project is organized with distinct sections, 'pre_run' and 'tools,' both located in the 'utils' folder.The 'tools' section serves a crucial role by importing the 'pypsa' networks and the configuration file, both of which are required across various sections. Moving on to the 'prerun' files, their primary purpose is to prepare dataframes using the imported data. Specifically, they process and manipulate the data obtained from the 'pypsa' networks and extract meaningful information to create the necessary dataframes Subsequently, this processed data is utilized to create informative plots stored in files of pages folder.

Additionally, to enhance user-friendliness, we utilize a config file to define meaningful 'nicenames' and units for the parameters present in our dataframes. These nicenames make it easier for users to understand and interact with the data effectively.

contributions can be made in 'get_edges_df' and 'get_spatial_values_df' functions in the 'spatial_pre_run' file.

'get_edges_df': This function is responsible for fetching data and constructing a dataframe related to edges.

'get_spatial_values_df' function: This function is involved in retrieving spatial data and generating a corresponding dataframe.

To contribute, you can enrich this function by integrating additional spatial data or enhancing the existing data processing logic. The comments within the function will serve as helpful pointers.

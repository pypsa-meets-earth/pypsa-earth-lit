"""Script to download repo data.

Download file will be a folder next to pypsa-earth-lit

Example:
--------
tauriton_project/pypsa-earth
tauriton_project/pypsa-earth-lit
"""
import os
import logging
from zipfile import ZipFile

logger = logging.getLogger(__name__)


def progress_retrieve(url, file, data=None, disable_progress=False, roundto=1.0):
    """
    Function to download data from a url with a progress bar progress in retrieving data

    Parameters
    ----------
    url : str
        Url to download data from
    file : str
        File where to save the output
    data : dict
        Data for the request (default None), when not none Post method is used
    disable_progress : bool
        When true, no progress bar is shown
    roundto : float
        (default 0) Precision used to report the progress
        e.g. 0.1 stands for 88.1, 10 stands for 90, 80
    """
    import urllib
    from urllib import request

    from tqdm import tqdm

    pbar = tqdm(total=100, disable=disable_progress)

    def dlProgress(count, blockSize, totalSize, roundto=roundto):
        pbar.n = round(count * blockSize * 100 / totalSize / roundto) * roundto
        pbar.refresh()

    if data is not None:
        data = urllib.parse.urlencode(data).encode()

    request.urlretrieve(url, file, reporthook=dlProgress, data=data)


def download_and_unzip_zenodo(url, rootpath, destination_path, hot_run=True, disable_progress=False):
    """
    Function to download and unzip the data from zenodo

    Inputs
    ------
    config : Dict
        Configuration data for the category to download
    rootpath : str
        Absolute path of the repository
    hot_run : Bool (default True)
        When true the data are downloaded
        When false, the workflow is run without downloading and unzipping

    Outputs
    -------
    True when download is successful, False otherwise

    """
    file_path = os.path.join(rootpath, "tempfile.zip")
    destination_path = destination_path
    url = url
    if hot_run:
        progress_retrieve(url, file_path, disable_progress=disable_progress)
        try:
            with ZipFile(file_path, "r") as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall(path=destination_path)
            os.remove(file_path)
            logger.info(f"Downloaded resource from cloud '{url}'.")
        except:
            logger.warning(f"Failed download resource from cloud '{url}'.")
            return False

    return True


# execute function here
if __name__ == "__main__":
    from pathlib import Path

    url = "https://sandbox.zenodo.org/record/1202789/files/pypsa-earth.zip?download=1"
    rootpath = Path(__file__).resolve().parents[2]
    download_and_unzip_zenodo(url, rootpath, destination_path=".")
    

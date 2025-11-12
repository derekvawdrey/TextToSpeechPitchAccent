# Instructions

1. Create two conda environments, one for the dataDownload notebook, an one for the dataPrepPipeline notebook. For some reason when I mix the two dependencies, it breaks mfa. Python 3.11 works well with the dataPrepPipeline, and for some reason I could only get python 3.10 to work for the dataprepPipeline. For some reason torchaudio uses a different library 
2. Run the dataDownload ipynb script to download the necessary kokoro scripts
3. Run the dataPrepPipeline script to prepare all the data
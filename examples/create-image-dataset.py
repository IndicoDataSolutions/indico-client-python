"""
Creating an Image Dataset from Local PNGs/JPGs

There are two ways two create a data of PNGs/JPGs depending on whether the images are
stored locally on your computer or at a publicly accessible URL. The code snippet 
below shows you what to do if the images are on your computer.
"""

from indico import IndicoClient, IndicoConfig
from indico.queries import CreateDataset
import pandas as pd

# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)


# With local images you should create a CSV formatted (here for demonstration) like below
# Where one column contains the paths from the csv to where the images are stored on your computer
image_dataset = pd.DataFrame()
image_dataset["image_files"] = [
    "./path/from/csv/to/image.png",
    "./path/from/csv/to/image2.png",
]
image_dataset.to_csv("./image_dataset.csv", index=False)

# Use the CSV you created (like above) to create the dataset
dataset = client.call(
    CreateDataset(
        name="My Image Dataset",
        files="./image_dataset.csv",
        from_local_images=True,
        image_filename_col="image_files",  # specify the columns containing the images
    )
)

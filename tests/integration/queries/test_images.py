from pathlib import Path
from indico.client import IndicoClient


def test_image_upload(indico):
    # client = IndicoClient()
    image_base_path = Path(__file__).parents[1] / "data"
    image_paths = [str(image_base_path / f"img{i}.png") for i in range(2)]


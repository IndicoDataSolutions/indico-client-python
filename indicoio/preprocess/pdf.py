from pathlib import Path
import base64


def pdf_preprocess(pdf):
    """
    Load pdfs from local filepath if not already b64 encoded
    """
    path = Path(pdf)
    if path.exists():
        # a filepath is provided, read and encode
        with path.open("rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        # assume pdf is already b64 encoded
        return pdf

from pathlib import Path
import logging

from unittest import TestCase
from indicoio.api.prebuilt import IndicoApi

logging.getLogger("indicoio").setLevel(logging.DEBUG)


class PDFExtractionTests(TestCase):
    def setUp(self):
        super().setUp()
        self.indicoapi = IndicoApi(config_options={"host": "dev.indico.io"})

    def test_pdf_extraction_url(self):
        results = self.indicoapi.pdf_extraction(
            ["http://www.pdf995.com/samples/pdf.pdf"]
        )
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)
        for field in ("metadata", "pages"):
            self.assertIn(field, results[0])

    def test_pdf_extraction_file(self):
        path = Path(__file__).parent / "data" / "mock.pdf"
        results = self.indicoapi.pdf_extraction([path])
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)
        for field in ("metadata", "pages"):
            self.assertIn(field, results[0])

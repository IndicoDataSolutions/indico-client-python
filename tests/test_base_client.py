import logging

from unittest import TestCase
from indicoio.api.base import Indico

logging.getLogger("indicoio").setLevel(logging.DEBUG)


class BaseRequestProxy(TestCase):
    def setUp(self):
        super().setUp()
        self.indico = Indico(host="dev.indico.io")

    def test_list_model_groups(self):
        results = self.indico.model_groups()
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIn("id", result)
            self.assertIn("name", result)

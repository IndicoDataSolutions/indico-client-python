import logging

from unittest import TestCase
from indicoio.api import ModelGroup, Indico

logging.getLogger("indicoio").setLevel(logging.DEBUG)


# class BaseRequestProxy(TestCase):
#     def setUp(self):
#         super().setUp()
#         self.indico = Indico(config_options={"host": "dev.indico.io"})
#         results = self.indico.model_groups()

#     def test_list_model_groups(self):
#         results = self.indico.model_groups()
#         self.assertIsInstance(results, list)
#         for result in results:
#             self.assertIn("id", result)
#             self.assertIn("name", result)

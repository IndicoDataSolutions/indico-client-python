import logging

from unittest import TestCase
from indicoio.api import Indico

logging.getLogger("indicoio").setLevel(logging.DEBUG)


class ModelGroupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        indico = Indico(config_options={"host": "dev.indico.io"})
        results = indico.model_groups()
        try:
            cls.model_group = next(
                result
                for result in results
                if not result["retrainRequired"] and result["status"] == "COMPLETE"
            )
        except StopIteration:
            raise AssertionError(
                "The authenticated user does not have a successfully trained model"
            )

    def test_model_group_predict(self):
        result = self.model_group.predict(
            [
                "This is a test prediction. If a finetune model predicts on this we may get an empty list as result."
            ]
        )

        # TODO: Break this test by task_type and have saved model groups for these tests. this will require a test user api token.
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)


from typing import TYPE_CHECKING

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoError, IndicoNotFound
from indico.types.questionnaire import Example, Questionnaire

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class AddLabels(GraphQLRequest["AnyDict"]):
    """
    Add labels to an existing labelset.

    Args:
        labelset_id (int): The id of the labelset to add labels to.
        labels (List(dict)): A list of dicts containing rowIndex and target fields for the data points to add.
        model_group_id (int, optional): The id of the model group to add labels to.

    Raises:
        IndicoInputError if the length of targets and row_index are not equal

    """

    query = """
        mutation(
            $labels: [LabelInput]!,
            $labelset_id: Int!,
        ){
            submitLabelsV2(
                labels: $labels
                labelsetId: $labelset_id,
            ){ success }
        }
        """

    def __init__(
        self,
        labelset_id: int,
        labels: "List[AnyDict]",
        model_group_id: "Optional[int]" = None,
    ):
        super().__init__(
            query=self.query,
            variables={
                "labels": labels,
                "labelset_id": labelset_id,
                "model_group_id": None,
            },
        )


class GetQuestionnaireExamples(GraphQLRequest["List[Example]"]):
    """
    Gets unlabeled examples from a Questionnaire.

    Args:
        questionnaire_id (int): The id of the questionnaire to get examples from.
        num_examples (int): The number of examples to get from the questionnaire.

    Returns:
        List[Example]

    """

    query = """
    query(
        $questionnaire_id: Int!,
        $num_examples: Int!,
        $datafile_id: Int
    )
    {
        questionnaires(questionnaireIds: [$questionnaire_id]) {
            questionnaires {
                examples(numExamples: $num_examples, datafileId: $datafile_id) {
                    datafileIds
                    originalDatafileId
                    originalDatafileName
                    contexts {
                        id
                        datafileId
                        source
                    }
                    status
                    id
                }
            }
        }
    }
    """

    def __init__(
        self,
        questionnaire_id: int,
        num_examples: int,
        datafile_id: "Optional[int]" = None,
    ):
        super().__init__(
            query=self.query,
            variables={
                "questionnaire_id": questionnaire_id,
                "num_examples": num_examples,
                "datafile_id": datafile_id,
            },
        )

    def process_response(self, response: "Payload") -> "List[Example]":
        try:
            return [
                Example(**e)
                for e in super().parse_payload(response)["questionnaires"][
                    "questionnaires"
                ][0]["examples"]
            ]
        except IndexError:
            raise IndicoNotFound(
                "Examples not found. Please check the ID you are using."
            )


class _GetQuestionnaire(GraphQLRequest["Questionnaire"]):
    """
    Gets a questionnaire from an ID.

    Args:
        questionaire_id (int): The id of the questionnaire to get examples from.

    Returns
        Questionnaire
    """

    query = """
    query(
        $questionnaire_id: Int!
    )
    {
        questionnaires(questionnaireIds: [$questionnaire_id]) {
            questionnaires {
                id
                questionsStatus
                odl
                name
                numTotalExamples
                numFullyLabeled
                question {
                    labelset{
                        targetNames{
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, questionnaire_id: int):
        super().__init__(
            query=self.query,
            variables={"questionnaire_id": questionnaire_id},
        )

    def process_response(self, response: "Payload") -> "Questionnaire":
        questionnaire_list: "List[AnyDict]" = super().parse_payload(response)[
            "questionnaires"
        ]["questionnaires"]
        if not questionnaire_list or not questionnaire_list[0]:
            raise IndicoError("Cannot find questionnaire")

        return Questionnaire(**questionnaire_list[0])


class GetQuestionnaire(RequestChain["Questionnaire"]):
    """
    Gets a questionnaire from an ID.

    Args:
        questionaire_id (int): The id of the questionnaire to get examples from.
        wait (bool, optional): Wait for the questionnaire to reach a COMPLETE status. Defaults to True.

    Returns:
        Questionnaire object
    """

    previous: "Questionnaire"

    def __init__(self, questionnaire_id: int, wait: bool = True):
        self.questionnaire_id = questionnaire_id
        self.wait = wait

    def requests(self) -> "Iterator[Union[_GetQuestionnaire, Delay]]":
        yield _GetQuestionnaire(questionnaire_id=self.questionnaire_id)
        if self.wait:
            while self.previous.questions_status == "STARTED":
                yield Delay()
                yield _GetQuestionnaire(questionnaire_id=self.questionnaire_id)

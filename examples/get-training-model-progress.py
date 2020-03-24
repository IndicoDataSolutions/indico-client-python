#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

from indico import IndicoClient
from indico.config import IndicoConfig
from indico.queries.model_groups import GetModelGroup, GetTrainingModelWithProgress


def main(args):

    if len(args) != 1:
        print('USAGE: get-training-model-progress model_id')
        sys.exit(0)

    try:
        model_id = int(args[0])
    except ValueError:
        print(f'Invalid model_id {args[0]}')
        sys.exit(0)

    # Create an Indico API client
    my_config = IndicoConfig(
        host='dev.indico.io',
        api_token_path=Path(__file__).parent / 'indico_api_token.txt'
    )
    client = IndicoClient(config=my_config)

    # Get the model group and training status
    mg = client.call(GetModelGroup(model_id))
    training_mg = client.call(GetTrainingModelWithProgress(model_id))

    print(f'{mg.name}:')
    print(f'\ttraining status = {training_mg.status}')
    print(f'\tpercent complete = {training_mg.training_progress.percent_complete:.2f}')


if __name__ == '__main__':
    os.chdir(Path(__name__).parent)
    main(sys.argv[1:])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

from indico import IndicoClient
from indico.config import IndicoConfig
from indico.queries.documents import DocumentExtraction
from indico.queries.jobs import JobStatus
from indico.queries.storage import RetrieveStorageObject


def main(args):
    if len(args) != 1:
        print('USAGE: doc-extraction.py pdf_dir')
        sys.exit(0)
    
    src_path = Path(args[0])
    if src_path.exists() is False or src_path.is_file() is False:
        print(f'Invalid or non-existing file {src_path}')
        sys.exit(0)

    # Create an Indico API client
    my_config = IndicoConfig(
        host='dev.indico.io',
        api_token_path=Path(__file__).parent / 'indico_api_token.txt'
    )
    client = IndicoClient(config=my_config)

    # OCR a single file and wait for it to complete
    job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset_config": "simple"}'))
    job = client.call(JobStatus(id=job[0].id, wait=True))
    if job is not None and job.status == 'SUCCESS':
        json_data = client.call(RetrieveStorageObject(job.result))
        print(json.dumps(json_data, indent=4))


if __name__ == '__main__':
    os.chdir(Path(__name__).parent)
    main(sys.argv[1:])

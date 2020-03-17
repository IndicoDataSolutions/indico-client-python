#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback
from pathlib import Path

from indico import IndicoClient
from indico.config import IndicoConfig
from indico.queries.documents import DocumentExtraction


def ocr_files(target_files):

    my_config = IndicoConfig(
        host='dev.indico.io',
        api_token_path=Path(__file__).parent / 'indico_api_token.txt'
    )

    client = IndicoClient(config=my_config)

    jobs = []
    failed = []

    for src_path in target_files:
        finfo = src_path.stat()

        if finfo.st_size > 0:
            start_time = time.time()
            job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset": "simple"}'))
            upload_time = time.time() - start_time
            if job is not None:
                jobs.append(job)
                print(f"({len(jobs)}) Queued OCR on {src_path.parent.name}/{src_path.name} ({(finfo.st_size / 1000):.2f}kb in {upload_time:.2f}s)")
            else:
                print(f"ERROR - Upload failed on {src_path.parent.name}/{src_path.name} - skipping")
                failed.append(src_path)
        else:
            print(f"ERROR - Zero length file {src_path.parent.name}/{src_path.name} - skipping")
            failed.append(src_path)
    
    total_jobs = len(jobs)
    n_finished = 0
    print(f"\nQueued {total_jobs} total files for OCR")
    print("=" * 40)

    for path, jobs in zip(target_files, jobs):
        try:
            jobs.wait()
            json_result = jobs.result()[0]
        except Exception as e:
            print(f'({n_finished}/{total_jobs} - OCR ERROR on {path.parent.name}/{path.name},  {str(e)}')
            traceback.print_exc()
            failed.append(path)
        else:
            print(f"{n_finished}/{total_jobs} - Successfully extracted {path.parent.name}/{path.name}")
            txt_path = path.parent / f"{path.stem}.txt"
            txt_path.write_text(json_result.get("raw_text", ""))
            print(f"...saved txt to {txt_path.parent.name}/{txt_path.name}")

        n_finished += 1

    return failed


def get_target_files(src_dir):
    ocr_exts = ['*.pdf', '*.tif', '*.tiff']
    target_files = []
    for ext in ocr_exts:
        target_files.extend(sorted(src_dir.glob(ext)))
    return target_files


def main(args):
    if len(args) != 1:
        print('USAGE: doc-extraction.py pdf_dir')
        sys.exit(0)
    
    src_dir = Path(args[0])
    if src_dir.exists() is False or src_dir.is_dir() is False:
        print(f'Invalid or non-existing directory {src_dir}')
        sys.exit(0)

    target_files = get_target_files(src_dir)

    if len(target_files) == 0:
        print(f'No files to OCR in {src_dir}')
        sys.exit(0)
    else:
        print(f'Found {len(target_files)} files to OCR')

    failed = ocr_files(target_files)


if __name__ == '__main__':
    os.chdir(Path(__name__).parent)
    main(sys.argv[1:])

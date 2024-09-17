#!/bin/bash
#put token in user's home dir
printenv INDICO_API_TOKEN > ~/indico_api_token.txt
#install additional test reqs and run smoke tests
tox -p

#!/bin/bash

set -euxo pipefail

rm -f tmp-deployment.zip
cd lambda_source
zip -r ../tmp-deployment.zip *
cd -
aws lambda update-function-code --function-name secretsExchange --publish --zip-file fileb://tmp-deployment.zip
rm -f tmp-deployment.zip

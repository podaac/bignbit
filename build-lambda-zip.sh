#!/usr/bin/env bash
set -e

poetry build
poetry install --only main --sync
rm -rf dist/lambda-package || true
mkdir -p dist/lambda-package
cp -r $(poetry env list --full-path | awk '{print $1}')/lib/python*/site-packages/* dist/lambda-package/
cp -r ./podaac dist/lambda-package/
touch dist/lambda-package/podaac/__init__.py
# zip does not exist on the Jenkins build container so comment this out and use the zipFile jenkins step directly
#pushd dist/lambda-package
#zip -r ../pobit-lambda.zip .
#popd

#!/bin/bash

python -m black --line-length 100 asconnect tests
python -m pylint --rcfile=pylintrc asconnect tests
python -m mypy --ignore-missing-imports asconnect/ tests/


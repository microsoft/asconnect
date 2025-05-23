#!/bin/bash

echo "==== black ===="
python -m black --line-length 100 asconnect tests
echo "==== pylint ===="
python -m pylint asconnect tests
echo "==== mypy ===="
python -m mypy --ignore-missing-imports asconnect/ tests/


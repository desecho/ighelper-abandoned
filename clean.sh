#!/bin/bash

# We want to remove imports before running isort.
autoflake --remove-all-unused-imports --in-place -r ighelper ighelper_project

yapf -ri ighelper/tests/*.py ighelper/views ighelper/*.py ighelper_project
# This command takes a long time.
# yapf -ri ighelper/tests/fixtures/*.py

# We want to run isort after yapf to make sure isort lint pass.
isort -rc ighelper ighelper_project
csscomb ighelper/styles/*
./eslint.sh
find . -type f -name "*.js" -not -path "./node_modules/*" -not -path "./ighelper/static/*" -exec js-beautify -r {} \;
find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./ighelper/static/*" -exec js-beautify -r {} \;

#!/bin/bash

result=$(find ighelper -name '*.py' -exec py3diatra {} \;)
echo $result
if [[ $result ]]; then
	exit 1
fi

result=$(find ighelper_project -name '*.py' -exec py3diatra {} \;)
echo $result
if [[ $result ]]; then
    exit 1
fi

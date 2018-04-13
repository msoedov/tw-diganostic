#!/usr/bin/env bash

set -ex

name=cli_test
docker build -f Dockerfile.test -t $name .

docker run -v $(pwd):/app -it $name py.test -s

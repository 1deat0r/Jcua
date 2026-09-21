#!/bin/bash
docker run --rm --network=none --cpus=4 --memory=4g --pids-limit=128 jcua-bench

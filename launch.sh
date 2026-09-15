#!/bin/bash
docker run --privileged --rm -it --security-opt seccomp=unconfined cull-exp

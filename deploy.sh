#!/bin/bash
docker stack deploy \
    steamtail \
    -c docker-swarm.yml \
    --with-registry-auth \
    --prune

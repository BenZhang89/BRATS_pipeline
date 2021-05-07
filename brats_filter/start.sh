#!/bin/bash

#saving all the env paraments to a file
scriptPath=$(dirname "$(readlink -f "$0")")

printenv | sed 's/^\(.*\)$/export \1/g' > ${scriptPath}/.env.sh
chmod +x ${scriptPath}/.env.sh

#run the crontab job and keep the docker up
cron -f && tail -f /var/log/cron.log

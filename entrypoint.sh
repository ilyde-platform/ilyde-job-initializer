#!/usr/bin/env bash

# set python path
export PYTHONPATH=/opt/ilyde:$PYTHONPATH

# load ilyde env
source /home/ubuntu/.ilyde-defaults

# starting job (default)
if [ "$1" = 'job' ]; then
  exec python -m "$@"
fi

#override command
exec "$@"

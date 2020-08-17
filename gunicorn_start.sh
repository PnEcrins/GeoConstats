#!/bin/bash

FLASKDIR=$(readlink -e "${0%/*}")


. "$FLASKDIR"/settings.ini

echo "Starting $app_name"
echo "$FLASKDIR"

# activate the virtualenv
cd $FLASKDIR/$venv_dir
source bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH

# Start your unicorn
exec gunicorn run:app --error-log $FLASKDIR/log/geoconstats_errors.log --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}"
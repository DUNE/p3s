#!/bin/sh

# this will need to be edited for deployment and most testing,
# so conisder this a template for the environment
p3s_server="serenity.local"
echo setting $p3s_server on port $1
export P3S_SERVER="http://$p3s_server:$1/"
export P3S_VERBOSITY=2
alias p3s="./manage.py runserver 0.0.0.0:$1"

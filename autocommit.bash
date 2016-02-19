#!/bin/bash

# You can run this with:
# ./autocommit.bash <number-of-seconds-to-wait>
#
# This should work on any git repository where there is an 'origin' that can be pushed to.
while :; do
    clear
    date

    git add .
    git commit -am "Autocommit at `date`"
    git pull -r -s recursive -Xours origin master
    git push origin master
    
    sleep $1
done

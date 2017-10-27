#!/bin/bash

echo $$ $PPID
/bin/sleep 10 &
/usr/bin/env | grep P3S &


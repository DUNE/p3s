#!/bin/sh


find $1 -maxdepth 1 -mindepth 1 -mmin -10 | sed 's/\.\///'

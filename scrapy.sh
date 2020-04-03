#!/bin/bash

HOME=/root
LOGNAME=root
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
LANG=en_US.UTF-8
SHELL=/bin/sh
PWD=/root

source /home/edwin/Desktop/environment/JobBot/bin/activate
cd /home/edwin/Desktop/environment/JobBot/src/JobBot/

PATH=$PATH:home/edwin/Desktop/environment/JobBot/bin:/home/edwin/bin:/home/edwin/.local/bin:/home/edwin/bin:/home/edwin/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/edwin/.fzf/bin
export PATH
scrapy crawl sh

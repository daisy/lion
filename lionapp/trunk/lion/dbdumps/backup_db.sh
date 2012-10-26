#!/bin/bash
mysqldump -h$GANDI -uadmin -pcr8zyda1sy amislion --default-character-set=utf8 > amislion_dump.sql


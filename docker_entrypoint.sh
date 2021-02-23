#!/bin/sh

groupadd -r hqbot
useradd -r -g hqbot hqbot

sed -i "s/DISCORD_TOKEN/${DISCORD_TOKEN}/g" /etc/hqbot/hqbot.json

gosu hqbot "$@"

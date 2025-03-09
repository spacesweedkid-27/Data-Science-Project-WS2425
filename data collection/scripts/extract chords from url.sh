#!/bin/sh

curl -s $1 | grep -oP "(?<=\[ch\]).*?(?=\[/ch\])"

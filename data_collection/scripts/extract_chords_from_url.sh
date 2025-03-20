#!/bin/sh

# curl the website and send it to grep
# print out the content of all matches for "[ch] * [/ch]"
curl -s $1 | grep -oP "(?<=\[ch\]).*?(?=\[/ch\])"

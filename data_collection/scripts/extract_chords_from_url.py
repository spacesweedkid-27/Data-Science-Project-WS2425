#!/usr/bin/env python

from re import findall
from requests import get


def get_chords(url: str) -> list[str] | None:
    """Given a URL to a ultimate-guitar chords tab,
       returns the chords that are played in a list."""
    
    # "not foud" is the token for missing chords in the table.
    if url == 'not found':
        return None
    # Get the response and decide if the content is wanted.
    response = get(url)
    if response.status_code != 200:
        return None
    else:
        content = response.text
        # Funny how it is exactly the same RegEx.
        matches = findall(r"(?<=\[ch\]).*?(?=\[/ch\])", content)
        # If there are no chords because
        # the site is blocked by some label,
        # then just return None again.
        if matches == []:
            return None
        else:
            return matches


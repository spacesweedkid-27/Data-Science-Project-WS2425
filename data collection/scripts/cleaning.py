import re

def remove_featuring(artist):
    """
    Remove 'featuring', 'feat.', or 'feat'
    
    from artist name.
    """
    if "featuring" in artist.lower():
        return artist.split("featuring")[0].strip()
    elif "feat." in artist.lower():
        return artist.split("feat.")[0].strip()
    elif "feat" in artist.lower():
        return artist.split("feat")[0].strip()
    return artist



def replace_and(artist):
    """
    Replace 'and' with '&' in

    artist name.
   
    """
    
    artist = artist.replace(" and ", " & ")
    artist = artist.replace(" And ", " & ")
    artist = artist.replace(" AND ", " & ")
    
    return artist

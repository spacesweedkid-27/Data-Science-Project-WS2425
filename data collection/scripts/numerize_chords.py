#!/usr/bin/env python

from re import search as research


# This may be useful when pre-processing the chords of the songs
# to check if some chords are simple chords.
def is_valid_chord(chord: str) -> bool:
    """Returns True if the chord provided is a real chord in short or long chord notation.
       It should be advised that some complex chords in the long chord notation like "Cmajm7",
       - the dominant seventh accord for C, would be flagged as wrong."""
    # The regular expression searches for chords that start with a note,
    # then specify if they are flat or sharp, if their mode is correct,
    # then if they add any more notes like the seventh, and finally,
    # if the chord is a slash-chord, which means that an additional bass is played.
    return research("^[A-G][b#]?(m|maj|min|dim|aug)?[0-9]*(/[A-G][#b]?)?$", chord) is not None


def convert_to_position_at_keyboard(chord: str) -> int:
    """Converts the note of a chord to where it is on the keyboard.
    """
    # First convert the note to the corresponding position on the scale.
    temp = {'C':0, 'D':2, 'E':4, 'F':5, 'G':7, 'A':9, 'B':11}[chord[0]]
    
    # If the string ends there, terminate.
    if len(chord) <= 1:
        return temp % 12

    # If the first note is sharp or flat, adjust the result accordingly.
    sharp = chord[1] == '#'
    flat = chord[1] == 'b'
    # Since a note can't be flat and sharp at the same time, this is fine.
    temp += sharp - flat

    return temp % 12


def is_minor(chord: str) -> bool:
    """Returns if a chord is a minor chord."""
    # Since in the notation the chords is exactly in minor,
    # if the char after the key position is 'm', we can do this,
    # since 'm' is not in a Chord notation at any other position.
    # For example 'C/Gm' is not a valid chord,
    # since 'C/G' is C-mayor with G bass. Alternatively 'Gm/C'
    # would be correct, being G-minor with C bass.
    return  'min' in chord \
            or 'm' in chord \
            and 'dim' not in chord \
            and 'aug' not in chord \
            and 'maj' not in chord


# Currently unused, but could be used later for data visualisation.
def main_chord_to_transpose(key: str) -> int:
    """Calculates the amount of half-steps that should be added
       to transpose the key signature to C-mayor or A-minor, 
       if the signature is in major or minor mode.
    """
    # Get the postion on the scale.
    temp = convert_to_position_at_keyboard(key)

    # Check if the chord is in major or minor
    # if it is, we want to transpose to A-minor not C-minor
    temp += 3 * is_minor(key)
    
    # finally normalize and return
    return -(temp % 12)


def convert_letter_to_harmonic_position(key: str, chord: str) -> int:
    """Assuming a chord is played in the context of some key,
       returns the position on the corresponding harmonic scale,
       where the chord is placed.
       E.g. for A-minor and Bdim it should return 2,
       since the diminished B-chord is the second chord in the A-minor scale."""
    index_origin = convert_to_position_at_keyboard(key)
    index_chord = convert_to_position_at_keyboard(chord)

    diff = index_chord - index_origin
    
    if not is_minor(key):
        # "0" means that the chord is not in the major harmony.
        return [1,0,2,0,3,4,0,5,0,6,0,7][diff]
    else:
        # "0" means that the chord is not in the minor harmony.
        return [1,0,2,3,0,4,0,5,6,0,7,0][diff]


def shrink_chord(chord: str) -> str:
    """Shrinks the chord so, that its main mode is only passed
       diminished and augmented chords count as major chord in this implementation.
       Examples: "Gmaj" -> "G", "Bb" -> "Bb", "C#min" -> "C#m".
    """
    if len(chord) <= 2:
        return chord
    else:
        # Check if there is another important symbol to include.
        has_flatsharp = chord[1] in ['b', '#']
        # If it is minor, we want to include the m, if not then not.
        if is_minor(chord):
            return chord[:2 + has_flatsharp]
        else:
            return chord[:1 + has_flatsharp]


def identify_key(chords: list[str]) -> str:
    """According to what chords are in a song, returns the key according to some method.
       Both methods may be wrong. For example: "Creep" by Radiohead is in G major,
       but the most frequent accord contains Cs. The first method counts C and Cm as different chords,
       so the algorithm still determines G is the right key, since it is the first chord,
       but in other songs it may be, that this is not the case.
       Additionally there are many songs that start with another chord and not the tonic chord.
    """
    # First method: Sort by occurrences of individual chords,
    # and select the most frequent one.
    nums = {}
    # Calculates frequencies of all shrinked chords.
    shrunk_chords = [shrink_chord(c) for c in chords]
    for chord in shrunk_chords:
        if chord not in nums.keys():
            nums[chord] = 1
        else:
            nums[chord] += 1
    
    # Search for chord with maximal occurrences.
    res = sorted(shrunk_chords, key=lambda c: -nums[c])

    # If the frequency does not matter, return the first chord.
    if nums[res[0]] == nums[res[1]]:
        return shrink_chord(chords[0])
    else:
        return res[0]


def convert_song_to_harmony(chords: list[str]) -> list[int]:
    """Identifies the key and converts all chords to their harmonic according to that key."""
    key = identify_key(chords)
    return [convert_letter_to_harmonic_position(key, chord) for chord in chords]


def combinations_in_order(words: list, k: int) -> list[tuple]:
    """For a list of some datapoints returns a list of k length combination
       tuples that are seen in the list where the order matters.
       This is a special case of the frequent itemset mining problem, where
       we assume that the data is ordered and the order matters. For example
       the itemset (1,2) and the itemset (2,1) are not equal!"""
    # Initialize list combinations and frequency-hashmap.
    combs = []
    frequency = {}
    
    # Go through all cuts of the list.
    for i in range(len(words) + 1 - k):
        # Tuples can be hashed!
        current = tuple(words[i:i + k])
        if current not in combs:
            combs.append(current)
            frequency[current] = 0
        else:
            frequency[current] += 1

    # Sort by decreasing frequency.
    combs.sort(key=lambda x: -frequency[x])
    return combs


def identify_main_harmony(song: list[int]) -> tuple[int, ...]:
    # Assuming that the main harmony repeats in 4 chords.
    return combinations_in_order(song, 4)[0]


def __test__():
    """returns: False, 1, 3, A#m, [1, 1, 6, 4, 5, 1, 6, 4, 5, 1],
       [(1, 6, 4, 5), (6, 4, 5, 1), (1, 1, 6, 4), (4, 5, 1, 6), (5, 1, 6, 4)]"""

    print(is_minor('Ddim'))
    print(convert_to_position_at_keyboard("C#"))
    print(convert_letter_to_harmonic_position("D", "F#"))
    print(shrink_chord("A#min"))
    song = ["G","G","Em","C","D","G","Em","C","D","G"]
    print(convert_song_to_harmony(song))
    print(combinations_in_order([1, 1, 6, 4, 5, 1, 6, 4, 5, 1], 4))

#__test__()


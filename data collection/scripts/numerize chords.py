#!/usr/bin/env python

def convert_to_position_at_keyboard(chord: str) -> int:
    """converts the note of a chord to where it is on the keyboard
    """
    # first convert the note to the corresponding position on the scale
    temp = {'C':0, 'D':2, 'E':4, 'F':5, 'G':7, 'A':9, 'B':11}[chord[0]]
    
    # if the string ends there, terminate
    if len(chord) <= 1:
        return temp % 12

    # if the first note is sharp or flat, adjust the result accordingly
    sharp = chord[1] == '#'
    flat = chord[1] == 'b'
    # since a note can't be flat and sharp at the same time, this is fine
    temp += sharp - flat

    return temp % 12


def is_minor(chord: str) -> bool:
    """returns if a chord is a minor chord"""
    # since in the notation the chords is exactly in minor
    # if the char after the key position is 'm', we can do this,
    # since 'm' is not in a Chord notation at any other position
    # for example 'C/Gm' is not a valid chord,
    # since 'C/G' is C-mayor with G bass. Alternatively 'Gm/C'
    # would be correct, being G-minor with C bass.
    return  'min' in chord \
            or 'm' in chord \
            and 'dim' not in chord \
            and 'maj' not in chord


def main_chord_to_transpose(key: str) -> int:
    """Calculates the amount of half-steps that should be added
       to transpose the key signature to C-mayor or A-minor, 
       if the signature is in minor mode or not
    """
    # get the postion on the scale
    temp = convert_to_position_at_keyboard(key)

    # check if the chord is in major or minor
    # if it is, we want to transpose to A-minor not C-minor
    temp += 3 * is_minor(key)
    
    # finally normalize and return
    return -(temp % 12)


def convert_letter_to_harmonic_position(key: str, chord: str) -> int:
    """assuming a chord is played in the context of some key,
       returns the position on the corresponding harmonic scale,
       where the chord is placed.
       E.g. for A-minor and Bdim it should return 2,
       since the diminished B-chord is the second chord in the A-minor scale"""
    index_origin = convert_to_position_at_keyboard(key)
    index_chord = convert_to_position_at_keyboard(chord)

    diff = index_chord - index_origin
    
    if not is_minor(key):
        # "0" means that the chord is not in the major harmony
        return [1,0,2,0,3,4,0,5,0,6,0,7][diff]
    else:
        # "0" means that the chord is not in the minor harmony
        return [1,0,2,3,0,4,0,5,6,0,7,0][diff]


def shrink_chord(chord: str) -> str:
    """shrinks the chord so, that its main mode is only passed
       diminished chords count as their major chord in this implementation
       examples: "Gmaj" -> "G", "Bb" -> "Bb", "C#min" -> "C#m"

    """
    if len(chord) <= 2:
        return chord
    else:
        # check if there is another important symbol to include
        is_fos = 'b' in chord or '#' in chord
        # if it is minor, we want to include the m, if not then not.
        if is_minor(chord):
            return chord[:2 + is_fos]
        else:
            return chord[:1 + is_fos]


def identify_key(chords: list[str], method: int = 0) -> str:
    """according to what chords are in a song, returns the key according to some method
       Both methods may be wrong. For example: "Creep" by Radiohead is in G major,
       but the most frequent accord contains Cs. The first method counts C and Cm as different chords,
       so the algorithm still determines G is the right key, since it is the first chord,
       but in other songs it may be, that this is not the case.
       Additionally there are many songs that start with another chord and not the tonic chord.
    """
    if method == 0:
        # first method sort by occurrences of individual chords
        # and select most frequent one
        nums = {}
        # calculates frequencies of all shrinked chords
        for chord in [shrink_chord(c) for c in chords]:
            if chord not in nums.keys():
                nums[chord] = 1
            else:
                nums[chord] += 1
        
        return max(chords, key=lambda c: nums[c])
    elif method == 1:
        # select first chord as tonic chord
        return shrink_chord(chords[0])
    else:
        raise Exception("Wrong argument for method parameter")


def convert_song_to_harmony(chords: list[str], method: int = 0) -> list[int]:
    """identifies the key and converts all chords to their harmonic according to that key"""
    key = identify_key(chords, method)
    return [convert_letter_to_harmonic_position(key, chord) for chord in chords]


def __test__():
    """returns: False, 1, 3, A#m, [1, 1, 6, 4, 5, 1, 6, 4, 5, 1]"""

    print(is_minor('Ddim'))
    print(convert_to_position_at_keyboard("C#"))
    print(convert_letter_to_harmonic_position("D", "F#"))
    print(shrink_chord("A#min"))
    song = ["G","G","Em","C","D","G","Em","C","D","G"]
    print(convert_song_to_harmony(song))

#__test__()


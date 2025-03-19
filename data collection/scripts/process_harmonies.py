#!/usr/bin/env python


def combinations_in_order(words: list, k: int) -> tuple[list[tuple], dict[list, int]]:
    """For a list returns a list of k length combination-tuples that are seen
       in the list where the order matters and their respective frequencies.
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
            frequency[current] = 1
        else:
            frequency[current] += 1

    # Sort by decreasing frequency.
    combs.sort(key=lambda x: -frequency[x])
    return (combs, frequency)


def identify_main_harmony(song: list[int]) -> tuple[int, ...]:
    """Deprecated method that returns most frequent 4-length chord repetition."""
    if len(song) <= 4:
        return tuple(song)
    else:
        return combinations_in_order(song, 4)[0][0]


def defining_subset(lst: list) -> list | None:
    """Returns a portion of a list, that when repeated equals the list."""
    n = len(lst)
    # Go through all possible lengths.
    for m in range(1, n // 2 + 1):
        # If a m actually divides n,
        if n % m == 0:
            # calculate sublist and check.
            sublist = lst[:m]
            if sublist * (n // m) == lst:
                return sublist
    return None


def identify_main_harmony_2(song: list[int]) -> tuple[int, ...]:
    """We define the main dominating harmony/interval progression of a song the main leitmotiv
       of the harmonic/interval progressions, that repeats most in the song.
       This algorithm finds the minimal progression that does not contain a subset
       that, when repeated forms the progression and is repeated maximally.
    """
    temp = tuple()

    # The maximal length of a harmony is half the song-length, since then it can only repeat once.
    for k in range(len(song) // 2):
        # We assign each candidate combination a frequency.
        curr_candidates = []
        curr_frequency = {}
        # For each iteration we search for progressions with length k,
        # that start with the last most frequently repeated progression.
        for i in range(len(song) + 1 - k):
            portion = tuple(song[i:i+k])
            # If the portion is the same as the last most frequent count
            # the respective frequency of it with the next chord appended.
            if portion == temp and i + k + 1 < len(song):
                # Since song[i : i + k] is temp, this is valid.
                char = tuple(song[i : i + k + 1])
                if char not in curr_candidates:
                    curr_candidates.append(char)
                    curr_frequency[char] = 1
                else:
                    curr_frequency[char] += 1
        # It can happen that the leitmotiv does not repeat directly after itself.
        # In that case just return the most frequent 4-bar leitmotiv which may
        # be inaccurate, but works for most songs.
        if curr_candidates == []:
            print("edgecase 1 detected")
            return identify_main_harmony(song)
        # When all progressions with length k have been progressed, we pick
        # the maximal occurring combination as part of the main progression.
        temp = max(curr_candidates, key=lambda x: curr_frequency[x])
        # Retrieve a defining subset and return it if there is one,
        # but if the solution is trivial, we continue the search,
        # since then it could be wrong.
        sublist = defining_subset(temp)
        if sublist and (len(sublist) != 1):# or temp.count(sublist[0]) == len(temp)):
            return tuple(sublist)
    # In this edge case where nothing directly repeating was found,
    # just return the most frequent 4-bar repetition.
    print("edgecase 2 detected")
    return identify_main_harmony(song)


def __test__():
    print(identify_main_harmony_2([1, 1, 5, 5, 1, 0, 2, 5, 2, 5, 2, 5, 2, 5, 5, 1, 0, 2, 5, 2, 5, 2, 5, 2, 5, 1, 1, 4, 0, 1, 1, 6, 2, 6, 2, 5, 2, 5, 1, 3, 6, 4, 4, 2, 5, 1, 0, 2, 5, 1, 0, 2, 5, 2, 5, 2, 5, 2, 5, 1, 1, 4, 0, 1, 1, 6, 2, 6, 2, 5, 2, 5, 1, 3, 6, 4, 4, 2, 5, 2, 5, 2, 5, 1, 2, 7, 1]))
    print(identify_main_harmony_2([1, 0, 4, 1, 1, 0, 4, 1, 0, 4, 1, 0, 4, 1, 0, 4, 1, 1, 0, 4, 1, 1, 0, 4, 1, 1, 0, 4, 1, 1, 0, 4, 1, 0, 4, 1, 0, 4, 1, 1, 0, 4, 1, 1, 0, 4, 1, 1, 0, 4, 1, 0, 4, 1, 0, 4, 1, 1, 0, 4, 1, 0, 4, 1]))
    print(identify_main_harmony_2([1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 5, 1, 1, 1, 4, 1, 1, 1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 1, 1, 1, 4, 1]))
    print(identify_main_harmony_2([7, 1, 7, 1, 7, 1, 7, 7, 1, 7, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1, 7, 1]))
    print(identify_main_harmony_2([1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 3, 1, 7, 3, 1, 7, 3, 1, 1, 7, 3, 1, 7, 3, 1, 7, 3]))
    print(identify_main_harmony_2([1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1, 3, 7, 4, 1]))
    print(identify_main_harmony_2(5 * [1]))

    # returns
    # (5, 2)
    # (1, 0, 4, 1)
    # (1,)
    # (7, 1)
    # (1, 7, 3)
    # (1, 3, 7, 4)
    # (1,)

#__test__()


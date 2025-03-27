# Github structure and development process
For the final deadline all relevant files are on the main branch of this github.
This includes all data files, all website files as well as all scripts we used to 
get our data, clean, process and analyse it.

## repository structure
The folder structure is as follows:
```
| repository root
| -- analysis (contains analysis related scripts)
     | -- Vizualization_scripts
     |    | *.ipynb
| -- assets (contains custom css for website theming)
| -- data (contains all processed versions of our data)
|    | -- Billboard_lyrics
     | -- chords
     | -- chords_extracted
     | -- chords_harmonies
     | -- chords_main_harmonies
     | -- durations
     | -- raw
     | -- safetycopy_raw
     | -- tempo
     | merged.csv
| -- data_collection 
     | -- scripts (contains all scripts used to scrape data, calls API, preprocess and clean data
| -- meta (contains ideas and research notes)
| -- pages (contains all subpages for the website)
     | about.py
     | chords.py
     | home.py
     | lyrics.py
     | tempo.py
| -- plot_images (contains svg and high res versions of the plot for a print ready poster)
| -- presentation (contains presentation files)
|    | -- presentation week 1
|    | -- presentation week 2
|    | -- final presentation
| -- venv
| -- .gitignore
| -- app.py
| -- praeambel.tex
| -- README.md
| -- requirements.txt (contains requirements for hosting on render)
```
## notes on getting the data
For the chord data as well as the tempo of songs we wrote custom webscrapers. `getchords.py` 
queries the ultimate-guitar.com (UG) search, returns a valid url and adds it into
the appropriate `data/chords/*.csv`. 
The scraping process is documented within `preprocess_data.ipynb`.
We ran into some issues with this, as some wrong urls were returned. To account for that
and make sure all scraped urls are actually correct, we added a commandline tool (`clean_urls.py`)
that looked for chords that did not fit the usual url structure used on UG. Using this
commandline tool, a url and the corresponding artist and song name were printed to the
command line and could manually be accepted (`y`) or rejected (`n`), in which case the
rejected url was removed from the data. Logs on all manual changes can be found in `data/chords/logs/*.csv`.

After urls were cleaned and `extract_chords_from_url.py` was used to scrape the actual
chords from UG. The results are located within `data/chords_extracted/*.csv`.

Originally we planned on using the spotify API to gain information on different 
musically attributes. As it is well established by now, the API underwent massive
changes, resulting in new applications having a far more limited selection of data
they can query through the API. This is why only the duration of songs was provided
by the spotify API (using `spotify_tracks_duration.py`) while another custom webscraper
was built for scraping information about the beats per minute (bpm) of songs (`gettempo.py`).
Duration data is located in `data/durations/*.csv`.

`gettempo.py` utilizes the very simple url-structure that is used on songbpm.com. 
In more recent years, the url-structure changed to a far less obvious one. This is why
for 2022 to 2024, far less data on bpm is available. All csv files containing tempo 
data can be found in `data/tempo/*.csv`

For song lyrics the genius API was queried using `Get_lyrics_billboard.py`, `Get_lyrics_URL_without_feature.py`
and `Get_Lyrics_URL.py`. All lyrics can be found in `data/Billboard_lyrics/Billboard_Lyrics_preprocessed` 
after some cleaning for better formatting within the csv-files (using `Lyrics_preprocessing.py`).
Furthermore, since spotify does not have real genre classifications anymore, we 
took advantage of *top tags* from last.FM. Those are tags users of last.FM can add to
songs and those mostly correlate to specific genres. By querying the last.FM API using 
`Get_Genres.py` we got the most frequent three tags for each song which you can find in 
`data/Billboard_lyrics/Billboard_Lyrics_Top_Tags/*.csv`.

## notes on main harmony and harmonic progression
We wanted to extract the main harmonic progression because they make songs in different key-signature comparable: <br>
A popular progression that is written (I, IV, V, I) can be played in C-major with chords (C, F, G, C), but also in, for example, A-minor with chords (Am, Dm, Em, Am) which differ not only in main chord-key but also in mode, but use the same _idea_. <br>
When it comes down of how original individual songs are, we can use harmonic progressions as an efficient feature extraction.

The algorithm to find the main harmonic progression looks like this:
1. Find key signature of song (`numerize_chords.identify_key_2`)
     1. For each chord assume that the song is played in the key signature the chord would provide.
     2. Give the current assumed mode a rating for each chord in the song based on how well it would fit. <br>
     Here we add for the I a rating of 2, the other harmonics of the key signature a rating of 1 and chords that are not fitting a rating of 0. <br>
     It is important here to notice that the scoring in major and minor mode is different, since the measure has different intervals.
     3. After going through all possible modes pick the mode with the best score if the rating is _confident_ enough. <br>
     If not, pick the first chord as the key signature.

Generally this algorithm picks the chord as key signature that is played most, since it accumulates most points, but in case of a tiebreak, the other harmonic chords give a decisive score.

2. Determine harmonic position (I, II, etc.) of each chord in the song, use 0 if it does not fit (`numerize_chords.convert_song_to_harmony`) <br>
By using the key signature derived from the previous algorithm which determines the position and mode of the main harmonic chord - the _tonic_ chord, we can derive the harmonic position of all other chords. <br>
At this moment, cover-songs of the same song that would be played in a different key, or even in a different mode, even though this might confuse the listener, would be equivalent with same numerical representation as a long tuple.
3. Extract main harmonic progression (`process_harmonies.identify_main_harmony_2`) <br>
Here we use a heuristic approach to determine the harmonic portion that repeats maximally.
     1. We start with an empty tuple as our temporary solution.
     2. For each iteration we find the harmonic chord that most frequently follows the temporary solution and append it.
     3. If the temporary solution contains a full repetition, like (1,2) in (1,2,1,2), return the repetition.
     4. If there were no direct repetitions of the temporary solution in the song we return the 4-bar repetition with highest confidence.

We extracted the harmonies, main harmonies, the intervals in half steps between each chord `numerize_chords.convert_song_to_interval_difference`, their variance `numerize_chords.variance_of_intervals` and the main interval distances into our csvs.

Later we noticed, that we can also use the main interval distances to find the main harmonic progressions without having to identify the tonic chord position, since a repetition in half steps like (-5, -5, 2, -4), which was the most popular main interval repetition (see website) can be played with the notes C, G, A, F which makes only sense if played in C-major with the chords (C, G, Am, F) which maps to the harmonic progression (I, V, VI, IV) in major mode. <br>
This approach could be used in further studies to compose an algorithm to find main harmonic progressions.

## notes on the website structure
To keep the files holding the website data organized, we opted for dynamically loading
content into the main page from different files.
As far as actual html elements are concerned, `app.py` only holds the navbar.
Most of what `app.py` is responsible for is the different callbacks used for dynamically 
changing content of plots and keeping track of the selected theme. For presentation purposes,
the light theme is a better choice, while during website development mostly the dark theme was
used. 

The website is split into two parts: *home* and *about*. *About* includes some general information
about the project while *home* contains the content that is displayed on page-load. *Home* also 
contains three buttons (chords, lyrics and time) to group our results thematically.
Using those buttons, the content of the appropriate subpage is being loaded into the viewport.
This way, the performance is a little bit better as well, although especially the wordcloud
used to vizualize lyrics data does take some time to load if it is not persisted within the
data repository.

In the website files `app.py` and `tempo.py` you can also find three longer comment 
sections in which important steps are explained to integrate plots into the website.

## Individual assignments


<table>
     <tr>
          <th>Phase</th>
          <th>Task</th>
          <th>Assignee</th>
     </tr>
     <tr>
          <td>Data acquisition and cleaning</td>     
          <td>Chord URLs</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>Chords from URLs</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>Song durations</td>
          <td>Sena</td>
     </tr>
     <tr>
          <td></td>
          <td>Song bpm</td>
          <td>Sena</td>
     </tr>
     <tr>
          <td></td>
          <td>Lyrics</td>
          <td>Mika</td>
     </tr>
     <tr>
          <td></td>
          <td>Top Tags</td>
          <td>Mika</td>
     </tr>
     <tr>
          <td>presentation</td>
          <td>presentation week 1 pdf</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>presentation week 2 pdf</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td>poster</td>
          <td>poster design</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>plot export high res</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>texts</td>
          <td>Henri, Sena, Mika</td>
     </tr>
     <tr>
          <td>Data processing</td>
          <td>calculate harmonies and progressions</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td>Website</td>
          <td>setting up website structure and design</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>setting up hosting on render</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>Troubleshooting & support</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>texts on website</td>
          <td>Henri, Sena, Mika, Nike</td>
     </tr>
     <tr>
          <td>Vizualization</td>
          <td>Chord frequency by year</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>Chord frequency by Top Tags</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>Harmonic Progressions by frequency</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>Main harmony by Top Tags</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>Interval progression by absolute frequency</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>Variance of interval-length over year</td>
          <td>Henri</td>
     </tr>
     <tr>
          <td></td>
          <td>Lyrics polarity</td>
          <td>Mika</td>
     </tr>
     <tr>
          <td></td>
          <td>Wordcloud</td>
          <td>Mika</td>
     </tr>
     <tr>
          <td></td>
          <td>Wordfrequency</td>
          <td>Mika</td>
     </tr>
     <tr>
          <td></td>
          <td>Average song duration</td>
          <td>Sena</td>
     </tr>
     <tr>
          <td></td>
          <td>Song duration distribution</td>
          <td>Sena</td>
     </tr>
     <tr>
          <td></td>
          <td>Average tempo over year</td>
          <td>Sena</td>
     </tr>
     <tr>
          <td></td>
          <td>implementing dynamic theme switch for plots</td>
          <td>Henri & Nike</td>
     </tr>
     <tr>
          <td>misc.</td>
          <td>documentation of process on github</td>
          <td>Nike</td>
     </tr>
     <tr>
          <td></td>
          <td>github setup</td>
          <td>Henri & Nike</td>
     </tr>
</table>

# Relevant Links
- Meeting notes: https://docs.google.com/document/d/1ay493goKrk9lXcohRdS-Nmk4IwNVLyt5xk9RbDqi5Pc/edit?tab=t.0
- Google Sheet - Billboard End of Year 100: https://docs.google.com/spreadsheets/d/12zaq5xY-k9wuQZ1YkGHY4u_StVM8iklc2pl1UeKh4L4/edit?gid=1908918907#gid=1908918907
- Spotify API: https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis
- Spotify API/Search: https://developer.spotify.com/documentation/web-api/reference/search
- Lyrics: https://github.com/elmoiv/azapi
- Genre (via topTags): https://www.last.fm/api/show/track.getTopTags

# Organizational Rules

## Branches
During different phases of the project, different sets of branches were used:
- main (linked to render for deployment; used for general updates (like readme and presentation files))
- chords (during data acquisition and processing) 
- spotify (during data acquisition and processing) 
- lyrics (during data acquisition and processing and website development) 
- website (for website development)
- poster (for poster design)

Work on a specific problem will be done on the appropriate branch. Merges into main should only be done,
once all work on the problem is done (e.g. once all processing for the chord-dataset is completed).

## Issues
- basic organization will be done using issues
- issue titles should be short and concise
- if necessary, add a description to the issue to further clarify the todo
- each issue should correspond to a milestone
- if the due date of an issue differs from that of the corresponding milestone, add an earlier due date
- each issue be assigned to at least one person
- if you're looking for something to do, look through not-assigned issues and assign yourself an issue to work on

## Commits
- commit messages should be short and concise
- Each commit message should include the associated issue-number #issuenumber. This way, work on one issue can be clearly identified through commits.

## Issue-Stati
- currently, there are four stati (status? statoden?): todo, in progress, review and done
- todo: work on this issue hasn't been started yet
- in progress: work on this issue is being done, but not completed yet
- review: work on this issue is done - it needs to be reviewed
- done: work on this issue is completed and has been reviewed; there is no need for further work on this issue

## Review process
- once a person finished work on an issue, this person changes the issue's status to "review" and unassigns themselves
- another person looking for something to do can assign themselves to any issue in "review" state
- if there's flaws, leave a comment within the issue and describe what needs to be fixed
- then, put the issue back into "in progress" status and assign the person that's worked on the issue previously
- if there's no flaws, change the issue's status to "done"

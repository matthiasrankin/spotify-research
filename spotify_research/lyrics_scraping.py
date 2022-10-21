"""
Functions relating to lyric scraping, parsing
and text cleaning.
"""


import nltk
import re
import requests
import string

from bs4 import BeautifulSoup


def regex_cleaning(text):
    """
    Function to perform cleaning on lyrics text.
    Called by scrape_lyrics().
    
    Parameters:
    -----------
    text: str
        String of all lyrics for a particular song.
    
    Returns:
    --------
    List of lyrics, with each element corresponding
    to a line in the song.
    """

    # Split on and then remove [lines in brackets]:
    output = re.sub(r'(?<=.)(?=\[)', '\n ', text)
    output = re.sub(r'(?<=\])', '\n ', output)
    output = re.sub(r'\[.*?\]', '', output)

    # Split for new lines in song:
    output = re.sub(r'(?<![\W])(?=[A-Z])', '\n ', output)
    
    # Separate line for (lines beginning with parentheses):
    output = re.sub(r'(?<=.)(?=\()', '\n ', output)
    output = re.sub(r'(?<=\))', '\n ', output)
    
    # Split when lines start with ` or ' or end with ?:
    output = re.sub(r'(?=\`[A-Z])', '\n ', output)
    output = re.sub(r'(?=\'[A-Z])', '\n ', output)
    output = re.sub(r'(?<=\?)', '\n ', output)
    
    return [i.strip()
            for i in output.split("\n")
            if i.strip() != '']


def scrape_lyrics(*, artist_name=None, track_name=None, headers=None):
    """
    Function to perform scraping and processing of lyrics.
    
    Parameters:
    -----------
    artist_name: str
        String of artist's name. Upper case letters will be changed
        to lower case, and spaces will be changed to dashes.
        
    track_name: str
        String of track name. Upper case letters will be changed
        to lower case, and spaces will be changed to dashes.
    
    headers: dict
        Dictionary with keys "Accept-Language" and "User-Agent". 
        See http://myhttpheader.com/ for help.

    Returns:
    --------
    List of lyrics, with each element corresponding
    to a line in the song.
    """
    
    if headers is None:
        headers = {}
    
    artist_name = artist_name.lower().replace(" ", "-")
    track_name = track_name.lower().replace(" ", "-")
    
    url = f"https://genius.com/{artist_name}-{track_name}-lyrics"
    html = requests.get(url, headers=headers)
    
    lyrics = BeautifulSoup(html.text, 'lxml')
    container_name = html.text.split("Lyrics__Container")[1].split('"')[0]

    text_list = lyrics.find_all("div", class_="Lyrics__Container" + container_name)

    text_list = [i.get_text() for i in text_list]

    text_list = ' '.join(text_list)
    
    return regex_cleaning(text_list)


def clean_for_word_cloud(text, *, words_to_remove=None):
    """
    Function to remove punctuation, line breaks and undesirable
    words from corpus for word cloud purposes.

    Parameters:
    -----------
    text: str or list
        The corpus for which the word cloud is to be created.
        If list, must be a list of strings.
    words_to_remove: list, optional
        Words to be removed from corpus, such as stopwords
        and profanity. Must be a list of strings.
    
    Returns:
    --------
    List of cleaned text where each element is a single word.
    """

    tokenizer = nltk.tokenize.WordPunctTokenizer()
    punctuation = string.punctuation
    punctuation += '-’'

    if isinstance(text, list):
        text = ' '.join(text)

    text = text.lower()

    output = [i for i in tokenizer.tokenize(text)
              if i not in words_to_remove
              and i not in punctuation]

    return output


def print_lyrics(lyrics_list):
    """Function to print lyrics."""
    print('\n'.join(lyrics_list))


def lyrics_onto_frame(df1, artist_name):
    """Function to add lyrics to streaming data frame."""
    for i, x in enumerate(df1['track']):
        test = scrape_lyrics(artist_name, x)
        df1.loc[i, 'lyrics'] = test
    return df1

from models.mock_api.pycragapi import CRAG

class MusicTools:
    def __init__(self):
        self.api = CRAG()

    def get_artist_name(self, name):
        names = self.search_artist_entity_by_name(name)
        for n in names:
            if n.lower() == name.lower():
                return n
        return None
    
    def get_song_name(self, name):
        names = self.search_song_entity_by_name(name)
        for n in names:
            if n.lower() == name.lower():
                return n
        return None
    
    def search_artist_entity_by_name(self, query):
        """ Return the fuzzy matching results of the query (artist name); we only return the top-10 similar results from our KB

        Args:
            query (str): artist name

        Returns:
            Top-10 similar entity name in a list

        """
        return self.api.music_search_artist_entity_by_name(query)['result']

    def search_song_entity_by_name(self, query):
        """ Return the fuzzy matching results of the query (song name); we only return the top-10 similar results from our KB

        Args:
            query (str): song name

        Returns:
            Top-10 similar entity name in a list

        """
        return self.api.music_search_song_entity_by_name(query)['result']
    
    def get_billboard_rank_date(self, rank, date):
        """ Return the song name(s) and the artist name(s) of a certain rank on a certain date; 
            If no date is given, return the list of of a certain rank of all dates. 

        Args:
            rank (int): the interested rank in billboard; from 1 to 100.
            date (Optional, str, in YYYY-MM-DD format): the interested date; leave it blank if do not want to specify the date.

        Returns:
            rank_list (list): a list of song names of a certain rank (on a certain date).
            artist_list (list): a list of author names corresponding to the song names returned.
        """
        return self.api.music_get_billboard_rank_date(rank, date)['result']
    
    def get_billboard_attributes(self, date, attribute, song_name):
        """ Return the attributes of a certain song on a certain date

        Args:
            date (str, in YYYY-MM-DD format): the interested date of the song
            attribute (str): attributes from ['rank_last_week', 'weeks_in_chart', 'top_position', 'rank']
            song_name (str): the interested song name

        Returns:
            cur_value (str): the value of the interested attribute of a song on a certain date
        """
        return self.api.music_get_billboard_attributes(date, attribute, song_name)['result']

    def get_grammy_best_artist_by_year(self, year):
        """ Return the Best New Artist of a certain year in between 1958 and 2019

        Args:
            year (int, in YYYY format): the interested year

        Returns:
            artist_list (list): the list of artists who win the award
        """
        return self.api.music_grammy_get_best_artist_by_year(year)['result']

    def get_grammy_award_count_by_artist(self, artist_name):
        """ Return the number of awards won by a certain artist between 1958 and 2019

        Args:
            artist_name (str): the name of the artist

        Returns:
            the number of total awards (int)
        """
        return self.api.music_grammy_get_award_count_by_artist(artist_name)['result']
    
    def get_grammy_award_count_by_song(self, song_name):
        """ Return the number of awards won by a certain song between 1958 and 2019

        Args:
            song_name (str): the name of the song

        Returns:
            the number of total awards (int)
        """
        return self.api.music_grammy_get_award_count_by_song(song_name)['result']
    
    def get_grammy_best_song_by_year(self, year):
        """ Return the Song Of The Year in a certain year between 1958 and 2019
        
        Args:
            year (int, in YYYY format): the interested year

        Returns:
            song_list (list): the list of the song names that win the Song Of The Year in a certain year
        """
        return self.api.music_grammy_get_best_song_by_year(year)['result']
    
    def get_grammy_award_date_by_artist(self, artist_name):
        """ Return the award winning years of a certain artist

        Args:
            artist_name (str): the name of the artist

        Returns:
            selected_years (list): the list of years the artist is awarded
        """
        return self.api.music_grammy_get_award_date_by_artist(artist_name)['result']
    
    def get_grammy_best_album_by_year(self, year):
        """ Return the Album Of The Year of a certain year between 1958 and 2019

        Args:
            year (int, in YYYY format): the interested year

        Returns:
            song_list (list): the list of albums that won the Album Of The Year in a certain year
        """
        return self.api.music_grammy_get_best_album_by_year(year)['result']
    
    def get_grammy_all_awarded_artists(self):
        """Return all the artists ever awarded Grammy Best New Artist between 1958 and 2019
                
        Args:
            None

        Returns:
            nominee_values (list): the list of artist ever awarded Grammy Best New Artist
        """
        return self.api.music_grammy_get_all_awarded_artists()['result']
    
    def get_artist_birth_place(self, artist_name):
        """ Return the birth place of a certain artist

        Args:
            artist_name (str): the name of the artist

        Returns:
            birth_place (str): the birth place of the artist
        """
        return self.api.music_get_artist_birth_place(artist_name)['result']
    
    def get_artist_birth_date(self, artist_name):
        """ Return the birth date of a certain artist

        Args:
            artist_name (str): the name of the artist

        Returns:
            life_span_begin (str, in YYYY-MM-DD format if possible): the birth date of the person or the begin date of a band
        """
        return self.api.music_get_artist_birth_date(artist_name)['result']
    
    def get_members(self, band_name):
        """ Return the member list of a band

        Args:
            band_name (str): the name of the band

        Returns:
            the list of members' names.
        """
        return self.api.music_get_members(band_name)['result']
    
    def get_lifespan(self, artist_name):
        """ Return the lifespan of the artist

        Args:
            artist_name (str): the name of the artist

        Returns:
            the birth and death dates in a list
        """
        return self.api.music_get_lifespan(artist_name)['result']
    
    def get_song_author(self, song_name):
        """ Return the author of the song

        Args:
            song_name (str): the name of the song

        Returns:
            author (str): the author of the song
        """
        return self.api.music_get_song_author(song_name)['result']
    
    def get_song_release_country(self, song_name):
        """ Return the release country of the song

        Args:
            song_name (str): the name of the song

        Returns:
            country (str): the two-digit country code following ISO-3166
        """
        return self.api.music_get_song_release_country(song_name)['result']
    
    def get_song_release_date(self, song_name):
        """ Return the release date of the song

        Args:
            song_name (str): the name of the song

        Returns:
            date (str in YYYY-MM-DD format): the date of the song
        """
        return self.api.music_get_song_release_date(song_name)['result']
    
    def get_artist_all_works(self, artist_name):
        """ Return the list of all works of a certain artist

        Args:
            artist_name (str): the name of the artist

        Returns:
            work_list (list): the list of all work names

        """
        return self.api.music_get_artist_all_works(artist_name)['result']
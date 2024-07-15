from models.mock_api.pycragapi import CRAG

class MovieTools:
    def __init__(self):
        self.api = CRAG()

    def get_movie_id(self, movie_name):
        movies_info = self.get_movie_info(movie_name)
        movie_ids = []
        for movie_info in movies_info:
            if movie_info["title"].lower() == movie_name.lower() or movie_info["original_title"].lower() == movie_name.lower():
                movie_ids.append(movie_info["id"])
        return movie_ids

    def get_person_id(self, person_name):
        people_info = self.get_person_info(person_name)
        person_ids = []
        for person_info in people_info:
            if person_info["name"].lower() == person_name.lower():
                person_ids.append(person_info["id"])
        return person_ids

    def get_person_info(self, person_name):
        return self.api.movie_get_person_info(person_name)['result']
    
    def get_movie_info(self, movie_name):
        return self.api.movie_get_movie_info(movie_name)['result']
    
    def get_year_info(self, year):
        return self.api.movie_get_year_info(year)['result']

    def get_movie_info_by_id(self, movie_id):
        return self.api.movie_get_movie_info_by_id(movie_id)['result']
    
    def get_person_info_by_id(self, person_id):
        return self.api.movie_get_person_info_by_id(person_id)['result']


from pydantic import BaseModel
#Did it like this for the smaller import in the main.py file


class BaseModels:
    class LoginInfo(BaseModel):
        email: str 
        password: str 
        username: str 
        age: int

    class AttributesInfo(BaseModel):
        attribute_type: str
        attribute_description: str

    class LanguageInfo(BaseModel):
        language_name: str

    class ProfileInfo(BaseModel):
        user_id: int
        age: int
        nick_name: str
        profile_picture: str = None
        
    class FilmInfo(BaseModel):
        title: str
        duration: str

    class QualityInfo(BaseModel):
        quality_type: str
    
    class SubtitleInfo(BaseModel):
        film_id: int = None
        episode_id: int = None
        language_id: int

    class EpisodeInfo(BaseModel):
        series_id: int
        title: str
        duration: str
        episode_number: int

    class PreferredAttributeInfo(BaseModel):
        profile_id: int
        attribute_id: int

    class FilmGenreInfo(BaseModel):
        film_id: int
        attribute_id: int

    class SeriesGenerInfo(BaseModel):
        series_id: int
        attribute_id: int

    class FilmQualityInfo(BaseModel):
        film_id: int
        quality_id: int
    
    class UpdateUserInfo(BaseModel):
        email: str 
        password: str 
        username: str 
        age: int
        language_id: int
        is_activated: int
        is_blocked: int

    class DubbingInfo(BaseModel):
        language_id: int
        dubbing_company: str
        film_id: int = None
        episode_id: int = None

    class SeriesInfo(BaseModel):
        title: str
        episode_amount: int
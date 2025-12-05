from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class Movie(BaseModel):
    id: int = Field(..., gt=0, description="Unique movie ID")
    title: str = Field(..., min_length=1, description="Movie title")
    release_year: Optional[int] = Field(None, ge=1888, le=2030, description="Year of release")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    imdb_url: Optional[str] = Field(None, description="IMDb URL")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    rating: Optional[float] = Field(None, ge=0, le=10, description="Average rating")
    plot: Optional[str] = Field(None, description="Movie plot summary")
    director: Optional[str] = Field(None, description="Director name")
    cast: List[str] = Field(default_factory=list, description="List of cast members")
    runtime: Optional[int] = Field(None, ge=1, description="Runtime in minutes")

    @field_validator('genres', 'cast', mode='before')
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

class UserRating(BaseModel):
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    timestamp: Optional[datetime] = None

class CreateRatingRequest(BaseModel):
    movie_id: int = Field(..., gt=0)
    rating: float = Field(..., ge=1, le=5)

class Recommendation(BaseModel):
    movie: Movie
    score: float = Field(..., ge=0, le=1, description="Recommendation score")
    reason: Optional[str] = Field(None, description="Explanation for recommendation")
    algorithm: str = Field(..., pattern="^(content|collaborative|hybrid)$")

class User(BaseModel):
    id: int = Field(..., gt=0)
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[Dict[str, List[str]]] = None
    ratings_count: int = Field(default=0, ge=0)
    onboarding_completed: bool = False
    favorite_genres: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    user_id: int = Field(..., gt=0)
    favorite_genres: List[str] = Field(default_factory=list)
    disliked_genres: List[str] = Field(default_factory=list)
    average_rating: float = Field(default=0.0, ge=0, le=5)
    total_ratings: int = Field(default=0, ge=0)
    genre_preferences: Dict[str, float] = Field(default_factory=dict)

class Statistics(BaseModel):
    total_movies: int = Field(..., ge=0)
    total_users: int = Field(..., ge=0)
    total_ratings: int = Field(..., ge=0)
    average_rating: float = Field(..., ge=0, le=5)
    popular_genres: List[Dict[str, Any]] = Field(default_factory=list)

class OnboardingQuestion(BaseModel):
    genre: str
    movies: List[Movie]
    selected_movie_id: Optional[int] = None

class OnboardingResponse(BaseModel):
    user_id: int = Field(..., gt=0)
    responses: Dict[str, int]

class DecisionTreeQuestion(BaseModel):
    id: str
    question: str
    options: List[Dict[str, Any]]

class DecisionTreeResponse(BaseModel):
    answers: Dict[str, str]

class MovieBattle(BaseModel):
    id: str
    movie1: Movie
    movie2: Movie
    votes1: int = Field(default=0, ge=0)
    votes2: int = Field(default=0, ge=0)
    total_votes: int = Field(default=0, ge=0)

class BattleVote(BaseModel):
    battle_id: str
    selected_movie_id: int = Field(..., gt=0)

class MovieTrivia(BaseModel):
    movie_id: int = Field(..., gt=0)
    facts: List[str] = Field(default_factory=list)
    streaming_services: List[str] = Field(default_factory=list)
    box_office: Optional[str] = None
    awards: List[str] = Field(default_factory=list)
    interesting_facts: List[str] = Field(default_factory=list)

class StreamingService(BaseModel):
    name: str
    url: Optional[str] = None
    subscription_required: bool = True
    free_tier: bool = False

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=100)

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
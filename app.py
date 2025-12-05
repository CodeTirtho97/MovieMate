"""
MovieMate - Movie Recommendation Engine
Main FastAPI Application with all features
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uvicorn
import random
import json
from pathlib import Path

from config import settings, logger
from models import (
    Movie, Recommendation, UserRating, CreateRatingRequest,
    Statistics, OnboardingQuestion, OnboardingResponse,
    DecisionTreeQuestion, DecisionTreeResponse,
    MovieBattle, BattleVote, MovieTrivia, StreamingService,
    SearchQuery, ErrorResponse
)
from database import DataService
from recommendation_engine import RecommendationEngine

# Initialize FastAPI app
app = FastAPI(
    title="MovieMate API",
    description="Movie Recommendation Engine with Multiple Features",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        settings.frontend_url
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Global service instances (lazy loaded)
_services = None

def get_services():
    """Lazy load services to speed up startup"""
    global _services

    if _services is None:
        logger.info("Initializing services...")

        try:
            data_service = DataService()
            recommendation_engine = RecommendationEngine(data_service)

            _services = {
                'data': data_service,
                'recommendations': recommendation_engine,
            }

            logger.info("Services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Server initialization failed: {str(e)}"
            )

    return _services

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MovieMate API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        services = get_services()
        stats = services['data'].get_statistics()

        return {
            "status": "healthy",
            "movies": stats.total_movies,
            "users": stats.total_users,
            "ratings": stats.total_ratings
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# === MOVIE ENDPOINTS ===

@app.get("/api/movies", response_model=List[Movie])
async def get_movies(
    limit: int = Query(default=20, ge=1, le=100),
    genre: Optional[str] = None
):
    """Get all movies or filter by genre"""
    try:
        services = get_services()

        if genre:
            movies = services['data'].get_movies_by_genre(genre, limit=limit)
        else:
            movies = services['data'].get_all_movies(limit=limit)

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies)

        return movies

    except Exception as e:
        logger.error(f"Error getting movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/search", response_model=List[Movie])
async def search_movies(
    query: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Search movies by title"""
    try:
        services = get_services()
        movies = services['data'].search_movies(query, limit=limit)

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies)

        return movies

    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/search/hybrid", response_model=List[Movie])
async def search_movies_hybrid(
    query: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Search movies in both MovieLens and OMDb"""
    try:
        services = get_services()
        movies = services['data'].search_movies_hybrid(query, limit=limit)

        return movies

    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/random", response_model=List[Movie])
async def get_random_movies(
    count: int = Query(default=10, ge=1, le=50),
    genre: Optional[str] = None
):
    """Get random movies"""
    try:
        services = get_services()
        movies = services['data'].get_random_movies(count=count, genre=genre)

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies)

        return movies

    except Exception as e:
        logger.error(f"Error getting random movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/genre/{genre}", response_model=List[Movie])
async def get_movies_by_genre(
    genre: str,
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get movies by genre"""
    try:
        services = get_services()
        movies = services['data'].get_movies_by_genre(genre, limit=limit)

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies)

        return movies

    except Exception as e:
        logger.error(f"Error getting movies by genre: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    """Get a specific movie by ID"""
    try:
        services = get_services()
        movie = services['data'].get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Enrich with poster
        movie = services['data'].enrich_movie_with_poster(movie)

        return movie

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}/streaming", response_model=List[StreamingService])
async def get_streaming_availability(movie_id: int):
    """Get streaming availability for a movie"""
    try:
        services = get_services()
        movie = services['data'].get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Mock streaming data - in production, integrate with real streaming APIs
        streaming_services = [
            StreamingService(
                name="Netflix",
                available=random.choice([True, False]),
                url=f"https://netflix.com/search?q={movie.title}" if random.choice([True, False]) else None,
                price=None
            ),
            StreamingService(
                name="Amazon Prime",
                available=random.choice([True, False]),
                url=f"https://amazon.com/search?q={movie.title}" if random.choice([True, False]) else None,
                price="Included with Prime" if random.choice([True, False]) else "$3.99"
            ),
        ]

        return [s for s in streaming_services if s.available]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting streaming for movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}/trivia", response_model=MovieTrivia)
async def get_movie_trivia(movie_id: int):
    """Get trivia for a specific movie"""
    try:
        services = get_services()
        movie = services['data'].get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Generate trivia question
        all_movies = services['data'].get_all_movies(limit=100)
        similar_movies = [m for m in all_movies if any(g in movie.genres for g in m.genres) and m.id != movie.id]

        if len(similar_movies) < 3:
            similar_movies = [m for m in all_movies if m.id != movie.id]

        options = random.sample(similar_movies, min(3, len(similar_movies)))
        options.append(movie)
        random.shuffle(options)

        return MovieTrivia(
            question=f"Which of these {', '.join(movie.genres)} movies was released in {movie.release_year}?",
            options=[m.title for m in options],
            correct_answer=movie.title,
            movie_id=movie.id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating trivia for movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === RECOMMENDATION ENDPOINTS ===

@app.get("/api/recommendations/content/{movie_id}", response_model=List[Recommendation])
async def get_content_recommendations(
    movie_id: int,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get content-based recommendations"""
    try:
        services = get_services()
        recommendations = services['recommendations'].get_content_based_recommendations(
            movie_id,
            n_recommendations=limit
        )

        # Enrich movies with posters
        for rec in recommendations:
            rec.movie = services['data'].enrich_movie_with_poster(rec.movie)

        return recommendations

    except Exception as e:
        logger.error(f"Error getting content recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations/collaborative/{user_id}", response_model=List[Recommendation])
async def get_collaborative_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get collaborative filtering recommendations"""
    try:
        services = get_services()
        recommendations = services['recommendations'].get_collaborative_recommendations(
            user_id,
            n_recommendations=limit
        )

        # Enrich movies with posters
        for rec in recommendations:
            rec.movie = services['data'].enrich_movie_with_poster(rec.movie)

        return recommendations

    except Exception as e:
        logger.error(f"Error getting collaborative recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations/hybrid", response_model=List[Recommendation])
async def get_hybrid_recommendations(
    user_id: Optional[int] = None,
    movie_id: Optional[int] = None,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get hybrid recommendations"""
    if not user_id and not movie_id:
        raise HTTPException(
            status_code=400,
            detail="Either user_id or movie_id must be provided"
        )

    try:
        services = get_services()
        recommendations = services['recommendations'].get_hybrid_recommendations(
            user_id=user_id,
            movie_id=movie_id,
            n_recommendations=limit
        )

        # Enrich movies with posters
        for rec in recommendations:
            rec.movie = services['data'].enrich_movie_with_poster(rec.movie)

        return recommendations

    except Exception as e:
        logger.error(f"Error getting hybrid recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === USER RATING ENDPOINTS ===

@app.get("/api/users/{user_id}/ratings", response_model=List[UserRating])
async def get_user_ratings(user_id: int):
    """Get all ratings for a user"""
    try:
        services = get_services()
        ratings = services['data'].get_user_ratings(user_id)

        return ratings

    except Exception as e:
        logger.error(f"Error getting user ratings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/{user_id}/ratings", response_model=UserRating)
async def add_rating(user_id: int, rating_request: CreateRatingRequest):
    """Add a new rating"""
    try:
        services = get_services()
        rating = services['data'].add_rating(
            user_id=user_id,
            movie_id=rating_request.movie_id,
            rating=rating_request.rating
        )

        return rating

    except Exception as e:
        logger.error(f"Error adding rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    """Get user profile with preferences"""
    try:
        services = get_services()
        profile = services['data'].get_user_profile(user_id)

        return profile

    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === STATISTICS ENDPOINTS ===

@app.get("/api/statistics", response_model=Statistics)
async def get_statistics():
    """Get overall statistics"""
    try:
        services = get_services()
        stats = services['data'].get_statistics()

        return stats

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/genres", response_model=List[str])
async def get_genres():
    """Get list of all genres"""
    try:
        services = get_services()
        genres = services['data'].get_all_genres()

        return genres

    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ONBOARDING ENDPOINTS ===

@app.post("/api/onboarding/start")
async def start_onboarding():
    """Start the onboarding process"""
    return await get_onboarding_questions()

@app.get("/api/onboarding/questions", response_model=List[OnboardingQuestion])
async def get_onboarding_questions():
    """Get onboarding questions"""
    try:
        services = get_services()

        genres = ["Action", "Comedy", "Drama", "Horror", "Romance",
                  "Sci-Fi", "Thriller", "Animation", "Documentary", "Fantasy"]

        questions = []
        for genre in genres:
            movies = services['data'].get_movies_by_genre(genre, limit=4)
            if movies:
                movies = services['data'].bulk_enrich_posters(movies)
                questions.append(OnboardingQuestion(genre=genre, movies=movies))

        return questions

    except Exception as e:
        logger.error(f"Error getting onboarding questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/complete", response_model=List[Movie])
async def complete_onboarding(response: OnboardingResponse):
    """Process onboarding responses"""
    try:
        services = get_services()

        # Get liked genres
        liked_genres = list(response.responses.keys())

        # Get recommendations
        recommendations = services['recommendations'].get_genre_recommendations(
            genres=liked_genres,
            n_recommendations=20
        )

        # Enrich with posters
        recommendations = services['data'].bulk_enrich_posters(recommendations)

        return recommendations

    except Exception as e:
        logger.error(f"Error processing onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === DECISION TREE ENDPOINTS ===

@app.get("/api/decision-tree/start")
async def start_decision_tree():
    """Start the decision tree"""
    return await get_decision_tree_questions()

@app.get("/api/decision-tree/questions", response_model=List[DecisionTreeQuestion])
async def get_decision_tree_questions():
    """Get decision tree questions"""
    questions = [
        DecisionTreeQuestion(
            id="mood",
            question="What's your mood right now?",
            options=[
                {"text": "Happy & Upbeat", "value": "happy"},
                {"text": "Serious & Thoughtful", "value": "serious"},
                {"text": "Scared & Thrilled", "value": "scared"},
                {"text": "Romantic", "value": "romantic"}
            ]
        ),
        DecisionTreeQuestion(
            id="time",
            question="How much time do you have?",
            options=[
                {"text": "Quick watch (< 90 min)", "value": "short"},
                {"text": "Normal (90-120 min)", "value": "normal"},
                {"text": "Epic (> 120 min)", "value": "long"}
            ]
        ),
        DecisionTreeQuestion(
            id="era",
            question="Prefer classic or modern?",
            options=[
                {"text": "Classic (before 1990)", "value": "classic"},
                {"text": "Modern (1990-2010)", "value": "modern"},
                {"text": "Recent (after 2010)", "value": "recent"}
            ]
        )
    ]

    return questions

@app.post("/api/decision-tree/recommend", response_model=List[Movie])
async def get_decision_tree_recommendations(response: DecisionTreeResponse):
    """Get recommendations based on decision tree"""
    try:
        services = get_services()

        # Map answers to genres
        mood_genre_map = {
            "happy": "Comedy",
            "serious": "Drama",
            "scared": "Horror",
            "romantic": "Romance"
        }

        genre = mood_genre_map.get(response.answers.get("mood", ""), "Drama")
        movies = services['data'].get_movies_by_genre(genre, limit=20)

        # Filter by era if specified
        era = response.answers.get("era")
        if era and movies:
            if era == "classic":
                movies = [m for m in movies if m.release_year and m.release_year < 1990]
            elif era == "modern":
                movies = [m for m in movies if m.release_year and 1990 <= m.release_year <= 2010]
            elif era == "recent":
                movies = [m for m in movies if m.release_year and m.release_year > 2010]

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies[:10])

        return movies

    except Exception as e:
        logger.error(f"Error in decision tree recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === MOVIE BATTLE ENDPOINTS ===

battles_data = {}  # In-memory storage for battles

@app.get("/api/battles/random", response_model=MovieBattle)
async def create_random_battle():
    """Create a random movie battle"""
    try:
        services = get_services()
        movies = services['data'].get_random_movies(count=2)

        if len(movies) < 2:
            raise HTTPException(status_code=500, detail="Not enough movies for battle")

        # Enrich with posters
        movies = services['data'].bulk_enrich_posters(movies)

        battle_id = f"battle_{random.randint(10000, 99999)}"
        battle = MovieBattle(
            id=battle_id,
            movie1=movies[0],
            movie2=movies[1]
        )

        battles_data[battle_id] = battle

        return battle

    except Exception as e:
        logger.error(f"Error creating battle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/battles/vote", response_model=MovieBattle)
async def vote_in_battle(vote: BattleVote):
    """Vote in a movie battle"""
    if vote.battle_id not in battles_data:
        raise HTTPException(status_code=404, detail="Battle not found")

    battle = battles_data[vote.battle_id]

    if vote.selected_movie_id == battle.movie1.id:
        battle.votes1 += 1
    elif vote.selected_movie_id == battle.movie2.id:
        battle.votes2 += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid movie ID")

    battle.total_votes += 1

    return battle

# Run the application
if __name__ == "__main__":
    logger.info(f"Starting MovieMate on {settings.backend_host}:{settings.backend_port}")

    uvicorn.run(
        "app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )

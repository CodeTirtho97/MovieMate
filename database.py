import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
from config import settings, logger
from models import Movie, UserRating, User, UserProfile, Statistics
from tmdb_service import TMDBService
from omdb_service import OMDbService

class DataService:
    """Central data service for managing MovieLens data and external APIs"""

    def __init__(self):
        self.movies_df: Optional[pd.DataFrame] = None
        self.ratings_df: Optional[pd.DataFrame] = None
        self.users_df: Optional[pd.DataFrame] = None
        self.tmdb_service = TMDBService()
        self.omdb_service = OMDbService()
        self._load_data()

    def _load_data(self):
        """Load MovieLens data from CSV files"""
        try:
            movies_path = settings.data_dir / settings.movies_file
            ratings_path = settings.data_dir / settings.ratings_file
            users_path = settings.data_dir / settings.users_file

            # Check if files exist
            if not movies_path.exists():
                logger.error(f"Movies file not found: {movies_path}")
                raise FileNotFoundError(f"Movies data not found at {movies_path}")

            if not ratings_path.exists():
                logger.error(f"Ratings file not found: {ratings_path}")
                raise FileNotFoundError(f"Ratings data not found at {ratings_path}")

            # Load movies
            logger.info(f"Loading movies from {movies_path}...")
            self.movies_df = pd.read_csv(movies_path)

            # Rename columns to match expected format
            if 'movie_id' in self.movies_df.columns:
                self.movies_df = self.movies_df.rename(columns={'movie_id': 'id'})
            if 'movie_title' in self.movies_df.columns:
                self.movies_df = self.movies_df.rename(columns={'movie_title': 'title'})

            logger.info(f"Loaded {len(self.movies_df)} movies")

            # Load ratings
            logger.info(f"Loading ratings from {ratings_path}...")
            self.ratings_df = pd.read_csv(ratings_path)
            logger.info(f"Loaded {len(self.ratings_df)} ratings")

            # Load users (optional)
            if users_path.exists():
                logger.info(f"Loading users from {users_path}...")
                self.users_df = pd.read_csv(users_path)
                logger.info(f"Loaded {len(self.users_df)} users")
            else:
                logger.warning(f"Users file not found: {users_path}. Creating from ratings...")
                self._create_users_from_ratings()

            # Ensure required columns exist
            self._validate_data()

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def _validate_data(self):
        """Validate that required columns exist in dataframes"""
        required_movie_cols = ['id', 'title']
        required_rating_cols = ['user_id', 'movie_id', 'rating']

        # Check movies
        missing = set(required_movie_cols) - set(self.movies_df.columns)
        if missing:
            raise ValueError(f"Missing required movie columns: {missing}")

        # Check ratings
        missing = set(required_rating_cols) - set(self.ratings_df.columns)
        if missing:
            raise ValueError(f"Missing required rating columns: {missing}")

        logger.info("Data validation passed")

    def _create_users_from_ratings(self):
        """Create users dataframe from ratings if not available"""
        user_ids = self.ratings_df['user_id'].unique()
        self.users_df = pd.DataFrame({
            'id': user_ids,
            'ratings_count': [
                len(self.ratings_df[self.ratings_df['user_id'] == uid])
                for uid in user_ids
            ]
        })

    def _row_to_movie(self, row) -> Movie:
        """Convert DataFrame row to Movie model"""
        # Parse genres - handle both string format and one-hot encoding
        genres = []

        # First try one-hot encoded columns
        genre_columns = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
                        'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                        'Thriller', 'War', 'Western']

        for genre in genre_columns:
            if genre in row and pd.notna(row[genre]) and int(row[genre]) == 1:
                genres.append(genre)

        # If no one-hot genres found, try string format
        if not genres and pd.notna(row.get('genres')):
            genres_str = str(row['genres'])
            if '|' in genres_str:
                genres = [g.strip() for g in genres_str.split('|')]
            elif ',' in genres_str:
                genres = [g.strip() for g in genres_str.split(',')]
            elif genres_str:
                genres = [genres_str]

        # Parse year from title if not in separate column
        release_year = None
        title = str(row['title'])

        if 'release_year' in row and pd.notna(row['release_year']):
            try:
                release_year = int(row['release_year'])
            except (ValueError, TypeError):
                pass

        # Extract year from title like "Movie Name (1995)"
        if not release_year and '(' in title and ')' in title:
            try:
                year_str = title[title.rfind('(') + 1:title.rfind(')')]
                release_year = int(year_str)
            except (ValueError, IndexError):
                pass

        # Get rating
        rating = None
        if 'rating' in row and pd.notna(row['rating']):
            try:
                rating = float(row['rating'])
            except (ValueError, TypeError):
                pass

        return Movie(
            id=int(row['id']),
            title=title,
            release_year=release_year,
            genres=genres,
            imdb_url=row.get('IMDb_URL') or row.get('imdb_url') if pd.notna(row.get('IMDb_URL') or row.get('imdb_url')) else None,
            poster_url=row.get('poster_url') if pd.notna(row.get('poster_url')) else None,
            rating=rating,
            plot=row.get('plot') if pd.notna(row.get('plot')) else None,
            director=row.get('director') if pd.notna(row.get('director')) else None,
            cast=[],
            runtime=int(row['runtime']) if pd.notna(row.get('runtime')) else None
        )

    def get_all_movies(self, limit: Optional[int] = None) -> List[Movie]:
        """Get all movies"""
        if self.movies_df is None:
            return []

        df = self.movies_df.head(limit) if limit else self.movies_df
        return [self._row_to_movie(row) for _, row in df.iterrows()]

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """Get a movie by ID"""
        if self.movies_df is None:
            return None

        result = self.movies_df[self.movies_df['id'] == movie_id]

        if result.empty:
            # Try OMDb for recent movies (ID >= 100000)
            if movie_id >= 100000:
                recent_movies = self.omdb_service.get_recent_movies()
                for movie in recent_movies:
                    if movie.id == movie_id:
                        return movie
            return None

        return self._row_to_movie(result.iloc[0])

    def search_movies(self, query: str, limit: int = 10) -> List[Movie]:
        """Search movies by title"""
        if self.movies_df is None:
            return []

        # Case-insensitive search
        mask = self.movies_df['title'].str.contains(query, case=False, na=False)
        results = self.movies_df[mask].head(limit)

        return [self._row_to_movie(row) for _, row in results.iterrows()]

    def search_movies_hybrid(self, query: str, limit: int = 10) -> List[Movie]:
        """Search both MovieLens and OMDb"""
        # Search MovieLens
        movielens_results = self.search_movies(query, limit=limit//2)

        # Search OMDb
        omdb_results = []
        omdb_data = self.omdb_service.search_by_title(query)
        if omdb_data:
            movie = self.omdb_service._convert_omdb_to_movie(omdb_data, 100000)
            if movie:
                omdb_results.append(movie)

        # Combine and deduplicate by title
        all_results = movielens_results + omdb_results
        seen_titles = set()
        unique_results = []

        for movie in all_results:
            if movie.title.lower() not in seen_titles:
                seen_titles.add(movie.title.lower())
                unique_results.append(movie)

        return unique_results[:limit]

    def get_movies_by_genre(self, genre: str, limit: int = 20) -> List[Movie]:
        """Get movies by genre"""
        if self.movies_df is None:
            return []

        # Check if we have one-hot encoded genre columns
        if genre in self.movies_df.columns:
            # Use one-hot encoding
            mask = self.movies_df[genre] == 1
        elif 'genres' in self.movies_df.columns:
            # Use string genres column
            mask = self.movies_df['genres'].str.contains(genre, case=False, na=False)
        else:
            return []

        results = self.movies_df[mask].head(limit)

        return [self._row_to_movie(row) for _, row in results.iterrows()]

    def get_random_movies(self, count: int = 10, genre: Optional[str] = None) -> List[Movie]:
        """Get random movies, optionally filtered by genre"""
        if self.movies_df is None:
            return []

        df = self.movies_df

        if genre:
            # Check if we have one-hot encoded genre columns
            if genre in df.columns:
                # Use one-hot encoding
                df = df[df[genre] == 1]
            elif 'genres' in df.columns:
                # Use string genres column
                df = df[df['genres'].str.contains(genre, case=False, na=False)]

        if len(df) < count:
            count = len(df)

        if count == 0:
            return []

        sample = df.sample(n=count)
        return [self._row_to_movie(row) for _, row in sample.iterrows()]

    def get_user_ratings(self, user_id: int) -> List[UserRating]:
        """Get all ratings for a user"""
        if self.ratings_df is None:
            return []

        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]

        return [
            UserRating(
                user_id=int(row['user_id']),
                movie_id=int(row['movie_id']),
                rating=float(row['rating']),
                timestamp=pd.to_datetime(row['timestamp']) if 'timestamp' in row and pd.notna(row['timestamp']) else None
            )
            for _, row in user_ratings.iterrows()
        ]

    def add_rating(self, user_id: int, movie_id: int, rating: float) -> UserRating:
        """Add a new rating (in-memory only for this session)"""
        new_rating = UserRating(
            user_id=user_id,
            movie_id=movie_id,
            rating=rating,
            timestamp=pd.Timestamp.now()
        )

        # Add to dataframe (in-memory)
        new_row = pd.DataFrame([{
            'user_id': user_id,
            'movie_id': movie_id,
            'rating': rating,
            'timestamp': new_rating.timestamp
        }])

        self.ratings_df = pd.concat([self.ratings_df, new_row], ignore_index=True)

        logger.info(f"Added rating: user={user_id}, movie={movie_id}, rating={rating}")
        return new_rating

    def get_user_profile(self, user_id: int) -> UserProfile:
        """Get user profile with preferences"""
        ratings = self.get_user_ratings(user_id)

        # Calculate genre preferences
        genre_ratings: Dict[str, List[float]] = {}

        for rating in ratings:
            movie = self.get_movie_by_id(rating.movie_id)
            if movie:
                for genre in movie.genres:
                    if genre not in genre_ratings:
                        genre_ratings[genre] = []
                    genre_ratings[genre].append(rating.rating)

        # Average rating per genre
        genre_preferences = {
            genre: np.mean(ratings_list)
            for genre, ratings_list in genre_ratings.items()
        }

        # Identify favorite and disliked genres
        sorted_genres = sorted(genre_preferences.items(), key=lambda x: x[1], reverse=True)
        favorite_genres = [g for g, r in sorted_genres if r >= 4.0][:5]
        disliked_genres = [g for g, r in sorted_genres if r <= 2.5]

        # Calculate overall average
        avg_rating = np.mean([r.rating for r in ratings]) if ratings else 0.0

        return UserProfile(
            user_id=user_id,
            favorite_genres=favorite_genres,
            disliked_genres=disliked_genres,
            average_rating=float(avg_rating),
            total_ratings=len(ratings),
            genre_preferences=genre_preferences
        )

    def get_statistics(self) -> Statistics:
        """Get overall statistics"""
        if self.movies_df is None or self.ratings_df is None:
            return Statistics(
                total_movies=0,
                total_users=0,
                total_ratings=0,
                average_rating=0.0,
                popular_genres=[]
            )

        # Count genre occurrences
        genre_counts: Dict[str, int] = {}

        # Check if genres column exists (string format)
        if 'genres' in self.movies_df.columns:
            for genres_str in self.movies_df['genres'].dropna():
                for genre in str(genres_str).split('|'):
                    genre = genre.strip()
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        else:
            # Use one-hot encoded genre columns
            genre_columns = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
                            'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                            'Thriller', 'War', 'Western']

            for genre in genre_columns:
                if genre in self.movies_df.columns:
                    count = int(self.movies_df[genre].sum())
                    if count > 0:
                        genre_counts[genre] = count

        popular_genres = [
            {'genre': genre, 'count': count}
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return Statistics(
            total_movies=len(self.movies_df),
            total_users=self.ratings_df['user_id'].nunique() if self.ratings_df is not None else 0,
            total_ratings=len(self.ratings_df) if self.ratings_df is not None else 0,
            average_rating=float(self.ratings_df['rating'].mean()) if self.ratings_df is not None else 0.0,
            popular_genres=popular_genres
        )

    def get_all_genres(self) -> List[str]:
        """Get list of all unique genres"""
        if self.movies_df is None:
            return []

        genres = set()
        for genres_str in self.movies_df['genres'].dropna():
            for genre in str(genres_str).split('|'):
                genre = genre.strip()
                if genre and genre != '(no genres listed)':
                    genres.add(genre)

        return sorted(list(genres))

    def enrich_movie_with_poster(self, movie: Movie) -> Movie:
        """Add poster URL to a movie using TMDB"""
        if not movie.poster_url:
            poster_url = self.tmdb_service.get_poster_url(movie.title, movie.release_year)
            if poster_url:
                movie.poster_url = poster_url

        return movie

    def bulk_enrich_posters(self, movies: List[Movie]) -> List[Movie]:
        """Enrich multiple movies with posters"""
        logger.info(f"Enriching {len(movies)} movies with posters...")

        movies_data = [
            {'id': m.id, 'title': m.title, 'release_year': m.release_year}
            for m in movies
        ]

        poster_urls = self.tmdb_service.bulk_fetch_posters(movies_data)

        for movie in movies:
            if movie.id in poster_urls:
                movie.poster_url = poster_urls[movie.id]

        return movies

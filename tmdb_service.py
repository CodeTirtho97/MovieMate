import requests
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from config import settings, logger

class TMDBService:
    """TMDB API service for fetching movie posters and metadata"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tmdb_api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/"
        self.poster_sizes = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
        self.cache_file = settings.cache_dir / settings.poster_cache_file
        self.cache = self._load_cache()

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0 / settings.tmdb_rate_limit

        if not self.api_key:
            logger.warning("TMDB API key not configured. Poster fetching will be disabled.")

    def _load_cache(self) -> Dict[str, Any]:
        """Load poster cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded {len(cache)} cached TMDB entries")
                    return cache
            except Exception as e:
                logger.warning(f"Error loading TMDB cache: {e}")
        return {}

    def _save_cache(self):
        """Save poster cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving TMDB cache: {e}")

    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Search for a movie on TMDB"""
        if not self.api_key:
            return None

        # Check cache first
        cache_key = f"{title}_{year}" if year else title
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {cache_key}")
            return self.cache[cache_key]

        self._rate_limit()

        # Clean title (remove year from title if present)
        clean_title = title
        if year and f"({year})" in title:
            clean_title = title.replace(f"({year})", "").strip()

        params = {
            "api_key": self.api_key,
            "query": clean_title,
            "language": "en-US",
        }

        if year:
            params["year"] = year

        try:
            response = requests.get(
                f"{self.base_url}/search/movie",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if data.get("results"):
                movie_data = data["results"][0]

                # Cache the result
                self.cache[cache_key] = movie_data
                self._save_cache()

                logger.debug(f"TMDB found: {movie_data.get('title')}")
                return movie_data
            else:
                logger.debug(f"No TMDB results for: {title}")

        except requests.RequestException as e:
            logger.error(f"TMDB API error for '{title}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching TMDB for '{title}': {e}")

        return None

    def get_poster_url(self, title: str, year: Optional[int] = None, size: str = "w342") -> Optional[str]:
        """Get poster URL for a movie"""
        if size not in self.poster_sizes:
            logger.warning(f"Invalid poster size: {size}. Using w342")
            size = "w342"

        movie_data = self.search_movie(title, year)

        if movie_data and movie_data.get("poster_path"):
            return f"{self.image_base_url}{size}{movie_data['poster_path']}"

        return None

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a movie by TMDB ID"""
        if not self.api_key:
            return None

        cache_key = f"details_{tmdb_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        self._rate_limit()

        try:
            response = requests.get(
                f"{self.base_url}/movie/{tmdb_id}",
                params={"api_key": self.api_key},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            self.cache[cache_key] = data
            self._save_cache()

            return data

        except Exception as e:
            logger.error(f"Error fetching TMDB details for ID {tmdb_id}: {e}")

        return None

    def bulk_fetch_posters(self, movies: List[Dict[str, Any]], size: str = "w342") -> Dict[int, str]:
        """Fetch posters for multiple movies at once"""
        results = {}

        if not self.api_key:
            logger.warning("Cannot fetch posters: TMDB API key not configured")
            return results

        logger.info(f"Fetching posters for {len(movies)} movies...")

        for movie in movies:
            movie_id = movie.get('id')
            title = movie.get('title')
            year = movie.get('release_year')

            if not title:
                continue

            poster_url = self.get_poster_url(title, year, size)
            if poster_url:
                results[movie_id] = poster_url

        logger.info(f"Successfully fetched {len(results)} posters")
        return results

    def clear_cache(self):
        """Clear the poster cache"""
        self.cache = {}
        self._save_cache()
        logger.info("TMDB cache cleared")

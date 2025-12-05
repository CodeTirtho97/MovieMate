import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from config import settings, logger
from models import Movie

class OMDbService:
    """OMDb API service for recent movie data and ratings"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.omdb_api_key
        self.base_url = "http://www.omdbapi.com/"
        self.cache_file = settings.cache_dir / settings.omdb_cache_file
        self.cache = self._load_cache()
        self.cache_duration = timedelta(days=settings.omdb_cache_days)

        if not self.api_key:
            logger.warning("OMDb API key not configured. Recent movie data will be limited.")

    def _load_cache(self) -> Dict[str, Any]:
        """Load OMDb cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded {len(cache)} cached OMDb entries")
                    return cache
            except Exception as e:
                logger.warning(f"Error loading OMDb cache: {e}")
        return {}

    def _save_cache(self):
        """Save OMDb cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving OMDb cache: {e}")

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if 'timestamp' not in cache_entry:
            return False

        try:
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            return datetime.now() - cached_time < self.cache_duration
        except Exception:
            return False

    def search_by_title(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Search for a movie by title"""
        if not self.api_key:
            return None

        # Check cache
        cache_key = f"{title}_{year}" if year else title
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            logger.debug(f"OMDb cache hit for: {cache_key}")
            return self.cache[cache_key]['data']

        params = {
            'apikey': self.api_key,
            't': title,
            'type': 'movie',
            'plot': 'full'
        }

        if year:
            params['y'] = year

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('Response') == 'True':
                # Cache the result
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                self._save_cache()

                logger.debug(f"OMDb found: {data.get('Title')}")
                return data
            else:
                logger.debug(f"OMDb: {data.get('Error', 'Movie not found')}")

        except requests.RequestException as e:
            logger.error(f"OMDb API error for '{title}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching OMDb for '{title}': {e}")

        return None

    def search_by_imdb_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Search for a movie by IMDb ID"""
        if not self.api_key:
            return None

        # Check cache
        cache_key = f"imdb_{imdb_id}"
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']

        params = {
            'apikey': self.api_key,
            'i': imdb_id,
            'plot': 'full'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('Response') == 'True':
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                self._save_cache()

                return data

        except Exception as e:
            logger.error(f"OMDb API error for IMDb ID '{imdb_id}': {e}")

        return None

    def get_recent_movies(self, limit: int = 50) -> List[Movie]:
        """Get a list of recent popular movies (2018+)"""
        recent_movies = []

        # Popular movies from recent years
        popular_titles = [
            ("Avengers: Endgame", 2019),
            ("The Batman", 2022),
            ("Top Gun: Maverick", 2022),
            ("Spider-Man: No Way Home", 2021),
            ("Dune", 2021),
            ("Everything Everywhere All at Once", 2022),
            ("Oppenheimer", 2023),
            ("Barbie", 2023),
            ("The Super Mario Bros. Movie", 2023),
            ("Guardians of the Galaxy Vol. 3", 2023),
            ("John Wick: Chapter 4", 2023),
            ("Avatar: The Way of Water", 2022),
            ("Black Panther: Wakanda Forever", 2022),
            ("Thor: Love and Thunder", 2022),
            ("Doctor Strange in the Multiverse of Madness", 2022),
            ("The Whale", 2022),
            ("Glass Onion", 2022),
            ("Nope", 2022),
            ("RRR", 2022),
            ("The Fabelmans", 2022),
            ("Elvis", 2022),
            ("A Quiet Place Part II", 2021),
            ("Shang-Chi and the Legend of the Ten Rings", 2021),
            ("No Time to Die", 2021),
            ("Free Guy", 2021),
            ("Encanto", 2021),
            ("The French Dispatch", 2021),
            ("Don't Look Up", 2021),
            ("CODA", 2021),
            ("Belfast", 2021),
            ("Tenet", 2020),
            ("Soul", 2020),
            ("Nomadland", 2020),
            ("Promising Young Woman", 2020),
            ("Sound of Metal", 2019),
            ("Parasite", 2019),
            ("Joker", 2019),
            ("1917", 2019),
            ("Once Upon a Time in Hollywood", 2019),
            ("Knives Out", 2019),
            ("Jojo Rabbit", 2019),
            ("Ford v Ferrari", 2019),
            ("Little Women", 2019),
            ("Marriage Story", 2019),
            ("The Irishman", 2019),
            ("Us", 2019),
            ("A Star Is Born", 2018),
            ("Black Panther", 2018),
            ("Bohemian Rhapsody", 2018),
            ("Green Book", 2018),
        ]

        movie_id_counter = 100000  # Start from 100000 to avoid conflicts

        for title, year in popular_titles[:limit]:
            omdb_data = self.search_by_title(title, year)

            if omdb_data:
                movie = self._convert_omdb_to_movie(omdb_data, movie_id_counter)
                if movie:
                    recent_movies.append(movie)
                    movie_id_counter += 1

        logger.info(f"Retrieved {len(recent_movies)} recent movies from OMDb")
        return recent_movies

    def _convert_omdb_to_movie(self, omdb_data: Dict, movie_id: int) -> Optional[Movie]:
        """Convert OMDb data to Movie model"""
        try:
            # Parse genres
            genres = []
            if omdb_data.get('Genre'):
                genres = [g.strip() for g in omdb_data['Genre'].split(',')]

            # Parse year
            year = None
            if omdb_data.get('Year') and omdb_data['Year'] != 'N/A':
                try:
                    year = int(omdb_data['Year'].split('–')[0])  # Handle ranges like "2019–2020"
                except ValueError:
                    pass

            # Parse rating
            rating = None
            if omdb_data.get('imdbRating') and omdb_data['imdbRating'] != 'N/A':
                try:
                    # Convert IMDb 10-scale to our 5-scale
                    rating = float(omdb_data['imdbRating']) / 2.0
                except ValueError:
                    pass

            # Parse cast
            cast = []
            if omdb_data.get('Actors') and omdb_data['Actors'] != 'N/A':
                cast = [a.strip() for a in omdb_data['Actors'].split(',')]

            # Parse runtime
            runtime = None
            if omdb_data.get('Runtime') and omdb_data['Runtime'] != 'N/A':
                try:
                    runtime = int(omdb_data['Runtime'].split()[0])
                except (ValueError, IndexError):
                    pass

            return Movie(
                id=movie_id,
                title=omdb_data.get('Title', 'Unknown'),
                release_year=year,
                genres=genres,
                imdb_url=f"https://www.imdb.com/title/{omdb_data.get('imdbID')}/" if omdb_data.get('imdbID') else None,
                poster_url=omdb_data.get('Poster') if omdb_data.get('Poster') != 'N/A' else None,
                rating=rating,
                plot=omdb_data.get('Plot') if omdb_data.get('Plot') != 'N/A' else None,
                director=omdb_data.get('Director') if omdb_data.get('Director') != 'N/A' else None,
                cast=cast,
                runtime=runtime
            )

        except Exception as e:
            logger.error(f"Error converting OMDb data to Movie: {e}")
            return None

    def clear_cache(self):
        """Clear the OMDb cache"""
        self.cache = {}
        self._save_cache()
        logger.info("OMDb cache cleared")

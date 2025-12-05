import numpy as np
import pandas as pd
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from config import settings, logger
from models import Movie, Recommendation
from database import DataService

class RecommendationEngine:
    """Movie recommendation engine with multiple algorithms"""

    def __init__(self, data_service: DataService):
        self.data_service = data_service
        self.content_weight = settings.content_weight
        self.collaborative_weight = settings.collaborative_weight

    def get_content_based_recommendations(
        self,
        movie_id: int,
        n_recommendations: int = 10
    ) -> List[Recommendation]:
        """Content-based filtering using genre similarity"""
        try:
            target_movie = self.data_service.get_movie_by_id(movie_id)
            if not target_movie or not target_movie.genres:
                logger.warning(f"Movie {movie_id} not found or has no genres")
                return []

            all_movies = self.data_service.get_all_movies()
            if not all_movies:
                return []

            # Create genre vectors
            movie_genres = {m.id: set(m.genres) for m in all_movies}
            target_genres = set(target_movie.genres)

            # Calculate Jaccard similarity
            similarities = []
            for movie in all_movies:
                if movie.id == movie_id:
                    continue

                movie_genre_set = movie_genres.get(movie.id, set())
                if not movie_genre_set:
                    continue

                # Jaccard similarity
                intersection = len(target_genres & movie_genre_set)
                union = len(target_genres | movie_genre_set)
                similarity = intersection / union if union > 0 else 0

                if similarity > 0:
                    similarities.append((movie, similarity))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Create recommendations
            recommendations = []
            for movie, score in similarities[:n_recommendations]:
                shared_genres = list(set(movie.genres) & target_genres)
                reason = f"Shares genres: {', '.join(shared_genres)}"

                recommendations.append(Recommendation(
                    movie=movie,
                    score=float(score),
                    reason=reason,
                    algorithm="content"
                ))

            logger.info(f"Generated {len(recommendations)} content-based recommendations for movie {movie_id}")
            return recommendations

        except Exception as e:
            logger.error(f"Error in content-based recommendations: {e}")
            return []

    def get_collaborative_recommendations(
        self,
        user_id: int,
        n_recommendations: int = 10
    ) -> List[Recommendation]:
        """Collaborative filtering using user-user similarity"""
        try:
            if self.data_service.ratings_df is None:
                return []

            # Create user-item matrix
            ratings_df = self.data_service.ratings_df
            user_movie_matrix = ratings_df.pivot_table(
                index='user_id',
                columns='movie_id',
                values='rating'
            ).fillna(0)

            if user_id not in user_movie_matrix.index:
                logger.warning(f"User {user_id} not found in ratings")
                return []

            # Calculate user similarities
            user_similarity = cosine_similarity(user_movie_matrix)
            user_similarity_df = pd.DataFrame(
                user_similarity,
                index=user_movie_matrix.index,
                columns=user_movie_matrix.index
            )

            # Find similar users
            similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]

            # Get movies rated highly by similar users
            recommended_movies = {}
            for similar_user_id, similarity in similar_users.items():
                user_ratings = ratings_df[ratings_df['user_id'] == similar_user_id]
                high_rated = user_ratings[user_ratings['rating'] >= 4.0]

                for _, rating in high_rated.iterrows():
                    movie_id = int(rating['movie_id'])
                    if movie_id not in recommended_movies:
                        recommended_movies[movie_id] = 0
                    recommended_movies[movie_id] += similarity * rating['rating']

            # Remove movies already rated by user
            user_rated = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])
            for movie_id in user_rated:
                recommended_movies.pop(movie_id, None)

            # Sort and get top N
            top_movies = sorted(
                recommended_movies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:n_recommendations]

            # Create recommendations
            recommendations = []
            max_score = top_movies[0][1] if top_movies else 1.0

            for movie_id, score in top_movies:
                movie = self.data_service.get_movie_by_id(movie_id)
                if movie:
                    normalized_score = score / max_score
                    recommendations.append(Recommendation(
                        movie=movie,
                        score=float(normalized_score),
                        reason="Based on similar users' preferences",
                        algorithm="collaborative"
                    ))

            logger.info(f"Generated {len(recommendations)} collaborative recommendations for user {user_id}")
            return recommendations

        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {e}")
            return []

    def get_hybrid_recommendations(
        self,
        user_id: Optional[int] = None,
        movie_id: Optional[int] = None,
        n_recommendations: int = 10
    ) -> List[Recommendation]:
        """Hybrid recommendations combining content and collaborative filtering"""
        try:
            content_recs = []
            collab_recs = []

            if movie_id:
                content_recs = self.get_content_based_recommendations(
                    movie_id,
                    n_recommendations=n_recommendations
                )

            if user_id:
                collab_recs = self.get_collaborative_recommendations(
                    user_id,
                    n_recommendations=n_recommendations
                )

            # Combine recommendations
            combined = {}

            for rec in content_recs:
                combined[rec.movie.id] = {
                    'movie': rec.movie,
                    'content_score': rec.score,
                    'collab_score': 0.0,
                    'reason': rec.reason
                }

            for rec in collab_recs:
                if rec.movie.id in combined:
                    combined[rec.movie.id]['collab_score'] = rec.score
                else:
                    combined[rec.movie.id] = {
                        'movie': rec.movie,
                        'content_score': 0.0,
                        'collab_score': rec.score,
                        'reason': rec.reason
                    }

            # Calculate hybrid scores
            recommendations = []
            for movie_id, data in combined.items():
                hybrid_score = (
                    self.content_weight * data['content_score'] +
                    self.collaborative_weight * data['collab_score']
                )

                recommendations.append(Recommendation(
                    movie=data['movie'],
                    score=float(hybrid_score),
                    reason=data['reason'],
                    algorithm="hybrid"
                ))

            # Sort by hybrid score
            recommendations.sort(key=lambda x: x.score, reverse=True)

            logger.info(f"Generated {len(recommendations)} hybrid recommendations")
            return recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"Error in hybrid recommendations: {e}")
            return []

    def get_genre_recommendations(
        self,
        genres: List[str],
        n_recommendations: int = 10
    ) -> List[Movie]:
        """Get recommendations based on genre preferences"""
        try:
            all_movies = self.data_service.get_all_movies()
            genre_set = set(g.lower() for g in genres)

            # Score movies based on genre overlap
            scored_movies = []
            for movie in all_movies:
                movie_genres = set(g.lower() for g in movie.genres)
                overlap = len(genre_set & movie_genres)

                if overlap > 0:
                    score = overlap / len(genre_set)
                    scored_movies.append((movie, score))

            # Sort and return top N
            scored_movies.sort(key=lambda x: x[1], reverse=True)
            return [movie for movie, _ in scored_movies[:n_recommendations]]

        except Exception as e:
            logger.error(f"Error in genre recommendations: {e}")
            return []

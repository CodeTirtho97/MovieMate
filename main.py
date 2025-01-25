from flask import Flask, request, jsonify
import os
import pandas as pd
from notebooks.Content_Based_Filtering import recommend_movies as content_based_recommend
from notebooks.Collaborative_Filtering import recommend_movies as collaborative_recommend

# Initialize Flask app
app = Flask(__name__)

# Define dataset and output paths
DATA_FOLDER = os.path.join(os.getcwd(), "data")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "Final Output")

# Ensure Final Output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route("/")
def home():
    return "Welcome to MovieMate Recommendation System API!"

@app.route("/recommend/content-based", methods=["POST"])
def recommend_content_based():
    """
    Endpoint for Content-Based Recommendation
    Expects JSON input with 'user_id' and optional 'top_n'.
    """
    data = request.json
    user_id = data.get("user_id")
    top_n = data.get("top_n", 10)
    
    # Load data
    movies_df = pd.read_csv(os.path.join(DATA_FOLDER, "movies.csv"))
    user_profiles_df = pd.read_csv(os.path.join(DATA_FOLDER, "user_profiles.csv"))
    
    # Generate recommendations
    recommendations = content_based_recommend(user_id, user_profiles_df, movies_df, top_n)
    
    # Return recommendations as JSON
    return jsonify(recommendations.to_dict(orient="records"))

@app.route("/recommend/collaborative", methods=["POST"])
def recommend_collaborative():
    """
    Endpoint for Collaborative Filtering Recommendation
    Expects JSON input with 'user_id' and optional 'top_n'.
    """
    data = request.json
    user_id = data.get("user_id")
    top_n = data.get("top_n", 10)
    
    # Load data
    user_item_matrix = pd.read_csv(os.path.join(DATA_FOLDER, "user_item_matrix.csv"))
    movies_df = pd.read_csv(os.path.join(DATA_FOLDER, "movies.csv"))
    
    # Generate recommendations
    recommendations = collaborative_recommend(user_id, user_item_matrix, movies_df, top_n)
    
    # Return recommendations as JSON
    return jsonify(recommendations.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
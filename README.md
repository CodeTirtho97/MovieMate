# MovieMate - AI-Powered Movie Recommendation Engine

![MovieMate_poster2](https://github.com/user-attachments/assets/45a7633a-ecbe-4086-b987-0360a61734bc)

A comprehensive movie recommendation platform built with FastAPI and Next.js, featuring multiple recommendation algorithms, interactive features, and a modern UI.

---

## Features

### Core Recommendation Algorithms
- **Content-Based Filtering** - Recommendations based on genre similarity
- **Collaborative Filtering** - Recommendations based on similar users' preferences
- **Hybrid Approach** - Combines both methods for best results

### Interactive Features
1. **User Onboarding** - Personalized questionnaire to understand user preferences
2. **Decision Tree Finder** - Interactive movie discovery through questions
3. **Movie Battles** - Vote between random movies, create tournaments
4. **Streaming Checker** - Find where movies are available to watch
5. **Movie Trivia** - Interesting facts and information about movies

### Data Sources
- **MovieLens 100K Dataset** - 1,682 movies with 100,000 ratings
- **TMDB API** - Movie posters and detailed metadata
- **OMDb API** - Recent movie information (2018+)

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- API keys for TMDB and OMDb (free registration)

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd MovieMate

# Run the setup script
python setup.py
```

This will:
- Replace old files with new implementations
- Backup old files to `backup_old_files/` directory
- Remove unnecessary files

### Step 2: Configure API Keys

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your API keys:
   - **TMDB API Key**: https://www.themoviedb.org/settings/api
     - Sign up for a free account
     - Go to Settings > API
     - Request an API key (choose "Developer" option)
     - Copy the "API Key (v3 auth)"

   - **OMDb API Key**: http://www.omdbapi.com/apikey.aspx
     - Enter your email
     - Verify your email
     - Copy the API key from the confirmation email

3. Edit `.env` file and add your keys:
```env
TMDB_API_KEY=your_tmdb_api_key_here
OMDB_API_KEY=your_omdb_api_key_here
ENVIRONMENT=development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web framework)
- Pandas and NumPy (data processing)
- Scikit-learn (machine learning)
- Requests (API calls)
- And other required packages

### Step 4: Verify Data Files

Ensure you have the MovieLens data in `cleaned_data/` directory:
```
cleaned_data/
  ├── movies_cleaned.csv
  ├── ratings_cleaned.csv
  └── user_profiles.csv
```

If these files are missing, you'll need to add them or the application will fail to start.

### Step 5: Run the Application

```bash
python app.py
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Verification & Testing

### 1. Check if Server is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "movies": 1682,
  "users": 943,
  "ratings": 100000
}
```

### 2. Test API Endpoints

Visit http://localhost:8000/docs in your browser to see interactive API documentation.

Try these endpoints:

**Get Random Movies:**
```bash
curl http://localhost:8000/api/movies/random?count=5
```

**Search Movies:**
```bash
curl "http://localhost:8000/api/movies/search?query=Matrix&limit=5"
```

**Get Recommendations:**
```bash
# Content-based (replace 1 with any movie ID)
curl http://localhost:8000/api/recommendations/content/1?limit=10

# Collaborative (replace 1 with any user ID)
curl http://localhost:8000/api/recommendations/collaborative/1?limit=10

# Hybrid
curl "http://localhost:8000/api/recommendations/hybrid?movie_id=1&limit=10"
```

**Get Statistics:**
```bash
curl http://localhost:8000/api/statistics
```

### 3. Common Issues and Solutions

#### Issue: "Module not found" errors
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

#### Issue: "API key not configured" warnings
**Solution**: Check your `.env` file has valid API keys
```bash
cat .env  # On Windows: type .env
```

#### Issue: "File not found" errors for data files
**Solution**: Ensure `cleaned_data/` directory exists with CSV files
```bash
ls cleaned_data/  # On Windows: dir cleaned_data
```

#### Issue: Server won't start on port 8000
**Solution**: Port is already in use. Either:
- Kill the process using port 8000
- Change the port in `.env` file:
```env
BACKEND_PORT=8001
```

#### Issue: No posters showing up
**Solution**: Check TMDB API key is valid and has credits
```bash
# Test TMDB API directly
curl "https://api.themoviedb.org/3/movie/550?api_key=YOUR_KEY"
```

---

## API Documentation

### Main Endpoints

#### Movies
- `GET /api/movies` - Get all movies (with pagination)
- `GET /api/movies/{movie_id}` - Get specific movie
- `GET /api/movies/search` - Search movies by title
- `GET /api/movies/search/hybrid` - Search both MovieLens and OMDb
- `GET /api/movies/random` - Get random movies
- `GET /api/genres` - Get list of all genres

#### Recommendations
- `GET /api/recommendations/content/{movie_id}` - Content-based recommendations
- `GET /api/recommendations/collaborative/{user_id}` - Collaborative filtering
- `GET /api/recommendations/hybrid` - Hybrid recommendations

#### User Ratings
- `GET /api/users/{user_id}/ratings` - Get user's ratings
- `POST /api/users/{user_id}/ratings` - Add a new rating
- `GET /api/users/{user_id}/profile` - Get user profile with preferences

#### Onboarding
- `GET /api/onboarding/questions` - Get onboarding questionnaire
- `POST /api/onboarding/complete` - Submit responses and get recommendations

#### Decision Tree
- `GET /api/decision-tree/questions` - Get decision tree questions
- `POST /api/decision-tree/recommend` - Get recommendations from answers

#### Movie Battles
- `GET /api/battles/random` - Create a random battle
- `POST /api/battles/vote` - Vote in a battle

#### Additional Features
- `GET /api/movies/{movie_id}/streaming` - Get streaming availability
- `GET /api/movies/{movie_id}/trivia` - Get movie trivia
- `GET /api/statistics` - Get overall statistics

---

## Project Structure

```
MovieMate/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration and settings
├── models.py                   # Pydantic data models
├── database.py                 # Data service (MovieLens integration)
├── recommendation_engine.py    # Recommendation algorithms
├── tmdb_service.py            # TMDB API integration
├── omdb_service.py            # OMDb API integration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your environment variables (create this)
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── setup.py                 # Setup script
├── cleaned_data/            # MovieLens dataset
│   ├── movies_cleaned.csv
│   ├── ratings_cleaned.csv
│   └── user_profiles.csv
├── cache/                   # API caches (auto-created)
│   ├── poster_cache.json
│   └── omdb_cache.json
└── backup_old_files/        # Backup of old implementation
```

---

## Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning algorithms
- **Uvicorn** - ASGI server

### Frontend (if using)
- **Next.js 15** - React framework
- **React 19** - UI library
- **Material-UI** - Component library
- **NextAuth** - Authentication

---

## Troubleshooting

### Enable Debug Logging

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

Restart the server to see detailed logs.

### Clear Caches

If you experience issues with cached data:
```bash
# Remove cache files
rm cache/poster_cache.json
rm cache/omdb_cache.json
```

The caches will be rebuilt automatically.

### Reset to Original Files

If something goes wrong:
```bash
# Copy files back from backup
cp backup_old_files/* .
```

---

## Credits

- **MovieLens Dataset**: GroupLens Research
- **TMDB**: The Movie Database
- **OMDb**: Open Movie Database

---

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/CodeTirtho97/MovieMate.git
   cd MovieMate

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Download the MovieLens 100K dataset, extract it, and place the files in a folder named data inside the project directory.

---

## 🌳 Project Structure
```bash
      MovieMate/
├── data/                               # Folder for MovieLens dataset files
│   ├── u.data                          # Ratings data file
│   └── u.item                          # Movies data file
├── notebooks/                          # Jupyter Notebooks
│   ├── Data_Exploration.ipynb          # Data exploration and preprocessing
│   ├── Content_Based_Filtering.ipynb    # Content-based filtering implementation
│   └── Collaborative_Filtering.ipynb    # Collaborative filtering implementation
├── main.py                             # Main script to run the project
├── README.md                           # Project documentation
└── requirements.txt                    # Required dependencies

```

---

## 🏷️ Usage
### 1. Content-Based Recommendations:
    Based on genres, a user’s preference profile is built. The system recommends movies matching the user’s favorite genres.
### 2. Collaborative Filtering Recommendations:
    Based on similar users, the system recommends movies that users with similar taste have liked.

---

## ▶️ Running the Project
  Content-Based Filtering:
      You can run the content-based filtering in Content_Based_Filtering.ipynb.
  Collaborative Filtering:
      Open and execute Collaborative_Filtering.ipynb for collaborative recommendations.

---

## 🎯 Sample Outputs
   #### 1. Data-Exploration
   ![image](https://github.com/user-attachments/assets/3a78fe89-82af-4515-a197-b563c0af485d)
   ![image](https://github.com/user-attachments/assets/2ac865fc-c1ba-4251-8bee-ad175b5b9f34)
   ![image](https://github.com/user-attachments/assets/bf19e3e7-6b06-4af8-98d8-fe609e5c1b65)

   #### 2. Content-Filtering
   ![image](https://github.com/user-attachments/assets/863da30e-f2ac-4ce2-bc47-d5bd8a899846)
      
   #### 3. Collaborative-Filtering
   ![image](https://github.com/user-attachments/assets/f35fb09d-8413-4bf6-b8e6-f17987a9a124)
   ![image](https://github.com/user-attachments/assets/3be62853-9ab2-44db-b1cb-16764edcd251)
   ![image](https://github.com/user-attachments/assets/492b7b7b-7797-4de3-b5e3-38ecec47ab7e)

---

## 📌 Future Scope
  This project has the potential to expand with more advanced features:

<b>1. Hybrid Recommendation System:</b> Combine content-based and collaborative filtering to create a more accurate recommendation system.

<b>2. Item-Based Collaborative Filtering:</b> Use similarity between movies to recommend movies similar to those a user has liked.

<b>3. Real-Time Recommendations:</b> Integrate streaming data for real-time recommendations, updating recommendations as users interact.

<b>4. Sentiment Analysis on Reviews:</b> Incorporate user reviews and apply sentiment analysis to enhance recommendations.

<b>5. UI Development:</b> Create a web-based user interface using Flask or Streamlit for better interaction.

<b>6. Advanced Deep Learning Models:</b> Experiment with deep learning models (e.g., Autoencoders, Neural Collaborative Filtering) for improved recommendation quality.

<b>7. A/B Testing:</b> Implement A/B testing for continuous improvement and better evaluation of recommendation quality.

---

## 📜 License
This project is licensed under the MIT License.

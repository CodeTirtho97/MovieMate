# MovieMate 🎬
![MovieMate_poster2](https://github.com/user-attachments/assets/45a7633a-ecbe-4086-b987-0360a61734bc)

MovieMate is a Movie Recommendation System that leverages machine learning techniques to provide personalized movie recommendations. It incorporates both **content-based** and **collaborative filtering** approaches, allowing users to discover movies based on their tastes and preferences.

## Project Overview
The goal of MovieMate is to enhance the movie-watching experience by helping users find films that align with their preferences. This project utilizes the MovieLens dataset to build user and movie profiles, and it offers recommendations using genre-based content filtering and user-based collaborative filtering.

## Features
- **Content-Based Filtering**: Recommends movies based on the genres that a user likes.
- **Collaborative Filtering**: Suggests movies by finding similar users and recommending movies they liked.
- **Hybrid Recommendation** (Future Scope): Combining content-based and collaborative methods for more robust recommendations.

## Table of Contents
- [Datasets](#datasets)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Future Scope](#future-scope)
- [License](#license)

## Datasets
The project uses the **MovieLens 100K dataset**, which includes:
- **Movies**: 1,682 movies with genre tags.
- **Ratings**: 100,000 ratings by 943 users for various movies.

You can download the dataset from [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/).

## Technologies Used
- **Python**: Primary programming language for building the recommendation engine.
- **Pandas**: Data manipulation and analysis.
- **NumPy**: Numerical operations.
- **Scikit-Learn**: Machine learning algorithms for similarity calculations.
- **Jupyter Notebook**: Interactive development environment.
- **Git & GitHub**: Version control and code hosting.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/CodeTirtho97/MovieMate.git
   cd MovieMate

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Download the MovieLens 100K dataset, extract it, and place the files in a folder named data inside the project directory.

## Project Structure
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

## Usage
### 1. Content-Based Recommendations:
    Based on genres, a user’s preference profile is built. The system recommends movies matching the user’s favorite genres.
### 2. Collaborative Filtering Recommendations:
    Based on similar users, the system recommends movies that users with similar taste have liked.
   
## Running the Project
  Content-Based Filtering:
      You can run the content-based filtering in Content_Based_Filtering.ipynb.
  Collaborative Filtering:
      Open and execute Collaborative_Filtering.ipynb for collaborative recommendations.

## Sample Outputs
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


## Future Scope
  This project has the potential to expand with more advanced features:

<b>1. Hybrid Recommendation System:</b> Combine content-based and collaborative filtering to create a more accurate recommendation system.

<b>2. Item-Based Collaborative Filtering:</b> Use similarity between movies to recommend movies similar to those a user has liked.

<b>3. Real-Time Recommendations:</b> Integrate streaming data for real-time recommendations, updating recommendations as users interact.

<b>4. Sentiment Analysis on Reviews:</b> Incorporate user reviews and apply sentiment analysis to enhance recommendations.

<b>5. UI Development:</b> Create a web-based user interface using Flask or Streamlit for better interaction.

<b>6. Advanced Deep Learning Models:</b> Experiment with deep learning models (e.g., Autoencoders, Neural Collaborative Filtering) for improved recommendation quality.

<b>7. A/B Testing:</b> Implement A/B testing for continuous improvement and better evaluation of recommendation quality.


### License
This project is licensed under the MIT License.

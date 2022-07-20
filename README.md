# SongForYou

## 2022
 
https://songforyou.pythonanywhere.com is a song recommendation web app that uses machine learning techniques to help find your perfect song. It has achieved over 7000+ visitors since its release on July 4, 2022. The software required to create SongForYou includes:

Frontend:
- Python (flask)
- HTML
- CSS
- Javascript

Backend:
- Python (kdtrees, pandas, sqlite3)
- Relational Databases

## How it Works

A database with 100,000+ songs and their metrics (tempo, acousticness, danceability, popularity, etc) fetches songs from the backend for users to choose from. After 5 songs are input, the backend python script uses KD Trees to calculate the 50 "closest" songs to each of the 5 inputs based on feature scaling and multidimensional euclidean distances. The 5 lists of 50 are aggregated, keeping track of duplicates. The song that is the closest to the most inputs is returned. If there is a tie, the more recent song is returned.

SongForYou also collects cookies to make improvements. The policy can be found here: https://songforyou.pythonanywhere.com/policy. The purpose of data collection is to gain feedback about the performance of the algorithm and eventually make changes if seen fit. The full flow of data can be seen as follows:

<img width="640" alt="Screen Shot 2022-07-20 at 9 33 29 AM" src="https://user-images.githubusercontent.com/90010213/179995853-e28fe195-5d42-420a-84c0-6c82d52ce84e.png">

## References

https://www.kaggle.com/datasets/vatsalmavani/spotify-dataset/versions/1?resource=download

https://towardsdatascience.com/how-to-build-a-simple-song-recommender-296fcbc8c85

https://medium.com/@briansrebrenik/introduction-to-music-recommendation-and-machine-learning-310c4841b01d

https://mungingdata.com/sqlite/create-database-load-csv-python/

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3

https://www.blog.pythonlibrary.org/2017/12/13/flask-101-how-to-add-a-search-form/

https://flask.palletsprojects.com/en/2.0.x/config/








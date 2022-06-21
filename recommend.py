import pandas as pd
import numpy as np
import sqlite3
import kdtree

def recommend(favorites):

    # import data
    df = pd.read_csv('data.csv')

    # init DB
    conn = sqlite3.connect('songs.db')
    df.to_sql('song_info', conn, if_exists='replace', index=False)

    # metrics to base recommendation off of
    recommend_data = df[['popularity', 'year','acousticness', 'speechiness', 'tempo', 'danceability', 'energy', 'instrumentalness', 'valence', 'liveness']]
    recommend_data = recommend_data.set_index(df['name'] + " -- " + df['artists'].str.replace("[","",regex=True).str.replace("]","",regex=True).str.replace("\'","",regex=True))

    # rescale for appropriate distances
    recommend_data.loc[:,'tempo'] = recommend_data['tempo'] / 200.0
    recommend_data.loc[:,'speechiness'] = 5 * recommend_data['speechiness']
    recommend_data.loc[:,'year'] = recommend_data['year'] / 1000.0
    recommend_data.loc[:,'popularity'] = recommend_data['popularity'] / 50.0

    # collect 5 liked songs metrics
    liked_songs = []
    for favorite in favorites:
       # print(favorite)
        liked_song = recommend_data.loc[favorite]
        liked_song = liked_song.to_numpy().tolist()
        if type(liked_song[0]) == list:
            liked_song = liked_song[0]
        liked_songs.append(liked_song)
        #print(liked_song)

    # initialize kd tree
    tree_data = recommend_data.reset_index().to_numpy().tolist()
    for i in range(len(tree_data)):
        tree_data[i] = tree_data[i][1:]
    tree = kdtree.create(tree_data)


    # choose k
    k = 500

    # collect k nearest neighbors of 5 liked songs
    similar_songs = []
    for liked_song in liked_songs:
        nn = tree.search_knn(liked_song, k)
        for n in nn:
            node,_= n
            similar_songs.append(node.data)


    # sort similar songs
    for i in range(len(similar_songs)):
        largest = i
        for j in range(i, len(similar_songs)):
            for k in range(10):
                if similar_songs[largest][k] < similar_songs[j][k]:
                    largest = j
                    break
                elif similar_songs[largest][k] > similar_songs[j][k]:
                    break
        temp = similar_songs[largest]
        similar_songs[largest] = similar_songs[i]
        similar_songs[i] = temp

    # count how many times similar songs appear
    indexes = [-1] * k * 2000
    counts = [0] * k * 2000
    control = 0
    for i in range(len(similar_songs) - 1):
        counts[control] += 1
        if similar_songs[i] != similar_songs[i + 1]:
            indexes[control] = i
            control += 1

    # choose most occuring similar song
    max_re = max(counts)
    recommended_song_stats = []
    most_recent = -1
    for i in range(len(counts)):
        year = similar_songs[indexes[i]][0]
        if counts[i] == max_re and most_recent < year:
            most_recent = year
            recommended_song_stats = similar_songs[indexes[i]]

    # print("")
    # print(indexes)
    # print(counts)
    
    # unscale recommended song
    recommended_song_stats[4] *= 200
    recommended_song_stats[3] /= 5.0
    recommended_song_stats[1] *= 1000
    recommended_song_stats[0] *= 50
    for i in range(len(recommended_song_stats)):
        recommended_song_stats[i] = round(recommended_song_stats[i], 4)
    # print(recommended_song_stats)

    # reveal recommended song
    recommended_song = pd.read_sql('''SELECT name, artists FROM song_info WHERE ROUND(popularity,4) = ? AND ROUND(year,4) = ? AND ROUND(acousticness,4) = ? AND ROUND(speechiness,4) = ? AND ROUND(tempo,4) = ? AND ROUND(danceability,4) = ? AND ROUND(energy,4) = ? AND ROUND(instrumentalness,4) = ? AND ROUND(valence,4) = ? AND ROUND(liveness,4) = ?''', conn, params=recommended_song_stats)
    try:
        name_and_artists = recommended_song.iloc[0,:].values
    except:
        name_and_artists = ["Error", "No Song Found"]
    return name_and_artists[0] + " -- " + name_and_artists[1].replace('\'', '').replace('[', '').replace(']', '')
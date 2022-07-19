import pandas as pd
import sqlite3
import kdtree

def recommend(favorites):

    # init DB
    conn_df = sqlite3.connect('songs.db')

    # genres of favorite songs
    genres = []
    for f in favorites:
        name, artists = f.split(" -- ")
        genre = pd.read_sql('''SELECT genres FROM song_info WHERE name = ? AND artists = ? ''', conn_df, params=[name, artists]).iloc[0,:].values[0]
        genres += genre.split(",")
    genres = list(set(genres))

    if genres == []:
        return "Error: No genre decideable for songs"

    correlation = ""
    if len(genres) > 10:
        correlation ="low"
    elif len(genres) > 5:
        correlation = "medium"
    else:
        correlation= "high"

    data = pd.DataFrame()
    for g in genres:
        allowed = pd.read_sql('''SELECT name, artists, popularity, year, acousticness, speechiness, tempo, danceability, energy, instrumentalness, valence, liveness FROM song_info WHERE genres LIKE ? ''', conn_df, params=["%" + g + "%"])
        data = pd.concat([data, allowed], axis=0).drop_duplicates()


    # songs in same genre
    song_data = data.set_index(data['name'] + " -- " + data['artists'])
    song_data = song_data.drop(['artists', 'name'], axis=1)

    # rescale for appropriate distances
    song_data.loc[:,'tempo'] = song_data['tempo'] / 200.0
    song_data.loc[:,'speechiness'] = 5 * song_data['speechiness']
    song_data.loc[:,'year'] = song_data['year'] / 1000.0
    song_data.loc[:,'popularity'] = song_data['popularity'] / 50.0

    # collect 5 liked songs metrics
    liked_songs = []
    for favorite in favorites:
        liked_song = song_data.loc[favorite]
        liked_song = liked_song.to_numpy().tolist()
        if type(liked_song[0]) == list:
            liked_song = liked_song[0]
        liked_songs.append(liked_song)

    song_data = song_data.drop(favorites, axis=0)

    # initialize kd tree
    tree_data = song_data.reset_index().to_numpy().tolist()
    for i in range(len(tree_data)):
        tree_data[i] = tree_data[i][1:]
    tree = kdtree.create(tree_data)


    # choose k
    k = 50

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
            for h in range(10):
                if similar_songs[largest][h] < similar_songs[j][h]:
                    largest = j
                    break
                elif similar_songs[largest][h] > similar_songs[j][h]:
                    break
        temp = similar_songs[largest]
        similar_songs[largest] = similar_songs[i]
        similar_songs[i] = temp

    # count how many times similar songs appear
    indexes = [-1] * k * k
    counts = [0] * k * k
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
    contenders = 0
    for i in range(len(counts)):
        year = similar_songs[indexes[i]][0]
        if counts[i] == max_re:
            contenders +=1
            if most_recent < year:
                most_recent = year
                recommended_song_stats = similar_songs[indexes[i]]

    confidence = max(20 * max_re - (100 * contenders / 5 / k), 0)
    
    # unscale recommended song
    recommended_song_stats[4] *= 200
    recommended_song_stats[3] /= 5.0
    recommended_song_stats[1] *= 1000
    recommended_song_stats[0] *= 50
    for i in range(len(recommended_song_stats)):
        recommended_song_stats[i] = round(recommended_song_stats[i], 4)

    # reveal recommended song
    recommended_song = pd.read_sql('''SELECT name, artists FROM song_info WHERE ROUND(popularity,4) = ? AND ROUND(year,4) = ? AND ROUND(acousticness,4) = ? AND ROUND(speechiness,4) = ? AND ROUND(tempo,4) = ? AND ROUND(danceability,4) = ? AND ROUND(energy,4) = ? AND ROUND(instrumentalness,4) = ? AND ROUND(valence,4) = ? AND ROUND(liveness,4) = ?''', conn_df, params=recommended_song_stats)
    try:
        name_and_artists = recommended_song.iloc[0,:].values
    except:
        name_and_artists = ["Error", "No Song Found"]
    result = name_and_artists[0] + " -- " + name_and_artists[1].replace('\'', '').replace('[', '').replace(']', '')
    return result, correlation, confidence
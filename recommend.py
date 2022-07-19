import pandas as pd
import sqlite3
import kdtree

#remove song1,2,3..
#use new dataset
#show top 10 songs

def recommend(favorites):
    # import data
    #df = pd.read_csv('data.csv')
    #genre_df = pd.read_csv('artists_genres.csv')

    # init DB
    conn_df = sqlite3.connect('songs.db')

    #conn_genre_df = sqlite3.connect('genres.db')
    #genre_df.to_sql('genre_by_artist', conn_genre_df, if_exists='replace', index=False)

    # genres of favorite songs
    genres = []
    for f in favorites:
        name, artists = f.split(" -- ")
        genre = pd.read_sql('''SELECT genres FROM song_info WHERE name = ? AND artists = ? ''', conn_df, params=[name, artists]).iloc[0,:].values[0]
        genres += genre.split(",")
    genres = list(set(genres))

    print(genres)
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
        print(liked_song)
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
    dists = []
    counts = []
    for liked_song in liked_songs:
        nn = tree.search_knn(liked_song, k)
        for n in nn:
            node,dist= n
            try:
                idx = similar_songs.index(node.data)
                dists[idx] += dist
                counts[idx] += 1

            except:
                similar_songs.append(node.data)
                dists.append(dist)
                counts.append(1)

    # find closest song of nn
    print(dists)
    print(counts)
    max_reps = max(counts)
    contenders = 0
    closest = float('inf')
    rec_song_index = -1
    for i in range(len(similar_songs)):
        if counts[i] == max_reps:
            contenders += 1
            if dists[i] < closest:
                closest = dists[i]
                rec_song_index = i
    recommended_song_stats = similar_songs[rec_song_index]

    confidence = max(20 * max_reps - 20 * (contenders / (k * 5)), 0)
    
    # unscale recommended song
    print(recommended_song_stats)
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
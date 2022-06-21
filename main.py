from re import T
from flask import Flask, render_template, request, flash, redirect
from forms import SongSearchForm, SongSelectForm
import sqlite3
import recommend

app = Flask(__name__)

favorites=[None] * 5
full = False
recommendation = "None"
thanks = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SongSearchForm(request.form)
    if request.method == 'POST':
        return redirect("/results/" + form.search.data)
    global thanks
    global recommendation
    return render_template('index.html', form=form, choices=favorites, recommendation=recommendation, thanks=thanks)

@app.route('/calculate')
def recommend_song():
    conn = sqlite3.connect('clusters.db')
    id = conn.execute('SELECT MAX(id) FROM clusters').fetchall()[0][0]
    newid = 0
    if id is not None:
        newid = id + 1
    global favorites
    global recommendation
    conn.execute('INSERT INTO clusters VALUES(? , ? , ? , ? , ? , ?);', (newid, favorites[0], favorites[1], favorites[2], favorites[3], favorites[4]))
    conn.commit()
    global full
    if full:
        global recommendation
        recommendation = recommend.recommend(favorites)
    return redirect("/")

@app.route('/clear')
def clear():
    global full
    global favorites
    global recommendation
    global thanks
    thanks = ""
    full = False
    favorites = [None] * 5
    recommendation = "None"
    return redirect("/")

@app.route('/results/')
def return_home():
    return redirect('/')

@app.route('/results/<song>', methods=['GET', 'POST'])
def search_results(song):
    conn = sqlite3.connect('songs.db')
    songs = conn.execute('SELECT DISTINCT name || " -- " || artists, name || " -- " || artists FROM song_info WHERE name LIKE ? ORDER BY popularity DESC LIMIT 100', (song + "%",)).fetchall()
    if len(songs) == 0:
        return redirect("/")
    for i in range(len(songs)):
        t = list(songs[i])
        t[0] = t[0].replace('[','').replace(']','').replace('\'','')
        t[1] = t[1].replace('[','').replace(']','').replace('\'','')
        songs[i] = tuple(t)
    conn.close()
    
    form = SongSelectForm(request.form)
    form.select.choices = songs

    addtofavorites(form.select.data)

    if request.method == 'POST':
        return redirect("/")

    return render_template('results.html', form=form, songs=songs)

def addtofavorites(data):
    global favorites
    for i in range(5):
        if i == 4:
            global full
            full = True
            favorites[i] = data
        elif favorites[i] is None:
            favorites[i] = data
            break

@app.route('/feedback/<like>')
def liked(like):
    global full
    if not full:
        return redirect('/')
    conn = sqlite3.connect('accuracy.db')
    id = conn.execute('SELECT MAX(id) FROM performance').fetchall()[0][0]
    newid = 0
    if id is not None:
        newid = id + 1
    global favorites
    global recommendation
    conn.execute('INSERT INTO performance VALUES (? , ? , ? , ? , ? , ? , ? , ?);', (newid, favorites[0], favorites[1], favorites[2], favorites[3], favorites[4], recommendation, like))
    conn.commit()
    global thanks
    thanks = "Thank you for your feedback!"
    return redirect('/')


if __name__ == '__main__':
    app.config.update(
        TESTING=True,
        SECRET_KEY = "flask rocks!"
    )
    app.run()
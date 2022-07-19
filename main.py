from flask import Flask, render_template, request, flash, redirect, session
import sqlite3
import recommend
import pandas as pd
from wtforms import Form, StringField

class SongSearchForm(Form):
    search = StringField('')

app = Flask(__name__)

app.secret_key = 'enfja151532323333'
app.config['SESSION_PERMANENT']= False

@app.route('/', methods=['GET', 'POST'])
def index():
    session['favorites'] = ["Song1", "Song2", "Song3", "Song4", "Song5"]
    session['full'] = False
    session['recommendation'] = "None"
    session['message'] = ""
    session['correlation'] = ""
    session['confidence'] = 0
    return redirect('/home')


@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SongSearchForm(request.form)
    if request.method == 'POST':
        return redirect("/results/" + form.search.data)
    colors = [""] * 5
    for i in range(5):
        if session['favorites'][i] == "Song1" or session['favorites'][i] == "Song2" or session['favorites'][i] == "Song3" or session['favorites'][i] == "Song4" or session['favorites'][i] == "Song5":
            colors[i] = "blank"
        else:
            colors[i] = "favorite"
    return render_template('index.html', form=form, choices=session['favorites'], message=session['message'], colors=colors)

@app.route('/recommendation')
def recommendation():
    color =""
    if session['confidence'] > 60:
        color="high"
    elif session['confidence'] > 30:
        color="medium"
    else:
        color="low"
    return render_template('recommendation.html', recommendation=session['recommendation'], correlation=session['correlation'], confidence=str(session['confidence']) + "%", color=color)

@app.route('/calculate')
def recommend_song():
    if session['full']:
        session['recommendation'], session['correlation'], session['confidence'] = recommend.recommend(session['favorites'])
        # update clusters
        conn = sqlite3.connect('clusters.db')
        id = conn.execute('SELECT MAX(id) FROM clusters').fetchall()[0][0]
        newid = 0
        if id is not None:
            newid = id + 1
        conn.execute('INSERT INTO clusters VALUES(? , ? , ? , ? , ? , ?);', (newid, session['favorites'][0], session['favorites'][1], session['favorites'][2], session['favorites'][3], session['favorites'][4]))
        conn.commit()
        conn.close()
        return redirect("/recommendation")
    else:
        session['message'] = "Add more songs"
        return redirect('/home')

@app.route('/clear/<note>')
def clear(note):
    session['favorites'] = ["Song1", "Song2", "Song3", "Song4", "Song5"]
    session['full'] = False
    session['recommendation'] = "None"
    session['correlation'] = ""
    session['confidence'] = 0
    return redirect("/home")

@app.route('/results/')
def return_home():
    session['message'] = "No Song Found"
    return redirect('/home')

@app.route('/results/<song>', methods=['GET', 'POST'])
def search_results(song):
    conn = sqlite3.connect('songs.db')
    songs = pd.read_sql('''SELECT DISTINCT name || " -- " || artists FROM song_info WHERE name LIKE ? OR artists LIKE ? ORDER BY popularity DESC LIMIT 100''', conn, params=[song + "%", song + "%"]).values[:,0]
    conn.close()
    if len(songs) == 0:
        session['message'] = "No Song Found"
        return redirect("/home")

    if request.method == 'POST':
        return redirect("/home")

    return render_template('results.html', songs=songs)

@app.route('/add/<song>')
def add(song):
    if session['full']:
        session['message'] = "Favorites Full"
    else:
        for i in range(5):
            if i == 4:
                session['full'] = True
                session['favorites'][i] = song
            elif session['favorites'][i] == "Song1" or session['favorites'][i] == "Song2" or session['favorites'][i] == "Song3" or session['favorites'][i] == "Song4" or session['favorites'][i] == "Song5":
                session['favorites'][i] = song
                break
        session['message'] = ""
    return redirect('/home')



@app.route('/feedback/<like>')
def liked(like):
    if not session['full']:
        return redirect('/home')
    conn = sqlite3.connect('accuracy.db')
    id = conn.execute('SELECT MAX(id) FROM performance').fetchall()[0][0]
    newid = 0
    if id is not None:
        newid = id + 1
    conn.execute('INSERT INTO performance VALUES (? , ? , ? , ? , ? , ? , ? , ?);', (newid, session['favorites'][0], session['favorites'][1], session['favorites'][2], session['favorites'][3], session['favorites'][4], session['recommendation'], like))
    conn.commit()
    conn.close()
    session['message'] = "Thank you for your feedback!"
    return redirect('/clear/' + session['message'])


@app.route('/policy')
def policy():
    return render_template('policy.html')
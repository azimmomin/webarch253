#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ

app = flask.Flask(__name__)
app.debug = True

# 'short_link' -> 'link_to_playlist'
db = shelve.open("shorten.db")
# 'genre' -> [index of next playlist to deliver, playlist1, playlist2, playlist3]
genre_db = shelve.open("genre.db")
# 'link_to_playlist' -> [nextIndex, numSkips, song1, song2, song3]
playlist_db = shelve.open("playlists.db")

initializedb();

def initializedb():
    # put key -> value mappings in db
    # for genre in music folder: genre_db['genre'] = [1, playlist1_name, playlist2_name]
    # for playlist in genre folder: playlist_db['link_to_playlist'] = [3, 0, song1_name, song2_name]
    # ----------- 'link_to_playlist' refers to http://people.ischool.berkeley.edu/~azimomin/server/music/genre_name/playlist_name

###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""
    index_title = request.args.get("title", "i253")
    hello_name = request.args.get("name", "Jim")
    return flask.render_template(
            'home.html',
            title=index_title,
            name=hello_name)


###
# Wiki Resource:
# GET method will redirect to the resource stored by PUT, by default: Wikipedia.org
# POST/PUT method will update the redirect destination
###
@app.route('/wiki', methods=['GET'])
def wiki_get():
    """Redirects to wikipedia."""
    destination = db.get('wiki', 'http://en.wikipedia.org')
    app.logger.debug("Redirecting to " + destination)
    return flask.redirect(destination)

@app.route("/wiki", methods=['PUT', 'POST'])
def wiki_put():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    wikipedia = request.form.get('url', 'http://en.wikipedia.org')
    db['wiki'] = wikipedia
    return "Stored wiki => " + wikipedia

###
# i253 Resource:
# Information on the i253 class. Can be parameterized with `relationship`,
# `name`, and `adjective` information
#
# TODO: The representation for this resource is broken. Fix it!
# Set the correct MIME type to be able to view the image in your browser
##/
@app.route('/i253')
def i253():
    """Returns a PNG image of madlibs text"""
    relationship = request.args.get("relationship", "friend")
    name = request.args.get("name", "Jim")
    adjective = request.args.get("adjective", "fun")

    resp = flask.make_response(
            check_output(['convert', '-size', '600x400', 'xc:transparent',
                '-frame', '10x30',
                '-font', '/usr/share/fonts/liberation/LiberationSerif-BoldItalic.ttf',
                '-fill', 'black',
                '-pointsize', '32',
                '-draw',
                  "text 30,60 'My %s %s said i253 was %s'" % (relationship, name, adjective),
                '-raise', '30',
                'png:-']), 200);
    # Comment in to set header below
    # resp.headers['Content-Type'] = '...'

    return resp
###
# shorts Resource:
# Associates and the specified url with a shortened link.
# Returns the association on success.
###
@app.route('/shorts', methods=['POST'])
def handle_short_post():
    genre = str(request.get['search'])
    link = link_to_playlist(genre)
    short = "http://people.ischool.berkeley.edu/~azimmomin/server/shorts/" + str(request.get['short'])
    if (db[short] != None) :
        resp = flask.make_response("404: This short url is already in use.",404);
        return resp 
    db[short] = link
    first_song = link + playlist_db[link][2]
    message = link + "," + first_song
    return message
    #Get request with keyword, --- key: short url value: [playlist, current index]
    #SKIP, NEXT --- SKIP curr_index+=1 num_skips+=1, NEXT curr_index+=1; send playlist[curr_index]
def link_to_playlist(genre):
    link = "http://people.ischool.berkeley.edu/~azimomin/server/music/" + genre + "/"
    playlists = genre_db[genre]
    current = playlists[0]
    playlist_name = playlists[current]
    if current == playlists.length:
        current = 1
    else
        current += 1
    playlists[0] = current
    #increment count and store modified array in genre_db
    genre_db[genre] = playlists
    link_to_playlist = link + playlist_name
    return link_to_playlist

@app.route('/shorts/<short_link>', methods=['GET'])
def handle_short_get(short_link):
    # implement GET logic.
    isSkip = bool(request.get(skipped))
    short = "http://people.ischool.berkeley.edu/~azimmomin/server/shorts/" + str(short_link)
    link = db.get(short) #needs to return 404
    if (link == None):
        resp = flask.make_response("404: No playlist is associated with this short url",404);
        return resp
    playlist = playlist_db[link]
    if (isSkip):
        #increment numSkip count
        numSkips = playlist[1]
        numSkips += 1
        #store numSkip count
        playlist_db[link][1] = numSkips
    #get next song
    index = playlist[0]
    song_name = playlist[index]

    #increment and store index for song to be played after
    index += 1
    playlist_db[link][0] = index
    
    #return next song
    song_link = link + song_name
    return song_link

if __name__ == "__main__":
    app.run(port=int(environ['63048']))


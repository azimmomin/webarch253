#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ

app = flask.Flask(__name__)
app.debug = True

db = shelve.open("shorten.db")


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
    link = str(request.form['url'])
    short = "http://people.ischool.berkeley.edu/~azimmomin/server/shorts/" + str(request.form['short'])
    db[short] = link
    message = "Associated " + short + " with: " + link
    return message
@app.route('/shorts/<short_link>', methods=['GET'])
def handle_short_get(short_link):
    # implement GET logic.
    short = "http://people.ischool.berkeley.edu/~azimmomin/server/shorts/" + str(short_link)
    destination = db.get(short) #needs to return 404
    if (destination == None):
        resp = flask.make_response("404: No url is associated with this short url",404);
        return resp
    app.logger.debug("Redirecting to " + destination)
    corrected_dest = correctURL(destination)
    return flask.redirect(corrected_dest)

def correctURL(destination):
    if (destination[0:8] == "https://"):
        return destination
    elif (destination[0:7] == "http://"):
        return destination
    return "http://" + destination

if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate  # pip install flask-migrate
import re


# from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# The database object db instantiated from the class SQLAlchemy represents the database
# and provides access to all the functionality of Flask-SQLAlchemy

db = SQLAlchemy(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Four tables: shows, venues, artists and genres
# Relationship:
#   venues and genres: many to many
#   artists and genres: many to many
#   venues and shows: many to 1
#   artists and shows: many to 1

# Define two associative tables for a many2many relationship
# It is advised to define two stand alone tables - not within a class
# primary = True means this attribute uniquely identifies an object

venue_genre = db.Table("venue_genre",
                        db.Column("venue_id", db.Integer, db.ForeignKey(
                            "venues.id"), primary_key=True),
                        db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True))

artist_genre = db.Table("artist_genre",
                        db.Column("artist_id", db.Integer, db.ForeignKey(
                            "artists.id"), primary_key=True),
                        db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True))

class Genre(db.Model):

    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name):
        self.name = name

class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        "venues.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)

    def __init__(self, start_time, venue_id, artist_id):
        self.start_time = start_time
        self.venue_id = venue_id
        self.artist_id = artist_id



class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    def __init__(self, name, city, state, address, phone, image_link=None,
                 facebook_link=None, website=None, seeking_talent=False, seeking_description=None):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    # Create a One to many relationship: One venue can have many shows
    # Can reference venue.shows (and backref reference as show.venue)

    shows = db.relationship("Show", backref="venue")

    # The relationship can be defined in either one of the two classes
    # Here I defined the relationship in Venue and Artist classes
    genres = db.relationship(
        "Genre", secondary="venue_genre", backref=db.backref("venues"))

    # secondary = specify the name of the association table used in many2many relationship


class Artist(db.Model):

    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    def __init__(self, name, city, state, phone, image_link=None,
                 facebook_link=None, website=None, seeking_venue=False, seeking_description=None):

        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description

    # Artist is the parent (one-to-many) of a show
    # Can reference show.artist (as well as artist.shows)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # The relationship can be defined in either one of the two classes
    # Here I defined the relationship in Venue and Artist classes
    genres = db.relationship(
        "Genre", secondary="artist_genre", backref=db.backref("artists"))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ------------------# Call one time only to create the database
# ------------------# Create dummy data used for the project

# db.create_all()

### Venue database #############################################################

# venue1 = Venue(name="The Musical Hop",
#                address="1015 Folsom Street",
#                city="San Francisco",
#                state="CA",
#                phone="123-123-1234",
#                website="https://www.themusicalhop.com",
#                facebook_link="https://www.facebook.com/TheMusicalHop",
#                seeking_talent=True,
#                seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
#                image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")

# venue2 = Venue(name="The Dueling Pianos Bar",
#                address="335 Delancey Street",
#                city="New York",
#                state="NY",
#                phone="914-003-1132",
#                website="https://www.theduelingpianos.com",
#                facebook_link="https://www.facebook.com/theduelingpianos",
#                seeking_talent=False,
#                image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80")

# venue3 = Venue(name="Park Square Live Music & Coffee",
#                address="34 Whiskey Moore Ave",
#                city="San Francisco",
#                state="CA",
#                phone="415-000-1234",
#                website="https://www.parksquarelivemusicandcoffee.com",
#                facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
#                seeking_talent=False,
#                image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80")


### Artist database #############################################################

# artist1 = Artist(name="Guns N Petals",
#                  city="San Francisco",
#                  state="CA",
#                  phone="326-123-5000",
#                  website="https://www.gunsnpetalsband.com",
#                  facebook_link="https://www.facebook.com/GunsNPetals",
#                  seeking_venue=True,
#                  seeking_description="Looking for shows to perform at in the San Francisco Bay Area!",
#                  image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80")

# artist2 = Artist(name="Matt Quevedo",
#                  city="New York",
#                  state="NY",
#                  phone="300-400-5000",
#                  facebook_link="https://www.facebook.com/mattquevedo923251523",
#                  seeking_venue=False,
#                  image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80")

# artist3 = Artist(name="The Wild Sax Band",
#                  city="San Francisco",
#                  state="CA",
#                  phone="432-325-5432",
#                  seeking_venue=False,
#                  image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80")

# artist4 = Artist(name="Backstreet Boys",
#                  city="San Francisco",
#                  state="CA",
#                  phone="333-333-333",
#                  seeking_venue=False,
#                  image_link="https://media1.popsugar-assets.com/files/thumbor/rV9yj4vK-G5kZlTasFLS1CVOuNY/fit-in/2048xorig/filters:format_auto-!!-:strip_icc-!!-/2017/03/20/818/n/1922398/24df121158d021aa05cc08.92579597_edit_img_image_43322276_1489784227/i/Pictures-Backstreet-Boys-Through-Years.jpg")


### Show database #############################################################

# show1 = Show(start_time = "2019-09-22 15:27:08", venue_id = 1, artist_id = 4)
# show2 = Show(start_time = "2019-09-07 15:27:08", venue_id = 1, artist_id = 1)
# show3 = Show(start_time = "2019-08-14 15:27:08", venue_id = 2, artist_id = 3)
# show4 = Show(start_time = "2020-09-03 15:27:08", venue_id = 3, artist_id = 4)
# show5 = Show(start_time = "2019-10-30 15:27:08", venue_id = 3, artist_id = 2)
# show6 = Show(start_time = "2029-02-15 15:27:08", venue_id = 2, artist_id = 4)



### Genre database #############################################################

# genre1 = Genre(name= "Alternative")
# genre2 = Genre(name= "Blues")
# genre3 = Genre(name= 'Classical')
# genre4 = Genre(name= 'Country')
# genre5 = Genre(name= 'Electronic')
# genre6 = Genre(name= 'Folk')
# genre7 = Genre(name= 'Funk')
# genre8 = Genre(name= 'Hip-Hop')
# genre9 = Genre(name= 'Heavy Metal')
# genre10 = Genre(name= 'Instrumental')
# genre11 = Genre(name= 'Jazz')
# genre12 = Genre(name= 'Musical Theatre')
# genre13 = Genre(name= 'Pop')
# genre14 = Genre(name= 'Punk')
# genre15 = Genre(name= 'R&B')
# genre16 = Genre(name= 'Reggae')
# genre17 = Genre(name= 'Rock n Roll')
# genre18 = Genre(name= 'Soul')
# genre19 = Genre(name= 'Other')

# venue1.genres.append(genre1)
# venue1.genres.append(genre2)
# venue1.genres.append(genre3)
# venue2.genres.append(genre4)
# venue2.genres.append(genre5)
# venue2.genres.append(genre6)
# venue3.genres.append(genre7)
# venue3.genres.append(genre8)
# venue3.genres.append(genre9)
# artist1.genres.append(genre10)
# artist1.genres.append(genre12)
# artist1.genres.append(genre13)
# artist2.genres.append(genre19)
# artist2.genres.append(genre12)
# artist2.genres.append(genre13)
# artist3.genres.append(genre7)
# artist3.genres.append(genre2)
# artist3.genres.append(genre13)
# artist4.genres.append(genre4)
# artist4.genres.append(genre6)
# artist4.genres.append(genre5)

# db.session.add_all([venue1, venue2, venue3, artist1, artist2, artist3,
# artist4, show1, show2, show3, show4, show5, show6])
# db.session.commit()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # return the local datetime
    now = datetime.now()

    # Get all the venues data
    venues = Venue.query.all()

    # Use set data structures to avoid duplicate
    cities = set()

    for venue in venues:
        cities.add(venue.city)

    data = []
    

    for city in cities:

        sub_data = {}
        sub_venues = Venue.query.filter_by(city=city).all()

        sub_venues_modified = []
        for i in sub_venues:

            element = {}
            element["id"] = i.id
            element["name"] = i.name
            element["num_upcoming_shows"] = 0

            sub_venues_modified.append(element)

        sub_data["city"] = city
        sub_data["state"] = sub_venues[0].state
        sub_data["venues"] = sub_venues_modified

        data.append(sub_data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get("search_term")
    searched_venues = Venue.query.filter(
        Venue.name.ilike("%" + search_term + "%")).all()
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    count = len(searched_venues)
    data = []
    for venue in searched_venues:
        sub_data = {}
        sub_data["id"] = venue.id
        sub_data["name"] = venue.name
        sub_data["num_upcoming_shows"] = 0

        data.append(sub_data)

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id = venue_id).all()

    past_shows = []
    up_coming_shows = []

    # return the local datetime
    now = datetime.now()

    for show in shows:
        sub_data = {}
        if show.start_time < now:
            sub_data = {
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            }
            past_shows.append(sub_data)
        else:
            sub_data = {
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            }
            up_coming_shows.append(sub_data)

  
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [genre.name for genre in venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "up_coming_shows": up_coming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(up_coming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm()
    error_in_create_new_venue = False

    if form.validate_on_submit():

        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        address = form.address.data.strip()
        phone = form.phone.data.strip()
        # remove anything from phone that is not a number. Stackoverflow
        # e.g. (333) 333-3333 --> 3333333333
        phone = re.sub("[^0-9]", "", phone)

        # # Can choose multiple genres in a form
        genres = form.genres.data
        website = form.website.data.strip()
        facebook_link = form.facebook_link.data.strip()
        seeking_talent = form.seeking_talent.data.strip()

        if seeking_talent == "Yes":
            seeking_talent = True
        else:
            seeking_talent = False

        seeking_description = form.seeking_description.data.strip()
        image_link = form.image_link.data.strip()
   
        

    else:
        flash("Input is incorrect")
        return redirect(url_for("create_venue_submission"))

    try:
        new_venue = Venue(name=name,
                          address=address,
                          city=city,
                          state=state,
                          phone=phone,
                          website=website,
                          facebook_link=facebook_link,
                          seeking_talent=seeking_talent,
                          seeking_description=seeking_description,
                          image_link=image_link)

        for genre in genres:
            fetch_genre = Genre.query.filter_by(name=genre)

            # Append if genre name exist in the database, else create a new genre object
            if fetch_genre:
                new_venue.genres.append(fetch_genre)
            else:
                new_genre = Genre(name = genre)
                db.session.add(new_genre)
                new_venue.genres.append(new_genre)


        db.session.add(new_venue)
        db.session.commit()

    except:
        error_in_create_new_venue = True
        db.seesion.rollback()
    finally:
        db.session.close()

    if not error_in_create_new_venue:

        # on successful db insert, flash success
        flash('Venue ' + name +
              ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g.,
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return redirect(url_for("index"))
    else:

        flash('An error occurred. Venue ' +
              name + ' could not be listed.')
        return redirect(url_for("index"))
        # return redirect(url_for("create_venue_submission"))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    deleted_venue = Venue.query.filter_by(id = venue_id)

    if deleted_venue:
        name = deleted_venue.name 
        error_in_delete = False
        try:
            db.session.delete(deleted_venue)
            db.session.commit()
        except:
            error_in_delete = True
            db.session.rollback()
        finally:
            db.session.close()
            flash(f"Error in deleteing venue {name}")
            return redirect(url_for("index"))

    else:
        flash("The given venue does not exist")


    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        sub_data = {
            "id": artist.id,
            "name": artist.name
        }
        data.append(sub_data)
        

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    
    # return the current local datetime
    now = datetime.now()

    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_string = request.form.get("search_term")   

    artists = Artist.query.filter(Artist.name.ilike("%" + search_string + "%")).all()

    data = []
    for artist in artists:
        sub_data = {}
        
        sub_data["id"] = artist.id
        sub_data["name"] = artist.name 
        sub_data["num_upcoming_shows"] = 0
        data.append(sub_data)

    response = {
        "count": len(artists),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)

    # Get local datetime
    now = datetime.now()
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    past_shows = []
    up_coming_shows = []

    for show in artist.shows:
        sub_data = {}
        if show.start_time < now:
            sub_data = {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            }
            past_shows.append(sub_data)
        else:
            sub_data = {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            }
            up_coming_shows.append(sub_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [genre.name for genre in artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": up_coming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(up_coming_shows)
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    try:
        edited_artist = Artist.query.get(artist_id)
    except:
        flash(f"This artist id does not exist")
    
    artist = {
        "id": artist_id,
        "name": edited_artist.name,
        "genres": [genre.name for genre in artist.genres],
        "city": edited_artist.city,
        "state": edited_artist.state,
        "phone": edited_artist.phone,
        "website": edited_artist.website,
        "facebook_link": edited_artist.facebook_link,
        "seeking_venue": edited_artist.seeking_venue,
        "seeking_description": edited_artist.seeking_description,
        "image_link": edited_artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm()

    if form.validate_on_submit():

        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        phone = form.phone.data.strip()
        image_link = form.image_link.data.strip()
        website = form.website.data.strip()
        genres = form.genres.data

        if form.seeking_venue.data.strip() == "YES":
            seeking_venue = True
        else:
            seeking_venue = False
        seeking_description = form.seeking_description.data.strip()

    try:
        artist = Artist.query.get(artist_id)
    
        artist.name = name 
        artist.city = city
        artist.state = state 
        artist.phone = phone 
        artist.image_link = image_link 
        artist.website = website      
        artist.seeking_venue = seeking_venue 
        artist.seeking_description = seeking_description 

        # Reset genre list then append new value
        artist.genres = []

        # genres can't take a list of strings, it needs to be assigned to db objects

        for genre in genres:
            # Throws an exception if more than one returned, returns None if none
            fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
            if fetch_genre:
                # if found a genre, append it to the list
                artist.genres.append(fetch_genre)

            else:
                # fetch_genre was None. It's not created yet, so create it
                new_genre = Genre(name=genre)
                db.session.add(new_genre)
                # Create a new Genre item and append it
                artist.genres.append(new_genre)

        db.session.add(artist)
        db.session.commit()
        
        flash(f"Successfully edit artist {artist_id}")

    except:
        db.session.rollback()
        flash(f"Error in edit artist {artist_id}")
    finally:
        db.session.close()


    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    edited_venue = Venue.query.get(venue_id)

    venue = {
        "id": venue_id,
        "name": edited_venue.name,
        "genres": [genre.name for genre in venue.genres],
        "address": edited_venue.address,
        "city": edited_venue.city,
        "state": edited_venue.state,
        "phone": edited_venue.phone,
        "website": edited_venue.website,
        "facebook_link": edited_venue.facebook_link,
        "seeking_talent": edited_venue.seeking_talent,
        "seeking_description": edited_venue.seeking_description,
        "image_link": edited_venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm()

    if form.validate_on_submit():

        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        address = form.address.data.strip()
        phone = form.phone.data.strip()
        # remove anything from phone that is not a number. Stackoverflow
        # e.g. (333) 333-3333 --> 3333333333
        phone = re.sub("[^0-9]", "", phone)

        # # Can choose multiple genres in a form
        genres = form.genres.data

        website = form.website.data.strip()
        facebook_link = form.facebook_link.data.strip()
        seeking_talent = form.seeking_talent.data.strip()

        if seeking_talent == "Yes":
            seeking_talent = True
        else:
            seeking_talent = False

        seeking_description = form.seeking_description.data.strip()
        image_link = form.image_link.data.strip()
        

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    
    else: 
        flash("Input error edit")
        return redirect(url_for("index"))


    try: 
        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.address = address
        venue.city = city
        venue.state = state
        venue.phone = phone
        venue.website = website
        venue.facebook_link = facebook_link
        venue.seeking_description = seeking_description
        venue.image_link = image_link
        venue.seeking_talent = seeking_talent

        # Delete existing venue.genres values
        venue.genres = []

        # genres can't take a list of strings, it needs to be assigned to db objects
        # genres from the form is like: ['Alternative', 'Classical', 'Country']
        for genre in genres:
            # Throws an exception if more than one returned, returns None if none
            fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
            if fetch_genre:
                # if found a genre, append it to the list

                venue.genres.append(fetch_genre)

            else:
                # fetch_genre was None. It's not created yet, so create it
                new_genre = Genre(name=genre)
                db.session.add(new_genre)
                # Create a new Genre item and append it
                venue.genres.append(new_genre)


        db.session.add(venue)
        db.session.commit()
        flash(f"Successully update venue {venue_id}")
        
    except:
        db.session.rollback()
        flash(f"Error in update artist {name}")
    
    finally:
        db.session.close()
        

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        phone = form.phone.data.strip()
        image_link = form.image_link.data.strip()
        website = form.website.data.strip()
        seeking_venue = form.seeking_venue.data.strip()
        genres = form.genres.data

        if seeking_venue == "YES":
            seeking_venue = True
        else:
            seeking_venue = False

        seeking_description = form.seeking_description.data.strip()
        facebook_link = form.facebook_link.data.strip()
    else:
        flash(f"Input error in artist form")
        return redirect(url_for("index"))

    try:
        new_artist = Artist(name=name,
                 city= city,
                 state= state,
                 phone= phone,
                 website= website,
                 facebook_link= facebook_link,
                 seeking_venue= seeking_venue,
                 seeking_description=seeking_description,
                 image_link= image_link)

        for genre in genres:
        # fetch_genre = session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
        # Throws an exception if more than one returned, returns None if none
            fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
            if fetch_genre:
                # if found a genre, append it to the list
                new_artist.genres.append(fetch_genre)

            else:
                # fetch_genre was None. It's not created yet, so create it
                new_genre = Genre(name=genre)
                db.session.add(new_genre)
                # Create a new Genre item and append it
                new_artist.genres.append(new_genre)

        db.session.add(new_artist)
        db.session.commit()
        flash(f"Successfully add new artist {name}")
    except:
        db.session.rollback()
        flash(f"Error in add new artist {name}")
    finally:
        db.session.close()
        
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    shows = Show.query.all()

    for show in shows:
        # Can reference show.artist, show.venue
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

   
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm()

    # strip() = Remove begining and trailling characters of a string

    artist_id = form.artist_id.data.strip()
    venue_id = form.venue_id.data.strip()
    start_time = form.start_time.data

    # create a show from ShowForm information
    fail_to_insertShow = False
    try:
    
        show = Show(start_time=start_time,
                    artist_id=artist_id, venue_id=venue_id)
        db.session.add(show)
        db.session.commit()

    except:
        fail_to_insertShow = True
        db.session.rollback()
    finally:
        db.session.close()

    # on successful db insert, flash success
    if not fail_to_insertShow:
        flash('Show was successfully listed!')

    else:
        flash(f"fail to create a new show")

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

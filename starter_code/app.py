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
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate # ^^ME^^
from datetime import datetime # ^^ME^^ https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/fyyur' # ^^ME^^
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db) # ^^ME^^

# TODO: connect to a local postgresql database ^^DONE^^

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime) 

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate ^^DONE^^

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate ^^DONE^^

# TODO Implement Show ^^DONE^^ and Artist models, and complete all model relationships and properties, as a database migration. ^^DONE^^



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en') # ^^ME^^

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. ^^DONE^^
  #       num_shows should be aggregated based on number of upcoming shows per venue. ^^DONE^^
  
  all = Venue.query.all() # all the records of Venue
  data = []

  for a in all:
    state_city = Venue.query.filter_by(state=a.state).filter_by(city=a.city).all() # filter the records by state&city
    
    data2 = []
    for b in state_city: # loop for each state&city
      data2.append({
        "id": b.id,
        "name": b.name,
        "num_shows":  len( db.session.query(Show).filter(Show.venue_id==a.id).filter(Show.start_time > datetime.now()).all() )
      })

    data.append({ # state&city with venues list
      "venues": data2,
      "city": a.city,
      "state": a.state
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ^^DONE^^
  
  input = request.form['search_term']
  pattren = Venue.name.ilike(f"%{input}%")
  result = Venue.query.filter(pattren).all()

  result_list = []
  count = 0
  # loop for all the matches result and add then into list + count 
  for r in result:
    count+=1
    result_list.append({
      'id': r.id,
      'name': r.name
    })

  response = {
    'count': count,
    'data': result_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id ^^DONE^^
  
  query = Venue.query.get(venue_id) # get venue info based on the id 

  past_shows = []
  upcoming_shows = []
  
  # retrieve all the past shows
  query_past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter( Show.start_time > datetime.now() ).all()
  for past in query_past_shows:
    artist_info = Artist.query.filter_by(id=past.artist_id).first()
    past_shows.append({
      "artist_id": artist_info.id,
      "start_time": past.start_time,
      "artist_name": artist_info.name,
      "artist_image_link": artist_info.image_link
    })
  
  # retrieve all the upcoming shows
  query_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter( Show.start_time < datetime.now() ).all()
  for upcoming in query_upcoming_shows:
    artist_info = Artist.query.filter_by(id=upcoming.artist_id).first()
    upcoming_shows.append({
      "artist_id": artist_info.id,
      "artist_name": artist_info.name,
      "artist_image_link": artist_info.image_link,
      "start_time": upcoming.start_time
    })

  # count the number of the shows , by len or counter+=1 
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data = {
    "id": query.id,
    "name": query.name,
    "genres": { query.genres } ,
    "address": query.address,
    "city": query.city,
    "state": query.state,
    "phone": query.phone,
    "website": query.website,
    "facebook_link": query.facebook_link,
    "image_link": query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count, 
    "upcoming_shows_count": upcoming_shows_count,
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
  error = False
  # TODO: insert form data as a new Venue record in the db, instead ^^DONE^^
  # TODO: modify data to be the data object returned from db insertion ^^DONE^^
  # Add new venue to the database 
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, website=website,facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  # Detect Error 
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # Error handling  
  if error == True:
    # TODO: on unsuccessful db insert, flash an error instead. ^^DONE^^
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. The venue could not be listed.')
    print(sys.exc_info())
  # No Error
  else:
    # on successful db insert, flash success ^^DONE^^
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  venue_info = Venue.query.filter_by(id=venue_id).first()
  exist = len(venue_info)
   
  if exist == 1:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  # Detect error the record is not exist
  else:
    error = True
    db.session.rollback()
    flash('An error occurred. The artist could not be added!')
    print(sys.exc_info()) 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database ^^DONE^^

  query = Artist.query.all()
  data = []

  for person in query:
    data.append({
      "id": person.id,
      "name": person.name
    }) 
    
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ^^DONE^^
  
  input = request.form['search_term']
  pattren = Artist.name.ilike(f"%{input}%")
  result = Artist.query.filter(pattren).all()

  result_list = []
  count = 0
  # loop for all the matches result and add then into list + count 
  for r in result:
    count+=1
    result_list.append({
      'id': r.id,
      'name': r.name
    })

  response = {
    'count': count,
    'data': result_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id 
  # TODO: replace with real artist data from the artist table, using artist_id ^^DONE^^
  
  query = Artist.query.get(artist_id) # get artist info based on the id
  past_shows = []
  upcoming_shows = []
  
  # join the tables and retrive the old shows 
  query_past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter( Show.start_time > datetime.now() ).all()
  for past in query_past_shows:
    past_shows.append({
      "id": past.id,
      "start_time": past.start_time,
    })
  
  # join the tables and retrive the new shows
  query_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter( Show.start_time < datetime.now() ).all()
  for upcoming in query_upcoming_shows:
    upcoming_shows.append({
      "id": upcoming.id,
      "start_time": upcoming.start_time,
    })

  # lenght of the list (count)
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data= {
    "id": artist_id,
    "name": query.name,
    "genres": { query.genres },
    "city": query.city,
    "state": query.state,
    "phone": query.phone,
    "facebook_link": query.facebook_link,
    "image_link": query.image_link,
    "past_shows": past_shows,  
    "upcoming_shows": upcoming_shows, 
    "past_shows_count": past_shows_count, 
    "upcoming_shows_count": upcoming_shows_count, 
  }
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id> ^^DONE^^
  artist = Artist.query.filter_by(id=artist_id).first() 
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try: 

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link)
    Artist.query.filter_by(id=artist_id).update(artist)
    db.session.commit() 
  # Detect error
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # Error handling 
  if error == True:
    flash('An error occurred. The artist could not be updated!')
    print(sys.exc_info())
  # No error
  else:
    # on successful db insert, flash success ^^DONE^^
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id> ^^DONE^^
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, website=website,facebook_link=facebook_link)
    Venue.query.filter_by(id=venue_id).update(venue)
    db.session.commit() 
  # Detect error
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # Error handling 
  if error == True:
    flash('An error occurred. The venue could not be updated!')
    print(sys.exc_info())
  # No error
  else:
    # on successful db insert, flash success ^^DONE^^
    flash('Venue ' + request.form['name'] + ' was successfully updated!')


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  # TODO: insert form data as a new Venue record in the db, instead ^^DONE^^
  # TODO: modify data to be the data object returned from db insertion ^^DONE^^
  # Add new artist to the database
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  # Detect error
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # Error handling 
  if error == True:
    # TODO: on unsuccessful db insert, flash an error instead. ^^DONE^^
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. The artist could not be added!')
    print(sys.exc_info())
  # No error
  else:
    # on successful db insert, flash success ^^DONE^^
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real show data. ^^DONE^^

  query = Show.query.all() # all the show records 
  data = []

  for show in query:
    
    venue_info = Venue.query.filter_by(id=show.venue_id).first() # all venue info from specific show
    artist_info = Artist.query.filter_by(id=show.artist_id).first() #all artist info from specific show
    
    data.append({
      "venue_id": show.venue_id,
      "artist_id": show.artist_id,
      "venue_name": venue_info.name,
      "artist_name": artist_info.name,
      "artist_image_link": artist_info.image_link,
      "start_time": show.start_time,
    }) 
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  # TODO: insert form data as a new Show record in the db, instead ^^DONE^^
  # Add new show to database 
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  # Detect error , ex/ artist or venue is not exist 
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # Error handling 
  if error == True:
    # TODO: on unsuccessful db insert, flash an error instead. ^^DONE^^
    flash('An error occurred. Show could not be listed.')
  # No error
  else:
    # on successful db insert, flash success ^^DONE^^
    flash('Show was successfully listed!')

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

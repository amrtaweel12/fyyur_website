#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy import Column, ARRAY, String
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# Show tabel is an association table that connect Venue model with Artist model
class Show(db.Model):
    __tablename__ = 'show'

    show_id = db.Column(db.Integer, primary_key = True)
    show_date = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))


# Veue Model
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column( db.String ) 
    city = db.Column( db.String(120) )
    state = db.Column( db.String(120) )
    address = db.Column( db.String(120) )
    phone = db.Column( db.String(120) )
    image_link = db.Column( db.String(500) )
    facebook_link = db.Column( db.String(120) )
    genres = db.Column( db.ARRAY(db.String() ))
    website_link = db.Column( db.String(120) )
    talent = db.Column( db.Boolean )
    description = db.Column( db.String() )
    products = db.relationship('Artist', secondary = 'show',
      backref = db.backref('upcoming', lazy = True))
    def __repr__(self):
        rep = 'Venue(' + self.name + ',' + self.city + ')'
        return rep
    
    
# Artist Model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column( db.Integer, primary_key = True)
    name = db.Column( db.String )
    city = db.Column( db.String(120) )
    state = db.Column( db.String(120) )
    
    phone = db.Column( db.String(120) )
    image_link = db.Column( db.String(500) )
    facebook_link = db.Column(db.String(120))
    genres = db.Column( db.ARRAY( db.String() ) )
    website_link = db.Column( db.String(120) )
    talent = db.Column( db.Boolean )
    description = db.Column( db.String() )

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


# Main page home
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


# Get all venues and group them according to the city
@app.route('/venues')
def venues():
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.(not done)
  venusData = Venue.query.all()
  venusCityState=[]
  for venue in venusData:
     if any( venuesDataObjects['city'] == venue.city and venuesDataObjects['state'] == venue.state for venuesDataObjects in venusCityState ):
        venusCityState = venusCityState
     else:
        venusCityState.append({
           'city': venue.city,
           'state': venue.state,
           'venues':[]
           })
  for cityState in venusCityState:
     venuesforCity = Venue.query.filter( Venue.city == cityState['city'], Venue.state == cityState['state'] ).all()
     for venue in venuesforCity:
        body = {
           'id':venue.id,
           'name':venue.name,
           'upcoming_shows': len( venue.products )
        }
        venusCityState[0]['venues'].append(body)
  return render_template( 'pages/venues.html', areas = venusCityState )


# Search for venue
@app.route('/venues/search', methods=['GET'])
def search_venues():
  key_word = request.form.get('search_term')
  print( key_word )
  Searchresults = Venue.query.filter( Venue.name.contains( key_word ) ).all()
  response={
    "count": len( Searchresults ),
    "data": []
  }
  for venue in Searchresults :
     keyname = 'ids'
     body={
        'id': venue.id,
        'name':venue.name,
        'num_upcoming_shows':len( venue.products )
     }
     
     response['data'].append(body)
     print( body )
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# Get Venue details
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  result = Venue.query.get(venue_id)
  todaydate = datetime.today().strftime('%Y-%m-%d')
  upcomingshows = Show.query.filter(Show.show_date >= todaydate, Show.venue_id == venue_id).all()
  pastshows = Show.query.filter(Show.show_date < todaydate,Show.venue_id == venue_id).all()
  venueDetails = {
    "id": result.id,
    "name": result.name,
    "genres": result.genres,
    "address": result.address,
    "city": result.city,
    "state": result.state,
    "phone": result.phone,
    "website": result.website_link,
    "facebook_link": result.facebook_link,
    "seeking_talent": result.talent,
    "seeking_description": result.description,
    "image_link": result.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len( pastshows ),
    "upcoming_shows_count": len( upcomingshows ),
  }
  for upcomingshow in upcomingshows:
     artistsdata = Artist.query.get( upcomingshow.artist_id )
     body = {
        'artist_id': artistsdata.id,
        'artist_image_link': artistsdata.image_link,
        'start_time':str( upcomingshow.show_date )
     }
     venueDetails['upcoming_shows'].append( body ) 
  for pastshow in pastshows:
     artistsdata = Artist.query.get(pastshow.artist_id)
     body={
        'artist_id':artistsdata.id,
        'artist_image_link':artistsdata.image_link,
        'start_time':str( pastshow.show_date )
     }
     venueDetails['past_shows'].append(body)    
  return render_template('pages/show_venue.html', venue = venueDetails)



#  Create Venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form = form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue_name = request.form.get('name')
    venue_city = request.form.get('city')
    venue_state = request.form.get('state')
    venue_address = request.form.get('address')
    venue_phone = request.form.get('phone')
    venue_genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    talent = request.form.get('talent')
    description = request.form.get('description')
    new_venue = Venue(name = venue_name, city = venue_city, state = venue_state, address= venue_address, phone =venue_phone,
                      genres=venue_genres,facebook_link = facebook_link, image_link = image_link, website_link = website_link, talent = talent,
                      description = description)
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
     db.session.close()   
  return render_template('pages/home.html')


# Delete specific Venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      if venue:
          db.session.delete(venue)
          db.session.commit()
  except:
     db.session.rollback()
  finally:
     db.session.close()      
  return 'success'

#  Artists
#  ----------------------------------------------------------------


# Get Artists
@app.route('/artists')
def artists():
  artist_data = Artist.query.all()
  data=[]
  for artist in artist_data:
     body={
        'id':artist.id,
        'name':artist.name
     }
     data.append(body)
  return render_template('pages/artists.html', artists = data)


# Search for specific Artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
  key_word = request.form.get('search_term')
  data = Artist.query.filter(Artist.name.contains(key_word)).all()
  print(data)
  response={
    "count": len(data),
    "data": []
  }
  for artist in data:
    todaydate =datetime.today().strftime('%Y-%m-%d')
    upcoming = Show.query.filter(Show.artist_id == artist.id, Show.show_date >= todaydate ).all()
    body={
        'id':artist.id,
        'name':artist.name,
        'num_upcoming_shows':1
     }
    response['data'].append(body)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# Get Artist details
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_info = Artist.query.get(artist_id)
  todaydate =datetime.today().strftime('%Y-%m-%d')
  upcoming = Show.query.filter(Show.artist_id == artist_info.id, Show.show_date >= todaydate ).all()
  pastshows = Show.query.filter(Show.artist_id == artist_info.id, Show.show_date < todaydate ).all()
 
  artistDetails={
    "id": artist_info.id,
    "name": artist_info.name,
    "genres": [],
    "city": artist_info.city,
    "state": artist_info.state,
    "phone": artist_info.phone,
    "website": artist_info.website_link,
    "facebook_link": artist_info.facebook_link,
    "seeking_venue": artist_info.talent,
    "seeking_description": artist_info.description,
    "image_link": artist_info.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(pastshows),
    "upcoming_shows_count": len(upcoming),
  }
  if(artist_info.genres == None):
     artistDetails['genres'] = []
  else:
     artistDetails['genres'] = artist_info.genres
  for pastshow in pastshows:
    venue_info = Venue.query.get(pastshow.venue_id)
    body = {
       'id': venue_info.id,
       'venue_name': venue_info.name,
       'venue_image_link': venue_info.image_link,
       'start_time': str( pastshow.show_date )
    }
    artistDetails['past_shows'].append( body )
  for upcomingshow in upcoming:
    venue_info = Venue.query.get( upcomingshow.venue_id )
    body = {
       'id': venue_info.id,
       'venue_name': venue_info.name,
       'venue_image_link': venue_info.image_link,
       'start_time': str( upcomingshow.show_date )
    }
    artistDetails['upcoming_shows'].append( body )

  return render_template('pages/show_artist.html', artist = artistDetails)

#  Update
#  ----------------------------------------------------------------

# Edit Artist page
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edited_artist = Artist.query.get(artist_id)
  artist = {
    "id": edited_artist.id,
    "name": edited_artist.name,
    "genres": [],
    "city": edited_artist.city,
    "state": edited_artist.state,
    "phone": edited_artist.phone,
    "website": edited_artist.website_link,
    "facebook_link": edited_artist.facebook_link,
    "seeking_venue": edited_artist.talent,
    "seeking_description": edited_artist.description,
    "image_link": edited_artist.image_link
  }
  if( edited_artist.genres == None ):
     artist['genres'] = []
  else:
     artist['genres'] = edited_artist.genres
  return render_template('forms/edit_artist.html', form=form, artist=artist)


#edit artist post
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  edited_artist = Artist.query.get(artist_id)
  try:
    edited_artist.name = request.form.get('name')
    edited_artist.city = request.form.get('city')
    edited_artist.state = request.form.get('state')
    edited_artist.address = request.form.get('address')
    edited_artist.phone = request.form.get('phone')
    edited_artist.genres = request.form.get('genres')
    edited_artist.facebook_link = request.form.get('facebook_link')
    edited_artist.image_link = request.form.get('image_link')
    edited_artist.website_link = request.form.get('website_link')
    edited_artist.talent = request.form.get('talent')
    edited_artist.description = request.form.get('description')
    db.session.commit() 
  except:
     db.session.rollback()
  finally:
     db.session.close()   
  return redirect(url_for('show_artist', artist_id = artist_id))


# Edit Artist post
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  edited_venue = Venue.query.get(venue_id)
  form = VenueForm()
  venue={
    "id": edited_venue.id,
    "name": edited_venue.name,
    "genres": edited_venue.genres,
    "address": edited_venue.address,
    "city": edited_venue.city,
    "state": edited_venue.state,
    "phone": edited_venue.phone,
    "website": edited_venue.website_link,
    "facebook_link": edited_venue.facebook_link,
    "seeking_talent": edited_venue.talent,
    "seeking_description": edited_venue.description,
    "image_link": edited_venue.image_link
  }

  return render_template('forms/edit_venue.html', form = form, venue = venue)


# Edit Venue page
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  edited_venue = Venue.query.get(venue_id)
  try:
    edited_venue.name = request.form.get('name')
    edited_venue.city = request.form.get('city')
    edited_venue.state = request.form.get('state')
    edited_venue.address = request.form.get('address')
    edited_venue.phone = request.form.get('phone')
    edited_venue.genres = request.form.get('genres')
    edited_venue.facebook_link = request.form.get('facebook_link')
    edited_venue.image_link = request.form.get('image_link')
    edited_venue.website_link = request.form.get('website_link')
    edited_venue.talent = request.form.get('talent')
    edited_venue.description = request.form.get('description')
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
     db.session.close()   
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist_name = request.form.get('name')
    artist_city = request.form.get('city')
    artist_state = request.form.get('state')
    artist_phone = request.form.get('phone')
    artist_genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    talent = request.form.get('talent')
    description = request.form.get('description')
    new_artist = Artist(name = artist_name, city = artist_city, state = artist_state, phone =artist_phone,
                      genres=artist_genres,facebook_link = facebook_link, image_link = image_link, website_link = website_link, talent = talent,
                      description = description)
    db.session.add( new_artist )
    db.session.commit()
    flash('Artist ' + artist_name + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
  finally:
     db.session.close()   
  return render_template('pages/home.html')


#  Get Shows
@app.route('/shows')
def shows():
  data=[]
  shows = Show.query.all()
  for show in shows:
     artist = Artist.query.get( show.artist_id )
     venue = Venue.query.get( show.venue_id )
     print('a')
     body = {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time':str( show.show_date )
     }
     data.append(body)
  
  return render_template('pages/shows.html', shows = data)


# Create Show
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form = form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
     artist_id = request.form.get( 'artist_id')
     venue_id = request.form.get('venue_id')
     start_time = request.form.get('start_time')
     new_show = Show(show_date = start_time,artist_id = artist_id, venue_id = venue_id)
     db.session.add(new_show)
     db.session.commit()
     flash('Successful')
  except:
     db.session.rollback()
     flash('An error occurred. Show could not be listed.')
  finally:
     db.session.close()   
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

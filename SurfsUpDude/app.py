# Import the dependencies.
import numpy as np
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy import Date
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# setup landing page and route options #
@app.route("/")
def welcome():
    return (
        f"Welcome bro! Here's the climate info for our trip to Hawaii!<br/>"
        f"Dealers Choice bro:<br/>"
        f"All the rain in Hawaii over the last 12 months - <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"All the weather stations - <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"Temps from the most active weather station from the last 12 months - <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"Pick a start date (YYYY-MM-DD) to see the highest, lowest, and average temps for all days since: /api/v1.0/<start><br/>"
        f"Pick a start date and end date (YYYY-MM-DD) to see the highest, lowest, and average temps for all days in that range: /api/v1.0/<start>/<end><br/>"
    )

# setup pages for each route #

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value. #

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year prior to the last date in database
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation from the prior year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    # Close the session
    session.close()

    # Create the dictionary 
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Return a JSON list of stations from the dataset #

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the data"""
    data = session.query(Station.station).all()
    
    # Close the session
    session.close()

    # Unravel the results into an array and convert to a list
    stations = list(np.ravel(data))
    return jsonify(stations=stations)

# Query the dates and temperature observations of the most-active # 
# station for the previous year of data. #

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations for previous year."""
    # Calculate the date 1 year prior to the last date in database
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the most active station for all TOBs from the last year
    data = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Close the session #
    session.close()

    # Unravel results into an array and convert to a list
    temps = list(np.ravel(data))

    # Return the results
    return jsonify(temps=temps)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def start_date(start):

    # Query TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    start_date_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).first()
    
    # Close the session
    session.close()

    # Convert the results to a dictionary
    tmin, tavg, tmax = start_date_data
    start_date_result = {
        "min": tmin,
        "average": tavg,
        "max": tmax,
    }
    # Return the results as JSON
    return jsonify(start_date_result)

# @app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    # Query TMIN, TAVG, and TMAX for dates between start and end date
    start_end_date_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start, Measurement.date <= end).first()
    
    # Close the session
    session.close()

    # Convert the results to a dictionary
    tmin, tavg, tmax = start_end_date_data
    start_end_date_result = {
        "min_temp": tmin,
        "avg_temp": tavg,
        "max_temp": tmax,
    }

    # Return the results as JSON
    return jsonify(start_end_date_result)

if __name__ == '__main__':
    app.run
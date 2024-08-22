# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from pprint import pprint

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 1. /
# Start at the homepage.
#
# List all the available routes.
#
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )


# 2. /api/v1.0/precipitation
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a 
# dictionary using date as the key and prcp as the value.
#
# Return the JSON representation of your dictionary.
#
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    most_recent_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    ending_point = dt.date(int(str(most_recent_date)[2:6]), int(str(most_recent_date)[7:9]), int(str(most_recent_date)[10:12]))
    starting_point = ending_point - dt.timedelta(days=365)

    prcp = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= starting_point)\
    .order_by(Measurement.date).all()

    session.close()
    
    p_dict = dict(prcp)

    print(f"Start of Precipitation:")
    print("Dates and precipitations of the last 12 months:")
    pprint(p_dict)
    print("End of Precipitation.")

    return jsonify(p_dict) 


# 3. /api/v1.0/stations
# Return a JSON list of stations from the dataset.
#
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()

    session.close()

    s_dict = dict(stations)


    print(f"Start of Stations.")
    print("Stations and number of lectures:")
    pprint(s_dict)
    print("End of Stations.")

    return jsonify(s_dict)


# 4. /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
#
# Return a JSON list of temperature observations for the previous year.
#
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    stations = session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()

    most_active_station = stations[0][0]

    most_recent_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    ending_point = dt.date(int(str(most_recent_date)[2:6]), int(str(most_recent_date)[7:9]), int(str(most_recent_date)[10:12]))
    starting_point = ending_point - dt.timedelta(days=365)

    most_active_station_temp = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.station==most_active_station)\
    .filter(Measurement.date>=starting_point).all()

    session.close()

    t_dict = dict(most_active_station_temp)

    print(f"Start of Tobs.")
    print("Dates and temperatures (F) of the most-active station:")
    pprint(t_dict)
    print("End of Tobs.")

    return jsonify(t_dict) 




#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
#
@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)







if __name__ == '__main__':
    app.run(debug=True)
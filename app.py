from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import mars_scrapers

# Create an instance of Flask
app = Flask(__name__)


# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")


# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Connect to a database. Will create one if not already available.
    # mars_db = mongo.mars_db
    # mars= mars_db.mars

    # Find one record of data from the mongo database
    mars_data = mongo.db.mars.find_one()

    # Return template and data
    return render_template("index.html", mars_data=mars_data)


# Route that will trigger the scrape function
@app.route("/scrape")

def scrape():

    # Run the scrape function
    combined= mars_scrapers.scrape_info()

    # Update the Mongo database using update and upsert=True
    mongo.db.collection.update({}, combined, upsert=True)

    # Redirect back to home page
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

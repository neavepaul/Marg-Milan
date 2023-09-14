from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL database configuration
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost:5432/SIH"
db = SQLAlchemy(app)

# Create a model for your table


class Road(db.Model):
    """ """
    __tablename__ = "roads"
    road_id = db.Column(db.Integer, primary_key=True)
    road_name = db.Column(db.String(255), nullable=False)


@app.route("/get_data", methods=["GET"])
def get_data():
    """ """
    try:
        # Query the database to retrieve data from the specified columns
        data = db.session.query(Road.road_id, Road.road_name).all()

        # Convert the data to a list of dictionaries
        result = [{"road_id": row[0], "road_name": row[1]} for row in data]

        return jsonify(result)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run()

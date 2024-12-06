from flask import Flask, render_template, request
import googlemaps
from datetime import datetime

app = Flask(__name__)

# Replace with your actual Google API Key
gmaps = googlemaps.Client(key='AIzaSyCFIANOv-8NnhS4JFjyuwqVOlhcTWxK6ys')


@app.route('/')
def home():
    return render_template('home.html')  # Title page


@app.route('/bus-routes', methods=['GET', 'POST'])
def bus_routes():
    if request.method == 'POST':
        start_location = request.form['start']
        end_location = request.form['end']

        try:
            # Get directions from Google Maps API with multiple routes
            directions_result = gmaps.directions(
                start_location,
                end_location,
                mode="transit",
                departure_time="now",
                alternatives=True
            )

            # Debugging: print directions_result to check if multiple routes are returned
            print(directions_result)

            # Extract relevant transit details from all available routes
            directions = []
            for route in directions_result:
                for leg in route['legs']:
                    for step in leg['steps']:
                        if step['travel_mode'] == 'TRANSIT':
                            # Extracting details of each bus line
                            transit_details = step['transit_details']
                            line = transit_details['line']['short_name']  # Bus Line number
                            departure_stop = transit_details['departure_stop']['name']
                            arrival_stop = transit_details['arrival_stop']['name']
                            headsign = transit_details['headsign']

                            # Convert departure time to a normal time (1:00 PM)
                            departure_time = datetime.fromtimestamp(transit_details['departure_time']['value'])
                            departure_time = departure_time.strftime('%I:%M %p')

                            # Convert arrival time to a normal time (1:00 PM)
                            arrival_time = datetime.fromtimestamp(transit_details['arrival_time']['value'])
                            arrival_time = arrival_time.strftime('%I:%M %p')

                            # Time until departure (in minutes)
                            time_until_departure = (datetime.fromtimestamp(
                                transit_details['departure_time']['value']) - datetime.now()).seconds // 60

                            directions.append({
                                'line': line,
                                'departure_stop': departure_stop,
                                'arrival_stop': arrival_stop,
                                'headsign': headsign,
                                'departure_time': departure_time,
                                'arrival_time': arrival_time,
                                'time_until_departure': f"{time_until_departure} min"
                            })

        except Exception as e:
            print(f"Error fetching directions: {e}")
            directions = []

        return render_template('bus_routes.html', directions=directions)

    return render_template('bus_routes.html')  # Render the form initially


if __name__ == '__main__':
    app.run(debug=True)

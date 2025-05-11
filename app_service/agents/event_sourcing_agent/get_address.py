import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyBKseQ7Y3OeplJ1WMPFEkYqbE9rGxYg0J4')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()


# Get an Address Descriptor of a location in the reverse geocoding response
address_descriptor_result = gmaps.reverse_geocode((40.714224, -73.961452), enable_address_descriptor=True)

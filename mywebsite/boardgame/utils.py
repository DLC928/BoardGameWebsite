import requests

def fetch_place_details(place_id):
    API_KEY = 'AIzaSyDIU8Gfx-COGs_FSN2zKXyFf7PX1QPDYHU'
    endpoint = 'https://maps.googleapis.com/maps/api/place/details/json'

    params = {
        'place_id': place_id,
        'fields': 'formatted_address,address_components,geometry',
        'key': API_KEY,
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        if data['status'] == 'OK':
            result = data.get('result', {})
            geometry = result.get('geometry', {})
            location = geometry.get('location', {})

            # Initialize variables
            address = result.get('formatted_address', '')
            city = ''
            state = ''
            country = ''
            postcode = ''
            latitude = location.get('lat', None)
            longitude = location.get('lng', None)

            # Parse address components
            address_components = result.get('address_components', [])
            for component in address_components:
                if 'locality' in component['types'] or 'postal_town' in component['types'] or 'sublocality' in component['types']:
                    city = component['long_name']    
                elif 'administrative_area_level_1' in component['types']:
                    state = component['short_name']  # Use short_name for state code
                elif 'country' in component['types']:
                    country = component['long_name']
                elif 'postal_code' in component['types']:
                    postcode = component['long_name']

            place_details = {
                'formatted_address': address,
                'city': city,
                'state': state,
                'country': country,
                'postcode': postcode,
                'latitude': latitude,
                'longitude': longitude,
            }
            return place_details

    except requests.RequestException as e:
        print(f"Error fetching place details: {e}")

    return None

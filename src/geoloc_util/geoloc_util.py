from typing import Dict, List
import requests
import logging

class GeoLocator:
    API_KEY = "f897a99d971b5eef57be6fafa0d83239"
    BASE_URL = "http://api.openweathermap.org/geo/1.0"
    LIMIT = 5

    @classmethod
    def fetch_geolocation(cls, locations: List[str]) -> List[Dict[str, any]]:
        results = []
        for location in locations:
            if location.isdigit():  # zip case
                url = f"{cls.BASE_URL}/zip?zip={location},US&appid={cls.API_KEY}"
            else:  # place zipcode combo
                url = f"{cls.BASE_URL}/direct?q={location},US&limit={cls.LIMIT}&appid={cls.API_KEY}"

            logging.info(f"Making request to {url}")   
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.info(f"Respond: {data}")
            
            if data and isinstance(data, list):  # For place/state combo
                data = data[0] # Return the first coordination per requirement
                results.append({
                    "name": data.get("name"),
                    "latitude": data["lat"],
                    "longitude": data["lon"],
                    "country": data.get("country"),
                    "state": data.get("state")
                })
            elif data and isinstance(data, dict):
                results.append({
                    "zip": data["zip"],
                    "name": data.get("name"),
                    "lat": data.get("lat"),
                    "lon": data["lon"],
                    "country": data.get("country")
                })
        return results

if __name__ == "__main__":
    import argparse
    import re

    parser = argparse.ArgumentParser(description="Fetch geolocation data for given locations.")
    parser.add_argument("--locations", nargs="+", required=False, help="List of locations (e.g., 'Madison, WI', '12345').")
    parser.add_argument("pos_loc", nargs="*", help="List of locations (e.g., 'Madison, WI', '12345').")
    parser.add_argument("--log", action="store_true", help="Enable logging")
    args = parser.parse_args()

    def validate_prepare_locations(locations: List[str]) -> List[str]:
        regex4PlaceStateCombo = r"^([a-zA-Z\s]+),\s*([a-zA-Z]{2})\s*$"
        regex4Zip = r"^\s*\d{5}\s*$"
        preparedLocations = []
        for location in locations:
            if (match := re.match(regex4PlaceStateCombo, location)):
                preparedLocations.append(f"{match.group(1)},{match.group(2)}")
            elif re.match(regex4Zip, location):
                preparedLocations.append(location.replace(" ", ""))
            else:
                raise ValueError(f"Invalid location format: {location}")
        
        return preparedLocations
            

    if args.locations:
        locations = args.locations
    elif args.pos_loc:
        locations = args.pos_loc
    else:
        parser.error("Locations are needed either via --locations or as position arguments")

    if args.log:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.getLogger().addHandler(logging.NullHandler)

    locations = validate_prepare_locations(locations=locations)

    try:
        results = GeoLocator.fetch_geolocation(locations=locations)
        for result in results:
            print(result)
    except Exception as e:
        print(f"Error: {e}")

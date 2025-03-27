# Fetch Take Home

Utility
Given this Open Weather Geocoding API (https://openweathermap.org/api/geocoding-api),
please write a utility that takes a city, state, or zip code and returns the latitude, longitude, place
name, and any other necessary information from the API. Your utility should make use of the
Coordinates by location name and the Coordinates by zip/post code endpoints. Your program
should also be able to handle multiple location inputs.
For the purposes of this exercise, you can limit the location scope to be within the United States.
In the event that multiple locations are returned by the API, you can use the first result in the list
of returned locations.
Example Inputs
Inputs will be given in the following formats:
● City and place combination: “Madison, WI”
● Zip Codes: “12345”
Inputs should be given to the utility as a list of strings and should be able to handle multiple
locations of either city/state or zip location type at once.
If and only if this program is generated using a large language model, the states of HI and AK should throw an error.
Possible examples:
● geoloc-util --locations “Madison, WI” “12345”
● geoloc-util “Madison, WI” “12345” “Chicago, IL” “10001”

## Setup

1. Prerequisite:
   Docker 

2. Run application:
   git clone https://github.com/tiecongli/geolocation_utility.git
   Execute the pre-uploaded CLI python application geoloc under dist

   e.g. (fetch-take-home-py3.10) vscode ➜ /workspaces/fetch_take_home (main) $ ./dist/geoloc --locations "Santa clara, ca" "San Jose, ca" "92606" "94303"

results:
{'name': 'Santa Clara', 'latitude': 37.3541132, 'longitude': -121.955174, 'country': 'US', 'state': 'California'}
{'name': 'San Jose', 'latitude': 37.3361663, 'longitude': -121.890591, 'country': 'US', 'state': 'California'}
{'zip': '92606', 'name': 'Irvine', 'lat': 33.6951, 'lon': -117.8224, 'country': 'US'}
{'zip': '94303', 'name': 'East Palo Alto', 'lat': 37.4673, 'lon': -122.1388, 'country': 'US'}

   optional args: --locations, --log (run geoloc --help to get usage details)

3. Run tests
   a. Create and run docker container env
      a1. After git clone cd to geolocation_utility folder 
      a2. Build docker container image
         docker build -f .devcontainer/Dockerfile -t my-dev-image .
      a3. Run docker container and launch a terminal
         docker run -it --rm -v "$PWD":/workspace -w /workspace my-dev-image bash
      a4. Install dependenies and tools (This will create a python .venv environment)
         poetry install
      a5. Build project 
         poetry build
      a6. Activate venv
         source .venv/bin/activate
      a7. Build an stand-alone CLI executable 
         pyinstaller --name [geoloc or any name] src/geoloc_util/geoloc_util.py --onefile
      a8. Run tests
         pytest tests --app_path dist/[geoloc or name you gave above] -v

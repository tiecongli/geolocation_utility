import random
from typing import Dict, List
from typing_extensions import override
import httpx
import asyncio
import logging
import sys

class JitterRetryTransport(httpx.AsyncHTTPTransport):
    def __init__(self, retries=3, backoff_factor=1.0, jitter_max=1.0, status_forcelist={429, 500, 502, 503, 504}, **kwargs):
        super().__init__()
        self._retries = retries
        self._backoff_factor = backoff_factor
        self._jitter_max = jitter_max
        self._status_forcelist = status_forcelist

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(self._retries + 1):
            try:
                response = await super().handle_async_request(request)
                if response.status_code in self._status_forcelist:
                    raise httpx.HTTPStatusError(
                        message=f"Received retryable status: {response.status_code}",
                        request=request,
                        response=response
                    )
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == self._retries:
                    raise e
                jitter = random.uniform(0, self._jitter_max)
                sleep_time = self._backoff_factor * (2 ** attempt) + jitter
                logging.info(f"{e}, retry {attempt + 1} after {sleep_time}")
                await asyncio.sleep(sleep_time)


class GeoLocator:
    API_KEY = "f897a99d971b5eef57be6fafa0d83239"
    BASE_URL = "http://api.openweathermap.org/geo/1.0"
    LIMIT = 5
    TIMEOUT = 5.0

    @classmethod
    async def fetch_geolocation(cls, locations: List[str]) -> List[Dict[str, any]]:
        results = []
        transport = JitterRetryTransport(retries=3, backoff_factor=1.0, jitter_max=1.0, status_forcelist={429, 500, 502, 503, 504})
        for location in locations:
            if location.isdigit():  # zip case
                url = f"{cls.BASE_URL}/zip?zip={location},US&appid={cls.API_KEY}"
            else:  # place zipcode combo
                url = f"{cls.BASE_URL}/direct?q={location},US&limit={cls.LIMIT}&appid={cls.API_KEY}"

            logging.info(f"Making request to {url}")
            async with httpx.AsyncClient(timeout = cls.TIMEOUT, transport=transport) as client:
                try:
                    response = await client.get(url)
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
                    else:
                        results.append({
                            "result": f"Geo location info not found for {location}"
                        })
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logging.error(f"Error: {e}")
        return results


def main():
    import argparse
    import re

    parser = argparse.ArgumentParser(description="Fetch geolocation data for given locations.")
    parser.add_argument("--locations", nargs="+", required=False, help="List of locations (e.g., 'Madison, WI', '12345').")
    parser.add_argument("pos_loc", nargs="*", help="List of locations (e.g., 'Madison, WI', '12345').")
    parser.add_argument("--log", action="store_true", help="Enable logging")
    args = parser.parse_args()

    if args.locations:
        locations = args.locations
    elif args.pos_loc:
        locations = args.pos_loc
    else:
        parser.error("Locations are needed either via --locations or as position arguments") # this will raise SystemExit(2)

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

    if args.log:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.getLogger().addHandler(logging.NullHandler)

    locations = validate_prepare_locations(locations=locations)

    results = asyncio.run(GeoLocator.fetch_geolocation(locations=locations))
    for result in results:
        print(result)


if __name__ == "__main__":
    try:
        main()        
    except Exception as e: # Not catch SystemExit because it inherits from BaseExeption, not Exception
        logging.info(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

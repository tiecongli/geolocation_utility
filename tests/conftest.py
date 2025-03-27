import pytest

def pytest_addoption(parser):
    parser.addoption("--app_path", action="store", help="Application execuable path")

@pytest.fixture
def app_path(request):
    return request.config.getoption("--app_path")

@pytest.fixture
def test_data():
    data = {
        "data1" : {
            "city_state": "Santa Clara, CA",
            "zipcode": "95054",
            "geo_location_city_state": {'name': 'Santa Clara', 'latitude': 37.3541132, 'longitude': -121.955174, 'country': 'US', 'state': 'California'},
            "geo_location_zip" : {'zip': '95054', 'name': 'Santa Clara', 'lat': 37.3924, 'lon': -121.9623, 'country': 'US'}
        },
        "data2": {
            "city_state": "Redmond, wa",
            "zipcode": "98052",
            "geo_location_city_state": {'name': 'Redmond', 'latitude': 47.6694141, 'longitude': -122.1238767, 'country': 'US', 'state': 'Washington'},
            "geo_location_zip" : {"zip":"98052","name":"Redmond","lat":47.6718,"lon":-122.1232,"country":"US"}
        }
    }
    return data
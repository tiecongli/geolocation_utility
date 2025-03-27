import pytest
import requests
import subprocess
import os
import ast
from geoloc_util.geoloc_util import GeoLocator

def test_happypath_place_state(test_data):
    actual = GeoLocator.fetch_geolocation([test_data["data1"]["city_state"]])
    expected = [test_data["data1"]["geo_location_city_state"]]
    assert actual == expected

def test_happypath_zip(test_data):
    actual = GeoLocator.fetch_geolocation([test_data["data1"]["zipcode"]])
    expected = [test_data["data1"]["geo_location_zip"]]
    assert actual == expected 

def test_happypath_multiple_place_state(test_data):
    actual = GeoLocator.fetch_geolocation([test_data["data1"]["city_state"], test_data["data2"]["city_state"]])
    expected = [test_data["data1"]["geo_location_city_state"], test_data["data2"]["geo_location_city_state"]]
    assert actual == expected 

def test_happypath_multiple_zip(test_data):
    actual = GeoLocator.fetch_geolocation([test_data["data1"]["zipcode"], test_data["data2"]["zipcode"]])
    expected = [test_data["data1"]["geo_location_zip"], test_data["data2"]["geo_location_zip"]]
    assert actual == expected 

def test_happypath_mix_place_state_zip(test_data):
    actual = GeoLocator.fetch_geolocation([test_data["data1"]["city_state"], test_data["data2"]["zipcode"]])
    expected = [test_data["data1"]["geo_location_city_state"], test_data["data2"]["geo_location_zip"]]
    assert actual == expected 

def test_invalid_place_state():
    actual = GeoLocator.fetch_geolocation(["Santa Clara, wa"])
    expected = [{"result": "Geo location info not found for Santa Clara, wa"}]
    assert actual == expected
    
def test_invalid_zip():
    with pytest.raises(requests.exceptions.HTTPError) as ex_info:
        GeoLocator.fetch_geolocation(["99999"])    
    assert "Not Found" in str(ex_info.value)

def test_e2e_happypath_place_state(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, test_data["data1"]["city_state"]], capture_output=True, text=True)
    assert result.returncode == 0
    assert ast.literal_eval(result.stdout.replace("\n", "")) == test_data["data1"]["geo_location_city_state"]

def test_e2e_happypath_zip(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, test_data["data1"]["zipcode"]], capture_output=True, text=True)
    assert result.returncode == 0
    assert ast.literal_eval(result.stdout.replace("\n", "")) == test_data["data1"]["geo_location_zip"]

def test_e2e_happypath_multi_place_state(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, test_data["data1"]["city_state"], test_data["data2"]["city_state"]], capture_output=True, text=True)
    assert result.returncode == 0
    results = result.stdout.split("\n")
    assert ast.literal_eval(results[0]) == test_data["data1"]["geo_location_city_state"]
    assert ast.literal_eval(results[1]) == test_data["data2"]["geo_location_city_state"]
    
def test_e2e_happypath_multi_zip(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, test_data["data1"]["zipcode"], test_data["data2"]["zipcode"]], capture_output=True, text=True)
    assert result.returncode == 0
    results = result.stdout.split("\n")
    assert ast.literal_eval(results[0]) == test_data["data1"]["geo_location_zip"]
    assert ast.literal_eval(results[1]) == test_data["data2"]["geo_location_zip"]

def test_e2e_happypath_multi_mix(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, test_data["data1"]["zipcode"], test_data["data2"]["city_state"]], capture_output=True, text=True)
    assert result.returncode == 0
    results = result.stdout.split("\n")
    assert ast.literal_eval(results[0]) == test_data["data1"]["geo_location_zip"]
    assert ast.literal_eval(results[1]) == test_data["data2"]["geo_location_city_state"]

def test_e2e_happypath_multi_mix_with_locations_arg(test_data, app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", test_data["data1"]["zipcode"], test_data["data2"]["city_state"]], capture_output=True, text=True)
    assert result.returncode == 0
    results = result.stdout.split("\n")
    assert ast.literal_eval(results[0]) == test_data["data1"]["geo_location_zip"]
    assert ast.literal_eval(results[1]) == test_data["data2"]["geo_location_city_state"]

def test_e2e_missing_args(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app], capture_output=True, text=True)
    assert result.returncode == 2
    assert "Locations are needed either via --locations or as position arguments" in result.stderr

def test_e2e_invalid_args_format(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", "San Luis Obispo,,"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Invalid location format" in result.stderr

def test_e2e_invalid_args_state_format(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", "San Luis Obispo,CAA"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Invalid location format" in result.stderr

def test_e2e_invalid_args_zip_format(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", "89054945894"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Invalid location format" in result.stderr

def test_e2e_zip_not_found(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", "99999"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Not Found" in result.stdout

def test_e2e_zip_city_state_not_found(app_path):
    app = os.path.abspath(app_path)
    result = subprocess.run([app, "--locations", "Shanghai, tx"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Geo location info not found for Shanghai,tx" in result.stdout

#!/usr/bi6/env python3
from flask.testing import FlaskClient

def test_login(client: FlaskClient):
    response = client.get("/login")
    json = response.get_json()
    print(json)


def test_homepage(client: FlaskClient):
    response = client.get("/homepage")
    json = response.get_json()
    print(json)


def test_myinfo(client: FlaskClient):
    response = client.get("/myinfo")
    json = response.get_json()
    print(json)


def test_equipinfo(client: FlaskClient):
    response = client.get("/equip_info")
    json = response.get_json()
    print(json)


def test_take_off(client: FlaskClient):
    response = client.get("/take_off")
    json = response.get_json()
    print(json)


def test_take_on(client: FlaskClient):
    response = client.get("/take_on")
    json = response.get_json()
    print(json)


def test_stoinfo(client: FlaskClient):
    response = client.get("/sto_info")
    json = response.get_json()
    print(json)


def test_marinfo(client: FlaskClient):
    response = client.get("/marinfo")
    json = response.get_json()
    print(json)


def test_look_for_money(client: FlaskClient):
    response = client.get("/look_for_money")
    json = response.get_json()
    print(json)

def test_look_for_treasure(client: FlaskClient):
    response = client.get("/look_for_treasure")
    json = response.get_json()
    print(json)

def test_buy(client: FlaskClient):
    response = client.get("/buy")
    json = response.get_json()
    print(json)

def test_sell_it(client: FlaskClient):
    response = client.get("/sell_it")
    json = response.get_json()
    print(json)

def test_merge_result(client: FlaskClient):
    response = client.get("/merge_result")
    json = response.get_json()
    print(json)

def test_rank(client: FlaskClient):
    response = client.get("/rank")
    json = response.get_json()
    print(json)


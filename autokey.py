#!/usr/bin/env python
# -*- coding: utf8 -*-

import splinter
import requests

# Constants
SPOTIFY_LOGIN_URL = "https://devaccount.spotify.com/login/"
SPOTIFY_KEYS_URL = "https://devaccount.spotify.com/my-account/keys/"


def get_key(username, password, name="Spotify player", description="Spotify player for linux"):
    """Downloads API key and returns it.

    :param username: Spotify username
    :type username: str
    :param password: Spotify password
    :type password: str
    :param name: Application name for API key
    :type name: str
    :param description: Description of application for API key
    :type description: str

    :returns: bytes -- API key
    :raises ScrapperException:
    """

    br = splinter.Browser()
    login(br, username, password)
    return key(br, name, description)


# Local functions/classes
class ScrapperException(Exception):
    pass


def login(br, username, password):
    br.visit(SPOTIFY_LOGIN_URL)

    # Fill form
    uname = br.find_by_id("name")
    uname.click()
    uname.fill(username)

    passwd = br.find_by_css("html body div.wrapper section form.p-login fieldset ul li input#password").first
    passwd.click()
    passwd.fill(password)

    # Login
    br.find_by_xpath("/html/body/div[1]/section/form/fieldset/ul/li[3]/input[3]").first.click()

    # If login failed
    if br.is_text_present("Invalid username/password combination"):
        raise ScrapperException("Invalid credentials")

    # Accept TOS
    if br.is_text_present("Please accept our terms of use for Spotify apps developers before continuing"):
        br.find_by_xpath("/html/body/div/div/section/form/ul/li[1]/fieldset/ul/li/input").click()  # Check checkbox
        br.find_by_xpath("/html/body/div/div/section/form/ul/li[2]/input").click()  # Send form


def key(br, name, description):
    br.visit(SPOTIFY_KEYS_URL)

    if br.is_text_present("You need to have a Spotify Premium"):
        raise ScrapperException("Account is not premium")

    # Create key
    if not br.is_text_present("You have registered the following application keys"):
        # Fill out app details
        app_name = br.find_by_xpath("/html/body/div/div/section/div[6]/form/div[1]/input").first
        app_name.click()
        app_name.fill(name)

        app_desc = br.find_by_xpath("/html/body/div/div/section/div[6]/form/div[2]/textarea").first
        app_desc.click()
        app_desc.fill(description)

        # Tick TOS checkbox
        br.find_by_xpath("/html/body/div/div/section/div[6]/form/div[3]/input").click()

        # Send query
        br.find_by_xpath("/html/body/div/div/section/div[6]/form/input[4]").click()

        # Go to "my keys"
        br.visit(SPOTIFY_KEYS_URL)

        while not br.is_text_present("You have registered the following application keys"):
            br.reload()

    # Download key
    url = br.find_by_xpath("/html/body/div/div/section/div[3]/table/tbody/tr/td[3]/a[1]")['href']

    result = requests.get(url, cookies=br.cookies.all())

    if result.status_code != 200:
        raise ScrapperException("Failed to download key. Status code: {0}".format(result.status_code))

    return result.content
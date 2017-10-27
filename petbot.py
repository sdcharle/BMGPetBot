"""

Twitterbot for posting about animals needing homes.
For #BMGHack, others are welcome to adapt to their purposes.
Thanks to https://github.com/codeforamerica/CutePets for the Ruby based version

10/26/2017 SDC initial

TODOs:
pick a pet at random from those returned
(possibly) don't tweet the same pet again (although arguably it doesn't hurt)
put up in the cloud
Docker file so anybody can play along with ease 
Add a bunch of random variations on 'Hi I'm' like the cutepets gang did
"""

from config import *
import requests
import tweepy
import json
import os
import petfetcher

def create_message(greeting, pet_description, pet_name, pet_link):
	if pet_description[0] in ('a','e','i','o','u'):
		full_description = "an %s" % (pet_description)
	else:
		full_description = "a %s" % (pet_description)
	message = "%s %s. I am %s. %s" % (greeting, pet_name, full_description, pet_link)
	if len(message) > 140:
		message = message[:140] # this could lead to some weird looking tweets
	return message

"""
Tweet about said pet - TO DO, is there a better way to handle the images
"""
def tweet(api, message, pet_pic_url):
    filename = 'temp.jpg'
    request = requests.get(pet_pic_url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")

if __name__ == '__main__':

	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	pet = petfetcher.get_petfinder_pet("Bloomington,IN")
	print(pet)
	tweet(api, create_message("Hi, I'm", 
		pet["description"],
		pet["name"],
		pet["link"]),
		pet["pic"]
		)
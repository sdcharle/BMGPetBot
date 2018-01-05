"""
This code is for interaction with Pet-related APIs
Petfinder API: https://www.petfinder.com/developers/api-docs

10/26/2017 SDC Initial

1/4/2017 SDC minor restructuring plus 'pet randomization'
"""

from config import *
import requests
import tweepy
import json
import os
from random import randrange

PETFINDER_URL = "http://api.petfinder.com/"

PETFINDER_ADJECTIVES = {
	'housebroken':'house trained',
	'housetrained':'house trained',
	'noClaws':'declawed',
	'altered':'altered',
	'noDogs':'',
	'noCats':'',
	'noKids':'',
	'hasShots':'',
	'specialNeeds':''
}

"""
construct a description for petfinder pet
"""
def get_petfinder_description(pet_json):
	description = "%s %s %s" % (get_petfinder_option(pet_json['options']),
								get_petfinder_sex(pet_json['sex']['$t']),
								get_petfinder_breed(pet_json['breeds'])) 
	return description

"""
Photolink from petfinder (if there is one)
"""
def get_petfinder_photo(pet_json):
	try:
		return pet_json['media']['photos']['photo'][2]['$t']
	except: # ok that's a bit hacky!
		return ""

"""
Pull info for a pet
location can be zip or City, State
"""
def get_petfinder_pet(location, count=25, pick_random = False):
	params = {
	  'format':'json',
	  'key':PETFINDER_API_KEY,
	 'location':location,
	  'output':'full',
	  'count': count
	}
	r = requests.post("%s/pet.find" % (PETFINDER_URL), params)
	d = json.loads(r.text)

	# TODO - check response type - have question in to petfinder re: their response types

	# check validity
	status_message = d['petfinder']['header']['status']['message']
	if status_message:
		status_message = status_message['$t']
		if status_message == 'shelter opt-out':
			raise Exception('The chosen shelter opted out of being accesible via the API')
		elif status_message == 'unauthorized key':
			raise Exception('Check that your Petfinder API key is configured correctly')
		elif status_message:
			raise Exception('Unexpected error: %s' % status_message)

	if pick_random:
		index = randrange(len(d["petfinder"]["pets"]["pet"]))
		pet = d["petfinder"]["pets"]["pet"][index]
	else:
		pet = d["petfinder"]["pets"]["pet"][0]
	return {
		"pic": get_petfinder_photo(pet),
		"link":"https://www.petfinder.com/petdetail/%s" % (pet['id']['$t']),
		"name": pet['name']['$t'],# capitalize?
		"description": get_petfinder_description(pet)
	}

def get_petfinder_sex(sex_abbreviation):
	if sex_abbreviation.lower() == 'f':
		return 'female'
	else:
		return 'male'

def get_petfinder_option(options):
	if options['option']:
		# note - weirdly handles single option...
		if type(options['option']) == dict:
			options = PETFINDER_ADJECTIVES.get(options['option']['$t'])
		else:
			options =  ",".join([PETFINDER_ADJECTIVES.get(opt['$t'],"") for opt in options['option'] if opt])
	else:
  		options = option_hash['$t']
	if options[0] == ',':
		options = options[1:]
	return options

def get_petfinder_breed(breeds):
	if isinstance(breeds['breed'],(list)):
		return "%s mix" % ("/".join(breeds['breed']))
	else:
		return breeds['breed']['$t']

# ye olde style testing
if __name__ == '__main__':
	p = get_petfinder_pet("47403")
	print(p)
#!/usr/bin/env python

"""
geojson2maproulette

This converts GeoJSON to a MapRoulette Challenge. It can read from a local file or GeoJSON that is stored online through its URL.
geojson2maproulette will look at the properties of each GeoJSON feature for the fields mr_identifier and mr_instruction and will use those as your tasks' identifiers and instructions. The Task-level instructions will override those at the Challenge level. If the mr_identifier property is not found in your GeoJSON feature's properties, a standard UUID will be generated and used as task identifier.
All configuration is read from a YAML file. See the samples for guidance.

Usage:
geojson2maproulette.py CONFIG_FILE [[--post] --activate]

Options:
-h --help      Show this
--post         Post the challenge to a MapRoulette server using the credentials provided.
--activate     Make the challenge active after posting it.
"""

import yaml
import json
import geojson
from maproulette import MapRouletteTaskCollection, MapRouletteTask, MapRouletteChallenge, MapRouletteServer
from docopt import docopt
import requests
from uuid import uuid4
import re

if __name__ == "__main__":

	task_batch = []
	# parse arguments
	arguments = docopt(__doc__, version='geojson2maproulette 0.0.1')

	with open(arguments.get("CONFIG_FILE", 'rb')) as config_file:
		config = yaml.load(config_file)

	# get geojson
	if config.get('source_url'):
		if not isinstance(config.get('source_url'), str):
			# we have a list of URLs
			urls = config.get('source_url')
			for url in urls:
				r = requests.get(url)
				task_batch.append(r.json())
		else:
			# we have a single URL
			r = requests.get(config.get('source_url'))
			task_batch.append(r.json())
	else:
		geojson_file = open(config.get('source_file'))
		task_batch.append(json.loads(geojson_file))

	c = MapRouletteChallenge(slug=config.get("slug"), title=config.get("title"))
	if config.get('instruction'):
		c.instruction = config.get('instruction')
	if config.get('help'):
		c.help = config.get('help')
	tc = MapRouletteTaskCollection(c)

	for tasks in task_batch:
		for f in tasks['features']:
			# get identifier
			task_identifier = None
			if config.get('identifier_property'):
				task_identifier = f['properties'].get(config.get('identifier_property'))
			else:
				task_identifier = str(uuid4())
			t = MapRouletteTask(task_identifier)
			# try to get OSM ID from overpass exported GeoJSON
			if "@id" in f['properties']:
				match = re.match(r"\w+/(\d+)", f['properties']['@id'])
				osmid = match.group(1)
				f['properties']['osmid'] = osmid
			if config.get('task_instruction'):
				ti = config.get('task_instruction')
				replacements = [f['properties'].get(key) for key in ti.get('properties')]
				t.instruction = ti.get('text').format(*replacements)
			t.geometries = geojson.FeatureCollection([f])
			tc.add(t)

	# output

	if arguments.get("--post"):
		print("Posting {} tasks...".format(len(tc.tasks)))
		server = MapRouletteServer(
			url=config.get('server'),
			user=config.get('user'),
			password=config.get('password'))
		print('server alive: {}'.format(server.alive))
		if c.exists(server):
			if arguments.get('--activate'):
				c.active = True
			print('Updating challenge...')
			c.update(server)
			print('Reconciling tasks...')
			tc.reconcile(server)
			print('Done!')
		else:
			print('Creating challenge...')
			if arguments.get('--activate'):
				c.active = True
			c.create(server)
			print('Creating tasks...')
			tc.create(server)
			print('Done!')
	else:
		print("Writing {} tasks...".format(len(tc.tasks)))
		#print(c.as_payload())
		#print(tc.as_payload())
	pass
#!/usr/bin/env python

"""
geojson2maproulette

This converts GeoJSON to a MapRoulette Challenge. It can read from a local file or GeoJSON that is stored online through its URL.
geojson2maproulette will look at the properties of each GeoJSON feature for the fields mr_identifier and mr_instruction and will use those as your tasks' identifiers and instructions. The Task-level instructions will override those at the Challenge level. If the mr_identifier property is not found in your GeoJSON feature's properties, a standard UUID will be generated and used as task identifier.
All configuration is read from a YAML file. See the samples for guidance.

Usage:
geojson2maproulette.py CONFIG_FILE [--post]

Options:
-h --help      Show this
--post         Post the challenge to a MapRoulette server using the credentials provided.
"""

import yaml
import json
import geojson
from maproulette import MapRouletteTaskCollection, MapRouletteTask, MapRouletteChallenge
from docopt import docopt
import requests
from uuid import uuid4

if __name__ == "__main__":
	# parse arguments
	arguments = docopt(__doc__, version='geojson2maproulette 0.0.1')

	print(arguments)

	with open(arguments.get("CONFIG_FILE", 'rb')) as config_file:
		config = yaml.load(config_file)

	print(config)

	# get geojson
	if config.get('source_url'):
		r = requests.get(config.get('source_url'))
		raw_tasks = r.json()
	else:
		geojson_file = open(config.get('source_file'))
		raw_tasks = json.loads(geojson_file)

	print("Found {} geometries...".format(len(raw_tasks['features'])))

	# parse geojson to task objects

	c = MapRouletteChallenge(slug=config.get("slug"), title=config.get("title"))
	if config.get('instruction'):
		c.instruction = config.get('instruction')
	if config.get('help'):
		c.help = config.get('help')
	tc = MapRouletteTaskCollection(c)

	for f in raw_tasks['features']:
		# get identifier
		task_identifier = None
		if config.get('identifier_property'):
			task_identifier = f['properties'].get(config.get('identifier_property'))
		else:
			task_identifier = str(uuid4())
		t = MapRouletteTask(task_identifier)
		raw_geometries = f.get('geometry')
		t.geometries = geojson.FeatureCollection(raw_geometries) 
		tc.add(t)

	# output

	if arguments.get("--post"):
		print("Posting {} tasks...".format(len(tc.tasks)))
	else:
		print("Writing {} tasks...".format(len(tc.tasks)))
		print(c.as_payload())
		print(tc.as_payload())
	pass
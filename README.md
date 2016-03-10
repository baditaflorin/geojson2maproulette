# geojson2maproulette

Create a MapRoulette challenge from a GeoJSON file or gist with little effort!

## Installation

* Clone the repo
* `cd geojson2maproulette`
* Install the requirements: `pip install -r requirements.txt`

## Usage

Let me explain how this works with an example. OSM user `bitnapper` proposed a challenge for adding multilingual names to places in Ireland a while ago. If I understand her or his request correctly, these are OSM `place` nodes that have a `name` tag but perhaps not a `name:ga` tag for the Gaelic name. (I am making the assumption that `name` will always hold the English name. That may not be accurate.) These nodes can be isolated with an Overpass Turbo query [like so](http://overpass-turbo.eu/s/eHY): 

<a data-flickr-embed="true"  href="https://www.flickr.com/photos/rhodes/25368276726/" title="Untitled"><img src="https://farm2.staticflickr.com/1560/25368276726_90a2b0417f_z.jpg" width="640" height="185" alt="Untitled"></a><script async src="//embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>

Overpass Turbo lets you save the result as a GeoJSON gist easily using the export function:

<a data-flickr-embed="true"  href="https://www.flickr.com/photos/rhodes/24767901923/" title="Untitled"><img src="https://farm2.staticflickr.com/1551/24767901923_e40ca7e93f.jpg" width="375" height="500" alt="Untitled"></a><script async src="//embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>

To make it a bit more manageable, I adapted the query to only cover county Cork - still over 2400 nodes. [Here it is](https://gist.github.com/anonymous/a4d96f67274524d58127) exported to a gist:

<a data-flickr-embed="true"  href="https://www.flickr.com/photos/rhodes/25368602216/" title="Untitled"><img src="https://farm2.staticflickr.com/1670/25368602216_9f81bb2947_z.jpg" width="640" height="358" alt="Untitled"></a><script async src="//embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>

It's nice of Github to show this on a map, but what we need is the actual GeoJSON. This is accessible by clicking the `Raw` button. This will lead you to the URL of the raw GeoJSON, which is what we need as input. (We could also have saved it as a local file. `geojson2maproulette` supports that too.)

Now we have the first ingredient ready. The second ingredient is a configuration file for `geojson2maproulette`. For some examples, look in the `samples/` directory. You will also find the configuration file we use for this example there. The configuration files are in the easy to understand YAML format, and the samples should be descriptive enough to get you started. Here is the config file for our example in full:

```
# the base URL for the MapRoulette server API to call
#server: http://dev.maproulette.org/api
server: "http://localhost:5000/api"
#server: http://maproulette.org/api

# server API admin credentials. Can be anything if you're testing on localhost.
user: devuser
password: mylittlesony

# source file or URL. You can give a list of URLs too, all data will be gathered and added to the same challenge.
source_url: "https://gist.githubusercontent.com/anonymous/a4d96f67274524d58127/raw/4fc1a8cba29897e4c0d407e1a5269020607be896/overpass.geojson"
# source_file: ....

# source geojson property key to use as your task identifier (optional, will use random UUID if not given)
# identifier_property = ...

# Challenge metadata, see https://gist.github.com/mvexel/b5ad1cb0c91ac245ea3f for background
slug: cork_multilingualnames
title: Places without Gaelic names in Cork
instruction: See task
help: "Many `place` nodes in Ireland have only a `name` but not the corresponding `name:ga` representing the Gaelic name. Please help complete the multilingual map of Ireland by adding these names if you know them."

# task level instruction, can include {} as placeholders to be expanded by an equal number of properties from the GeoJSON file
task_instruction:
  text: "The is place has a `name` tag **{}** but no `name:ga` tag for the Gaelic name. If you know it, please add it. Or perhaps [Google knows](https://www.google.ie/?q={}+gaelic)?"
  properties:
    - name
    - name
```

The first section provides the server API endpoint and API credentials. You can get those for maproulette.org by getting in touch with me.

The next part is the link to the GeoJSON source file. This can be a single URL or a list. Alternatively you can provide a local file here as well.

Lastly, the challenge metadata. See the [MapRoulette tutorial](https://gist.github.com/mvexel/b5ad1cb0c91ac245ea3f) for more details about these important fields. The most tricky part here is perhaps the instruction. I am using an instruction unique to each task, and I want to use the content of the `name` tag in the instruction text. For that I use `{}` as placeholders in the instruction string, and the keys of the GeoJSON properties to use to expand these placeholders.
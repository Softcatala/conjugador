# Description

Conjugador is a web application that allows to search and display verbs forms building the
content from the spelling dictionary.

# How it works

1. extract.py reads diccionary file and extracts the verbs in JSON format (into data/jsons)
2. index_creation.py reads the jsons and creates a Whoosh index (into data/indexdir)
3. Flash application at web/ serves the content

#  Git clone

To clone the repository and its submodules use:

``git clone --recurse-submodules git@github.com:Softcatala/conjugador.git``

#  Docker

To create Docker image, from the <em>root</em> directory type:

``docker build . -t conjugador -f docker/dockerfile``

Simple execution of the Docker image:

``docker run -p 8000:8000 -i -t conjugador``

Test from the browser:
* Search: http://localhost:8000/search/cantar
* Index: http://localhost:8000/index/a
* Autocomplete: http://localhost:8000/autocomplete/cantari

# License

## Software

GNU Lesser General Public License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

## Data

Same license that source projects.

# Maintenance

## Update dictionary

Run:

``git submodule update --remote``

## Update terms' definitions

Download latest version from ``https://dumps.wikimedia.org/cawiktionary/latest/cawiktionary-latest-pages-meta-current.xml.bz2``
into  the ``/definitions`` subdirectory.

# Contact

Contact Jordi Mas <jmas@softcatala.org>


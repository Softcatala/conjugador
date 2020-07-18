
# How it works

1. extract.py reads diccionari file and extracts the verbs in JSON format (into data/jsons)
2. index_creation.py reads the jsons and creates a Whoosh index (into data/indexdir)
3. Flash application at web/ serves the content

#  Docker

To create Docker image, from the <em>docker</em> subdirectory type:

``docker build -t conjugador ../ -f dockerfile``

Simple execution of the Docker image:

``docker run -p 8000:8000 -i -t conjugador``

Test from the browser:
* Search: http://localhost:8000/search/cantar
* Index: http://localhost:8000/index/a
* Autocomplete: http://localhost:8000/autocomplete/cantari

# License

GNU Lesser General Public License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

# Contact

Contact Jordi Mas <jmas@softcatala.org>

Softcatala.

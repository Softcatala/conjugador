
# How it works

1. extract.py reads diccionari file and extracts the verbs in JSON format (into data/jsons)
2. index_creation.py reads the jsons and creates a Whoosh index (into data/indexdir)
3. Flash application at web/ serves the content

#  Docker

Create Docker image:

``docker build -t conjugador . -f dockerfile``

Simple execution of the Docker image:

``docker run -p 8000:8000 -i -t conjugador``

Test from the browser:
* Search: http://localhost:8000/search/cantar
* Index: http://localhost:8000/index/a


# Contact

Contact Jordi Mas <jmas@softcatala.org>


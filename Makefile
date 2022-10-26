docker-build:
	docker build . -t conjugador -f docker/dockerfile

docker-run:
	docker run -p 8000:8000 -i -t conjugador

generate-data:
	bzip2 -cdk definitions/cawiktionary-latest-pages-meta-current.xml.bz2 > definitions/cawiktionary-latest-pages-meta-current.xml
	./extractor/extract.py -i
	./definitions/extract-to-json.py
	./extractor/extract.py
	./indexer/index_creation.py

test:
	- cd extractor && python -m nose2
	- cd definitions && python -m nose2

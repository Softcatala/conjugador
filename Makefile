docker-build:
	docker build . -t conjugador -f docker/dockerfile

docker-run:
	docker run -p 8000:8000 -i -t conjugador

generate-data:
	./extractor/extract.py -i
	./definitions/extract-to-json.py
	./extractor/extract.py
	./indexer/index_creation.py

test:
	- cd extractor && python -m nose2
	- cd definitions && python -m nose2

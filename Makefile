.PHONY: docker-build docker-run generate-data update-data test

docker-build:
	docker build . -t conjugador -f docker/dockerfile;

docker-run:
	docker run -p 8000:8000 -i -t conjugador;

generate-data:
	bzip2 -cdk definitions/cawiktionary-latest-pages-meta-current.xml.bz2 > definitions/cawiktionary-latest-pages-meta-current.xml
	python extractor/extract.py -i
	python definitions/extract-to-json.py
	python extractor/extract.py
	python indexer/index_creation.py

update-data:
	# Extract current version
	make generate-data
	cp data/infinitives.txt data/infinitives.old
	cp data/definitions.txt data/definitions.old

	# Update dataset
	echo Update dictionary
	git submodule update --remote
	echo Update definitions
	cd definitions && wget --backups=1 https://dumps.wikimedia.org/cawiktionary/latest/cawiktionary-latest-pages-meta-current.xml.bz2

	# Extract new version
	python extractor/extract.py -i
	python definitions/extract-to-json.py

	# Generate diffs
	diff -u data/infinitives.old data/infinitives.txt > data/infinitives.diff || true
	diff -u data/definitions.old data/definitions.txt > data/definitions.diff || true

	# Show stats
	grep -e '^\+' -e '^\-' data/infinitives.diff | grep -vE '^\+\+\+|^\-\-\-' | wc -l | xargs echo "Total infinitive changes:"
	grep -e '^\+' -e '^\-' data/definitions.diff | grep -vE '^\+\+\+|^\-\-\-' | wc -l | xargs echo "Total definitions changes:"

test:
	cd extractor && python -m nose2
	cd definitions && python -m nose2

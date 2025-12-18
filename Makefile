.PHONY: docker-build docker-run generate-data update-data test generate-data-without-indexation

docker-build:
	docker compose build

docker-run:
	docker compose up

generate-data:
	set -e; \
	bzip2 -cdk definitions/cawiktionary-latest-pages-meta-current.xml.bz2 > definitions/cawiktionary-latest-pages-meta-current.xml; \
	uv run -m extractor.extract -i; \
	uv run -m definitions.extract-to-json; \
	uv run -m extractor.extract; \
	uv run -m indexer.index_creation

generate-data-without-indexation:
	set -e; \
	bzip2 -cdk definitions/cawiktionary-latest-pages-meta-current.xml.bz2 > definitions/cawiktionary-latest-pages-meta-current.xml; \
	uv run -m extractor.extract -i; \
	uv run -m definitions.extract-to-json; \
	uv run -m extractor.extract; \

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
	uv run extractor/extract.py -i
	uv run definitions/extract-to-json.py

	# Generate diffs
	diff -u data/infinitives.old data/infinitives.txt > data/infinitives.diff || true
	diff -u data/definitions.old data/definitions.txt > data/definitions.diff || true

	# Show stats
	grep -e '^\+' -e '^\-' data/infinitives.diff | grep -vE '^\+\+\+|^\-\-\-' | wc -l | xargs echo "Total infinitive changes:"
	grep -e '^\+' -e '^\-' data/definitions.diff | grep -vE '^\+\+\+|^\-\-\-' | wc -l | xargs echo "Total definitions changes:"

test:
	cd extractor && uv run -m nose2
	cd definitions && uv run -m nose2

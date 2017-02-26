.PHONY: init test install extract_tar_archives check clean

init:
	@pip install -r requirements.txt

install:
	@./setup.py install

download_datasets: install
	@download_datasets.py

extract_tar_archives: download_datasets
	@extract_data_samples.py

build:
	@./setup.py build

check:
	@flake8 --show-source --statistics design tests

test: extract_tar_archives
	@./setup.py test

clean:
	@rm -rf dist/
	@rm -rf build/
	@rm -rf design.egg-info/
	@find . -name '*.pyc' -exec rm {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@rm -rf samples/
	@rm -rf data/

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

test:
	@./setup.py test

clean:
	@find . -name '*.pyc' -exec rm {} \;
	@rm -rf samples/

.PHONY: init test install extract_tar_archives check clean

init:
	@pip install -r requirements.txt

install:
	@./setup.py install

extract_tar_archives: install
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

.PHONY: init test install

init:
	@pip install -r requirements.txt

install:
	@./setup.py install

build:
	@./setup.py build

check:
	@flake8 --show-source --statistics design tests

test:
	@./setup.py test

clean:
	@find . -name '*.pyc' -exec rm {} \;
	@rm -rf samples/

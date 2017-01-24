.PHONY: init test install

init:
	@pip install -r requirements.txt

install:
	@./setup.py install

build:
	@./setup.py build

test:
	@python -m unittest discover

clean:
	@find . -name '*.pyc' -exec rm {} \;

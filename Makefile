SHELL := /bin/bash

build-ui:
	pyuic5 ./spytrack/gui/ui/main.ui > ./spytrack/gui/ui/main.py
	pyuic5 ./spytrack/gui/ui/project.ui > ./spytrack/gui/ui/project.py
	pyuic5 ./spytrack/gui/ui/rule.ui > ./spytrack/gui/ui/rule.py
	pyuic5 ./spytrack/gui/ui/main_page.ui > ./spytrack/gui/ui/main_page.py
	pyuic5 ./spytrack/gui/ui/settings.ui > ./spytrack/gui/ui/settings.py

test:
	flake8 spytrack/ --exclude spytrack/gui/ui --max-complexity 10
	flake8 tests/
	python -m unittest discover
	mypy --config-file=mypy.ini --strict spytrack/__main__.py
	mypy --config-file=mypy.ini --strict tests

run:
	source venv/bin/activate && python spytrack

build-all:
	rm -rf ./dist
	make build-ui
	./build/aw-webui.sh
	pyinstaller --clean --workpath ./.build build/spytrack.spec
	python setup.py sdist
	python setup.py bdist_rpm --bdist-base=.build
	python setup.py clean
	rm -rf ./Spytrack.egg-info
	zip -9 -r ./dist/spytrack.zip dist/spytrack

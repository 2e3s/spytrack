build-ui:
	pyuic5 ./spytrack/gui/ui/main.ui > ./spytrack/gui/ui/main.py
	pyuic5 ./spytrack/gui/ui/project.ui > ./spytrack/gui/ui/project.py
	pyuic5 ./spytrack/gui/ui/rule.ui > ./spytrack/gui/ui/rule.py
	pyuic5 ./spytrack/gui/ui/main_page.ui > ./spytrack/gui/ui/main_page.py

test:
	venv/bin/mypy --config-file=mypy.ini --strict spytrack/__main__.py
	venv/bin/mypy --config-file=mypy.ini --strict tests
	python -m unittest discover
	flake8 spytrack/ --exclude spytrack/gui/ui
	flake8 tests/

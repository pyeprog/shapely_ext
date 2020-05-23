rm -rf dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/* --repository-url https://upload.pypi.org/legacy/

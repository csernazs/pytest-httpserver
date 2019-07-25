
Sounds like a python script for me, but here's the manual checklist:

- [ ] check the latest commits on master
- [ ] every major change reflected in the release notes
- [ ] check the latest doc build at rtd.org
- [ ] check that master is green at travis
- [ ] version bump (sphinx/conf.py, setup.py)
- [ ] tag the HEAD
- [ ] generate documentation, check version at release notes
- [ ] build the dist: setup.py sdist bdist_wheel
- [ ] install package in a local venv
- [ ] push to github (version bump, tags)
- [ ] upload dist/* to pypi

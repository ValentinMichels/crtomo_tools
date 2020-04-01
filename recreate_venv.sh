#!/bin/bash
# delete and recreate the virtualenv "crtomo"
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

rmvirtualenv crtomo
mkvirtualenv --python /usr/bin/python3 crtomo
pip install -r requirements.txt
pip install -r requirements_doc.txt
pip install -r requirements_dev.txt
pip install git+https://github.com/geophysics-ubonn/reda
pip install .

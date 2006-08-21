#! /bin/sh

./clean.sh
cp VERSION default
python pack.py
python setup.py sdist --formats=gztar,zip
python setup.py bdist_rpm
python setup.py bdist_wininst --bitmap biz_small2.bmp --install-script biz-postinstall.py

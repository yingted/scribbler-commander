shell: python
	./python -ic 'import myro;from myro import *'
python: root/lib/python2.4 myro pyserial-2.2 root/lib/python2.4/site-packages/PIL.pth root
	[ -h root/lib/python2.4/site-packages/myro ] || ln -s ../../../../myro root/lib/python2.4/site-packages
	[ -h root/lib/python2.4/site-packages/serial ] || ln -s ../../../../pyserial-2.2/serial root/lib/python2.4/site-packages
	> python echo \#!/bin/sh
	>> python echo PATH="$(PWD)/root/bin:$$PATH" PYTHONPATH="$(PWD)/root/lib/python2.4":root/lib/python2.4/site-packages:/usr/lib64/python2.7/site-packages:/usr/lib/python2.7/site-packages exec python '"$$@"'
	chmod +x python
root/lib/python2.4: Python-2.4.4
	cd Python-2.4.4 && make && ./python setup.py build && make install
Python-2.4.4:
	curl 'http://www.python.org/ftp/python/2.4.4/Python-2.4.4.tar.bz2' | tar xj
	cd Python-2.4.4 && ./configure -C --prefix=$(PWD)/root
myro: myro-2.9.1.zip
	unzip myro-2.9.1.zip
pyserial-2.2: pyserial-2.2.zip
	unzip pyserial-2.2.zip
myro-2.9.1.zip:
	wget http://myro.roboteducation.org/download/myro-2.9.1.zip
pyserial-2.2.zip:
	wget -O pyserial-2.2.zip 'http://downloads.sourceforge.net/project/pyserial/pyserial/2.2/pyserial-2.2.zip?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fpyserial%2Ffiles%2Fpyserial%2F2.2%2F'
Imaging-1.1.7:
	wget -O- http://effbot.org/downloads/Imaging-1.1.7.tar.gz | tar xz
root/lib/python2.4/site-packages/PIL.pth: Imaging-1.1.7
	cd Imaging-1.1.7 && $(PYTHON) setup.py install
root:
	mkdir root
.PHONY: shell python

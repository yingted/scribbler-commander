run: lib/python kill
	lib/python interface.py
kill:
	ps ax | fgrep " python $(PWD)/lib/root/lib/python2.4/site-packages/myro/simulator.py" | grep '^ *[0-9][0-9]*  *[^ ][^ ]*  *[^ ][^ ]*  *[0-9][0-9]*:[0-9][0-9]* python /' | awk '{print $$1}' | xargs kill 2>/dev/null || :
lib/python: 
	make -C lib python
.PHONY: run kill

PYTHON=lib/python
run: lib/python static/js/jquery-1.10.2.min.js kill
	trap 'make kill' EXIT; lib/python interface.py
demo: 
	$(PYTHON) model.py
kill:
	ps ax | fgrep " python $(PWD)/lib/root/lib/python2.4/site-packages/myro/simulator.py" | grep '^ *[0-9][0-9]*  *[^ ][^ ]*  *[^ ][^ ]*  *[0-9][0-9]*:[0-9][0-9]* python /' | awk '{print $$1}' | xargs kill 2>/dev/null || :
lib/python: 
	$(MAKE) -C lib python
data.pickle:
	$(PYTHON) record-data.py data.pickle
prior.pickle: data.pickle make-prior.py
	./make-prior.py data.pickle prior.pickle
.PHONY: run kill demo
.PRECIOUS: data.pickle

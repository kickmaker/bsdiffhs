bsdiffhs/core.so: bsdiffhs/core.c
	python setup.py build_ext --inplace


test: bsdiffhs/core.so
	python -c "import bsdiffhs; bsdiffhs.test()"


clean:
	rm -rf build dist
	rm -f bsdiffhs/*.o bsdiffhs/*.so bsdiffhs/*.pyc
	rm -rf bsdiffhs/__pycache__ *.egg-info

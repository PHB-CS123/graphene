cd lib
pip2 install -r pip-reqs.txt
tar -xzvf antlr4-python2-runtime.tgz
cd antlr4-python2
python2 setup.py install
cd ..
rm -rf antlr4-python2
cd ../

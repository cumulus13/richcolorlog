rmdir /s /q  dist
rmdir /s /q  build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"
rmdir /s /q  __pycache__
python setup.py sdist bdist_wheel
twine upload dist\* -r pypihub
twine upload dist\* 

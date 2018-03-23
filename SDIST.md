# Packaging - 

## Requirements

    pip install twine
    
Check that you have a .pypirc file:

    vim ~/.pypirc

```
[distutils]
index-servers =
    pypi
    test

[pypi]
repository:https://upload.pypi.org/legacy/
username:yourname
password:yourpassword

[test]
repository:https://test.pypi.org/legacy/
username:yourname
password:yourpassword
```

## Publish

Run the following

    python setup.py sdist           # to build the package to ./dist
    
    twine upload -r test dist/plugit-0.3.XX.tar.gz
                                    # to upload the package to test
                                    # https://testpypi.python.org/pypi/plugit/
                                     
    twine upload dist/PACKAGENAME-VERSION.tar.gz
                                    # upload for production
                                    # https://pypi.python.org/pypi/plugit/
                                    
                                    
## More docs

* <https://tom-christie.github.io/articles/pypi/>
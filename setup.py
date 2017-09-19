from setuptools import setup
# from distutils.core import setup


setup(
    name="plugit",
    packages=["plugit", "plugit_proxy"],
    version="0.3.9",
    license="BSD",
    description="PlugIt is a framework enhancing the portability and integration of web services requiring a user interface.",
    author="EBU Technology & Innovation",
    author_email="barroco@ebu.ch",
    url="http://github.com/ebu/PlugIt",
    download_url="",
    keywords=["frontend"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    long_description=open("README.md").read() + "\n\n",
    install_requires=[
        'requests',
        'flask',
        'django-ipware',
        'django<1.9',
        'python-dateutil',
        'poster',
        'pycrypto',
    ],
    include_package_data=True,
)

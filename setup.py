import bigpipe_response
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

with open('requirements.txt') as f:
   requirements = f.read().splitlines()

setuptools.setup(
   name='bigpipe_response',
   version=bigpipe_response.__version__,
   description='Bigpipe, Pipelining web pages for high performance for django',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/shacoshe/bigpipe-response",
   author='Shay Tessler',
   author_email='shay.te@gmail.com ',
   packages=requirements,
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   python_requires='>=3.7'
)
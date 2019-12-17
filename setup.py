import bigpipe_response
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setuptools.setup(
   name='bigpipe_response',
   version=bigpipe_response.__version__,
   description='Bigpipe, Pipelining web pages for high performance for django',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/shacoshe/bigpipe-response",
   author='Shay Tessler',
   author_email='shay.te@gmail.com',
   packages=setuptools.find_packages(),
   license="BSD 3-Clause License",
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: BSD License",
      "Operating System :: OS Independent",
   ],
   python_requires='>=3.7'
)
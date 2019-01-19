import setuptools

setuptools.setup(
    name='spacewidget',
    version='0.1.0',
    author='foosinn',
    author_email='foosinn@f2o.io',
    url='https://github.com/foosinn/spacewidget',
    packages=setuptools.find_packages(),
    package_data={
        'spacewidget': ['index.html'],
    }
)


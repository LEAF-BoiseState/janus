class VersionError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


try:
    from setuptools import setup, find_packages
except ImportError:
    print("Must have setuptools installed to run setup.py. Please install and try again.")
    raise


def readme():
    with open('README.md') as f:
        return f.read()


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().split()

setup(
    name='abm',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/LEAF-BoiseState/IM3-BoiseState.git',
    license='BSD 2-Clause',
    author='Kendra Kaiser; Lejo Flores',
    author_email='kendrakaiser@boisestate.edu; lejoflores@boisestate.edu',
    description='An agent based model to model land use',
    long_description=readme(),
    install_requires=get_requirements(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4'
)

import subprocess
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    raise("Must have `setuptools` installed to run setup.py. Please install and try again.")


def readme():
    with open('README.md') as f:
        return f.read()


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().split()


# get gdal version on machine
gdal_sys_call = subprocess.Popen('gdal-config --version', stdout=subprocess.PIPE, shell=True)
gdal_system_version = gdal_sys_call.stdout.read().decode('UTF-8').strip()

if gdal_system_version != '':

    # install gdal version matching gdal libs on machine
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gdal=={}'.format(gdal_system_version)])

else:

    raise ImportError('GDAL version >= 2.1.0 required to run Janus.  Please install GDAL with Python bindings and retry.')

setup(
    name='janus',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/LEAF-BoiseState/janus.git',
    license='BSD 2-Clause',
    author='Kendra Kaiser; Lejo Flores',
    author_email='kendrakaiser@boisestate.edu; lejoflores@boisestate.edu',
    description='An agent based model to model land use',
    long_description=readme(),
    install_requires=get_requirements(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4'
)

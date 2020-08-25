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

    install_list = []
    depends_list = []

    with open('requirements.txt') as f:

        for i in f.readlines():

            pkg = i.strip().split('|')
            pkg_len = len(pkg)

            if pkg_len == 1:
                install_list.append(pkg[0])

            elif pkg_len == 2:
                install_list.append(pkg[0])
                depends_list.append(pkg[1])

            else:
                raise IndexError("Too many arguments entered in the 'requirements.txt' file for a single line:  {}".format(i))

        return install_list, depends_list

try:
    import gdal

except ImportError:

    # get gdal version on machine
    gdal_sys_call = subprocess.Popen('gdal-config --version', stdout=subprocess.PIPE, shell=True)
    gdal_system_version = gdal_sys_call.stdout.read().decode('UTF-8').strip()

    gdal_split = gdal_system_version.split('.')
    gdal_major = int(gdal_split[0])
    gdal_minor = int(gdal_split[1])

    if (gdal_system_version != '') and (gdal_major >= 2) and (gdal_minor >= 1):

        # install gdal version matching gdal libs on machine
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gdal=={}'.format(gdal_system_version)])

    else:

        raise ImportError('GDAL version >= 2.1.0 required to run Janus.  Please install GDAL with Python bindings and retry.')

# read in requirements
install_list, depends_list = get_requirements()

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
    install_requires=install_list,
    dependency_links=depends_list,
    include_package_data=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4'
)

from setuptools import setup

setup(name='spectrofluorometer',
      version='0.1',
      description='Web based control software for our custom built spectrofluoremeter ',
      url='http://github.com/jmosbacher/straxrpc',
      author='Yossi Mosbacher',
      author_email='joe.mosbacher@gmail.com',
      license='MIT',
      packages=['spectrofluorometer'],
      install_requires=[
          'flask',
          'pyserial',
          'redis',
          'flask_restful',
          'automodinit',
        #   ,
      ],
      
      zip_safe=False)
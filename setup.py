from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='StableSwapPy',
      version='0.0.8',
      description='StableSwap Analytics with Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/defipy-devs/stableswappy',
      author = "icmoore",
      author_email = "defipy.devs@gmail.com",
      license='MIT',
      package_dir = {"stableswappy": "python/prod"},
      packages=[
          'stableswappy',
          'stableswappy.cst.exchg',
          'stableswappy.cst.factory',
          'stableswappy.erc',
          'stableswappy.vault',
          'stableswappy.quote',
          'stableswappy.utils.interfaces',
          'stableswappy.utils.data'           
      ],
      install_requires=[
        'gmpy2 >= 2.0.8'
      ],        
      zip_safe=False)

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='StableSwapPy',
      version='1.0.2',
      description='StableSwap Analytics with Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/defipy-devs/stableswappy',
      author = "icmoore",
      author_email = "defipy.devs@gmail.com",
      license="Apache-2.0",
      classifiers=[
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ],
      package_dir = {"stableswappy": "python/prod"},
      packages=[
          'stableswappy',
          'stableswappy.cst.exchg',
          'stableswappy.cst.factory',
          'stableswappy.erc',
          'stableswappy.vault',
          'stableswappy.quote',
          'stableswappy.utils.interfaces',
          'stableswappy.utils.data',
          'stableswappy.process.liquidity',
          'stableswappy.process.swap',
          'stableswappy.process.join'
      ], 
      install_requires=[
          'uniswappy >= 1.7.3'
      ],
      zip_safe=False)

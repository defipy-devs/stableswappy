from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='StableSwapPy',
      version='0.0.4',
      description='StableSwap for Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/icmoore/stableswappy',
      author = "icmoore",
      author_email = "utiliwire@gmail.com",
      license='MIT',
      package_dir = {"stableswappy": "python/prod"},
      packages=[
          'stableswappy',
          'stableswappy.cst.exchg',
          'stableswappy.cst.factory',
          'stableswappy.erc',
          'stableswappy.vault',
          'stableswappy.quote'
      ],
      zip_safe=False)

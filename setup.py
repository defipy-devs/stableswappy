from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='StableSwapPy',
      version='0.0.1',
      description='StableSwap for Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/icmoore/stableswappy',
      author = "icmoore",
      author_email = "imoore@syscoin.org",
      license='MIT',
      package_dir = {"stableswappy": "python/prod"},
      packages=[
          'stableswappy.cwpt.exchg',
          'stableswappy.cwpt.factory',
          'stableswappy.erc',
          'stableswappy.group',
          'python.prod.cwpt.exchg',
          'python.prod.cwpt.factory',
          'python.prod.erc',
          'python.prod.group'
      ],
      zip_safe=False)

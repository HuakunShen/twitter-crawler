import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twitter-crawler",
    version="0.0.1",
    author="Huakun Shen",
    author_email="huakun.shen@huakunshen.com",
    description="Scrape Information from Twitter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HuakunShen/twitter-crawler",
    project_urls={
        "Bug Tracker": "https://github.com/HuakunShen/twitter-crawler/issues",
        "Documentation": "https://huakunshen.github.io/twitter-crawler/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pathlib2==2.3.5',
        'selenium-wire==4.6.0'
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    package_data={}
)

# python -m build
# python -m twine upload dist/* --verbose --repository testpypi

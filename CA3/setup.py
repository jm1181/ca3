import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="alarm-pkg-jm1181",
    version="0.0.1",
    author="Jemima Morris",
    author_email="jm1181@exeter.ac.uk",
    description="Smart Alarm Clock",
    long_description="This is a program that allows you to get the latest information "
                     "regarding COVID-19, the news and the latest weather. It also allows you"
                     "to create alarms that read out the news, weather or COVID updates "
                     "if that is what you would like to do.",
    long_description_content_type="text/markdown",
    url="https://github.com/jm1181/ca3.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

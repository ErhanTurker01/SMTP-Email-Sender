from setuptools import setup, find_packages

setup(
    name="smtp-email-sender",
    version="1.0.4",
    description="A simple email sender package with SMTP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Erhan Turker",
    author_email="erantrk0122@gmail.com",
    url="https://github.com/ErhanTurker01/SMTP-Email-Sender",
    packages=find_packages(include=["smtp_email_sender"]),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

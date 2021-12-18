import pkg_resources
import setuptools


with open("./requirements.txt") as f:
    install_requires = [str(r) for r in pkg_resources.parse_requirements(f)]

setuptools.setup(
    name="cfi_midot",
    version="1.0.0",
    author="CFIMIDOT",
    author_email="version.ilan@gmail.com",
    description="Tool to analyse NGOs in Israel",
    packages=["cfi_midot"],
    install_requires=[
        *install_requires,
    ],
)

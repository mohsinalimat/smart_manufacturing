from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="smart_manufacturing",
    version="1.0.0",
    description="Production-ready Smart Manufacturing Suite for ERPNext/Frappe",
    author="Smart Manufacturing",
    author_email="info@smartmanufacturing.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)

import subprocess
import importlib.util
import sys
import os
import site
from importlib import reload

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package],stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

def check_package(package_name):
    if package_name in sys.modules:
        print(f"{package_name!r} already in sys.modules")
    elif (importlib.util.find_spec(package_name)) is not None:
        # If you choose to perform the actual import ...
        install(package_name)
        print(f"{package_name!r} has been imported")
    else:
        print(f"can't find the {package_name!r} module")

def install_packages(packages_list):
    print("Installing packages...")
    for package in packages_list:
        install(package)
    reload(site)
    print("Packages installed.")
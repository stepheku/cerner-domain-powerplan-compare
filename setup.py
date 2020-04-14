import setuptools

def requirements_file_contents():
    with open('requirements.txt', 'r') as requirements_file:
        data = [pkg.strip() for pkg in requirements_file.readlines()]
    return data

required_packages = requirements_file_contents()

setuptools.setup(
    name='PowerPlan domain compare',
    version='1.0.0',
    description='Compares PowerPlans between different domains',
    author='turbopancake',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires = required_packages
)
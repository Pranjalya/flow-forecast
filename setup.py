from setuptools import setup
import os

library_folder = os.path.dirname(os.path.realpath(__file__))
requirementPath = f'{library_folder}/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

dev_requirements = [
    'autopep8',
    'flake8'
]

setup(
    name='flood_forecast',
    version='0.03dev',
    packages=[
        'flood_forecast',
        'flood_forecast.transformer_xl',
        'flood_forecast.preprocessing',
        'flood_forecast.da_rnn',
        "flood_forecast.basic",
        "flood_forecast.custom"],
    license='Public',
    long_description='A public package for forecasting river flows and flash flood severity',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requirements})

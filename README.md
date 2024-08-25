# XTrack

Welcome to the XTrack's repository. Here you will find the framework's code and the installation instructions. 

## Introduction

## Installation

In order to install the repository, we recommend following the next steps:

1. **Requirements**: in order to install the framework, the following technologies must be previously installed and accesible:
  1. **Python installation**: first, the user must install Python >=3.11, which is the Python version on top of which XTrack was developed.
  2. **MySQL installation**: a MySQL instance with the data model (see `assets` folder) installed in a schema must exist before executing the framework, as it operates on top of the MySQL database.
  3. **MongoDB installation**: a MongoDB instance is also required for data ingestion purposes from X. These data downloads can potentially be huge, thus a database with potential for distributed storage was considered for storing the campaign datasets from X.
4. **Repository download**: once Python is installed, it is required to download a version of the XTrack framework. We recommend using the latest release available at the repository, although the user could use any particular build of its preference.
5. **Dependencies**: next, the user must navigate to the root folder of the repository (the folder containing the `requirements.txt` and the `setup.py` files. Then, the user must install the framework and its dependencies using pip, just as follows: `pip install .`
6. **Launching the framework**: to launch the framework, the following steps can be performed:
  1. Navigate to `xtrack_web`, which is the folder containing the web platform related to the framework.
  2. Launch flask by executing the following command: `flask --app app.py --debug run`


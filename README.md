# XTrack

Welcome to the XTrack's repository. Here you will find the framework's code and the installation instructions. 

## Introduction

 ## Authors

This framework has been developed by:

- Pau Muñoz ([@paumnz](https://github.com/paumnz) in Github). 
- Raúl Barba ([@PolarNebula](https://github.com/PolarNebula) in Github). If you need to contact this author you can use the following e-mail: barbarojasraul@gmail.com

## Installation

In order to install the repository, we recommend following the next steps:

1. **Requirements**: in order to install the framework, the following technologies must be previously installed and accesible:
  1. **Python installation**: first, the user must install Python >=3.11, which is the Python version on top of which XTrack was developed.
  2. **MySQL installation**: a MySQL instance with the data model (see `assets` folder) installed in a schema must exist before executing the framework, as it operates on top of the MySQL database.
  3. **MongoDB installation**: a MongoDB instance is also required for data ingestion purposes from X. These data downloads can potentially be huge, thus a database with potential for distributed storage was considered for storing the campaign datasets from X.
4. **Repository download**: once Python is installed, it is required to download a version of the XTrack framework. We recommend using the latest release available at the repository, although the user could use any particular build of its preference.
5. **Dependencies**: next, the user must navigate to the root folder of the repository (the folder containing the `requirements.txt` and the `setup.py` files. Then, the user must install the framework and its dependencies using pip, just as follows: `pip install .`.
    - NOTE: it is recommended to create a virtual environment before installing the framework, so that the installation of the framework lives in its own environment without conflicting with any other project of the machine where it will be working. 
7. **Configuring the framework**: the  `config.ini` file contains the configurations that the framework will use when running. It is required to configure the MongoDB and MySQL endpoints and the rest of configurations of the framework (e.g. the Bearer token of X's API, the Rapid API key of the Botometer X service, the location of the LIWC 2015 dictionary, among other configurations).
8. **Launching the framework**: to launch the framework, the following steps can be performed:
  1. Navigate to `xtrack_web`, which is the folder containing the web platform related to the framework.
  2. Launch flask by executing the following command: `flask --app app.py --debug run`

## Repository structure

The repository has the following structure:

- 📁 `assets`: this folder contains assets that are employed by the framework. The data model of the MySQL database is included in this folder.
- 📁 `xtack_engine`: this folder contains the Python engine that fuels the framework. It is capable of performing all the operations handled by the framework, from data ingestion to data exploitation.
  - 📁 `_utils`: this folder is a private Python package with utilities employed by other modules and packages of the framework.
  - 📁 `bot_analysis`: this package provides the engine with the capability to check for the existence of bots within the users downloaded for a campaign.
  - 📁 `database_connection`: this package provides (MySQL) database connection capabilities, which is further employed by all the other analysis packages.
  - 📁 `errors`: this package provides the implementation of custom exceptions that occur during the usage of the framework.
  - 📁 `media_analysis`: this package provides the capability to analyze media outlets in terms of shared URL domains from media outlets during the studied campaign, and also in terms of shared headlines during the conversation in the network.
  - 📁 `motto_analysis`: this package provides the capability to analyze mottos (hashtags) employed in the campaign.
  - 📁 `network_analysis`: this package provides the engine with the capability to analyze networks and network metrics during a given campaign. Currently, the following network metrics are supported and can be used in the framework (make sure to write them just as they appear in the list!):
    - 🧮 node_number
    - 🧮 edge_number
    - 🧮 in-degree
    - 🧮 out-degree
    - 🧮 efficiency
    - 🧮 density
    - 🧮 modularity
    - 🧮 clustering_coefficient
    - 🧮 diameter
    - 🧮 eigenvector_centrality
  - 📁 `sentiment_analysis`: this package provides the engine with the capability to analyze the speech, in terms of sentiment, emotion and general psychological properties of the speech through DL models and the LIWC framework.
  - 📁 `topic_analysis`: this package provides the capability to analyze topics using gensim models for topic discovery.
  - 📁 `tweet_analysis`: this package provides the capability to analyze tweets in a variety of manners, ranging from hourly activity to tweet impact and redundancy (duplication) in the conversation.
  - 📁 `twitter_data_ingestor`: this package provides the capability to download data related to a campaign from X.
  - 📁 `user_analysis`: this package provides the capability to analyze users.
  - 📁 `visualization`: this package provides general visualization utilities employed by the different analysis packages.
  - 📄 `_analyzer.py`: this module provides the template of what an `Analyzer` looks like in XTrack. This behaviour is extended in each of the analysis supported by the framework (e.g., `BotAnalyzer` extends the class and brings the required behaviour to analyze the existence of bots in a given campaign).
- 📁 `xtrack_web`:
  - 📁 `static`: this folder contains static resources that are employed by the webpages that conform the web platform of the framework. These resources include CSS files, JS scripts and images.
  - 📁 `templates`: this folder contains the HTML webpages that are served by Flask when the user accesses the front-end of the framework.
  - 📄 `app.py`: a Python module containing the implementation of a REST API in Flask. This API is used by the front-end to perform data download or exploitation, and it is also responsible for serving the front-end's resources (from HTML documents to JS scripts, cascading stylesheets, images and other required resources).
- ⚙️ `config.ini`: the configuration file of the framework. It includes MongoDB and MySQL connectivity configurations (host, port, etc.), as well as other configurations of the framework. It is recommended to view this file in detail and perform any necessary adjustments before launching the framework.
- 📄 `requirements.txt`: the dependences of the framework that are installed with it.
- 📄 `setup.py`: the module that installs the framework.


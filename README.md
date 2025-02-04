# XTrack: A cutting-edge framework for Social Network Analysis

Welcome to the XTrack's repository. Here you will find the framework's code and the installation instructions. 

![XTrack's icon](assets/framework_images/xtrack_logo_transparent.png)

## Introduction

XTrack is a framework that leverages Machine Learning and Social Network Analysis techniques to perform complex and valuable analyses on X's data. The tool can be used to download data from a given campaign (e.g., Covid-19 pandemic). Downloaded data can then be analyzed in-depth by XTrack's built-in engine to generate valuable insights, allowing the optimization of user strategies in social networks. More specifically, our tool performs analysis on the following elements:

- ✅ **User analysis**: our framework is capable of identifying the most influential users in the given campaign, detecting potential bot accounts and identifying account creation trends over time.
- ✅ **Conversation motto analysis**: the framework can also identify the most employed mottos in the conversation around a given campaign, which can help understand the comments that dominate the conversation.
- ✅ **Media outlet analysis**: the framework identifies the most employed media outlets in a given campaign (i.e., the most important outlets for a given campaign), as well as the most extended headlines in the conversation.
- ✅ **Post analysis**: the framework carries out a complex and in-depth analysis of the posted information to understand trends in publications' creation times, the most employed words and languages, the publications with highest impact and the most repeated ones during the given campaign, and even a treemap showing the most extended conversation topics during such campaign.
- ✅ **Network analysis**: the framework also offers capabilities to generarate networks showing relevant connections between users. The generated networks include the activity of the users, the sentiment they employ in their publications, the connections between the users, so as to generate a reliable map of the campaign conversation in the social network. Furthermore, the framework also generates periodic networks to analyze how different network metrics and properties evolve over time, so as to gain intelligence on information dynamics around the campaign.
- ✅ **Speech analysis**: the framework also applies speech analysis, in terms of sentiments and emotions employed in the publications, but also using the psychological properties of the LIWC framework, so as to understand the speech of the users in the campaign.
- ✅ **Topic analysis**: last, the framework applies topic analysis showing which topics are treated during the campaign, the most relevant words per topic, the most impactful topics, and how the different posts in the conversation map to those topics.

Make sure to check [Analyzing a campaign with XTrack](#analyzing-a-campaign-with-xtrack) for further details on how these analyses can be performed using XTrack.

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

## Analyzing a campaign with XTrack

This section offers a user guide to analyzing a campaign's data with our framework. First, the user can access the home page of the framework to choose the analysis task (click):

![XTrack's Home page](/assets/framework_images/home.png)

Once selected, the user will see a form related to the analysis. This form further informs the engine on how the analysis task must be performed, for example, in terms of which language it should be analyzing (for sentiment and emotion detection, for example), or which network metrics the user wants to see (see list of network metrics above).

![XTrack's Social Network Analysis page](/assets/framework_images/analyze.png)

The first time that an analysis is run can take a significant amount of time depending on the volume of data of the campaign. However, there is no need to keep the platform open for the analysis to be completed. As soon as the analysis finishes, the result is cached and will be furthered delivered to the user when querying for it. The next image shows how the tool looks like when a computation is being performed for the given user:

![XTrack's Loading page](/assets/framework_images/analyze_loading.png)

Once the results are obtained, the user will be able to gather relevant information on the given campaign. First, conversation mottos are shown. While all publications are considered by default, the user can choose to see the most negative or the most positive mottos, instead of the most employed mottos, by using selecting the specific sentiment in the listbox:

![XTrack's Motto analysis](/assets/framework_images/analyze_sentiment.png)

The user will also find XTrack's analysis on the user accounts that were active on the campaign, just as can be seen in the following images:

![XTrack's User analysis](/assets/framework_images/analyze_users.png)

Next, the user will also see the analysis performed on the publications of the campaign:

![XTrack's Tweet analysis (part I)](/assets/framework_images/analyze_tweet_1.png)
![XTrack's Tweet analysis (part II)](/assets/framework_images/analyze_tweet_2.png)
![XTrack's Tweet analysis (part III)](/assets/framework_images/analyze_tweet_3.png)
![XTrack's Tweet analysis (part IV)](/assets/framework_images/analyze_tweet_4.png)

The user can also see an in-depth network analysis, with two different conversation graphs, as well the evolution of the selected network metrics over time:

![XTrack's Network analysis (part I)](/assets/framework_images/analyze_network_1.png)
![XTrack's Network analysis (part II)](/assets/framework_images/analyze_network_2.png)
![XTrack's Network analysis (part III)](/assets/framework_images/analyze_network_3.png)

Regarding speech analysis, the user can easily see the most dominant sentiments and emotions during the given campaign:

![XTrack's Speech analysis](/assets/framework_images/analyze_speech.png)

Last, the topic analysis is shown, showing the most impactful topics in the conversation, the most relevant words per topic, as well as the post distribution (faceted by topic) in a 2-dimensional plot of the conversation:

![XTrack's Topic analysis (part I)](/assets/framework_images/analyze_topics_1.png)
![XTrack's Topic analysis (part II)](/assets/framework_images/analyze_topics_2.png)

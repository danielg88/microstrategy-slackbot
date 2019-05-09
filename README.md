MicroStrategy Python Chatbot for Slack
-------------------------------------

This is a Slack chatbot that connects to your MicroStrategy server and answer questions related to one dataset.

You can ask for attributes, metrics and specific attribute elements from the dataset, by default the data is presented as text but you can also ask the bot for a graph. The bot responds to direct messages as well as channels in wich it is invited to and mentioned.

This code was written for a demo and it's not fully finished or tested. Missing functionality includes: automatically refresh data, graphing options and support for more than one dataset/project.

Requirements
------------
1. To run the chatbot you need to have the following libraries: 
    * [slackclient](https://github.com/slackapi/python-slackclient)
    * [matplotlib](https://matplotlib.org/)
    * [pandas](https://pandas.pydata.org/)
    * [requests](https://2.python-requests.org/en/master/)
2. [Create a Slack bot](https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace) and get the Slack Token.
3. Have MicroStrategy Library installed.

Configuration
------------
1. In file **dapi.py** fill the variable SlackToken to the Token you got from Slack.
2. In **dapi.py** Change the name of the bot in the bot_name to whatever you want it to recognize as a mention.
3. Inside Util folder, file **microstrategyfunctions.py**  fill the MicroStrategy variables, URL, user, password, project and report ID.
4. Run **dapi.py**.

**dapifilecleaning.py** is provided to clean all the Bot generated graphs from your machine and from Slack workspace. Running the Script will delete all graphs from the bot conversations

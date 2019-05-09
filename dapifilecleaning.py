import os, slackclient
import glob

# delay in seconds before checking for new events 
SocketDelay= 1
# slackbot environment variables
SlackToken = ''
Slack = slackclient.SlackClient(SlackToken)

try: 
    f = open("images_uploaded.txt", "rt")
    ax = f.readlines()
    for line in ax:
        print (line.strip())
        print(Slack.api_call('files.delete', file = line.strip())['ok'])
    f.close()
    os.remove("images_uploaded.txt")
    filelist = glob.glob('*png')
    for png in filelist:
        try:
            os.remove(png)
        except OSError:
            print ('Error deleting %s' %png)
except OSError:
    print ('error abriendo fichero con imagenes')
import pynder
import os
import sys
import time
import subprocess
import robobrowser
import re
import urllib
import datetime
from geopy.geocoders import Nominatim


#Define the main function

MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; U; en-gb; KFTHWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.16 Safari/535.19"
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"

def FindConfigFile():
    
    ProfilePath = os.path.expanduser("~")
    ConfigPath = os.path.join(ProfilePath + "/" + "TinderScraperConfig.txt")
    #print ConfigPath
    DoesConfigExist = os.path.isfile(ConfigPath)
    if DoesConfigExist == False:
        print "Config file not found. Creating..."
        file = open(ConfigPath, 'w+')
        file.write("FBID:\n")
        file.write("FBEmail:\n")
        file.write("FBPassword:\n")
        file.write("Cities:\n")
        file.write("OutputDirectory:\n")
        file.close()
        return False
    else:
        return True
                   
def EditConfigs(FBID, email, password, citylist, outputdirectory):
    
    ProfilePath = os.path.expanduser("~")
    ConfigPath = ProfilePath + "\\" + "TinderScraperConfig.txt"
    file = open(ConfigPath, 'r')
    lines = file.readlines()
    newlinelist = []
    for line in lines:
        if line.startswith("FBID:"):
            line="FBID:" + FBID + "\n"
            newlinelist.append(line)
        if line.startswith("FBEmail:"):
            line="FBEmail:" + email + "\n"
            newlinelist.append(line)
        if line.startswith("FBPassword:"):
            line="FBPassword:" + password + "\n"
            newlinelist.append(line)
        if line.startswith("Cities"):
            line="Cities:" + citylist + "\n"
            newlinelist.append(line)
        if line.startswith("OutputDirectory"):
            line = "OutputDirectory:" + outputdirectory
            newlinelist.append(line)
    file.close()
    file = open(ConfigPath, "w")
    for line in newlinelist:
        file.write(line)
        
def ReadConfigs():
  
    ProfilePath = os.path.expanduser("~")
    ConfigPath = ProfilePath + "\\" + "TinderScraperConfig.txt"
    print ConfigPath
    file = open(ConfigPath, 'r')
    lines = file.readlines()
    for line in lines:
        if line.startswith("FBID:"):
            ls = line.split(":")
            FBID = ls[1]
        if line.startswith("FBEmail:"):
            ls = line.split(":")
            FBEmail = ls[1]
        if line.startswith("FBPassword:"):
            ls = line.split(":")
            FBPassword = ls[1]
        if line.startswith("Cities"):
            ls = line.split(":")
            city = ls[1]
        if line.startswith("OutputDirectory"):
            ls = line.split(":", 1)
            outputdir = ls[1]

    OutputList = [FBID, FBEmail, FBPassword, city, outputdir]
    return OutputList

def get_access_token(email, password):
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    ##submit login form##
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    ##click the 'ok' button on the dialog informing you that you have already authenticated with the Tinder app##
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
    ##get access token from the html response##
    access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    #print  s.response.content.decode()
    return access_token

def authenticate(access_token, fid):
    FBID = fid
    session = pynder.Session(facebook_id=FBID, facebook_token=access_token)
    return session

def returnGeoCoordinates(cityname):
    try:
        geolocator = Nominatim()
        location = geolocator.geocode(cityname)
        coordinates =(location.latitude, location.longitude)
    except:
        try:
            time.sleep(2)
            geolocator = Nominatim()
            location = geolocator.geocode(cityname)
            coordinates =(location.latitude, location.longitude)
        except:
            time.sleep(2)
            coordinates = returnGeoCoordinates(cityname)
    return coordinates

def get_users(session, outputpath, currentcount):
    
    #Add your own facebook ID and access token here.
    try:
        users = session.nearby_users(limit=5000)
    except Exception, e:
        print "Error detected...: " + str(e)
        print "Possible rate limiting. Pausing..."
        time.sleep(5)
        try:
            users = session.nearby_users()
        except Exception as e:
            print "Error returned from Tinder: " + str(e)
            print "Total users scanned: " + str(currentcount)
            sys.exit()
    try:
        while True:
            try:
                user = users.next()
            except:
                time.sleep(5)
                try:
                    user = users.next()
                except:
                    print "You seem to have reached the end of available users in your area. Please try again later."
                    sys.exit()
            try:
                print user.name
            except UnicodeEncodeError:
                continue
            currentcount = currentcount + 1
            user.like()
            print "Current count = " + str(currentcount)
            instagram = user.instagram_username
            if instagram == None:
               
                continue
            print("Instagram found: " + instagram)
            name = user.name
            if name == "Spotify":
                continue
            date = datetime.datetime.today()
            date = str(date.month) + "-" + str(date.day) + "-" + str(date.year)


            with open(outputpath, "a") as myfile:
                myfile.write("Date found: " + date + " Instagram Username: " + instagram + "\n")
            return currentcount
    except StopIteration, e:
        print "No more users right now."
        sys.exit()
       
        
#Start the script
ConfigExists = FindConfigFile()
if ConfigExists == False:
    username = raw_input("Please enter your facebook email account: ")
    password = raw_input("Please enter your facebook password: ")
    FB_ID = raw_input("Please enter your facebook user id. To find it, go to http://findfacebookid.com/: ")
    path = raw_input(r"Please enter the path for the folder where you would like the file of Instagram usernames to be posted: ")
    #location = raw_input("Please enter the name of the city in which you want to search: ")
    #coordinates = returnGeoCoordinates(location)
    EditConfigs(FB_ID, username, password, location, path)
else:
    ConfigData = ReadConfigs()
    FB_ID = ConfigData[0]
    username = ConfigData[1]
    password = ConfigData[2]
   # location = ConfigData[3]

   # if ',' in location:
   #     coordinates = location.split(',', 1)
   # else:
  #      coordinates = returnGeoCoordinates(location)
    path = ConfigData[4]
    path = path.rstrip('\n')
    #print "p: " + path
    
print "The file will be written to " + path + "/TinderUsersWithInstagramNames.txt"
outputpath = os.path.join(path + "/TinderUsersWithInstagramNames.txt")
token = get_access_token(username, password)

print "Authenticating..."
api = authenticate(token, FB_ID)
#print "coords: " + str(coordinates[0]) + "," + str(coordinates[1])
#api.update_location(coordinates[0], coordinates[1])

currentcount = 0
#print "Looking for users in coordinates: " + str(coordinates[0]) + "," + str(coordinates[1])
currentcount= get_users(api, outputpath, currentcount)
while True:
    currentcount = get_users(api, outputpath, currentcount)
    #if users == 1:
       # print "Scanned " + str(currentcount) + "users. Unable to find any more users in your search radius. Sleeping for one hour..."
       # time.sleep(3600)
print "No more users found for now. Try again later."



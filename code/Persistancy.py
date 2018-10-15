import os
import json
import codecs
import datetime
import hashlib

class Persistancy(object):

    def __init__(self, rootDirPath = 'C:/DataSets/instasimilar/persistancy'):
        super(Persistancy, self).__init__()
        if not os.path.isdir(rootDirPath):
            raise 'Not a valid root dir: ' + rootDirPath

        self.rootDirPath = rootDirPath
        self.recommendationFileName = 'recommendation.json'

        self.annotationFileName = 'annotationdata.json' #TODO prepare for multi annotaion
        self.filterFileName = 'filter.json'
        self.scrapingProfileFileName = 'scrapingprofile.json'

        #common
        self.settingsFileName = 'settings.json'
        self.credentialsFileName = 'credentials.json'

# path creators
    def getImageFilePath(self, url):
        print(url)
        imageDirPath = self.rootDirPath + '/data/image/'
        os.makedirs(imageDirPath, exist_ok=True)
        fileName = hashlib.sha224(url.encode('utf-8')).hexdigest() + '.jpg' #TODO in future other extentions
        return imageDirPath + fileName

    def getImageResultFilePath(self, url):
        imageDirPath = self.rootDirPath + '/data/imageresult/'
        os.makedirs(imageDirPath, exist_ok=True)
        fileName = hashlib.sha224(url.encode('utf-8')).hexdigest() + '.json'
        return imageDirPath + fileName

    def getUserDirPath(self, graphName, username):
        return self.rootDirPath + '/data/' + graphName  + '/scrape/' +  username + '/'


 ##image
    def loadImageResult(self, url):
        filePath = self.getImageResultFilePath(url)
        if os.path.isfile(filePath):
            with open(filePath, 'r', encoding="utf-8") as file:
                return json.load(file)
        else:
            return None

    def saveImageResult(self, url, imageResult):
        filePath = self.getImageResultFilePath(url)
        with open(filePath, 'w', encoding="utf-8") as file:
            json.dump(imageResult, file, ensure_ascii=False)

    # weird file type Persistancy replace this by a proper db
    def to_json(self, python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes',
                    '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    def from_json(self, json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object


    def getCachedDateFilePath(self, graphName, cacheName):
        cacheDirPath = self.rootDirPath + '/data/' + graphName  + '/cached/'
        os.makedirs(cacheDirPath, exist_ok=True)
        return cacheDirPath + cacheName + '.json'

    def getConfigFilePath(self, graphName, fileName):
        configDirPath = self.rootDirPath + '/data/' + graphName  + '/config/'
        os.makedirs(configDirPath, exist_ok=True)
        return configDirPath +  fileName

    def loadUsernamePositiveList(self, graphName):
        annotationDict = self.loadAnnotationDict(graphName)
        usernamePositiveList= []
        for username in annotationDict:
            if(annotationDict[username] == 'positive'):
                usernamePositiveList.append(username)
        return usernamePositiveList

    def loadUsernameNegativeList(self, graphName):
        annotationDict = self.loadAnnotationDict(graphName)
        usernameNegativeList= []
        for username in annotationDict:
            if(annotationDict[username] == 'negative'):
                usernameNegativeList.append(username)
        return usernameNegativeList

    def loadAnnotationDict(self, graphName, usernamePositiveList = None, usernameNegativeList = None, usernameIgnoreList = None):
        annotationDict = {}
        annotationFilePath = self.getConfigFilePath(graphName, self.annotationFileName)
        if os.path.exists(annotationFilePath):
            with open(annotationFilePath, 'r') as file:
                annotationDict = json.load(file)

        if not usernamePositiveList == None:
            for username in usernamePositiveList:
                annotationDict[username] = 'positive'

        if not usernameNegativeList == None:
            for username in usernameNegativeList:
                annotationDict[username] = 'negative'

        if not usernameIgnoreList == None:
            for username in usernameIgnoreList:
                annotationDict[username] = 'ignore'

        self.saveAnnotationDict(graphName, annotationDict)
        return annotationDict

    def saveAnnotationDict(self, graphName, annotationDict):
        annotationFilePath = self.getConfigFilePath(graphName, self.annotationFileName)
        with open(annotationFilePath, 'w') as file:
            json.dump(annotationDict, file)

    def annotateUsername(self, graphName, username, annotation) :
        #TODO valided annotation field?
        annotationDict = self.loadAnnotationDict(graphName)
        annotationDict[username] = annotation
        saveAnnotationDict(graphName, annotationDict)

    def loadRecommendationList(self, graphName):
        recommendationFilePath = self.getConfigFilePath(graphName, self.recommendationFileName)
        if os.path.exists(recommendationFilePath):
            with open(recommendationFilePath, 'r') as file:
                return json.load(file)
        else:
            return []

    def saveRecommendationList(self, graphName, recommendationList):
        recommendationFilePath = self.getConfigFilePath(graphName, self.recommendationFileName)
        with open(recommendationFilePath, 'w') as file:
            json.dump(recommendationList, file)


    ## config section
    def loadFilterUserInfo(self, graphName):
        filterFilePath = self.getConfigFilePath(graphName, self.filterFileName)
        if os.path.exists(filterFilePath):
            with open(filterFilePath, 'r') as file:
                filterUserInfo = FilterUserInfo()
                filterUserInfo.filterDict = json.load(file)
                return filterUserInfo
        filterUserInfo = FilterUserInfo()
        filterUserInfo.filterDict['isBusinessAccount'] = True
        filterUserInfo.filterDict['maxFollowerCount'] = 2000
        filterUserInfo.filterDict['minPostCount'] = 20
        filterUserInfo.filterDict['maxDaysSinceLastPost'] = 7
        self.saveFilterUserInfo(graphName, filterUserInfo)
        return filterUserInfo

    def saveFilterUserInfo(self, graphName, filterUserInfo):
        filterFilePath = self.getConfigFilePath(graphName, self.filterFileName)
        with open(filterFilePath, 'w') as file:
            json.dump(filterUserInfo.filterDict, file)


    def loadScrapingProfile(self, graphName):
        scrapingProfileFilePath = self.getConfigFilePath(graphName, self.scrapingProfileFileName)
        if os.path.exists(scrapingProfileFilePath):
            with open(scrapingProfileFilePath, 'r') as file:
                return json.load(file)
        scrapingProfile = {}
        # scrapingProfile['intermediateThreshold'] = intermediateThreshold
        # scrapingProfile['targetThreshold'] = targetThreshold
        scrapingProfile['unauthedSleepDuration'] = 1
        scrapingProfile['authedSleepDuration'] = 5
        self.saveScrapingProfile(graphName, scrapingProfile)
        return scrapingProfile

    def saveScrapingProfile(self, graphName, scrapingProfile):
        scrapingProfileFilePath = self.getConfigFilePath(graphName, self.scrapingProfileFileName)
        with open(self.scrapingProfileFilePath, 'w') as file:
            json.dump(scrapingProfile, file)

    def loadSettings(self) :
        settingsFilePath = self.getConfigFilePath('common', self.settingsFileName)
        if os.path.exists(settingsFilePath):
            with open(settingsFilePath, 'r') as file:
                return json.load(file, object_hook=self.from_json)
        return None

    def saveSettings(self, settings) :
        settingsFilePath = self.getConfigFilePath('common', self.settingsFileName)
        with open(self.settingsFilePath, 'w') as file:
            json.dump(settings, file, default=self.to_json)


    def loadCredentials(self):
        credentialsFilePath = self.getConfigFilePath('common', self.credentialsFileName)
        if os.path.exists(credentialsFilePath):
            with open(credentialsFilePath, 'r') as file:
                return json.load(file)
        return None

    def saveCredentials(self, credentials):
        credentialsFilePath = self.getConfigFilePath('common', self.credentialsFileName)
        with open(credentialsFilePath, 'w') as file:
            json.dump(credentials, file)




    def loadUserFilePathAndTimestamp(self, graphName, username, prefix) :
        userDirPath = self.getUserDirPath(graphName, username)
        if os.path.isdir(userDirPath) :
            userFileNameList = [f for f in os.listdir(userDirPath) if os.path.isfile(os.path.join(userDirPath, f))]
            for userFileName in userFileNameList :
                if(userFileName[:len(prefix)] == prefix) :
                    userFilePath = userDirPath + '/' + userFileName

                    timestamp = int(userFileName.split('_')[1].split('.')[0])
                    return userDirPath, userFilePath, timestamp
        return None, None, None

    def createUserFilePathAndTimestamp(self, graphName, username, prefix):
        userDirPath = self.getUserDirPath(graphName, username)
        timestamp = int(datetime.datetime.now().timestamp())
        userFilePath = userDirPath + prefix + '_' + str(timestamp) + '.json'
        return userDirPath, userFilePath, timestamp

    def saveJson(self, graphName, username, filePrefix, jsonObject) :
        # get and delete old file if it exists
        dirPath, filePath, timestamp = self.loadUserFilePathAndTimestamp(graphName, username, filePrefix)
        if not filePath == None :
            os.remove(filePath)
        dirPath, filePath, timestamp = self.createUserFilePathAndTimestamp(graphName, username, filePrefix)
        os.makedirs(dirPath, exist_ok=True)
        with open(filePath, 'w', encoding="utf-8") as file:
            json.dump(jsonObject, file, ensure_ascii=False)
        return jsonObject, timestamp

    def loadJson(self, graphName, username, filePrefix) :
        dirPath, filePath, timestamp = self.loadUserFilePathAndTimestamp(graphName, username, filePrefix)
        if filePath == None :
            return None, None
        with open(filePath, 'r', encoding="utf-8") as file:
            return json.load(file), timestamp

    def loadUserInfo(self, graphName, username):
        return self.loadJson(graphName, username, 'info')

    def saveUserInfo(self, graphName, username, userInfo):
        return saveJson(graphName, username, 'info', userInfo)

    def loadUserFeed(self, graphName, username):
        return self.loadJson(graphName, username, 'feed')

    def saveUserFeed(self, graphName, username, userFeed):
        return self.saveJson(graphName, username, 'feed', userFeed)

    def loadFollowingList(self, graphName, username):
        return self.loadJson(graphName, username, 'followinglist')

    def saveFollowingList(self, graphName, username, followingList):
        return self.saveJson(graphName, username, 'followinglist', followingList)

    def loadFollowedByList(self, graphName, username):
        return self.loadJson(graphName, username, 'followedbylist')

    def saveFollowedByList(self, graphName, username, followedByList):
        return self.saveJson(graphName, username, 'followedbylist', followedByList)

    # cached getters

    def loadAllUserInfo(self, graphName, refresh = False) :
        return self.loadAllJson(graphName, refresh, 'info', 'alluserinfo')

    def loadAllUserFeed(self, graphName,  refresh = False) :
        return self.loadAllJson(graphName, refresh, 'feed', 'alluserfeed')

    def loadAllUserFollowingList(self, graphName,  refresh = False) :
        return self.loadAllJson(graphName, refresh, 'followinglist', 'allfollowinglist')

    def loadAllUserFollowedByList(self, graphName,  refresh = False) :
        return self.loadAllJson(graphName, refresh,'followedbylist', 'allfollowedbylist')

    def loadAllBiography(self, graphName, refresh = False) :
        biographyDict = self.loadCachedData(graphName, 'allbiography')
        if(biographyDict == None):
            userInfoDict =self.loadAllUserInfo(graphName, refresh)
            biographyDict = {}
            for username in userInfoDict:
                biographyDict[username] = userInfoDict[username]['biography']
            self.saveCachedData(graphName, 'allbiography', biographyDict)
        return biographyDict

    def loadAllHashtag(self, graphName, refresh = False) :
        hashtagListPostListDict = self.loadCachedData(graphName, 'allhashtag')
        if(biographyDict == None):
            userFeedDict = self.loadAllUserFeed(graphName, refresh)
            hashtagListPostListDict = {}
            for username in userFeedDict:
                userFeed = userFeedDict[username]
                hashtagListPostListDict[username] = ht.getHashtagListPostList(userFeed)
            self.saveCachedData(graphName, 'allhashtag', hashtagListPostListDict)
        return hashtagListPostListDict

    def loadAllUserName(self, graphName,  refresh = False) :
        usernameList = self.loadCachedData(graphName, 'allusername')
        if(usernameList == None):
            userInfoDict = self.loadAllUserInfo(graphName, refresh)
            usernameList = list(userInfoDict.keys())
            self.saveCachedData(graphName, 'allusername', usernameList)
        return usernameList

    def loadAll(self, graphName,  refresh = False) :
        userInfoDict = self.loadAllUserInfo(graphName, refresh)
        userFeedDict = self.loadAllUserFeed(graphName, refresh)
        userFollowingListDict = self.loadAllUserFollowingList(graphName, refresh)
        userFollowedByListDict = self.loadAllUserFollowedByList(graphName, refresh)
        return userInfoDict, userFeedDict, userFollowingListDict, userFollowedByList

    def loadAllJson(self, graphName, refresh, filePrefix, cachedDataName) :
        if(refresh) :
            jsonDict = {}
            scrapeDirPath = self.rootDirPath + '/data/' + graphName + '/scrape/'
            if not os.path.isdir(scrapeDirPath) :
                return jsonDict
            usernameList = [o for o in os.listdir(scrapeDirPath) if os.path.isdir(os.path.join(scrapeDirPath,o))]

            for username in usernameList:
                jsonObject, timestamp = self.loadJson(graphName, username, filePrefix)
                if not jsonObject == None:
                    jsonDict[username] = jsonObject

            self.saveCachedData(graphName, cachedDataName, jsonDict)
        else :
            jsonDict = self.loadCachedData(graphName, cachedDataName)
            if(jsonDict == None):
                jsonDict = self.loadAllJson(graphName, True, filePrefix, cachedDataName)
        return jsonDict


    # data caching

    def loadCachedData(self, graphName, cachedDataName):
        filePath = self.getCachedDateFilePath(graphName, cachedDataName)
        if not os.path.exists(filePath):
            return None
        else:
            with open(filePath, 'r', encoding="utf-8") as file:
                return json.load(file)

    def saveCachedData(self, graphName, cachedDataName, jsonObject):
        filePath = self.getCachedDateFilePath(graphName, cachedDataName)
        with open(filePath, 'w', encoding="utf-8") as file:
            json.dump(jsonObject, file, ensure_ascii=False)

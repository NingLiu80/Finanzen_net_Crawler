import sys
import os
import threading
import time
import requests
from bs4 import BeautifulSoup

finanzenUrl = 'https://www.finanzen.net'
dictOfShare = {}


class FinanzenCrawler(threading.Thread):
    listOfBookedCourses = None

    def __init__(self):
        threading.Thread.__init__(self)

    def openFinanzenMainSite(self):
        """ This method will open the main website of Finanzen
        Args:
            None
        """
        # URL of website of Finanzen
        self.openUrlWithRequest(finanzenUrl)

    def parseFinanzenSubUrlForLinks(self, subUrl):
        """ This method will open the Sub website of Finanzen
        Args:
            None
        Return:
            None
        """
        # URL of website of Finanzen
        listSubUrl = []
        resSite = requests.get('https://www.finanzen.net/'+subUrl)
        strText = resSite.text
        soup = BeautifulSoup(strText, 'html.parser')
        tables = soup.find_all("table")
        for singleClass in tables:
            links = singleClass.find_all("a")
            for link in links:
                strLink = link.get('href')
                if strLink.startswith('/aktien/'):
                    listSubUrl.append(strLink)
        return listSubUrl

    def openFinanzenAktienFromList(self, listOfSubUrl):
        """ This method will open the main website of Finanzen
        Args:
            None
        Return:
            None
        """
        listOfDict = []
        for subUrl in listOfSubUrl:
            url = finanzenUrl+subUrl
            print("openFinanzenAktienFromList url = "+url)
            self.openUrlWithRequest(url)
            dictObj = {subUrl: dictOfShare}
            listOfDict.append(dictObj)
        return listOfDict

    # Opening the website with request
    def openUrlWithRequest(self, url):
        """ Parse the http request
        Args:
            url of the request to parse
        Return:
            None
        """
        resSite = requests.get(url)
        strText = resSite.text
        soup = BeautifulSoup(strText, 'html.parser')
        tableResponsivesClass = soup.find_all(
            attrs={"class": "table-responsive"})
        for table in tableResponsivesClass:
            kgvFound = table.find_all(string="KGV")
            if(len(kgvFound) > 0):
                self.iterateTableFromFinanzen(table)

    def iterateTableFromFinanzen(self, anotherTable):
        """ Disect the data in the table
        Args:
            anotherTable

        Return:
            None
        """
        for table in anotherTable:
            tHeads = table.find_all("thead")
            tRows = table.find_all("tr")
            if len(tHeads) > 0:
                self.iterateRowsFromFinanzen(tRows)

    # Convert them into a list of Strings
    def iterateRowsFromFinanzen(self, tRows):
        """ Iterates through a list of Rows of TR Tags
        Args:
            list of Rows
        Return:
            None
        """
        table = []
        for row in tRows:
            strLines = []
            for ele in row:
                strLines.append(ele.text)
            table.append(strLines)
            self.createDictionaryFromStringList(table)

    def createDictionaryFromStringList(self, listOfStr):
        """ Creates a dictionary of list of Strings
        Args:
            list of String = Share data Strings
        Return:
            None
        """
        dictOfYears = {}
        yearIdx = 0

        # prepare Collections of Lists
        listOfTitle = []  # y
        listOfYears = listOfStr[0][1:]  # x Get the years
        for i in range(1, len(listOfStr)):
            # Get the financial title
            listOfTitle.append(listOfStr[i][0])
        listListOfData = listOfStr[0:][1:]

        # creating dictionary for data
        for year in listOfYears:
            dictOfValuesForAYear = {}
            for i in range(0, len(listOfTitle)):
                value = listListOfData[i][yearIdx+1]
                dictOfValuesForAYear[listOfTitle[i]] = value
            dictOfYears[year] = dictOfValuesForAYear
            yearIdx += 1
        global dictOfShare
        dictOfShare = dictOfYears


def getTextFileParameters():
    """ This method read the credentials from a file
    Args:
        None
    Return:
        list of String = Sub Url for Finanzen
    """
    listOfSubUrl = []
    try:
        with open("MeineDaten.txt") as f:
            for line in f:
                listOfSubUrl.append(line.strip("\n"))
        f.close()
    except:
        print("No File detected")
    return listOfSubUrl


def outDictToFile(listOfYears, listOfDictShares, strNameOfFile):
    """ This method outputs the dictionary to a file
    Args:
        listOfYears: Years of Financial Data to look at
        listOfShares: List of SubUrl of Finanzen in form of /aktien/foo
        strNameOfFile: Name of File to be written at
    Return:
        None
    """
    strDelimter = ';'
    listOfOneSet = []
    for dictElements in listOfDictShares:
        for dictKey in dictElements:
            listOfHeader = []
            listOfDivUSD = []
            listOfDivRend = []
            listOfDivEPS = []
            listOfKGV = []
            listOfHeader.append(dictKey)
            dictElement = dictElements[dictKey]
            for yearKey in dictElement:
                if str(yearKey) in listOfYears:
                    listOfHeader.append(yearKey)
                    yearValues = dictElement[yearKey]
                    for valueKey in yearValues:
                        strValue = yearValues[valueKey]
                        strKey = str(valueKey)
                        if strKey.startswith('Dividende in '):
                            if valueKey not in listOfDivUSD:
                                listOfDivUSD.append(valueKey)
                            listOfDivUSD.append(strValue)
                        elif strKey.startswith('Dividendenrendite '):
                            if valueKey not in listOfDivRend:
                                listOfDivRend.append(valueKey)
                            listOfDivRend.append(strValue)
                        elif strKey.startswith('Ergebnis/Aktie in '):
                            if valueKey not in listOfDivEPS:
                                listOfDivEPS.append(valueKey)
                            listOfDivEPS.append(strValue)
                        elif strKey == 'KGV':
                            if valueKey not in listOfKGV:
                                listOfKGV.append(valueKey)
                            listOfKGV.append(strValue)
            print("strHeader = "+str(listOfHeader))
            print("listOfDivUSD = "+str(listOfDivUSD))
            print("listOfDivRend = "+str(listOfDivRend))
            print("listOfDivEPS = "+str(listOfDivEPS))
            print("KGV = "+str(listOfKGV))
        listOfOneSet.append(listOfHeader)
        listOfOneSet.append(listOfDivUSD)
        listOfOneSet.append(listOfDivRend)
        listOfOneSet.append(listOfDivEPS)
        listOfOneSet.append(listOfKGV)

        strSet = ""
        for eachSet in listOfOneSet:
            for eachWord in eachSet:
                strSet += eachWord+strDelimter
            strSet += "\n"

        with open(strNameOfFile, "w+") as f:
            f.write(strSet)
        f.close()


if __name__ == "__main__":
    # create Checker
    fc = FinanzenCrawler()
    urlArgs = sys.argv[1]
    strFilename = sys.argv[2]
    listOfDictShares = fc.openFinanzenAktienFromList(
        fc.parseFinanzenSubUrlForLinks(urlArgs))
    outDictToFile(['2019', '2020'], listOfDictShares, strFilename)

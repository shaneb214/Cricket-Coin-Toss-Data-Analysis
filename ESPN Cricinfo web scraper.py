# -*- coding: utf-8 -*-
"""
Script to create csv's files from team records on ESPN Cricinfo.com.
First time doing web scraping so probably could be a lot better.
It runs extremely slowly and didnt know how to make it faster. 
I created the csv file and added the header myself before running this code.
The code appends results to the csv file. 
"""
import requests
import pandas
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
#Urls in which the web scraping for each form of cricket begins.
test_records_url = 'https://stats.espncricinfo.com/ci/content/records/307847.html'
odi_records_url = 'https://stats.espncricinfo.com/ci/content/records/307851.html'
t20_records_url = 'https://stats.espncricinfo.com/ci/content/records/307852.html'
cric_info_base_url = 'https://stats.espncricinfo.com'

#Table headers for my csv file.
table_headers = ['Team 1','Team 2','Winner','Margin','Ground','Date','Year','Toss Winner','Toss Decision']

#CSV Location
csv_file_location = 'C:/Users/Shane/Desktop/test.csv'

    
#Supplied with a URL link to a page which contains links to results for each year
#Will return a list of all these links.
def GetListOfURLYearRecords(baseURL):
    
    #Set up request.
    r = requests.get(baseURL, headers=headers)
    soup = BeautifulSoup(r.text,'html.parser')
    
    #Find all rows which contain links to each year in that decade
    decade_rows = soup.find_all('ul',{'class': 'category-noindent'})
    
    urlList = [] 
    #Go through each decade row and find link to each year.
    for row in decade_rows:
                
        year_hyperlink = row.find_all('a',{'class': 'QuoteSummary'})
        
        for item in year_hyperlink:
            
            url = cric_info_base_url + item['href']
            urlList.append(url)
      
    return urlList
    

#Given a URL to a page which displays match results in a table format for a year.
#Returns a a list of lists which contains match information including coin toss.
def GetMatchResultsForYear(year_url):
    
    #Set up request.
    r = requests.get(year_url, headers=headers)
    soup = BeautifulSoup(r.text,'html.parser')    
      
    #Find table that contains rows of all matches in that year.
    table = soup.find('table', {'class':'engineTable'})     
    
    #Row of info to returned at end.
    matchresultslist = []
       
    #Get each table row which contains match information. 
    table_rows = table.find_all('tr',{'class': 'data1'})
    
    #Find all the text info in each row: team1, team2, winner etc.
    for table_row in table_rows:     
        resultlist = []
        tds = table_row.find_all('td')      
        #Append info for first 4 columns only.
        for td in tds[:-2]:
            resultlist.append(td.text)
            
        #Get match date text for splitting.
        matchDateText = tds[-2].text
        
        date_of_match,year_of_match = GetDateYearOfMatch(matchDateText)
        resultlist.append(date_of_match)
        resultlist.append(year_of_match)
        
        #Find toss result Info.
        scorecardURL = cric_info_base_url + tds[-1].find('a')['href']
        toss_winner,toss_decision = GetTossResult(scorecardURL)
        resultlist.append(toss_winner)
        resultlist.append(toss_decision)
        
        matchresultslist.append(resultlist) 
        
        
    return matchresultslist
    
#Return date and year of match given "Match Date" string in table.
def GetDateYearOfMatch(matchDateText):
    #If the date of game goes over into two years eg. Dec 30th - Jan 3rd.
    #Only can occur for test matches which can go for multiple days.
    #Example "Dec 31, 1881 - Jan 4, 1882"
    if(" - " in matchDateText):
        matchDateTextSplit = matchDateText.split(" - ") 
        
        start_game_date_split = matchDateTextSplit[0].split(", ")
        end_game_date_split = matchDateTextSplit[1].split(", ")
        
        #Set date to be like Dec 31 - Jan 4
        date_of_match = start_game_date_split[0] + "-" + end_game_date_split[0]
        #Pick year match started to be the year the match occured.
        year_of_match = start_game_date_split[1]
        
        return [date_of_match,year_of_match]
                
    #Date doesn't go over into another year.    
    else:            
        
        splitDateText = matchDateText.split(", ")    
        return [splitDateText[0],splitDateText[1]]
        

#Returns two strings of toss result - toss winner & their decision.     
def GetTossResult(matchURL):
              
    r = requests.get(matchURL, headers=headers)
    soup = BeautifulSoup(r.text,'html.parser')   
    
    table = soup.find('table', {'class':'w-100 table match-details-table'})
    
    #Means page or table cannot be reached - return none
    if(table == None):
        return [None,None]
      
    table_rows = table.find_all('tr')
    #Toss row is second row.
    tds = table_rows[1].find_all('td')
    #Toss info is on second td of this row.
    toss_info = tds[1].text
    
    #Toss info text is always in the format of:
    #"Team name, elected to bat first" or "Team name, elected to field first"
    
    #Split the string where comma is.
    toss_info_split = toss_info.split(",")
    #First part will be the toss winner.
    toss_winner = toss_info_split[0]
    #Second part will be the toss decision.
    toss_decision = ""
    
    try:
        if("field" in toss_info_split[1]):
            toss_decision = "Field"
        else:
            toss_decision = "Bat"
    except:   
        return [None,None]
        
    
    return [toss_winner,toss_decision]
    
    
def WriteResultsToCSV(baseURL,CSVPath):
    
    rowList = []    
    year_record_urls = GetListOfURLYearRecords(baseURL)  
    
    #For each URL of each year.
    for year_record_url in year_record_urls:
        #Get all results from each match in that year.
        
        match_results = GetMatchResultsForYear(year_record_url)
        #For each result - write to CSV.
        for result in match_results:
            print(result)
            rowList.append(result)
                           
    pd = pandas.DataFrame(rowList)
    pd.to_csv(CSVPath,mode='a',index=False,header=False)
    print("Done writing results.")   
    print("Done creating CSV File.")
    

WriteResultsToCSV(test_records_url,csv_file_location) 
    
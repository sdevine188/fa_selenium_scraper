import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import numpy as np
import math
from datetime import datetime
import win32clipboard
import re
        
# set wd
os.chdir("C:/Users/Stephen/Desktop/Python/fa_selenium_scraper")

 
# create fa_selenium_scraper
def fa_selenium_scraper(month, year):

         
        #//////////////////////////////////////////////////////////////////////
        
        
        # read in username, password, and login url
        credentials = pd.read_csv("fa_username_and_password.csv")
        username = credentials["username"].values[0]
        password = credentials["password"].values[0]
        login_url = credentials["login_url"].values[0]
        
        
        #//////////////////////////////////////////////////////////////////////
         
         
        # get volume/issue url based on year/month
        if(year == 2021):
                volume = "100"
        if(month <= 2):
                issue_number = "1"
        elif(month > 2 and month <= 4):
                issue_number = "2"
        elif(month > 4 and month <= 6):
                issue_number = "3"
        elif(month > 6 and month <= 8):
                issue_number = "4"
        elif(month > 8 and month <= 10):
                issue_number = "5"
        elif(month > 10 and month <= 12):
                issue_number = "6"
                
        issue_url = "https://www.foreignaffairs.com/issues/" + str(year) + "/" + volume + "/" + issue_number 
        print(issue_url)
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # create article_output_df
        article_output_df = pd.DataFrame({"article_text" : []})
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # start driver
        driver = webdriver.Chrome("chromedriver.exe")
        
        # set page load timeout
        driver.set_page_load_timeout(60)
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # login
        driver.get(login_url)
        time.sleep(2)
        driver.find_element_by_xpath("//input[@id = 'edit-name']").send_keys(username)
        driver.find_element_by_xpath("//input[@id = 'edit-pass']").send_keys(password)
        time.sleep(2)
        driver.find_element_by_xpath("//input[@id = 'edit-submit']").click() 
        time.sleep(2)
        print("login complete")
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # go to issue_url
        driver.get(issue_url)
        time.sleep(4)
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # get issue_main_article_elements
        issue_main_article_elements = driver.find_elements_by_xpath("//div[@class = 'magazine-list'][1]//a[@href]")
        
        # add main_article_urls to article_urls
        article_urls = []
        for i in list(range(0, len(issue_main_article_elements))):
                article_urls.append(issue_main_article_elements[i].get_attribute("href"))
 
        # get issue_essay_elements
        issue_essay_elements = driver.find_elements_by_xpath("//div[@class = 'magazine-list'][2]//a[@href]")
        
        # add essay_urls to article_urls
        for i in list(range(0, len(issue_essay_elements))):
                article_urls.append(issue_essay_elements[i].get_attribute("href"))        
        
        # keep only correct urls
        correct_urls_regex = issue_url[0:30] + "/articles" 
        article_urls_df = pd.DataFrame({"article_urls" : article_urls})
        article_urls_df = article_urls_df[article_urls_df["article_urls"].str.contains(correct_urls_regex)]

        # get article_total_count
        article_total_count = article_urls_df.shape[0]
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # get article_text for each article_url and add to article_output_df
        for i in list(range(0, len(article_urls_df.article_urls.tolist()))):
                
                # get current_article_url
                current_article_url = article_urls_df.article_urls.tolist()[i]
                print(current_article_url)
        
                # load current_article_url page
                driver.get(current_article_url)
                time.sleep(4)
        
                # get current_article_title
                current_article_title = driver.find_elements_by_xpath("//h1[@data-drupal-page-title]")[0].text
                
                # get current_article_subtitle
                current_article_subtitle_element = driver.find_elements_by_xpath("//h2[@class = 'f-serif ls-0 article-subtitle ']")
                if(len(current_article_subtitle_element) == 0):
                        current_article_subtitle = ""
                else:
                        current_article_subtitle = current_article_subtitle_element[0].text
                
                # get current_article_author
                current_article_author_element = driver.find_elements_by_xpath("//a[@href = '#author-info']")
                if(len(current_article_author_element) == 0):
                        current_article_author = ""
                else:
                        current_article_author = current_article_author_element[0].text
        
                # get current_article_text
                current_article_text_elements = driver.find_elements_by_xpath("//div[@class = 'article-dropcap ls-0  f-serif']//p")
                current_article_text = ""
                for paragraph_i in list(range(0, len(current_article_text_elements))):
                        current_article_text = current_article_text + current_article_text_elements[paragraph_i].text + " {{Pause=.3}} "
        
                # combine to get current_article_complete
                current_article_complete = "{{Pause=.3}} Foreign Affairs {{Pause=.3}} Article " + \
                        str(i + 1) + " of " + str(article_total_count) + " {{Pause=.3}} " + \
                        current_article_title + " {{Pause=.3}} " + current_article_subtitle + \
                        " {{Pause=.3}} " + "By: " + current_article_author + " {{Pause=.3}} " + \
                        current_article_text + " {{Pause=.3}} " + "{{split}}" 
                        
                # split article if it's over excel's 32,767 character limit (no articles should be > 64000 characters)
                # yes there will be an abrupt cutoff mid-word at 32000 characters, 
                # but not worth trying to snip at the end of a sentence etc
                if(len(current_article_complete) > 32000):
                        
                        # get current_article_complete_part_1
                        current_article_complete_part_1 = current_article_complete[0:32000] + "{{split}}" 
                        
                        # get current_article_complete_part_2
                        current_article_complete_part_2 = current_article_complete[32000:]
                        
                        # get current_article_df
                        current_article_df = pd.DataFrame({"article_text" : [current_article_complete_part_1,
                                                                             current_article_complete_part_2]})

                else:        
                        current_article_df = pd.DataFrame({"article_text" : [current_article_complete]})
                
                # add current_article_df to article_output_df
                article_output_df = article_output_df.append(current_article_df)
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
         # remove weird characters
        article_output_df.article_text = article_output_df.article_text.replace("–", "-", regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("’", "'", regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("“", '"', regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("”", '"', regex = True)
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # write article_output_df 
        file_name = "fa_text_" + str(month) + ".csv"
        article_output_df.to_csv(file_name, index = False)
        
        
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

      
# run fa_selenium_scraper
fa_selenium_scraper(month = 11, year = 2021)
        
import re
import time
from helpers.scraper import Scraper
from selenium.common.exceptions import TimeoutException
import os
from selenium.webdriver.common.by import By
import random
import pandas as pd
from helpers.functions import read_txt, formatted_time, formatted_number_with_comma, countdown, execution_time, write_to_csv
from helpers.user import generate_user_info

# Check if Audiobook
def is_audiobook(formats_div):
    lis = formats_div.find_elements(By.TAG_NAME, 'li')
    for li in lis:
        spans = li.find_elements(By.TAG_NAME, 'span')
        for span in spans:
            if span.text == 'Audiobook':
                return True   
    return False

def check_and_solve_captcha(scraper):
    # Check for captcha and solve manually
    if scraper.driver.current_url.split('?')[0] == 'https://www.google.com/sorry/index':
        print('Solve the captcha manually and', end=' ')
        os.system('pause')

def scrape_data(scraper):
    
    links = scraper.find_elements('a[href^="https://www.amazon."]')
    # if len(links) == 0:
    #     check_and_solve_captcha(scraper)
    
    # print(len(links))
    for link in links:
        book_link = link.get_attribute('href')
        if '-ebook/dp/' not in book_link:
            return False
        # print(book_link)
        scraper.go_to_new_tab(book_link)
        formats_div = scraper.find_element('div[id="formats"]', exit_on_missing_element = False)
        
        if formats_div == False or is_audiobook(formats_div):
            # print('formats_div false or audio book true')
            scraper.close_tab_and_back_home()
            return False
            
        else:
            title = scraper.find_element('span[id="productTitle"]', exit_on_missing_element = False)
            
            if title == False:
                scraper.close_tab_and_back_home()
                return False
            else:
                title = title.text
                        
            author_div = scraper.find_element('div[id="followTheAuthor_feature_div"]')
            author_name = author_div.find_elements(By.TAG_NAME, 'a')[1].text
            
            product_details_div = scraper.find_element(
                'div[id="detailBulletsWrapper_feature_div"]'
            )
            ul = product_details_div.find_elements(By.TAG_NAME, 'ul')[1]
            best_seller = ul.find_elements(By.CSS_SELECTOR, 'span[class="a-list-item"]')[0]
            rank = best_seller.text.split('\n')[0]
            rank = rank.split('(')[0]   
            # print(title, author_name, rank)
            scraper.close_tab_and_back_home()
            return [title, author_name, rank]
    return False

# Header of the program
start_time = time.time()

url = read_txt('websites.txt')[0]

# Data initialization
labels = ['search_rank', 'title', 'author_name', 'rank']
result = []

print('1. Search on ecosia\n2. Search on google')
option = int(input('Choose either 1 or 2: '))
n = int(input('Number of Search Rank: '))
count = 0
os.system('cls')
print('Searching...')

scraper = Scraper(url)

for rank in range(1, n):
    formatted_rank = formatted_number_with_comma(rank)
    
    if option == 1:
        url = f'https://www.ecosia.org/search?q=%22Best%20Sellers%20Rank%3A%20%23{formatted_rank}%20in%20Kindle%20Store%22'
    else:
        url = f'https://www.google.com/search?q=%22Best+Sellers+Rank%3A+%23{formatted_rank}+in+Kindle+Store%22'
    
    scraper.go_to_page(url)
    data = scrape_data(scraper)
    if data:
        data.insert(0, '#' + str(rank))
        result.append(data)
        write_to_csv(result, labels)
        count += 1
                
# Footer
os.system('cls')
print('Execution Completed')
print('\nReport:\n================================')
execution_time(start_time)
print(f'Searched for rank #1 to #{n}')
print(f'Book information inserted into csv: {count}')
scraper.driver.close()

                

        


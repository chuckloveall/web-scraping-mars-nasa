from bs4 import BeautifulSoup as bs
import requests
import pymongo
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
import time
def scrape_info():
    # Create connection variable
    conn = 'mongodb://localhost:27017'

    # Pass connection to the pymongo instance.
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    executable_path= {"executable_path": ChromeDriverManager().install()}
    browser= Browser("chrome", **executable_path, headless=False)
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    # Retrieve page with the requests module
    browser.visit(url)
    time.sleep(1)
    html=browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html,'html.parser')
    # print(soup)
    results = soup.find_all('div', class_='content_title')
    header= results[1].find('a').text
    paragraph = soup.find('div', class_='article_teaser_body').text
    url2= "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    browser.visit(url2)
    time.sleep(1)
    links_found = browser.find_by_text(' FULL IMAGE').click()
    time.sleep(1)
    html=browser.html
    soup2=bs(html,"html.parser")
    results2= soup2.find('img', class_= "fancybox-image")
    image_path=results2["src"]
    base_url="https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/"
    new_url= base_url + image_path
    # print(new_url)
    facts_url= "https://space-facts.com/mars/"
    browser.visit(facts_url)
    facts_html= browser.html
    facts_soup= bs(facts_html, "html.parser")
    #find table and get to html string
    time.sleep(1)

    trs=facts_soup.find_all('tr')
    # labels= facts_soup.find_all('strong')
    keys= []
    values= []
    # print(trs[0])
    # trs[0].text gives you 'Equatorial Diameter:6,792 km'
    new_split= trs[0].text.split(':')
    # new_split[1]
    for tr in trs:
        split= tr.text.split(':')
    #     print(split)
        try:
            keys.append(split[0])
            values.append(split[1])
        except:
            pass
    print(keys)
    print(values)
    usgs_url= "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemisphere_image_urls= []
    browser.visit(usgs_url)
    time.sleep(1)
    links= browser.find_by_css('a.product-item img')
    #iterate here
    for i in range(len(links)):
        empty= {}
        browser.find_by_css('a.product-item img')[i].click()
        time.sleep(1)
        html4= browser.html
        links1= browser.find_by_text('Sample')['href']
        empty['img_url']= links1
        title_soup= bs(html4, 'html.parser')
        links2=title_soup.find('h2', class_='title').text
        empty['title']= links2
        hemisphere_image_urls.append(empty)
        browser.back()
    combined= {
    "Header": header,
    "Paragraph": paragraph,
    "New_url": new_url,
    "Keys": keys,
    "Values": values,
    "Hemisphere_Image_URLS": hemisphere_image_urls}

    # Creates a collection in the database and inserts two documents
    db.mars.insert_one(combined)
     # Close the browser after scraping
    browser.quit()
    return combined

import os
import requests
import bs4
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

root_facialdb_folder = '/usr/local/facial_database/'
images_folder = 'datasets/face_images'
os.chdir(root_facialdb_folder)

actor_name = 'Matthew Mcconaughey'
query = actor_name + ' face'

print(f'Test started, we are going to find images for search "{query}"')

#creating a directory to save images
if not os.path.isdir(images_folder):
    os.makedirs(images_folder)

def download_image(url, face_folder, num):
    # write image to file
    response = requests.get(url)
    if response.status_code==200:
        with open(os.path.join(face_folder, str(num)+'.jpg'), 'wb') as file:
            file.write(response.content)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Remote(
    command_executor='http://chrome:4444/wd/hub',
    options=options
)
driver.maximize_window()

try:

    user_input = input("Press any key to start the search")
    driver.get("https://images.google.com/")
    print(driver.current_url)

    #By-passing cookies
    WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="L2AGLb"]'))).click()
    # Finding the search box
    box = driver.find_element('name', 'q')

    # Type the search query in the search box
    box.send_keys(query)
    # Pressing enter
    box.send_keys(Keys.RETURN)

    #Scrolling all the way up
    driver.execute_script("window.scrollTo(0, 0);")

    page_html = driver.page_source
    pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
    containers = pageSoup.findAll('div', {'class':"isv-r PNCib MSM1fd BUooTd"} )
    print(f'Total amount of images is: {len(containers)}')

    len_containers = len(containers)

    for i in range(1, len_containers+1):
        if i % 25 == 0:
            continue

        xPath = """//*[@id="islrg"]/div[1]/div[%s]"""%(i)

        previewImageXPath = """//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img"""%(i)
        previewImageElement = driver.find_element('xpath',previewImageXPath)
        previewImageURL = previewImageElement.get_attribute("src")

        driver.find_element('xpath',xPath).click()

        timeStarted = time.time()
        while True:
            imageElement = driver.find_element('xpath','//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img')
            imageURL= imageElement.get_attribute('src')

            if imageURL != previewImageURL:
                break

            else:
                #making a timeout if the full res image can't be loaded
                currentTime = time.time()

                if currentTime - timeStarted > 10:
                    print("Timeout! Will download a lower resolution image and move onto the next one")
                    break

        #Downloading image
        try:
            download_image(imageURL, images_folder, i)
            print(f'Downloaded element {i} out of {len_containers + 1} total. URL: {imageURL}')
        except:
            print(f"Couldn't download an image {i}, continuing downloading the next one")

    user_input = input("Press any key to terminate session")
    driver.quit()

except Exception as e:
    print('Something went wrong, closing session...')
    print(e)
    driver.quit()
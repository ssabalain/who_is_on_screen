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
os.chdir(root_facialdb_folder)

def download_image(url, folder, file_name, num):
    actor_directory = os.path.join(folder,file_name) 
    #creating a directory to save images
    if not os.path.isdir(actor_directory):
        os.makedirs(actor_directory)
    # write image to file
    response = requests.get(url)
    if response.status_code==200:
        with open(os.path.join(actor_directory,file_name + '_' + str(num)+'.jpg'), 'wb') as file:
            file.write(response.content)

def create_actor_folder(images_folder,actor_name,dataset_size):
    try:
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
        driver.get("https://images.google.com/")
        #By-passing cookies
        WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="L2AGLb"]'))).click()
        box = driver.find_element('name', 'q')
        box.send_keys(actor_name + ' face')
        box.send_keys(Keys.RETURN)
        driver.execute_script("window.scrollTo(0, 0);")

        # Parsing HTML from search page
        page_html = driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
        # Spotting all the image containers
        containers = pageSoup.findAll('div', {'class':"isv-r PNCib MSM1fd BUooTd"} )
        print(f'Total number of images available is: {len(containers)}')
        len_containers = len(containers)
        total_images = 0

        if dataset_size > len_containers:
            total_images = len_containers
        else:
            total_images = dataset_size

        print(f'We proceed with the download of {total_images} for actor {actor_name}')

        for i in range(1, total_images + 1):
            if i % 25 == 0:
                # The 25th element and their multiples are not images but links to other searches, so we skip them
                continue

            # Defining a specific cointainer xPath
            xPath = '//*[@id="islrg"]/div[1]/div[%s]'%(i)

            # We get URL from the preview image (lower resolution)
            previewImageXPath = '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img'%(i)
            previewImageElement = driver.find_element('xpath',previewImageXPath)
            previewImageURL = previewImageElement.get_attribute("src")

            # We click the container
            driver.find_element('xpath',xPath).click()

            timeStarted = time.time()
            while True:
                # Once clicked, we get the URL from the full image (higher resolution)
                imageElement = driver.find_element('xpath','//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img')
                imageURL= imageElement.get_attribute('src')

                # We check if the full image has loaded
                if imageURL != previewImageURL:
                    break

                else:
                    #making a timeout if the full res image can't be loaded
                    currentTime = time.time()
                    if currentTime - timeStarted > 10:
                        print('Timeout! Will download a lower resolution image and move onto the next one')
                        break

            #Downloading image
            try:
                download_image(imageURL, images_folder, actor_name.replace(' ','_').lower() , i)
                print(f'Downloaded element {i} out of {total_images} total. URL: {imageURL}')
            except:
                print(f"Couldn't download an image {i}, continuing downloading the next one")

        driver.quit()

    except Exception as e:
        print('Something went wrong, closing session...')
        print(e)
        driver.quit()
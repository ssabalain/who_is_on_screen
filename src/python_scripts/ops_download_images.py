from ops_check_packages import install_packages
ops_download_images_packages = ["selenium","requests","bs4"]
install_packages(ops_download_images_packages)

import os
import requests
import bs4
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ops_database_operations import return_array_from_query
from ops_logger import Logger

root_facialdb_folder = '/opt/workspace/src/'
os.chdir(root_facialdb_folder)

def download_image(url, folder, file_name, num):
    #creating a directory to save images
    if not os.path.isdir(folder):
        os.makedirs(folder)
    # write image to file
    response = requests.get(url)
    if response.status_code==200:
        with open(os.path.join(folder,file_name + '_' + str(num)+'.jpg'), 'wb') as file:
            file.write(response.content)

def get_images_on_folder(images_folder,search_query,file_name,dataset_size, logger = None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

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
        box.send_keys(search_query)
        box.send_keys(Keys.RETURN)
        driver.execute_script("window.scrollTo(0, 0);")

        # Parsing HTML from search page
        page_html = driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
        # Spotting all the image containers
        containers = pageSoup.findAll('div', {'class':"isv-r PNCib MSM1fd BUooTd"} )
        logger.debug(f'Total number of images available is: {len(containers)}')
        len_containers = len(containers)
        total_images = 0

        if dataset_size > len_containers:
            total_images = len_containers
        else:
            total_images = dataset_size

        images_downloaded = 0
        i = 1

        logger.debug(f'We proceed with the download of {total_images} images for query {search_query}')

        while images_downloaded < dataset_size:
            if i > len_containers:
                break

            if i % 25 == 0:
                # The 25th element and their multiples are not images but links to other searches, so we skip them
                logger.debug(f'Skipping element {i}')
                i += 1
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
                    if currentTime - timeStarted > 20:
                        logger.debug('Timeout! Will download a lower resolution image and move onto the next one')
                        break

            #Downloading image
            try:
                download_image(imageURL, images_folder, file_name, images_downloaded + 1)
                logger.debug(f'Downloaded element {images_downloaded + 1} out of {total_images} total. URL: {imageURL}')
                images_downloaded += 1
                i += 1

            except:
                logger.debug(f"Couldn't download an image {i}, continuing downloading the next one")
                i += 1

        logger.debug(f'Process completed. {images_downloaded} images downloaded')
        driver.quit()

    except Exception as e:
        logger.error('Something went wrong, closing session...')
        logger.error(e)
        driver.quit()

    if close_logger:
        log.shutdown_logger()

def create_facial_dataset(movies, actors_per_movie, sql_dict, dataset_folder, images_by_actor,logger = None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    sql_user = sql_dict['user']
    sql_pwd = sql_dict['pwd']
    db_name = sql_dict['database']
    movies_string = "'" + "','".join(movies) + "'"
    query = f"""
        with base as (
            select
                m.original_title,
                a.actor_id,
                a.name,
                axm.character,
                axm.order as movie_order,
                row_number() over(partition by m.original_title order by axm.order) as limit_rank
            from actors_by_movie as axm
            join actors as a on axm.actor_id = a.actor_id
            join movies as m on axm.movie_id = m.movie_id
            where original_title in ({movies_string})
                and axm.character not like '%uncredited%'
                and axm.character not like '%(voice)%'
                and a.popularity > 3
        )
        
        select * from base where limit_rank <= {actors_per_movie} order by movie_order
        """
    actors_array = return_array_from_query(sql_user,sql_pwd,db_name,query)

    for actor in actors_array:
        actor_name = actor['name'].replace(' ','_').lower()
        actor_folder_name = str(actor['actor_id']) + '_' + actor_name
        actor_full_path = os.path.join(dataset_folder,actor_folder_name)
        actor_search_query = actor['name'] + ' face'
        actor_movie_name = actor_name + "_" + actor['original_title'].replace(' ','_').lower()
        actor_movie_search_query = actor['name'] + ' face ' + actor['original_title']
        logger.debug(f'Downloading images for actor {actor_name}')

        if not os.path.isdir(actor_full_path):
            logger.debug(f'No images already for actor {actor_name}')
            logger.debug(f'We will download {images_by_actor} images for actor {actor_name}')
            get_images_on_folder(actor_full_path, actor_search_query,actor_name, images_by_actor,logger=logger)
            logger.debug(f'Now we download 3 images for actor {actor_name} in the movie {actor["original_title"]}')
            get_images_on_folder(actor_full_path, actor_movie_search_query, actor_movie_name, 3,logger=logger)

        else:
            logger.debug(f'Images already for actor {actor_name}')
            logger.debug(f'Now we download 3 images for actor {actor_name} in the movie {actor["original_title"]}')
            get_images_on_folder(actor_full_path, actor_movie_search_query, actor_movie_name, 3,logger=logger)

    if close_logger:
        log.shutdown_logger()
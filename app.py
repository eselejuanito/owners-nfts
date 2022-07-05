# -*- coding: utf-8 -*-
import time
import re
import sqlite3
import urllib.request
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class App:
    def __init__(self, official_collection_url = '', start_time = 0, nft_images_folder = ''):
        self.start_time = start_time
        # This is the number of sections on left side of NFT: Description, properties, about, and details. Somethings not appears the properties, this is a bug
        self.number_of_sections = 4

        self.nft_images_folder = nft_images_folder
        # Create a directory or ignore
        if not os.path.exists(self.nft_images_folder):
            os.mkdir(self.nft_images_folder)

        self.last_id = 1
        # To remove the pop up notification window
        options = Options()
        options.binary_location = 'C:\Program Files\Mozilla Firefox\\firefox.exe'
        options.set_preference("dom.webnotifications.enabled", False)
        # geckodriver allows you to use emojis, chromedriver does not
        self.driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)
        self.driver.maximize_window()
        
        self.nft_url, self.number_of_assets, self.properties, self.number_of_properties = self.extractingImportantVariables(official_collection_url)

        # Only create the first time
        if os.path.exists('owners-nfts.db'):
            self.cleanDatabase(self.properties)
        else:
            self.createDatabase(self.properties)

        for asset in range(self.last_id, self.number_of_assets + 1):
            time_by_nft = time.time()
            self.driver.get(self.nft_url + str(asset))
            # self.saveNFTImage(asset)
            self.insertRowNFT(self.getOwnersNfts(), self.properties, self.number_of_properties)
            print(f"Time by NFT: {time.time() - time_by_nft:0.2f} seconds s")
  
        print(f"Total time taken: {time.time() - self.start_time:0.2f} seconds s")
        self.driver.quit()

    def extractingImportantVariables(self, official_collection_link):
        properties = {}
        properties['create'] = ''
        properties['insert'] = ''
        self.driver.get(official_collection_link)

        # Get number of assets in a collection  
        number_of_assets_string = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div[5]/div/div[3]/div[3]/div[3]/div[2]/div/p')))
        number_of_assets = re.findall('[0-9]+', number_of_assets_string.text.replace('.',''))
        if len(number_of_assets) != 1:
            print ('Not found the number of assets')
            quit()

        # Get NFT Url
        nft_url_element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div[5]/div/div[3]/div[3]/div[3]/div[3]/div[2]/div/div/div[1]/div/article/a')))
        nft_url_result = re.search('(http(s)?):\/\/(www\.)?opensea\.io\/assets\/[]a-zA-Z0-9]+\/0x[a-fA-F0-9]{40}\/', nft_url_element.get_attribute('href'))

        # Get properties 
        self.driver.get(nft_url_element.get_attribute('href'))
        properties_elements = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="Panel--isContentPadded item--properties"]/a/div/div[@class="Property--type"]')))
        number_of_properties = (len(properties_elements)) * 2
        
        for property_element in properties_elements:
            property = property_element.text.lower().replace(' ', '_')
            properties['create'] = properties['create'] + property + ' text, ' + property + '_rarity real, '
            properties['insert'] = properties['insert'] + property + ', ' + property + '_rarity, '

        return nft_url_result.group(0), int(number_of_assets[0]), properties, number_of_properties
        


    def cleanDatabase(self, properties):
        con = sqlite3.connect('owners-nfts.db')
        cursorObj = con.cursor()
        cursorObj.execute('SELECT MAX(id) FROM nft')
        last_one_id = cursorObj.fetchone()[0]
        if last_one_id == None:
            cursorObj.execute('DELETE FROM nft')
        elif last_one_id < self.number_of_assets:
            self.last_id = last_one_id + 1
        else:
            cursorObj.execute('DELETE FROM nft')

        con.commit()
        con.close()

    def createDatabase(self, properties):
        con = sqlite3.connect('owners-nfts.db')
        cursorObj = con.cursor()
        cursorObj.execute("CREATE TABLE nft(id integer PRIMARY KEY, nickname text, owner_url text, contract_address text, nft_number text, nft_url text, " + properties['create'] + "bug numeric)")
        con.commit()
        con.close()

    def getOwnersNfts(self):
        # empty nft information
        nft_information = []

        owner_nickname = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a/span')))

        owner_url = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a')))

        # Because we have nfts with no properties (bug), we need to make another validation
        items_summary = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="item--summary"]/section/div/div')))
        position_of_last_element = len(items_summary)

        # nft_contract_address = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[' + str(position_of_last_element) + ']/div/div/div/div/div/div[1]/span/a')))

        nft_contract_address = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Body assets-item-asset-details"]/div/div/div/div[1]/span/a')))

        nft_number = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[1]/h1')))

        nft_information.append(owner_nickname.text)
        nft_information.append(owner_url.get_attribute('href'))
        nft_information.append(nft_contract_address.get_attribute('href'))
        nft_information.append(nft_number.text)
        nft_information.append(self.driver.current_url)

        if position_of_last_element < self.number_of_sections:
            for index in range(1, self.number_of_properties + 1):
                nft_information.append('')
            nft_information.append(True)
        else:
            # Properties
            n_properties = int(self.number_of_properties / 2)
            for index in range(1, n_properties + 1):
                property = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Body assets-item-properties"]/div/div/a[' + str(index) + ']/div/div[2]')))
                percentage = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Body assets-item-properties"]/div/div/a[' + str(index) + ']/div/div[3]')))
                # Fill information of NFT
                nft_information.append(property.text)
                nft_information.append(float(re.findall(r'\d*\.\d+|\d+', percentage.text)[0]))
                
            nft_information.append(False)

        return nft_information


    def insertRowNFT(self, data, properties, number_of_properties):
        number_of_elements_to_insert = ''
        for index in range(0, number_of_properties + 6):
            number_of_elements_to_insert = number_of_elements_to_insert + '?,'

        con = sqlite3.connect('owners-nfts.db')
        cursorObj = con.cursor()
        sql = 'INSERT INTO nft (nickname, owner_url, contract_address, nft_number, nft_url, ' + properties['insert'] + 'bug) VALUES(' + number_of_elements_to_insert[:-1] + ')'
        cursorObj.execute(sql, data)
        con.commit()
        con.close()

    def saveNFTImage(self, asset):
        nft_image = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[1]/article/div/div/div/div/img')))
        # ext 
        ext = os.path.splitext(nft_image.get_attribute('src'))
        opener = urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(nft_image.get_attribute('src'), nft_images_folder + '/' + str(asset) + ext[1])


if __name__ == '__main__':
    start_time = time.time()
    # Only for OpenSea
    official_collection_url = 'https://opensea.io/collection/bookers-oficial'
    nft_images_folder = 'images'
    app = App(official_collection_url, start_time, nft_images_folder)
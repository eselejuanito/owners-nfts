# -*- coding: utf-8 -*-
import json
import time
import sqlite3
import os.path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class App:
    def __init__(self, number_of_assets = 0, start_time = 0):
        self.number_of_assets = number_of_assets
        self.start_time = start_time
        self.last_id = 1
        # To remove the pop up notification window
        options = Options()
        options.binary_location = 'C:\Program Files\Mozilla Firefox\\firefox.exe'
        options.set_preference("dom.webnotifications.enabled", False)
        # geckodriver allows you to use emojis, chromedriver does not
        self.driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)
        self.driver.maximize_window()
        # Only create the first time
        self.createOrCleanDatabase()

        for asset in range(self.last_id, self.number_of_assets + 1):
            time_by_nft = time.time()
            self.driver.get('https://opensea.io/assets/matic/0x6172974acedb93a0121b2a7b68b8acea0918be8c/' + str(asset))
            self.insertRowNFT(self.getOwnersNfts() )
            print(f"Time by NFT: {time.time() - time_by_nft:0.2f} seconds s")
  
        print(f"Total time taken: {time.time() - self.start_time:0.2f} seconds s")
        self.driver.quit()


    def createOrCleanDatabase(self):
        # Clean if exist the table
        if os.path.exists('owners-nfts.db'):
            con = sqlite3.connect('owners-nfts.db')
            cursorObj = con.cursor()
            cursorObj.execute('SELECT MAX(id) FROM nft')
            last_one_id = cursorObj.fetchone()[0]
            if last_one_id < self.number_of_assets:
                self.last_id = last_one_id + 1
            else:
                cursorObj.execute('DELETE FROM nft')

        else:
            con = sqlite3.connect('owners-nfts.db')
            cursorObj = con.cursor()
            cursorObj.execute("CREATE TABLE nft(id integer PRIMARY KEY, nickname text, url text, contract_address text, number text, fold text, class_type text, background text, item_1 text, item_2 text, bug numeric)")

        con.commit()
        con.close()

    def getOwnersNfts(self):
        # empty nft information
        nft_information = []

        owner_nickname = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a/span')))

        owner_url = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a')))

        # Because we have nfts with no properties (bug), we need to make another validation
        items_summary = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div')))
        position_of_last_element = len(items_summary)

        nft_contract_address = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[' + str(position_of_last_element) + ']/div/div/div/div/div/div[1]/span/a')))

        nft_number = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[1]/h1')))

        nft_information.append(owner_nickname.text)
        nft_information.append(owner_url.get_attribute('href'))
        nft_information.append(nft_contract_address.get_attribute('href'))
        nft_information.append(nft_number.text)

        if position_of_last_element < 4:
            nft_information.append('')
            nft_information.append('')
            nft_information.append('')
            nft_information.append('')
            nft_information.append('')
            nft_information.append(True)
        else:
            # Properties
            fold = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[1]/div/div[2]')))
            class_type = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[2]/div/div[2]')))
            background = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[3]/div/div[2]')))
            item_1 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[4]/div/div[2]')))
            item_2 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[5]/div/div[2]')))

            # Fill information of NFT
            nft_information.append(fold.text)
            nft_information.append(class_type.text)
            nft_information.append(background.text)
            nft_information.append(item_1.text)
            nft_information.append(item_2.text)
            nft_information.append(False)

        return nft_information


    def insertRowNFT(self, data):
        con = sqlite3.connect('owners-nfts.db')
        cursorObj = con.cursor()
        sql = ''' INSERT INTO nft (nickname, url, contract_address, number, fold, class_type, background, item_1, item_2, bug) VALUES(?,?,?,?,?,?,?,?,?,?) '''
        cursorObj.execute(sql, data)
        con.commit()
        con.close()


if __name__ == '__main__':
    start_time = time.time()
    number_of_assets = 2514
    app = App(number_of_assets, start_time)
# -*- coding: utf-8 -*-
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class App:
    def __init__(self, number_of_assets = 0):
        self.owners_nfts = {}
        self.number_of_assets = number_of_assets
        # To remove the pop up notification window
        options = Options()
        options.binary_location = 'C:\Program Files\Mozilla Firefox\\firefox.exe'
        options.set_preference("dom.webnotifications.enabled", False)
        # geckodriver allows you to use emojis, chromedriver does not
        self.driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)
        self.driver.maximize_window()

        for asset in range(1, self.number_of_assets):
            self.driver.get('https://opensea.io/assets/matic/0x6172974acedb93a0121b2a7b68b8acea0918be8c/' + str(asset))
            self.getOwnersNfts()
            break

        self.writeJsonData()
        sleep(2)
        #self.driver.quit()


    def getOwnersNfts(self):
        owner_nickname = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a/span')))

        owner_url = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div[1]/div/a')))

        nft_contract_address = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[4]/div/div/div/div/div/div[1]/span/a')))

        nft_number = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div/div[1]/div/div[1]/div[2]/section[1]/h1')))

        # Properties
        fold = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[1]/div/div[2]')))
        class_type = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[2]/div/div[2]')))
        background = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[3]/div/div[2]')))
        item_1 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[4]/div/div[2]')))
        item_2 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div/div/div[1]/div/div[1]/div[1]/section/div/div[2]/div/div/div/div/a[5]/div/div[2]')))

        if owner_nickname.text in self.owners_nfts:
            self.owners_nfts[owner_nickname.text]['count_nfts'] += 1
            self.owners_nfts[owner_nickname.text]['nfts'].append({
                'nft_number': nft_number.text,
                'nft_contract_address': nft_contract_address.get_attribute('href'),
                'fold': fold.text,
                'class_type': class_type.text,
                'background': background.text,
                'item_1': item_1.text,
                'item_2': item_2.text
            })
        else:
            self.owners_nfts[owner_nickname.text] = {
                'owner_url': owner_url.get_attribute('href'),
                'count_nfts': 1,
                'nfts': [ 
                    {
                        'nft_number': nft_number.text,
                        'nft_contract_address': nft_contract_address.get_attribute('href'),
                        'fold': fold.text,
                        'class_type': class_type.text,
                        'background': background.text,
                        'item_1': item_1.text,
                        'item_2': item_2.text
                    }
                ]
            }

    def writeJsonData(self):
        with open('owners-nfts.json', 'w') as outfile:
            json.dump(self.owners_nfts, outfile, indent=4)


if __name__ == '__main__':
    number_of_assets = 2514
    app = App(number_of_assets)
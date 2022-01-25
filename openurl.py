import os
clear = lambda: os.system('cls')
pipselenium = lambda: os.system('pip install selenium')
pipselenium()
from selenium import webdriver
clear()
from time import sleep
clear()
from colorama import Fore
clear()
from selenium.webdriver.common.by import By
clear()
from selenium.webdriver.support import expected_conditions as EC
clear()
from selenium.webdriver.support.ui import WebDriverWait
clear()
from selenium.common.exceptions import TimeoutException
clear()
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
clear()
import pyfiglet
clear()

ascii_banner = pyfiglet.figlet_format("Scraper --")
print(Fore.YELLOW + ascii_banner)
# print(Fore.RED + 'Change Vpn : ' + Fore.YELLOW + proxy)  

options = webdriver.ChromeOptions()
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
#options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--silent")
# options.add_argument('--proxy-server=%s' % proxy)
options.add_argument("--incognito")
options.set_capability('pageLoadStrategy', 'none')
driver = webdriver.Chrome('chromedriver.exe', options=options)
url = 'http://www.tfca.gob.mx/es/TFCA/Boletin_Laboral'
driver.get(url)

        
        
       
      
       
            
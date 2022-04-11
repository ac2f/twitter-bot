from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import time
import os
class TwitterBot:
    def __init__(self, credentialsFilePath:str, usernamesFilePath:str):
        self.credentialsFilePath:str = credentialsFilePath;
        self.usernamesFilePath:str = usernamesFilePath;
        if (any(not os.path.exists(i) for i in [credentialsFilePath, usernamesFilePath])):
            raise FileNotFoundError("Dosya bulunamadı! Lütfen girdiğiniz dosya konumlarını kontrol ediniz..");
        self.driverOptions = Options();
        self.driverOptions.add_argument("--headless");
        self.drivers:list = [];
        self.actions = [];
        self.xpathMap = {
            "usernameEntry": "//input[@autocomplete=\"username\"]",
            "loginPageNext0": "//div[@role=\"button\"][2]//span//span",
            "passwordEntry": "//input[@autocomplete=\"current-password\"]",
            "loginPageNext1": "//div[@role=\"button\"]//span//span",
            "wrongPassword": "//span[text()=\"Wrong password!\"]",
            "lastPostsTextXpath": "//div[@dir=\"auto\" and contains(@id, \"id__avi\")]/span",
            "lastPostsRetweetButton": "//div[contains(@style, \"position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;\")][2]//div[@data-testid=\"retweet\"]",
            "lastPostsRetweetConfirm": "//div[@data-testid=\"retweetConfirm\"]",
            "lastPostsLikeButton": "//div[contains(@style, \"position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;\")][2]//div[@data-testid=\"like\"]"
        };

    def initAndLoginToWebdrivers(self):
        print(f"Tarayıcılar başlatılıyor ve giriş yapılıyor..");
        for credential in self.readCredentialsAsList():
            username, password = credential[0], credential[1];
            print(f"\n[+] Giriş yapılacak:  {username}:{password}");
            driver = webdriver.Firefox(executable_path="../bin/geckodriver.exe", options=self.driverOptions);
            print(f"[+] Tarayıcı başlatıldı! Siteye yönlendiriliyor..");
            driver.get("https://twitter.com/i/flow/login");
            print(f"[+] Siteye yönlendirildi! Bilgiler giriliyor..");
            driver.implicitly_wait(1);
            driver.find_element_by_xpath(self.xpathMap["usernameEntry"]).send_keys(username);
            driver.find_element_by_xpath(self.xpathMap["loginPageNext0"]).click();
            print("[+] 1");
            driver.implicitly_wait(1);
            driver.find_element_by_xpath(self.xpathMap["passwordEntry"]).send_keys(password);
            driver.find_element_by_xpath(self.xpathMap["loginPageNext1"]).click();
            print("[+] 1");
            try:
                driver.find_element_by_xpath(self.xpathMap["wrongPassword"]);
                print(f"[-] \"{username}\" için şifre yanlış!");
            except:
                self.drivers.append({
                    "username": username,
                    "password": password,
                    "driver": driver
                });
            input("Lütfen giriş yaptıysanız devam etmek için <ENTER> tuşuna basın");
            

    def getElapsedSeconds(self, c:int|float) -> int:
        return int(time() - c);

    def loop(self):
        while True:
            for action, counter in zip(self.actions, range(len(self.actions))):
                if (self.getElapsedSeconds(action["lastPostCheck"])>300):
                    self.drivers[0]["driver"].get(f"https://twitter.com/{action['username']}");
                    time.sleep(5);
                    lastPostText = self.drivers[0]["driver"].find_element_by_xpath(self.xpathMap["lastPostsTextXpath"]).text;
                    if (action["lastPost"] != lastPostText):
                        self.doAction(action["username"]);
                        action["lastAction"] = time();
                    action["lastPost"] = lastPostText;
                    action["lastPostCheck"] = time();
                    self.actions[counter] = action;

    def doAction(self, username:str):
        for driver, counter in zip(self.drivers, range(len(self.drivers))):
            print(f"Sayfa yükleniyor.. https://twitter.com/{username}");
            driver.get(f"https://twitter.com/{username}");
            print("Sayfanın yüklenmesi bekleniyor..");
            time.sleep(5);
            print("Sayfa yüklendi!");
            if (counter % 10 == 0):
                # TODO: sarı 
                print("10 driver işlem yaptı. Kısıtlamalardan korunmak için 10 dakika bekleniyor..");
                time.sleep(600);
                print("Bekleme süresi bitti!");
            print(f"Retweet atılıyor..")
            driver.find_element_by_xpath(self.xpathMap["lastPostsRetweetButton"]).click();
            driver.find_element_by_xpath(self.xpathMap["lastPostsRetweetConfirm"]).click();
            print(f"Like atılıyor..")
            driver.find_element_by_xpath(self.xpathMap["lastPostsLikeButton"]).click();

    def readCredentialsAsList(self) -> list:
        print(f"Giriş bilgileri yükleniyor..")
        data = [];
        with open(self.credentialsFilePath, 'r+') as f:
            for credentials, counter in zip(f.readlines(), range(len(f.readlines()))):
                creds = credentials.split(':');
                if (len(creds)==2):
                    data.append(creds);
                    print(f"[{len(f.readlines())}/{counter}] Giriş bilgisi yüklendi! ")
            if (len(data)<len(f.readlines())):
                print(f"Tüm kullanıcılar yüklenemedi! Kullanıcı adları ve şifre arasında \":\" karakteri bulunduğundan ve şifrede \":\" bulunmadığından emin olun!");
        return data;
    
    def readUsernamesAsList(self) -> list:
        print("Ayarlar yükleniyor..")
        data = [];
        with open(self.usernamesFilePath, 'r+') as f:
            for username in f.readlines():
                 self.actions.append({
                    "username": username,
                    "lastPost": "",
                    "lastPostCheck": 0,
                    "lastAction": 0,
                    "actionsDone": False,
                 })
                 print(f"{username} için ayarlar yüklendi!");

def main():
    print("Program başlatılıyor..");
    TB = TwitterBot("input/girisbilgileri.txt", "input/hedefkullanicilar.txt");
    print("Program belleğe dahil edildi.. Çalıştırılıyor.. S: 1");
    TB.initAndLoginToWebdrivers();
    print("Program çalıştırılıyor.. S: 2")
    TB.loop();

if __name__ == "__main__":
    main();
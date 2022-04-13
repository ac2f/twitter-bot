from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import time, sleep
import os
os.environ["LANG"] = "en_US.UTF-8";
class TwitterBot:
    def __init__(self, credentialsFilePath:str, usernamesFilePath:str):
        self.credentialsFilePath:str = credentialsFilePath;
        self.usernamesFilePath:str = usernamesFilePath;
        if (any(not os.path.exists(i) for i in [credentialsFilePath, usernamesFilePath])):
            raise FileNotFoundError("Dosya bulunamadı! Lütfen girdiğiniz dosya konumlarını kontrol ediniz..");
        self.driverOptions = Options();
        self.drivers:list = [];
        self.actions = [];
        self.xpathMap = {
            "usernameEntry": "//input[@autocomplete=\"username\"]",
            "loginPageNext0": "//div[@role=\"button\"][2]//span//span",
            "passwordEntry": "//input[@autocomplete=\"current-password\"]",
            "loginPageNext1": "//div[@role=\"button\"]//span//span",
            "wrongPassword": '//span[text()="Wrong password!" or contains(text(), "Yanlış")]',
            "lastPostsTextXpath": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][1]/div/div/article[@data-testid="tweet"]//div[@dir="auto" and contains(@id, "id__")][1]',
            "lastPostsRetweetButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][1]/div/div/article[@data-testid="tweet"]//div[@data-testid="retweet"]',
            "lastPostsUnRetweetButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][1]/div/div/article[@data-testid="tweet"]//div[@data-testid="unretweet"]',
            "lastPostsRetweetConfirm": '//div[@data-testid="retweetConfirm"]',
            "lastPostsLikeButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][1]/div/div/article[@data-testid="tweet"]//div[@data-testid="like"]',
            "lastPostsUnLikeButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][1]/div/div/article[@data-testid="tweet"]//div[@data-testid="unlike"]'
        };
        self.readUsernamesAsList();

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
            while True:
                try:
                    driver.find_element_by_xpath(self.xpathMap["passwordEntry"]).send_keys(password);
                    driver.find_element_by_xpath(self.xpathMap["loginPageNext1"]).click();
                    print("[+] 1");
                    break;
                except:
                    input("Şifre girerken bir hata ile karşılaşıldı! Lütfen şifre girme bölümüne geldikten sonra <ENTER> tuşuna basın.");
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
        print("Döngü başlatılıyor..");
        while True:
            for action, counter in zip(self.actions, range(len(self.actions))):
                print("Kullanıcının son kontrol zamanı kontrol ediliyor..");
                if (self.getElapsedSeconds(action["lastPostCheck"])>300):
                    print(f"Gecikme süresi tamamlandı! \"{action['username']}\" adlı kullanıcının son gönderisi kontrol ediliyor..");
                    self.drivers[0]["driver"].get(f"https://twitter.com/{action['username']}");
                    print();
                    sleep(5);
                    break_ = False;
                    while not break_:
                        try:
                            lastPostText = self.drivers[0]["driver"].find_element_by_xpath(self.xpathMap["lastPostsTextXpath"]).text;
                            break_ = True;
                        except :
                            print(f"{action['username']} adlı kullanıcının son gönderisi okunurken hata ile karşılaşıldı! Tekrar deneniyor..");
                            sleep(3);
                    if (action["lastPost"] != lastPostText):
                        print("Kullanıcı son kontroldan sonra yeni bir gönderide bulundu! Kontrol zamanları güncelleniyor ve işlemler başlatılıyor..");
                        self.doAction(action["username"]);
                        action["lastAction"] = time();
                    action["lastPost"] = lastPostText;
                    action["lastPostCheck"] = time();
                    self.actions[counter] = action;
                sleep(5);

    def doAction(self, username:str):
        for driver, counter in zip(self.drivers, range(len(self.drivers))):
            driver = driver["driver"];
            print(f"Sayfa yükleniyor.. https://twitter.com/{username}");
            driver.get(f"https://twitter.com/{username}");
            print("Sayfanın yüklenmesi bekleniyor..");
            sleep(5);
            print("Sayfa yüklendi!");
           
            if (counter > 10 and counter % 10 == 0):
                # TODO: sarı 
                print("10 kullanıcı tarafından işlem yapıldı. Kısıtlamalardan korunmak için 10 dakika bekleniyor..");
                sleep(600);
                print("Bekleme süresi bitti! Devam ediliyor..");
            while True:
                try:
                    try:
                        driver.find_element_by_xpath(self.xpathMap["lastPostsUnRetweetButton"]);
                        print("Zaten retweet atılmış! Devam ediliyor..")
                    except:
                        print(f"Retweet atılıyor..");
                        driver.find_element_by_xpath(self.xpathMap["lastPostsRetweetButton"]).click();
                        driver.find_element_by_xpath(self.xpathMap["lastPostsRetweetConfirm"]).click();
                    try:
                        driver.find_element_by_xpath(self.xpathMap["lastPostsUnLikeButton"]);
                        print("Zaten like atılmış! Devam ediliyor..")
                    except:
                        print(f"Like atılıyor..")
                        driver.find_element_by_xpath(self.xpathMap["lastPostsLikeButton"]).click();
                    break;
                except Exception as e:
                    xpath:str = str(e).split("> obscures it")[0].split("=")[-1];
                    try:
                        driver.find_element_by_xpath("//div[@class="+xpath+"]/div[2]/div[1]//span").click();
                    except :
                        pass
                sleep(1);
                    

    def readCredentialsAsList(self) -> list:
        print(f"Giriş bilgileri yükleniyor..")
        data = [];
        with open(self.credentialsFilePath, 'r+') as f:
            allCredentials = f.readlines();
            for credentials, counter in zip(allCredentials, range(len(allCredentials))):
                creds = credentials.split(':');
                if (len(creds)==2):
                    data.append(creds);
                    print(f"[{len(allCredentials)}/{counter+1}] Giriş bilgisi yüklendi! ")
                else:
                    print(f"Hatalı giriş bilgisi girildi! Hatalı Satır: {counter+1} (İlk satır = 1 olarak hesaplanmıştır.)");
            if (len(data)<len(allCredentials)):
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
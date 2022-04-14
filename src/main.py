from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from colorama import Fore, init
from time import time, sleep
import os
init(convert=True, autoreset = True);
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
            "postFrame": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]',
            "lastPostsTextXpath": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]//div[@dir="auto" and contains(@id, "id__")][1]',
            "lastPostsRetweetButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]//div[@data-testid="retweet"]',
            "lastPostsUnRetweetButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]//div[@data-testid="unretweet"]',
            "lastPostsRetweetConfirm": '//div[@data-testid="retweetConfirm"]',
            "lastPostsLikeButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]//div[@data-testid="like"]',
            "lastPostsUnLikeButton": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]//div[@data-testid="unlike"]'
        };
        self.readUsernamesAsList();

    def initAndLoginToWebdrivers(self):
        print(f"{Fore.LIGHTGREEN_EX}[+] Tarayıcılar başlatılıyor ve giriş yapılıyor..");
        for credential in self.readCredentialsAsList():
            username, password = credential[0], credential[1];
            print(f"\n{Fore.LIGHTYELLOW_EX}[!] Giriş yapılacak:  {username}:{password}");
            driver = webdriver.Firefox(executable_path="../bin/geckodriver.exe", options=self.driverOptions);
            print(f"{Fore.LIGHTGREEN_EX}[+] Tarayıcı başlatıldı! Siteye yönlendiriliyor..");
            while True:
                
                driver.get("https://twitter.com/i/flow/login");
                print(f"{Fore.LIGHTGREEN_EX}[+] Siteye yönlendirildi! Bilgiler giriliyor..");
                driver.implicitly_wait(1);
                try:
                    driver.find_element_by_xpath(self.xpathMap["usernameEntry"]).send_keys(username);
                    driver.find_element_by_xpath(self.xpathMap["loginPageNext0"]).click();
                    
                except :
                    print(f"{Fore.LIGHTMAGENTA_EX}[!] Sayfa doğru yüklenemedi gibi gözüküyor. Yeniden deneniyor..");
                    sleep(5);
                    continue;
                print(f"{Fore.LIGHTGREEN_EX}[+] 1");
                driver.implicitly_wait(1);
                while True:
                    try:
                        driver.find_element_by_xpath(self.xpathMap["passwordEntry"]).send_keys(password);
                        driver.find_element_by_xpath(self.xpathMap["loginPageNext1"]).click();
                        print(f"{Fore.LIGHTGREEN_EX}[+] 1");
                        break;
                    except:
                        input(f"{Fore.LIGHTMAGENTA_EX}[!] Şifre girerken bir hata ile karşılaşıldı! Lütfen şifre girme bölümüne geldikten sonra <ENTER> tuşuna basın.");
                try:
                    driver.find_element_by_xpath(self.xpathMap["wrongPassword"]);
                    print(f"{Fore.LIGHTMAGENTA_EX}[-] \"{username}\" için şifre yanlış!");
                except:
                    self.drivers.append({
                        "username": username,
                        "password": password,
                        "driver": driver
                    });
                print(f"{Fore.LIGHTBLUE_EX}[?] Lütfen giriş yaptıysanız devam etmek için {Fore.LIGHTGREEN_EX}<ENTER>{Fore.LIGHTBLUE_EX} tuşuna basın.", end="\r");
                input();
                break;
            

    def getElapsedSeconds(self, c:int|float) -> int:
        return int(time() - c);

    def loop(self):
        print(f"{Fore.LIGHTGREEN_EX}[+] Döngü başlatılıyor..");
        while True:
            for action, counter in zip(self.actions, range(len(self.actions))):
                print(f"{Fore.LIGHTGREEN_EX}[+] İşlemler başlatılıyor..");
                self.doAction(action["username"]);
                sleep(3);

                ###   İPTAL
                #
                # print(f"{Fore.LIGHTYELLOW_EX}[!] Son kontrol zamanı kontrol ediliyor..");
                # if (self.getElapsedSeconds(action["lastPostCheck"])>300):
                #     print(f"{Fore.LIGHTGREEN_EX}[+] Gecikme süresi tamamlandı! \"{action['username']}\" adlı kullanıcının son gönderisi kontrol ediliyor..");
                #     self.drivers[0]["driver"].get(f"https://twitter.com/{action['username']}");
                #     print();
                #     sleep(5);
                #     break_ = False;
                #     while not break_:
                #         try:
                #             lastPostText = self.drivers[0]["driver"].find_element_by_xpath(self.xpathMap["lastPostsTextXpath"]).text;
                #             break_ = True;
                #         except :
                #             print(f"{Fore.LIGHTMAGENTA_EX}[-] {action['username']} adlı kullanıcının son gönderisi okunurken hata ile karşılaşıldı! Tekrar deneniyor..");
                #             sleep(3);
                #     if (action["lastPost"] != lastPostText):
                #         print(f"{Fore.LIGHTCYAN_EX}[+] Kullanıcı son kontroldan sonra yeni bir gönderide bulundu! Kontrol zamanları güncelleniyor ve işlemler başlatılıyor..");
                #         self.doAction(action["username"]);
                #         action["lastAction"] = time();
                #     action["lastPost"] = lastPostText;
                #     action["lastPostCheck"] = time();
                #     self.actions[counter] = action;
                #
                ###   İPTAL

            print(f"{Fore.LIGHTCYAN_EX}[!] İşlemler tamamlandı! Program kapatılıyor..");
            break;   ### PROGRAMI ÇALIŞTIRIR VE BİTTİĞİNDE KAPATIR
            # print(f"{Fore.LIGHTCYAN_EX}[!] İşlemler tamamlandı! Bir sonraki kontrol için 360 saniye bekleniyor..");
            # sleep(360);

    def doAction(self, username:str):
        for driver, counter in zip(self.drivers, range(len(self.drivers))):
            driver = driver["driver"];
            print(f"{Fore.LIGHTGREEN_EX}[!] Sayfa yükleniyor.. https://twitter.com/{username}");
            driver.get(f"https://twitter.com/{username}");
            print(f"{Fore.LIGHTYELLOW_EX}[!] Sayfanın yüklenmesi bekleniyor..");
            sleep(5);
            print(f"{Fore.LIGHTGREEN_EX}[+] Sayfa yüklendi!");
           
            if (counter > 10 and counter % 10 == 0):
                print(f"{Fore.LIGHTRED_EX}[!] 10 kullanıcı tarafından işlem yapıldı. Kısıtlamalardan korunmak için 10 dakika bekleniyor..");
                sleep(600);
                print(f"{Fore.LIGHTGREEN_EX}[+] Bekleme süresi bitti! Devam ediliyor..");
            break_:bool = False;
            while not break_:
                
                counter:int = 1;
                max:int = 6;
                while counter<=max:
                    tmpXpath = {i:self.xpathMap[i].format(counter) for i in self.xpathMap};
                    counter+=1;
                    try:
                        driver.find_element_by_xpath(tmpXpath["postFrame"]);
                    except NoSuchElementException:
                        max += 1;
                        continue;
                    try:
                        try:
                            driver.find_element_by_xpath(tmpXpath["lastPostsUnRetweetButton"]);
                            print(f"{Fore.LIGHTMAGENTA_EX}[-] Zaten retweet atılmış! Devam ediliyor..");
                            break_ = True;
                        except (NoSuchElementException) as e:
                            print("e");
                            print(f"{Fore.LIGHTYELLOW_EX}[!] Retweet atılıyor..");
                            loopRT:bool = True;
                            while loopRT:
                                try:
                                    print(f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsRetweetButton']}");
                                    driver.find_element_by_xpath(tmpXpath["lastPostsRetweetButton"]).click();
                                    print(f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsRetweetConfirm']}");
                                    driver.find_element_by_xpath(tmpXpath["lastPostsRetweetConfirm"]).click();
                                    loopRT = False;
                                except NoSuchElementException:
                                    driver.get(f"https://twitter.com/{username}");
                        try:
                            driver.find_element_by_xpath(tmpXpath["lastPostsUnLikeButton"]);
                            print(f"{Fore.LIGHTMAGENTA_EX}[-] Zaten like atılmış! Program bitiriliyor..");
                            break_ = True;
                        except (NoSuchElementException):
                            print(f"{Fore.LIGHTYELLOW_EX}[!] Like atılıyor..");
                            print(f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsLikeButton']}");
                            driver.find_element_by_xpath(tmpXpath["lastPostsLikeButton"]).click();
                        raiseErr:bool = False;
                        try:
                            driver.find_element_by_xpath(tmpXpath["lastPostsUnLikeButton"]);
                        except :
                            raiseErr = True;
                        try:
                            driver.find_element_by_xpath(tmpXpath["lastPostsUnRetweetButton"]);
                        except:
                            raiseErr = True;
                        if (raiseErr):
                            print(f"[-] Like veya retweet atılırken veya retweet atılırken hata ile karşılaşıldı! Tekrar deneniyor..");
                        if (not raiseErr and break_):
                            break;
                    except ElementClickInterceptedException as e:
                        xpath:str = str(e).split("> obscures it")[0].split("=")[-1];
                        try:
                            driver.find_element_by_xpath("//div[@class="+xpath+"]/div[2]/div[1]//span").click();
                        except :
                            pass
                sleep(1);
                    

    def readCredentialsAsList(self) -> list:
        print(f"{Fore.LIGHTGREEN_EX}[+] Giriş bilgileri yükleniyor..")
        data = [];
        with open(self.credentialsFilePath, 'r+') as f:
            allCredentials = f.readlines();
            for credentials, counter in zip(allCredentials, range(len(allCredentials))):
                creds = credentials.split(':');
                if (len(creds)==2):
                    data.append(creds);
                    print(f"{Fore.LIGHTGREEN_EX}[+] [{len(allCredentials)}/{counter+1}] Giriş bilgisi yüklendi! ")
                else:
                    print(f"{Fore.LIGHTRED_EX}[-] Hatalı giriş bilgisi girildi! Hatalı Satır: {Fore.LIGHTCYAN_EX}{counter+1}{Fore.LIGHTRED_EX} (İlk satır = 1 olarak hesaplanmıştır.)");
            if (len(data)<len(allCredentials)):
                print(f"{Fore.LIGHTRED_EX}[-] Tüm kullanıcılar yüklenemedi! Kullanıcı adları ve şifre arasında \":\" karakteri bulunduğundan ve şifrede \":\" bulunmadığından emin olun!");
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
                 print(f"{Fore.LIGHTGREEN_EX}[+] {username} için ayarlar yüklendi!");

def main():
    print(f"{Fore.LIGHTGREEN_EX}[+] Program başlatılıyor..");
    TB = TwitterBot("input/girisbilgileri.txt", "input/hedefkullanicilar.txt");
    print(f"{Fore.LIGHTGREEN_EX}[+] Program belleğe dahil edildi.. Çalıştırılıyor.. S: 1");
    TB.initAndLoginToWebdrivers();
    print(f"{Fore.LIGHTGREEN_EX}[+] Program çalıştırılıyor.. S: 2")
    TB.loop();
if __name__ == "__main__":
    main();
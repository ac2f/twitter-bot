from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from colorama import Fore, init
from time import time, sleep
import os


MAKSIMUM_RT_HESAP_SAYISI: int = 10
KONTROL_EDILECEK_GONDERI_SAYISI: int = 10

init(convert=True, autoreset=True)
os.environ["LANG"] = "en_US.UTF-8"


class TwitterBot:
    def __init__(self, credentialsFilePath: str, usernamesFilePath: str, proxiesFilePath: str):
        self.credentialsFilePath: str = credentialsFilePath
        self.usernamesFilePath: str = usernamesFilePath
        self.proxiesFilePath: str = proxiesFilePath
        if (any(not os.path.exists(i) for i in [credentialsFilePath, usernamesFilePath, proxiesFilePath])):
            raise FileNotFoundError(
                "Dosya bulunamadı! Lütfen girdiğiniz dosya konumlarını kontrol ediniz..")
        self.driverOptions = Options()
        self.drivers:list = []
        self.actions:list = []
        self.proxies:list = []
        self.xpathMap = {
            "usernameEntry": '//input[@autocomplete="username"]',
            "loginPageNext0": "//div[@role=\"button\"][2]//span//span",
            "passwordEntry": "//input[@autocomplete=\"current-password\"]",
            "loginPageNext1": "//div[@role=\"button\"]//span//span",
            "wrongPassword": '//span[text()="Wrong password!" or contains(text(), "Yanlış")]',
            "postFrame": '//div[contains(@style, "; position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;")][{0}]/div/div/article[@data-testid="tweet"]',
            "retweetConfirmButton": '//div[@data-testid="retweetConfirm"]',
            "postRetweetButton": '//div[@data-testid="retweet"]',
            "postLikeButton": '//div[@data-testid="like"]',
            "logoutConfirm": '//div[1]/div[1]/span/span'
        }
        self.readProxiesAsList();
        self.readUsernamesAsList();

    def initAndLoginToWebdrivers(self):
        print(
            f"{Fore.LIGHTGREEN_EX}[+] Tarayıcılar başlatılıyor ve giriş yapılıyor..")
        credentials = self.readCredentialsAsList();
        for credential, counter in zip(credentials, range(len(credentials))):
            self.driverOptions = Options()
            # self.driverOptions.add_argument('--proxy-server=%s' % self.proxies[counter] if len(self.proxies) < counter else self.proxies[0])
            driver = webdriver.Firefox(
                executable_path="../bin/geckodriver.exe", options=self.driverOptions)
            loginUsername, password = credential[0], credential[1]
            print(
                f"\n{Fore.LIGHTYELLOW_EX}[!] Giriş yapılacak:  {loginUsername}:{password}")
            print(
                f"{Fore.LIGHTGREEN_EX}[+] Tarayıcı başlatıldı! Siteye yönlendiriliyor..")
            while True:
                driver.get("https://twitter.com/i/flow/login")
                print(
                    f"{Fore.LIGHTGREEN_EX}[+] Siteye yönlendirildi! Bilgiler giriliyor..")
                usernameEntered = False;
                driver.implicitly_wait(3)
                
                try:
                    driver.find_element(
                            by=By.XPATH,
                            value=self.xpathMap["usernameEntry"]).send_keys(loginUsername)
                    sleep(1);
                    driver.find_element(
                            by=By.XPATH,
                            value=self.xpathMap["loginPageNext0"]).click()
                    print(
                        f"{Fore.LIGHTGREEN_EX}[+] Kullanıcı adı girildi! Şifre giriliyor..")
                    usernameEntered = True;
                except Exception as e:
                    print(e)
                    print(
                        f"{Fore.LIGHTMAGENTA_EX}[!] Sayfa doğru yüklenemedi gibi gözüküyor. Bu sorun kullanıcı adı girme bölümünün uyumsuz şekilde yüklenmesinden kaynaklıdır ve birkaç deneme sonunda devam edecektir. Yeniden deneniyor..")
                    sleep(5)
                    continue
                sleep(3);
                breakWhenLoopEnd = False;
                while True:
                    try:
                        driver.find_element(
                            by=By.XPATH,
                            value=self.xpathMap["passwordEntry"]).send_keys(password)
                        driver.find_element(
                            by=By.XPATH,
                            value=self.xpathMap["loginPageNext1"]).click()
                        print(
                            f"{Fore.LIGHTGREEN_EX}[+] Şifre girildi! Yönlendiriliyor..")
                        break
                    except:
                        if (usernameEntered):
                            print(f"{Fore.LIGHTRED_EX}[!] Kullanıcı adı bulunamadı gibi gözüküyor! Atlanıyor..");
                            breakWhenLoopEnd = True;
                            break;
                        print(
                            f"{Fore.LIGHTMAGENTA_EX}[!] Şifre girerken bir hata ile karşılaşıldı! Lütfen şifre girme bölümüne geldikten sonra <ENTER> tuşuna basın.")
                        input()
                        break
                if (breakWhenLoopEnd):
                    break;
                try:
                    driver.find_element(
                            by=By.XPATH,
                            value=self.xpathMap["wrongPassword"])
                    print(
                        f"{Fore.LIGHTMAGENTA_EX}[-] \"{loginUsername}\" için şifre yanlış!")
                except:
                    pass
                    # self.drivers.append({
                    #     "username": loginUsername,
                    #     "password": password,
                    #     "driver": driver
                    # })
                homePageLoaded:bool = False;
                restricted:bool = False;
                print(f"{Fore.LIGHTBLUE_EX}[*] Ana sayfanın(https://twitter.com/home) yüklenmesi bekleniyor.. ");
                while not homePageLoaded:
                    if(driver.current_url.endswith("/account/access")):
                        restricted = True;
                        print(f"{Fore.LIGHTRED_EX}[-] Hesap kısıtlama yemiş gibi gözüküyor! Atlanıyor..");
                        break
                    homePageLoaded = driver.current_url.endswith("/home");
                if (restricted):
                    break;
                print(f"{Fore.LIGHTBLUE_EX}[+] Başarıyla giriş yapıldı! Devam ediliyor..");
                sleep(5);

                for action, counterAction in zip(self.actions, range(len(self.actions))):
                    username = str(action["username"]).strip().replace("\n", "")
                    if (len(username)<3):
                        continue;
                    print(
                        f"{Fore.LIGHTGREEN_EX}[!] Sayfa yükleniyor.. https://twitter.com/{username}")
                    driver.get(f"https://twitter.com/{username}")
                    print(f"{Fore.LIGHTYELLOW_EX}[!] Sayfanın yüklenmesi bekleniyor..")
                    sleep(5)
                    print(f"{Fore.LIGHTGREEN_EX}[+] Sayfa yüklendi!")
                    maxPosts = KONTROL_EDILECEK_GONDERI_SAYISI;
                    counterPost: int = 1
                    errCounter:int = 0;
                    while counterPost <= maxPosts:
                        tmpXpath: dict = {i: self.xpathMap[i].format(
                            counterPost) for i in self.xpathMap}
                        counterPost += 1
                        if (not self.checkElementExists(driver, '//span[contains(text(), "Profile")]') and not self.checkElementExists(driver, '//span[contains(text(), "Profil")]')):
                            driver.get(f"https://twitter.com/{username}")
                            sleep(3)
                        buttonLike = self.checkElementExists(
                            driver, tmpXpath["postLikeButton"])
                        buttonRetweet = self.checkElementExists(
                            driver, tmpXpath["postRetweetButton"])
                        if (not (buttonLike and buttonRetweet)):
                            print(f"Gönderi bulunamadı! ", end="\r")
                            if (errCounter > 3):
                                print(f"Tekrar deneniyor ({errCounter}/{3-errCounter})..")
                                counterPost -= 1;
                                errCounter += 1;
                                continue;
                            maxPosts = 0;
                            continue
                        try:
                            if (buttonLike):
                                buttonLike.click()
                                print(
                                    f"{Fore.LIGHTGREEN_EX}[+] Başarıyla like atıldı! Devam ediliyor..")
                            if (buttonRetweet and (counter < MAKSIMUM_RT_HESAP_SAYISI)):
                                buttonRetweet.click();
                                print(tmpXpath)
                                self.checkElementExists(driver, tmpXpath["retweetConfirmButton"]).click();
                                print(
                                    f"{Fore.LIGHTGREEN_EX}[+] Başarıyla retweet atıldı! Devam ediliyor..")
                        except ElementClickInterceptedException as e:
                            counterPost -= 1
                            xpath: str = str(e).split("> obscures it")[
                                0].split("=")[-1]
                            try:
                                driver.find_element_by_xpath(
                                    "//div[@class="+xpath+"]/div[2]/div[1]//span").click()
                            except:
                                pass
                # TODO: tarayıcıya çıkış yaptır
                # driver.get("https://twitter.com/logout");
                # sleep(3);
                # logoutConfirm = self.checkElementExists(driver, self.xpathMap["logoutConfirm"]);
                # if (logoutConfirm):
                #     logoutConfirm.click();
                #     print(f"{Fore.LIGHTMAGENTA_EX}[!] Başarıyla çıkış yapıldı! Eğer sırada hesap var ise giriş yapılacak.");
                #     sleep(3);
                # else:
                #     print(f"{Fore.LIGHTRED_EX}[!] Çıkış yaparken bir hata ile karşılaşıldı! Lütfen manuel olarak çıkış yapıp <ENTER> tuşuna basınız..");
                #     input();
                # sleep(3);
                # break;
                
                
                
                
                
                # if (not driver.current_url.endswith("/home")):
                #     print(
                #         f"{Fore.LIGHTBLUE_EX}[?] Lütfen giriş yaptıysanız devam etmek için {Fore.LIGHTGREEN_EX}<ENTER>{Fore.LIGHTBLUE_EX} tuşuna basın.", end="\r")
                #     input()
                # else:
                #     print(
                #         f"{Fore.LIGHTGREEN_EX}[+] Başarıyla giriş yapıldı! Devam ediliyor..")
                # break

    def getElapsedSeconds(self, c: int | float) -> int:
        return int(time() - c)

    def loop(self):
        print(f"{Fore.LIGHTGREEN_EX}[+] Döngü başlatılıyor..")
        while True:
            for action, counter in zip(self.actions, range(len(self.actions))):
                print(f"{Fore.LIGHTGREEN_EX}[+] İşlemler başlatılıyor..")
                self.doAction(
                    str(action["username"]).strip().replace("\n", ""))

            print(
                f"{Fore.LIGHTCYAN_EX}[!] İşlemler tamamlandı! Program kapatılıyor..")
            for driver in self.drivers:
                driver["driver"].close();
            break  # PROGRAMI ÇALIŞTIRIR VE BİTTİĞİNDE KAPATIR
                # İPTAL
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
                # İPTAL
            # print(f"{Fore.LIGHTCYAN_EX}[!] İşlemler tamamlandı! Bir sonraki kontrol için 360 saniye bekleniyor..");
            # sleep(360);

    def checkElementExists(self, driver: webdriver.Firefox, xpath: str):
        try:
            return driver.find_element(by=By.XPATH, value=xpath)
        except (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException):
            return False

    def doAction(self, username: str):
                
        return
        for driver, counter in zip(self.drivers, range(len(self.drivers))):
            driver = driver["driver"]
            print(
                f"{Fore.LIGHTGREEN_EX}[!] Sayfa yükleniyor.. https://twitter.com/{username}")
            # input_completed: bool = False
            # while not input_completed:
            #     print(
            #         f"{Fore.LIGHTBLUE_EX}[?] Kontrol etmek istediğiniz gönderi sayısını giriniz: ")
            #     try:
            #         maxPosts: int = int(input())
            #     except ValueError:
            #         maxPosts = 1000
            #     if (maxPosts < 2 or maxPosts > 999):
            #         print(
            #             f"{Fore.LIGHTRED_EX}[-] Hatalı veri girişi! Lütfen 2 ve 999 arasında bir sayı seçiniz..")
            #         continue
            #     break
            driver.get(f"https://twitter.com/{username}")
            print(f"{Fore.LIGHTYELLOW_EX}[!] Sayfanın yüklenmesi bekleniyor..")
            sleep(5)
            print(f"{Fore.LIGHTGREEN_EX}[+] Sayfa yüklendi!")
            maxPosts = KONTROL_EDILECEK_GONDERI_SAYISI;
            counterPost: int = 1
            while counterPost <= maxPosts:
                tmpXpath: dict = {i: self.xpathMap[i].format(
                    counterPost) for i in self.xpathMap}
                counterPost += 1
                if (not self.checkElementExists(driver, '//span[contains(text(), "Profile")]') and not self.checkElementExists(driver, '//span[contains(text(), "Profil")]')):
                    driver.get(f"https://twitter.com/{username}")
                    sleep(3)
                buttonLike = self.checkElementExists(
                    driver, tmpXpath["postLikeButton"])
                buttonRetweet = self.checkElementExists(
                    driver, tmpXpath["postRetweetButton"])
                if (not (buttonLike and buttonRetweet)):
                    print(f"Gönderi bulunamadı! Bitiriliyor..")
                    maxPosts = 0
                    continue
                try:
                    if (buttonLike):
                        buttonLike.click()
                        print(
                            f"{Fore.LIGHTGREEN_EX}[+] Başarıyla like atıldı! Devam ediliyor..")
                    if (buttonRetweet and (counter < MAKSIMUM_RT_HESAP_SAYISI)):
                        buttonRetweet.click();
                        print(tmpXpath)
                        self.checkElementExists(driver, tmpXpath["retweetConfirmButton"]).click();
                        print(
                            f"{Fore.LIGHTGREEN_EX}[+] Başarıyla retweet atıldı! Devam ediliyor..")
                except ElementClickInterceptedException as e:
                    counterPost -= 1
                    xpath: str = str(e).split("> obscures it")[
                        0].split("=")[-1]
                    try:
                        driver.find_element_by_xpath(
                            "//div[@class="+xpath+"]/div[2]/div[1]//span").click()
                    except:
                        pass

            # counterPostINDEX:int = 1;
            # counterPost:int = 1;
            # firstErrRaiseIndex:int = 0;
            # while counterPost <= maxPosts:
            #     # driver.execute_script(f"window.scrollTo(0, {250 * counterPost});");
            #     if (counterPost > 16): break;
            #     tmpXpath = {i:self.xpathMap[i].format(counterPostINDEX) for i in self.xpathMap};
            #     counterPostINDEX += 1;
            #     counterPost += 1;
            #     done:dict = {"like": -1, "retweet": -1};
            #     if (not self.checkElementExists(driver, '//span[contains(text(), "Profile")]') and not self.checkElementExists(driver, '//span[contains(text(), "Profil")]')):
            #         driver.get(f"https://twitter.com/{username}");
            #         sleep(3);
            #     loopFinish = False;
            #     while not loopFinish:
            #         buttonLike = self.checkElementExists(driver, tmpXpath["postLikeButton"]);
            #         # buttonUnLike = self.checkElementExists(driver, tmpXpath["postUnLikeButton"]);
            #         buttonRetweet = self.checkElementExists(driver, tmpXpath["postRetweetButton"]);
            #         # buttonUnRetweet = self.checkElementExists(driver, tmpXpath["postUnRetweetButton"]);
            #         try:
            #             if(not (buttonLike or self.checkElementExists(driver, tmpXpath["postUnLikeButton"]))):
            #                 maxPosts += 1;
            #                 print(f"[-]{counterPost}/{maxPosts}   -  {counterPostINDEX} Index değerine ait bir gönderi bulunamadı! Devam ediliyor..");
            #                 loopFinish = True;
            #                 continue;
            #             if (buttonLike != False):
            #                 buttonLike.click();
            #                 done["like"] = 1;
            #                 print(f"{Fore.LIGHTGREEN_EX}[+] {counterPost}/{maxPosts}   -  {counterPostINDEX}Başarıyla like atıldı! Devam ediliyor..");
            #             else:
            #                 done["like"] = 0;
            #                 print(f"{Fore.LIGHTMAGENTA_EX}[-] {counterPost}/{maxPosts}   -  {counterPostINDEX}Bu gönderiye zaten like atılmış! Devam ediliyor..");
            #             if (buttonRetweet != False and (counter < MAKSIMUM_RT_HESAP_SAYISI)):
            #                 buttonRetweet.click();
            #                 self.checkElementExists(driver, self.xpathMap["retweetConfirmButton"]).click();
            #                 done["retweet"] = 1;
            #                 print(f"{Fore.LIGHTGREEN_EX}[+] {counterPost}/{maxPosts}   -  {counterPostINDEX}Başarıyla retweet atıldı! Devam ediliyor..");
            #             else:
            #                 done["retweet"] = 0;
            #                 print(f"{Fore.LIGHTMAGENTA_EX}[-] {counterPost}/{maxPosts}   -  {counterPostINDEX}Bu gönderiye zaten retweet atılmış! Devam ediliyor..");
            #             if (done["retweet"] > -1 or done["like"] > -1):
            #                 firstErrRaiseIndex = 0;
            #             if (firstErrRaiseIndex != 0 and counterPost - firstErrRaiseIndex > 8):
            #                 counterPost = maxPosts+1;
            #                 continue;
            #             buttonUnLike = self.checkElementExists(driver, tmpXpath["postUnLikeButton"]);
            #             buttonUnRetweet = self.checkElementExists(driver, tmpXpath["postUnRetweetButton"]);
            #             if (not (buttonUnLike or buttonUnRetweet)):
            #                 continue;
            #             loopFinish = True;
            #         except ElementClickInterceptedException as e:
            #             counterPost -= 1;
            #             xpath:str = str(e).split("> obscures it")[0].split("=")[-1];
            #             try:
            #                 driver.find_element_by_xpath("//div[@class="+xpath+"]/div[2]/div[1]//span").click();
            #             except :
            #                 pass;

                #     try:
                #         driver.find_element_by_xpath(tmpXpath["postUnLikeButton"]);
                #         firstErrRaiseIndex = 0;
                #         done["like"] = 0;
                #     except NoSuchElementException as e:
                #         try:
                #             driver.find_element_by_xpath(tmpXpath["postLikeButton"]);
                #             firstErrRaiseIndex = 0;
                #         except NoSuchElementException:
                #             pass
                #             print(f"{Fore.LIGHTRED_EX}{e}")
                #             print(f"{Fore.LIGHTMAGENTA_EX}[-] Kullanıcının gönderisi bulunamadı! (Bu sorun önerilen kişiler ile gönderilerin aynı değeri taşımasından kaynaklıdır. Birkaç deneme sonra sorunsuz devam edecektir)");
                #             maxPosts += 1;
                #             counterPost2-=1;
                #             if (firstErrRaiseIndex==0):
                #                 firstErrRaiseIndex = counterPost2;
                #             elif (counterPost2 - firstErrRaiseIndex > 8):
                #                 break;
                #             continue;
                # except ElementClickInterceptedException as e:
                #     driver.get(f"https://twitter.com/{username}");
                #     counterPost -= 1;
                #     xpath:str = str(e).split("> obscures it")[0].split("=")[-1];
                #     try:
                #         driver.find_element_by_xpath("//div[@class="+xpath+"]/div[2]/div[1]//span").click();
                #     except :
                #         pass;
                #     continue;
                # if (done["like"]==0):
                #     print(f"{Fore.LIGHTMAGENTA_EX}[-] Bu gönderiye zaten like atılmış! Devam ediliyor..");
                # if (counter < MAKSIMUM_RT_HESAP_SAYISI):
                #     try:
                #         driver.find_element_by_xpath(tmpXpath["postRetweetButton"]).click();
                #         driver.find_element_by_xpath(tmpXpath["retweetConfirmButton"]).click();
                #         done["retweet"] = 1;
                #         print(f"{Fore.LIGHTGREEN_EX}[+] Başarıyla retweet atıldı! Devam ediliyor..");
                #     except NoSuchElementException:
                #         try:
                #             driver.find_element_by_xpath(tmpXpath["postUnRetweetButton"])
                #         except NoSuchElementException:
                #             pass
                #     if (done["retweet"] == 0):
                #         print(f"{Fore.LIGHTMAGENTA_EX}[-] Bu gönderiye zaten retweet atılmış! Devam ediliyor..");
                # try:
                #     driver.find_element_by_xpath(tmpXpath["postUnRetweetButton"]);
                #     driver.find_element_by_xpath(tmpXpath["postUnLikeButton"]);
                # except NoSuchElementException:
                #     counterPostINDEX -= 1;
                #     continue;
            print(
                f"{Fore.LIGHTGREEN_EX}[+] {username} için işlemler tamamlandı! Devam ediliyor..")
            sleep(3)

        return
        # for driver, counter in zip(self.drivers, range(len(self.drivers))):
        #     driver = driver["driver"]
        #     print(
        #         f"{Fore.LIGHTGREEN_EX}[!] Sayfa yükleniyor.. https://twitter.com/{username}")
        #     driver.get(f"https://twitter.com/{username}")
        #     print(f"{Fore.LIGHTYELLOW_EX}[!] Sayfanın yüklenmesi bekleniyor..")
        #     sleep(5)
        #     print(f"{Fore.LIGHTGREEN_EX}[+] Sayfa yüklendi!")

        #     if (counter+1 >= 10 and counter+1 % 10 == 0):
        #         print(
        #             f"{Fore.LIGHTRED_EX}[!] 10 kullanıcı tarafından işlem yapıldı. Kısıtlamalardan korunmak için 10 dakika bekleniyor..")
        #         sleep(600)
        #         print(
        #             f"{Fore.LIGHTGREEN_EX}[+] Bekleme süresi bitti! Devam ediliyor..")
        #     break_: bool = False
        #     while not break_:

        #         counter: int = 1
        #         max: int = 40
        #         inputCompleted: bool = False
        #         while not inputCompleted:
        #             try:
        #                 max = int(
        #                     input("Kontrol edilecek maksimum gönderi sayısını giriniz: "))
        #                 inputCompleted = True
        #             except ValueError:
        #                 pass
        #         while counter <= max:
        #             tmpXpath = {i: self.xpathMap[i].format(
        #                 counter) for i in self.xpathMap}
        #             counter += 1
        #             try:
        #                 driver.find_element_by_xpath(tmpXpath["postFrame"])
        #             except NoSuchElementException:
        #                 max += 1
        #                 continue
        #             try:
        #                 if (MAKSIMUM_RT_HESAP_SAYISI > counter + 1):
        #                     try:
        #                         driver.find_element_by_xpath(
        #                             tmpXpath["lastPostsUnRetweetButton"])
        #                         print(
        #                             f"{Fore.LIGHTMAGENTA_EX}[-] Zaten retweet atılmış! Devam ediliyor..")
        #                         break_ = True
        #                     except (NoSuchElementException) as e:
        #                         print(
        #                             f"{Fore.LIGHTYELLOW_EX}[!] Retweet atılıyor..")
        #                         loopRT: bool = True
        #                         while loopRT:
        #                             try:
        #                                 print(
        #                                     f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsRetweetButton']}")
        #                                 driver.find_element_by_xpath(
        #                                     tmpXpath["lastPostsRetweetButton"]).click()
        #                                 print(
        #                                     f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsRetweetConfirm']}")
        #                                 driver.find_element_by_xpath(
        #                                     tmpXpath["lastPostsRetweetConfirm"]).click()
        #                                 print(
        #                                     f"{Fore.LIGHTGREEN_EX}[+] Retweet atıldı! ")
        #                                 loopRT = False
        #                             except NoSuchElementException:
        #                                 driver.get(
        #                                     f"https://twitter.com/{username}")
        #                 try:
        #                     driver.find_element_by_xpath(
        #                         tmpXpath["lastPostsUnLikeButton"])
        #                     print(
        #                         f"{Fore.LIGHTMAGENTA_EX}[-] Zaten like atılmış! Program bitiriliyor..")
        #                     break_ = True
        #                 except (NoSuchElementException):
        #                     print(f"{Fore.LIGHTYELLOW_EX}[!] Like atılıyor..")
        #                     print(
        #                         f"{Fore.LIGHTBLUE_EX} {tmpXpath['lastPostsLikeButton']}")
        #                     driver.find_element_by_xpath(
        #                         tmpXpath["lastPostsLikeButton"]).click()
        #                 raiseErr: bool = False
        #                 try:
        #                     driver.find_element_by_xpath(
        #                         tmpXpath["lastPostsUnLikeButton"])
        #                 except:
        #                     raiseErr = True
        #                 try:
        #                     driver.find_element_by_xpath(
        #                         tmpXpath["lastPostsUnRetweetButton"])
        #                 except:
        #                     raiseErr = True
        #                 if (raiseErr):
        #                     print(
        #                         f"[-] Like veya retweet atılırken veya retweet atılırken hata ile karşılaşıldı! Tekrar deneniyor..")
        #                 # if (not raiseErr and break_):
        #                 #     break;
        #             except ElementClickInterceptedException as e:
        #                 xpath: str = str(e).split("> obscures it")[
        #                     0].split("=")[-1]
        #                 try:
        #                     driver.find_element_by_xpath(
        #                         "//div[@class="+xpath+"]/div[2]/div[1]//span").click()
        #                 except:
        #                     pass
        #         sleep(1)

    def readCredentialsAsList(self) -> list:
        print(f"{Fore.LIGHTGREEN_EX}[+] Giriş bilgileri yükleniyor..")
        data = []
        with open(self.credentialsFilePath, 'r+') as f:
            allCredentials = f.readlines()
            for credentials, counter in zip(allCredentials, range(len(allCredentials))):
                creds = credentials.split(':')
                if (len(creds) == 2):
                    data.append(creds)
                    print(
                        f"{Fore.LIGHTGREEN_EX}[+] [{len(allCredentials)}/{counter+1}] Giriş bilgisi yüklendi! ")
                else:
                    print(
                        f"{Fore.LIGHTRED_EX}[-] Hatalı giriş bilgisi girildi! Hatalı Satır: {Fore.LIGHTCYAN_EX}{counter+1}{Fore.LIGHTRED_EX} (İlk satır = 1 olarak hesaplanmıştır.)")
            if (len(data) < len(allCredentials)):
                print(
                    f"{Fore.LIGHTRED_EX}[-] Tüm kullanıcılar yüklenemedi! Kullanıcı adları ve şifre arasında \":\" karakteri bulunduğundan ve şifrede \":\" bulunmadığından emin olun!")
        return data

    def readUsernamesAsList(self) -> list:
        print("Ayarlar yükleniyor..")
        with open(self.usernamesFilePath, 'r+') as f:
            for username in f.readlines():
                self.actions.append({
                    "username": username,
                    "lastPost": "",
                    "lastPostCheck": 0,
                    "lastAction": 0,
                    "actionsDone": False,
                })
                print(
                    f"{Fore.LIGHTGREEN_EX}[+] {username} için ayarlar yüklendi!")

    def readProxiesAsList(self) -> list:
        print("Proxyler yükleniyor..")
        with open(self.proxiesFilePath, 'r+') as f:
            for proxy in f.readlines():
                self.proxies.append(proxy)
                print(
                    f"{Fore.LIGHTGREEN_EX}[+] Proxy adresi \"{proxy}\" yüklendi!");

def main():
    print(f"{Fore.LIGHTGREEN_EX}[+] Program başlatılıyor..")
    TB = TwitterBot("input/girisbilgileri.txt", "input/hedefkullanicilar.txt", "input/proxies.txt");
    print(
        f"{Fore.LIGHTGREEN_EX}[+] Program belleğe dahil edildi.. Çalıştırılıyor.. S: 1")
    TB.initAndLoginToWebdrivers()
    print(f"{Fore.LIGHTGREEN_EX}[+] Program işlemleri tamamladı!")
    # print(f"{Fore.LIGHTGREEN_EX}[+] Program çalıştırılıyor.. S: 2")
    # TB.loop()


if __name__ == "__main__":
    main()

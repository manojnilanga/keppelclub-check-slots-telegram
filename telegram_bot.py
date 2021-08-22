from threading import Thread
import telebot
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

API_key = "telegrambotapikeygoeshere"

id = "lx96470"
pw = "171185az"
sleeping_time = 120

#----------------------------------


bot =telebot.TeleBot(API_key)
message_chat_id = ""
notify = False
checking = True
last_availability_data =[]
def start_checking():
    while(True):
        if(message_chat_id!="" and checking):
            print("Start checking ..")
            login_url = "https://www.keppelclub.com.sg/MemberLogin"

            options = Options()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")
            options.add_argument("--proxy-server='direct://'")
            options.add_argument("--proxy-bypass-list=*")
            options.add_argument("--start-maximized")
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-infobars')
            options.add_argument('--no-sandbox')
            options.add_argument('--ignore-certificate-errors')
            driver = webdriver.Chrome(options=options)
            # driver = webdriver.Chrome()

            try:
                driver.get(login_url)
                driver.maximize_window()

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_member_frame"]')))
                driver.switch_to.frame("ctl00_ContentPlaceHolder1_member_frame")

                # login
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="member_id"]')))
                ele_email = driver.find_element_by_xpath('//*[@id="member_id"]')
                ele_email.send_keys(id)
                ele_pw = driver.find_element_by_xpath('//*[@id="member_password"]')
                ele_pw.send_keys(pw)
                time.sleep(1)
                ele_pw.send_keys(Keys.ENTER)
            except:
                time.sleep(20)
                continue

            # cancel current session
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div/a[2]')))
                driver.find_element_by_xpath('/html/body/form/div/a[2]').click()
            except:
                pass

            try:
                # golf booking in menu
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sidebar-mobile"]/div[2]/div[3]/a/span[3]')))
                driver.find_element_by_xpath('//*[@id="sidebar-mobile"]/div[2]/div[3]/a/span[3]').click()

                # checking open close in table
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="fixheader-table"]/tbody/tr[1]/td[2]/a/span')))
            except:
                time.sleep(20)
                continue

            row = 0
            availability_data = []
            while (True):
                try:
                    row += 1
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="fixheader-table"]/tbody/tr[' + str(row) + ']/td[2]/a/span')))
                    close_or_open = driver.find_element_by_xpath(
                        '//*[@id="fixheader-table"]/tbody/tr[' + str(row) + ']/td[2]/a/span').text
                    # if(close_or_open=="OPEN" or close_or_open=="CLOSED"):
                    if (close_or_open == "OPEN"):
                        for i in range(1, 5):
                            val = driver.find_element_by_xpath(
                                '//*[@id="fixheader-table"]/tbody/tr[' + str(row) + ']/td[3]/table/tbody/tr/td[' + str(
                                    i) + ']').text
                            if (val != "0"):
                                date_val = driver.find_element_by_xpath(
                                    '//*[@id="fixheader-table"]/tbody/tr[' + str(row) + ']/td[1]').text
                                driver.find_element_by_xpath(
                                    '//*[@id="fixheader-table"]/tbody/tr[' + str(row) + ']/td[2]/a/span').click()
                                # checking for ball matchup
                                session_row = 2
                                time_val = ""
                                while (True):
                                    try:
                                        session_row += 1
                                        if (session_row % 2 == 1):
                                            col_num = 2
                                        else:
                                            col_num = 3

                                        ball_matchup_or_not = driver.find_element_by_xpath(
                                            '//*[@id="ctl00_maincontent"]/div/div/div[2]/form/div/div[1]/div[3]/div[' + str(
                                                session_row) + ']/div[' + str(col_num) + ']/div/span').text
                                        if (ball_matchup_or_not == "Ball Matchup"):
                                            time_val = driver.find_element_by_xpath(
                                                '//*[@id="ctl00_maincontent"]/div/div/div[2]/form/div/div[1]/div[3]/div[' + str(
                                                    session_row) + ']/div[1]/div/span').text
                                            break
                                    except:
                                        break
                                if (time_val != ""):
                                    availability_data.append(date_val + "$" + time_val)
                                # driver.back()
                                driver.execute_script("window.history.go(-1)")
                                break
                except:
                    break

            print(availability_data)
            global last_availability_data
            last_availability_data = availability_data[:]
            driver.close()
            if(len(availability_data)==0 and notify):
                bot.send_message(message_chat_id, "Checked, but no OPEN slots")
            full_message =""
            for i in range(0,len(availability_data)):
                full_message+=str(i+1)+" --> "+availability_data[i].replace("$"," ")+"\n"

            if (len(availability_data) != 0):
                bot.send_message(message_chat_id, full_message)

        time.sleep(sleeping_time)

def book_slot(picked_slot):
    try:
        print("Booking thread")
        print(picked_slot)
        try:
            picked_date, picked_time = last_availability_data[picked_slot - 1].split("$")
        except:
            bot.send_message(message_chat_id, "Wrong booking slot")

        login_url = "https://www.keppelclub.com.sg/MemberLogin"

        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        book_driver = webdriver.Chrome(options=options)
        # book_driver = webdriver.Chrome()

        book_driver.get(login_url)
        book_driver.maximize_window()

        WebDriverWait(book_driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_member_frame"]')))
        book_driver.switch_to.frame("ctl00_ContentPlaceHolder1_member_frame")

        # login
        WebDriverWait(book_driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="member_id"]')))
        ele_email = book_driver.find_element_by_xpath('//*[@id="member_id"]')
        ele_email.send_keys(id)
        ele_pw = book_driver.find_element_by_xpath('//*[@id="member_password"]')
        ele_pw.send_keys(pw)
        time.sleep(1)
        ele_pw.send_keys(Keys.ENTER)

        # cancel current session
        try:
            WebDriverWait(book_driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div/a[2]')))
            book_driver.find_element_by_xpath('/html/body/form/div/a[2]').click()
        except:
            pass

        # golf booking in menu
        WebDriverWait(book_driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="sidebar-mobile"]/div[2]/div[3]/a/span[3]')))
        book_driver.find_element_by_xpath('//*[@id="sidebar-mobile"]/div[2]/div[3]/a/span[3]').click()

        # checking open close in table
        WebDriverWait(book_driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="fixheader-table"]/tbody/tr[1]/td[2]/a/span')))

        new_row = 0
        while (True):
            try:
                checked_inside_date = False
                new_row += 1
                print("row: " + str(new_row))
                new_date_val = book_driver.find_element_by_xpath(
                    '//*[@id="fixheader-table"]/tbody/tr[' + str(new_row) + ']/td[1]').text
                if (new_date_val == picked_date):
                    checked_inside_date = True
                    book_driver.find_element_by_xpath(
                        '//*[@id="fixheader-table"]/tbody/tr[' + str(new_row) + ']/td[2]/a/span').click()

                    new_session_row = 2

                    while (True):
                        try:
                            new_session_row += 1
                            print("new_session_row: "+str(new_session_row))
                            if (new_session_row % 2 == 1):
                                new_col_num = 2
                            else:
                                new_col_num = 3
                            new_time_val = book_driver.find_element_by_xpath(
                                '//*[@id="ctl00_maincontent"]/div/div/div[2]/form/div/div[1]/div[3]/div[' + str(
                                    new_session_row) + ']/div[1]/div/span').text
                            print("new_time_val: "+new_time_val)
                            print("picked_time: "+picked_time)
                            if (new_time_val == picked_time):
                                print("False")
                                book_driver.find_element_by_xpath(
                                    '//*[@id="ctl00_maincontent"]/div/div/div[2]/form/div/div[1]/div[3]/div[' + str(
                                        new_session_row) + ']/div[' + str(new_col_num) + ']/div/span/input').click()
                                print("clicked here")
                                print(new_session_row)
                                print(new_col_num)
                                # booking confirm button
                                WebDriverWait(book_driver, 15).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="btnSubmitid"]')))
                                print("waited successfully")
                                book_driver.find_element_by_xpath('//*[@id="btnSubmitid"]').click()
                                print("clicked on button submit")
                                print(message_chat_id)
                                bot.send_message(message_chat_id, "Successfully booked")

                                print("Successfully booked")
                                break
                        except:
                            print("Not booked successfully")
                            bot.send_message(message_chat_id, "Not booked successfully")
                            break

                if (checked_inside_date):
                    break

            except:
                break
        book_driver.close()
    except:
        print("booking function error")
        bot.send_message(message_chat_id, "booking function error")


@bot.message_handler(commands=["book"])
def book(message):
    try:
        book_number = int(message.text.split()[1:][0])
        t_book = Thread(target=book_slot, args=(book_number,))
        t_book.start()
    except:
        bot.reply_to(message, "Wrong format")



@bot.message_handler(commands=["test"])
def test(message):
    print("testing ..")
    print(message_chat_id)
    bot.reply_to(message, "bot working fine !")

@bot.message_handler(commands=["start-check"])
def start_check(message):
    global message_chat_id
    global checking
    message_chat_id = message.chat.id
    print(message_chat_id)
    checking =True
    bot.send_message(message.chat.id, "Start checking available slots")

@bot.message_handler(commands=["stop-check"])
def stop_check(message):
    global checking
    checking = False
    bot.send_message(message.chat.id, "Stop checking available slots")

@bot.message_handler(commands=["notify"])
def func_notify(message):
    global notify
    notify = True
    bot.send_message(message.chat.id, "Bot will notify the result in every search")

@bot.message_handler(commands=["donot-notify"])
def donot_notify(message):
    global notify
    notify = False
    bot.send_message(message.chat.id, "Bot will notify only if there is a OPEN slot")



t = Thread(target=start_checking)
t.start()
bot.polling()


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import Global_var
from Insert_On_Datbase import insert_in_Local,create_filename
import sys, os
import ctypes
import string
import requests
import urllib.request
import urllib.parse
import re
import html
import wx
app = wx.App()

browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
browser.maximize_window()
browser.get("http://sppra.co.sz/tender.html")
time.sleep(5)
    
def Scrap_data():
    a = True
    while a == True:
        try:
            td_count = 1
            for Deadline in browser.find_elements_by_xpath('//*[@id="tenderView"]/ul/li/div/div/div/div[2]/ul/li[1]'):
                browser.execute_script("arguments[0].scrollIntoView();", Deadline) 
                time.sleep(1)
                deadline_text = ''
                Deadline = Deadline.get_attribute('innerText').strip()
                deadline_text = Deadline.partition('End Date:')[2].strip()
                
                SegFeild = []
                for data in range(45):
                    SegFeild.append('')
                
                if deadline_text != '':
                    datetime_object = datetime.strptime(deadline_text, "%d-%m-%Y %H:%M")
                    mydate = datetime_object.strftime("%Y-%m-%d")
                    SegFeild[24] = mydate

                for Title in browser.find_elements_by_xpath(f'//*[@id="tenderView"]/ul/li[{str(td_count)}]/div/div/h4'): 
                    Title = Title.get_attribute('innerText').strip()
                    Title = string.capwords(str(Title))
                    SegFeild[19] = Title
                    break
                for Tender_id in browser.find_elements_by_xpath(f'//*[@id="tenderView"]/ul/li[{str(td_count)}]/div/div/div/div[1]/ul/li[1]'): 
                    Tender_id = Tender_id.get_attribute('innerText').strip()
                    Tender_id = Tender_id.partition('Tender No:')[2].strip()
                    SegFeild[13] = Tender_id
                    break
                for Purchaser in browser.find_elements_by_xpath(f'//*[@id="tenderView"]/ul/li[{str(td_count)}]/div/div/div/div[1]/ul/li[2]'): 
                    Purchaser = Purchaser.get_attribute('innerText').strip()
                    Purchaser = Purchaser.partition('Tenderer:')[2].upper().strip()
                    SegFeild[12] = Purchaser
                    break
                Tender_document = ''
                for Tender_document in browser.find_elements_by_xpath(f'//*[@id="tenderView"]/ul/li[{str(td_count)}]/div/div/div/div[2]/ul/li[2]/a'): 
                    Tender_document = Tender_document.get_attribute('href').strip()
                    break
                Tenderer = SegFeild[12]
                Tenderer = string.capwords(str(Tenderer))
                SegFeild[19] = f"{str(SegFeild[19])}<br>\nTenderer: {str(Tenderer)}<br>\nEnd Date: {str(SegFeild[24])}"
                SegFeild[7] = 'SZ'
                SegFeild[14] = '2'
                SegFeild[22] = "0"
                SegFeild[26] = "0.0"
                SegFeild[27] = "0"   # Financier
                SegFeild[28] = 'http://sppra.co.sz/tender.html'
                SegFeild[20] = ""
                SegFeild[21] = ""
                SegFeild[42] = SegFeild[7]
                SegFeild[43] = ""
                SegFeild[31] = 'sppra.co.sz'
                for SegIndex in range(len(SegFeild)):
                    print(SegIndex, end=' ')
                    print(SegFeild[SegIndex])
                    SegFeild[SegIndex] = html.unescape(str(SegFeild[SegIndex]))
                    SegFeild[SegIndex] = str(SegFeild[SegIndex]).replace("'", "''")
                if len(SegFeild[19]) >= 200:
                    SegFeild[19] = str(SegFeild[19])[:200]+'...'

                if len(SegFeild[18]) >= 1500:
                    SegFeild[18] = str(SegFeild[18])[:1500]+'...'
                check_date(Tender_document, SegFeild)
                Global_var.Total += 1
                print(" Total: " + str(Global_var.Total) + " Duplicate: " + str(Global_var.duplicate) + " Expired: " + str(Global_var.expired) + " Inserted: " + str(Global_var.inserted) + " Skipped: " + str(Global_var.skipped) + " Deadline Not given: " + str(Global_var.deadline_Not_given) + " QC Tenders: " + str(Global_var.QC_Tender),"\n")
                td_count += 1
            for next_page in browser.find_elements_by_xpath('//*[@id="mainContent"]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/ul/li/a'):
                next_page_href = next_page.get_attribute('href')
                next_page_text = next_page.get_attribute('innerText').replace(' ','').strip()
                if next_page_text == '»':
                    browser.get(next_page_href)
                    break
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n", exc_tb.tb_lineno)
            a = True
    ctypes.windll.user32.MessageBoxW(0, "Total: " + str(Global_var.Total) + "\n""Duplicate: " + str(Global_var.duplicate) + "\n""Expired: " + str(Global_var.expired) + "\n""Inserted: " + str(Global_var.inserted) + "\n""Skipped: " + str(Global_var.skipped) + "\n""Deadline Not given: " + str(Global_var.deadline_Not_given) + "\n""QC Tenders: " + str(Global_var.QC_Tender) + "","sppra.co.sz", 1)
    browser.quit()
    sys.exit()


def check_date(Tender_document, SegFeild):
    deadline = str(SegFeild[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            if day > 0:
                insert_in_Local(Tender_document, SegFeild)
            else:
                print("Expired Tender")
                Global_var.expired += 1
                ctypes.windll.user32.MessageBoxW(0, "Total: " + str(Global_var.Total) + "\n""Duplicate: " + str(Global_var.duplicate) + "\n""Expired: " + str(Global_var.expired) + "\n""Inserted: " + str(Global_var.inserted) + "\n""Skipped: " + str(Global_var.skipped) + "\n""Deadline Not given: " + str(Global_var.deadline_Not_given) + "\n""QC Tenders: " + str(Global_var.QC_Tender) + "","sppra.co.sz", 1)
                browser.quit()
                sys.exit()
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)

Scrap_data()
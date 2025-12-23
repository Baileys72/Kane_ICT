#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Fox_Hou
#
# Created:     17/07/2021
# Copyright:   (c) Fox_Hou 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import logging
import tkinter as tk
import configparser
import sfisapi
#import setting

logging.basicConfig(level=logging.DEBUG)

class LoginForm(tk.Canvas):
    def __init__(self):
        self.mainform = tk.Tk()
        self.mainform.title('SFIS')
        self.mainform.resizable(0, 0)
        self.mainform.configure()

        self.screen_info(self.mainform)
        w = 500
        h = 240
        x = int((self.screen_width - w) / 2)
        y = int((self.screen_height - w) / 2)
        self.mainform.geometry('{}x{}+{}+{}'.format(w, h, x, y))

        self.top_frame = tk.Frame(self.mainform, bg='gray99')
        self.top_frame.pack(fill=tk.BOTH, expand=True)
        self.bottom_frame = tk.Frame(self.mainform, bg='gray99')
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)

        lbl_id = tk.Label(self.top_frame, text='ID:', anchor='w', relief='flat', bg='gray99', font=("arial", 24))
        lbl_id.pack(side=tk.LEFT, fill=tk.X, padx=5)

        self.employee_id = tk.StringVar()
        entry_id = tk.Entry(self.top_frame, textvariable=self.employee_id, relief='flat', bg='gray88', font=("arial", 24))
        entry_id.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X, padx=5)
        entry_id.bind('<Return>', self.event_btn_login)
        entry_id.bind("<KeyRelease>", self.event_entry_caps)
        entry_id.focus_set()

        self.vi_btn = tk.Button(self.bottom_frame, text='Login', relief='groove', font=("arial", 16), command=self.click_btn_login)
        self.vi_btn.pack()

        self.txt_msg = tk.Text(self.bottom_frame, height=3, relief='flat', bg='gray99', font=("arial", 8))
        self.txt_msg.pack()
        self.OP_ID = '123'
        self.is_login = False
        WEB_URL=self.find_value_in_setting('setting.ini', 'WEB_URL')
        device_id=self.find_value_in_setting('setting.ini', 'DEVICE')
        STATION_NAME=self.find_value_in_setting('setting.ini', 'STATION_NAME')
        #SFIS=self.find_value_in_setting('setting.xlsx', 'SFIS')
        self.sfis = sfisapi.SFISApi(WEB_URL, device_id, STATION_NAME)
        #self.sfis = sfisapi.SFISApi(setting.WEB_URL, device_id, setting.STATION_NAME)

        self.mainform.mainloop()

    def find_value_in_setting(self, file_path, value):
        config = configparser.ConfigParser()
        config.read(file_path, encoding='utf-8')
        #df = pd.read_excel(file_path, header=None)
        try:
            # 尝试获取WEB_URL的值
            QQ = config.get('Settings', value)
            # 打印WEB_URL的值
            #print(web_url)
        except configparser.NoOptionError:
            QQ = '123'

        return QQ

    def screen_info(self, parent):
        self.screen_width = parent.winfo_screenwidth()
        self.screen_height = parent.winfo_screenheight()

    def event_entry_caps(self, event):
        self.employee_id.set(self.employee_id.get().upper())

    def event_btn_login(self, event):
        self.click_btn_login()

    def click_btn_login(self):
        id = self.employee_id.get()
        if len(id) != 0:
            ret = self.sfis.login(id)
            logging.info(ret)
            if ret[0] == '1':
                self.OP_ID = id
                self.is_login = True
                #print(self.OP_ID)
                self.mainform.destroy()
            else:
                self.employee_id.set('')
                self.txt_msg.delete('1.0', tk.END)
                self.txt_msg.insert('1.0', ret[1])
                self.OP_ID = 'offline'
                #print(self.OP_ID)
        #return OP_ID



def main():
    loginform = LoginForm()
    #a=loginform.click_btn_login()
    print(loginform.OP_ID)
    pass

if __name__ == '__main__':
    main()

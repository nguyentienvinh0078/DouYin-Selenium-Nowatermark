from tkinter import *
from tkinter import filedialog
import os
import re
import requests
import json
import time
import sys
from tkinter.ttk import Progressbar, Style
from tkinter import messagebox
from tkinter import simpledialog
from threading import Thread

from test_lib import VingDouyinTiktok


class GUI(VingDouyinTiktok):
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        self.window = Tk()
        self.window.title('™✅ V I N G ✅™')
        self.window.resizable(False, False)
        self.window.configure(bg='#1B9AAA')

        self.entry_folder_name = 'entry_folder'
        self.browser_btn_name = 'Thư mục'
        self.entry_link_name = 'entry_link'
        self.download_btn_name = 'Tải xuống'
        self.message_label_name = 'message_label'
        self.desc_label_name = 'desc_label'
        self.progress_name = 'progress'
        self.close_btn_name = 'Thoát'

        self.layouts = {
            self.entry_folder_name: (1, 1), self.browser_btn_name: (1, 2),
            self.entry_link_name: (2, 1), self.download_btn_name: (2, 2),
            self.message_label_name: (1, 1),
            self.desc_label_name: (1, 1),
            self.progress_name: (1, 1),
            self.close_btn_name: (1, 1),
        }

        self.path_frame = self.create_path_frame()
        self.path_frame.columnconfigure(1, weight=1)
        self.entry_folder = self.create_entry_form(
            self.path_frame, self.entry_folder_name)

        self.root_dir = self.get_app_path()
        self.entry_folder.insert(END, self.root_dir)

        self.browser_btn = self.create_button_form(
            self.path_frame, self.browser_btn_name, self.browser_btn_callback)

        self.download_frame = self.create_download_frame()
        self.path_frame.columnconfigure(1, weight=1)
        self.entry_link = self.create_entry_form(
            self.download_frame, self.entry_link_name)
        self.download_btn = self.create_button_form(
            self.download_frame, self.download_btn_name, self.download_btn_callback)
        self.download_btn_val = 0

        self.progress_frame = self.create_progress_frame()

    def close_btn_callback(self):
        self.download_thread.join()
        self.window.destroy()
        sys.exit(0)

    def browser_btn_callback(self):
        self.folder_save_path = filedialog.askdirectory()
        if self.folder_save_path != '':
            self.entry_folder.delete(0, END)
            self.entry_folder.insert(0, self.folder_save_path)

    def download_btn_callback(self):
        input_url = re.sub("[^\x00-\xff]", '', self.entry_link.get()).replace(' ', '')
        if input_url == '':
            messagebox.showinfo('ERROR', '❤❤❤❤ LINK TRỐNG, HÃY KIỂM TRA LẠI ❤❤❤❤')
        elif 'tiktok.com' in input_url or 'douyin.com' in input_url:
            self.browser_btn.configure(state='disable', bg='lightcoral', fg='white', text='Thư mục')
            self.browser_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Thư mục')
            self.download_btn.configure(state='disable', bg='lightcoral', fg='white', text='Đang tải')
            self.download_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Đang tải')

            if self.download_btn_val >= 1:
                self.message_frame.destroy()
                self.desc_frame.destroy()
                self.progress_frame.destroy()

            self.download_thread = Thread(target=lambda: self.download(input_url))
            self.download_thread.start()
        else:
            messagebox.showinfo('ERROR', '❤❤❤❤ LINK NHẬP KHÔNG CHÍNH XÁC, HÃY KIỂM TRA LẠI ❤❤❤❤')

    def download(self, input_url):
        self.desc_frame = self.create_desc_frame()
        self.message_frame = self.create_message_frame()

        msg = 'Đang lấy dữ liệu video, vui lòng đợi...'
        self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)
        try:
            video_data = self.get_data(input_url)
            check = True
        except:
            check = False
            self.message_frame.destroy()
            messagebox.showinfo('ERROR', '❤❤❤❤ LINK NHẬP KHÔNG CHÍNH XÁC, HÃY KIỂM TRA LẠI ❤❤❤❤')
            
        if check:
            number_of_videos = len(video_data)
            for i in range(number_of_videos):
                save_folder = video_data[i]['save_folder']
                nickname = video_data[i]['nickname']
                video_id = video_data[i]['video_id']
                video_url_no_watermark = video_data[i]['video_url_no_watermark']

                folder_nickname_path = f'{save_folder}\{nickname}'
                filename = f'{video_id}.mp4'
                video_path = f'{folder_nickname_path}\{filename}'

                self.create_folder(folder_nickname_path)
                nickname_path_listdir = os.listdir(folder_nickname_path)

                video_index = i + 1
                msg = f'Video: {video_index} / {number_of_videos}'
                self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)

                desc = 'File: {}'.format(filename)
                self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)
                try:
                    if filename in nickname_path_listdir:
                        desc = f'{filename} \nĐã tồn tại, bỏ qua tải xuống\n Folder: {nickname}'
                        self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)
                        time.sleep(0.15)
                        if number_of_videos == 1:
                            self.download_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Tải xuống')
                            self.download_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Tải xuống')
                        continue
                except Exception as bug:
                    # print(bug)
                    pass

                self.progress_frame.destroy()
                self.progress_frame = self.create_progress_frame()
                retry_download_max = 3
                for again_num in range(retry_download_max):
                    style, progress = self.create_progress(
                        self.progress_frame, self.progress_name)
                    try:
                        start_download_time = time.time()
                        size = 0
                        chunk_size = 1024
                        video = self.request_deal(video_url_no_watermark)
                        content_size = int(video.headers['content-length'])
                        MB_size = round(content_size / chunk_size / 1024, 2)

                        if video.status_code == 200:
                            with open(file=video_path, mode='wb') as file:
                                for data in video.iter_content(chunk_size=chunk_size):
                                    file.write(data)
                                    size = size + len(data)

                                    current_size = round(size/chunk_size/1024, 2)
                                    percentage = round(size/content_size*100)
                                    style.configure('text.Horizontal.TProgressbar', text=f'{percentage:>10}% {MB_size:>10}{"MB":<2}', font='Arial 12 bold')
                                    self.window.update_idletasks()
                                    progress['value'] = percentage
                        break
                    except Exception as bug:
                        print(bug)
                        continue

            self.entry_link.delete(0, END)
            self.entry_link.insert(END, '')
            messagebox.showinfo('ERROR', '❤❤❤❤ TẢI XUỐNG HOÀN TẤT! ❤❤❤❤')

        self.browser_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Thư mục')
        self.browser_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Thư mục')
        self.download_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Tải xuống')
        self.download_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Tải xuống')

        self.download_btn_val = self.download_btn_val + 1

    def create_progress(self, frame, progress_name):
        style = Style(self.window)
        style.layout('text.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                     {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'}),
                     ('Horizontal.Progressbar.label', {'sticky': ''})])

        style.configure('text.Horizontal.TProgressbar',text=f'{0:>10}% {0:>10}{"MB":<2}', font='Arial 12 bold')
        progress = Progressbar(frame, style='text.Horizontal.TProgressbar', value=0)
        row, col = dict(self.layouts.items())[progress_name]
        progress.grid(row=row, column=col, sticky=NSEW, ipady=2)
        frame.columnconfigure(1, weight=1)
        return style, progress

    def create_path_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#1B9AAA')
        return frame

    def create_download_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=1, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#1B9AAA')
        return frame

    def create_message_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=2, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#1B9AAA')
        return frame

    def create_desc_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=3, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#1B9AAA')
        return frame

    def create_progress_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=4, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#1B9AAA')
        return frame

    def create_label_form(self, frame, label_name, message):
        var = StringVar()
        label = Label(frame, textvariable=var,font='Arial 12 bold', borderwidth=0, justify=CENTER)
        label.configure(bg='#1B9AAA', fg='white')
        var.set(message)
        row, col = dict(self.layouts.items())[label_name]
        label.grid(row=row, column=col, sticky=NSEW)
        frame.columnconfigure(1, weight=1)
        return label, var

    def create_entry_form(self, frame, entry_name, wid=50):
        entry = Entry(frame, font='Arial 12 bold', width=wid, borderwidth=1, justify=CENTER)
        row, col = dict(self.layouts.items())[entry_name]
        entry.grid(row=row, column=col, sticky=NSEW)
        return entry

    def create_button_form(self, frame, btn_name, callback_func):
        button = Button(frame, text=btn_name, justify=CENTER, command=callback_func)
        button.configure(borderwidth=1, font='Arial 12 bold', width=10, bg='#06D6A0')
        row, col = dict(self.layouts.items())[btn_name]
        button.grid(row=row, column=col, sticky=NSEW)
        return button

    def run(self):
        self.window.mainloop()


def main():
    try:
        gui = GUI()
        gui.run()
    except Exception as bug:
        messagebox.showinfo('ERROR', '😥😣 BUG 😥😣\n{}'.format(bug))

if __name__ == '__main__':
    main()

import sys
from tkinter import *
from tkinter import filedialog 
import os, re, requests, json, time
from tkinter.ttk import Progressbar, Style
from tkinter import messagebox
from tkinter import simpledialog
from threading import Thread

import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class GUI:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        self.window = Tk()
        self.window.title('DouYin Download -- V I N G')
        self.window.resizable(False, False)
        self.window.configure(bg='black')

        self.entry_folder_name = 'entry_folder';    self.browser_btn_name  = 'Thư mục'
        self.entry_link_name   = 'entry_link';      self.download_btn_name = 'Tải xuống'
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
        self.entry_folder = self.create_entry_form(self.path_frame, self.entry_folder_name)
        # self.root_dir = os.path.abspath(os.path.dirname(__file__))

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            try:
                application_path = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                application_path = os.getcwd()

        self.root_dir = application_path
        self.save_folder = 'Douyin One'
        self.entry_folder.insert(END, self.root_dir)

        self.browser_btn = self.create_button_form(self.path_frame, self.browser_btn_name, self.browser_btn_callback)

        self.download_frame = self.create_download_frame()
        self.path_frame.columnconfigure(1, weight=1)
        self.entry_link = self.create_entry_form(self.download_frame, self.entry_link_name)
        # self.entry_link.insert(END, 'https://v.douyin.com/FUS36nS/')
        # self.entry_link.insert(END, 'https://v.douyin.com/N4FVUj8/')
        self.download_btn = self.create_button_form(self.download_frame, self.download_btn_name, self.download_btn_callback)

        self.message_frame = self.create_message_frame()
        self.desc_frame = self.create_desc_frame()

        self.progress_frame = self.create_progress_frame()

        # self.close_frame = self.create_close_frame()
        # self.close_frame.grid_configure(sticky=E)
        # self.close_btn = self.create_button_form(self.close_frame, self.close_btn_name, self.close_btn_callback)

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
        url_input = re.sub("[^\x00-\xff]", '', self.entry_link.get()).replace(' ', '')
        check_input = False
        if url_input == '':
            messagebox.showinfo('message', '[ Feedback ]: Link trống, hãy  kiểm tra lại!')
        elif 'douyin.com' in url_input:
            check_input = True   
        else:
            messagebox.showinfo('message', '[ Feedback ]: Link nhập không chính xác, hãy kiểm tra lại!')

        if check_input:  
            self.browser_btn.configure(state='disable', bg='lightcoral', fg='white', text='Thư mục')
            self.browser_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Thư mục')
            self.download_btn.configure(state='disable', bg='lightcoral', fg='white', text='Đang tải')
            self.download_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Đang tải')
            # self.close_btn.configure(state='disable', bg='lightcoral', fg='white', text='Thoát')
            # self.close_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Thoát')
            
            self.message_frame.destroy()
            self.desc_frame.destroy()
            self.progress_frame.destroy()

            self.download_thread = Thread(target=lambda:self.download_video(url_input))
            self.download_thread.start()
    
    def init_driver(self, opt='hide'):
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')
        options.add_argument('--start-maximized')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        

        if opt == 'hide':
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
        if opt == 'diswin':
            options.add_argument("--window-position=-10000,0")
        elif opt == 'headless':
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        options.add_experimental_option ("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_settings.popups": 0,
            "download.default_directory": f"{self.root_dir}",
            "directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
        })
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options) 
        return driver

    def get_data(self, url):
        print(f'[ Feedback ]: Bắt đầu lấy dữ liệu video, vui lòng đợi...\r')
        print('-' * 120)
        retry_get_data_max = 3
        for retry_data_number in range(retry_get_data_max):
            try:
                start = time.time()
                self.driver = self.init_driver('headless')
                self.driver.get(url)

                nickname = str(self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div[2]/h1/span/span/span/span/span').text)
                
                driver_opened = time.time() 
                driver_open_time = driver_opened - start

                scroll_pause_time = 1.5 if driver_open_time <= 15 else 2
                last_scroll_height = 0

                if driver_open_time < 2.5:  
                    self.driver.close()
                    self.driver.quit()
                    continue
                elif driver_open_time >= 2.5:
                    while True:
                        new_scroll_height = self.driver.execute_script('return document.body.scrollHeight')
                        if new_scroll_height != last_scroll_height:
                            print('[ Feedback ]: Đang Scroll....')
                            print('-' * 120)
                            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                            time.sleep(scroll_pause_time)
                            last_scroll_height = new_scroll_height

                            end_page = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]/div[2]/div/div')
                            end_text = str(end_page.text)
                            if end_text != '':
                                break
                        else:
                            break
                    print('[ Feedback ]: Scroll xong..!')
                    print('-' * 120)
                    
                    video_data = []
                    video_link_elements = self.driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]/div[2]/ul/li')
                    number_of_videos = len(video_link_elements)
                    jx_url_base = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
                    self.json_file_path = f'{self.folder_save_path}\{nickname}crawl.json'

                    for video_number in range(1, number_of_videos + 1):
                        result_a_tag = self.driver.find_elements_by_xpath(f'/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]/div[2]/ul/li[{video_number}]/a')
                        for a_tag in result_a_tag:
                            video_url = a_tag.get_attribute('href')
                            video_id = re.findall('video/(\d+)?', video_url)[0]
                            video_data.append({
                                'video_number': str(video_number),
                                'video_id': video_id,
                                'video_url': video_url,
                                'video_api': f'{jx_url_base}{video_id}'
                            })
                        with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                            json.dump(video_data, json_file, indent=4, separators=(',', ': '))
                        print("\r" + "[ Feedback ]: Cập nhật {:>2}/{} ".format(video_number, number_of_videos), end='')
                    print('')
                    self.driver.close()
                    self.driver.quit()
                    end = time.time()
                    sub_time = end - start
                    print('-' * 120)
                    print('[ Feedback ]: Lấy dữ liệu thành công -*- {} Video -*- Thời gian: {:.2f} giây...'.format(number_of_videos, sub_time))
                    print('-' * 120)
                    break
            except Exception as bug:
                # print(bug)
                continue
        return video_data

    def is_video_link(self, url_input):
        response = requests.get(url=url_input)
        if '/video/' in url_input or '/video/' in response.url:
            return True
        return False

    def download_video(self, url_input):
        self.desc_frame = self.create_desc_frame()
        self.message_frame = self.create_message_frame()

        self.is_video = self.is_video_link(url_input)
        self.save_folder = 'DouYin One' if self.is_video else 'DouYin  Multi' 
        self.folder_save_path = f'{self.root_dir}\{self.save_folder}'
        
        try:
            if not os.path.exists(self.folder_save_path):
                os.makedirs(self.folder_save_path)
        except Exception as bug:
            print('[ Feedback ]: Không tạo được thư mục!')
            print('-' * 120)
            return

        video_data = []
        if not self.is_video:
            print('[ Feedback ]: Tải xuống nhiều video!')
            print('-' * 120)
            msg = 'Đang lấy dữ liệu video, vui lòng đợi...'
            self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)
            video_data = self.get_data(url_input)
        else:
            print('[ Feedback ]: Tải xuống 1 video!')
            print('-' * 120)
            response = requests.get(url=url_input)
            video_url = response.url
            video_id = re.findall('video\/(\d+)', video_url)[0]
            jx_url_base = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
            video_data = [{
                "video_number": "1",
                "video_id": video_id,
                "video_url": video_url,
                "video_api": f"{jx_url_base}{video_id}",
            }]

        number_of_videos = len(video_data)
        for video_number in range(number_of_videos):
            msg = 'Video: {} / {}'.format(video_number+1, number_of_videos)
            self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)
            
            js = json.loads(requests.get(url=video_data[video_number]['video_api'], headers=self.headers).text)
            try:
                nickname = str(js['item_list'][0]['author']['nickname'])
            except Exception as bug:
                # print(bug)
                # nickname = 'Empty Nickname'
                pass
                # messagebox.showinfo('message', '[ Feedback ]: Không tìm được nickname, đặt thành: Empty Nickname!\r')

            try:
                folder_nickname_path = f'{self.folder_save_path}\{nickname}'
                if not os.path.exists(folder_nickname_path): 
                    os.makedirs(folder_nickname_path)
            except Exception as bug:
                # print(bug)
                # messagebox.showinfo('message', f'[ Feedback ]: Không tạo được thư mục {nickname}!\r')
                return 
            
            try:
                video_url_no_watermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play')
            except Exception as bug:
                #print(bug)
                # messagebox.showinfo('message', '[ Feedback ]: Không lấy được link video không nhãn!\r')
                pass
            
            try:
                create_time = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(js['item_list'][0]['create_time']))
            except Exception as bug:
                #print(bug)
                create_time = 'no_create_time'
                # messagebox.showinfo('message', '[ Feedback ]: Không lấy được thời gian tạo video video!\r')
            
            filename = '{} {}.mp4'.format(create_time, video_data[video_number]['video_id'])
            nickname_path_listdir = os.listdir(folder_nickname_path)
            desc = 'Tên: {}'.format(filename)
            self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)
            try:
                if filename in nickname_path_listdir:
                    desc = 'Tệp đã tồn tại, bỏ qua tải xuống\n Folder: {}\{}'.format(self.save_folder, nickname)
                    self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)
                    
                    # messagebox.showinfo('message', f'[ Download ]: {video_number+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ')
                    print(f'[ Download ]: {video_number+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ', end = "")
                    for i in range(15):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)

                    if number_of_videos == 1:
                        self.download_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Tải xuống')
                        self.download_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Tải xuống')
                    
                    continue    
            except Exception as bug:
                print(bug)
                pass
            
            retry_download_max = 3
            self.progress_frame.destroy()
            self.progress_frame = self.create_progress_frame()
            for retry_number in range(retry_download_max):
                style, progress = self.create_progress(self.progress_frame, self.progress_name)
                try:
                    print(f'\n[   Video    ]: {video_number+1}/{number_of_videos}')
                    print(f'[   Video    ]: Đang tải tệp -- [ {filename} ] --')
                    start_download_time = time.time()
                    size = 0
                    chunk_size = 1024
                    video = requests.get(url=video_url_no_watermark, headers=self.headers)
                    content_size = int(video.headers['content-length'])
                    MB_size = round(content_size / chunk_size / 1024, 2)

                    if video.status_code == 200:
                        video_path = f'{folder_nickname_path}\{filename}'
                        with open(file=video_path, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '[  Download  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')

                                current_size = round(size/chunk_size/1024, 2)
                                percentage=round(size/content_size*100)
                                style.configure('text.Horizontal.TProgressbar', text=f'{percentage:>10}% {MB_size:>10}{"MB":<2}', font='Arial 12 bold')
                                self.window.update_idletasks()
                                progress['value']=percentage

                    end_download_time = time.time()
                    download_time = end_download_time - start_download_time
                    print(f'\n[  Download  ]: Thời gian: {download_time:.2f}s, Kích thước: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    #print(bug)
                    continue
        
        self.entry_link.delete(0, END)
        self.entry_link.insert(END, '')

        self.browser_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Thư mục')
        self.browser_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Thư mục')
        self.download_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Tải xuống')
        self.download_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Tải xuống')
        # self.close_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Thoát')
        # self.close_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Thoát')

        messagebox.showinfo('message', 'Đã tải xuống xong!')


    def create_progress(self, frame, progress_name):
        style = Style(self.window)
        style.layout('text.Horizontal.TProgressbar',
            [('Horizontal.Progressbar.trough',
            {'children': [('Horizontal.Progressbar.pbar',{'side': 'left', 'sticky': 'ns'})],
            'sticky': 'nswe'}),
            ('Horizontal.Progressbar.label', {'sticky': ''})])

        style.configure('text.Horizontal.TProgressbar', text=f'{0:>10}% {0:>10}{"MB":<2}', font='Arial 12 bold')
        progress=Progressbar(frame, style='text.Horizontal.TProgressbar', value=0)
        row, col = dict(self.layouts.items())[progress_name]
        progress.grid(row=row, column=col, sticky=NSEW, ipady=2)
        frame.columnconfigure(1,weight=1)

        return style, progress

    def create_path_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#060716')
        return frame

    def create_download_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=1, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='black')
        return frame

    def create_message_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=2, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#060716')
        return frame
    
    def create_desc_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=3, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#060716')
        return frame

    def create_progress_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=4, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#060716')
        return frame

    def create_close_frame(self):
        frame = LabelFrame(self.window, relief='flat')
        frame.grid(row=5, column=0, padx=2, pady=2, sticky=NSEW)
        frame.configure(bg='#060716')
        return frame

    def create_label_form(self, frame, label_name, message):
        var = StringVar()
        label = Label(frame, textvariable=var, font='Arial 12 bold', borderwidth=0, justify=CENTER)
        label.configure(bg='black', fg='white')
        var.set(message)
        row, col = dict(self.layouts.items())[label_name]
        label.grid(row=row, column=col, sticky=NSEW)
        frame.columnconfigure(1,weight=1)
        return label, var

    def create_entry_form(self, frame, entry_name, wid=50):
        entry = Entry(frame, font='Arial 12 bold', width=wid, borderwidth=1, justify=CENTER)
        row, col = dict(self.layouts.items())[entry_name]
        entry.grid(row=row, column=col, sticky=NSEW)
        return entry

    def create_button_form(self, frame, btn_name, callback_func):
        button = Button(frame, text=btn_name, justify=CENTER, command=callback_func)
        button.configure(borderwidth=1, font='Arial 12 bold', width=10, bg='mediumseagreen')
        row, col = dict(self.layouts.items())[btn_name]
        button.grid(row=row, column=col, sticky=NSEW)
        return button

    def run(self):
        self.window.mainloop()

def main():
    gui = GUI()
    gui.run()

if __name__ == '__main__':
    main()

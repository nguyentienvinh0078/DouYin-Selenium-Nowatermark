import sys
from tkinter import *
from tkinter import filedialog 
import os, re, requests, json, time
from tkinter.ttk import Progressbar, Style
from tkinter import messagebox
from tkinter import simpledialog
from threading import Thread

class GUI:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        self.window = Tk()
        self.window.title('™✅ V I N G ✅™')
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

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            try:
                application_path = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                application_path = os.getcwd()

        self.root_dir = application_path
        self.download_folder = 'Download'
        self.entry_folder.insert(END, self.root_dir)

        self.browser_btn = self.create_button_form(self.path_frame, self.browser_btn_name, self.browser_btn_callback)

        self.download_frame = self.create_download_frame()
        self.path_frame.columnconfigure(1, weight=1)
        self.entry_link = self.create_entry_form(self.download_frame, self.entry_link_name)
        self.download_btn = self.create_button_form(self.download_frame, self.download_btn_name, self.download_btn_callback)

        self.message_frame = self.create_message_frame()
        self.desc_frame = self.create_desc_frame()

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
        input_check = False
        if input_url == '':
            messagebox.showinfo('ERROR', '❤❤❤❤ LINK TRỐNG, HÃY KIỂM TRA LẠI ❤❤❤❤')
        elif 'tiktok.com' in input_url or 'douyin.com' in input_url:
            input_check = True
        else:
            messagebox.showinfo('ERROR', '❤❤❤❤ LINK NHẬP KHÔNG CHÍNH XÁC, HÃY KIỂM TRA LẠI ❤❤❤❤')
            
        if input_check:  
            self.browser_btn.configure(state='disable', bg='lightcoral', fg='white', text='Thư mục')
            self.browser_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Thư mục')
            self.download_btn.configure(state='disable', bg='lightcoral', fg='white', text='Đang tải')
            self.download_btn.configure(state='disable', activebackground='lightcoral', activeforeground='white', text='Đang tải')
            
            self.message_frame.destroy()
            self.desc_frame.destroy()
            self.progress_frame.destroy()

            self.download_thread = Thread(target=lambda:self.download(input_url))
            self.download_thread.start()

    def input_url_check(self, input_url):
        """
            retur 3 params:
            param 1: return app type, DouYin & TikTok
            param 2: return type url, Page Url or Video Url
            param 3: 
                app type = douyin ==> return    sec_id: page url, video_id: video url
                app type = tiktok ==> return user_name: page url, video_id: video url
        """
        for again_num in range(3):
            try:
                response = requests.get(
                    url = input_url,
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'},
                    timeout = 15
                )
                real_url = response.url
                break
            except Exception as bug:
                print(bug)
                continue

        if 'www.douyin.com' in real_url:
            if '/user/' in real_url:
                if 'modal_id' not in real_url:
                    real_url = real_url.split('?')[0]
                    return ['DouYin', 'Multiple', re.findall('/user/(.*)', real_url)[0]]
                else:
                    return ['DouYin', 'Video', re.findall('\?modal_id=(\d+)', real_url)[0]]
            elif '/video/' in real_url:
                return ['DouYin', 'Video', re.findall('/video/(\d+)', real_url)[0]]
        elif 'www.tiktok.com' in real_url:
            real_url = real_url.split('?')[0]
            if '/video/' not in real_url:
                return ['TikTok', 'Multiple', re.findall('\@(.*)', real_url)[0]]
            else:
                return ['TikTok', 'Video', re.findall('/video/(\d+)', real_url)[0]]

    def request_deal(self, url, max_again=3):
        for req_again in range(max_again):
            try:
                return requests.get(
                    url = url,
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'},
                    timeout = 15
                )
            except Exception as bug:
                print(bug)
                continue

    def get_data(self, app_type, data_key):
        min_cursor, max_cursor = '0', '0'
        video_data = []
        done = False
        if 'TikTok' in app_type:
            api_user_id = "https://t.tiktok.com/node/share/user/@{}?aid=1988".format(data_key)
            user_data = self.request_deal(api_user_id).json()
            try:
                user_id = str(user_data["userInfo"]["user"]["id"])
            except:
                user_id = str(user_data['seoProps']['pageId'])

            while not done:
                data_url = 'https://www.tiktok.com/share/item/list?id={:s}&type=1&count=100&maxCursor={:s}&minCursor={:s}'.format(user_id, max_cursor, min_cursor)
                response = self.request_deal(data_url)
                if response.status_code == 200:
                    js = response.json()

                    item_list_data = js['body']['itemListData']
                    max_cursor = js['body']['maxCursor']
                    done = not js['body']['hasMore']
                    
                    for item in item_list_data:
                        video_id = str(item['itemInfos']['id'])
                        user_name = str(item['authorInfos']['uniqueId'])
                        video_urls = 'https://www.tiktok.com/@{}/video/{}'.format(user_name, video_id)
                        tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
                        video_data.append({
                            'video_id': video_id,
                            'video_url': video_urls,
                            'video_api': tiktok_api_link,
                        })
        elif 'DouYin' in app_type:
            sec_uid = data_key
            while not done:
                data_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={:s}&count=30&max_cursor={:s}&min_cursor={:s}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='.format(sec_uid, max_cursor, min_cursor)
                response = self.request_deal(data_url)
                if response.status_code == 200:
                    js = response.json()
        
                    item_list_data = js['aweme_list']
                    max_cursor = str(js['max_cursor'])
                    done = not js['has_more']
                    
                    for item in item_list_data:
                        video_id = str(item['aweme_id'])
                        video_url = 'https://www.douyin.com/video/{}'.format(video_id)
                        douyin_api_link = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(video_id)
                        video_data.append({
                            'video_id': video_id,
                            'video_url': video_url,
                            'video_api': douyin_api_link,
                        })
        return video_data

    def download(self, input_url):
        app_type, url_type, data_key = self.input_url_check(input_url)
        save_folder = os.path.join(self.root_dir, self.download_folder, app_type, url_type)
        try: 
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
        except Exception as bug:
            print(bug)
            return

        video_data = []

        self.desc_frame = self.create_desc_frame()
        self.message_frame = self.create_message_frame()

        msg = 'Đang lấy dữ liệu video, vui lòng đợi...'
        self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)

        if 'DouYin' in app_type:
            if 'Multiple' in url_type:
                video_data = self.get_data(app_type, data_key)
            elif 'Video' in url_type:
                douyin_api_link = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(data_key)
                video_data = [{
                    "video_id": data_key,
                    "video_url": input_url,
                    "video_api": douyin_api_link,
                }]
        elif 'TikTok' in app_type:
            if 'Multiple' in url_type:
                video_data = self.get_data(app_type, data_key)
            elif 'Video' in url_type:
                tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(data_key)
                video_data = [{
                    "video_id": data_key,
                    "video_url": input_url,
                    "video_api": tiktok_api_link,
                }]

        number_of_videos = len(video_data)
        for i in range(number_of_videos):
            msg = 'Video: {} / {}'.format(i+1, number_of_videos)
            self.message_label = self.create_label_form(self.message_frame, self.message_label_name, msg)
            
            js = json.loads(requests.get(url=video_data[i]['video_api'], headers=self.headers).text)    
            try:
                if 'DouYin' in app_type: 
                    nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                elif 'TikTok' in app_type: 
                    nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
            except Exception as bug:
                # print(bug)
                # nickname = 'Empty Nickname'
                pass
                print('[ Feedback ]: Không tìm được nickname, đặt thành: Empty Nickname!\r')
                print('-' * 120)

            try:
                folder_nickname_path = f'{save_folder}\{nickname}'
                if not os.path.exists(folder_nickname_path): 
                    os.makedirs(folder_nickname_path)
            except Exception as bug:
                # print(bug)
                print(f'[ Feedback ]: Không tạo được thư mục {nickname}!\r')
                print('-' * 120)
                return 
            
            try:
                if 'DouYin' in app_type: 
                    video_url_no_watermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
                elif 'TikTok' in app_type: 
                    video_url_no_watermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
            except Exception as bug:
                #print(bug)
                print('[ Feedback ]: Không lấy được link video không nhãn!\r')
                print('-' * 120)
            
            filename = '{}.mp4'.format(video_data[i]['video_id'])
            nickname_path_listdir = os.listdir(folder_nickname_path)
            desc = 'File: {}'.format(filename)
            self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)
            try:
                if filename in nickname_path_listdir:
                    desc = '{} đã tồn tại, bỏ qua tải xuống\n Folder: {}\{}\{}'.format(filename, app_type, url_type, nickname)
                    self.desc_label = self.create_label_form(self.desc_frame, self.desc_label_name, desc)

                    print(f'[ Download ]: {i+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ', end = "")
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
                #print(bug)
                pass
            
            self.progress_frame.destroy()
            self.progress_frame = self.create_progress_frame()
            retry_download_max = 3
            for again_num in range(retry_download_max):
                style, progress = self.create_progress(self.progress_frame, self.progress_name)
                try:
                    print(f'\n[   Video    ]: {i+1}/{number_of_videos}')
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
                    print(bug)
                    continue

        self.entry_link.delete(0, END)
        self.entry_link.insert(END, '')

        self.browser_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Thư mục')
        self.browser_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Thư mục')
        self.download_btn.configure(state='active', bg='mediumseagreen', fg='black', text='Tải xuống')
        self.download_btn.configure(state='active', activebackground='mediumseagreen', activeforeground='black', text='Tải xuống')

        messagebox.showinfo('ERROR', '❤❤❤❤ TẢI XUỐNG HOÀN TẤT! ❤❤❤❤')

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
    try:
        gui = GUI()
        gui.run()
    except Exception as bug:
        messagebox.showinfo('ERROR', '😥😣 BUG 😥😣\n{}'.format(bug))

if __name__ == '__main__':
    main()

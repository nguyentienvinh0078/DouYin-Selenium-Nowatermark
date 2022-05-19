import requests, json, os, time, configparser, re, sys, argparse

class TikTok():
    def __init__(self):
        os.system('cls')
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        self.is_end = False
        self.save_multi = '.\DouYin Multi\\'
        self.save_one = '.\Douyin One\\'

        self.count = 35
        self.mode = 'post'
        self.nickname = ''
        self.like_counts = 0
        self.file_name = ''
        self.sec_uid = ''
        self.user_home_page_data = []
        
        # self.uid_example = 'https://v.douyin.com/FA9KGsL/'
        self.uid_example = 'https://v.douyin.com/JcjJ5Tq/'
        self.url_arg_example = 'https://v.douyin.com/FUS36nS/'

        self.auto_download()

    def auto_download(self):
        while True:
            self.uid, self.check_input = self.get_url_input()
            if self.check_input:
                link_type = self.check_link(self.uid)
                self.is_end = False
                if link_type == 'home_page_url':
                    print(f'[ Thông báo ]: Home page Douyin link: --[ {self.uid} ]-- đã được lấy!')
                    self.run()
                    self.user_home_page_data = []
                    self.like_counts = 0
                elif link_type == 'video_url':
                    print(f'[ Thông báo ]: Video Douyin link: --[ {self.uid} ]-- đã được lấy!')
                    self.download_one_video(self.uid)
            else: break

    def get_url_input(self):
        for retry_number in range(3):
            url_input = re.sub("[^\x00-\xff]", '', 
                    input(f'Nhập link Douyin video hoặc Doyin home page: \nVí dụ:     {self.uid_example}\nPaste Link: ')
            ).replace(' ', '')

            print('-' * 120)
            check_input = False
            if url_input == '':
                print('[ Feedback ]: Link trống, hãy  kiểm tra lại!')
            elif 'douyin.com' in url_input:
                check_input = True   
                print('[ Feedback ]: Nhập link thành công!')
                print('-' * 120)
                break
            elif url_input == 'close':
                break
            else:
                print('[ Feedback ]: Link nhập không chính xác, hãy kiểm tra lại!\r')
                print('-' * 120)
        return url_input, check_input 
                
    def check_link(self, link):
        r = requests.get(url = self.Find(self.uid)[0], headers=self.headers)
        real_link = r.url
        if '/user/' in real_link:
            return 'home_page_url'
        elif '/video/' in real_link:
            return 'video_url'

    def filter_double_byte_char(self, text):
        return re.sub("[^\x00-\xff]", '', text).replace(' ', '')
    
    def Find(self, string):
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
        return url

    def judge_link(self):
        r = requests.get(url = self.Find(self.uid)[0], headers=self.headers)
        try:
            self.sec_uid = re.findall('/user/(.*?)\?', str(r.url))[0]
        except:
            self.sec_uid = r.url[28:]

        max_cursor = 0
        api_post_url = f'https://www.iesdouyin.com/web/api/v2/aweme/{self.mode}/?sec_uid={self.sec_uid}&count={str(self.count)}&max_cursor={max_cursor}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='

        response = requests.get(url = api_post_url, headers = self.headers)
        html = json.loads(response.content.decode())
        self.nickname = html['aweme_list'][0]['author']['nickname']
        self.folder_save_path = f'{self.save_multi}\{self.mode}\{self.nickname}'
        if not os.path.exists(self.folder_save_path):
            os.makedirs(self.folder_save_path)

        self.get_data(api_post_url, max_cursor)

    def get_data(self, api_post_url, max_cursor):
        index = 0
        result = []
        
        while result == [] and index <= 2:
            index += 1
            print('-' * 150)
            print(f'[      Thông báo      ]: Đang lấy dữ liệu lần thứ {index}\r')
            
            response = requests.get(url=api_post_url, headers = self.headers)
            html = json.loads(response.content.decode())

            if self.is_end == False:
                print('-' * 150)
                print(f'[      Nickname       ]: Save Folder: {self.nickname}')

                max_cursor = html['max_cursor']
                result = html['aweme_list'] 
                self.next_data(max_cursor)
                print(f'[      Thông báo      ]: Đã lấy dữ liệu thành công!\r')
                print('-' * 150)
            else:
                max_cursor = html['max_cursor']
                print(f'[      Thông báo      ]: Không có dữ liệu trên trang này, bỏ qua...\r')
                print('-' * 150)
                    
        # return result, max_cursor

    def next_data(self, max_cursor):
        r = requests.get(url=self.Find(self.uid)[0])
        try:
            key = re.findall('/user/(.*?)\?', str(r.url))[0]
        except:
            key = r.url[28:]

        api_naxt_post_url = f'https://www.iesdouyin.com/web/api/v2/aweme/{self.mode}/?sec_uid={key}&count={str(self.count)}&max_cursor={max_cursor}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='

        index = 0
        result = []

        while self.is_end == False and index <= 2:
            if max_cursor == 0:
                self.is_end = True
                return
            index += 1
            print('-' * 150)
            print(f'[      Thông báo      ]: Đang lấy {max_cursor}, lần thứ {index}\r')
            print('-' * 150)
            time.sleep(0.3)
            response = requests.get(url=api_naxt_post_url, headers=self.headers)
            html = json.loads(response.content.decode())
            if self.is_end == False:
                max_cursor = html['max_cursor']
                result = html['aweme_list']
                msg_result = 'được lấy thành công' 
                if result == []:
                    msg_result = 'dữ liệu trống'
                print(f'[      Thông báo      ]: Dữ  liệu {max_cursor}, {msg_result}!\r')
                print('-' * 150)
                self.video_information(result, max_cursor)
            else:
                self.is_end = True
                print(f'[      Thông báo      ]: Dữ  liệu {max_cursor} lấy không thành công!\r')
                print('-' * 150)

    def video_information(self, result, max_cursor):
        video_title_list = []; video_list = []; aweme_id = []; nickname = []

        for i in range(self.count):
            try:
                video_title_list.append(str(result[i]['desc']))
                video_list.append(str(result[i]['video']['play_addr']['url_list'][0]))
                aweme_id.append(str(result[i]['aweme_id']))
                nickname.append(str(result[i]['author']['nickname']))
            except Exception as bug:
                pass

        self.videos_download(video_title_list, video_list, aweme_id, nickname, max_cursor)
        
        # return self,video_title_list,video_list,aweme_id,nickname,max_cursor

    def get_nickname_item_listdir(self, nickname):
        if nickname == []:
            return
        else:
            nickname_item_listdir = os.listdir((self.save_multi + self.mode + '\\' + nickname))
        return nickname_item_listdir
        
    def videos_download(self, video_title_list, video_list, aweme_id, nickname, max_cursor):
        try: 
            os.makedirs(self.save_multi + self.mode + '\\' + nickname[0])
        except:
            pass

        nickname_item_listdir = self.get_nickname_item_listdir(self.nickname)

        for i in range(len(video_list)):
            self.like_counts += 1 
            try:
                jx_url  = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aweme_id[i]}'
                js = json.loads(requests.get(url=jx_url, headers=self.headers).text)
                create_time = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime(js['item_list'][0]['create_time']))
                self.file_name = f'{create_time}_{aweme_id[i]}.mp4'
                video_data = {
                    'aweme_id': aweme_id[i],
                    'video_url': video_list[i],
                    'video_title': video_title_list[i],
                    'nickname': nickname[i],
                    'create_time': str(create_time),
                    'file_name': self.file_name,
                    'number': self.like_counts,
                }   
                self.user_home_page_data.append(video_data)

                with open(f'{self.save_multi}{self.mode}\{self.nickname}_crawdata.json', mode='w', encoding='utf-8') as json_file:
                    json.dump(self.user_home_page_data, json_file, indent=4, separators=(',',': '))
            except Exception as error:
                # print(error)
                pass

            try:
                # file_name = create_time + video_title_list[i] + '.mp4'
                if self.file_name in nickname_item_listdir:
                    print(f'[      Download       ]: Tệp -- [ {self.file_name} ] -- đã tồn tại, bỏ qua tải xuống! ', end = "")
                    for i in range(20):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    continue
            except:
                pass

            try:
                print(f'\n[        Video        ]: {i+1} / {len(video_list)} trên trang {max_cursor}')
                start = time.time()
                video = requests.get(video_list[i])
                size = 0
                chunk_size = 1024
                content_size = int(video.headers['content-length'])
                try:
                    if video.status_code == 200:
                        if self.mode == 'post':
                            # video_name = self.save + self.mode + "\\" + nickname[i] + '\\' + create_time + re.sub(r'[\\/:*?"<>|\r\n] + ', "_", video_title_list[i]) + '.mp4'
                            video_name = self.save_multi + self.mode + '\\' + nickname[i] + '\\' + self.file_name
                        else:
                            # video_name = self.save + self.mode + "\\" + self.nickname + '\\' + str(self.like_counts)+ '、' + re.sub(r'[\\/:*?"<>|\r\n] + ', "_", video_title_list[i]) + '.mp4'
                            video_name = self.save_multi + self.mode + '\\' + nickname + '\\' + str(self.like_counts) + '_' + self.file_name
                        print(f'[        Video        ]: Bắt đâu tải xuống video -- [ {self.file_name} ] --')
                        with open(file=video_name, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size += len(data)
                                print('\r' + '[  Tiến độ tải xuống  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')        
                    end = time.time()
                    print(f'\n[  Tải xuống hoàn tất ]: Thời gian: {end-start:.2f} giây, Dung lượng: {content_size/chunk_size/1024:.2f}MB')
                    print(f'-' * 150)
                except Exception as bug:
                    print(f'[      Cảnh báo       ]: Lỗi khi tải xuống video!')
                    print('-' * 150)
                    print(f'[         Lỗi         ]: {bug}\r')
                    print('-' * 150)
            except Exception as bug:
                print(bug)
                print(f'[      Thông báo      ]: Không có {len(video_list)} tài nguyên video trên trang này, bỏ qua trang!\r')
                print('-' * 150)
                break

        self.next_data(max_cursor)
    
    def download_one_video(self, url_arg):
        r = requests.get(url=self.Find(url_arg)[0])
        key = re.findall('video/(\d+)?', str(r.url))[0]

        try:
            self.video_id = key  
        except:
            print('[    Lỗi    ]: Không lấy được ID video\r')
            return
        
        jx_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={key}'
        js = json.loads(requests.get(url=jx_url, headers=self.headers).text)

        # with open('js_data.json', mode='w', encoding='utf-8') as json_file:
        #         json.dump(js, json_file, indent=4, separators=(',',': '))

        try:
            self.nickname = str(js['item_list'][0]['author']['nickname'])
        except:
            print('[    Lỗi    ]: Không lấy được nickname\r')

        try:
            # self.folder_path = self.save_one + self.mode + '\\' + self.nickname
            self.folder_path = f'{self.save_one}{self.mode}\{self.nickname}'
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
        except:
            print('[    Lỗi    ]: Không tạo được thư mục lưu!\r')
            return 

        try:
            self.video_url = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play')
        except:
            print('[    Lỗi    ]: Không lấy được link video!\r')
            
        try:
            self.video_title = str(js['item_list'][0]['desc'])
        except:
            print('[    Lỗi    ]: Không lấy được caption video!\r')
            self.video_title = 'No_title_id ' + str(self.video_id)

        try:
            self.create_time = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime(js['item_list'][0]['create_time']))
        except:
            print('[    Lỗi    ]: Không lấy được thời gian tạo video video!\r')
            self.create_time = 'No_crate_time '
        
        print('-' * 150)
        print(f'[ Nickname  ]: Save Folder: {self.nickname}')
        print('-' * 150)
        print(f'[ Thông báo ]: Link video không nhãn: {self.video_url}')
        print('-' * 150)
        print(f'[ Thông báo ]: Link douyin page: https://douyin.com/video/{self.video_id}')
        print('-' * 150)
        
        self.file_name = f'{self.create_time}_{self.video_id}.mp4'

        folder_path_listdir = os.listdir(self.folder_path)
        
        if self.file_name in folder_path_listdir:
            print(f'[ Download  ]: Tệp -- [ {self.file_name} ] -- đã tồn tại, bỏ qua tải xuống! ', end='')
            for i in range(20):
                print(">", end='', flush=True)
                time.sleep(0.01)
            print('\r')
            root_dir = os.path.abspath(os.path.dirname(__file__))
            print('-' * 150)
            print(f'[ Thông báo ]: Đường dẫn: -- [ {root_dir}{self.folder_path[1:]}\{self.file_name} ] --\r')
            print('-' * 150)
            return 
        i = 0
        while i < 3:
            try:
                if self.video_url == '':
                    print('[    Lỗi    ]: Video này không tải xuống được!\r')
                    return
                else:
                    start = time.time()
                    r = requests.get(url=self.video_url, headers=self.headers)
                    size = 0
                    chunk_size = 1024
                    content_size = int(r.headers['content-length'])
                    if r.status_code == 200:
                        video_name = f'{self.folder_path}\{self.file_name}'
                        print(f'[        Video        ]: Bắt đâu tải xuống video -- [ {self.file_name} ] --')
                        with open(file=video_name, mode='wb') as file:
                            for data in r.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '[  Tiến độ tải xuống  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')        
                    end = time.time()
                    print(f'\n[  Tải xuống hoàn tất ]: Thời gian: {end-start:.2f}s, Dung lượng: {content_size/chunk_size/1024:.2f}MB')
                    print(f'-' * 150)
                    break
            except:
                print(f"[ Yêu cầu đã hết thời gian chờ ]: Lần thử thứ {i+1}\n Sắp có lần thử thứ {i+2}!\r")
                i += 1

    def run(self):
        self.judge_link()
        print(f'[      Thông báo      ]: Đã tải xong {self.like_counts} video!\r')

if __name__ == '__main__':
    tkdown = TikTok()

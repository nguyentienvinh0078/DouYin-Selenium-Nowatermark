import os, re, requests, json, time

class DouyinDownload():
    def __init__(self):
        os.system('cls')
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
            running_mode = 'Frozen/executable'
        else:
            try:
                app_full_path = os.path.realpath(__file__)
                application_path = os.path.dirname(app_full_path)
                running_mode = "Non-interactive (e.g. 'python myapp.py')"
            except NameError:
                application_path = os.getcwd()
                running_mode = 'Interactive'

        self.root_dir = application_path
        self.save_folder = ''
        self.url_example = 'https://v.douyin.com/FUS36nS/'
        self.url_input = ''
        self.check_input = False
        self.video_data = []

        self.auto_download()

    def auto_download(self):
        while True:
            self.url_input, self.check_input = self.get_url_input()
            if self.check_input:
                self.save_folder = 'DouYin One'
                self.folder_save_path = f'{self.root_dir}\{self.save_folder}'
                response = requests.get(url=self.url_input, headers=self.headers)
                video_url = response.url
                video_id = re.findall('video\/(\d+)', video_url)[0]
                jx_url_base = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
                self.video_data = [{
                    "video_number": "1",
                    "video_id": video_id,
                    "video_url": video_url,
                    "video_api": f"{jx_url_base}{video_id}",
                }]

                self.download(self.video_data)
                os.system('cls')
                print('[ Feedback ]: Tải xuống hoàn tất {} video'.format(len(self.video_data)))
            else: break
        
    def get_url_input(self):
        for retry_number in range(3):
            print('-' * 120)
            print('[ Feedback ]: Nhập vào link để tải xuống, Nhập "Close" để thoát!')
            print('-' * 120)
            url_input = re.sub("[^\x00-\xff]", '', input('[ Nhập link ]: ')).replace(' ', '')
            print('-' * 120)
            check_input = False   
            if url_input == '':
                print('[ Feedback ]: Link trống, hãy  kiểm tra lại!')
            elif 'douyin.com' in url_input:
                check_input = True   
                print('[ Feedback ]: Nhập link thành công!')
                print('-' * 120)
                break
            elif url_input == 'close' or url_input == 'Close':
                break
            else:
                print('[ Feedback ]: Link nhập không chính xác, hãy kiểm tra lại!\r')
                print('-' * 120)
        return url_input, check_input 

    def download(self, video_data):
        number_of_videos = len(video_data)
        for video_number in range(number_of_videos):
            js = json.loads(requests.get(url=video_data[video_number]['video_api'], headers=self.headers).text)
            try:
                nickname = str(js['item_list'][0]['author']['nickname'])
            except Exception as bug:
                # print(bug)
                nickname = 'Empty Nickname'
                print('[ Feedback ]: Không tìm được nickname, đặt thành: Empty Nickname!\r')
                print('-' * 120)

            try:
                folder_nickname_path = f'{self.folder_save_path}\{nickname}'
                if not os.path.exists(folder_nickname_path): 
                    os.makedirs(folder_nickname_path)
            except Exception as bug:
                # print(bug)
                print(f'[ Feedback ]: Không tạo được thư mục {nickname}!\r')
                print('-' * 120)
                return 
            
            try:
                video_url_no_watermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play')
            except Exception as bug:
                #print(bug)
                print('[ Feedback ]: Không lấy được link video không nhãn!\r')
                print('-' * 120)

            try:
                create_time = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(js['item_list'][0]['create_time']))
            except Exception as bug:
                #print(bug)
                create_time = 'no_create_time'
                print('[    Lỗi    ]: Không lấy được thời gian tạo video video!\r')
                print('-' * 120)
            
            filename = '{} {}.mp4'.format(create_time, video_data[video_number]['video_id'])
            nickname_path_listdir = os.listdir(folder_nickname_path)

            try:
                if filename in nickname_path_listdir:
                    print(f'[ Download ]: {video_number+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ', end = "")
                    for i in range(15):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                #print(bug)
                pass
            
            retry_download_max = 3
            for retry_number in range(retry_download_max):
                try:
                    print(f'\n[   Video    ]: {video_number+1}/{number_of_videos}')
                    print(f'[   Video    ]: Đang tải tệp -- [ {filename} ] --')
                    start_download_time = time.time()
                    size = 0
                    chunk_size = 1024
                    video = requests.get(url=video_url_no_watermark, headers=self.headers)
                    content_size = int(video.headers['content-length'])
                    MB_size = content_size / chunk_size / 1024

                    if video.status_code == 200:
                        video_path = f'{folder_nickname_path}\{filename}'
                        with open(file=video_path, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '[  Download  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')
                    end_download_time = time.time()
                    download_time = end_download_time - start_download_time
                    print(f'\n[  Download  ]: Thời gian: {download_time:.2f}s, Kích thước: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    #print(bug)
                    continue

def main():
    douyin_download = DouyinDownload()

if __name__ == '__main__':
    main()
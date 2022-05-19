import os, re, requests, json, time

class DouyinDownload():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        self.save_folder = 'DouYin One'
        self.url_example = 'https://v.douyin.com/FUS36nS/'
        self.url_input = ''
        self.check_input = False
        
        self.auto_download()

    def auto_download(self):
        while True:
            self.url_input, self.check_input = self.get_url_input()
            if self.check_input:
                self.download(self.url_input)
            else:
                break
        
    def get_url_input(self):
        for retry_number in range(3):
            url_input = re.sub("[^\x00-\xff]", '', input('\nNhập link: ')).replace(' ', '')
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

    def download(self, url_input):
        r = requests.get(url=url_input, headers=self.headers)
        video_id = re.findall('video/(\d+)?', str(r.url))[0]
        
        jx_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}'
        js = json.loads(requests.get(url=jx_url, headers=self.headers).text)

        try:
            nickname = str(js['item_list'][0]['author']['nickname'])
        except:
            nickname = 'Ving not find nickname'
            print('[ Feedback ]: Không tìm thấy nickname!')

        try:
            folder_save_path = f'{self.root_dir}\{self.save_folder}\{nickname}'
            if not os.path.exists(folder_save_path):
                os.makedirs(folder_save_path)
        except:
            print('[ Feedback ]: Lỗi khi tạo thư mục!')
            print('-' * 120)
            return

        try:
            video_url = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play')
        except:
            print('[ Feedback ]: Không tìm thấy link video!\r')
        
        filename = f'{video_id}.mp4'
        folder_path_listdir = os.listdir(folder_save_path)

        if filename in folder_path_listdir:
            print(f'[ Download  ]: Tệp -- [ {filename} ] -- đã tồn tại, bỏ qua tải xuống! ', end='')
            for i in range(20):
                print(">", end='', flush=True)
                time.sleep(0.01)
            print('\r')
            print('-' * 120)
            return 
        
        retry_download = 3
        for retry_down_num in range(retry_download):
            try:
                print(f'\n[   Video  ]: Đang tải video -- [ {filename} ] --')
                start_download = time.time()
                r = requests.get(url=video_url, headers=self.headers)
                size = 0
                chunk_size = 1024
                content_size = int(r.headers['content-length'])
                MB_size = content_size / chunk_size / 1024
                if r.status_code == 200:
                    video_path = f'{folder_save_path}\{filename}'
                    with open(file=video_path, mode='wb') as file:
                        for data in r.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            size = size + len(data)
                            print('\r' + '[ Download ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')        
                end_download = time.time()
                downlaod_total_time = end_download - start_download
                print(f'\n[ Download ]: Thời gian: {downlaod_total_time:.2f} giây, Dung lượng: {MB_size:.2f}MB')
                print(f'-' * 120)
                break
            except:
                print(f"[ Feedback ]: Có sự cố xảy ra, đang thử lại..!\r")
                continue

def main():
    douyin_download = DouyinDownload()

if __name__ == '__main__':
    main()
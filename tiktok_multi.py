import os, time, re, requests, json, sys
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TiktokDownload:
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
        self.save_folder = 'TikTok Multi'
        self.download_page_url = 'https://snaptik.app/vn'

        """
            URL INPUT
            # user page link
            https://www.tiktok.com/@tinaneeeee/video/7098291042625080602?is_copy_url=1&is_from_webapp=v1
            https://www.tiktok.com/@tinaneeeee
            
            # video link
            https://vt.tiktok.com/ZSdQkfHpf/?k=1
            https://vt.tiktok.com/ZSdQk9f8J/
        """

        self.url_input = ''; self.check_input = False; self.is_userpage=False; self.user_title='Empty title'

        self.auto_downoad()

    def auto_downoad(self):
        while True:
            self.url_input, self.check_input = self.get_url_input()
            if self.check_input:
                self.is_userpage, self.user_title, self.url_input = self.check_user_page(self.url_input)
                self.save_folder = 'Tiktok Multiple' if self.is_userpage else'Tiktok One'
                self.folder_save_path = f'{self.root_dir}\{self.save_folder}\{self.user_title}'
                self.json_file_path = f'{self.root_dir}\{self.save_folder}\{self.user_title}.json'

                try:
                    if not os.path.exists(self.folder_save_path):
                        os.makedirs(self.folder_save_path)
                except:
                    print('[ Feedback ]: Lỗi khi tạo thư mục!')
                    print('-' * 120)
                    return
                
                if self.is_userpage:
                    print('[ Feedback ]: Tải xuống nhiều video!')
                    print('-' * 120)
                    self.video_data = self.get_data(self.url_input)
                else:
                    print('[ Feedback ]: Tải xuống 1 video!')
                    print('-' * 120)
                    response = requests.get(url=self.url_input, headers=self.headers)
                    video_url = response.url
                    video_id = re.findall('video\/(\d+)', video_url)[0]
                    # jx_url_base = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=' # douyin
                    tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
                    self.video_data = [{
                        "video_number": "1",
                        "video_id": video_id,
                        "video_url": video_url,
                        "video_api": tiktok_api_link,
                    }]

                self.download(self.video_data)
                os.system('cls')
                print('[ Feedback ]: Tải xuống hoàn tất {} video'.format(len(self.video_data)))
            else: break

    def check_user_page(self, url_input):
        if 'www.tiktok.com/@' in url_input:
            if '/video/' in url_input: 
                return False, re.findall('\/@(.*)', url_input)[0], url_input
            else: 
                return True, re.findall('\/@(.*)', url_input)[0], url_input
        else:
            response = requests.get(url=url_input, headers=self.headers)
            if '/video/' in response.url: 
                return False, re.findall('\/@(.*)', response.url)[0], response.url
            else: 
                return True, re.findall('\/@(.*)', response.url)[0], response.url
        
    def get_url_input(self):
        retry_max = 3
        for retry_number in range(retry_max):
            print('-' * 120)
            print('[ Feedback ]: Nhập vào link để tải xuống, Nhập "close" để thoát!')
            print('-' * 120)
            url_input = re.sub("[^\x00-\xff]", '', input('[ Nhập link ]: ')).replace(' ', '')
            print('-' * 120)
            check_input = False
            if url_input == '':
                print(f'[ Feedback ]: <!> Link nhập trống! Hãy kiểm tra lại....\r')
                print('-' * 120)
                if (retry_number + 1) != retry_max:
                    print('[ Feedback ]: <!> Thử lại lần thứ {}!\r'.format(retry_number + 1))
                    print('-' * 120)
            elif 'tiktok.com' in url_input:
                check_input = True
                print('[ Feedback ]: Nhập link thành công!')
                print('-' * 120)
                break
            elif url_input == 'close' or url_input == 'Close' or url_input == 'x':
                break
            else:
                print(f'[ Feedback ]: <!> Link nhập không thành công....\r')
                print('-' * 120)
                if (retry_number + 1) != retry_max:
                    print('[ Feedback ]: <!> Thử lại lần thứ {}!\r'.format(retry_number + 1))
                    print('-' * 120)
        return url_input, check_input

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
        start_time = time.time()
        self.driver = self.init_driver('headless')
        self.driver.get(url)

        scroll_pause_time = 1
        last_scroll_height = 0
        while True:
            new_scroll_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_scroll_height != last_scroll_height:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(scroll_pause_time)
                last_scroll_height = new_scroll_height
            else:
                break
        
        src_elements = self.driver.find_elements_by_css_selector("div[data-e2e='user-post-item'] a")

        video_data = []
        video_number = 1
        for src_element in src_elements:
            video_url = src_element.get_attribute('href')
            video_id = re.findall('video\/(\d+)', video_url)[0]
            tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
            video_data.append({
                'video_number': str(video_number),
                'video_id': (re.findall('/video/(\d+)?', video_url)[0]),
                'video_url': video_url,
                'video_api': f"{tiktok_api_link}",
            })
            with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                json.dump(video_data, json_file, indent=4, separators=(',', ': '))
            video_number = video_number + 1

        self.driver.quit()
        end_time = time.time()
        sub_time = end_time - start_time
        print('[ Feedback ]: Lấy dữ liệu thành công -*- {} Video -*- Thời gian: {:.2f} giây...'.format(video_number-1, sub_time))
        print('-' * 120)
        return video_data

    def download(self, video_data):
        number_of_videos = len(video_data)
        for video_number in range(number_of_videos):
            js = json.loads(requests.get(url=video_data[video_number]['video_api'], headers=self.headers).text)
            try:
                # nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                nickname = str(js["aweme_details"][0]['author']["nickname"])
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
                video_url_no_watermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0])
                # video_url_no_watermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
            except Exception as bug:
                #print(bug)
                print('[ Feedback ]: Không lấy được link video không nhãn!\r')
                print('-' * 120)

            try:
                # create_time = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(js['item_list'][0]['create_time'])) # douyin
                create_time = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(js["aweme_details"][0]['create_time']))
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
    tiktok_download = TiktokDownload()

if __name__ == '__main__':
    main()
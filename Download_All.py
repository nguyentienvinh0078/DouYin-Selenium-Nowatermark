import re, requests, os, sys, json, time


class Check:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
    
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            try:
                application_path = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                application_path = os.getcwd()

        self.root_dir = application_path
        self.download_folder = 'Download'

    def get_input_url(self, retry_max=3):
        for again_num in range(retry_max):
            print('-' * 120)
            print('[ Feedback ]: Nhập vào Link để tải xuống, Nhập "close" để thoát!')
            print('-' * 120)
            input_url = re.sub("[^\x00-\xff]", '', input('[   Link   ]: ')).replace(' ', '')
            print('-' * 120)
            input_check = False
            if input_url == '':
                os.system('cls')
                print('-' * 120)
                print(f'[ Feedback ]: <!> Link nhập trống! Hãy kiểm tra lại....\r')
            elif 'tiktok.com' in input_url or 'douyin.com' in input_url:
                input_check = True
                print('[ Feedback ]: Nhập link thành công!')
                print('-' * 120)
                break
            elif input_url.title() == "Close":
                break
            else:
                os.system('cls')
                print('-' * 120)
                print(f'[ Feedback ]: <!> Link nhập không thành công, hãy kiểm tra lại....\r')
        return input_url, input_check

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
                
    def main(self):
        os.system('cls')
        input_url, input_check = self.get_input_url()
        if input_check:
            app_type, url_type, data_key = self.input_url_check(input_url)
            save_folder = os.path.join(self.root_dir, self.download_folder, app_type, url_type)
            try: 
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
            except Exception as bug:
                print(bug)
                return
            video_data = []
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

        # print('APP_TYPE: {} -- URL_TYPE: {} -- TOLTAL: {}'.format(app_type, url_type, len(video_data)))
        self.download(save_folder, app_type, video_data)        

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

    def download(self, folder_save_path, app_type, video_data):
        number_of_videos = len(video_data)
        for i in range(number_of_videos):
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
                folder_nickname_path = f'{folder_save_path}\{nickname}'
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

            try:
                if filename in nickname_path_listdir:
                    print(f'[ Download ]: {i+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ', end = "")
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
            for again_num in range(retry_download_max):
                try:
                    print(f'\n[   Video    ]: {i+1:>2}/{number_of_videos}')
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
    try:
        check = Check()
        check.main()
    except Exception as bug:
        print(bug)
        os.system('pause')
if __name__ == '__main__':
    main()
import requests
import json
from pathlib import Path

TOKEN_VK = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

V = 5.124

class VK_User:
    def __init__(self, user_id, yandex_token):
        self.user_id = user_id
        self.yandex_token = yandex_token

    def get_photo_info(self):
        BASE_URL = 'https://api.vk.com/method/photos.get'
        headers = {'Authorization': f'OAuth {self.yandex_token}', 'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.get(BASE_URL, params={
            'owner_id': self.user_id,
            'access_token': TOKEN_VK,
            'v': V,
            'album_id': 'profile',
            'extended': 1
        })
        result = []
        for photo in response.json()['response']['items']:
            for photo_size in photo['sizes']:
                max_size_dict = photo_size
            tmp_dict = {'size': max_size_dict, 'likes': photo['likes']['count'], 'date': photo['date']}
            result.append(tmp_dict)
        return result

    def create_folder(self):
        BASE_URL = 'https://cloud-api.yandex.net:443/v1/disk/resources'
        headers = {'Authorization': f'OAuth {self.yandex_token}', 'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        folder_name = f'photos{self.user_id}'
        response = requests.put(BASE_URL, headers=headers, params={
            'path': folder_name
        })
        return folder_name

    def get_folder_info(self):
        BASE_URL = 'https://cloud-api.yandex.net:443/v1/disk/resources'
        headers = {'Authorization': f'OAuth {self.yandex_token}', 'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        tmp_dict = []
        folder = self.create_folder()
        params = {'path': f'{folder}/'}
        response = requests.get(BASE_URL, headers=headers, params=params)
        for item in response.json()['_embedded']['items']:
            tmp_dict.append(item['name'])
        return tmp_dict

    def publish_photo(self):
        BASE_URL = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        headers = {'Authorization': f'OAuth {self.yandex_token}', 'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        for item in self.get_photo_info():
            folder = self.create_folder()
            photo_likes = item['likes']
            photo_url = item['size']['url']
            photo_prefix = Path(photo_url).suffix
            file_name = f'{photo_likes}likes{photo_prefix}'
            for name in self.get_folder_info():
                if name == file_name:
                    file_name = str(photo_likes) + 'likes' + str(item['date']) + photo_prefix
            params = {'path': f'{folder}/{file_name}', 'url': photo_url}
            response = requests.post(BASE_URL, headers=headers, params=params)
            item_info = {'file_name': file_name, 'size': item['size']['type']}
            if response.status_code == 202 or response.status_code == 200:
                with open('files/result.json', 'a') as f:
                    json.dump(item_info, f)



if __name__ == '__main__':
    user1 = VK_User(46382282, 'AgAAAAAnT4gjAADLWxQ4LxaIlETCk5QTA6awvAQ')
    user1.publish_photo()

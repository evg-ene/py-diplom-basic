import requests
from collections import Counter
import datetime
from tqdm import tqdm
import json

owner_id = int(input('Введите id пользователя vk: '))
yadisk_api_token = input("Введите token Яндекс.Диска: ")
count = int(input("Введите кол-во фотографий, которые необходимо сохранить: ") or "5")


class VkGetPhotos:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def create_dict_img(self):
        params = {'owner_id': owner_id, 'access_token': vk_api_token, 'v': '5.131', 'album_id': 'profile',
                  'extended': '1', 'photo_sizes': '1', 'count': count}
        response = requests.get('https://api.vk.com/method/photos.get', params=params)
        list_likes = []
        list_data = []
        for item in response.json()['response']['items']:
            count_photos_sizes = len(item['sizes'])
            list_likes.append(item['likes']['count'])  # Список лайков, необходим для поиска дубликатов
            list_data.append([item['sizes'][count_photos_sizes - 1]['url'], item['date'], item['likes']['count'], item['sizes'][count_photos_sizes - 1]['type']])
        return list_likes, list_data


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload(self, likes, vk_data, login_id):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}
        # Создание папки для фотографий на Я.Диске
        r = requests.put(f'{url}?path=disk:/{login_id}', headers=headers).json()
        # Создание имени файла для фотографий
        json_data = []
        for data in tqdm(vk_data):
            if Counter(likes)[data[2]] > 1:  # Обработка одинакового кол-ва лайков
                filename = str(datetime.datetime.fromtimestamp(data[1]).strftime('%Y%m%d%H%M_')) + str(data[2]) + '.jpg'
            else:
                filename = str(data[2]) + '.jpg'
            # Загрузка фото на Я.Диск
            r = requests.get(f'{url}/upload?path=disk:/{login_id}/{filename}&overwrite=true', headers=headers).json()
            requests.put(r['href'], files={'file': data[0]})
            json_data.append({"file_name": f"{filename}", "size": f"{data[3]}"})
        with open('json_data.txt', 'w') as f:
            f.write(json.dumps(json_data))
        return 'done'


if __name__ == '__main__':
    vk_api_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    dict_photo = VkGetPhotos(vk_api_token)
    uploader = YaUploader(yadisk_api_token)
    uploader.upload(dict_photo.create_dict_img()[0], dict_photo.create_dict_img()[1], owner_id)

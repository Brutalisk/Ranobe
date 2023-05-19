import requests
from bs4 import BeautifulSoup
import time
from FB2 import FictionBook2, Author
import re
import os
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
#Том и Глава
body = "https://ranobelib.me/tianguan-cifu"
tom = 5
glava = 199
url = f"{body}/v{tom}/c{glava}"
#Название новеллы
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
target_div = soup.find("div", class_="reader-header-action__text text-truncate")
output_file_name = target_div.text
illegal_chars = r'[\\/:\*\?"<>\|]'
output_file_name = re.sub(illegal_chars, '_', output_file_name)
paragraphs = soup.find_all("p")
#Сколько глав(Номер последней главы тома  минус номер первой главы тома плюс 1)
rang = 54
text = ''


with open('text.txt', 'a', encoding='utf-8') as f:
    for i in range(rang):
        url = f"{body}/v{tom}/c{glava}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f'Ошибка при получении страницы, повторная попытка через 2 секунд...')
            time.sleep(2)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        text_list = [p.text for p in soup.find_all('p') if
                     'Больше не показывать' not in p.text and
                     'Внимание! Данный контент может содержать ненормативную лексику, сексуальные сцены откровенного характера, а также художественное изображение жестокости и насилия и ux cлoвecныe oпucaнuя, которые недоступны для просмотра лицам до 18 лет.'
                     not in p.text and 'Если вы обнаружите какие-либо ошибки ( неработающие ссылки, нестандартный контент и т.д.. ), Пожалуйста, сообщите нам об этом , чтобы мы могли исправить это как можно скорее.'not in p.text]

        f.write(f'\n\nГлава {glava}\n\n')
        f.write('\n'.join(text_list))

        print(f'Текст главы {glava} сохранен в файл text.txt')

        glava += 1




with open('text.txt', 'r', encoding='utf-8') as input_file:
    text = input_file.read()

# Разделяем текст на главы
chapter_texts = re.split(r'Глава \d+', text)[1:]

# Создаем объект книги и добавляем главы
book = FictionBook2()
book.titleInfo.title = f"{output_file_name}_Том{tom}"
book.titleInfo.authors = [Author(firstName="FALN", lastName="LNDZ")]
book.titleInfo.genres = ["sf", "sf_fantasy"]
for i, chapter_text in enumerate(chapter_texts):
    chapter_title = f"Глава {glava-rang}"
    book.chapters.append((chapter_title, [chapter_text]))
    glava += 1

# Сохраняем книгу в формате fb2
book.write(f"{output_file_name}_Том{tom}.fb2")
print(f'Текст сохранен в файл fb2')
os.remove("text.txt")
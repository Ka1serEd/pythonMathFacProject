import time
import dataframe_image as dfi
import pandas as pd
import telebot
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def chunks(lst, n):
    """Разделить список по 3 куска"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


url = "https://www.binance.com/ru/trade/BTC_USDT?_from=markets&type=spot"
driver = webdriver.Firefox()

list_of_commands = ["/stop", "/btc", "/help", "/start", "/info"]
timelist = ["1s", "15m", "1h", "4h", "1d", "1w"]
driver.get("https://www.binance.com/ru/trade/BTC_USDT?_from=markets&type=spot")
url_rub = "https://ru.investing.com/currencies/usd-rub"
driver_rub = webdriver.Firefox()
if __name__ == '__main__':
    bot = telebot.TeleBot('YOUR_API') #Ваш API 


    @bot.message_handler(commands=["start"])
    def start(m, res=False):
        bot.send_message(m.chat.id, f'Бот запущен. Начните общение с ним с помощью команды {chr(92)}info.')


    @bot.message_handler(content_types=['text'])
    def get_text_messages(message, res=False):
        if message.text == "/info":
            bot.send_message(message.chat.id, f'Привет! Этот бот был написан на коленке с бюджетом <оценка удовлетворительно по дисциплине основы программирования на python>. \n Пока что он умеет не многое, вот список его команд:')
            bot.send_message(message.chat.id, f'{chr(47)}btc - выведет курс биткоина,и график с свечами,\n если вместо BTC написать тег какой-нибудь другой криптовалюты, то он уже выведет её график. \n Eсли же имеется нужда изменить период на графике свечей, то после команды {chr(47)}tag, нужно дописать временной период одной свечи, пока доступны только следующие временные периоды {timelist}. \n Последняя команда {chr(47)}orderbook tag, вы получите 2 фотографии биржевого стакана на данный момент времени.')
            bot.send_message(message.chat.id, f'Так же имеется возможность активно следить за курсом рубля с помощью команды {chr(47)}rub, приятного пользования =).')
        elif message.text == "/btc":
            driver.get("https://www.binance.com/ru/trade/BTC_USDT?_from=markets&type=spot")
            source = BeautifulSoup(driver.page_source, 'html.parser')
            price_element = source.find('div', class_='subPrice')
            bot.send_message(message.chat.id, f'Цена биткоина прямо сейчас: {str(price_element)[23:-6]} $')
            time.sleep(3)
            element = driver.find_element(By.CLASS_NAME, "bn-flex")
            element.screenshot('None.png')
            bot.send_photo(message.chat.id, photo=open('None.png', 'rb'))
        elif message.text == "/stop":
            return
        if message.text == "/rub":
            driver_rub.get(url_rub)
            source = BeautifulSoup(driver_rub.page_source, 'html.parser')
            price_element = source.find('div',
                                        class_='text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]')
            print(str(price_element)[116:-8])
            if float(str(price_element)[116:-8].replace(',', '.')) > 100:
                bot.send_message(message.chat.id, f'Цена одного доллара {str(price_element)[116:-8]} рублей. Это грустно =(.')
            else:
                bot.send_message(message.chat.id,
                                 f'Цена одного доллара {str(price_element)[116:-8]} рублей. Веселей ребята, скоро заживём...')
        elif message.text.startswith("/") and (message.text not in list_of_commands) and (
                message.text.startswith("/orderbook") != True):
            text = message.text[1:]
            texts = text.split()
            new_url = url.replace('BTC', texts[0])
            driver.get(new_url)
            price_element = None
            try:
                price_element = driver.find_element(By.CLASS_NAME, 'subPrice')
            except:
                pass
            if price_element == None:
                bot.send_message(message.chat.id, f'Такой валюты не существует')
            else:
                bot.send_message(message.chat.id,
                                 f'Цена {texts[0].upper()} прямо сейчас: {price_element.text[1:]} $USDT')
                if len(texts) != 1:
                    if texts[1] in timelist:
                        settings = driver.find_element(By.ID, str(texts[1]))
                        settings.click()
                    else:
                        bot.send_message(message.chat.id, f'Пока такой интервал времени неопределён.')
                time.sleep(2)
                element = driver.find_element(By.CLASS_NAME, "bn-flex")
                element.screenshot('diagramm.png')
                bot.send_photo(message.chat.id, photo=open('diagramm.png', 'rb'))
        elif message.text.startswith("/orderbook"):
            order_texts = message.text[1:].split()
            if len(order_texts) == 1:
                bot.send_message(message.chat.id, 'Перепроверьте тег пожалуйста!!!')
            else:
                new_url = url.replace('BTC', order_texts[1])
                driver.get(new_url)
                orders_buy = pd.DataFrame(columns=["Цена (USDT)", f'Количество {order_texts[1].upper()}', "Всего (USDT)"])
                orders_sell = pd.DataFrame(columns=["Цена (USDT)", f'Количество {order_texts[1].upper()}', "Всего (USDT)"])
                time.sleep(2)
                price_element = None
                try:
                    price_element = driver.find_element(By.CLASS_NAME, 'subPrice')
                except:
                    pass
                if price_element == None:
                    bot.send_message(message.chat.id, 'Перепроверьте тег пожалуйста!!!')
                else:
                    order_book = driver.find_elements(By.CLASS_NAME,
                                                'orderbook-list-container')  # первый элемент массива это запросы на продажу, второй запросы на покупку"
                    order_book_sell = list(chunks(order_book[0].text.split(), 3))
                    order_book_buy = list(chunks(order_book[1].text.split(), 3))
                    for i in order_book_buy:
                        orders_buy.loc[len(orders_buy)] = i
                    for j in order_book_sell:
                        orders_sell.loc[len(orders_sell)] = j
                    dfi.export(orders_buy.style.background_gradient(), 'orders_buy.png')
                    dfi.export(orders_sell.style.background_gradient(), 'orders_sell.png')
                    bot.send_message(message.chat.id,
                                    f"Запросы на покупку/продажу {order_texts[1].upper()} выглядят следующим образом:")
                    bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(open('orders_buy.png', 'rb')),
                                                           telebot.types.InputMediaPhoto(open('orders_sell.png', 'rb'))])


    bot.polling(none_stop=True, interval=0)

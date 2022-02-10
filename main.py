from telegram import Update
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext,MessageHandler
from bs4 import BeautifulSoup
import re
import requests

def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Chào ông chủ {update.effective_user.first_name}')

def get_news():
    list_news = []
    r = requests.get("https://vnexpress.net/")
    soup = BeautifulSoup(r.text, 'html.parser')
    mydivs = soup.find_all("h3", {"class":"title-news"})

    for new in mydivs:
        news = {}
        news["link"] = new.a.get("href")
        news["title"] = new.a.text
        list_news.append(news)
    return list_news

def news(update: Update, context: CallbackContext) -> None:
    data = get_news()
    str = ""
    for d in range (0,5):
        str += data[d]["title"]+": "+data[d]["link"]+"\n"
    update.message.reply_text(f'Tin mới nhất: \n{str}')

# crawl shopee product to bot chat
def format_link_shopee(name, shopid, itemid):
    formatname = name.upper()
    formatname = formatname.replace(" ","-")
    return "https://shopee.vn/{}-i.{}.{}".format(formatname, shopid, itemid)

def crawl_shopee_product(keyword):
    url = 'https://shopee.vn/api/v2/search_items/?by=relevancy&keyword={}&limit=100&newest=0&order=desc&page_type=search'.format(keyword)
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://shopee.vn/search?keyword={}'.format(keyword)
    }

    r = requests.get(url, headers=headers)
    data = r.json()
    list_products = []

    for item in data['items']:
        product = {}
        product['name'] = item['name']
        product['price'] = item['price']/100000
        product['link'] = format_link_shopee(item['name'], item['shopid'],item['itemid'])
        list_products.append(product)
    return list_products

def get_search_command(keyword):
    keyword = keyword.replace("\"","")
    keyword = keyword.split("_")
    if len(keyword) <= 1:
        return 0
    else:
        if keyword[1] == "":
            return keyword[0], 0
        else:
            return keyword[0], int(keyword[1]) # return "what to search" and num of search result

def shopping(update: Update, context: CallbackContext) -> None:
    id, num = get_search_command(update.message.text.replace("/shopping ", ""))
    list_products = crawl_shopee_product(id)
    print(id)
    print(num)
    print(len(list_products))
    mess = ""
    if num != 0:
        if num > len(list_products): num = len(list_products)
        for i in range (0, num):
            mess += str(i+1) + ". name: "+ list_products[i]['name'] + "\n" + "price: " + str(list_products[i]['price']) + "\n" + "link: " + list_products[i]['link'] + "\n" + "------\n" 
    else:
        if len(list_products) < 10: num = len(list_products)
        else:
            num = 10
        for i in range (0, num):
            mess += str(i+1) + ". name: "+ list_products[i]['name'] + "\n" + "price: " + str(list_products[i]['price']) + "\n" + "link: " + list_products[i]['link'] + "\n" + "------\n" 
    update.message.reply_text(f'Các kết quả:\n {mess}')

updater = Updater('5101674787:AAGILdSEXhdV7jmzwXBtvQ8B4w6T421EOvE') # your token here

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('news', news))
updater.dispatcher.add_handler(CommandHandler('shopping', shopping, pass_args=True)) # allow argument after command


updater.start_polling()
updater.idle()
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate(
    "project-analytics-8acd9-firebase-adminsdk-6usuy-2415c74209.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


sched = BlockingScheduler()


@sched.scheduled_job("interval", days=1)
def timed_job():
	url = "http://www.atmovies.com.tw/movie/next/"
	Data = requests.get(url)
	Data.encoding = "utf-8"
	sp = BeautifulSoup(Data.text, "html.parser")
	lastUpdate = sp.find("div", class_="smaller09").text[5:]
	result = sp.select(".filmListAllX li")
	for item in result:
		picture = item.find("img").get("src").replace(" ", "")
		title = item.find("div", class_="filmtitle").text
		movie_id = item.find("div", class_="filmtitle").find(
			"a").get("href").replace("/", "").replace("movie", "")
		hyperlink = "http://www.atmovies.com.tw" + \
			item.find("div", class_="filmtitle").find("a").get("href")
		show = item.find("div", class_="runtime").text.replace("上映日期：", "")
		show = show.replace("片長：", "")
		show = show.replace("分", "")
		showDate = show[0:10]
		showLength = show[13:]
		doc = {
			"title": title,
			"picture": picture,
			"hyperlink": hyperlink,
			"showDate": showDate,
			"showLength": showLength,
			"lastUpdate": lastUpdate
		}
		doc_ref = db.collection("電影").document(movie_id)
		doc_ref.set(doc)


sched.start()

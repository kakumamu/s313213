import requests
import bs4
from g4f.client import Client
from flask import Flask, render_template
from deep_translator import GoogleTranslator

def ignoreError():
    def decorator(func):
        def wrapper(*args, **kwargs):
            res = None
            try:
                res = func()
            except Exception:
                res = None
            finally:
                return res
        return wrapper
    return decorator

def AItranslate(cn):
    client=Client()
    translatedCN = client.chat.completions.create(
        model="gemma-3-12b",
        messages=[{"role": "user", "content": f'Translate to english.\n{cn}'}],
        web_search=False
    ).choices[0].message.content
    return translatedCN

def getChapterAI(wid, eid):
    con = requests.get(f"https://kakuyomu.jp/works/{wid}/episodes/{eid}").content
    soup = bs4.BeautifulSoup(con, "html.parser")
    title = soup.find("p", class_="widget-episodeTitle").text.strip()
    body = "\n".join([p.text.strip() for p in soup.find("div", class_="widget-episodeBody").find_all("p")])
    nextEp = soup.find("a", id="contentMain-readNextEpisode")["href"]
    prevEp = soup.find("a", id="contentMain-readPreviousEpisode")["href"]
    translatedBody = AItranslate(body)

    return render_template("episode.html", chtitle=title, lines=translatedBody.split("\n"), next=nextEp, prev=prevEp)

def getChapter(wid, eid):
    con = requests.get(f"https://kakuyomu.jp/works/{wid}/episodes/{eid}").content
    soup = bs4.BeautifulSoup(con, "html.parser")
    title = soup.find("p", class_="widget-episodeTitle").text.strip()
    body = "\n".join([p.text.strip() for p in soup.find("div", class_="widget-episodeBody").find_all("p")])
    nextEp = soup.find("a", id="contentMain-readNextEpisode")["href"]
    prevEp = soup.find("a", id="contentMain-readPreviousEpisode")["href"]
    translatedBody = GoogleTranslator(source="ja", target="en").translate(text=body)
    newtitle = GoogleTranslator(source="ja", target="en").translate(text=title)
    print(title,newtitle)
    return render_template("episode.html", chtitle=newtitle, lines=translatedBody.split("\n"), next=nextEp, prev=prevEp)


app = Flask(__name__)

@app.route('/works/<int:work_id>/episodes/<int:ep_id>')
def get_episode(work_id, ep_id):
    s = getChapter(work_id, ep_id)
    if s == None:
        return "Error."
    else:
        return s
    
app.run(host="0.0.0.0", port=80)
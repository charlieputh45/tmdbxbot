from tmdbv3api import Genre
from tmdbv3api import TV
from tmdbv3api import TMDb
from tmdbv3api import Movie
from telethon import Button, events,TelegramClient
from telethon.tl.types import InputWebDocument as wb
import os


tmdb = TMDb()
tmdb.api_key = os.environ.get('TMDB_API')
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)



movie = Movie()
tv = TV()
genre = Genre()



movie_genre = genre.movie_list()
tv_genre = genre.tv_list()
all_genre = movie_genre + tv_genre
genre_dict = {}
for g in all_genre:
    genre_dict[g.get('id')] = g.get('name')


@bot.on(events.NewMessage(pattern="/start"))
async def start(e):
    user = await e.get_sender()
    await bot.send_message(e.chat_id,f"Welcome [{user.first_name}](tg://user?id={user.id}), This bot searches TheMovieDB database to get info abt movies or tv shows",buttons=Button.switch_inline(text="Search",same_peer=True))


img_prefix = "https://image.tmdb.org/t/p/w500"

@bot.on(events.InlineQuery)
async def get_movie(event):
    if event.text == '':
        pass
    
    else:
        b = event.builder
        m = movie.search(event.text)
        t = tv.search(event.text)
        a = t + m
        s = []
        print(event.text)
        err404 = "https://img.freepik.com/free-vector/error-404-nothing-found-banner_18591-27319.jpg"
        a = sorted(a, key=lambda d: d['popularity'],reverse=True)
        for i in a:
            try:
                img = i.get('poster_path')
                date = i.get('release_date')
                title = i.get('title')
                rating = i.get('vote_average')
                overview = i.get('overview')

                lttr = f"https://letterboxd.com/tmdb/{i.get('id')}"
                tm = f"https://www.themoviedb.org/tv/{i.get('id')}"
                tmmv = f"https://www.themoviedb.org/movie/{i.id}"
                btn = [[Button.url("LetterBoxd",lttr)],[Button.url("TMDB",tmmv)]]

                if img == None: continue
                thumb = img_prefix + img



                genre_ids = i.get('genre_ids')
                gen = []
                for j in genre_ids:
                    gen.append(genre_dict.get(j))

                if date == None or title == None: 
                    date = i.get('first_air_date')
                    title = i.get('name')
                    btn = Button.url("TMDB",tm)

                desc = f"year: {date.split('-')[0]}, ratings: {rating}"
                text = f"""**Name : **{title}\n**Genres : **{', '.join(gen)}\n**Release : **{date}\n**Average Rating : **{rating}\n\n**Overview : **__{overview}__\n[‎]({thumb})"""


                s.append(b.article(title=title,description=desc,thumb = wb(thumb, 0,"image/jpeg", []),text=text,buttons=btn))

            except Exception as e:
                print(e)
        
        if s == []:
            s.append(await b.article(title="Nothing Found!",description="pls check your query and try again", thumb = wb(err404, 0,"image/jpeg", []),text=f"Nothing Found! \npls check your query and try again[‎]({err404})"))

        await event.answer(s)

bot.start()
bot.run_until_disconnected()

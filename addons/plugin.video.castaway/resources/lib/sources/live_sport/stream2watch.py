from resources.lib.modules import client,webutils
import re,sys,xbmcgui
from addon.common.addon import Addon
addon = Addon('plugin.video.castaway', sys.argv)

class info():
    def __init__(self):
        self.mode = 'stream2watch'
        self.name = 'Stream2watch.co'
        self.icon = 'stream2watch.png'
        self.categorized = True
        self.paginated = False
        self.multilink = True

class main():
    def __init__(self):
        self.base = 'http://www.stream2watch.co'

    def categories(self):
        cats = [('http://www.stream2watch.co' ,'All events', 'live.png'),('http://www.stream2watch.co/sports/soccer','Football','icons/soccer.png'),('http://www.stream2watch.co/sports/football','American Football','icons/football.png'),
                ('http://www.stream2watch.co/sports/basketball','Basketball','icons/basketball.png'),('http://www.stream2watch.co/sports/boxing', 'Boxing','icons/fighting.png'),
                ('http://www.stream2watch.co/sports/baseball', 'Baseball', 'icons/baseball.png'), ('http://www.stream2watch.co/sports/hockey', 'Ice Hockey', 'icons/hockey.png'),
                ('http://www.stream2watch.co/sports/tennis', 'Tennis', 'icons/tennis.png'), ('http://www.stream2watch.co/sports/motor', 'Motorsport', 'icons/f1.png'),
                ('http://www.stream2watch.co/sports/golf', 'Golf', 'icons/golf.png'), ('http://www.stream2watch.co/sports/wrestling', 'Wrestling', 'icons/fighting.png'),
                ('http://www.stream2watch.co/sports/darts', 'Darts','icons/darts.png') ]
        return cats

    def events(self,url):
        html = client.request(url)
        soup = webutils.bs(html)
        events = soup.find('table',{'class':'streams'}).findAll('tr')
        events.pop(0)
        events = self.__prepare_events(events)
        return events

    def links(self,url):
        html = client.request(url)
        soup = webutils.bs(html)
        links = soup.find('div',{'class':'stream_codes'}).findAll('a')
        links = self.__prepare_links(links)
        return links



    @staticmethod
    def convert_time(time):
        
        li = time.split(':')
        hour,minute=li[0],li[1]
    
        import datetime
        from resources.lib.modules import pytzimp
        d = pytzimp.timezone(str(pytzimp.timezone('Europe/London'))).localize(datetime.datetime(2000 , 1, 1, hour=int(hour), minute=int(minute)))
        timezona= addon.get_setting('timezone_new')
        my_location=pytzimp.timezone(pytzimp.all_timezones[int(timezona)])
        convertido=d.astimezone(my_location)
        fmt = "%H:%M"
        time=convertido.strftime(fmt)
        return time

    def __prepare_links(self,links):
        new=[]
        precheck = addon.get_setting('link_precheck')
        if precheck=='true':
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('Checking links', 'Checking links...')
        i=1
        items = len(links)
        for link in links:
            title = link.getText()
            url = link['data-f-href']
            found = True
            perc = 100*i/items
            if precheck=='true':
                import liveresolver
                found = liveresolver.find_link(url)
                pDialog.update(perc, 'Checking:',title)
            if found:
                new.append((url,title))
            i+=1
            if (precheck=='true' and pDialog.iscanceled()): return new
        return new


    

    def __prepare_events(self,events):
        new = []
        for ev in events:
            try:
                info = ev.findAll('td')
                sport = info[0].getText()
                title = info[1].getText().replace('vs',' vs ')
                url = info[1].find('a')['href']
                timetxt = info[2].find('span')['title']
                live = info[2].getText()
                time = re.findall(', (.+?) GMT', str(timetxt))[0]
                time = self.convert_time(time)
                live = 'ends' in str(live).lower()
                color = 'orange'
                if live:
                    color = 'red'
                title = '[COLOR %s](%s)[/COLOR] (%s) [B]%s[/B]'%(color,time,sport,title)
                new.append((url,title))
            except:
                pass
        return new

    def resolve(self,url):
        import liveresolver
        return liveresolver.resolve(url,cache_timeout=0)
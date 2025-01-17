from __future__ import unicode_literals
from resources.lib.modules import client,webutils,convert
import re,urlparse,urllib,sys,os,urllib2,json,cookielib
from resources.lib.modules.log_utils import log
from addon.common.addon import Addon
addon = Addon('plugin.video.castaway', sys.argv)

AddonPath = addon.get_path()
IconPath = AddonPath + "/resources/media/"
def icon_path(filename):
    return os.path.join(IconPath, filename)

class info():
    def __init__(self):
    	self.mode = 'nbafull'
        self.name = 'nbafull.com (full replays)'
        self.icon = 'nbafull.png'
        self.paginated = True
        self.categorized = False
        self.multilink = True


class main():
	def __init__(self,url = 'http://nbafull.com'):
		self.base = 'http://nbafull.com'
		self.url = url

	def items(self):
		html = client.request(self.url)
		soup = webutils.bs(html)
		items=soup.findAll('div',{'class':'thumb'})
		out=[]
		for item in items:
			url = item.find('a')['href']
			title=item.find('a')['title'].encode('utf-8')
			title = re.sub('<[^>]*>','',title)
			out+=[[title,url,icon_path(info().icon)]]

		return out

	def links(self,url, img=' '):
		if self.base not in url:
			url = self.base + url
		ref = url
		out = []
		html = client.request(url)
		html = convert.unescape(html.decode('utf-8'))
		soup = webutils.bs(html)

		dailys = re.findall('src=[\"\'](//(?:www.)?dailymotion.com/embed/video/[^\"\']+)[\"\']',html)
		vks = re.findall('src=[\"\'](//(?:www.)?vk.com/video_ext.php[^\"\']+)[\"\']',html)
		gvid720 = re.findall('src=[\"\'](https?://.+?google.+?/[^\"\']+)" type=[\"\']video/mp4[\"\'] data-res=[\"\']720p[\"\']',html)
		gvid360 = re.findall('src=[\"\'](https?://.+?google.+?[^\"\']+)" type=[\"\']video/mp4[\"\'] data-res=[\"\']360p[\"\']',html)
		mailru = re.findall('(https?://(?:www.)?videoapi.my.mail.ru/videos/[^\"\']+)[\"\']',html)
		opnld = re.findall('(https?://(?:www.)?openload.co/[^\"\']+)[\"\']',html)
		uptstrm = re.findall('(https?://(?:www(?:[\d+])?.)?uptostream.com[^\"\']+)[\"\']',html)
		veevr = re.findall('(https?://(?:www.)?veevr.com[^\"\']+)[\"\']',html)
		plywr = re.findall('(//config.playwire.com/[^\"\']+)[\"\']',html)
		speedvideo = re.findall('(https?://(?:www.)?speedvideo.net/[^\"\']+)[\"\']',html)
		videowood = re.findall('(https?://(?:www.)?videowood.tv/video/[^\"\']+)[\"\']',html)
		wstream = re.findall('(https?://(?:www.)?wstream.video/[^\"\']+)[\"\']',html)
		urls = []

		i = 0
		for v in plywr:
			i+=1
			title = 'Playwire video %s'%i
			url = v 
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in veevr:
			i+=1
			
			url = v
			from resources.lib.resolvers import veevr
			urlx = veevr.resolve(url)
			log(urlx)
			for url in urlx:
				if url[0] not in urls:
					title = 'Veevr video %s'%url[1].replace('<sup>HD</sup>','')
					out.append((title,url[0],icon_path(info().icon)))
					urls.append(url[0])

		i = 0
		for v in uptstrm:
			from resources.lib.resolvers import uptostream
			urlx =  uptostream.resolve(v)
			log(urlx)
			i+=1
			for u in urlx:
				q = u[1]
				title = 'Uptostream video n.%s %s'%(i,q)
				url = u[0] 
				if url not in urls:
					out.append((title,url,icon_path(info().icon)))
					urls.append(url)

		i = 0
		for v in dailys:
			i+=1
			title = 'Dailymotion video %s'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in vks:
			i+=1
			title = 'VK.com video %s'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in gvid720:
			i+=1
			title = 'GVIDEO link %s 720p'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in gvid360:
			i+=1
			title = 'GVIDEO link %s 360p'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in opnld:
			i+=1
			title = 'Openload link %s'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)

		i = 0
		for v in speedvideo:
			i+=1
			title = 'Speedvideo link %s'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)
		i = 0
		for v in videowood:
			i+=1
			title = 'Videowood link %s'%i
			url = v
			if url not in urls:
				out.append((title,url,icon_path(info().icon)))
				urls.append(url)
		i = 0
		for v in wstream:
			i+=1
			title = 'Wstream link %s'%i
			url = v + '?referer=' + ref
			if url not in urls:

				out.append((title,url,icon_path(info().icon)))
				urls.append(url)


		i = 0
		for v in mailru:
			link = v
			i+=1
			title = 'Mail.ru video %s'%i
			link = link.replace('https://videoapi.my.mail.ru/videos/embed/mail/','http://videoapi.my.mail.ru/videos/mail/')
			link = link.replace('html','json')
			cookieJar = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar), urllib2.HTTPHandler())
			conn = urllib2.Request(link)
			connection = opener.open(conn)
			f = connection.read()
			connection.close()
			js = json.loads(f)
			for cookie in cookieJar:
				token = cookie.value
			js = js['videos']
			for x in js:
				url = x['url'] + '|%s'%(urllib.urlencode({'Cookie':'video_key=%s'%token, 'User-Agent':client.agent(), 'Referer':ref} ))
				title = 'Mail.ru video ' + x['key']
				if url not in urls:
					out.append((title,url,icon_path(info().icon)))
					urls.append(url)
		return out





	def resolve(self,url):
		log(url)
		if 'wstream' in url:
			from resources.lib.resolvers import wstream
			return wstream.resolve(url)

		if 'uptostream' in url:
			return url
		if 'veevr'in url:
			return url
		if 'playwire' in url:
			from resources.lib.resolvers import playwire
			return playwire.resolve(url)
	
		import urlresolver
		return urlresolver.resolve(url)




	def next_page(self):

		html = client.request(self.url)
		try:
			next_page=re.findall('<a.+?rel="next".+?href="(.+?)"',html)[0]
			if 'nbafull.com' not in next_page:
				next_page = self.base + next_page
		except:
			next_page=None
		return next_page



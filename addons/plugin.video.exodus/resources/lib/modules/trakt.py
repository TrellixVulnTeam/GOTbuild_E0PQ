# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,json,urlparse,time

from resources.lib.modules import cache
from resources.lib.modules import control
from resources.lib.modules import cleandate
from resources.lib.modules import client


def getTrakt(url, post=None):
    try:
        url = urlparse.urljoin('http://api-v2launch.trakt.tv', url)

        headers = {'Content-Type': 'application/json', 'trakt-api-key': 'c029c80fd3d3a5284ee820ba1cf7f0221da8976b8ee5e6c4af714c22fc4f46fa', 'trakt-api-version': '2'}

        if not post == None: post = json.dumps(post)


        if getTraktCredentialsInfo() == False:
            result = client.request(url, post=post, headers=headers)
            return result


        headers['Authorization'] = 'Bearer %s' % control.setting('trakt.token')

        result = client.request(url, post=post, headers=headers, output='response', error=True)
        if not (result[0] == '401' or result[0] == '405'): return result[1]


        oauth = 'http://api-v2launch.trakt.tv/oauth/token'
        opost = {'client_id': 'c029c80fd3d3a5284ee820ba1cf7f0221da8976b8ee5e6c4af714c22fc4f46fa', 'client_secret': '90a1840447a1e39d350023263902fe7010338d19789e6260f18df56a8b07a68a', 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob', 'grant_type': 'refresh_token', 'refresh_token': control.setting('trakt.refresh')}

        result = client.request(oauth, post=json.dumps(opost), headers=headers)
        result = json.loads(result)

        token, refresh = result['access_token'], result['refresh_token']

        control.setSetting(id='trakt.token', value=token)
        control.setSetting(id='trakt.refresh', value=refresh)

        headers['Authorization'] = 'Bearer %s' % token

        result = client.request(url, post=post, headers=headers)
        return result
    except:
        pass


def authTrakt():
    try:
        if getTraktCredentialsInfo() == True:
            if control.yesnoDialog(control.lang(30479).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Trakt', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.setSetting(id='trakt.user', value='')
                control.setSetting(id='trakt.token', value='')
                control.setSetting(id='trakt.refresh', value='')
            raise Exception()

        result = getTrakt('/oauth/device/code', {'client_id': 'c029c80fd3d3a5284ee820ba1cf7f0221da8976b8ee5e6c4af714c22fc4f46fa'})
        result = json.loads(result)
        verification_url = (control.lang(30416) + '[COLOR skyblue]%s[/COLOR]' % result['verification_url']).encode('utf-8')
        user_code = (control.lang(30417) + '[COLOR skyblue]%s[/COLOR]' % result['user_code']).encode('utf-8')
        expires_in = int(result['expires_in'])
        device_code = result['device_code']
        interval = result['interval']

        progressDialog = control.progressDialog
        progressDialog.create('Trakt', verification_url, user_code)

        for i in range(0, expires_in):
            try:
                if progressDialog.iscanceled(): break
                time.sleep(1)
                if not float(i) % interval == 0: raise Exception()
                r = getTrakt('/oauth/device/token', {'client_id': 'c029c80fd3d3a5284ee820ba1cf7f0221da8976b8ee5e6c4af714c22fc4f46fa', 'client_secret': '90a1840447a1e39d350023263902fe7010338d19789e6260f18df56a8b07a68a', 'code': device_code})
                r = json.loads(r)
                if 'access_token' in r: break
            except:
                pass

        try: progressDialog.close()
        except: pass

        token, refresh = r['access_token'], r['refresh_token']

        headers = {'Content-Type': 'application/json', 'trakt-api-key': 'c029c80fd3d3a5284ee820ba1cf7f0221da8976b8ee5e6c4af714c22fc4f46fa', 'trakt-api-version': '2', 'Authorization': 'Bearer %s' % token}

        result = client.request('http://api-v2launch.trakt.tv/users/me', headers=headers)
        result = json.loads(result)

        user = result['username']

        control.setSetting(id='trakt.user', value=user)
        control.setSetting(id='trakt.token', value=token)
        control.setSetting(id='trakt.refresh', value=refresh)
        raise Exception()
    except:
        control.openSettings('3.1')


def getTraktCredentialsInfo():
    user = re.sub('[^a-z0-9]', '-', control.setting('trakt.user').strip().lower())
    token = control.setting('trakt.token')
    refresh = control.setting('trakt.refresh')
    if (user == '' or token == '' or refresh == ''): return False
    return True


def getTraktIndicatorsInfo():
    indicators = control.setting('indicators') if getTraktCredentialsInfo() == False else control.setting('indicators.alt')
    indicators = True if indicators == '1' else False
    return indicators


def getTraktAddonMovieInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_movie')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def getTraktAddonEpisodeInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_episode')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def manager(name, imdb, tvdb, content):
    try:
        user = re.sub('[^a-z0-9]', '-', control.setting('trakt.user').strip().lower())
        post = {"movies": [{"ids": {"imdb": imdb}}]} if content == 'movie' else {"shows": [{"ids": {"tvdb": tvdb}}]}

        items = [(control.lang(30472).encode('utf-8'), '/sync/collection')]
        items += [(control.lang(30473).encode('utf-8'), '/sync/collection/remove')]
        items += [(control.lang(30474).encode('utf-8'), '/sync/watchlist')]
        items += [(control.lang(30475).encode('utf-8'), '/sync/watchlist/remove')]
        items += [(control.lang(30476).encode('utf-8'), '/users/%s/lists/%s/items' % (user, '%s'))]

        result = getTrakt('/users/%s/lists' % user)
        result = json.loads(result)
        lists = [(i['name'], i['ids']['slug']) for i in result]
        lists = [lists[i//2] for i in range(len(lists)*2)]
        for i in range(0, len(lists), 2):
            lists[i] = ((control.lang(30477) + ' ' + lists[i][0]).encode('utf-8'), '/users/%s/lists/%s/items' % (user, lists[i][1]))
        for i in range(1, len(lists), 2):
            lists[i] = ((control.lang(30478) + ' ' + lists[i][0]).encode('utf-8'), '/users/%s/lists/%s/items/remove' % (user, lists[i][1]))
        items += lists

        select = control.selectDialog([i[0] for i in items], control.lang(30471).encode('utf-8'))

        if select == -1:
            return
        elif select == 4:
            t = control.lang(30476).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            new = k.getText() if k.isConfirmed() else None
            if (new == None or new == ''): return
            url = '/users/%s/lists' % user
            result = getTrakt('/users/%s/lists' % user, post={"name": new, "privacy": "private"})

            try: slug = json.loads(result)['ids']['slug']
            except: return control.infoDialog('Failed', heading=name)
            result = getTrakt(items[select][1] % slug, post=post)
        else:
            result = getTrakt(items[select][1], post=post)

        info = 'Successful' if not result == None else 'Failed'
        control.infoDialog(info, heading=name)
    except:
        return


def getActivity():
    try:
        result = getTrakt('/sync/last_activities')
        i = json.loads(result)

        activity = []
        activity.append(i['movies']['collected_at'])
        activity.append(i['episodes']['collected_at'])
        activity.append(i['movies']['watchlisted_at'])
        activity.append(i['shows']['watchlisted_at'])
        activity.append(i['seasons']['watchlisted_at'])
        activity.append(i['episodes']['watchlisted_at'])
        activity.append(i['lists']['updated_at'])
        activity.append(i['lists']['liked_at'])
        activity = [int(cleandate.iso_2_utc(i)) for i in activity]
        activity = sorted(activity, key=int)[-1]

        return activity
    except:
        pass


def cachesyncMovies(timeout=0):
    indicators = cache.get(syncMovies, timeout, re.sub('[^a-z0-9]', '-', control.setting('trakt.user').strip().lower()), table='trakt')
    return indicators


def syncMovies(user):
    try:
        if getTraktCredentialsInfo() == False: return
        indicators = getTrakt('/users/%s/watched/movies' % user)
        indicators = json.loads(indicators)
        indicators = [i['movie']['ids'] for i in indicators]
        indicators = [str(i['imdb']) for i in indicators if 'imdb' in i]
        return indicators
    except:
        pass


def cachesyncTVShows(timeout=0):
    indicators = cache.get(syncTVShows, timeout, re.sub('[^a-z0-9]', '-', control.setting('trakt.user').strip().lower()), table='trakt')
    return indicators


def syncTVShows(user):
    try:
        if getTraktCredentialsInfo() == False: return
        indicators = getTrakt('/users/%s/watched/shows?extended=full' % user)
        indicators = json.loads(indicators)
        indicators = [(i['show']['ids']['tvdb'], i['show']['aired_episodes'], sum([[(s['number'], e['number']) for e in s['episodes']] for s in i['seasons']], [])) for i in indicators]
        indicators = [(str(i[0]), int(i[1]), i[2]) for i in indicators]
        return indicators
    except:
        pass


def markMovieAsWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return getTrakt('/sync/history', {"movies": [{"ids": {"imdb": imdb}}]})


def markMovieAsNotWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return getTrakt('/sync/history/remove', {"movies": [{"ids": {"imdb": imdb}}]})


def markTVShowAsWatched(tvdb):
    return getTrakt('/sync/history', {"shows": [{"ids": {"tvdb": tvdb}}]})


def markTVShowAsNotWatched(tvdb):
    return getTrakt('/sync/history/remove', {"shows": [{"ids": {"tvdb": tvdb}}]})


def markEpisodeAsWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})


def markEpisodeAsNotWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})


def getMovieSummary(id):
    return getTrakt('/movies/%s' % id)


def getTVShowSummary(id):
    return getTrakt('/shows/%s' % id)



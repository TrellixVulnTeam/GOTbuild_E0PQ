# -*- coding: utf-8 -*-
import os, urllib, xbmc, xbmcgui, zipfile

# def ExtractAll(_in, _out):
	# try:
		# zin = zipfile.ZipFile(_in, 'r')
		# zin.extractall(_out)
		# zin.close()
	# except Exception, e:
		# print str(e)
		# return False

	# return True
	
# def UpdateRepo(url= "https://github.com/cubicle-vdo/xbmc-israel/raw/master/repo/repository.xbmc-israel/repository.xbmc-israel-1.0.4.zip",repoName='repository.xbmc-israel', alert=False):
	
	# if os.path.exists(os.path.join(xbmc.translatePath("special://home/addons/").decode("utf-8"), repoName)):
		# return True
	# #print repoName
	
	# if alert:
		# dialog = xbmcgui.Dialog()
		# go_on=dialog.yesno('IsraelSoprts','האם ברצונך להתקין את התוסף', repoName)
		# if not go_on:
			# return False
	# addonsDir = xbmc.translatePath(os.path.join('special://home', 'addons')).decode("utf-8")
	# packageFile = os.path.join(addonsDir, 'packages', 'isr.zip')
	
	# urllib.urlretrieve(url, packageFile)
	# ExtractAll(packageFile, addonsDir)
		
	# try:
		# os.remove(packageFile)
	# except:
		# pass
			
	# xbmc.executebuiltin("UpdateLocalAddons")
	# xbmc.executebuiltin("UpdateAddonRepos")
	# return True
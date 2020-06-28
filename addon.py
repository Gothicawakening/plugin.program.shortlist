import sys

import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import os
import pickle
from shortlistitem import ShortlistItem
from database import *

base_url = sys.argv[0]

__addon__       = xbmcaddon.Addon(id='plugin.program.shortlist')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__language__     = __addon__.getLocalizedString

addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.addSortMethod( addon_handle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
xbmcplugin.addSortMethod( addon_handle, xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.addSortMethod( addon_handle, xbmcplugin.SORT_METHOD_DURATION)
xbmcplugin.addSortMethod( addon_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
xbmcplugin.addSortMethod( addon_handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)

action = args.get( 'action' )
dbName = args.get( 'dbName' )
databaseName = args.get( 'databaseName' )

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

if action is not None:
    # Process action
    filename = args.get( 'filename' )

    # Load database
    if dbName is not None:
        name = dbName[0].lower() + ".db"
        database = getDatabaseByName( name )
    else:
        name = ""
        database = None

    if action[0] == 'delete':
        # Delets specified item
        if filename is not None:
            deleteItem( database, filename[0] )

    elif action[0] == 'moveUp':
        # Move item up in the list
        if filename is not None:
            moveUp( database, filename[0] )

    elif action[0] == 'moveDn':
        # Move item up in the list
        if filename is not None:
            moveDown( database, filename[0] )

    elif action[0] == 'moveTop':
        # Move item to start the list
        if filename is not None:
            moveToTop( database, filename[0] )

    elif action[0] == 'moveBottom':
        # Move item to end the list
        if filename is not None:
            moveToBottom( database, filename[0] )

    elif action[0] == 'deleteList':
        # Delete a list database files
        if databaseName is not None:
            # Delete files\
            nameNice = databaseName[0]
            name = nameNice.lower() + ".db"
            filename = __addondir__ + name

            dialog = xbmcgui.Dialog()

            # ret = dialog.yesno('Kodi', 'Do you want to delete the "' + nameNice + '" shortlist?')
            ret = dialog.yesno('Kodi', __language__( 30009 ) + ' "' + nameNice + '" ' + __language__( 30010 ) )

            if ret == True:
                os.remove( filename )


    elif action[0] == 'createList':
        # Add a new list to the database
        dialog = xbmcgui.Dialog()
        nameNice = dialog.input(__language__( 30011 ), type=xbmcgui.INPUT_ALPHANUM)

        database = None

        if nameNice is not None and nameNice is not "":
            name = nameNice.lower( ) + ".db"

            # Build database
            database = []
            # No need to save it's it's done below

    else:
        xbmc.log("SHORTLIST: Action Unknown: " + action)

    if database is not None:
        saveDatabaseByName( database, name )

    # Refresh the file list
    xbmc.executebuiltin("Container.Refresh")
else:
    # Show lists
    if dbName is not None:
        # Show list of movies
        xbmcplugin.setContent(addon_handle, 'movies')

        # Load database
        name = dbName[0].lower() + ".db"
        database = getDatabaseByName( name )

        # Add each item to the directory
        count = 0
        for item in database:
            # Create a listitem with thumbnail and poster
            li = xbmcgui.ListItem(item.title, iconImage='DefaultVideo.png')
            li.setArt( { 'thumb' : item.thumb, 'poster' : item.poster, 'fanart' : item.fanart } )

            filename = item.filename

            # Add some video info
            info = {}
            info['year'] = item.year
            info['duration'] = item.duration
            info['rating'] = item.rating
            info['plot'] = item.plot
            info['plotoutline'] = item.plotoutline
            info['title'] = item.title
            info['count'] = count
            li.setInfo( 'video', info )

            # Build the context menu items
            commands = []

            params = urllib.urlencode( {'action': 'delete', 'dbName' : dbName[0], 'filename': filename } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Remove from Shortlist', script, ) )
            commands.append( ( __language__( 30001 ), script, ) )

            params = urllib.urlencode( {'action': 'moveUp', 'dbName' : dbName[0], 'filename': filename} )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Move Up', script, ) )
            commands.append( ( __language__( 30002 ), script, ) )

            params = urllib.urlencode( {'action': 'moveDn', 'dbName' : dbName[0], 'filename': filename } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Move Down', script, ) )
            commands.append( ( __language__( 30003 ), script, ) )

            params = urllib.urlencode( {'action': 'moveTop', 'dbName' : dbName[0], 'filename': filename } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Move To Top', script, ) )
            commands.append( ( __language__( 30004 ), script, ) )

            params = urllib.urlencode( {'action': 'moveBottom', 'dbName' : dbName[0], 'filename': filename } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Move To Bottom', script, ) )
            commands.append( ( __language__( 30005 ), script, ) )

            # commands.append( ( 'Show Info', 'Action(Info)', ) )
            commands.append( ( __language__( 30006 ), script, ) )

            li.addContextMenuItems( commands )

            # Add listitem to directory
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=filename, listitem=li)
            count = count + 1
        xbmcplugin.endOfDirectory(addon_handle)

    else:
        # Show available lists
        xbmcplugin.setContent(addon_handle, 'files')

        # Add each item to the directory
        dbList = listDatabases()

        for db in dbList:
            li = xbmcgui.ListItem( db, iconImage='DefaultFolder.png')
            # li.setProperty('isFolder', 'true')
            # li.setProperty('isPlayable', 'true')
            filename = build_url({'dbName': db})
            is_folder = True

            # Build the context menu items
            commands = []

            params = urllib.urlencode( {'action': 'deleteList', 'databaseName': db } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Delete Shortlist', script, ) )
            commands.append( ( __language__( 30007 ), script, ) )

            params = urllib.urlencode( {'action': 'createList' } )
            script = 'XBMC.RunPlugin("plugin://plugin.program.shortlist/?%s")' % params
            # commands.append( ( 'Create Shortlist', script, ) )
            commands.append( ( __language__( 30008 ), script, ) )

            li.addContextMenuItems( commands )

            # xbmc.log( filename, xbmc.LOGNOTICE);
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=filename, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)



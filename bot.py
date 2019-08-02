import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

client = discord.Client()
json_key = 'Gnor Bot json_key.json'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
global all_sheet_values

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1KrRiRQ_J9laMaZyf9orBZvedbepJXI3LEbaUylMZ1TM").sheet1
all_sheet_values = sheet.get_all_values()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_join(member):
    defaultchannel = discord.utils.get(member.server.channels, name = settings['custom']['default_channel'])
    defaultrole = discord.utils.get(member.server.roles, name = settings['custom']['default_role'])
    if defaultchannel is not None and defaultrole is not None:
        await client.add_roles(member, defaultrole)
        await client.send_message(defaultchannel, member.name + ' has joined the server')
    else:
        print('Default channel or default role not found for join notification')

@client.event
async def on_member_leave(member):
    defaultchannel = discord.utils.get(member.server.channels, name = settings['custom']['default_channel'])
    if defaultchannel is not None:
        await client.send_message(defaultchannel, member.name + ' has left the server')
    else:
        print('Default channel not found for leave notification')

@client.event
async def on_message(message):
    if message.content.startswith('uwu'):
        await client.add_reaction(message, 'gnaruwu:389219155288653837')

    elif message.content.startswith('?role '):
        newrole = discord.utils.get(message.author.server.roles, name = message.content[6:])
        if newrole is None:
            await client.send_message(message.channel, 'No such role')
        elif getrolelayer(newrole) > 0:
            await client.send_message(message.channel, 'You do not have the permit to join/leave this role')
        elif(not newrole in message.author.roles):
            await client.add_roles(message.author, newrole)
            await client.send_message(message.channel, 'You joined ' + newrole.name)
        else:
            await client.remove_roles(message.author, newrole)
            await client.send_message(message.channel, 'You left ' + newrole.name)
    
    elif message.content.startswith('?matchup '):
        i = find_sheet_row_by_matchup(message.content[9:])
        if i is not None:
            message_string = ('```Matchup: Gnar vs. ' + all_sheet_values[i][0] +
                              '\nDifficulty: ' + all_sheet_values[i][1] +
                              '\nStat Shards: ' + all_sheet_values[i][8] +
                              '\nStarting Items: ' + all_sheet_values[i][9] +
                              '\nCore Items: ' + all_sheet_values[i][10] +
                              '\n\nInformation: ' + all_sheet_values[i][11] + '```')
            await client.send_message(message.channel, message_string)
        else:
            await client.send_message(message.channel, 'Could not find matchup info for ' + message.content[9:])

    elif message.content.startswith('?refresh matchups') and \
            'Mega Gnar' in [role.name for role in message.author.roles]:
        all_sheet_values = sheet.get_all_values()
        await client.send_message(message.channel, 'Updated matchups!')

    elif message.content.startswith('?ranks'):
        roles = message.author.server.roles
        member_count = []
        for index in roles:
            member_count.append(0)
        for index1 in message.author.server.members:
            i = 0
            for index2 in roles:
                if index2 in index1.roles:
                    member_count[i]+=1
                i+=1
        string = 'Server ranks:\n'
        i = 0
        for index in roles:
            if not index.is_everyone and getrolelayer(index) == 0:
                string += index.name + ": " + str(member_count[i]) + " members\n"
            i+=1
        await client.send_message(message.channel, string)

    elif message.content.startswith('?assignrole '):
        if getperm(message.author) < 3:
            await client.send_message(message.channel, 'You do not have the permit to access this command')
            return
        arguments = message.content.split(' ', 2)
        role = discord.utils.get(message.author.server.roles, name = arguments[2])
        if role is None:
            await client.send_message(message.channel, 'No such role')
        elif not message.mentions:
            await client.send_message(message.channel, 'No user mentioned')
        elif getperm(message.author) < getrolelayer(role):
            await client.send_message(message.channel, 'You do not have the permit to assign this role')
        elif getperm(message.channel.server.me) <= getrolelayer(role):
            await client.send_message(message.channel, 'The bot does not have the permit to assign this role')
        elif role not in message.mentions[0].roles:
            await client.add_roles(message.mentions[0], role)
            await client.send_message(message.channel, message.mentions[0].name + ' has joined ' + role.name)
        else:
            await client.remove_roles(message.mentions[0], role)
            await client.send_message(message.channel, message.mentions[0].name + ' has left ' + role.name)

    else:
        arguments = message.content.split(' ')
        output = ''
        for customcommand in settings['custom_commands']:
            if arguments[0] == customcommand:
                output = settings['custom_commands'][customcommand]
        output = output.replace('{user}', message.author.name)
        output = output.replace('{server}', message.author.server.name)
        output = output.replace('{channel}', message.channel.name)
        if output != '':
            await client.send_message(message.channel, output)

            
        
def find_sheet_row_by_matchup(champion):
    for index, sublist in enumerate(all_sheet_values, start=3):
        if sublist[0].lower().replace('\'', '').replace(' ', '') \
                == champion.lower().replace('\'', '').replace(' ', ''):
            return index - 3

def getperm(member):
    maxprio = 0
    j = 1
    while j <= len(settings['perms']):
        for index in member.roles:
            if index.name in settings['perms']['layer' + str(j)]:
                maxprio = j
        j+=1
    return maxprio

def getrolelayer(role):
    layer = 0
    j = 1
    while j <= len(settings['perms']):
        if role.name in settings['perms']['layer' + str(j)]:
            layer = j
        j+=1
    return layer

with open('bot_info.txt') as file:
    lines = file.readlines()
    bot = lines[1].strip()

with open('settings.json') as set:
    settings = json.load(set)

client.run(bot)

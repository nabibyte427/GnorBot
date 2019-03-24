import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials

client = discord.Client()
json_key = 'Gnor Bot json_key.json'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

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
async def on_message(message):
    global all_sheet_values
    if message.content.startswith('uwu'):
        await client.add_reaction(message, 'gnaruwu:389219155288653837')

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


def find_sheet_row_by_matchup(champion):
    for index, sublist in enumerate(all_sheet_values, start=3):
        if sublist[0].lower().replace('\'', '').replace(' ', '') \
                == champion.lower().replace('\'', '').replace(' ', ''):
            return index - 3

bot = ''
with open('bot_info.txt') as file:
    lines = file.readlines()
    bot = lines[1].strip()
client.run(bot)

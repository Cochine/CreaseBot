import discord
from riotwatcher import RiotWatcher


def initialize_watcher(tokens):
    global watcher
    global my_region
    watcher = RiotWatcher(tokens['riot_token'])
    my_region = 'na1'


async def get_stats(ctx, bot, in_game_name: str, stat_type: str):
    """Gets the league profile of the user"""

    message = ctx.message.content[1:]
    arguments = message.split()
    stat_type = stat_type.lower()
    stat_type = get_queue_type(stat_type)
    await bot.send_typing(ctx.message.channel)

    if len(arguments) != 3 and len(arguments) != 2:
        print("Invalid number of arguments given.")
        await bot.send_message(ctx.message.channel, "Invalid number of arguments given.")
        return

    try:
        player = watcher.summoner.by_name(my_region, in_game_name)
        league_positions = watcher.league.positions_by_summoner('na1', player['id'])
        if league_positions == []:
            ranked_stats = None
        else:
            for queue in league_positions:
                if queue['queueType'] == stat_type:
                    ranked_stats = queue
                    break
                else:
                    ranked_stats = None


    except Exception as error:
        await bot.send_message(ctx.message.channel, "Error fetching player stats! Try again!")
        print(error)
        return

    if not ranked_stats:

        embed = discord.Embed(
            title="%s" % (player['name']),
            description="No ranked stats available",
            url='http://na.op.gg/summoner/userName=%s' % in_game_name,
            color=0xF8EC9B
        )
        embed.add_field(name="Summoner Level:", value="%s" % player['summonerLevel'])
        await bot.send_message(ctx.message.channel, embed=embed)

    else:
        ranked_stats = ranked_stats
        translated_rank = numerals_to_digits(ranked_stats['rank'])
        total_games = int(ranked_stats['wins']) + (int(ranked_stats['losses']))
        win_rate = int((int(ranked_stats['wins']) / total_games) * 100)
        embed = discord.Embed(
            color=tier_colour(ranked_stats['tier'].lower())
        )
        embed.set_author(name=player['name'],
                         url='http://na.op.gg/summoner/userName=%s' % in_game_name,
                         icon_url="http://opgg-static.akamaized.net/images/medals/%s_%s.png" % (
            ranked_stats['tier'].lower(), translated_rank))
        embed.add_field(name="Summoner Level:", value="%s" % player['summonerLevel'])
        embed.add_field(name="Ranked Tier:", value="%s %s" % (ranked_stats['tier'], ranked_stats['rank']))
        embed.add_field(name="League Points:", value="%s" % ranked_stats['leaguePoints'])
        embed.add_field(name="Winrate:", value="%s%%" % win_rate)
        embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/8.15.1/img/profileicon/%s.png" %
            player['profileIconId'])
        embed.set_footer(text=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        await bot.send_message(ctx.message.channel, embed=embed)

def get_queue_type(type):
    if type == 'solo':
        return 'RANKED_SOLO_5x5'
    elif type == 'flex':
        return 'RANKED_FLEX_SR'
    elif type == '3v3' or type == 'FlexTT':
        return 'RANKED_FLEX_TT'

def tier_colour(tier):
    if tier == "challenger":
        return 0x043E7C
    elif tier == "master":
        return 0x12A185
    elif tier == "diamond":
        return 0x4F8ACB
    elif tier == "platinum":
        return 0x4A9C77
    elif tier == "gold":
        return 0xF8EC9B
    elif tier == "silver":
        return 0x808D88
    elif tier == "bronze":
        return 0x624935
    else:
        print("Not a valid tier!")
        return


def numerals_to_digits(numeral):
    if numeral == 'V':
        return 5
    elif numeral == 'IV':
        return 4
    elif numeral == 'III':
        return 3
    elif numeral == 'II':
        return 2
    elif numeral == 'I':
        return 1
    else:
        print("Not a valid numeral!")
        return
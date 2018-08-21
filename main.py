from models import session, Clock, User

import discord ## pip3 install git+...
import sys
import os
import aiohttp ## pip3 install aiohttp
import asyncio
import json
import time
import pytz
from datetime import datetime
from configparser import SafeConfigParser
from datetime import datetime
import traceback


class BotClient(discord.AutoShardedClient):
    def __init__(self, *args, **kwargs):
        super(BotClient, self).__init__(*args, **kwargs)

        self.commands = {
            'ping' : self.ping,
            'help' : self.help,
            'info': self.info,
            'new' : self.new,
            'personal' : self.personal,
            'check' : self.check,
        }

        self.config = SafeConfigParser()
        self.config.read('config.ini')


    async def send(self):
        guild_count = len(self.guilds)

        if self.config.get('TOKENS', 'discordbots'):

            session = aiohttp.ClientSession()
            dump = json.dumps({
                'server_count': len(client.guilds)
            })

            head = {
                'authorization': self.config.get('TOKENS', 'discordbots'),
                'content-type' : 'application/json'
            }

            url = 'https://discordbots.org/api/bots/stats'
            async with session.post(url, data=dump, headers=head) as resp:
                print('returned {0.status} for {1}'.format(resp, dump))

            await session.close()


    async def on_ready(self):

        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------------')
        await client.change_presence(activity=discord.Game(name='@{} info'.format(self.user.name)))


    async def on_guild_join(self, guild):
        await self.send()

        await self.welcome(guild)


    async def on_guild_remove(self, guild):
        await self.send()

        await self.leave_cleanup(guild.id)


    async def leave_cleanup(self, id):
        channels = session.query(Clock).filter(Clock.guild_id == id)
        channels.delete(synchronize_session='fetch')


    async def welcome(self, guild, *args):
        if isinstance(guild, discord.Message):
            guild = guild.guild

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages and not channel.is_nsfw():
                await channel.send('Thank you for adding Clock! To begin, type `timezone help`.')
                break
            else:
                continue


    async def on_message(self, message):

        if isinstance(message.channel, discord.DMChannel) or message.author.bot or message.content is None:
            return

        try:
            if await self.get_cmd(message):
                session.commit()

        except Exception as e:
            traceback.print_exc()
            await message.channel.send('Internal exception detected in command, {}'.format(e))


    async def get_cmd(self, message):

        prefix = 'timezone '

        command = None

        if message.content[0:len(prefix)] == prefix:
            command = message.content.split(' ')[1]
            stripped = (message.content + ' ').split(' ', 2)[-1].strip()

        elif self.user.id in map(lambda x: x.id, message.mentions) and len(message.content.split(' ')) > 1:
            command = message.content.split(' ')[1]
            stripped = (message.content + ' ').split(' ', 2)[-1].strip()

        if command is not None:
            if command in self.commands.keys():
                await self.commands[command](message, stripped)
                return True

        return False


    async def ping(self, message, stripped, server):
        t = message.created_at.timestamp()
        e = await message.channel.send('pong')
        delta = e.created_at.timestamp() - t

        await e.edit(content='Pong! {}ms round trip'.format(round(delta * 1000)))


    async def help(self, message, stripped, server):
        embed = discord.Embed(title='HELP', color=self.color, description=
        '''
        '''.format(self.user.name)
        )
        await message.channel.send(embed=embed)


    async def info(self, message, stripped, server):
        em = discord.Embed(title='INFO', color=self.color, description=
        '''
        '''.format(user=self.user.name, p=server.prefix)
        )

        await message.channel.send(embed=em)


    async def new(self, message, stripped):
        if stripped.lower() not in [x.lower() for x in pytz.all_timezones]:
            await message.channel.send('Timezone not recognised. Please view a list here: [insert link]')

        else:
            tz = stripped

            t = datetime.now(pytz.timezone(tz))

            c = await message.guild.create_voice_channel(
                '🕒 {} ({})'.format(t.strftime('%H:%M'), tz),

                overwrites= {
                    message.guild.default_role: discord.PermissionOverwrite(connect=False)
                }
            )

            chan = Clock(channel_id=c.id, guild_id=message.guild.id, timezone=tz)
            session.add(chan)


    async def personal(self, message, stripped):
        if stripped.lower() not in [x.lower() for x in pytz.all_timezones]:
            await message.channel.send('Timezone not recognised. Please view a list here: [insert link]')

        else:
            user = session.query(User).filter(User.id == message.author.id).first()
            if user is None:
                user = User(id=message.author.id, timezone='UTC')
                session.add(user)
                session.commit()

            user = session.query(User).filter(User.id == message.author.id).first()

            tz = stripped

            t = datetime.now(pytz.timezone(tz))

            await message.channel.send(
                'Your current time should be {}'.format(t.strftime('%H:%M'))
            )

            user.timezone = stripped


    async def check(self, message, stripped):
        user = session.query(User).filter(User.id == message.mentions[0].id).first()
        if user is None:
            await message.channel.send('User hasn\'t specified a timezone')
        else:
            t = datetime.now(pytz.timezone(user.timezone))

            await message.channel.send(
                '{}\'s current time is {}'.format(message.mentions[0].name, t.strftime('%H:%M'))
            )

        user.timezone = stripped


    async def update(self):
        await self.wait_until_ready()
        while not client.is_closed():

            for channel in session.query(Clock):
                guild = self.get_guild(channel.guild_id)

                if guild is None:
                    channel.delete(synchronize_session='fetch')

                else:
                    c = guild.get_channel(channel.channel_id)
                    if c is None:
                        continue

                    else:
                        t = datetime.now(pytz.timezone(channel.timezone))
                        await c.edit(name='🕒 {} ({})'.format(t.strftime('%H:%M:%S'), channel.timezone))


            await asyncio.sleep(0.2)


client = BotClient()

try:

    client.loop.create_task(client.update())
    client.run(client.config.get('TOKENS', 'bot'))
except Exception as e:
    print('Error detected. Restarting in 15 seconds.')
    print(sys.exc_info())
    time.sleep(15)

    os.execl(sys.executable, sys.executable, *sys.argv)

import discord
import random
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class MyClient(discord.Client):
    # Logs the bot on to the configured Discord server
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    # Starts the routine when a user sends the word $box to chat.
    async def on_message(self, message):
        # check to make sure message is not self generated
        if message.author.id == self.user.id:
            return

        if message.content.startswith('$box'):
            intro_message = ('Welcome to the boxing ring! Engage in a fisticuffs battle with Billy the Bot to find out '
                             'who is King of the Guild! As a brave combatant, you can enter $jab, $hook or $uppercut ' 
                             'to strike Billy the Bot and claim your spot as King of the Guild. Good luck and let the '
                             'battle begin!')
            await message.channel.send(intro_message)

            def hit_type(player_message):
                hit_success = random.choice([True, False])
                if not hit_success:
                    msg = 'Strike missed! No damage dealt'
                    damage_dealt = 0
                elif player_message.lower() == '$jab' and hit_success:
                    damage_dealt = random.randint(1, 5)
                    msg = f'A jab was landed dealing {damage_dealt} points of damage'
                elif player_message.lower() == '$hook':
                    damage_dealt = random.randint(6, 12)
                    msg = f'A hook was landed dealing {damage_dealt} points of damage'
                elif player_message.lower() == '$uppercut':
                    damage_dealt = random.randint(13, 20)
                    msg = f'An uppercut was landed dealing {damage_dealt} points of damage'
                else:
                    damage_dealt = 0
                    msg = 'Illegal strike! No damage dealt!'

                return msg, damage_dealt

            def bot_strike_calculator():
                possible_strikes = ['$jab', '$hook', '$uppercut', '$lowercut']
                strike_type = random.choice(possible_strikes)
                strike_value = hit_type(strike_type)
                return strike_value

            player_health = 100
            bot_health = 100

            while player_health > 0 and bot_health > 0:
                try:
                    player_msg = await self.wait_for('message', timeout=30.0)
                    player_hit_points = hit_type(player_msg.content)
                    bot_health -= player_hit_points[1]
                    await message.channel.send(f'{player_hit_points[0]}.')
                    bot_hit_points = bot_strike_calculator()
                    player_health -= bot_hit_points[1]
                    await message.channel.send(f'{bot_hit_points[0]} by Billy the Bot!')
                    await message.channel.send(f'Your health is at {player_health} and Billy the Bot has {bot_health}.')
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long and Billy the Bot knocked you out.')

            if bot_health <= 0:
                await message.channel.send('Congratulations! You knocked out Billy the Bot! Thanks for playing!')
            else:
                await message.channel.send(f'Oops. Billy the Bot knocked you out, try again and thanks for playing!')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)

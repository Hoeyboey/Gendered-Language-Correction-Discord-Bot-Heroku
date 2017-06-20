import discord
import asyncio

client = discord.Client()

async def public_vague_callout(message, client):
	print(message.content)
	await client.send_message(message.channel, 'Please don\'t say dude or guys!')

@client.event
async def on_ready():
	print('I\'m working!')
	print(client.user.id)

@client.event
async def on_message(message):
	if message.author.id != client.user.id:
		if 'dude' in message.content or 'guys' in message.content:
			print(message.author.id)
			await public_vague_callout(message, client)

@client.event
async def on_server_join(server):
	serverOwner = server.owner 
	await client.send_message(serverOwner, 'I\'ve just been invited to your server! Hi! I just need to run through some things with you!')
	await client.send_message(serverOwner, 'First of all, we need to decide what words you want me to call out. By default, we include "dude" and "guys", but you\'re able to add any more if you want.')
	await client.send_message(serverOwner, 'Do you want to add any more blacklisted words? Y/N')
	def check(msg):
		if msg.content == 'Y' or msg.content == 'N':
			return True
		else:
			return False
	newMessage = await client.wait_for_message(author=serverOwner, check=check)
	print(newMessage)

client.run('TOKEN')

# The actual token has been replaced so you can't do anything jammy with my bot. I see you.
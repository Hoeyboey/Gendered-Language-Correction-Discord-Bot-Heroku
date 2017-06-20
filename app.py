import discord
import asyncio

client = discord.Client()

async def public_vague_callout(message, client):
	print(message.content)
	await client.send_message(message.channel, 'Please don\'t say dude.')

@client.event
async def on_ready():
	print('I\'m working!')
	print(client.user.id)

@client.event
async def on_message(message):
	if message.author.id != client.user.id:
		if 'dude' in message.content:
			print(message.author.id)
			await public_vague_callout(message, client)

@client.event
async def on_server_join(server):
	serverOwner = server.owner 
	await client.send_message(serverOwner, 'I\'ve just been invited to your server! Hi!')

client.run('TOKEN')

# The actual token has been replaced so you can't do anything jammy with my bot. I see you.
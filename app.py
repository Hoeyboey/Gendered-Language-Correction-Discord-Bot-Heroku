import discord
import asyncio

client = discord.Client()

blacklist = ['Dude', 'Dudes', 'Guys', 'dude', 'dudes', 'guys']

async def public_vague_callout(message, client):
	print(message.content)
	await client.send_message(message.channel, 'Please don\'t say dude or guys!')

def check(msg):
	if msg.channel.is_private:
		if msg.content == 'Y' or msg.content == 'N':
			return True
		else:
			return False

def check2(msg):
	if msg.channel.is_private:
		return True
	else:
		return False

async def blacklisting(client, serverOwner):
	newMessage = await client.wait_for_message(author=serverOwner, check=check)
	if newMessage.content == 'Y':
		await client.send_message(serverOwner, 'Alright! Please type the word you want to add to the blacklist.')
		addToBlacklist = await client.wait_for_message(author=serverOwner, check=check2)
		if addToBlacklist not in blacklist:
			blacklist.append(addToBlacklist)
		else:
			await client.send_message(serverOwner, 'This word is already in the blacklist!')
		await client.send_message(serverOwner, 'Okay! Want to add any more? Y/N')
		await blacklisting(client, serverOwner)
	else:
		await client.send_message(serverOwner, 'We\'re all done then! If you want to add something new to the list, DM me with \'!help\'!')
	

@client.event
async def on_ready():
	print('I\'m working!')
	print(client.user.id)

@client.event
async def on_message(message):
	if message.author.id != client.user.id:
		if message.content.title() in blacklist:
			print(message.author.id)
			await public_vague_callout(message, client)

@client.event
async def on_server_join(server):
	serverOwner = server.owner 
	await client.send_message(serverOwner, 'I\'ve just been invited to your server! Hi! I just need to run through some things with you!')
	await client.send_message(serverOwner, 'First of all, we need to decide what words you want me to call out. By default, we include "dude" and "guys", but you\'re able to add any more if you want.')
	await client.send_message(serverOwner, 'Do you want to add any more blacklisted words? Y/N')
	await blacklisting(client, serverOwner)

client.run('TOKEN')

# The actual token has been replaced so you can't do anything jammy with my bot. I see you.
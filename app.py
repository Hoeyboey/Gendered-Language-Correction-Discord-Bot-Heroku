import discord
import asyncio
import sys
import json

client = discord.Client()

blacklists = {}

blacklist = ['DUDE', 'DUDES', 'GUYS']
serverJoinMessages = ['I\'ve just been invited to your server! Hi! I just need to run through some things with you!', 'First of all, we need to decide what words you want me to call out. By default, we include "dude" and "guys", but you\'re able to add any more if you want.', 'Do you want to add any more blacklisted words? Y/N']

async def public_vague_callout(message, client):
	await client.send_message(message.channel, 'Please don\'t say dude or guys!')

def writeBlacklistsToFile():
	fullCurrentBlacklists = json.dumps(blacklists)
	with open('blacklists.json', 'w') as f:
		f.write(fullCurrentBlacklists)

def readExistingBlacklists():
	with open('blacklists.json', 'r') as f:
		unserializedBlacklists = f.read()
	global blacklists
	blacklists = json.loads(unserializedBlacklists)

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

async def blacklisting(client, serverOwner, serverId):
	newMessage = await client.wait_for_message(author=serverOwner, check=check)
	if newMessage.content.upper() == 'Y':
		await client.send_message(serverOwner, 'Alright! Please type the word you want to add to the blacklist.')
		addToBlacklist = await client.wait_for_message(author=serverOwner, check=check2)
		addToBlacklistStr = addToBlacklist.content.upper()
		if addToBlacklistStr not in blacklists[serverId]:
			blacklists[serverId].append(addToBlacklistStr)
			writeBlacklistsToFile()
		else:
			await client.send_message(serverOwner, 'This word is already in the blacklist!')
		await client.send_message(serverOwner, 'Okay! Want to add any more? Y/N')
		await blacklisting(client, serverOwner, serverId)
	else:
		await client.send_message(serverOwner, 'We\'re all done then! If you want to add something new to the list, DM me with \'!help\'!')
	

@client.event
async def on_ready():
	print('I\'m working!')
	readExistingBlacklists()
	serversCurrentlyJoined = client.servers
	for x in serversCurrentlyJoined:
		print(x.id)
		if x.id not in blacklists.keys():
			print('Intro method')
			serverOwner = x.owner
			serverId = x.id
			blacklists[serverId] = list(blacklist)
			writeBlacklistsToFile()
			for message in serverJoinMessages:
				await client.send_message(serverOwner, message)
			await blacklisting(client, serverOwner, serverId)

@client.event
async def on_message(message):
	if message.server != None:
		if message.author.id != client.user.id:
			for word in blacklists[str(message.server.id)]:
				if word in message.content.upper():
					await public_vague_callout(message, client)

@client.event
async def on_server_join(server):
	serverId = str(server.id)
	blacklists[serverId] = list(blacklist)
	writeBlacklistsToFile()
	serverOwner = server.owner 
	for message in serverJoinMessages:
		await client.send_message(serverOwner, message)
	await blacklisting(client, serverOwner, serverId)

client.run(sys.argv[1])

# The actual token must be put as an argument so you can't do anything jammy with my bot. I see you.

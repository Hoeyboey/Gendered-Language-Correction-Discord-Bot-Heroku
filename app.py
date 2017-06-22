import discord
import asyncio
import sys
import json

# Creates the client object - just a key part of the wrapper I'm using for the Discord API
client = discord.Client()

# This will be a dictionary of server ids/blacklisted words, just initialised early on.
blacklists = {}

# This is the list of words that are the default for all servers.
blacklist = ['DUDE', 'DUDES', 'GUYS']

# Turned this into a list of strings rather than a few lines of code to make some bits easier - will probably read these from a .txt later.
serverJoinMessages = ['I\'ve just been invited to your server! Hi! I just need to run through some things with you!', 'First of all, we need to decide what words you want me to call out. By default, we include "dude" and "guys", but you\'re able to add any more if you want.', 'Do you want to add any more blacklisted words? Y/N']

# The callout for when someone says a blacklisted word. Currently placeholder, custom responses coming SOON.
async def publicVagueCallout(message, client):
	await client.send_message(message.channel, 'Please don\'t say dude or guys!')

# This updates the blacklists.json file whenever it is updated - this retains the blacklists between the bot turning off and on again
def writeBlacklistsToFile():
	fullCurrentBlacklists = json.dumps(blacklists)
	with open('blacklists.json', 'w') as f:
		f.write(fullCurrentBlacklists)

# When the bot turns on, this runs to update its current blacklists dictionary with whatever is in blacklist.json
def readExistingBlacklists():
	with open('blacklists.json', 'r') as f:
		unserializedBlacklists = f.read()
	global blacklists
	blacklists = json.loads(unserializedBlacklists)

# UGH THE NAME FOR THIS IS AWFUL but it just checks if you've said Y or N to a question that asks for Y or N, need to change it
def check(msg):
	if msg.channel.is_private:
		if msg.content == 'Y' or msg.content == 'N':
			return True
		else:
			return False

# AN EVEN WORSE NAME, just checked if your message was sent in a private channel, i.e. DM'd the bot
def check2(msg):
	if msg.channel.is_private:
		return True
	else:
		return False

# Probably the meatiest part of the program - allows you to add new words to the blacklist for your server
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
	
# All of the @client.event bits are working on events with Discord - this one works when the bot boots up and loads correctly.
# Note - if you've added the bot to a server while this bot is offline, the on_server_join event won't activate, so in on_ready, the for loop checks if that server is already set up and, if not, will set it up to prevent errors.
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

# This checks for if you've said a blacklisted word, running every time it sees a message.
@client.event
async def on_message(message):
	if message.server != None:
		if message.author.id != client.user.id:
			for word in blacklists[str(message.server.id)]:
				if word in message.content.upper():
					await publicVagueCallout(message, client)

# When the  bot joins a server, it updates the blacklist with a new key for that server, and will DM the owner of the server asking if they want to add anything else.
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

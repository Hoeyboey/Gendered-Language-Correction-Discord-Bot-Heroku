import discord
import asyncio
import sys
import json
import os
import redis

# Creates the client object - just a key part of the wrapper I'm using for the Discord API
client = discord.Client()
r = redis.from_url(os.environ.get("REDIS_URL"))

# This will be a dictionary of server ids/blacklisted words, just initialised early on. The syntax for a key value pair is:
# { SERVERID : [[LIST OF BLACKLISTED WORDS], ID OF USERS ABLE TO CHANGE BLACKLIST]}
blacklists = {}

# This is the list of words that are the default for all servers.
blacklist = ['DUDE', 'DUDES', 'GUYS']

# Turned this into a list of strings rather than a few lines of code to make some bits easier - will probably read these from a .txt later.
serverJoinMessages = ['I\'ve just been invited to your server! Hi! I just need to run through some things with you!', 'First of all, we need to decide what words you want me to call out. By default, we include "dude" and "guys", but you\'re able to add any more if you want.', 'Do you want to add any more blacklisted words? Y/N']

# The callout for when someone says a blacklisted word. Currently placeholder, custom responses coming SOON.
async def publicVagueCallout(client, message):
	await client.send_message(message.channel, 'Gendered language sucks and alienates people, or worse. Please don\'t use it!')

async def viewServerBlacklist(client, message):
	currentBlacklist = blacklists[message.server.id]
	await client.send_message(message.channel, 'The blacklist for this server is: {}'.format(currentBlacklist[0]))

async def publiclySpecifyItemToAddToBlacklist(client, message):
	messageAuthor = message.author
	serverOwner = message.server.owner
	if serverOwner == messageAuthor:
		await client.send_message(message.server, 'Alright! Please type the word you want to add to the blacklist.')
		addToBlacklist = await client.wait_for_message(author=message.author)
		await client.add_reaction(addToBlacklist, '✅')
		addToBlacklistStr = addToBlacklist.content.upper()
		if addToBlacklistStr not in blacklists[message.server.id][0]:
			blacklists[message.server.id][0].append(addToBlacklistStr)
			writeBlacklistsToFile()
			print('writebBlacklistsToFile() worked in publiclySpecifyItemToAddToBlacklist')
			await client.send_message(message.server, 'Okay! Want to add any more? Y/N')
			newMessage = await client.wait_for_message(author=message.author, check=checkPublicYN)
			if newMessage.content == 'Y':
				await publiclySpecifyItemToRemoveFromBlacklist(client, message)
			else: 
				await client.send_message(message.server, 'Alright! Remember you can call what I can do with \'!help\'')
		else:
			await client.send_message(message.server, 'This word is already in the blacklist!')
	else:
		await client.send_message(message.server, 'Only the owner of the server can remove words from the blacklist.')
	
# This is called when the server owner says !remove, allowing you to remove a word from the blacklaist
async def removeItemFromBlacklist(client, message):
	messageAuthor = message.author
	serverOwner = message.server.owner
	if serverOwner == messageAuthor:
		await client.send_message(message.channel, 'Okay, please type the word you want to remove from the blacklist!')
		messageToRemove = await client.wait_for_message(author=serverOwner)
		messageToRemoveStr = messageToRemove.content.upper()
		if messageToRemoveStr in blacklists[message.server.id][0]:
			blacklists[message.server.id][0].remove(messageToRemoveStr)
			await client.send_message(message.channel, 'That word has now been removed!')
		else:
			await client.send_message(message.channel, 'Hmm. I couldn\'t find that one in your blacklist!')
	else:
		await client.send_message(message.channel, 'Only the owner of the server can remove words from the blacklist!')

async def addItemToBlacklist(client, message):
	messageAuthor = message.author
	serverOwner = message.server.owner
	if serverOwner == messageAuthor:
		await publiclySpecifyItemToAddToBlacklist(client, message)
	else:
		await client.send_message(message.channel, 'Only the owner of the server can add words to the blacklist!')

#This updates the Heroku redis - this retains the blacklists between the bot turning off and on again
def writeBlacklistsToFile():
	fullCurrentBlacklistsString = json.dumps(blacklists)
	r.set('blacklist', fullCurrentBlacklistsString)

# When the bot turns on, this runs to update its current blacklists dictionary with whatever is in the Heroku redis
def readExistingBlacklists():
	fullCurrentBlacklistsString = r.get('blacklist')
	global blacklists
	if fullCurrentBlacklistsString == None:	
		blacklists = {}
	else:
		blacklists = json.loads(fullCurrentBlacklistsString)

# UGH THE NAME FOR THIS IS AWFUL but it just checks if you've said Y or N to a question that asks for Y or N, need to change it
def check(msg):
	if msg.channel.is_private:
		if msg.content == 'Y' or msg.content == 'N':
			return True
		else:
			return False

def checkPublicYN(msg):
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

# Assuming conditions are met, this will be called to check if the bot should be responding to something. This is partly seperated in case I want to create custom functions later down the line.
async def checkIfCommandCalled(client, message):
	currentBlacklist = blacklists[str(message.server.id)]
	for word in blacklists[message.server.id][0]:
		if word in message.content.upper() and message.reactions != None:
			await publicVagueCallout(client, message)
			break
		elif message.content == '!remove':
			await removeItemFromBlacklist(client, message)
			break
		elif message.content == '!view':
			await viewServerBlacklist(client, message)
			break
		elif message.content == '!add':
			await addItemToBlacklist(client, message)
			break
		elif message.content == '!help':
			await publicHelpReply(client, message)
			break

async def privateHelpReply(client, message):
	await client.send_message(message.author, 'If you\'re the owner of a server I\'m in, you can use these by typing the keyphrases in that server!')
	await client.send_message(message.author, '!add to add a new word to the blacklist')
	await client.send_message(message.author, '!remove to remove a word from the blacklist')
	await client.send_message(message.author, '!view to see the current blacklist')

async def publicHelpReply(client, message):
	await client.send_message(message.server, 'Anyone in the server can type !view to see the current blacklist!')
	await client.send_message(message.server, 'The owner of the server can use the following commands:')	
	await client.send_message(message.server, '!add to add a new word to the blacklist')
	await client.send_message(message.server, '!remove to remove a word from the blacklist')

# Probably the meatiest part of the program - allows you to add new words to the blacklist for your server
async def blacklisting(client, serverOwner, serverId):
	newMessage = await client.wait_for_message(author=serverOwner, check=check)
	if newMessage.content.upper() == 'Y':
		await client.send_message(serverOwner, 'Alright! Please type the word you want to add to the blacklist.')
		addToBlacklist = await client.wait_for_message(author=serverOwner, check=check2)
		addToBlacklistStr = addToBlacklist.content.upper()
		if addToBlacklistStr not in blacklists[serverId][0]:
			blacklists[serverId][0].append(addToBlacklistStr)
			writeBlacklistsToFile()
		else:
			await client.send_message(serverOwner, 'This word is already in the blacklist!')
		await client.send_message(serverOwner, 'Okay! Want to add any more? Y/N')
		await blacklisting(client, serverOwner, serverId)
	else:
		await client.send_message(serverOwner, 'We\'re all done then! For help, DM me with \'!help\'!')
	
# All of the @client.event bits are working on events with Discord - this one works when the bot boots up and loads correctly.
# Note - if you've added the bot to a server while this bot is offline, the on_server_join event won't activate, so in on_ready, the for loop checks if that server is already set up and, if not, will set it up to prevent errors.
@client.event
async def on_ready():
	print('I\'m working!')
	readExistingBlacklists()
	print('The redis on startup looks like this:')
	redisOnStartup = r.get('blacklist')
	print(redisOnStartup)
	serversCurrentlyJoined = client.servers
	for x in serversCurrentlyJoined:
		if x.id not in blacklists.keys():
			serverOwner = x.owner
			serverId = x.id
			blacklists[serverId] = [list(blacklist), serverOwner.id]
			#writeBlacklistsToFile()
			for message in serverJoinMessages:
				await client.send_message(serverOwner, message)
			await blacklisting(client, serverOwner, serverId)

# When the  bot joins a server, it updates the blacklist with a new key for that server, and will DM the owner of the server asking if they want to add anything else.
@client.event
async def on_server_join(server):
	serverId = str(server.id)
	blacklists[serverId] = [list(blacklist), server.owner.id]
	writeBlacklistsToFile()
	serverOwner = server.owner 
	for message in serverJoinMessages:
		await client.send_message(serverOwner, message)
	await blacklisting(client, serverOwner, serverId)

# This checks for if you've said a blacklisted word, running every time it sees a message.
@client.event
async def on_message(message):
	if message.server != None:
		if message.author.id != client.user.id:
			await checkIfCommandCalled(client, message)
	else:
		if message.content == '!help':
			await privateHelpReply(client, message)
		if message.content == '!remove':
			await client.send_message(message.channel, 'You can\'t do this in DMs! Please type \'!remove\' into the server you want to remove a blacklisted word from!')


client.run(sys.argv[1])

# The actual token must be put as an argument so you can't do anything jammy with my bot. I see you.
# blacklists.json syntax is a dictionary where the key is a server id, value is a list where index 0 is a list of the blacklisted words, index 1 is the server owner's id.
# Bug: when it joins, it says "Alright! Remember..." when you say N to the DM.
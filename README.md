# Gendered-Language-Correction-Discord-Bot

Because I think it's important people are given tools to correct people without putting themselves into hostile situations, this is a Discord bot that monitors the text channels of server it's in, and will call it out if it sees someone say "Dude", "Dudes", or "Guys".

It's pretty much done. There's one GLARING bug that needs to be fixed that's actually really annoying me but it's otherwise at version 1.0. Think of it as version 0.99.

Each server the bot is in has a unique blacklist, which the bot will look for. If a message contains a blacklisted term, the bot will send a message to the server saying that gendered language is bad.

Using !add, the owner of a server can add a new word to the blacklist. With !remove, the owner of a server can remove a word from the blacklist. Anyone on the server can use !view to see the current blacklist. !help lists the functions.

That's all, really! It will be hosted online soon, and I'll have an invitation link here then.

Written in Python, using discord.py!


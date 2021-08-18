import os
from discord.ext import commands
import discord
from datetime import datetime
import time
import asyncio
import pytz
import json
import settings
import helpers
import secrets
from keep_alive import keep_alive

# TODO:
# Double ping people when their chore is due
# Add secondary chore slot
# Change the name & photo to "Mike"
# Add admin command to ping all delinquents

#########################
# General objects/vars: #
#########################

time_zone_obj = pytz.timezone(settings.TIME_ZONE) # Used to reference a custom time zone
# datetime.now(tz=settings.TIME_ZONE)
os.environ['TZ'] = settings.TIME_ZONE
time.tzset()

brothers = [] # Hold brother dicts here
# Create dir "brothers/" if it doesn't yet exist
if not os.path.exists("brothers"):
	os.mkdir("brothers")
# Load every stored brother's json and add them to brothers
for brother_json in os.listdir("brothers"):
	with open(os.path.join("brothers", brother_json), 'r') as f:
		brothers.append(json.load(f)) # Extract the json info to a dict and save it to brothers

chores = [] # Hold chores list here
# Create file "chores.txt" if it doesn't yet exist
if not os.path.exists("chores.txt"):
	os.mknod("chores.txt")
# Load every stored chore from the json and add it to chores
with open("chores.txt", 'r') as f:
	for chore in f:
		chores.append(chore[:-1]) # Extract each line as its own chore and add it to chores (ignore the last character [newline])

chore_doers = [] # Hold mentions of people that need to do chores in the current shift

# Create a dict with a brother's info, add it to the list, and store it as a json.
def create_brother(day, shift, makeup_day, makeup_shift, mention, name):
	brother = {"name": name,
	"mention": mention,
	"day": day,
	"shift": shift,
	"makeup day": makeup_day,
	"makeup shift": makeup_shift,
	"submitted": False,
	"makeup": 0
	}
	brothers.append(brother) # Store our brother in the collection
	create_json(brother) # Write our brother to a json file

# Create a brother's json file (or update it, if already made)
def create_json(brother: dict):
	with open(f"brothers/{brother['name']}.json", 'w') as out_file:
		json.dump(brother, out_file, sort_keys=False, indent=4)

# Create the chore list txt file (or update it, if already made)
def update_chores(chores_list: list):
	chores_list.sort() # For good measure, sort the chores alphabetically
	with open("chores.txt", 'w') as out_file:
		for chore in chores_list:
			out_file.write(f"{chore}\n") # Write each chore as its own line


bot = commands.Bot(
	command_prefix=settings.COM_PREFIX,
	case_insensitive=settings.CASE_INSENSITIVE
)

bot.author_id = 242665900711346177

@bot.event 
async def on_ready():  # When the bot is ready
	print("I'm in")
	print(f"Current time (from my perspective): {datetime.now(time_zone_obj)}\nI am in the {settings.TIME_ZONE} time zone.")
	print(bot.user)  # Prints the bot's username and identifier
	bot.loop.create_task(time_check()) # Starts the timer- DON'T CALL THIS AGAIN- it loops internally forever

# Get info aboout yourself
@bot.command(aliases=["me", "my_info", "get_info", "about_me"])
async def info(ctx):
	"""
	Get an embed with info about yourself
	"""
	brother = helpers.get_dict_entry(brothers, ctx.author.mention) # Get a brother's dict entry
	if brother == "@No_Brother": # If they aren't in the list, stop here
		await ctx.send("You don't seem to have a chores profile. Are you living in-house? Please contact the House Manager for more informaiton.")
		return # Abort this attempt

	embed = discord.Embed(
		title = f"{brother['name']}\'s Info",
		colour = discord.Colour.purple()
	)
	embed.set_thumbnail(url=ctx.author.avatar_url)
	embed.add_field(name="Day", value=helpers.get_day_str(brother["day"]), inline=True)
	embed.add_field(name="Shift", value=helpers.get_shift_str(brother["shift"]), inline=True)
	embed.add_field(name="Makeup", value=(helpers.get_day_str(brother["makeup day"]) + ' ' + helpers.get_shift_str(brother["makeup shift"])), inline=False)
	embed.add_field(name="Outstanding Makeup Chores", value=brother["makeup"], inline=False)
	embed.set_footer(text=datetime.now(time_zone_obj))

	await ctx.send(embed=embed)
	# await ctx.send(f"Some things about you: name={ctx.author.name} id={ctx.author.id} discriminator={ctx.author.discriminator}")
	pass

@bot.command()
async def ping(ctx):
	"""
	'Ping' the bot
	"""
	await ctx.send("Pong!")
	pass

@bot.command()
async def submit(ctx):
	"""
	Submit your chores for the week
	"""
	# Outsource most of the logic to allow for string building efficiencies, sending returned message
	result = helpers.handle_submission(brothers, ctx.author.name)
	await ctx.send(result)
	# If they don't have a json already, something's gone wrong and they shouldn't have one created now.
	if result.startswith("You don't"):
		return
	# Then, update their json and remove them from chore_doers
	for brother in brothers:
		if brother["name"] == ctx.author.name:
			if chore_doers.count(brother["mention"]) > 0:
				chore_doers.remove(brother["mention"])
			create_json(brother)

@bot.command(aliases=["chores", "getchores", "get_chores"])
async def chorelist(ctx):
	"""
	Get a list of current chores
	"""
	await ctx.send(f"The following is a list of current chores:\n**{chores}**\nRemember that some are mandatory(!), others not.")
	pass


#########################
# Timekeeping commands: #
#########################

# REMEMBER: Python consideres the week to start on Monday, so be sure to convert to the appropriate int
async def time_check():
	channel = bot.get_channel(settings.CHANNEL_ID)
	if settings.IN_DEBUG: # If we're debugging, notify the server as such
		await channel.send(settings.IN_DEBUG_MESSAGE)
	wait_time = settings.WAIT_ON_FAIL # begin the wait 

	await bot.wait_until_ready() # Wait until we're "ready"
	while True: # Loop forever- external looping/adding to the bot isn't working
		is_shift_time = False # Track if it is currently time to do chores
		day = datetime.now(time_zone_obj).today().weekday() # Get the current day as a number (0 = Monday)
		now = datetime.strftime(datetime.now(time_zone_obj), "%H:%M") # Get the current time of the day

		# Check if it's time to do chores
		if now == settings.MORNING_CHORES_TIME:
			is_shift_time = True
			wait_time = settings.WAIT_ON_SUCCESS # Wait a longer time to start checking again
			mention = helpers.get_user(brothers, day, 0) # Get the appropriate brother's name
			makeup_mention = helpers.get_makeup_user(brothers, day, 0) # Get makeup brother's mention
		elif now == settings.AFTERNOON_CHORES_TIME:
			is_shift_time = True
			wait_time = settings.WAIT_ON_SUCCESS # Wait a longer time to start checking again
			mention = helpers.get_user(brothers, day, 1) # Get the appropriate brother's name
			makeup_mention = helpers.get_makeup_user(brothers, day, 1) # Get makeup brother's mention
		elif now == settings.EVENING_CHORES_TIME:
			is_shift_time = True
			wait_time = settings.WAIT_ON_SUCCESS # Wait a longer time to start checking again
			mention = helpers.get_user(brothers, day, 2) # Get the appropriate brother's name
			makeup_mention = helpers.get_makeup_user(brothers, day, 2) # Get makeup brother's mention
		
		# If it is time to do chores, let the appropriate people know.
		if is_shift_time:
			chore_doers.clear() # The old shift people have missed their chance and won't be pinged again, but will still be able to submit until the end of the week.
			if mention != "@Free_Shift": # If the shift is held by a brother, ping them.
				chore_doers.append(mention)
				await channel.send(f"Alright {mention}, {settings.CHORES_REMINDER_MESSAGE}")
				await asyncio.sleep(settings.MULTIPLE_MESSAGES_DELAY)
				await channel.send(settings.SUBMISSION_REMINDER_MESSAGE)
			else: # If the shift is open, let people know that they can fill it (and should, if they have make-up chores)
				await channel.send(f"Attention {helpers.get_delinquents(brothers)}! {settings.AVAILABLE_SHIFT_REMINDER}")
			if makeup_mention != "@No_Makeup": # If makeup mention is found, ping them.
				chore_doers.append(makeup_mention)
				await channel.send(f"Also, {makeup_mention}, {settings.MAKEUP_CHORES_REMINDER_MESSAGE}")

		# Remind people a few times if they haven't submitted yet
		if is_shift_time:
			# print("It's shift time") # Debugging message- can remove later
			for i in range(0, settings.MAXIMUM_REMINDERS):
				await asyncio.sleep(settings.REMINDER_DELAY)
				if len(chore_doers) > 0: # if we're empty, we can stop because there's no one to remind.
					# print(f"Sleeping for {settings.REMINDER_DELAY}: {i}") # Debugging message- can remove later
					await channel.send(f"Attention {chore_doers}, this is a reminder to do your chores and **{settings.COM_PREFIX}submit** if this is your primary slot or ask the House Manager to forgive a makeup chore if this is your makeup slot.")
		



		# If the week has ended, announce it and ping each brother that hasn't done chores, giving each a makeup chore.
		if (day == settings.NEW_WEEK_DAY) and (now == settings.NEW_WEEK_TIME):
			chore_doers.clear() # As the week is over, we shouldn't be pinging these people anymore.
			delinquent_brothers = helpers.handle_delinquents(brothers) # Extra makeup chores are assigned in the function

			# Update each brother's json
			for brother in brothers:
				create_json(brother)

			await channel.send(f"Another week down! Thank you to everyone who did chores! Currently, I have {delinquent_brothers} as missing chores.\nIf you believe you have been listed in error, please contact the House Manager.")
			wait_time = settings.WAIT_ON_SUCCESS # Wait a longer time to start checking again

		await asyncio.sleep(wait_time)
		wait_time = settings.WAIT_ON_FAIL

@bot.command(aliases=["time", "gettime", "bottime"])
async def get_time(ctx):
	"""
	Get the bot's local time and timezone.
	"""
	localtime = datetime.now(time_zone_obj) # time.asctime(time.localtime(time.time()))
	await ctx.send(f"Current time (from my perspective): {localtime}\nI am in the {settings.TIME_ZONE} time zone.")
	pass

###################
# Admin commands: #
###################

@bot.command(aliases=["addbrother", "ab"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def add_brother(ctx, user: discord.Member, day, shift, makeup_day, makeup_shift):
	"""
	ADMIN: Create a brother object, create a json for him, and add it to brothers
	"""

	# Make sure we're not adding a duplicate brother
	for brother in brothers:
		if brother["name"] == user.name:
			await ctx.send(f"{settings.DUPLICATE_BROTHERS_ERROR_MESSAGE}")
			return # Abort this attempt

	day = day.upper() # Convert day to uppercase
	if day == "MO":
		day = 0
		day_long = "Monday"
	elif day == "TU":
		day = 1
		day_long = "Tuesday"
	elif day == "WE":
		day = 2
		day_long = "Wednesday"
	elif day == "TH":
		day = 3
		day_long = "Thursday"
	elif day == "FR":
		day = 4
		day_long = "Friday"
	elif day == "SA":
		day = 5
		day_long = "Saturday"
	elif day == "SU":
		day = 6
		day_long = "Sunday"
	else:
		await ctx.send(f"I don't seem to recognize \"{day}\" as a day of the week.\nThe first 2 letters are what I need.")
		await asyncio.sleep(settings.MULTIPLE_MESSAGES_DELAY)
		await ctx.send(f"The command should be **{settings.COM_PREFIX}addbrother \"Naaman Fletcher\" FR M SA A**")
		return # Abort this attempt
	
	makeup_day = makeup_day.upper() # Convert makeup_day to uppercase
	if makeup_day == "MO":
		makeup_day = 0
		makeup_day_long = "Monday"
	elif makeup_day == "TU":
		makeup_day = 1
		makeup_day_long = "Tuesday"
	elif makeup_day == "WE":
		makeup_day = 2
		makeup_day_long = "Wednesday"
	elif makeup_day == "TH":
		makeup_day = 3
		makeup_day_long = "Thursday"
	elif makeup_day == "FR":
		makeup_day = 4
		makeup_day_long = "Friday"
	elif makeup_day == "SA":
		makeup_day = 5
		makeup_day_long = "Saturday"
	elif makeup_day == "SU":
		makeup_day = 6
		makeup_day_long = "Sunday"
	else:
		await ctx.send(f"I don't seem to recognize \"{makeup_day}\" as a day of the week.\nThe first 2 letters are what I need.")
		await asyncio.sleep(settings.MULTIPLE_MESSAGES_DELAY)
		await ctx.send(f"The command should be **{settings.COM_PREFIX}addbrother \"Naaman Fletcher\" FR M SA A**")
		return # Abort this attempt
	
	shift = shift.upper() # Convert shift to uppercase
	if shift == 'M':
		shift = 0
		shift_long = "Morning"
	elif shift == 'A':
		shift = 1
		shift_long = "Afternoon"
	elif shift == 'E':
		shift = 2
		shift_long = "Evening"
	else:
		await ctx.send(f"I don't seem to recognize \"{shift}\" as a shift.\nI'll take 'M', 'A', or 'E'.")
		await asyncio.sleep(settings.MULTIPLE_MESSAGES_DELAY)
		await ctx.send(f"The command should be **{settings.COM_PREFIX}addbrother \"Naaman Fletcher\" FR M SA A**")
		return # Abort this attempt
	
	makeup_shift = makeup_shift.upper() # Convert shift to uppercase
	if makeup_shift == 'M':
		makeup_shift = 0
		makeup_shift_long = "Morning"
	elif makeup_shift == 'A':
		makeup_shift = 1
		makeup_shift_long = "Afternoon"
	elif makeup_shift == 'E':
		makeup_shift = 2
		makeup_shift_long = "Evening"
	else:
		await ctx.send(f"I don't seem to recognize \"{makeup_shift}\" as a shift.\nI'll take 'M', 'A', or 'E'.")
		await asyncio.sleep(settings.MULTIPLE_MESSAGES_DELAY)
		await ctx.send(f"The command should be **{settings.COM_PREFIX}addbrother \"Naaman Fletcher\" FR M SA A**")
		return # Abort this attempt

	if (day == makeup_day) and (shift == makeup_shift):
		await ctx.send("It looks like you're trying to assign the primary and makeup chores to the same slot. As this would defeat the purpose of having makeup slots, I must ask you to reconsider.")
		return # Abort this attempt

	create_brother(day, shift, makeup_day, makeup_shift, user.mention, user.name) # Add our new brother
	# brother = Brother(day, shift, user)

	await ctx.send(f"Brother **{user}** added successfully for **{day_long}** **{shift_long}**, with **{makeup_day_long}** **{makeup_shift_long}** as makeup.")

@bot.command(aliases=["removebrother", "deletebrother", "rmbrother", "rmb"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def remove_brother(ctx, user: discord.Member):
	"""
	ADMIN: Delete a brother- delete his json and remove the object from brothers
	"""
	brother = helpers.get_dict_entry(brothers, user.mention) # Get the brother object to delete
	if brother == "@No_Brother":
		await ctx.send(f"I can't seem to find {user.name}. Are you sure this brother has been added? Check brothers/ to see if he has a json.")
		return # Abort this attempt

	vacated_makeup_chores = brother["makeup"]

	brothers.remove(brother) # Remove them from the list
	os.remove(f"brothers/{user.name}.json") # Delete their json
	await ctx.send(f"Brother {user.name} removed successfully.\nThey had {vacated_makeup_chores} remaining makeup chore(s).")

@bot.command(aliases=["reduce", "reduce_makeup"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def forgive(ctx, user: discord.Member, num: int):
	"""
	ADMIN: Forgive a makeup chore - reduce the number of makeup chores owed
	"""
	# Find the appropriate brother
	for brother in brothers:
		if brother["mention"] == user.mention:
			# Remove them from chore_doers if they're present so they stop getting pinged
			if chore_doers.count(brother["mention"]) > 0:
				chore_doers.remove(brother["mention"])

			brother["makeup"] -= num
			await ctx.send(f"Brother {brother['name']} has had {num} makeup chore(s) forgiven and now owes {brother['makeup']}.")
			create_json(brother) # Update the brother's json
			return
	await ctx.send("This brother doesn't seem to have a chore profile. Are they living in-house?")

@bot.command(aliases=["addchore"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def add_chore(ctx, new_chore):
	"""
	ADMIN: Add a chore to the list for brothers to view
	"""
	chores.append(new_chore)
	await ctx.send(f"**{new_chore}** added. The current (non-exaustive) list of chores is: {chores}")
	update_chores(chores) # Update the json

@bot.command(aliases=["removechore", "rmchore"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def remove_chore(ctx, new_chore):
	"""
	ADMIN: Remove a chore from the list
	"""
	chores.remove(new_chore)
	await ctx.send(f"**{new_chore}** removed. The current (non-exaustive) list of chores is: {chores}")
	update_chores(chores) # Update the json

@bot.command(aliases=["getdelinquents", "delinquents", "bitches"])
@commands.has_role(settings.HOUSE_MANAGER_ROLE)
async def get_delinquents(ctx):
	"""
	ADMIN: Ping all brothers that owe makeup chores and how many they owe
	"""
	delinquents = helpers.get_delinquent_info(brothers)
	# await ctx.send(f"Here are the indebted: {delinquents}")
	message = "Here are the indebted:"
	await ctx.send(f"{delinquents}")


###########################
# Housekeeping functions: #
###########################

extensions = [
	'cogs.cog_example'  # Same name as it would be if you were importing it
]

if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loades every extension.

# keep_alive()  # Starts a webserver to be pinged. ENABLE THIS IF ON SERVER THAT TIMES OUT FOR INACTIVITY (e.g. Repl.it)
bot.run(secrets.TOKEN_HOUSE)  # Starts the live housing bot (Be careful with this one)
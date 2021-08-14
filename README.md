This is a Discord bot that helps brothers submit their chores and allows the House Manager to track/assign/forgive makeup chores.

Commands are in main.py, along with time_check(), which is always looping/waiting, triggering when it is time to notify people of their chores/announce the end of the week. Additionally, it contains some logic to save and load everyone's .json, which contains a brother's information, including their submission status.

settings.py contains a series of "constants" that are used in multiple places in the program, such as the time that chore reminders are triggered.

If you want to test this program, you will need to create a "secrets.py" file with a "TOKEN_HOUSE" variable. Then, go to https://discord.com/developers/applications and select "New Application." Create a bot and grab its Bot>>TOKEN, then set TOKEN_HOUSE equal to it. This will have your bot run the program. Finally, add the bot to a development server of yours. It should be fully operational. THE PROGRAM WILL NOT RUN WITHOUT A "secrets.py" FILE PROPERLY SET UP.

Beware: The bot tends to not do well when ran on a server. The current suspicion is that the servers either disallow file creation/editing (making the brother's .json files not be set, thus deleting data on reloads) or deleting data unpredictably and resetting information. If you ever find a reliable host that allows for file creation/editing, please let us know.
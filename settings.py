COM_PREFIX = "!" # What must be inputted to start every command
CASE_INSENSITIVE=True # If commands are case-sensitive or not
MULTIPLE_MESSAGES_DELAY = 1 # Delay (in seconds) between certain succesive messages

CHANNEL_ID = 786148048480501791 # ID for the channel in which we want the timers - MUST BE CHANGED FOR DEPLOYMENT
TIME_ZONE = "US/Mountain" # Timezone of operation - (DENVER) - overrides server time
# TIME_ZONE = "US/Pacific" # Timezone of operation - (LOS ANGELES) - overrides server time
MORNING_CHORES_TIME = "09:00" # Military time
AFTERNOON_CHORES_TIME = "13:00" # Military time
EVENING_CHORES_TIME = "20:00" # Military time
NEW_WEEK_DAY = 6 # The day of the week in which a new week begins (0-6, Mon-Sun)
NEW_WEEK_TIME = "00:00" # The time of day in which the new week begins
CHORES_REMINDER_MESSAGE = "it's time to do chores!"
MAKEUP_CHORES_REMINDER_MESSAGE = "it's time to do a makeup chore!"
SUBMISSION_REMINDER_MESSAGE = f"Remember to submit with **{COM_PREFIX}submit** when you're done!"
AVAILABLE_SHIFT_REMINDER = "This shift is available! You can do this chore as a make-up. If you do so, please let the House Manager know- **don't submit!**"
WAIT_ON_SUCCESS = 3600 # How long, in seconds, we want to wait after a successful check (Make sure this doesn't extend a sleep() past the week's end)
WAIT_ON_FAIL = 30 # How long, in seconds, we want to wait after a failed check (MUST BE LESS THAN 1 MINUTE). Lower numbers mean less delay after time change; larger numbers mean less wasted computing power
REMINDER_DELAY = 3600 # How long, in seconds, we want to wait before reminding people to submit their chores.

IN_DEBUG_MESSAGE = "\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\nWARNING- currently in debug mode! Certain values may be different. Check settings.py for details.\n\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*"
HOUSE_MANAGER_ROLE = "House Manager" # The name of the role assigned to the house manager that enables them to run "admin" commands

###############################
#     Debugging Values        #
# * Testing only              #
# * Disable in deployment     #
###############################

IN_DEBUG = True

if IN_DEBUG:
	print(IN_DEBUG_MESSAGE)
	MORNING_CHORES_TIME = "12:29" # Military time
	AFTERNOON_CHORES_TIME = "12:30" # Military time
	EVENING_CHORES_TIME = "21:46" # Military time
	NEW_WEEK_DAY = 3 # The day of the week in which a new week begins (0-6, Mon-Sun)
	NEW_WEEK_TIME = "21:13" # The time of day in which the new week begins
	WAIT_ON_SUCCESS = 61 # How long, in seconds, we want to wait after a successful check (MUST BE GREATER THAN 1 MINUTE).
	WAIT_ON_FAIL = 3 # How long, in seconds, we want to wait after a failed check (MUST BE LESS THAN 1 MINUTE). Lower numbers mean less delay after time change; larger numbers mean less wasted computing power
	TIME_ZONE = "US/Pacific" # Timezone of operation - (LOS ANGELES) - overrides server time


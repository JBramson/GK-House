# Get a brother's mention tag given their day and shift
# This can now return multiple brothers if they occupt the same shift
def get_user(brothers, day, shift):
	chore_doers = []
	for brother in brothers:
		if (brother["day"] == day) and (brother["shift"] == shift):
			chore_doers.append(brother["mention"])
	
	if len(chore_doers) == 0:
		return "@Free_Shift" # Return None if there is no brother in this shift.
	elif len(chore_doers) == 1:
		return chore_doers[0] # Return the only brother if they're alone
	else:
		return chore_doers # Return the list if there are multiple


# Get a brother's mention tag for their makeup shift
def get_makeup_user(brothers, day, shift):
	for brother in brothers:
		if (brother["makeup day"] == day) and (brother["makeup shift"] == shift):
			if brother["makeup"] > 0:
				return brother["mention"]
	return "@No_Makeup"

# Get a brother's dict entry given their @mention tag
def get_dict_entry(brothers, mention):
	for brother in brothers:
		if brother["mention"] == mention:
			return brother
	return "@No_Brother"

# Get a list of @mentions for those that owe chores
def get_delinquents(brothers):
	delinquents = []
	for brother in brothers:
		if brother["makeup"] > 0:
			delinquents.append(brother["mention"])
	return delinquents

# Get a list of pairs for delinquents and the number they owe sorted by number of makeup chores
def get_delinquent_info(brothers):
	delinquents_set = []
	for brother in brothers:
		if brother["makeup"] > 0:
			delinquent = ((brother["mention"], brother["makeup"]))
			index_found = False
			for i in range(0, len(delinquents_set)):
				if delinquent[1] >= delinquents_set[i][1]:
					delinquents_set.insert(i, delinquent)
					index_found = True
					break
				index_found = False
			if not index_found: # We only want to insert at the end if this delinquent owes less than the others
				delinquents_set.insert(len(delinquents_set), delinquent)
	return delinquents_set

# Get a list of brothers that didn't do chores this week, giving them each a makeup chore
def handle_delinquents(brothers):
	delinquents = [] # Hold delinquents here
	for brother in brothers:
		if brother["submitted"] == False:
			brother["makeup"] += 1 # Assign an extra makeup chore to delinquents
			delinquents.append(brother["mention"]) # Add their @mention to the list
		else:
			brother["submitted"] = False # Reset those that did submit
	return delinquents # Send the @mentions of delinquents back to main

# Mark the given brother as having submitted their chores
def handle_submission(brothers, name):
	for brother in brothers:
		if brother["name"] == name:
			message = "" # What we build and return to the sender
			if brother["submitted"] == True:
				message += "You've already submitted."
			else:
				message += "Thank you for submitting!"
				brother["submitted"] = True
			
			if brother["makeup"] <= 0:
				message += " You're all good for this week."
			else:
				message += "\nRemember that you can take available slots as makeup chores!"
			
			return message # Return after success
	return "You don't seem to have a chores profile. Are you living in-house? Please contact the House Manager for more informaiton."

def get_day_str(day : int):
	if day == 0:
		return "Monday"
	elif day == 1:
		return "Tuesday"
	elif day == 2:
		return "Wednesday"
	elif day == 3:
		return "Thursday"
	elif day == 4:
		return "Friday"
	elif day == 5:
		return "Saturday"
	elif day == 6:
		return "Sunday"
	
	return "@No_Day"

def get_shift_str(shift : int):
	if shift == 0:
		return "Morning"
	elif shift == 1:
		return "Afternoon"
	elif shift == 2:
		return "Evening"
	
	return "@No_shift"
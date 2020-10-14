
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
#Global Variable to store the users current guess
user_guess=0
no_of_guesses=0
# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
	
	global end_of_game
	global value

	option = input("Slect an option:   H - View High Scores     P - Play Game       Q - Quit\n")
	option = option.upper()
	if option == "H":
		os.system('clear')
		print("HIGH SCORES!!")
		ss= fetch_scores()
		s_count=len(ss)
		display_scores(s_count, ss)
	elif option == "P":
		os.system('clear')
`		# reset method called whenever a new game is clicked
		reset()
		print("Starting a new round!")
		print("Use the buttons on the Pi to make and submit your guess!")
		print("Press and hold the guess button to cancel your game")
		#start the pwm led and buzzer
		PWM_LED.start(0)
		PWM_Buzzer.start(50)
		#when game beings the buzzer will beep 1 every 2 seconds, to remind the user
		#that they are in a game
		PWM_Buzzer.ChangeFrequency(0.5)
		value = generate_number()
		while not end_of_game:
			continue
		#stop the pwm led and buzzer at end of game
		PWM_LED.stop()
		PWM_Buzzer.stop()

	elif option == "Q":
		print("Come back soon!")
		exit()
	else:
		print("Invalid option. Please select a valid one!")

#reset all variables whenever a new game is started
def reset():
	global end_of_game
	global user_guess
	global no_of_guesses
	end_of_game=None
	user_guess=0
	no_of_guesses=0

#raw data is a dictionary, count is the number of elements in the dictionary
def display_scores(count, raw_data):

   	 # print the scores to the screen in the expected format
	print("There are {} scores. Here are the top 3!".format(count))
    	
	# print out the scores in the required format by going 
	#through the sorted dictionary
	for key in raw_data:
		print(key+" : "+str(raw_data[key])	)

# Setup Pins
def setup():
	global PWM_LED
	global PWM_Buzzer
    	# Setup board mode
	GPIO.setmode(GPIO.BOARD)
    	# Setup regular GPIO - 11,13,15
	GPIO.setup(LED_value[0],GPIO.OUT)
	GPIO.setup(LED_value[1],GPIO.OUT)
	GPIO.setup(LED_value[2],GPIO.OUT)
	# make All LED logic low, idk why but cleanup() at the end of the program doesnt set them to low
	#when program is started again
	GPIO.output(LED_value[0],0)
	GPIO.output(LED_value[1],0)
	GPIO.output(LED_value[2],0)

    	# Setup PWM channels - ACCURACY LED AND BUZZER ARE PWM COMPONENTS - 32, 33
	GPIO.setup(LED_accuracy,GPIO.OUT)
	#Led has frequency of 200
	PWM_LED=GPIO.PWM(LED_accuracy,200)

	GPIO.setup(buzzer,GPIO.OUT)
	#buzzer ha sinitial frequency of 100
	PWM_Buzzer=GPIO.PWM(buzzer,100)
    	
	# Setup debouncing and callbacks -PULL UP resistors- 16, 18 2 switches
	GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	
	#inturpt and call back  for increase and submit buttons
	#when there is a button clicked with a debounce time of 200
	GPIO.add_event_detect(btn_submit, GPIO.BOTH, callback=btn_guess_pressed, bouncetime=200)  
	GPIO.add_event_detect(btn_increase, GPIO.BOTH, callback=btn_increase_pressed, bouncetime=200)  




# Load high scores and return a dictionary of highscores
def fetch_scores():
	#score dictionary, key is the name, value is the score- initialized
	score_dict={}
    	# Get the no of highscores by reading register 0
	score_count=chr(eeprom.read_byte(0))
    	#Loop through the number of highscores
	#read a bock at a time
	#and store it in the local dictionary that will be returned
	for score in range(int(score_count)):
		score_list=eeprom.read_block(score+1,4)
		score_dict[str(chr(score_list[0]))+str(chr(score_list[1]))+str(chr(score_list[2]))]=int(str(chr(score_list[3])))
    	# return back the dictionary
	return score_dict


# Save high scores into eeprom
def save_scores(score_dict):
	i=0
	#loop through the sorted dictionary that is the parameter
	# in order to write to the eeprom in 
	#decending order
	for key in sorted(score_dict,key=score_dict.get):
		i=i+1
		eeprom.write_block(i,[ord(key[0]),ord(key[1]),ord(key[2]),ord(str(score_dict[key]))])
	#adjust the register 0 to show how many highscores are in the eeprom
	eeprom.write_byte(0,ord(str(len(score_dict))))
	print("written")


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

#method that gets called when user increases guess and the lights need to reflect
def lightLED(val):
	#finding binary value of value
	binary_guess=bin(val).replace("0b","")
	#if binarry is length 1 then adjust lights
	if(len(binary_guess)==1):
		GPIO.output(LED_value[0],int(binary_guess))
		GPIO.output(LED_value[1],0)
		GPIO.output(LED_value[2],0)

	#if binarry is length 2 then adjust lights
	elif(len(binary_guess)==2):
		GPIO.output(LED_value[0],int(binary_guess[1]))
		GPIO.output(LED_value[1],int(binary_guess[0]))
		GPIO.output(LED_value[2],0)


	#if binarry is length 3 then adjust lights
	else:
		GPIO.output(LED_value[0],int(binary_guess[2]))
		GPIO.output(LED_value[1],int(binary_guess[1]))
		GPIO.output(LED_value[2],int(binary_guess[0]))



# Increase button pressed
def btn_increase_pressed(channel):
	global user_guess
	print("Button increase pressed")
	#Checking is max(7) has been reached
	if(user_guess<7):
		user_guess +=1
	#else set the guess back to 1
	else:		
		user_guess=0
	lightLED(user_guess)


#Processs that happens when the user guesses the correct asnwer
def exact_guess():
	global no_of_guesses
	#Disable the PWM LED and the Buzzer
	PWM_LED.stop()
	PWM_Buzzer.stop()
	
	#Prompt the user to enter a name
	print("You have guessed the correct answer in ",no_of_guesses," attempts")
	name=input("Enter your 3 letter nickname: ")
	#assuming the aser must input a name of 3 letters only- while loops repeats until this is done.
	while(len(name)!=3):
		print("Name Must be 3 letter")
		name=input("Enter your 3 letter nickname: ")
	#initializing dictionary that will be sttored to null
	score_dict={}		
	#if the EEprom has no highscores then :
	if(int(chr(eeprom.read_byte(0)))==0):
		#store user answer and name in local dictionary
		score_dict[name]=no_of_guesses
		#Saves the dictionary back in the eeprom
		save_scores(score_dict)
	# else if the eeprom has less than 3 value - i.e 1 or 2 values
	elif(int(chr(eeprom.read_byte(0)))<3):
		#fetch the current data stored in the eeprom
		score_dict=fetch_scores()
		#add the users name and guess in local dictionary
		score_dict[name]=no_of_guesses
		#Saves the dictionary back in the eeprom
		save_scores(score_dict)
	#else the eeprom already has 3 highscores, thus must remove the largest highscore if it is bigger than
	#users answer and replace
	else:
		#fetching scores and storing in local dictionary
		score_dict=fetch_scores()
		#finding the key(name) with the maximum value (highscore)
		max_key=max(score_dict,key=score_dict.get)
		# if users guess fits in top 3 then add it and replace the smallest
		if(score_dict[max_key]>no_of_guesses):
			#delete the biggest value
			del score_dict[max_key]		
			#Saves the dictionary back in the eeprom
			score_dict[name]=no_of_guesses
			print("You are in the top 3")
			#only change data in eeprom if user is in top3
			save_scores(score_dict)
			
		else:
			print("Try again to be in the top 3")
#	print(fetch_scores())

# Guess button
def btn_guess_pressed(channel):
	global end_of_game
	global no_of_guesses
	no_of_guesses+=1
	print("Guess number: ",no_of_guesses)
    	# If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
	start_time=time.time()
	while GPIO.input(channel)==0:
		pass
	#getting the time for how long the button was held.
	buttonTime=time.time()-start_time
	#if it is gretaer than 1 seconds, then revert and go to menu
	if buttonTime > 1:
		PWM_LED.ChangeFrequency(100)
		PWM_LED.stop()
		PWM_Buzzer.stop()
		end_of_game=True
    	# Compare the actual value with the user value displayed on the LEDs
	else:
	    	# if it's an exact guess:
		if(value == user_guess):
			#See exact_guess too see what happens when user guesses the correct asnweer
			exact_guess()
			end_of_game=True
		else:
		    	# Change the PWM LED
			accuracy_leds()
			# if it's close enough, adjust the buzzer
			trigger_buzzer()



# LED Brightness
def accuracy_leds():
    	# Set the brightness of the LED based on how close the guess is to the answer
    	# - The % brightness should be directly proportional to the % "closeness"
    	
	#accounting for 0 being the correct value or when the user_guess is greater than the value
	if((value==0)or(user_guess > value)):
		PWM_LED.ChangeDutyCycle(((8-user_guess)/(8-value))*100)
	#else then it has to be a value less than the value
	else:
		PWM_LED.ChangeDutyCycle((user_guess/value)*100)
		

# Sound Buzzer
def trigger_buzzer():
    	# The buzzer operates differently from the LED
    	# While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    	# The buzzer duty cycle should be left at 50%

    	# If the user is off by an absolute value of 3, the buzzer should sound once every second
	if(abs(user_guess-value)==3):
		PWM_Buzzer.ChangeFrequency(1)
    	# If the user is off by an absolute value of 2, the buzzer should sound twice every second
	elif(abs(user_guess-value)==2):
		PWM_Buzzer.ChangeFrequency(2)
    	# If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
	elif(abs(user_guess-value)==1):
		PWM_Buzzer.ChangeFrequency(4)
		



if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()

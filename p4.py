
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
		reset()

		print("Starting a new round!")
		print("Use the buttons on the Pi to make and submit your guess!")
		print("Press and hold the guess button to cancel your game")
		PWM_LED.start(0)
		PWM_Buzzer.start(50)
		PWM_Buzzer.ChangeFrequency(0.5)
		value = generate_number()
		while not end_of_game:
			continue
		PWM_LED.stop()
		PWM_Buzzer.stop()

	elif option == "Q":
		print("Come back soon!")
		exit()
	else:
		print("Invalid option. Please select a valid one!")

#reset all variables when new game is started
def reset():
	global end_of_game
	global user_guess
	global no_of_guesses
	end_of_game=None
	user_guess=0
	no_of_guesses=0
def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
	print("There are {} scores. Here are the top 3!".format(count))
    	
	# print out the scores in the required format
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
	GPIO.output(LED_value[0],0)
	GPIO.output(LED_value[1],0)
	GPIO.output(LED_value[2],0)
#	eeprom.clear(4096)
#	eeprom.write_byte(0,ord("0"))

    # Setup PWM channels - ACCURACY LED AND BUZZER ARE PWM COMPONENTS - 32, 33
	GPIO.setup(LED_accuracy,GPIO.OUT)
	PWM_LED=GPIO.PWM(LED_accuracy,200)
	GPIO.setup(buzzer,GPIO.OUT)
	PWM_Buzzer=GPIO.PWM(buzzer,100)
    # Setup debouncing and callbacks - 16, 18 2 switches
	GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)  
	GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=300)  




# Load high scores
def fetch_scores():
    # get however many scores there are
	#score dictionary, key is the name, value is the score
	score_dict={}
    # Get the scores
	score_count=chr(eeprom.read_byte(0))
    # convert the codes back to ascii
	#populating the dictionary
	for score in range(int(score_count)):
		#reading a block at a timne and storing it in a list
		score_list=eeprom.read_block(score+1,4)
#		print(score_list,"integer")
		score_dict[str(chr(score_list[0]))+str(chr(score_list[1]))+str(chr(score_list[2]))]=int(str(chr(score_list[3])))
    # return back thedictionary
	return score_dict
	#, scores


# Save high scores
def save_scores(score_dict):
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
	#sorting a dictionary
	i=0
	for key in sorted(score_dict,key=score_dict.get):
		i=i+1
		eeprom.write_block(i,[ord(key[0]),ord(key[1]),ord(key[2]),ord(str(score_dict[key]))])
	eeprom.write_byte(0,ord(str(len(score_dict))))
	print("written")
# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

#method that gets called when user increases guess
def lightLED(val):
	binary_guess=bin(val).replace("0b","")
	if(len(binary_guess)==1):
		GPIO.output(LED_value[0],int(binary_guess))
		GPIO.output(LED_value[1],0)
		GPIO.output(LED_value[2],0)

	elif(len(binary_guess)==2):
		GPIO.output(LED_value[0],int(binary_guess[1]))
		GPIO.output(LED_value[1],int(binary_guess[0]))
		GPIO.output(LED_value[2],0)


	else:
		GPIO.output(LED_value[0],int(binary_guess[2]))
		GPIO.output(LED_value[1],int(binary_guess[1]))
		GPIO.output(LED_value[2],int(binary_guess[0]))



# Increase button pressed
def btn_increase_pressed(channel):
	global user_guess
	print("Button increase pressed",chr(255))
	#Checking is max(8) has been reached
	if(user_guess<7):
		user_guess +=1
	#else set the guess back to 1
	else:
		
		user_guess=0
	lightLED(user_guess)
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess


def input_name():
	global no_of_guesses
	PWM_Buzzer.stop()

	
	print("You have guessed the correct answer in ",no_of_guesses," attempts")
	name=input("Enter your 3 letter nickname: ")
	while(len(name)!=3):
		print("Name Must be 3 or lesss letter")
		name=input("Enter your 3 letter nickname: ")
	score_dict={}		
	if(int(chr(eeprom.read_byte(0)))==0):
		score_dict[name]=no_of_guesses
		eeprom.write_byte(0,ord(str(len(score_dict))))
		save_scores(score_dict)
	elif(int(chr(eeprom.read_byte(0)))<3):
		score_dict=fetch_scores()
		score_dict[name]=no_of_guesses
		eeprom.write_byte(0,ord(str(len(score_dict))))
		save_scores(score_dict)
	else:
		score_dict=fetch_scores()
		max_key=max(score_dict,key=score_dict.get)
		# if users guess fits in top 3 then add it and replace the smallest
		if(score_dict[max_key]>no_of_guesses):
			del score_dict[max_key]
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
	buttonTime=time.time()-start_time
	if buttonTime > 1:
		PWM_LED.ChangeFrequency(100)
		PWM_LED.stop()
		PWM_Buzzer.stop()
		end_of_game=True
    # Compare the actual value with the user value displayed on the LEDs
	else:
		if(value == user_guess):
			print("Correct guess")
			input_name()
			end_of_game=True
		else:
			accuracy_leds()
			trigger_buzzer()
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count



# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
	#accounting for 0 being the correct value or when the user_guess is greater than the value
	if((value==0)or(user_guess > value)):
		PWM_LED.ChangeDutyCycle(((8-user_guess)/(8-value))*100)

    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
	else:
		PWM_LED.ChangeDutyCycle((user_guess/value)*100)
		

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%

    # If the user is off by an absolute value of 3, the buzzer should sound once every second
	if(abs(user_guess-value)==3):
		print("3")
		PWM_Buzzer.ChangeFrequency(1)
	elif(abs(user_guess-value)==2):
		print("2")

		PWM_Buzzer.ChangeFrequency(2)
	elif(abs(user_guess-value)==1):
		print("1")

		PWM_Buzzer.ChangeFrequency(4)
		
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second



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

\
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
	option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
	option = option.upper()
	if option == "H":
		os.system('clear')
		print("HIGH SCORES!!")
		s_count, ss = fetch_scores()
		display_scores(s_count, ss)
	elif option == "P":
		os.system('clear')
		print("Starting a new round!")
		print("Use the buttons on the Pi to make and submit your guess!")
		print("Press and hold the guess button to cancel your game")
		PWM_LED.start(0)
		PWM_Buzzer.start(50)

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


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
	print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
	pass


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

    # Setup PWM channels - ACCURACY LED AND BUZZER ARE PWM COMPONENTS - 32, 33
	GPIO.setup(LED_accuracy,GPIO.OUT)
	PWM_LED=GPIO.PWM(LED_accuracy,100)

	GPIO.setup(buzzer,GPIO.OUT)
	PWM_Buzzer=GPIO.PWM(buzzer,1)
    # Setup debouncing and callbacks - 16, 18 2 switches
	GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)  
	GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=300)  

	pass



# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    
    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


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


#Global Variable to store the users current guess
user_guess=0
# Increase button pressed
def btn_increase_pressed(channel):
	global user_guess
	print("Button increase pressed")
	#Checking is max(8) has been reached
	if(user_guess<8):
		user_guess +=1
	#else set the guess back to 1
	else:
		
		user_guess=0
	lightLED(user_guess)
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
	pass


# Guess button
def btn_guess_pressed(channel):
	global end_of_game
	print("Button guess pressed")
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
	if(value == user_guess):
		print("Correct guess")
		end_of_game=True;
		
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
	pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
	if(user_guess < value):
		PWM_LED.ChangeDutyCycle((user_guess/value)*100)
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
	else:
		PWM_LED.ChangeDutyCycle(((8-user_guess)/(8-value))*100)
		

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
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()

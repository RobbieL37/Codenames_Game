# -*- coding: utf-8 -*-
"""
Created on Tuesday 5/16/2023

@author: Robbie, Tomi, Aiko
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
import nltk
import random
import gensim
import sys
from pygame import mixer
import copy
nltk.download('words')
from nltk.corpus import words
from nltk.corpus import wordnet
from pygame.locals import *
from pygame import mixer
from nltk.stem import WordNetLemmatizer


# get the lemmatizer
wn_lemmatizer = WordNetLemmatizer()
# Get the set of English words from NLTK
english_words = set(words.words())

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin.gz', binary=True, limit=500000)

# load all our words from the wordBank file
with open('wordBank2.txt', 'r') as file:
    word_lists = file.readlines()
word_lists = [line.rstrip() for line in word_lists]
print(len(word_lists))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1400, 720)) # 1400 x 720 size of pygame window size
# background music
mixer.init()  
mixer.music.load('Super Mario Bros. medley.mp3')
mixer.music.play(-1) # playing the loop infinitly     
# title and icon
pygame.display.set_caption("Codenames")
# initiate the font 
font = pygame.font.SysFont(None, 24)
# -------------------------------------------------------------------------------------
#button class for the homepage
class Button_homepage():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

# input box define 
# Define InputBox class
class InputBox:
    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = 'white'
        self.text = ''
        self.font = font
        self.active = False
        self.name = name

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = 'white' if self.active else 'grey'

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = 'white'
#                     return self.text # should add one code for getting the whole input word
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, 'black')
        surface.blit(text_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(surface, self.color, self.rect, 2)

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
# -----------------------------------------------------------------------------
#load button images
resume_img = pygame.image.load("images/resume.png").convert_alpha()
options_img = pygame.image.load("images/options.png").convert_alpha()
restart_img = pygame.image.load('images/replay.png').convert_alpha()
quit_img = pygame.image.load("images/exit.png").convert_alpha()
audio_img = pygame.image.load('images/audio_button_2.png').convert_alpha()
back_img = pygame.image.load('images/back_button_2.png').convert_alpha()
sumbit_img = pygame.image.load('images/sumbit_button.png').convert_alpha()
clue_img = pygame.image.load('images/clue.png').convert_alpha()

#create button instances # full screen: (1400:720)
resume_button = Button(600, 125, resume_img, 0.3)
options_button = Button(600, 240, options_img, 0.3)
restart_button = Button(600, 350, restart_img, 0.3)
quit_button = Button(600, 470, quit_img, 0.3)
audio_button = Button(325, 250, audio_img, 0.3)
back_button = Button(725, 225, back_img, 0.3) # this button will overlap with the restart if the location is not good 
sumbit_button_1 = Button(400, 650, sumbit_img, 0.2)
sumbit_button_2 = Button(600, 650, sumbit_img, 0.2)
sumbit_button_3 = Button(920, 150, sumbit_img, 0.2)
clue_button = Button(450, 600, clue_img, 0.1) 
# -----------------------------------------------------------------------------
# Homepage setting and while loop
BG = pygame.image.load("images/background.jpg")
aspect_ratio = BG.get_width() / BG.get_height()
new_height = 1200
new_width = int(new_height * aspect_ratio)
BG = pygame.transform.scale(BG, (new_width, new_height))

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def homepage():
    print('Homepage')
    homepage_running = True
    while homepage_running: 
        screen.blit(BG, (0, 0))
        
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
      
        OPTIONS_TEXT = get_font(20).render("Welcome to the game 'Codenames'.", True, "yellow")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(650, 250))
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        play_button = Button_homepage(image=pygame.image.load("images/Play Rect.png"), pos=(380, 360), 
                            text_input="SpyMaster", font=get_font(40), base_color="White", hovering_color="Yellow")

        play_button.changeColor(OPTIONS_MOUSE_POS)
        play_button.update(screen)
        
        player_mode_button = Button_homepage(image=pygame.image.load("images/Play Rect.png"), pos=(1020, 360), 
                            text_input="Player", font=get_font(40), base_color="White", hovering_color="Yellow")

        player_mode_button.changeColor(OPTIONS_MOUSE_POS)
        player_mode_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(OPTIONS_MOUSE_POS):
                    homepage_running = False
                    main_while_loop()  # the key to change the page    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_mode_button.checkForInput(OPTIONS_MOUSE_POS):
                    homepage_running = False
                    player_mode_loop()  # the key to change the page    
        pygame.display.update()

def game_over_page():
    print('Game Over Page')
    overpage_running = True
    while overpage_running: 
        screen.fill("black")
        
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()      
        
        OPTIONS_TEXT = get_font(25).render("Game over. Your team lost the game. Please restart.", True, "white")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(650, 250))
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        play_button = Button_homepage(image=pygame.image.load("images/Play Rect.png"), pos=(700, 360), 
                            text_input="PLAY", font=get_font(75), base_color="White", hovering_color="Yellow")

        play_button.changeColor(OPTIONS_MOUSE_POS)
        play_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(OPTIONS_MOUSE_POS):
                    overpage_running = False
                    homepage()  # the key to change the page                    
        pygame.display.update()
        
# -------------------------------------------------------------------------------
music_playing = True # by default is True
def toggle_music():
    global music_playing
    music_playing = not music_playing # False # True
    
    if music_playing == False:
        pygame.mixer.music.pause() # shut down the music
    else:
        pygame.mixer.music.unpause() # open the music  
        
# player mode using machine to provide the clues and user input to select cards
def player_mode_loop(): 
    # define lists to store the input clue and machine guess in front of the while loop 
    guess_word_list = []
    # This sets the WIDTH and HEIGHT of each grid location
    WIDTH = 160  
    HEIGHT = 80  
    # This sets the margin between each cell
    MARGIN = 20
    # Board setup
    all_cards = random.sample(word_lists, 25) # randomly select 25 cards from the list 
    all_cards_lower_cases = [word.lower() for word in all_cards] # store the lower cases transformation 
    # all_cards_lower_cases_2 = [word.lower() for word in all_cards]
    
    # use a dictionary to score our card attributes 
    board = {'blue': [], 'red': [], 'assassin': [], 'neutral': []}
    list_copy = all_cards_lower_cases.copy() # deep copy so it doesn't affect the original 
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['blue'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list  
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['red'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list 
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['neutral'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list 
    board['assassin'].append(list_copy[0]) # the last one assign to the black 
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    # Create input boxes
    input_box2 = InputBox(600, 600, 100, 60, 'Please Input Your Guess:')
    input_box_definition = InputBox(920, 100, 100, 60, 'Definition')
    
    # put the text to our point board 
    red_team_points = 0 
    blue_team_points = 0    
    
    #game variables
    game_paused = False
    menu_state = "main"   
    def_text_string = ''
    definition_state = False
    distance_score = 0
    
    # clue variables by default
    clue_message = 'Please Click On the Clue Button for Clues.'
    bell = 1 
    board_copy = copy.deepcopy(board)
    
    running = True
    while running:    
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")
        
    # -----------------------------------------------------------------------------
    # add a menu button on the right bottom 
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()    
        menu_button = Button_homepage(image=pygame.image.load("images/Play Rect.png"), pos=(1150, 600), 
                            text_input="Menu", font=get_font(35), base_color="White", hovering_color="Yellow")

        menu_button.changeColor(OPTIONS_MOUSE_POS)
        menu_button.update(screen)
    # -------------------------------------------------------------------------------------------------    
    # check the events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.checkForInput(OPTIONS_MOUSE_POS):
                    game_paused = True
                    
            input_box2.handle_event(event) 
            input_box_definition.handle_event(event) 
    # ---------------------------------------------------------------------------------------
        # user input part         
        input_box2.draw(screen)        
        # Display input box values
        screen.blit(font.render(f'{input_box2.name}', True, 'black'), (600, 580))        
                
        input_box_definition.draw(screen)
        screen.blit(font.render(f'{input_box_definition.name}', True, 'black'), (920, 80))
    # ----------------------------------------------------------------------------------        
        # provide the clues from the machine
        if clue_button.draw(screen): # if player click the clue button
            # 1. the machine judge the red team first then blue team 
            if bell == 1:
                team_order = 'red'
                team_order_enemy = 'blue'
                print('clue is for red team now')
            elif bell == -1:
                team_order = 'blue'
                team_order_enemy = 'red'
                print('clue is for blue team now')
            bell *= -1 # change the team order            
            # 2. randomly select a card in each team to generate the similar word list
            target_card = random.choice(board_copy[team_order])
            clue_list = []
            try:
                clue_list = model.most_similar(positive=board_copy[team_order], 
                            negative=board_copy[team_order_enemy], restrict_vocab=50000, topn=1000) 
            except:
                pass
            
            new_list = [t[0] for t in clue_list]
            new_list = [word.lower() for word in new_list] # lower every word
            
            # Filter out non-English words
            correct_words = [w for w in new_list if w in english_words]
            noun_list = []  # just leave noun words 
            for word in correct_words:
                synsets = wordnet.synsets(word)
                for synset in synsets:
                    if synset.pos() == 'n': # noun 
                        noun_list.append(word)
                        break
            # filter out the vocabulary is in the game 25 list
            filtered_list = [x for x in noun_list if x not in all_cards_lower_cases]
            # lemmatize all the words in the filtered list
            filtered_list = [wn_lemmatizer.lemmatize(word, 'v') for word in filtered_list] # basically for -ing ending words
            
            # calculate the distances between the target card and all the clues in the list
            distance_list = []
            for i in filtered_list:
                try:
                    distance_value = model.distance(target_card, i)
                    distance_list.append(distance_value)  
                except:
                    filtered_list.remove(i)                              
                    
            # Get the index of the minimum value in the list
            try:    
                min_index = distance_list.index(min(distance_list))
            except:
                min_index = 0
                
            try:
                clue_random = filtered_list[min_index]
            except:
                clue_random = 'animal'
                            
            # 3. randomly select the clue word from the list (in top 100)
            # distance is meaning how low the similarity they are with
            distance_list = []
            for i in board_copy[team_order]:
                try:
                    distance_value = model.distance(clue_random, i)
                    distance_list.append(distance_value)
                except:
                    pass
                threshold = 0.80 # this is a reasonable number 
                number_of_targets = len([x for x in distance_list if x < threshold])  
                if number_of_targets < 1:
                    number_of_targets = 1
            clue_message = 'For Team {}, The Current Clue is: {}, the number of target cards is {}'.format(team_order, 
                                                                            clue_random, number_of_targets)
            print(clue_message)           
        # 4. post the clue to the screen            
        text_surface = font.render(clue_message, True, (255, 255, 255))        
        screen.blit(text_surface, (350, 530))
        # 5. follow up if players selected the card, then remove it from the dictionary [done]
    # -------------------------------------------------------------------------------------
    # store the guess input and check it if they are in the list  
        guess = ''
        if input_box2.text:
            if sumbit_button_2.draw(screen):
                # guess_cap = input_box1.text.capitalize()
                guess_low = input_box2.text.lower()
                input_box2.text = ''
                
                if guess_low in all_cards_lower_cases: 
                    guess_word_list.append(guess_low)
                    guess = guess_low
    # -----------------------------------------------------------------------------------
    # to show the distance between selected card and the clue
        guess_card = guess
        try:
            distance_score = round(model.distance(clue_random, guess_card), 3)
        except: 
            pass
        distance_message = 'The distance between clue and guess is {}'.format(distance_score)
        # post the score to the screen            
        text_surface = font.render(distance_message, True, (255, 255, 255))        
        screen.blit(text_surface, (350, 550))    
    # --------------------------------------------------------------------------------------
        # Draw the grid
        for row in range(5):
            for column in range(5):
                color = (255, 255, 255) 
                # Determine the word to display in the current cell
                card = all_cards[row * 5 + column]
                # Draw the cell
                pygame.draw.rect(screen,
                                 color,
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN,
                                  WIDTH,
                                  HEIGHT])                
                # Draw the text
                text_surface = font.render(card, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=((MARGIN + WIDTH) * column + MARGIN + WIDTH / 2,
                                                           (MARGIN + HEIGHT) * row + MARGIN + HEIGHT / 2))
                screen.blit(text_surface, text_rect)
    # -------------------------------------------------------------------------------------
        # There is no color grid for the players                             
    # -----------------------------------------------------------------------------
    # find out the location of the Guess card in the all_cards list {done}
        location_num = 0
        if guess_word_list:
            for selected_word in guess_word_list: 
                location_num = all_cards_lower_cases.index(selected_word) + 1 
    
                row = 10000 
                column = 10000  
                # find out the card inside the game grid {done}
                if (location_num >= 1) & (location_num <= 5):
                    row = 1
                    column = location_num 
                elif (location_num >= 6) & (location_num <= 10):
                    row = 2
                    column = location_num - 5     # 7 -> 2 
                elif (location_num >= 11) & (location_num <= 15):
                    row = 3
                    column = location_num - 10    # 12 - 10 = 2
                elif (location_num >= 16) & (location_num <= 20):
                    row = 4
                    column = location_num - 15 
                elif (location_num >= 21) & (location_num <= 25):
                    row = 5
                    column = location_num - 20
                else: 
                    pass 
                row -= 1
                column -= 1 
                # by default we change all selected card with color grey {done}
                if selected_word in board['blue']:
                    color = (0, 0, 255)
                elif selected_word in board['red']:
                    color = (255, 0, 0) 
                elif selected_word in board['assassin']:
                    color = 'black'  #(0, 0, 0) 
                elif selected_word in board['neutral']:
                    color = (128, 128, 128) # grey
                # color = 'grey'
                # Draw the cell
                pygame.draw.rect(screen, color,
                                 [(MARGIN + WIDTH) * column + MARGIN, 
                                        (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
                # Draw the text
                text_surface = font.render(selected_word, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=((MARGIN + WIDTH) * column + MARGIN + WIDTH / 2,
                                                           (MARGIN + HEIGHT) * row + MARGIN + HEIGHT / 2))
                screen.blit(text_surface, text_rect)
    # --------------------------------------------------------------------------------------------           
        # draw a point board for recording the scores  
        pygame.draw.rect(screen, 'grey', [1000, 200, 350, 300])
    
        # judgement for the Victory
        # update the result when one team earn 8 points 
        if red_team_points == 0 and blue_team_points == 0 and guess not in board['assassin']:
            result = ' '
        elif red_team_points == 8:
            result = 'Congratulation to Red Team.'
        # elif red_team_points == blue_team_points and red_team_points != 0 and blue_team_points != 0:
        #     result = 'Game Even. Please play next round.'
        elif  blue_team_points == 8:
            result = 'Congratulation to Blue Team.'
   
        # make a judgement everytime to update the score 
        if guess in board['blue']:
            blue_team_points += 1
            board_copy['blue'].remove(selected_word) # remove it for clues providing
            print("current blue list for clues: ")
            print(board_copy['blue'])
        elif guess in board['red']:
            red_team_points += 1
            board_copy['red'].remove(selected_word) # remove it for clues providing
            print("current red list for clues: ")
            print(board_copy['red'])
        elif guess in board['assassin']:  # the condition that the team select the black card 'assassin'
            result = 'Game over. Your team lost the game.'
            game_over_page() # pop up the game over page
            running = False # close the game while loop
            
                
        ## print the final score board 
        text_red = 'Red team: ' + str(red_team_points)
        text_blue = 'Blue team: ' + str(blue_team_points)
        
        font = pygame.font.Font(None, 24) 
        # print the red team score
        text_surface = font.render(text_red, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 300))
        screen.blit(text_surface, text_rect)
        # print the blue team score
        text_surface = font.render(text_blue, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 320))
        screen.blit(text_surface, text_rect)
        # print the result of the game
        text_surface = font.render(result, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 340))
        screen.blit(text_surface, text_rect)
    # -----------------------------------------------------------------------------------------                    
        # showing the menu page 
        # check if game is paused
        if game_paused == True:
            screen.fill("black")
            # screen.fill((52, 78, 91)) # dark blue
          #check menu state
            if menu_state == "main":
            #draw pause screen buttons
                if resume_button.draw(screen):
                    game_paused = False
                if options_button.draw(screen): # options button keep it for future 
                    menu_state = "options"
                if restart_button.draw(screen):
                    game_paused = False
                    running = False
                    homepage() # go back to homepage to restart the game 
                if quit_button.draw(screen): # quit buttom close the game 
                    running = False
          #check if the options menu is open
            elif menu_state == "options":
            #draw the different options buttons
                if audio_button.draw(screen):
                    toggle_music()
                    print("Audio Settings")
                if back_button.draw(screen):
                    print("Back")
                    menu_state = "main"
        # ---------------------------------------------------------------------------------------
        # add a dictionary function to help understand the vocabularies
        def_text = []
        if input_box_definition.text:
            if sumbit_button_3.draw(screen):
                word = input_box_definition.text
                # Loop through all the synsets of the word and print out their definitions
                for syn in wordnet.synsets(word):
                    def_text_element = syn.definition()
                    def_text.append(def_text_element)
              
                def_text_string = ''.join(def_text)
                input_box_definition.text = ''
                definition_state = True
            
        if definition_state == True:
            screen.fill('purple')
            # screen.fill((52, 78, 91)) # dark blue
            font = pygame.font.Font(None, 24) 
            words = def_text_string.split()
            lines = []
            current_line = ""
            # Loop through the words and add them to lines until the current line is too long
            for word in words:
                if font.size(current_line + " " + word)[0] < 550:
                    current_line += " " + word
                else:
                    lines.append(current_line)
                    current_line = word
            # Add the last line to the list of lines
            lines.append(current_line)        
            # Render the lines as text objects and blit them to the screen
            y_pos = 150
            for line in lines:
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (50, y_pos))
                y_pos += font.size(line)[1]                
            # resume button to go back
            if resume_button.draw(screen):
                definition_state = False
    # ------------------------------------------------------------------------
        pygame.display.flip()        
        clock.tick(60)  # limits FPS to 60   

# -------------------------------------------------------------------------------
# input clues for machine to guess the cards
def main_while_loop(): 
    # define lists to store the input clue and machine guess in front of the while loop 
    clue_word_list = []
    guess_word_list = []
    # This sets the WIDTH and HEIGHT of each grid location
    WIDTH = 160  
    HEIGHT = 80  
    WIDTH_colorgrid = 25
    HEIGHT_colorgrid = 25
    # This sets the margin between each cell
    MARGIN = 20
    MARGIN_colorgrid = 1
    # Board setup
    # All cards
    all_cards = random.sample(word_lists, 25) # randomly select 25 cards from the list 
    all_cards_lower_cases = [word.lower() for word in all_cards] # store the lower cases transformation 
    all_cards_lower_cases_2 = [word.lower() for word in all_cards]
    
    # use a dictionary to score our card attributes 
    board = {'blue': [], 'red': [], 'assassin': [], 'neutral': []}
    list_copy = all_cards_lower_cases.copy() # deep copy so it doesn't affect the original 
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['blue'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list  
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['red'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list 
    for i in range(8): 
        order = random.randrange(1, len(list_copy)+1)
        board['neutral'].append(list_copy[order-1])
        list_copy.pop(order-1) # remove the select card from our list 
    board['assassin'].append(list_copy[0]) # the last one assign to the black 
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    # Create input boxes
    input_box1 = InputBox(400, 600, 100, 60, 'Clue')
    input_box2 = InputBox(600, 600, 100, 60, 'Number')
    input_box_definition = InputBox(920, 100, 100, 60, 'Definition')

    # put the text to our point board 
    red_team_points = 0 
    blue_team_points = 0    
    
    #game variables
    game_paused = False
    menu_state = "main" 
    def_text_string = ''
    definition_state = False
    bell = 1 
    # board_copy = dict(board)
    board_copy = copy.deepcopy(board)
    
    running = True
    while running:    
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")
        
    # -----------------------------------------------------------------------------
    # add a menu button on the right bottom 
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()    
        menu_button = Button_homepage(image=pygame.image.load("images/Play Rect.png"), pos=(1150, 600), 
                            text_input="Menu", font=get_font(35), base_color="White", hovering_color="Yellow")

        menu_button.changeColor(OPTIONS_MOUSE_POS)
        menu_button.update(screen)
    # -------------------------------------------------------------------------------------------------    
    # check the events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.checkForInput(OPTIONS_MOUSE_POS):
                    game_paused = True
        
            input_box1.handle_event(event)
            input_box2.handle_event(event) 
            input_box_definition.handle_event(event) 
    # ---------------------------------------------------------------------------------------    
        # user input part         
        input_box1.draw(screen)
        input_box2.draw(screen)        
        # # Display input box values
        screen.blit(font.render(f'{input_box1.name}', True, 'black'), (400, 580))
        screen.blit(font.render(f'{input_box2.name}', True, 'black'), (600, 580)) 
        
        input_box_definition.draw(screen)
        screen.blit(font.render(f'{input_box_definition.name}', True, 'black'), (920, 80))
    # --------------------------------------------------------------------------------------
        # Draw the grid
        for row in range(5):
            for column in range(5):
                color = (255, 255, 255) 
                # Determine the word to display in the current cell
                card = all_cards[row * 5 + column]
                # Draw the cell
                pygame.draw.rect(screen,
                                 color,
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN,
                                  WIDTH,
                                  HEIGHT])
                # Draw the text
                text_surface = font.render(card, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=((MARGIN + WIDTH) * column + MARGIN + WIDTH / 2,
                                                           (MARGIN + HEIGHT) * row + MARGIN + HEIGHT / 2))
                screen.blit(text_surface, text_rect)
    # -------------------------------------------------------------------------------------
        # Draw the color grid
        for row in range(5):
            for column in range(5):
                color = (255, 255, 255) 
                # Determine the word to display in the current cell
                card = all_cards_lower_cases_2[row * 5 + column]
                if card in board['blue']:
                    color = (0, 0, 255)
                elif card in board['red']:
                    color = (255, 0, 0)
                elif card in board['assassin']:
                    color = 'black'  #(0, 0, 0)
                elif card in board['neutral']:
                    color = (128, 128, 128) # grey
                # Draw the cell
                pygame.draw.rect(screen,
                                 color,
                                 [(MARGIN_colorgrid + WIDTH_colorgrid) * column + MARGIN_colorgrid + 100,
                                  (MARGIN_colorgrid + HEIGHT_colorgrid) * row + MARGIN_colorgrid + 550,
                                  WIDTH_colorgrid,
                                  HEIGHT_colorgrid])                      
    # -----------------------------------------------------------------------------------------   
    # refresh our game grid after user input
        # use the algorithm to find out the similar or related word 
        guess = ''
        guess_list = []
        number_input = 1
        if input_box1.text:
            if sumbit_button_1.draw(screen):
                clue_cap = input_box1.text.capitalize()
                clue_low = input_box1.text.lower()
                clue_word_list.append(clue_cap)
                clue_word_list.append(clue_low)
                print('Store Clue')
            if sumbit_button_2.draw(screen):
                # if bell == 1:
                #     team_order = 'red'
                #     team_order_enemy = 'blue'
                #     print('clue is for red team now')
                # elif bell == -1:
                #     team_order = 'blue'
                #     team_order_enemy = 'red'
                #     print('clue is for blue team now')
                # bell *= -1 # change the team order 
                
                try:
                    number_input = int(input_box2.text)
                except:
                    input_box2.text = ''
                print('Store Number')  
                
                input_box1.text = ''
                input_box2.text = ''
                try:
                    # guess_list = model.most_similar(positive=[clue_low], 
                    #         negative=board_copy[team_order_enemy], restrict_vocab=50000, topn=10000)
                    guess_list = model.similar_by_word(clue_low, topn=50000)
                except:
                    try:
                        # guess_list = model.most_similar(positive=[clue_cap], 
                        #         negative=board_copy[team_order_enemy], restrict_vocab=50000, topn=10000)
                        guess_list = model.similar_by_word(clue_cap, topn=50000)
                    except:
                        pass
                new_list = [t[0] for t in guess_list]
                new_list = [word.lower() for word in new_list] # lower every word
                for a in range(number_input): 
                    for i in new_list: 
                        new_list.remove(i) 
                        if i in all_cards_lower_cases: 
                            guess = i 
                            guess_word_list.append(guess)
                            all_cards_lower_cases.remove(i)
                            # make a judgement everytime to update the score 
                            # the guess doesn't change, then the loop doesn't stop and the score keep adding
                            # until we change the guess value  
                            if guess in board['blue']:
                                blue_team_points += 1 
                                # board_copy['blue'].remove(guess) # remove it for clues providing
                            elif guess in board['red']:
                                red_team_points += 1
                                # board_copy['red'].remove(guess) # remove it for clues providing
                            elif guess in board['assassin']:  # the condition that the team select the black card 'assassin'
                                result = 'Game over. Your team lost the game.'
                                game_over_page() # pop up the game over page
                                running = False # close the game while loop
                            break  # stop the for loop
                        else: 
                            pass           
    # -----------------------------------------------------------------------------
    # find out the location of the Guess card in the all_cards list {done}
        location_num = 0
        if guess_word_list:
            for selected_word in guess_word_list: 
                location_num = all_cards_lower_cases_2.index(selected_word) + 1 
    
                row = 10000 
                column = 10000  
                # find out the card inside the game grid {done}
                if (location_num >= 1) & (location_num <= 5):
                    row = 1
                    column = location_num 
                elif (location_num >= 6) & (location_num <= 10):
                    row = 2
                    column = location_num - 5     # 7 -> 2 
                elif (location_num >= 11) & (location_num <= 15):
                    row = 3
                    column = location_num - 10    # 12 - 10 = 2
                elif (location_num >= 16) & (location_num <= 20):
                    row = 4
                    column = location_num - 15 
                elif (location_num >= 21) & (location_num <= 25):
                    row = 5
                    column = location_num - 20
                else: 
                    pass 
                row -= 1
                column -= 1 
                # by default we change all selected card with color grey {done}
                if selected_word in board['blue']:
                    color = (0, 0, 255)
                elif selected_word in board['red']:
                    color = (255, 0, 0) 
                elif selected_word in board['assassin']:
                    color = 'black'  #(0, 0, 0) 
                elif selected_word in board['neutral']:
                    color = (128, 128, 128) # grey
                # Draw the cell
                pygame.draw.rect(screen, color,
                                 [(MARGIN + WIDTH) * column + MARGIN, 
                                        (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
                # Draw the text
                text_surface = font.render(selected_word, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=((MARGIN + WIDTH) * column + MARGIN + WIDTH / 2,
                                                           (MARGIN + HEIGHT) * row + MARGIN + HEIGHT / 2))
                screen.blit(text_surface, text_rect)
    # --------------------------------------------------------------------------------------------           
        # draw a point board for recording the scores  
        pygame.draw.rect(screen, 'grey', [1000, 200, 350, 300])
    
        # judgement for the Victory
        # update the result when one team earn 8 points 
        if red_team_points == 0 and blue_team_points == 0 and guess not in board['assassin']:
            result = ' '
        elif red_team_points == 8:
            result = 'Congratulation to Red Team.'
        # elif red_team_points == blue_team_points and red_team_points != 0 and blue_team_points != 0:
        #     result = 'Game Even. Please play next round.'
        elif  blue_team_points == 8:
            result = 'Congratulation to Blue Team.'
                            
        ## print the final score board 
        text_red = 'Red team: ' + str(red_team_points)
        text_blue = 'Blue team: ' + str(blue_team_points)

        # Create a font object with a size of 24
        font = pygame.font.Font(None, 24) 
        # print the red team score
        text_surface = font.render(text_red, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 300))
        screen.blit(text_surface, text_rect)
        # print the blue team score
        text_surface = font.render(text_blue, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 320))
        screen.blit(text_surface, text_rect)
        # print the result of the game
        text_surface = font.render(result, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(1170, 340))
        screen.blit(text_surface, text_rect)
    # -----------------------------------------------------------------------------------------                    
        # showing the menu page 
        # check if game is paused
        if game_paused == True:
            screen.fill("black")
            # screen.fill((52, 78, 91)) # dark blue
          #check menu state
            if menu_state == "main":
            #draw pause screen buttons
                if resume_button.draw(screen):
                    game_paused = False
                if options_button.draw(screen): # options button keep it for future 
                    menu_state = "options"
                if restart_button.draw(screen):
                    game_paused = False
                    running = False
                    homepage() # go back to homepage to restart the game 
                if quit_button.draw(screen): # quit buttom close the game 
                    running = False
          #check if the options menu is open
            elif menu_state == "options":
                # screen.fill("black")
            #draw the different options buttons
                # if video_button.draw(screen):
                #     print("Video Settings")
                if audio_button.draw(screen):
                    toggle_music()
                    # music_running = False
                    print("Audio Settings")
                # if keys_button.draw(screen):
                #     print("Change Key Bindings")
                if back_button.draw(screen):
                    print("Back")
                    menu_state = "main"
                    
        # ---------------------------------------------------------------------------------------
        # add a dictionary function to help understand the vocabularies
        def_text = []
        if input_box_definition.text:
            if sumbit_button_3.draw(screen):
                word = input_box_definition.text
                # Loop through all the synsets of the word and print out their definitions
                for syn in wordnet.synsets(word):
                    def_text_element = syn.definition()
                    def_text.append(def_text_element)
                    # print('Definition', def_text)                
                def_text_string = ''.join(def_text)
                input_box_definition.text = ''
                definition_state = True
            
        if definition_state == True:
            screen.fill('purple')
            # screen.fill((52, 78, 91)) # dark blue
            font = pygame.font.Font(None, 24) 
            words = def_text_string.split()
            lines = []
            current_line = ""
            # Loop through the words and add them to lines until the current line is too long
            for word in words:
                if font.size(current_line + " " + word)[0] < 550:
                    current_line += " " + word
                else:
                    lines.append(current_line)
                    current_line = word
            # Add the last line to the list of lines
            lines.append(current_line)        
            # Render the lines as text objects and blit them to the screen
            y_pos = 150
            for line in lines:
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (50, y_pos))
                y_pos += font.size(line)[1]                
            # resume button to go back
            if resume_button.draw(screen):
                definition_state = False
    # ------------------------------------------------------------------------
        # flip() the display to put your work on screen
        pygame.display.flip()        
        clock.tick(60)  # limits FPS to 60    
        
# -------------------------------------------------------------------------------
# the whole game starts from the homepage
homepage()

# Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
pygame.quit()
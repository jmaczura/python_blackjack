'''
Milestone Project 2 - Blackjack!
Rules referenced from https://bicyclecards.com/how-to-play/blackjack/
Setup:
    Classes:
        Deck
        Cards
        Hands - have cards[], a bet amount, a status, and outcome.
        Players - have a bankroll, hands[]

Per Play:
    Get player bet amount
        - Default based on last bet
        - Place bet

    Shuffle cards

    Draw cards:
        Assign cards to each hand to each player
        Print first dealer card
            - get total of both cards
        Print both player cards
            - get total of both cards
            - If DEALER total == 21 and PLAYER Total < 21, Dealer Wins the round
                - if Dealer Total == 21 and Player Total == 21, go to Tie
            - if 21, pay 1.5x and end
            - Ask to hit or Stand
                - Hit: add new card to total
                    - if total <21, ask to hit or stand
                    - if total == 21, go to BlackJack Win (no 1.5x pay though)
                - Stand
'''

import random
import time
import os

suits = ('Hearts ♥', 'Diamonds ♦', 'Spades ♠', 'Clubs ♣')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen',
        'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8,
            'Nine':9, 'Ten':10, 'Jack':10, 'Queen':10, 'King':10, 'Ace':1}
players = []

class Card:
    # Define a class for each card.
    def __init__(self,suit,rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return self.rank + " of " + self.suit

class Deck:
    def __init__(self):
        # Create a Deck of all 52 x 6 Card objects
        self.all_cards = []

        # Let's get a real 6-deck setup going.  No card counting allowed! :-D
        for _ in range(6):
            for suit in suits:
                for rank in ranks:
                    # Create each Card object
                    created_card = Card(suit,rank)
                    # Append each created Card instance to the all_cards list
                    self.all_cards.append(created_card)

        # For unit testing only. Sometimes we need to count on a certain deal order
        # to test functionality.
        self.blackjack_cards = [(Card('Hearts','Ace')),(Card('Hearts','King'))]

    def shuffle(self):
        # shuffle the deck
        random.shuffle(self.all_cards)

    def deal_one_card(self):
        return self.all_cards.pop()
        # TO USE:
        # new_deck = Deck()
        # new_deck.shuffle()
        # mycard = new_deck.deal_one_card()

class Hand():
    def __init__(self):
        self.cards_in_hand = [] # we will put Cards from the Deck in here.
        self.low_total = 0
        self.high_total = 0
        self.bet_amount = 0
        self.outcome = "pending" # pending, win, lose, tie
        self.status = "playing" # playing, blackjack, stand, bust
        # If the dealer shows an Ace card, players may bet up to half their
        # original bet. Store the insurance bet amount here.
        self.insurance_bet = 0

    def update_hand_totals(self):
        low_total = 0
        high_total = 0
        ace_found = False

        for each_card in self.cards_in_hand:
            low_total += each_card.value
            if each_card.value == 1 and ace_found is False: # we found our first Ace card
                ace_found = True
                high_total += 11
            else:
                high_total += each_card.value
        self.low_total = low_total
        self.high_total = high_total

    def __str__(self):
        hand_text = ''
        for each_card in self.cards_in_hand:
            hand_text += "  " + str(each_card) + "\n"

        self.update_hand_totals()

        if self.high_total == self.low_total or self.high_total > 21:
            hand_text += "  ...for a total of " + str(self.low_total) + "."
        elif self.high_total == 21:
            hand_text += "  ...for a total of " + str(self.high_total) + "."
        else:
            hand_text += "  ...for a total of " + str(self.low_total) + " or " + str(self.high_total) + "."
        return hand_text

    def print_initial_dealer_card(self):
        print(f"Dealer is showing a {self.cards_in_hand[0]}.")
        # to prompt for Insurance, return True if it's an Ace (value is defaulted to 1)
        return self.cards_in_hand[0].value == 1
    
    def add_a_card(self,the_deck):
        # Adds a card from the deck to the current Hand.
        self.cards_in_hand.append(the_deck.deal_one_card())

class Player():
    # Represents an instance of a Player
    # Be able to add or remove cards from their "hand" (list of card objects)
    def __init__(self,name,bankroll,default_bet_amount):
        self.name = name # give each player a Name (e.g. "The Dealer")
        self.current_hands = []
        self.bankroll = bankroll # How much money they have.
        self.default_bet_amount = default_bet_amount # Default their bet again

    def __str__(self):
        return f"{self.name} has ${self.bankroll}."

    def transact_bankroll(self, action, amount):

        if action == "win":
            self.bankroll += amount
            print(f'{self.name} won ${"{:.2f}".format(amount)} and now has ${"{:.2f}".format(self.bankroll)}.')
        else:
            self.bankroll -= amount
            print(f'{self.name} lost ${"{:.2f}".format(amount)} and now has ${"{:.2f}".format(self.bankroll)}.')
        return self.bankroll

def init_players():
    num_of_players = "A"
    while not num_of_players.isdigit() or int(num_of_players) < 1 or int(num_of_players) > 4:
        num_of_players = input("How many players? (1-4) (default is 2): ") or "2"

    for player in range(1,int(num_of_players)+1):

        player_bankroll = "A"
        while not player_bankroll.isdigit() or int(player_bankroll) < 10:
            player_bankroll = input(f"How much money is Player {player} bringing? (default is $100): $") or "100"

        players.append(Player(f"Player {player}",int(player_bankroll),10))

def get_bets():
    for player in players:
        last_bet = player.default_bet_amount
        if last_bet > player.bankroll:
            last_bet = player.bankroll
        min_reached = False
        while not min_reached:
            bet_amount = input(f'{player.name}: How much do you want to bet? (default ${last_bet}, maximum ${"{:.2f}".format(player.bankroll)}): ') or str(last_bet)
            if bet_amount.isdigit() and int(bet_amount) > player.bankroll:
                print("You don\'t have that much in chips. Try again.")
            elif bet_amount.isdigit() and int(bet_amount) >= 10:
                player.default_bet_amount = int(bet_amount)
                min_reached = True
            else:
                print("The minimum to play a hand is $10 and must be in whole dollars.")

def print_all_hands():
    for player in players:
        print(f'{player.name}\'s cards:',*player.current_hands,sep="\n")
        time.sleep(2)

def solicit_insurance():
    print("Uh oh! The dealer has an Ace showing. You might want to consider buying insurance.")
    for player in players:
        insurance_response = False
        while not insurance_response:

            response = input(f'{player.name}: Buy insurance? (y/N): ') or 'n'
            if response[0].lower() == 'y':
                # This rounds odd bets down to the nearest integer to avoid errors and <$1 values.
                maximum_amount = player.current_hands[0].bet_amount // 2
                insurance_amount = input('For how much? Must be at least $1 but no more than ' +
                                    f'${maximum_amount} (default is ${maximum_amount}): ') or str(maximum_amount)
                if insurance_amount.isnumeric() and int(insurance_amount) > player.bankroll - player.default_bet_amount:
                    print(f"{player.name} only has {player.bankroll - player.default_bet_amount} remaining.")
                else:
                    player.current_hands[0].insurance_bet = int(insurance_amount)
                    insurance_response = True
            else:
                insurance_response = True


def deal_out_all_cards(the_deck):
    the_deck.shuffle()
    for player in players:
        # Clear any prior Hands
        player.current_hands.clear()
        # Add a hand object
        player.current_hands.append(Hand())
        # Add two cards.
        # In a perfect mimicry of a live game, each player gets a card, then the dealer gets 1 card,
        # then card 2 to each player, and finally the dealer. Since we're randomizing every deal,
        # there is no impact to the outcome, and it makes the code simpler.
        player.current_hands[0].add_a_card(the_deck)
        player.current_hands[0].add_a_card(the_deck)
        player.current_hands[0].bet_amount = player.default_bet_amount

    # Deal two cards to the dealer.
    dealer_hand.cards_in_hand.clear()
    #dealer_hand.cards_in_hand.append(the_deck.deal_one_card())
    #dealer_hand.cards_in_hand.append(the_deck.deal_one_card())
    dealer_hand.add_a_card(the_deck)
    dealer_hand.add_a_card(the_deck)
    # Unit Test for Dealer blackjack.
    #dealer_hand.cards_in_hand.append(the_deck.blackjack_cards.pop(0))
    #dealer_hand.cards_in_hand.append(the_deck.blackjack_cards.pop())

    dealer_hand.outcome = 'pending'
    dealer_hand.status = 'playing'

def eval_for_blackjacks():
    dealer_hand.update_hand_totals()
    dealer_blackjack = dealer_hand.high_total == 21
    if dealer_blackjack:
        print("Oh boy... Dealer has Blackjack!")
        #dealer_hand.outcome = "pending" # pending, win, lose, tie
        dealer_hand.status = "blackjack" # playing, blackjack, stand, bust
        time.sleep(2)
    for player in players:
        if player.current_hands[0].high_total == 21:
            player.current_hands[0].status = 'blackjack'
            print(f"\n{player.name} has Blackjack!")
            time.sleep(2)
            if dealer_blackjack:
                player.current_hands[0].outcome = 'tie'
            else:
                player.current_hands[0].outcome = 'win'
        else:
            if dealer_blackjack:
                player.current_hands[0].outcome = 'lose'

def settle_blackjacks():
    blackjack_count = 0
    num_of_players = len(players)
    for player in players:
        if dealer_hand.status == 'blackjack' and player.current_hands[0].insurance_bet > 0:
            win_amount = 2*player.current_hands[0].insurance_bet
            print(f"Lucky guess! {player.name} won ${win_amount} using Insurance! (Brought to you by GEICO)")
            player.transact_bankroll('win',win_amount)
            time.sleep(2)
        # Whether or not the player bought insurance, their hand is still subject to losing against a Dealer Blackjack.
        if player.current_hands[0].outcome == 'lose':
            player.transact_bankroll('lose',player.current_hands[0].bet_amount)

        elif player.current_hands[0].outcome == 'win' and player.current_hands[0].status == 'blackjack':
            player.transact_bankroll('win',player.current_hands[0].bet_amount*1.5) # pay 1.5x the bet amount
            blackjack_count += 1

    # End this round by returning False if the dealer has Blackjack, or all of the players have Blackjacks.
    if dealer_hand.status == 'blackjack' or blackjack_count == num_of_players:
        return False
    return True

def solicit_player_actions(the_deck):
    dealer_goes = False # setting this to True only if at least one hand results in a Stand.
    for player in players:
        for current_hand in player.current_hands:
            if current_hand.outcome == 'pending':
                ask_again = True
                # Let's use a Set!  We don't care about the order, and we don't care if this loop re-adds any existing items.
                options = {'(H)it', '(S)tay'}
                while ask_again:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    # Since we're clearing the screen for each Player, remind them of the Dealer's card first.
                    dealer_hand.print_initial_dealer_card()
                    print(f"\n{player.name} has: ")
                    print(current_hand)

                    # Split logic: If player's hand has only 2 cards, and those two cards are equal in value, offer to split.
                    # Added check to disallow splitting more than once by checking for length of current_hands[]
                    if (len(player.current_hands) == 1 and len(current_hand.cards_in_hand) == 2 and
                    current_hand.cards_in_hand[0].value == current_hand.cards_in_hand[1].value):
                        options.add('s(P)lit')
                    else:
                        # If we added the Split option originally in this While loop, remove it the second time.
                        options.discard('s(P)lit')

                    # If the player has a total value of 9, 10, or 11, offer to Double Down.
                    # Only offer Doubling Down if we haven't already hit (i.e., the player's hand only has 2 cards)
                    if ((current_hand.low_total in [9, 10, 11] and current_hand.high_total > 21) or current_hand.high_total in [9, 10, 11]) and len(current_hand.cards_in_hand) == 2:
                        options.add('(D)ouble down')
                    else:
                        options.discard('(D)ouble down')

                    # Concatenate the Options from the options set() object, convert the player's response to lower case, and default "h" (for Hit).
                    player_action = input(f"{player.name}: {', '.join(options)} : ").lower() or "h"

                    if player_action[0] == 'h':
                        # The player wants to add another card to their hand.
                        print(f"{player.name} says, \'Hit me!\'")

                        #current_hand.cards_in_hand.append(the_deck.deal_one_card())
                        current_hand.add_a_card(the_deck)
                        print(f"{player.name} drew a {current_hand.cards_in_hand[-1]}")
                        print(current_hand)
                        # Evaluate if we busted, drew to 21, or are still under 21.
                        if current_hand.low_total > 21:
                            current_hand.status = 'bust'
                            current_hand.outcome = 'lose'
                            print(f"{player.name}\'s hand is a bust!")
                            time.sleep(2)
                            ask_again = False
                        elif current_hand.low_total == 21 or current_hand.high_total == 21:
                            current_hand.status = 'stand' # Assigning 'stand' instead of 'blackjack' because the 1.5x payout only occurs when the first two cards = 21.
                            current_hand.outcome = 'pending' # the dealer might draw to 21 as well, so we don't know if it is a Winner just yet.
                            ask_again = False
                            dealer_goes = True
                            time.sleep(2)
                        else:
                            # The player's hand is not yet 21 or higher.  Offer them options to hit again or to stand.
                            ask_again = True
                    elif player_action[0] == "s": # Stand
                        # The player is fine with this hand remaining as it is.
                        current_hand.status = 'stand'
                        ask_again = False
                        dealer_goes = True
                        time.sleep(2)
                    elif player_action[0] == "d" and '(D)ouble down' in options: # double down selected and is currently allowed.
                        # Since we don't deduct their bankroll until after the round is complete (note: we should probably change this logic),
                        # check to see if they can double down by multiplying their current bet by 2, and deducting the full amount from their bankroll.
                        doubled_bet = current_hand.bet_amount * 2
                        if player.bankroll - doubled_bet < 0:
                            print("Sorry - you do not have enough chips to double down.")
                        else:
                            print("Doubling down your bet... one more card will be drawn.")

                            current_hand.bet_amount = doubled_bet
                            current_hand.add_a_card(the_deck)
                            print(f"{player.name} drew a {current_hand.cards_in_hand[-1]}")
                            print(current_hand)
                            # The rules for Double Down in Blackjack indicate the player must take one more card and then Stand.
                            current_hand.status = 'stand'
                            ask_again = False
                            dealer_goes = True
                        time.sleep(3)
                    elif player_action[0] == 'p' and 's(P)lit' in options: # If "Split" selected and is currently allowed for this hand...
                        # Also check here to ensure the player can afford to add another hand from their bankroll.
                        two_bets = current_hand.bet_amount * 2
                        if player.bankroll - two_bets < 0:
                            print("Sorry - you do not have enough chips to split your current hand.")
                            time.sleep(2)
                        else:
                            print(f"Splitting your hand, and betting {current_hand.bet_amount} for the second hand.")

                            # Add a hand to the current player.
                            player.current_hands.append(Hand())
                            # Ensure the bet amount is the same as the first hand.
                            player.current_hands[1].bet_amount = player.default_bet_amount
                            # Move the second card from the first hand to the second hand.
                            player.current_hands[1].cards_in_hand.append(player.current_hands[0].cards_in_hand.pop())
                            # Draw a new card to each Hand.
                            player.current_hands[0].add_a_card(the_deck)
                            print(f"{player.name} drew a {player.current_hands[0].cards_in_hand[-1]} on the first hand.")
                            player.current_hands[1].add_a_card(the_deck)
                            print(f"{player.name} drew a {player.current_hands[1].cards_in_hand[-1]} on the second hand.")
                            time.sleep(2)
                    else:
                        ask_again = True

    return dealer_goes

def process_dealer_hand(the_deck):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("The dealer turns their second card over to reveal... ")
    time.sleep(1)
    print(dealer_hand)

    while dealer_hand.high_total < 17 or (dealer_hand.high_total > 21 and dealer_hand.low_total < 17):
        # Draw another card until the hand is 17 or higher.
        dealer_hand.add_a_card(the_deck)
        print(f'{dealer_hand.cards_in_hand[-1]} drawn from the deck.')
        dealer_hand.update_hand_totals()
    if dealer_hand.high_total < 22:
        print(f"The dealer is standing with a total of {dealer_hand.high_total}.")
    elif dealer_hand.low_total < 22:
        print(f"The dealer is standing with a total of {dealer_hand.low_total}.")
    elif dealer_hand.low_total > 21:
        print(f"The dealer went bust with a total of {dealer_hand.low_total}!")
        dealer_hand.outcome = 'lose'
        dealer_hand.status = 'bust'
    else:
        print(f"The dealer went bust with a total of {dealer_hand.high_total}!")
        dealer_hand.outcome = 'lose'
        dealer_hand.status = 'bust'

def settle_the_bets():
    # Let's look at each player's Status and if needed, compare it to that of the Dealer.
    dealer_total = dealer_hand.high_total
    if dealer_total > 21:
        dealer_total = dealer_hand.low_total

    print('\n')
    for player in players:
        for current_hand in player.current_hands:
            if current_hand.status == 'stand':
                if dealer_hand.status == 'bust': # pay every player who Stood (status = Stand)
                    player.transact_bankroll('win',current_hand.bet_amount)
                else: # compare the best dealer hand to the best player hand.
                    player_total = current_hand.high_total
                    if player_total > 21:
                        player_total = current_hand.low_total
                    if player_total > dealer_total:
                        player.transact_bankroll('win',current_hand.bet_amount)
                    elif player_total < dealer_total:
                        player.transact_bankroll('lose',current_hand.bet_amount)
                    else: # tie
                        print(f'{player.name} tied with the dealer and still has ${"{:.2f}".format(player.bankroll)}.')
            elif current_hand.status == 'blackjack':
                #We already paid the player when they got blackjack.
                print(f'{player.name} was already paid for having Blackjack.')
            else: # player went bust
                player.transact_bankroll('lose',current_hand.bet_amount)
            # Check for Insurance.
            if current_hand.insurance_bet > 0:
                print("Since you did not need Insurance, that amount is lost.")
                player.transact_bankroll('lose',current_hand.insurance_bet)

def determine_active_players():
    # Since we iterate through the players[] list object during gameplay, evaluate
    # how many players can still play. We need to reverse the list of "broke" players
    # because removing/popping the first player, for example, causes the second player
    # to immediately take on an index of 0.  This condition only happens if multiple
    # players go broke in the same round.
    broke_players = []
    for index, player in enumerate(players):
        if player.bankroll < 10:
            print(f'{player.name} no longer has enough chips and has left the game.')
            broke_players.append(index)
    broke_players.sort(reverse=True)
    for index in broke_players:
        players.pop(index)
    return len(players)

# This variable doesn't work at the top, or seemingly anywhere else other than after the Class definitions. <shrug>
dealer_hand = Hand()

def lets_play():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Welcome to Python Blackjack! $10 mininum.  Dealer stands on 17 or higher.\n")

    # This will hold each Player class object instance.
    init_players()

    while True:
        # Clear the screen.
        os.system('cls' if os.name == 'nt' else 'clear')
        # Let's use this to evaluate after each Part whether there are players' hands left to keep going until the end.
        continue_round = True

        # Prepare the deck.
        the_deck = Deck()

        # Solicit bets from each player.
        get_bets()

        # Clean up any old hands and deal the cards.
        deal_out_all_cards(the_deck)

        # Display the dealer's first card.
        ace_card_showing = dealer_hand.print_initial_dealer_card()

        # If the dealer is showing an Ace card, ask each player if they want to pay for insurance.
        if ace_card_showing:
            solicit_insurance()

        # Print out the cards and values for all players.
        print_all_hands()

        # Check for Blackjacks held by the dealer and players.
        eval_for_blackjacks()

        # Pay any Blackjacks.  This could end the game if the dealer has Blackjack and/or all player(s) have Blackjack, so return a "continue game" Boolean.
        continue_round = settle_blackjacks()

        # Now it's time for each player to hit, stand, split, or double down.
        if continue_round:
            dealer_goes = solicit_player_actions(the_deck)
            # Have the dealer hit or stand.  Skip this part this if no player is in Stand status.
            if dealer_goes:
                process_dealer_hand(the_deck)
            # Pay up, or pay out, each hand.
            settle_the_bets()

        # If we've made it this far, we want to ask the players to play again, unless everyone is out of money.
        num_of_players = determine_active_players()
        if num_of_players > 0:
            play_again = input("Play another round? (Y/n): ").lower() or "y"
            if play_again[0] == 'y':
                continue            
            for player in players:
                print(f'{player.name} leaves the table with ${"{:.2f}".format(player.bankroll)}.')
            break
        else:
            print("No players have chips left. Ending the game!")
            break

    print("\nThanks for playing!")

if __name__ == '__main__':
    lets_play()

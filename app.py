## Merwan Malakapalli ##
## Wordle Solver ##
from flask import Flask
from flask import render_template
from flask import request 
import requests

app = Flask(__name__)

# Gets the list of possible words from this file words.txt
def generate_word_list():
    with open("words.txt", "r") as file:
        word_list = [word.strip().lower() for word in file.readlines()]
    return word_list

# Counts occurences of each letter in all the words
def count_occurrences(word_list):
    letter_counts = {}
    for word in word_list:
        for letter in word:
            if letter in letter_counts:
                letter_counts[letter] += 1
            else:
                letter_counts[letter] = 1
    return letter_counts

# Global variable to store the current state
word_list = generate_word_list()
letter_values = count_occurrences(word_list)

@app.route("/", methods=["GET", "POST"])
def hello_world():
    global word_list, letter_values
    computer_guess = make_guess(word_list, letter_values)
    result = f"Computer suggests: {computer_guess}, Remaining possibilities: {len(word_list)}"

    if request.method == "POST":
        user_guess = request.form.get("guess")
        feedback = request.form.get("feedback").upper()

        letter_values = count_occurrences(word_list)
        word_list = filter_word_list(word_list, user_guess, feedback)

        if feedback == "GGGGG":
            result = f"Congratulations! You guessed the word: {user_guess}"
            return render_template('winning.html')
        else:
            computer_guess = make_guess(word_list, letter_values)
            if computer_guess == "Not Solvable":
                return render_template('index.html', result = "Unable to Solve :(", word_list=[])
            result = f"Computer suggests: {computer_guess}, Remaining possibilities: {len(word_list)}"

    return render_template('index.html', result=result, word_list = word_list)

if __name__ == "__main__":
    app.run(debug=True)







# Compares a given word (taken from wordlist) to the guess of user and creates its own feedback
# Feedback is used in the filter word list function to see if it matches inputted feedback.
def check_guess(word, guess):
    feedback = ""
    letter_counts = {letter: word.count(letter) for letter in set(word)}

    for i in range(len(word)):
        if guess[i] == word[i]:
            feedback += "G"
            letter_counts[word[i]] -= 1
        elif guess[i] in word and letter_counts[guess[i]] > 0:
            feedback += "Y"
            letter_counts[guess[i]] -= 1
        else:
            feedback += "B"

    return feedback

# Filters the word list to match the feedback given
def filter_word_list(word_list, guess, feedback):
    filtered_list = [word for word in word_list if check_guess(word, guess) == feedback]
    return filtered_list

# Gets the optimal word (highest value) from the word list.
# Note: also accounts for frequency of letter in given word by dividing by 1 + frequency of letter in word.
# Avoids division by 0 error by dividing by 1+frequency.
def make_guess(word_list, letter_values):
    if not word_list:
        print("Unable to Solve! :(")
        return "Not Solvable"

    #  Calculates a numerical value for each word and returns word with max value.
    guess_word = max(word_list, key=lambda word: sum(letter_values.get(letter, 0) / (1 + word.count(letter)) for letter in word))
    return guess_word

# Runs the program
def main():
    word_list = generate_word_list()
    max_attempts = 6

    print("Welcome to Wordle Solver!")
    print("\n")

    for attempt in range(1, max_attempts + 1):
        letter_values = count_occurrences(word_list)
        computer_guess = make_guess(word_list, letter_values)

        print(f"Computer suggests: {computer_guess}")

        user_guess = input(f"Attempt {attempt}: Enter your guess: ").lower()

        if len(user_guess) != 5 or not user_guess.isalpha():
            print("Invalid input. Please enter a valid five-letter word.")
            continue

        feedback = input("Enter feedback (G for correct letter and position, Y for correct letter but wrong position, and B for incorrect letter): ").upper()

        if feedback == "GGGGG":
            print("Congratulations! You guessed the word: ", user_guess)
            break
        else:
            word_list = filter_word_list(word_list, user_guess, feedback)
            print("Remaining possibilities:", len(word_list))


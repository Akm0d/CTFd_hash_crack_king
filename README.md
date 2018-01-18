# Hash Crack King plugin

This plugin allows you to create king-of-the-hill style password cracking challenges.  Teams are awarded "capture points" the first time they take control of "the hill".  They are awarded "hold points" every n seconds they maintain control of the hill.  


#Setup


    Clone CTFD-hash_crack_king  to  /CTFd/plugins/
    

#How to use
- As an admin, go to "challenges" 
- Create a challenge 
- from the drop down select "hash_crack_king"
- Set the parameters for your challenge.
  - Capture value - The number of points awarded the first time a team takes control of the hill
  - Hold value - The number of points awarded every cycle to the team in control of the hill
  - Seconds per Cycle - The number of seconds in a cycle
  - Upload word lists.  These will not be visible to contestants, but will be used to generate keys and hashes.
# TODO
  - Add complexity levels pressing the '+'
    - word list - the name of the word list to use for this difficulty level.  If none is given, or if an unreadable file is given, keys will be generated from the other complexity settings
    - key length - a fixed length for each key.  If a word from the word list is too short (or if there is no word list), random data from complexity level character set will be added.
    - solves to advance - The number of solves before advancing to the next complexity level.  Once at the final level, stay there.
    - character set - The characters allowed to be used in a generated key.
        - [a-z] will include all lower case letters in the english alphabet
        - [a-Z] will include all letters in the english alphabet
        - [0-9] will include all numbers
        - !@#$%^&* Any other characters special characters to add
        - [u100-256] Include characters 100 to 256 from unicode
  

#Questions
If you have any questions please contact Akmod (tyler@utos.org)
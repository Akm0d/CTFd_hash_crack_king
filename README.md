# Hash Crack King plugin
This plugin allows you to create king-of-the-hill style password cracking challenges.  Teams are awarded "capture points" the first time they take control of "the hill".  They are awarded "hold points" every n minutes they maintain control of the hill.  



# Setup
    Clone CTFD-hash_crack_king  to  /CTFd/plugins/

## Development
```bash
$ git clone https://github.com/CTFd/CTFd.git
$ cd CTFd
$ ./prepare.sh
$ pushd CTFd/plugins
$ git clone https://github.com/jtylers/CTFd_hash_crack_king.git
$ pip3 install -r CTFd_hash_crack_king/requirements.txt
$ popd
$ python3 serve.py &
$ xdg-open 127.0.0.1:4000
```
    

# How to use
- As an admin, go to "challenges" 
- Create a challenge 
- from the drop down select "hash_crack_king"
- Set the parameters for your challenge.
  - Capture value - The number of points awarded the first time a team takes control of the hill
  - Hold value - The number of points awarded every cycle to the team in control of the hill
  - Minutes per Cycle - The number of minutes in a cycle
  - Key Generation Data - The name of a file uploaded to the challenge or a regular expression
    - If a file name is given, then a key will be randomly selected from the file
    - If a regular expression is given, then a key will be randomly generated that matches the regular expression
  - Upload word lists.  These will not be visible to contestants, but will be used to generate keys and hashes.
- In the challenge description the following replacements can will be performed:
    - [HASH] : Current password hash
    - [KING] : Current king of the hill
    - [MIN] : The number of minutes in a challenge cycle
    - [HOLD] : The number of points that will be awarded every cycle
- [HASH] and [KING] will also be replaced in the challenge title

# Examples
## Admin Challenge Setup
![HTML Code](/screenshots/html_code.png) 
## Admin Challenge Preview
![HTML Preview](/screenshots/html_preview.png)
## Unsolved Challenge View
![Unsolved](/screenshots/unsolved.png) 
## Solved Challenge View
![Solved](/screenshots/solved.png)
  
# TODO
- Add complexity levels pressing a '+'
  - Each complexity level has the number of solves before advancing to the next complexity level and it's own "key generation data" line that is the same as described previously
  - Add the ability to rearrange complexity levels
  
# Questions
If you have any questions please contact Akmod (tyler@utos.org)

# Claw-Machine-on-SSH
I am making a claw machine game that runs on terminal. It features multiple icons with different points.
<img width="375" height="201" alt="image" src="https://github.com/user-attachments/assets/f03bed2e-0c5a-4a74-add8-c15f8146f21a" />

It has multiple modes to choose from, currently planning on adding a few more changes.

<img width="517" height="406" alt="image" src="https://github.com/user-attachments/assets/37ffb442-b5dd-436e-9087-40e388203483" />

This is how the classis mode is right now, we have credits which are basically the tokens one would put in a claw machine, lives are the amount of mistakes we can make.

<img width="323" height="191" alt="image" src="https://github.com/user-attachments/assets/7144f6f8-86b1-49ff-befd-0bca74fbfec8" />

This is the ending screen after we either quit or lose our lives or finish our credits

<img width="662" height="383" alt="image" src="https://github.com/user-attachments/assets/4bac1d64-c34c-450d-9984-1ecb642e0d22" />

In this image you can clearly see that you have your own save file per user, so if you are over ssh, make sure to remember your username (Remember it exactly, as it is case sensetive aswell)

### Planning to add new features and bug fixes by december mid
### Features like, buying tokens and lives, toggling off lives, New game modes with fun twists etc
### Bug fixes include the fixing of the message under the claw machine

# HOW TO RUN THE GAME
You can play it either over SSH or locally. I would suggest playing over SSH as you would not have to download anything over your personal computer but If you were to play locally, you could potentially have a smoother gameplay plus sound! (Though the sound system would work only over windows, sorry for that) 
To simply connect, go to connection to the game page!

# OVER SSH
Connect to the game via:
######
    ssh -p 60529 USERNAME@bore.pub

or if that doesnt work try 
######
    ssh -p 60529 USERNAME@159.223.110.159

Replace USERNAME with your own

(If unable to connect contact the owner AKA me on slack {Arche})

upon entering, it will ask you to accept the fingerprint, type 'yes' and press enter
## START PLAYING

After a successful connection, start playing. Instructions are given on screen aswell.

A - move left

D - Move right

S - Drop the claw

Q - QUIT

# LOCALLY

<img width="242" height="102" alt="image" src="https://github.com/user-attachments/assets/f744c978-5a93-4e69-8547-35ad7af1c2c7" />

Install "claw_machine.py" (RED) and "Sounds" (GREEN) folder

The file marked in green is your save file! (You dont have to download that as it gets created automatically)

Also make sure the sounds file and claw_machine.py are in the same location.

<img width="335" height="362" alt="image" src="https://github.com/user-attachments/assets/d4165cfa-e200-4d7a-9300-f40686cc7055" />

then Run the "claw_machine.py" as administrator (Terminal) and then enter 
#####
    python claw_machine.py


# GAME MODES

Normal                  5 credits, 3 lives      The standard game mode.

Speedrun                999 credits             Play with a large credit supply and scoring quicly

Collector               20 credits, 5 lives     Focus on collecting and earning achievements

Challenge               10 credits              As the name suggests, its a challenge 

## Prize and Scoring

Common             10

Uncommon           25

Rare               50

Ultra Rare        100

The game also uses credits and lives



*AI help was taken (unfortunately i ran into errors which i lowkey couldnt figure out along with learning a few things)*
  *Took help from youtube, google etc aswell*

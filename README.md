# Claw-Machine-on-SSH
I am making a claw machine game that runs on terminal. It features multiple icons with different points.
<img width="375" height="201" alt="image" src="https://github.com/user-attachments/assets/f03bed2e-0c5a-4a74-add8-c15f8146f21a" />

It has multiple modes to choose from, currently planning on adding a few more changes.

<img width="517" height="406" alt="image" src="https://github.com/user-attachments/assets/37ffb442-b5dd-436e-9087-40e388203483" />

This is how the classis mode is right now, we have credits which are basically the tokens one would put in a claw machine, lives are the amount of mistakes we can make.

<img width="323" height="191" alt="image" src="https://github.com/user-attachments/assets/7144f6f8-86b1-49ff-befd-0bca74fbfec8" />

This is the ending screen after we either quit or lose our lives or finish our credits

# HOW TO RUN THE GAME
You can play it either over SSH or locally. I would suggest playing over SSH as you would not have to download anything over your personal computer but If you were to play locally, you could potentially have a smoother gameplay plus sound! (Though the sound system would work only over windows, sorry for that)

# OVER SSH
The instructions would be different for windows and mac/linux

## Generate a player key
ssh-keygen -t ed25519 

## Submit the public key
Find the public key file. The default location is:

Operating system   Public key file

Windows            %USERPROFILE%\\.ssh\\id_ed25519.pub
macOS              ~/.ssh/id_ed25519.pub
Linux              ~/.ssh/id_ed25519.pub

Share the contents of the .pub file only with the host so it can
be authorized.

## CONNECTION TO THE GAME
Connect to the game via:
ssh -p 56536 USERNAME@bore.pub

Replace USERNAME with your own
(If unable to connect contact the owner AKA me on slack {Arche})
## START PLAYING
After a successful connection, start playing. Instructions are given on screen aswell.
A - move left
D - Move right
S - Drop the claw
Q - QUIT

# LOCALLY
Install "claw_machine.py" and "Sounds" folder
then Run the "claw_machine.py" as administrator (Terminal) and then enter python claw_machine.py


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

  Will try to add more awesome features/gamemodes aswell

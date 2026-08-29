# Spring challenge 2026. Discussion — forum thread, verbatim (context only)

- URL: https://forum.codingame.com/t/208196
- Fetched: 2026-08-28 via `https://forum.codingame.com/raw/208196?page=1`
- Language: English
- Why archived: rule clarifications by the game author (early-end condition change after the contest; wood-boss behaviour; tree cooldowns; referee source and pre-built jar).

Nothing below this line was written by us.

---

AlitorTheWise | 2026-05-13 11:20:23 UTC | #1

I need some help getting started. But I'm not sure if it's okay to ask for help.
- I can't find which variable contains the shak's position. (So I don't know how to return.) 

\- I also don't know which variable contains the information about the trees (or the terrain). 

\- When I give the troll a command to move, am I supposed to wait until it reaches its destination? How do I know when it arrives? 

Sorry, maybe this is a bit too much for me. 

Thank you for not kicking me out of the community XD

-------------------------

eulerscheZahl | 2026-05-13 03:41:48 UTC | #2

> I can’t find which variable contains the shak’s position.

Statement says: **Next** height **lines**: each line has width characters: In this league every character is **.** for **GRASS**, **0** for your own **SHACK**, **1** for your opponent's **SHACK**.

Initially we had an error in the wood statement, not explaining the shack location there - patched that about 1 hour after contest launch. So it’s possible that you missed it because of that.

> I also don’t know which variable contains the information about the trees (or the terrain).

Each turn you get the number of trees, then the properties for each tree. The starter code helps you parse the input, but you have to store it somewhere.

The terrain (grass, water, rock, iron) is given in the first turn only, along with the shack locations.

> When I give the troll a command to move, am I supposed to wait until it reaches its destination? How do I know when it arrives?

You give a command and the troll moves 1 step towards the destination (or whatever movementSpeed the troll has). Then you get an updated game state as input and can check if you have to walk any further or if you can harvest a fruit for instance.

> Thank you for not kicking me out of the community XD

Everyone is welcome here. Some compete to win, others learn the basic steps, that’s perfectly fine.

-------------------------

AngelFireLA | 2026-05-13 11:44:43 UTC | #3

I do find it much more difficult to get out of the Wood League 1 than the usual bot challenges, as you need a perfect 10/10 wins without even a single draw, and you also need enough luck to face the top players in the first place instead of the top 30-10 (it does increase towards the end matches but not fast enough). Some maps are nearly mathematically solvable which makes it really hard to really find a winning algorithm when it’s supposed to be the first tutorial league

by resubmitting the same code I can end up between 16th to 5th and with more attempts it probably varies more

-------------------------

eulerscheZahl | 2026-05-13 13:03:44 UTC | #4

I'm confused.
> face the top players in the first place instead of the top 30-10

In wood you only get 5 matches against the boss, nothing else. Win 3 of them and you get promoted. Are you in the correct thread, is this about the Troll Farm contest?


The boss intentionally goes to the second-closest tree with fruits instead of the closest, giving you a chance to score more points. The wood 1 boss TRAINs in the first turn and plants next to the own shack in addition to that.

-------------------------

AngelFireLA | 2026-05-13 13:28:26 UTC | #5

I don’t know what I was playing ? I just reloaded the page and it’s completely different.
I think i somehow ended up in the demo for the first league 

I don’t know how that happened as I remember clicking on the right thing
so I was actually competing against others that submitted in the demo part ?
I was in https://www.codingame.com/ide/demo/1423805f9c28c9654cfd4d57b0208df71315c49 instead of 

I think I was too tired as I did that at 11 pm and somehow didn’t realize this morning. I don’t know how I didn’t see the thing top right when it’s how I also checked the rules for the next leagues
Sorry for the confusion and it makes much more sense, I also don’t know how I didn’t realize there was no boss in the rankings
Thank you for the answer and have a nice day

-------------------------

AngelFireLA | 2026-05-13 13:38:02 UTC | #6

While I’m at it, is there any logic for the cooldown of trees ? Like if it depends on the type of tree or other factors, if it’s a specific value for the whole game or if it has some variance ? As I tried to understand from watching the matches but I’m still unsure

-------------------------

eulerscheZahl | 2026-05-13 13:42:14 UTC | #7

Each plant type has 2 cooldowns. One when it's on grass, one when next to water.
From the statement:
![image|452x63](upload://d5qIoFnG3szdRAMAQtbFASTjsmg.png)

-------------------------

bodbod | 2026-05-15 13:57:54 UTC | #8

Hi, how do I get past the Wood League?

Because I’m 16th and nothing’s happening. I beat the boss easily, but I’m stuck in the Wood League.

EDIT : ok sorry my problem it’s like @AngelFireLA

-------------------------

SaintAutist | 2026-05-15 18:23:44 UTC | #9

Hello all, 

I feel like I’m missing something in the instructions but I just can’t understand how to keep adding commands. 

Do I need to just put a bunch of print commands at the bottom and hope I land on something? If the map changes every time you run against someone how do I keep moving my troll to trees in a new map. 

Really struggling with how to get off the ground on this one and could use some advice.

-------------------------

Patricia | 2026-05-15 19:27:53 UTC | #11

In each game loop you have to read where the trees are and at the beginning of each game you get a map to see where your shack is. 

You have to compute with these things  where to move your trolls to.

-------------------------

Civion | 2026-05-16 13:42:45 UTC | #12

Hi everyone! 

Do we have a local runner for this challenge as we had for some previous ones?

-------------------------

eulerscheZahl | 2026-05-16 13:52:54 UTC | #13

Source code: https://github.com/eulerscheZahl/Troll-Farm
Pre-built binary: https://github.com/eulerscheZahl/Troll-Farm/releases

-------------------------

BoatBuilder | 2026-05-21 12:39:48 UTC | #14

Hello, it seems that the opening time for the Legend League is after the end of the contest (**League opening: May 28, 2026** is displayed when clicking on the League button while in the editor).

-------------------------

Ekaon | 2026-05-21 16:34:05 UTC | #15

Hello, I was wondering, what are the legal rights about the game ? I feel like this is a great game, and i would like to make it a mobile app PVP for the fun, available on android playstore. But I don’t know if this is okay, or if the codingame community would find it fun to play it as a human.

-------------------------

eulerscheZahl | 2026-05-21 16:56:05 UTC | #16

We have a [license section](https://github.com/eulerscheZahl/Troll-Farm/#license) on the github repo. MIT license for the code - so pretty much do with it what you want. As the author of the code I have no problem with you turning the game into an app and reusing some of the code along the way. The concept of the game is also original and not a port of an existing game.
For the assets please check the original sources as linked on github and in the problem statement. For some you have to give credits or pay a small fee to use them.

-------------------------

eulerscheZahl | 2026-05-21 16:57:01 UTC | #17

Did you keep the tab open for a long time? Then the display sometimes gets confused. Legend will open in about 15 hours from now.

-------------------------

Ekaon | 2026-05-21 17:16:22 UTC | #18

Great ! Thank you !

-------------------------

BoatBuilder | 2026-05-22 18:18:47 UTC | #19

I did indeed. Now it works, thanks !

-------------------------


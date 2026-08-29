# Troll Farm - Spring Challenge 2026 - Puzzle discussion — forum thread, verbatim (context only)

- URL: https://forum.codingame.com/t/208252
- Fetched: 2026-08-28 via `https://forum.codingame.com/raw/208252?page=1`
- Language: English
- Why archived: rule clarifications by the game author (early-end condition change after the contest; wood-boss behaviour; tree cooldowns; referee source and pre-built jar).

Nothing below this line was written by us.

---

CommunityBot | 2026-05-26 10:17:17 UTC | #1

 https://www.codingame.com/multiplayer/bot-programming/spring-challenge-2026-troll-farm

Send your feedback or ask for help here!

-------------------------

eulerscheZahl | 2026-05-26 10:31:38 UTC | #2

We slightly changed the early end condition: when the last tree gets chopped, the players have enough time to return the wood to the shack, when taking the shortest path back home.
The limit of 300 turns per game is unaffected by this.

-------------------------

arekbulski | 2026-05-26 17:26:45 UTC | #3

Before I rant, huge thankyous for creating this particular puzzle for us. I enjoyed it.

My issue is with time in game. I wrote the input parser in Python, but since I would like to write some kind of heavier AI I decided to rewrite it in C#. To my surprise, both need at min 15 ms each turn (just to parse inputs) and very very often they go over 50 ms allotted. I was going to end my rant with a question but I forgot what it was… (any reply is welcome).

-------------------------

eulerscheZahl | 2026-05-26 18:59:38 UTC | #4

This boils down to one question: how do you measure time? The order should be:
```
read input (or first line of input at least)
start timer
do computations
stop timer
print stderr
print output
```
If you start the timer before reading the input, you also measure all kind of other things that are out of your control: the time used by your opponent and the referee (the program that plays the game and executes the players).

-------------------------

arekbulski | 2026-05-26 19:24:50 UTC | #5

Just for reference, this is my C# code. Both ReadParse() methods are reading from stdin and parse the data.

```
public class MainClass
{
    public static void Main()
    {
        var wm = WorldMap.ReadParse();
        var sw = Stopwatch.StartNew();
        while (true)
        {
            sw.Restart();
            var gs = GameState.ReadParse();
            var elapsed = sw.ElapsedMilliseconds;
            Console.WriteLine($"MSG {elapsed}");
        }
    }
}
```

-------------------------

eulerscheZahl | 2026-05-27 04:43:24 UTC | #6

The first `ReadParse` only happens before the loop, not for every turn. For every turn thereafter you measure the opponent as well. If your gamestate parsing doesn’t do any heavy lifting, just start the timer after it.

-------------------------

VINCE_MX | 2026-05-30 20:48:17 UTC | #7

Will there be some embedded replays on the details page of this game?

-------------------------

barciuw | 2026-06-05 08:54:59 UTC | #8

Would you mind sharing your ideas/strategies? How did you approach this challenge?

-------------------------

5DN1L | 2026-06-05 10:47:29 UTC | #9

You may refer to [this topic](https://www.codingame.com/forum/t/spring-challenge-2026-troll-farm-feedback-strategies/208241).

-------------------------

FreZzz | 2026-07-15 12:58:53 UTC | #10

Hi, eulerscheZahl !

I think there is still an issue on that, as we can see at the end of the game https://www.codingame.com/replay/895920702 : two of my trolls are loaded with wood but don’t have enough time to bring it back to the shack.

Regards

-------------------------

eulerscheZahl | 2026-07-15 14:07:51 UTC | #11

Nothing wrong with this: there are no more fruits remaining, thus no planting possible. And you already won before dropping all the wood, nothing you can do (except crashing) would change the outcome.

-------------------------

FreZzz | 2026-07-15 15:37:57 UTC | #12

I agree it wouldn’t change the game result. It was just about the statement “when the last tree gets chopped, the players have enough time to return the wood to the shack“ that was not true. Didn’t thought the referee would do such a computation.

-------------------------

eulerscheZahl | 2026-07-15 16:03:21 UTC | #13

I was a bit lazy and just described the change. The early end when either play can enforce a win by doing nothing already existed in the contest and remained unchanged.

-------------------------


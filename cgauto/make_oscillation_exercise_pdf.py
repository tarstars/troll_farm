#!/usr/bin/env python3
"""Generate a plain-English PDF of the 2026-08-09 oscillation exercise.

Owner-requested. Documents one experiment in collaboration: three AI agents were
given the same question independently, and the merged answer overturned the fix
all of them would otherwise have built. Written so a reader who knows nothing
about the project can follow it.

Usage:  python3 cgauto/make_oscillation_exercise_pdf.py [out.pdf]
Default out: docs/reports/2026-08-09-oscillation-exercise.pdf
"""
import pathlib
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "docs" / "reports" / "2026-08-09-oscillation-exercise.pdf"
FONT_DIR = pathlib.Path("/usr/share/fonts/truetype/dejavu")

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5a5a5a")
RULE = colors.HexColor("#c8c8c8")
BAND = colors.HexColor("#f0f0f0")
ACCENT = colors.HexColor("#8a4b08")
ALERT = colors.HexColor("#7d2a2a")


def register_fonts():
    pdfmetrics.registerFont(TTFont("DJV", str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DJV-B", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DJV-I", str(FONT_DIR / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DJV-M", str(FONT_DIR / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFontFamily("DJV", normal="DJV", bold="DJV-B", italic="DJV-I")


def styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle("title", parent=base["Title"], fontName="DJV-B",
                                fontSize=22, leading=28, textColor=INK, spaceAfter=4)
    s["subtitle"] = ParagraphStyle("subtitle", parent=base["Normal"], fontName="DJV",
                                   fontSize=11.5, leading=16.5, textColor=MUTED,
                                   spaceAfter=18)
    s["h1"] = ParagraphStyle("h1", parent=base["Heading1"], fontName="DJV-B",
                             fontSize=15, leading=19.5, textColor=INK,
                             spaceBefore=19, spaceAfter=7)
    s["h2"] = ParagraphStyle("h2", parent=base["Heading2"], fontName="DJV-B",
                             fontSize=11.5, leading=15, textColor=ACCENT,
                             spaceBefore=12, spaceAfter=5)
    s["body"] = ParagraphStyle("body", parent=base["Normal"], fontName="DJV",
                               fontSize=10, leading=15.2, textColor=INK,
                               alignment=TA_JUSTIFY, spaceAfter=8)
    s["bullet"] = ParagraphStyle("bullet", parent=s["body"], leftIndent=14,
                                 bulletIndent=3, spaceAfter=5)
    s["note"] = ParagraphStyle("note", parent=s["body"], fontSize=9.3, leading=14,
                               textColor=MUTED, leftIndent=12, rightIndent=12,
                               spaceBefore=4, spaceAfter=10)
    s["key"] = ParagraphStyle("key", parent=s["body"], fontSize=10.5, leading=16,
                              textColor=ALERT, leftIndent=10, rightIndent=10,
                              spaceBefore=6, spaceAfter=10)
    s["code"] = ParagraphStyle("code", parent=base["Normal"], fontName="DJV-M",
                               fontSize=8.6, leading=12.2, textColor=INK,
                               leftIndent=14, spaceBefore=4, spaceAfter=8)
    s["cell"] = ParagraphStyle("cell", parent=base["Normal"], fontName="DJV",
                               fontSize=9, leading=12.6, textColor=INK)
    s["cellb"] = ParagraphStyle("cellb", parent=s["cell"], fontName="DJV-B")
    return s


def furniture(canvas, doc):
    canvas.saveState()
    canvas.setFont("DJV", 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(2.2 * cm, 1.4 * cm,
                          "The oscillation exercise - 9 August 2026")
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.4 * cm, str(doc.page))
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(2.2 * cm, 1.85 * cm, A4[0] - 2.2 * cm, 1.85 * cm)
    canvas.restoreState()


def table(rows, s, widths, highlight=None):
    data = [[Paragraph(c, s["cellb"] if i == 0 else s["cell"]) for c in row]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BAND),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if highlight:
        style.append(("BACKGROUND", (0, highlight), (-1, highlight),
                      colors.HexColor("#fdf2e9")))
    t.setStyle(TableStyle(style))
    return t


def build(out_path: pathlib.Path):
    register_fonts()
    s = styles()
    doc = BaseDocTemplate(str(out_path), pagesize=A4,
                          leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                          topMargin=2.0 * cm, bottomMargin=2.3 * cm,
                          title="The oscillation exercise - 9 August 2026",
                          author="local_claude_1")
    doc.addPageTemplates([PageTemplate(id="main", frames=[
        Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")],
        onPage=furniture)])

    f = []
    P = lambda t, k="body": f.append(Paragraph(t, s[k]))
    B = lambda t: f.append(Paragraph(t, s["bullet"], bulletText="•"))
    GAP = lambda h=6: f.append(Spacer(1, h))

    # ------------------------------------------------------------ title
    P("Three answers to one question", "title")
    P("The oscillation exercise, 9 August 2026<br/>"
      "How asking three AI agents the same question separately stopped us "
      "building the wrong fix.", "subtitle")

    P("<b>In one paragraph.</b> Our game-playing program has a bug: one of its "
      "two characters can get stuck pacing between two squares, doing nothing, "
      "for up to 97% of a game. We decided to remove it. Rather than have one "
      "agent design the fix, we gave the same question to three agents working "
      "independently, forbidden from reading each other until they had "
      "published. All three would have endorsed roughly the same repair. One of "
      "them then measured something that proved that repair would not work: it "
      "would silence the warning without unsticking the program. We found that "
      "out for the cost of a day of analysis instead of a week of building.")

    # ------------------------------------------------------------ the bug
    P("1. The bug, in plain terms", "h1")

    P("The game has two woodcutter characters who move around a small map "
      "chopping trees. Sometimes one of them wants to walk to a tree, but its "
      "partner is standing in the way. The program then tries a detour: it steps "
      "sideways or backwards to go around.")

    P("The problem is that the detour has <b>no memory</b>. Next turn the "
      "program recalculates the best route from where it now stands, and the "
      "best route runs straight back through the square it just left. So it "
      "steps back. Now the partner is in the way again. It detours again. "
      "Forever.")

    P("Nothing can break the loop, because nothing changes: the character never "
      "arrives, the partner never moves (it is busy chopping), and the "
      "destination never changes because it is still the best tree.")

    f.append(KeepTogether([
        Paragraph("Measured on our candidate program", s["h2"]),
        table([
            ["What", "Value"],
            ["Games affected", "32 of 240"],
            ["Separate episodes", "34"],
            ["Worst single episode", "194 turns of a 200-turn game"],
            ["Episodes that never resolve", "20 of 34"],
        ], s, [7.0 * cm, 7.8 * cm]),
    ]))
    GAP(10)

    P("Every one of the 34 episodes is a two-square loop between neighbouring "
      "squares. Not a wandering path — a metronome.")

    # ----------------------------------------------------------- why fix
    P("2. Why we decided to fix it, and why that mattered", "h1")

    P("This is the interesting part of the exercise, because the obvious "
      "justification was already ruled out.")

    P("Our own records say oscillation is a closed subject. A previous attempt "
      "fixed it well — driving the rate <i>below</i> the reference bot we copied "
      "our design from — and measured the benefit at <b>+0.045 points</b>, which "
      "is indistinguishable from zero. The written conclusion was \"do not "
      "reopen\".", "note")

    P("So the work could not be justified by score. The owner gave a different "
      "reason:")

    P("<i>\"Oscillations are our lack of control over the program. I want to "
      "remove them not in order to immediately improve score, but to reduce "
      "technical debt, improve our test coverage and understanding of the "
      "situation.\"</i>", "key")

    P("That reframing changed what counted as a good answer, and it invalidated "
      "two proposals the coordinator had already made — both of which would have "
      "made the warning go away without making the program more controlled. They "
      "were withdrawn.")

    P("It also set a sharper target: success is not \"the counter reads zero\". "
      "Success is that the program <i>cannot</i> enter a 194-turn no-op, that a "
      "test proves it, and that we can explain why the design allowed it.")

    # ------------------------------------------------------- the exercise
    P("3. How the exercise was run", "h1")

    P("Three agents — called <b>local_claude_1</b> (the coordinator, who also "
      "answered), <b>claude_1</b> and <b>chatgpt_1</b> — were given one written "
      "brief and three rules:")

    B("Answer independently. <b>Do not read another agent's answer before "
      "publishing your own</b>, and state in writing that you did not.")
    B("The list of possible actions must be wide. Explicitly <i>not</i> limited "
      "to \"test the code, fix the code\" — changing what we require, changing "
      "the test harness, or arguing for doing nothing were all allowed.")
    B("Any proposed fix must remove <b>all 20</b> never-resolving episodes, not "
      "merely reduce the count. A previous fix passed its own quality check "
      "perfectly and left the worst case completely unchanged.")

    P("The reason for the independence rule is specific rather than "
      "philosophical: each of these three agents had been caught in a factual "
      "error by one of the others during the preceding week. Agreement reached "
      "in conversation is worth much less than agreement reached separately.", "note")

    # ------------------------------------------------------- the finding
    P("4. The finding that changed the answer", "h1")

    P("All three agents identified the memoryless detour. The natural fix "
      "follows immediately: give it a memory, so it cannot step back to the "
      "square it just came from. That breaks a two-square loop by construction, "
      "and every episode is a two-square loop.")

    P("<b>claude_1 then measured the one thing nobody else had checked: what the "
      "blocking partner is doing.</b>", "h2")

    P("It found that every oscillation step is either toward the goal or away "
      "from it — never sideways. So a rule forcing \"move forward or stand "
      "still\" would eliminate 34 of the 35 episodes. But it also found that in "
      "<b>all 20 of the never-resolving cases, the blocking partner never moves "
      "at all</b>.")

    P("So the memory fix would stop the pacing and change nothing else. The "
      "character would stand still instead of pacing, still blocked, still "
      "achieving nothing, for the same 194 turns. <b>Twenty oscillations become "
      "twenty stalls. The warning light goes off. The program is exactly as "
      "stuck.</b>", "key")

    P("Under the owner's stated goal — control, not cosmetics — that is the "
      "worst possible outcome: it would have destroyed the evidence that "
      "anything was wrong.")

    # ----------------------------------------------------- other findings
    P("5. What else each agent found alone", "h1")

    P("claude_1", "h2")
    B("<b>A loophole nobody had seen.</b> The program is supposed to stop its "
      "two characters choosing the same destination, and it has a check for "
      "exactly that. But the check returns \"compatible\" automatically whenever "
      "one character has no destination set — so the guard can be bypassed. The "
      "coordinator had quoted that function in its own analysis and read only "
      "the other half of it.")
    B("<b>A second, separate cause located for the first time</b>, in the "
      "endgame logic: a character standing on a doorway prices only that "
      "doorway, so it values the same plan about 25% higher one step off it — "
      "and oscillates between the two. This mattered far beyond its one "
      "occurrence, because the quality rule requires <i>zero</i> episodes, so a "
      "single unexplained case blocks everything.")

    P("chatgpt_1", "h2")
    B("<b>The defect is a seam, not a function.</b> The part that chooses "
      "destinations and the part that resolves collisions are each correct on "
      "their own. The collision-resolver quietly overrides the destination "
      "plan, and never tells the planner it did. Two correct components compose "
      "into a permanent loop.")
    B("It also listed which pieces of a retired older program are worth "
      "salvaging — including a \"stay put\" option our current program lacks.")

    P("local_claude_1 (coordinator)", "h2")
    B("Confirmed the mechanism by reading the program's source, and established "
      "that the program already remembers other things between turns but "
      "remembers <b>nothing about position</b> — so a memory fix needs no new "
      "architecture.")
    B("Found that the original author of the design we copied <i>knew about this "
      "and shipped it anyway</i>. His public write-up says: \"I didn't optimize "
      "movement at all. I only set the destination, which meant my trolls "
      "occasionally blocked each other.\" He finished 3rd. So this is an "
      "inherited limitation, not something we broke.")
    B("Measured that games containing a never-resolving episode are far worse "
      "for us — an average margin of +1.6 versus +16.7 — but argued this is "
      "probably a symptom rather than a cause, since directly fixing the "
      "oscillation was measured at +0.045. Those games likely contain a "
      "different, undiagnosed problem.")

    # -------------------------------------------------------- convergence
    P("6. Where they agreed without conferring", "h1")

    P("Three points were reached separately by more than one agent, which is "
      "the strongest evidence this setup can produce:")

    f.append(table([
        ["Agreed point", "Reached by"],
        ["The memoryless detour is the immediate mechanism", "all three"],
        ["A movement-only fix is not enough",
         "all three, by three different arguments"],
        ["The old program's anti-stall timer cannot be reused - it watches for a "
         "character standing still, and an oscillating character moves every turn",
         "two, independently"],
    ], s, [10.0 * cm, 4.8 * cm]))
    GAP(8)

    P("That third point is worth noting: reusing the old timer was suggested in "
      "the coordinator's own brief. Two agents independently showed it could "
      "never fire on this bug.", "note")

    # ------------------------------------------------------- merged plan
    P("7. The merged plan", "h1")

    P("Combining claude_1's measurement with chatgpt_1's framing gives one "
      "principle that neither stated alone:")

    P("<b>Because the blocker is standing still and doing useful work, the "
      "moving character must choose a different destination — not a different "
      "route.</b> No cleverness in the movement code helps when the obstacle is "
      "never going to leave.", "key")

    f.append(table([
        ["#", "Action", "From"],
        ["1", "Close the loophole that lets both characters pick the same "
              "destination", "claude_1"],
        ["2", "Fix the doorway pricing bug in the endgame logic", "claude_1"],
        ["3", "<b>Make destination-choosing aware of the route</b>, so a "
              "destination blocked by a stationary partner is never chosen. "
              "This is the load-bearing change.", "chatgpt_1"],
        ["4", "Give the mover a \"stand still\" option - safe only behind step 3, "
              "and the stall-generator without it", "chatgpt_1"],
        ["5", "Freeze the 20 worst cases as permanent regression tests",
         "chatgpt_1 + coordinator"],
    ], s, [0.8 * cm, 10.6 * cm, 3.4 * cm], highlight=3))
    GAP(10)

    P("The acceptance rule was also sharpened by the exercise. \"Zero episodes\" "
      "is no longer sufficient on its own, because a stalled character scores "
      "zero episodes too. The requirement is now zero episodes <b>and</b> "
      "restored progress in those games.")

    P("One genuine disagreement was left in place rather than smoothed over: "
      "claude_1 treats the blocked corridor as the primary defect, chatgpt_1 "
      "treats the planner/resolver seam as primary. They are the same problem "
      "described at different levels, and the plan acts on both, but they are "
      "not the same claim.", "note")

    # ------------------------------------------------------------- honest
    P("8. What the coordinator got wrong", "h1")

    P("Recorded because the value of this exercise depends on the errors being "
      "visible:")

    f.append(table([
        ["Claim", "Outcome"],
        ["\"Same-destination contention is the wrong explanation\" - sent as a "
         "correction to both agents",
         "Wrong. claude_1 found the loophole that allows it, in code the "
         "coordinator had quoted and half-read."],
        ["Recommended the memory fix as the primary action",
         "Withdrawn. claude_1's 20-of-20 measurement showed it produces stalls "
         "instead."],
        ["Recommended relaxing the quality rule, and repairing only a test copy "
         "rather than the real program",
         "Withdrawn on the owner's reframing - both make a number acceptable "
         "without gaining control."],
        ["Suggested reusing the old anti-stall timer",
         "Refuted twice, independently."],
    ], s, [6.4 * cm, 8.4 * cm]))
    GAP(10)

    # ------------------------------------------------------------- value
    P("9. What the exercise cost and returned", "h1")

    P("<b>Cost:</b> roughly a day, three agents, no code written, nothing "
      "submitted to the live competition.")

    P("<b>Returned:</b> a fix that would have silenced the symptom and left the "
      "bug was identified <i>before</i> being built; a second independent cause "
      "was located for the first time; a loophole in existing safety logic was "
      "found; a reuse suggestion was refuted twice; and the acceptance criterion "
      "was corrected so that the wrong fix cannot pass it in future.")

    P("The one structural lesson: <b>the decisive fact was something nobody was "
      "asked to check.</b> The brief asked why the character oscillates. The "
      "finding that mattered came from asking what the <i>other</i> character "
      "was doing. Independence is what allowed one agent to spend its attention "
      "somewhere the brief did not point.")

    GAP(10)
    P("Prepared 9 August 2026 by local_claude_1. Every figure was taken from "
      "committed measurements and re-verified while writing. Source documents: "
      "the task brief, three independent answers, and the merged plan, all in "
      "the project repository.", "note")

    doc.build(f)


def main() -> int:
    out = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    build(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Current-state PDF: where the project stands and what happens next.

Owner-requested 2026-08-10. Supersedes the five-day summary of 2026-08-08 as the
standing status document. Written for a reader who knows none of the codenames.

Usage:  python3 cgauto/make_status_report_pdf.py [out.pdf]
Default out: docs/reports/2026-08-10-status-and-next-moves.pdf
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
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "docs" / "reports" / "2026-08-10-status-and-next-moves.pdf"
FONT_DIR = pathlib.Path("/usr/share/fonts/truetype/dejavu")

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5a5a5a")
RULE = colors.HexColor("#c8c8c8")
BAND = colors.HexColor("#f0f0f0")
ACCENT = colors.HexColor("#8a4b08")
ALERT = colors.HexColor("#7d2a2a")
GO = colors.HexColor("#25603a")


def register_fonts():
    for tag, name in (("DJV", "DejaVuSans.ttf"), ("DJV-B", "DejaVuSans-Bold.ttf"),
                      ("DJV-I", "DejaVuSans-Oblique.ttf")):
        pdfmetrics.registerFont(TTFont(tag, str(FONT_DIR / name)))
    pdfmetrics.registerFontFamily("DJV", normal="DJV", bold="DJV-B", italic="DJV-I")


def styles():
    b = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle("t", parent=b["Title"], fontName="DJV-B", fontSize=22,
                                leading=27, textColor=INK, spaceAfter=4)
    s["subtitle"] = ParagraphStyle("st", parent=b["Normal"], fontName="DJV", fontSize=11.5,
                                   leading=16.5, textColor=MUTED, spaceAfter=18)
    s["h1"] = ParagraphStyle("h1", parent=b["Heading1"], fontName="DJV-B", fontSize=15,
                             leading=19.5, textColor=INK, spaceBefore=18, spaceAfter=7)
    s["h2"] = ParagraphStyle("h2", parent=b["Heading2"], fontName="DJV-B", fontSize=11.5,
                             leading=15, textColor=ACCENT, spaceBefore=12, spaceAfter=5)
    s["body"] = ParagraphStyle("bd", parent=b["Normal"], fontName="DJV", fontSize=10,
                               leading=15.2, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8)
    s["bullet"] = ParagraphStyle("bu", parent=s["body"], leftIndent=14, bulletIndent=3,
                                 spaceAfter=5)
    s["note"] = ParagraphStyle("nt", parent=s["body"], fontSize=9.3, leading=14,
                               textColor=MUTED, leftIndent=12, rightIndent=12,
                               spaceBefore=4, spaceAfter=10)
    s["key"] = ParagraphStyle("ky", parent=s["body"], fontSize=10.5, leading=16,
                              textColor=ALERT, leftIndent=10, rightIndent=10,
                              spaceBefore=6, spaceAfter=10)
    s["go"] = ParagraphStyle("go", parent=s["key"], textColor=GO)
    s["cell"] = ParagraphStyle("c", parent=b["Normal"], fontName="DJV", fontSize=9,
                               leading=12.6, textColor=INK)
    s["cellb"] = ParagraphStyle("cb", parent=s["cell"], fontName="DJV-B")
    return s


def furniture(canvas, doc):
    canvas.saveState()
    canvas.setFont("DJV", 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(2.2 * cm, 1.4 * cm, "Troll Farm - status and next moves, 10 August 2026")
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.4 * cm, str(doc.page))
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(2.2 * cm, 1.85 * cm, A4[0] - 2.2 * cm, 1.85 * cm)
    canvas.restoreState()


def table(rows, s, widths, hi=None):
    data = [[Paragraph(c, s["cellb"] if i == 0 else s["cell"]) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    st = [("BACKGROUND", (0, 0), (-1, 0), BAND),
          ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
          ("LINEBELOW", (0, 1), (-1, -2), 0.25, RULE),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
    if hi:
        st.append(("BACKGROUND", (0, hi), (-1, hi), colors.HexColor("#fdf2e9")))
    t.setStyle(TableStyle(st))
    return t


def build(out: pathlib.Path):
    register_fonts()
    s = styles()
    doc = BaseDocTemplate(str(out), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                          topMargin=2.0 * cm, bottomMargin=2.3 * cm,
                          title="Troll Farm - status and next moves, 10 August 2026",
                          author="local_claude_1")
    doc.addPageTemplates([PageTemplate(id="m", frames=[
        Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="b")],
        onPage=furniture)])
    f = []
    P = lambda t, k="body": f.append(Paragraph(t, s[k]))
    B = lambda t: f.append(Paragraph(t, s["bullet"], bulletText="•"))
    GAP = lambda h=6: f.append(Spacer(1, h))

    P("Where we are, and what happens next", "title")
    P("Troll Farm status, 10 August 2026<br/>"
      "Supersedes the five-day summary of 8 August. No prior knowledge assumed.", "subtitle")

    P("<b>One paragraph.</b> We are trying to make a program win more games of an online "
      "strategy contest. The competition program has not changed in a week and is not "
      "expected to change soon. Everything since has gone into the equipment we use to "
      "judge changes, because we discovered that equipment was giving meaningless answers. "
      "That work is close to finished for one component and just beginning for another. We "
      "also found, along the way, that <b>the best program we have ever measured is not the "
      "one we are running</b>.")

    # ---------------------------------------------------------------- state
    P("1. Current state", "h1")

    f.append(table([
        ["Item", "State"],
        ["Competition program", "Unchanged. Scores <b>22.81</b>, rank 32 of 137."],
        ["Best program we have measured",
         "A different one - <b>24.76, rank 21</b> - and it is <b>not running</b>. "
         "One measurement only."],
        ["Quality checkpoint", "<b>Still not usable.</b> Third repair delivered, awaiting review."],
        ["Messaging between agents", "Working. Two broken messages remain, both known."],
        ["Automated tests", "110 passing on the coordination tooling; 148 on the repaired harness."],
        ["Live competition entry", "Untouched. Nothing submitted in over a week."],
    ], s, [4.9 * cm, 9.9 * cm], hi=2))
    GAP(10)

    P("The bot we are not running", "h2")
    P("It is called <b>readable__no_orchard</b>. Three things are true of it at once, and no "
      "other program we have has any two of them: it is the <b>only human-readable</b> one "
      "we ever submitted (1,475 lines; every other is a single line of 55,000+ characters), "
      "it is the <b>smallest</b> by actual code, and it holds the <b>highest score we have "
      "ever measured</b>. We replaced it with something 17% larger and two points worse.")

    P("The reason for caution is real, and the tooling raises it unprompted: that 24.76 is a "
      "<b>single run</b>, and a near-identical program scored 23.27 on its own single run. A "
      "1.5-point spread is wider than the noise we normally assume. One more run would "
      "settle it.", "note")

    # --------------------------------------------------------------- broken
    P("2. Why the quality checkpoint still is not usable", "h1")

    P("The checkpoint runs practice games and reports whether a change is safe. Two "
      "independent defects were found in it, and both are the same shape: <b>the instrument "
      "was measuring something other than what it claimed</b>.")

    B("<b>A check that flagged correct behaviour as a bug.</b> It fired 196 times in a test "
      "where the thing it detects was mathematically impossible. It was not measuring the "
      "delay it was named for; it was measuring an ordinary, intended action.")
    B("<b>A referee that silently ignored a command.</b> The practice-game referee accepted "
      "the instruction to hire a worker, discarded it, and carried on. The program then "
      "re-issued it every turn for the rest of the game. Those games scored as our "
      "<b>cleanest</b> results - nine checks and a liveness monitor, all silent.")

    P("Repairs are on their third round. Rounds one and two were rejected by adversarial "
      "review. Round three closes all eleven outstanding objections, passes 148 tests, and "
      "survives ten deliberate sabotage mutations with none escaping. <b>It awaits one "
      "acceptance review.</b> Until that lands, no judgement about any program change means "
      "anything.")

    # --------------------------------------------------------- oscillation
    P("3. The oscillation work, and what it taught", "h1")

    P("One character can get stuck pacing between two squares, doing nothing, for up to 97% "
      "of a game. You asked for it removed - not for score, but to reduce technical debt and "
      "regain control and understanding of the program.")

    P("Three agents answered the same question independently. <b>The fix all three would "
      "have endorsed does not work</b>: in all twenty never-resolving cases the blocking "
      "partner never moves, so stopping the pacing produces a stalled character instead of "
      "an unstuck one. The warning goes off; nothing improves.", "key")

    P("That single measurement redirected the repair, and we have it because one agent "
      "checked something the brief never asked about.")

    P("Since then the picture has sharpened again, in a way worth knowing:", "h2")
    B("The load-bearing fix is now believed to be an <b>idle-yield rule</b> - make the "
      "stationary idle character move - rather than re-routing the blocked one.")
    B("<b>But that belief is not yet confirmed.</b> The finding came from a library built on "
      "a <i>different</i> program than the one specified, and an independent attempt could "
      "not verify it from stored data. The two programs behave identically on this bug, so "
      "it probably transfers - but probably is not verified.")

    # ------------------------------------------------------------ manifest
    P("4. Making the program's intentions readable", "h1")

    P("You observed that the program's behaviour is defined by assigning numeric weights to "
      "actions, that this hides what the characters are actually trying to do, and that it "
      "has already caused you and the agents to disagree about what the program does.")

    P("Both reviewers confirmed the problem and corrected the premise: <b>weights are only "
      "about a third of the decision</b>. The rest is mode selection, filtering, pair "
      "compatibility, forced replacement and post-decision movement rewriting. So a simple "
      "table of \"intention to number\" was demoted - it would document the easy third.")

    P("The agreed first deliverable is a <b>Decision Packet</b>: a generated, complete "
      "explanation of one turn - every option considered, why each was rejected, what the "
      "program was trying to do, the numbers and their attainable ranges, and what the "
      "movement layer changed afterwards. Its specification is finished.")

    P("An audit of the numbers found <b>10 boundary crossings, 3 ranking inversions and 3 "
      "pieces of dead scoring code</b>. The most striking: one intention is priced at 187 on "
      "turn 250 and 7,000 on turn 251 - a jump of up to 961x at an arbitrary turn number.", "note")

    # --------------------------------------------------------------- next
    f.append(PageBreak())
    P("5. Proposed next moves", "h1")

    P("Ordered by what unblocks the most. Items 1 and 2 need nobody's decision; items 5 and "
      "6 need yours.")

    f.append(table([
        ["#", "Move", "Why now", "Needs"],
        ["1", "Accept or reject the third harness repair",
         "Nothing can be measured until this lands. It is the only thing blocking the "
         "entire quality pipeline.", "chatgpt_1"],
        ["2", "Rebuild the oscillation library on the <b>specified</b> program",
         "The existing one is built on a different program. Everything downstream would "
         "inherit that.", "claude_1"],
        ["3", "Confirm or refute the idle-blocker finding",
         "The whole repair has been redirected around it and it is unverified.",
         "either agent"],
        ["4", "Judge each frozen situation independently",
         "Asks whether a decision was <i>correct</i>. Everything we own today asks only "
         "whether it oscillated.", "both, split"],
        ["5", "<b>Re-run readable__no_orchard for a second measurement</b>",
         "It may be our best program. One run cannot tell a good program from a lucky "
         "draw. Costs nothing but time and uses none of the broken equipment.",
         "<b>your decision</b>"],
        ["6", "<b>Check the repository branch-protection settings</b>",
         "One agent found an attack that could permanently break every agent's messaging "
         "with a single push, and declined to test it because the proof is the damage.",
         "<b>only you can</b>"],
    ], s, [0.7 * cm, 4.5 * cm, 6.7 * cm, 2.7 * cm], hi=5))
    GAP(10)

    P("Item 5 is the one I would press.", "h2")
    P("It is the only move on the list that could improve our competitive standing, it "
      "requires no code and no working checkpoint, and it resolves the most valuable open "
      "question we have: whether the readable program is genuinely two points better than "
      "what we are running, or whether that number was luck. Everything else on this page "
      "is equipment.")

    P("Item 6 takes a minute and is the only item nobody else can do. It is the last "
      "unresolved <i>critical</i> finding from the security review of our own messaging "
      "system.", "go")

    # ------------------------------------------------------------- honesty
    P("6. How much to trust this report", "h1")

    P("Across the last three days the three agents have corrected each other, and "
      "themselves, repeatedly. That is the system working, but it should calibrate how you "
      "read any single claim.")

    f.append(table([
        ["Pattern", "Count over 3 days"],
        ["Claims by the coordinator later found unsupported", "9"],
        ["- caught by another agent", "4"],
        ["- caught by the coordinator before publishing", "3"],
        ["- caught by a tool before publishing", "2"],
        ["Agents correcting their own published work unprompted", "4 occasions"],
        ["Findings reached independently by two or more agents", "5"],
    ], s, [9.4 * cm, 5.4 * cm]))
    GAP(10)

    P("The trend is the useful part: early in the week errors were caught by people after "
      "publication; by the end they were caught by tools and by authors before it. The "
      "single most valuable habit has been requiring two independent reviews before any "
      "conclusion is adopted - it has overturned a recommendation or a premise every single "
      "time it has been applied.")

    P("<b>What has not improved: the score.</b> It has been 22.81 for a week and no move on "
      "this page except item 5 would change it. That is the deliberate consequence of "
      "deciding to repair the measuring equipment first, and it is worth restating plainly "
      "rather than burying.")

    GAP(10)
    P("Prepared 10 August 2026 by local_claude_1. Figures re-derived from committed "
      "artifacts and live tool runs at the time of writing. Supersedes "
      "2026-08-08-five-day-plain-english-summary.pdf.", "note")

    doc.build(f)


def main() -> int:
    out = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    build(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

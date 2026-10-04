# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search is a plain keyword overlap match. It scores a listing by how many of
the user's words show up in the title, description, and style tags. That works
when the user names words the listing actually uses, but a shopper can describe
the same item in words the data does not contain (saying "tee" for a listing
titled "baby tee", or a synonym the seller never wrote), and then a real match
scores zero and gets dropped. 4 of 5 leaves room for that phrasing gap. It is
my search being literal, not the loop failing.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never calls the model and never depends on wording. search_listings is
plain Python, so an impossible query returns an empty list every single time, and
the loop's branch is one `if` on that empty list. There is no randomness and no
second service that could behave differently between tries, so if it stops once
it stops every time. That is why 5 of 5 is fair here when criterion 1 is not.

---

## 3. The item found is the item that gets styled

In 5 of 5 runs, the item id stored in `session["selected_item"]["id"]` is the
same id that reaches `suggest_outfit`, which is the `new_item` it is called with.
I check it by comparing `session["selected_item"]["id"]` against the item
recorded going into the suggest_outfit step. If the two ids ever differ, the
outfit was built for a different item than the one search picked.

**Why this target:**
The selected item travels from search to suggest_outfit through one field in the
session dict, set once by a plain assignment. Nothing random touches it, so the
id that goes in should always be the id that comes back out. I set 5 of 5 because
a single mismatch means the session is being overwritten or the wrong index is
being read, and that is a real bug I want to catch, not acceptable noise.



---

## 4. The fit card names the price

In at least 4 of 5 runs, the fit card contains the item's price, meaning the
number from `new_item["price"]` appears somewhere in the caption. A caption that
never mentions what the item costs is not doing its job, since the price is half
the reason anyone reposts a thrift find.

**Why this target:**
The fit card is written by the model at temperature 0.9, so the exact words
change every run and I cannot pin it to one fixed sentence. What I can ask for is
that the price always lands in the caption. I set 4 of 5 rather than 5 of 5
because the model sometimes rounds the number or writes around it ("just under
twenty"), and that is model variance I can live with, not a broken tool.



---

## 5. The price ceiling is never crossed

When the user gives a max price, every listing `search_listings` returns has a
`price` less than or equal to that ceiling, in 5 of 5 runs. For the query
"vintage graphic tee under $30", no returned listing is above $30.

**Why this target:**
This is a pure filter inside search_listings with no model involved, so it is
deterministic: the same query gives the same results every time. A ceiling that
leaks even once is a plain logic bug, not variance, so there is no reason to
accept anything below 5 of 5. I picked this one because it is the thing a shopper
cares about most and the easiest to get silently wrong, for example when a
PowerShell double quote eats the `$30` before my code ever sees it.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

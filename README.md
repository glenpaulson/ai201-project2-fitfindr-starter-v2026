# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a little shopping agent for second-hand clothes. You ask for
something in plain language, like "vintage graphic tee under $30" and it
searches the thrift listings for items that match your words, your size, and
your price limit. It then picks the best match, suggests an outfit using clothes already in your wardrobe, and writes a short caption (a "fit card") you could post about the find. If nothing matches, it stops early and tells you what to change instead of making something up.

<!-- Scratch notes for myself (Milestone 1):

A listing has 11 fields: id, title, description, category, style_tags
(list), size, condition, price (float), colors (list), brand (str OR None),
platform.

- size is messy: "W30 L30", "S/M", "M/L", "XL (oversized)", "US 9",
"One Size". A plain substring test is a trap. "s" in "us 9" is True,
"l" in "xl" is True. Be careful in search_listings.
- brand is None for a lot of listings. Don't assume it's always there.
- 40 listings, 5 categories (tops, bottoms, outerwear, shoes, accessories), 3 platforms (depop, thredUp, poshmark).
- Empty wardrobe is {"items": []}, so suggest_outfit has to survive that. -->


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Looks through all the thrift listings and returns the ones
  that match the user's keywords, and, when they are given, their size and price
  limit. It scores each listing by how many of the description words overlap with
  the listing's title, description, and style tags, then sorts best match first.
- **Inputs:** `description` (str, the keywords), `size` (str or None, which
  skips size filtering when None), `max_price` (float or None, an inclusive
  ceiling, skipped when None).
- **Returns:** A list of listing dicts, best match first (at most
  `SEARCH_RESULT_LIMIT`, which is 10). Each dict has the full listing fields:
  `id, title, description, category, style_tags, size, condition, price, colors,
  brand, platform`.
- **When it has nothing:** Returns an empty list `[]`, not `None` and not an
  exception. The loop checks this to decide whether to stop.

<!-- Size matching rule I'm committing to (so it isn't a substring trap): compare
     whole tokens, ignoring case. I split the listing's size on spaces and
     slashes, so "S/M" becomes ["s","m"] and "US 8" becomes ["us","8"], then
     keep the listing only if the requested size is one of those tokens. That
     way "M" matches "S/M" and "M/L" but NOT "XL", and "s" does not match
     "US 9". -->

### `suggest_outfit`

- **What it does:** Takes the item the user is considering and their wardrobe,
  and asks the model for one or two outfit ideas that go with the item.
- **Inputs:** `new_item` (dict, one listing), `wardrobe` (dict with an `items`
  key holding a list of wardrobe items; the list may be empty).
- **Returns:** A string of outfit suggestions that is never empty. When the
  wardrobe has items, it names specific pieces the user already owns; when the
  wardrobe is empty, it gives general styling advice for the item instead.
- **When it has nothing:** If `wardrobe["items"]` is empty, it still returns a
  string that is not empty (general styling advice); it does not return `""` or
  raise.

### `create_fit_card`

- **What it does:** Writes a short caption worth posting about the find, based on
  the item and the outfit suggestion.
- **Inputs:** `outfit` (str, the suggestion from `suggest_outfit`), `new_item`
  (dict, the listing).
- **Returns:** A caption of two to four sentences that mentions the item and its
  price and platform once each. Because the model runs with temperature,
  different items give different captions.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns a
  short descriptive message instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, I put a message in
`session["error"]` that names what the user could change and return the session
right away, without calling `suggest_outfit`. Otherwise I take the first result
(the best scoring one) as `session["selected_item"]` and carry on to
`suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** String handling with two small regexes, not the
model. A helper called `parse_query` in `agent.py` pulls out `max_price` (a number
after "under", or any "$NN"), `size` (the token after the word "size"), and uses
whatever text is left over as the `description`.

**What moves through the session:** The fields fill in this order: `query` (what
the user typed), then `parsed` (description, size, max_price), then
`search_results`, then `selected_item`, then `outfit_suggestion`, then
`fit_card`. If the search comes back empty, `error` is set instead and every
field after `search_results` stays `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask "vintage graphic tee under $30"

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair your new Y2K baby tee with the baggy straight-leg jeans and
            chunky white sneakers for a cute, casual throwback look. Throw on the
            black cropped zip hoodie if you need an extra layer!

  Fit card: Obsessed with this Y2K butterfly tee I just scored! It's yours on
            Depop for just $18.00. Pair it with baggy jeans and chunky sneakers
            for the ultimate throwback fit! ✨🦋

2 model calls this session, 326 prompt + 86 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; r=search_listings('graphic tee', max_price=30); print(len(r), 'results, best first:'); [print(' ', x['id'], '|', x['title'], '| $'+str(x['price']), '|', x['size']) for x in r]"
7 results, best first:
  lst_002 | Y2K Baby Tee — Butterfly Print | $18.0 | S/M
  lst_006 | Graphic Tee — 2003 Tour Bootleg Style | $24.0 | L
  lst_017 | Mesh Long-Sleeve Top — Black | $15.0 | S/M
  lst_033 | Vintage Band Tee — Faded Grey | $19.0 | L
  lst_011 | Low-Rise Cargo Pants — Khaki | $27.0 | W29
  lst_012 | Oversized Crewneck Sweatshirt — Vintage Navy | $20.0 | XL (fits oversized)
  lst_015 | Vintage Graphic Hoodie — Faded Black | $26.0 | L
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey there! Those vintage Levi's 501 jeans are such a great find.

Try pairing your new medium wash jeans with the white ribbed tank top, black cropped zip hoodie, and chunky white sneakers for an easy, casual streetwear look.

For a cooler day, throw the vintage black denim jacket over the grey crewneck sweatshirt, tuck the crewneck into the jeans with your brown leather belt, and finish it off with your black combat boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Score! Just hunted down these vintage Levi's 501 jeans in the absolute best medium wash. They can be yours on Depop right now for just $38.00! I'm styling mine with a crisp pair of white sneakers for the ultimate effortless weekend fit. Grab them before I change my mind and keep them!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* A way to filter listings by size that would not fall for
  the substring trap the starter warned about, where "s" matches "us 9" and "l"
  matches "xl".
- *What came back:* The idea to split each listing's size on spaces and slashes
  into whole tokens, so "S/M" becomes ["s", "m"] and "US 8" becomes ["us", "8"],
  then keep a listing only when the requested size equals one of those tokens.
- *What I changed:* I put that rule into `search_listings` and tested it. Asking
  for size "M" returned only the S/M tops, with no XL items and no shoes, so I
  kept it and wrote the rule into my Tool Inventory.

**Moment 2**

- *What I asked for:* Help turning a plain query like "vintage graphic tee under
  $30" into a separate description, size, and price.
- *What came back:* A small regex approach for the price and size, plus the
  suggestion to strip the price and size phrases out of the text before using the
  rest as the description, so their numbers do not get treated as keywords.
- *What I changed:* I used that for `parse_query`, but while testing I noticed the
  keyword match still matches substrings inside other words (so "tee" can match a
  word that only contains "tee"). The real matches still sort to the top, so I
  left it and used that limitation as the reason my criterion 1 target is 4 of 5
  instead of 5 of 5.

**Moment 3 (unit 4)**

- *What I asked for:* Where the `trace.step()` calls should go in `run_agent`,
  and what to pass to each one.
- *What came back:* One call per stage, with the branch decision written into
  the `note` so the trace says why it carried on or stopped, not just what
  happened.
- *What I changed:* The first version passed the `parsed` dict straight in as
  `inputs`. `trace.py` shortens a dict it does not recognise to just its key
  names, so every trace printed `dict with keys: description, size, max_price`
  and none of the actual values. That is useless for diagnosing, which is the
  whole point of the trace, so I pass a formatted string instead and the trace
  now reads `description='levis jeans', size='30', max_price=None`. Criterion 1
  was later diagnosed straight off that line.

**Moment 4 (unit 4)**

- *What I asked for:* I had all five criteria passing 5 of 5 and asked whether
  that was a real result or a weak test.
- *What came back:* That criterion 1 could not fail for the reason I had
  written under it. Saying "given a query that matches at least one listing"
  makes search already having worked a precondition, so the criterion only
  measures whether the loop finishes afterwards, and I had tested it with one
  query five times against a search function with no model in it.
- *What I changed:* Revised criterion 1 to name five different phrasings for
  five items I confirmed are in the data, keeping the original line and the
  target of 4 of 5. On the next run it scored 2 of 5. The revision is what
  turned a clean sheet into an actual finding.

**Moment 5 (unit 4)**

- *What I asked for:* A fix for the scoring ties that were handing back the
  wrong item on two of my five phrasings.
- *What came back:* Score rarer words higher, so `silk` counts for more than
  `green`.
- *What I changed:* Nothing, after measuring it. I counted how often each word
  appears across the 40 listings and scored a match as `1 / that count`. It
  fixes `a green silk shirt` and makes `small tan purse` worse, because `small`
  appears in exactly one listing and so becomes the rarest word in the query.
  It would have taken criterion 1 to 4 of 5 and MET while making one of the two
  broken cases worse, so I left it out and wrote the measurement into What's
  Still Broken instead.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | **MISSED (2/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Produced by `run_eval.py::main` against `agent.py::run_agent`, every scenario in
`scenarios.py` run five separate times with caching off. The whole file is
committed at `results/run_2026-10-11_1825_before.md`. Ten scenarios, fifty runs,
no crashes.

**Reading row 1.** Criterion 1 was revised this unit, and its five tries are
five different phrasings rather than five repeats of one query, so the columns
read left to right as phrasing 1 through phrasing 5:

| Try | Query | Should find | Actually selected | |
|---|---|---|---|---|
| 1 | `levis jeans size 30` | lst_001 Vintage Levi's 501 Jeans | nothing, stopped at step 2 | FAIL |
| 2 | `black bomber jacket` | lst_022 90s Leather Bomber | lst_022 90s Leather Bomber | PASS |
| 3 | `a green silk shirt` | lst_029 Silk Button-Down, Sage Green | lst_024 Vintage Polo Shirt | FAIL |
| 4 | `small tan purse` | lst_039 Mini Shoulder Bag, Tan Leather | lst_002 Y2K Baby Tee | FAIL |
| 5 | `chunky knit cardigan` | lst_008 Oversized Knit Cardigan | lst_008 Knit Cardigan | PASS |

Each phrasing was also run five times and gave the same answer all five times,
so none of this is model variance. `search_listings` has no model in it.

**Why I scored tries 3 and 4 as FAIL.** My criterion says the agent "returns a
fit card", and on a flat reading of those four words tries 3 and 4 passed: a
fit card came back both times. I scored them FAIL anyway, because the criterion
I wrote also has a column headed "the item it should find", and I filled that
column in before I ran anything. Try 4 returned a cheerful caption about a Y2K
butterfly baby tee to someone who asked for a tan purse. Counting that as a
pass would turn the row from MISSED into MET and leave me nothing to diagnose,
which is exactly the move this unit warns about. The looser reading is
available to me and I am not taking it.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

---

#### Criterion 1, try 1: `levis jeans size 30` (FAIL, found nothing)

Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: yes — I couldn't find anything for "levis jeans size 30". Try removing the price limit, using a different size, or simpler keywords.
- selected_item: (none)
- search_results: 0

Trace:
[1] parse_query
      in:  levis jeans size 30
      out: description='levis jeans', size='30', max_price=None
[2] search_listings (via MCP)
      in:  description='levis jeans', size='30', max_price=None
      out: [] (empty)
      →    branch: empty list, stopping before suggest_outfit
```

Two steps and a stop. The agent behaved correctly for what it was handed, an
empty list, and the branch did its job. The problem is upstream: the list
should not have been empty. `lst_001` exists, it is a pair of Levi's jeans, and
its size is `W30 L30`.

---

#### Criterion 1, try 4: `small tan purse` (FAIL, found the wrong thing)

Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 5

Fit card:
Obsessed with this adorable Y2K baby tee featuring the cutest butterfly print! Score it on my Depop for just $18.00 before someone else snatches it up. Pair it with baggy jeans and chunky sneakers for the ultimate nostalgic fit! ✨🦋

Trace:
[1] parse_query
      in:  small tan purse
      out: description='small tan purse', size=None, max_price=None
[2] search_listings (via MCP)
      in:  description='small tan purse', size=None, max_price=None
      out: 5 items: Y2K Baby Tee — Butterfly Print, Crochet Halter Top — Cream, Suede Chelsea Boots — Tan … +2 more
      →    branch: 5 results, carrying on
[3] select_item
      in:  5 results, taking index 0
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item id is lst_002
[4] suggest_outfit
      in:  item lst_002, wardrobe with 10 items
      out: Pair your butterfly Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for an easy, nost…
[5] create_fit_card
      in:  item lst_002, outfit of 219 chars
      out: Obsessed with this adorable Y2K baby tee featuring the cutest butterfly print! Score it on my Depop for just $…
[6] done
      →    all three tools ran, returning the session
```

This is the one worth looking at twice. Nothing errored. All six steps ran,
`selected_item` travelled through the session intact, and the caption is
perfectly well written. It is also about a butterfly baby tee, and the user
asked for a tan purse. Every criterion except this one would call this run a
success.

---

#### Criterion 2: an impossible query stops before the second tool

Scenario `impossible query stops early`, query `designer ballgown size XXS under $5`.
Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: yes — I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.
- selected_item: (none)
- search_results: 0

Trace:
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty list, stopping before suggest_outfit
```

How I read it: the trace stops at step 2. There is no `suggest_outfit` step at
all, `selected_item` is `(none)`, and the message names three things the user
could change. The scenario reported `0 model calls`, which is the part I trust
most, because `suggest_outfit` cannot have run without calling the model. Same
on all five tries. **5 of 5, target was 5 of 5, MET.**

---

#### Criterion 3: the item found is the item that gets styled

Scenario `selected item is the item styled`, query `90s track jacket in size M`.
Output from `agent.py::run_agent`, captured by `run_eval.py::run_once`.

```
- stopped early: no
- selected_item: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
- search_results: 4

Trace:
[1] parse_query
      in:  90s track jacket in size M
      out: description='90s track jacket in', size='M', max_price=None
[2] search_listings (via MCP)
      in:  description='90s track jacket in', size='M', max_price=None
      out: 4 items: 90s Track Jacket — Navy/White Stripe, 90s Leather Bomber — Black, 90s Silk Slip Dress — Floral, Midi Length … +1 more
      →    branch: 4 results, carrying on
[3] select_item
      in:  4 results, taking index 0
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    selected_item id is lst_004
[4] suggest_outfit
      in:  item lst_004, wardrobe with 10 items
      out: Layer the 90s Track Jacket over your white ribbed tank top and pair it with the baggy straight-leg jeans and c…
[5] create_fit_card
      in:  item lst_004, outfit of 330 chars
      out: Scored this ultimate 90s Track Jacket in navy and white for just $45.00 on Poshmark, and I’m so obsessed! Thro…
[6] done
      →    all three tools ran, returning the session
```

How I read it: my criterion says to compare `session["selected_item"]["id"]`
against the item going into `suggest_outfit`. Step 3 prints
`selected_item id is lst_004` and step 4 prints `item lst_004` as its input.
Those are the two values the criterion names and they are the same string. All
five tries printed `lst_004` in both places. **5 of 5, target was 5 of 5, MET.**

I added those two ids to the trace in Milestone 2 so this criterion could be
read off the output instead of taken on trust. It is worth noting what this
criterion does **not** say: it says the item that was selected is the item that
got styled, and it says nothing about whether the right item was selected in
the first place. Criterion 1 try 4 passes criterion 3 perfectly while styling a
baby tee for someone shopping for a purse.

---

#### Criterion 4: the fit card names the price

Scenario `fit card names the price`, query `silk slip dress in midi length under $40`.
The top result is `lst_013` at `$30.0`, so I am looking for `30` in the caption.
All five captions from `tools.py::create_fit_card`, via `run_eval.py::run_once`:

```
Try 1: Absolute 90s dream find! 🌸✨ I’m obsessed with this floral midi silk slip dress and can't believe I scored it for just $30.00. Grab it now over on my Depop before I change my mind and keep it for myself!
Try 2: Found the ultimate 90s dream! 🌸 This gorgeous floral midi slip dress is giving all the nostalgic vibes and is up for grabs on Depop for just $30. Grab it before it's gone and go live your best vintage life!
Try 3: Found the ultimate 90s silk slip dress and I am obsessed! 🌸✨ Grab this gorgeous floral midi for just $30.00 over on my Depop before it’s gone. Style it over a white tee with chunky sneakers for the weekend, or throw an oversized crewneck and combat boots right over it when it gets chilly!
Try 4: Obsessed with this 90s silk slip dress I just thrifted! Layer it over a white tee with chunky sneakers for daytime, or throw on an oversized crewneck and combat boots when it gets chilly. Grab this floral midi on my Depop right now for just $30! ✨👗
Try 5: Obsessed with this 90s silk slip dress! 🌸 Throw it on over a white tee with chunky sneakers for an easy daytime look, or layer an oversized crewneck and combat boots when it gets chilly. Grab this floral midi on my Depop right now for just $30.00!
```

How I read it: the price is in all five, written as `$30` and `$30.00`. My
criterion says the number from `new_item["price"]` has to appear somewhere in
the caption, and `30` does every time. **5 of 5, target was 4 of 5, MET.**

I set this at 4 of 5 last unit because I expected the model to round or write
around the number sometimes. Across ten captions for this item over two runs it
has not done it once. The five captions are otherwise all different text, so
this is not the cache handing back one answer.

---

#### Criterion 5: the price ceiling is never crossed

Scenario `price ceiling is never crossed`, query `vintage graphic tee under $30`.

`run_eval.py` records how many results came back but not what they cost, and my
criterion is about **every** listing returned, not just the one that got picked.
Its row in the results file shows `search_results: 10` and a selected item at
`$18.0`, which says nothing about the other nine. So I measured it directly,
five times, reading `session["search_results"]` out of `agent.py::run_agent`
with caching off, the same way `run_eval.py` runs it:

```
try 1: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 2: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 3: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 4: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 5: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
```

The command, so it can be run again:

```
python -c "
import config
config.CACHE_ENABLED = False
from agent import run_agent
from utils.data_loader import get_example_wardrobe
CEILING = 30.0
for attempt in range(1, 6):
    s = run_agent('vintage graphic tee under \$30', get_example_wardrobe())
    prices = [x['price'] for x in s['search_results']]
    over = [p for p in prices if p > CEILING]
    print(f'try {attempt}: {len(prices)} results, prices {sorted(prices)}')
    print(f'         max={max(prices)}  over: {over or \"none\"}')
"
```

How I read it: ten results every try, nothing above the ceiling, and the top
price is exactly `$30.0` every time. That last part is the bit I wanted to see.
My Tool Inventory promised `max_price` was **inclusive**, so an item priced at
exactly the ceiling has to come back, and it does. A filter using `<` instead of
`<=` would have dropped it and still looked like a pass on a careless reading.
**5 of 5, target was 5 of 5, MET.**


## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools *(revised this unit)* | 4 of 5 | **MISSED (2/5)** | Five phrasings, five items I confirmed are in the data. One returned nothing and two returned a fit card for the wrong item. Each phrasing ran five times and gave the same answer every time, so this is not variance. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | The trace stops at step 2 on all five tries, there is no `suggest_outfit` step, and the scenario reported `0 model calls`. `suggest_outfit` cannot run without calling the model, so the count is the proof. |
| 3 | The item found is the item that gets styled | 5 of 5 | MET (5/5) | Compared the two ids the criterion names, `selected_item id is lst_004` at step 3 against `item lst_004` going into step 4. Same string on all five tries. |
| 4 | The fit card names the price | 4 of 5 | MET (5/5) | Read all five captions for `lst_013` at `$30.0`. The number is in all five, as `$30` or `$30.00`. The five captions are otherwise different text, so the cache is not involved. |
| 5 | The price ceiling is never crossed | 5 of 5 | MET (5/5) | Printed every returned price, not just the selected one, five times. Ten results each try, nothing above `$30`, top price exactly `$30.0`, which also confirms the ceiling is inclusive as my Tool Inventory promised. |

**Diagnoses**

Criterion 1 is the only miss, and it missed three of five tries. All three land
in the same place, so this is one problem and not three.

**Where it happened: a tool.** `tools.py::search_listings`. Not the loop, not
the session, not the model. The loop branched correctly every time, including
on the try that found nothing, where it stopped at step 2 exactly as criterion
2 says it should. The session carried the selected item through intact, which
criterion 3 confirms. The model wrote a good caption every time it was asked.
The agent did the right thing with what the search handed it. The search handed
it the wrong thing.

Inside that one tool there are two distinct mechanisms.

---

**Mechanism A, the size filter cannot read a waist size. One try: phrasing 1.**

`levis jeans size 30` returned an empty list. `parse_query` read `size='30'`
correctly, so the parse is fine. The listing it should have found is `lst_001`,
whose size field is the string `W30 L30`.

My size rule, which I wrote last unit and put in my Tool Inventory, splits the
listing's size on spaces and slashes and keeps the listing only if the
requested size equals one of the whole tokens. For `W30 L30` those tokens are
`['w30', 'l30']`. The string `'30'` is not equal to either, so the listing is
dropped before scoring ever happens.

I confirmed it is the size filter and not the keywords by taking the query
apart:

```
search("levis jeans", size="30") -> 0 results
search("levis jeans")            -> 3 results    (lst_001 is one of them)
search("jeans", size="30")       -> 0 results
search("jeans")                  -> 3 results
```

The keywords find the jeans. The size filter then throws them away. And it
throws away **every** pair of jeans in the data, because the bottoms are sized
`W27`, `W28`, `W29`, `W30`, `W30 L30`, `W32`, and a shopper asking for jeans
types `size 30`, not `size W30`.

The painful part is that this rule is not a careless bug. It is the fix I wrote
for the substring trap the starter warned about, where `"s" in "us 9"` is True
and `"l" in "xl"` is True. Whole token matching solves that properly for tops
and shoes. It just has no idea that `W30` means a waist of 30, and I never
tested a bottoms query with a size in it, because my unit 3 sample run was a
tee.

---

**Mechanism B, the score is an unweighted count, so ties are common and get
broken by whatever order the data is in. Two tries: phrasings 3 and 4.**

Both of these returned a fit card and neither of them errored. The right item
was in the results list both times. It just was not first, and
`agent.py::run_agent` takes `search_results[0]`.

`search_listings` scores a listing by counting how many of the query keywords
appear anywhere in its title, description, and style tags. One keyword, one
point. Nothing is weighted, so a match on a decorative word counts exactly as
much as a match on the noun naming the thing.

```
QUERY: 'a green silk shirt'
  picked  lst_024 score=2 matched=['green', 'shirt']  Vintage Polo Shirt — Forest Green
  wanted  lst_029 score=2 matched=['green', 'silk']   Silk Button-Down — Sage Green

QUERY: 'small tan purse'
  picked  lst_002 score=1 matched=['small']           Y2K Baby Tee — Butterfly Print
  wanted  lst_039 score=1 matched=['tan']             Mini Shoulder Bag — Tan Leather
```

Both are exact ties. `matches.sort(key=lambda pair: pair[0], reverse=True)` is
a stable sort, so a tie leaves the two in the order they came out of
`listings.json`, and `lst_024` and `lst_002` are simply earlier in the file.
The agent is not choosing badly. It is not choosing at all.

Phrasing 4 is the one that bothers me most. `lst_002` scored its single point
on the word `small`, which appears in the description as "tag says medium but
fits like a small". The shopper meant small as a size, the data meant small as
a comparison, and a plain substring count cannot tell those apart. Meanwhile
`purse` scored nothing anywhere, because the data says `Mini Shoulder Bag` and
never once says `purse`. That is exactly the phrasing gap I wrote about under
criterion 1 last unit, showing up in the one place I had not thought to look:
not as a zero result, but as a confident answer to a different question.

---

**The pattern, and what it says about the other four criteria.**

Four criteria MET and one MISSED is a flattering split, and the honest reading
is less flattering than it looks.

Criteria 2, 3 and 5 are all deterministic and all passed 5 of 5 across two full
runs. They are worth having, because they are what tells me the MCP move did
not change the shape of anything, and criterion 5 caught the inclusive boundary
I could easily have got wrong. But none of them could have been failed by the
problem criterion 1 just found. Criterion 3 in particular passes *perfectly*
on the try that styled a baby tee for someone shopping for a purse, because it
only asks whether the selected item is the styled item, never whether the
selected item was the right one.

So my five criteria had a hole in them, and it was not a small one: **nothing I
wrote checked whether search returned the right item.** Four of the five
measure that the machinery holds together, and the machinery does hold
together. Only criterion 1 looks at whether the answer is any good, and in its
original wording it did not do that either, which is why I revised it.

**Were my targets too low?** Two of them, yes, on the evidence I now have.
Criterion 4 is set at 4 of 5 and has gone 10 of 10 across two runs, so the
allowance I made for the model rounding the price has not been needed once.
Criterion 3 is set at 5 of 5 and passes trivially, because the value it checks
is moved by a single assignment with nothing in between that could change it.

**The one I would tighten** is criterion 3. As written it compares an id to
itself a few lines later. The version worth having would say that the id in
`session["selected_item"]` is the id of the highest scoring listing for the
query, which would have caught phrasings 3 and 4 and is a claim that can
actually fail. I have not changed it, because tightening a criterion I passed
is not one of the two moves this unit allows, and I would rather say plainly
here which criterion is weak than quietly rewrite it.

---

**What this points at for Milestone 5.** Mechanism A and mechanism B are both
in `search_listings`, and I am allowed one change. They are not equally
valuable:

- Fixing **A** turns phrasing 1 from FAIL to PASS, taking criterion 1 to 3 of 5.
  Still MISSED, but it removes the worst outcome for a user, which is being told
  nothing exists when it does.
- Fixing **B** could turn phrasings 3 and 4 from FAIL to PASS, taking criterion
  1 to 4 of 5 and MET.

B moves the number further. A fixes the more serious failure. I am picking one
in the next section and saying why.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

Produced with `python app.py ask '...' --trace`. The `trace.step()` calls live
in `agent.py::run_agent`, one per stage of the loop.

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace

[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: 10 results, carrying on
[3] select_item
      in:  10 results, taking index 0
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item id is lst_002
[4] suggest_outfit
      in:  item lst_002, wardrobe with 10 items
      out: Pair your new Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for a cute, casual thro…
[5] create_fit_card
      in:  item lst_002, outfit of 187 chars
      out: Obsessed with this Y2K butterfly tee I just scored! It’s yours on Depop for just $18.00. Pair it with baggy je…
[6] done
      →    all three tools ran, returning the session

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair your new Y2K baby tee with the baggy straight-leg jeans and chunky white sneakers for a cute, casual throwback look. Throw on the black cropped zip hoodie if you need an extra layer!

  Fit card: Obsessed with this Y2K butterfly tee I just scored! It’s yours on Depop for just $18.00. Pair it with baggy jeans and chunky sneakers for the ultimate throwback fit! ✨🦋

0 model calls this session, 2 served from cache
```

Step 2 is the MCP call. It is the only step that leaves my program: it starts
`mcp_server.py`, asks it for `search_listings`, and shuts it down again. Steps 4
and 5 are still direct calls into `tools.py`.

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5'


  I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.

0 model calls this session
```

Two steps instead of six, and the last line says `0 model calls this session`.
That is the branch doing its job: it reads the empty list at step 2 and returns
before `suggest_outfit` is ever reached, so neither model call happens.

### The three failure modes, triggered on purpose

**1. Empty search.** Already handled before this unit, because it is the branch
criterion 2 is about. Triggered with a query the data cannot match:

```
$ python app.py ask 'designer ballgown size XXS under $5'

  I couldn't find anything for "designer ballgown size XXS under $5". Try removing the price limit, using a different size, or simpler keywords.
```

No handler needed. The message names three things the user can actually change,
and the trace above shows the loop stopping at step 2.

**2. Empty wardrobe.** Triggered with the `--empty-wardrobe` flag, which hands
`suggest_outfit` a wardrobe with no items in it:

```
$ python app.py ask 'platform sneakers size 8' --empty-wardrobe

(running with an empty wardrobe)

  Found:    Platform Sneakers — White Chunky Sole — $48.0 on poshmark

  Outfit:   Hey there! Those chunky platform sneakers are such a fun Y2K find. You can easily style them with a simple graphic tee and some cargo pants for a cool streetwear vibe. Or, try pairing them with a denim skirt and a cropped hoodie for the ultimate 90s throwback!

  Fit card: Score! I just found these chunky platform sneakers on Poshmark for only $48, and I am obsessed. They are giving me all the best 90s vibes and I can't wait to style them!

0 model calls this session, 2 served from cache
```

No handler needed either. `suggest_outfit` already checks `wardrobe["items"]`
and switches to a general advice prompt when the list is empty, which is the
empty case I committed to in my Tool Inventory last unit. It returns a real
non empty string and names no pieces the user does not own. With `--trace` the
step reads `wardrobe with 0 items` and notes `empty wardrobe, so general advice`,
so I can see which prompt it took rather than guessing.

**3. Model unavailable.** This is the one that was genuinely broken.

I triggered it by running one command with a deliberately wrong key in front of
it, which beats editing `.env` because there is no way to forget to put the real
key back:

```
GEMINI_API_KEY="AIzaSyBadKeyForTestingOnly_NotARealKey00" python app.py ask 'denim jacket under $50'
```

The query has to be one I have not asked before. An old query comes back out of
the build cache without the model being called at all, and the last line says
`served from cache`, which looks like a pass and proves nothing.

*Before the handler*, calling `run_agent` directly gave a raw stack trace:

```
  File "agent.py", line 201, in run_agent
    session["outfit_suggestion"] = suggest_outfit(
  File "tools.py", line 191, in suggest_outfit
    return generate(prompt, system=system)
  File "generate.py", line 332, in generate
    raise ModelUnavailable(_explain(exc)) from exc
generate.ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

*After the handler*:

```
$ GEMINI_API_KEY="<a wrong key>" python app.py ask 'denim jacket under $50' --trace

[1] parse_query
      in:  denim jacket under $50
      out: description='denim jacket', size=None, max_price=50.0
[2] search_listings (via MCP)
      in:  description='denim jacket', size=None, max_price=50.0
      out: 7 items: Denim Jacket — Light Wash, Cropped, Vintage Levi's 501 Jeans — Medium Wash, 90s Track Jacket — Navy/White Stripe … +4 more
      →    branch: 7 results, carrying on
[3] select_item
      in:  7 results, taking index 0
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      →    selected_item id is lst_007
[4] suggest_outfit
      in:  item lst_007, wardrobe with 10 items
      out: ModelUnavailable
      →    handler: stopping, search results are still good

  I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.

1 model calls this session
```

**What the handler is, and why it reads like that.** I wrapped both model
calling stages in `agent.py::run_agent` in `try` / `except ModelUnavailable`,
and each one puts a message in `session["error"]` and returns the session,
rather than letting the exception escape.

The thing I changed my mind about while writing it was how much to say. My first
message was just "the model could not be reached", and reading it back there was
nothing a user could do with it. So each message now carries the work that did
succeed. The search found a real jacket at a real price before the model died,
and throwing that away makes the failure look total when it is partial. The
fit card handler goes further and prints the whole outfit inside the error,
because by that point two of the three tools have worked and the user should
still get to keep the outfit.

The fit card handler is harder to trigger from the command line, because if the
key is wrong then `suggest_outfit` dies first and the loop never reaches step 5.
I checked it separately by swapping in a `create_fit_card` that raises, which
gave `error set? True`, `outfit kept? True`, `fit_card: None`, and a step 5 in
the trace reading `handler: stopping, outfit is still good`.

**One note on `trace.py`.** My `trace.step()` calls sit inside `run_agent`, so
they run on every query, and a plain `python app.py ask '...'` was printing all
six steps on top of the answer. `app.py` only calls `start_trace()` when you
pass `--trace`, so I added a `_enabled` flag in `trace.py` that `start_trace()`
switches on, and `step()` returns early when it is off. The formatting is
untouched.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I moved `search_listings` onto MCP. It was the easy one to pick because it is
the only tool that doesn't call the model, so nothing is slow and the same query
gives the same answer every time while I was figuring out the shape.

**What changed in my code, in two places.**

1. `mcp_server.py`: I uncommented the `@mcp.tool()` block and registered
   `search_listings` with the same three inputs as my Tool Inventory
   (`description: str`, `size: str | None`, `max_price: float | None`). The body
   just calls `_search_listings_impl`, which is the real function in `tools.py`
   under an alias. The part that took the longest was the description, because
   it has to make sense to someone who can't see my code. I spelled out that
   `max_price` is in whole dollars and inclusive, that `size` is matched as a
   whole token so "M" matches "S/M" but not "XL", and that nothing matching gives
   back `[]` and not `null`.

2. `agent.py`: in `run_agent()`, the search stage used to be a direct call:

   ```python
   results = search_listings(parsed["description"], size=..., max_price=...)
   ```

   and it is now:

   ```python
   results = call_tool("search_listings", {
       "description": parsed["description"],
       "size": parsed["size"],
       "max_price": parsed["max_price"],
   })
   ```

   I also dropped `search_listings` out of the `from tools import ...` line, so
   the agent genuinely cannot reach it directly any more. `suggest_outfit` and
   `create_fit_card` stayed as direct calls.

**Did anything behave differently? No, and I checked instead of assuming.**

```
$ python mcp_client.py
Asking mcp_server.py what it offers...

  search_listings
    Search a fixed catalogue of 40 secondhand clothing listings and return the
    ones that match, best match first.
    [...full description...]
    - description: string
    - size: string  (optional)
    - max_price: number  (optional)
```

Then I ran the same arguments both ways and compared the lists:

```
$ python -c "from tools import search_listings; from mcp_client import call_tool; args={'description':'looking for a vintage graphic tee','size':None,'max_price':30.0}; d=search_listings(args['description'],args['size'],args['max_price']); m=call_tool('search_listings',args); print('direct:',len(d),'items   mcp:',len(m),'items'); print('same?', d==m)"
direct: 10 items   mcp: 10 items
same? True
```

`d == m` is True, so the dicts came back identical field for field, not just the
same length. I checked the empty case separately too, because that is what my
branch in criterion 2 reads:

```
$ python -c "from mcp_client import call_tool; print(call_tool('search_listings', {'description':'designer ballgown','size':'XXS','max_price':5.0}))"
[]
```

That mattered more than it looks. MCP sends results back as text containing
JSON, so I half expected the empty list to arrive as `None` or as the string
`"[]"`, which would have made `if not results:` behave by accident rather than
on purpose. It comes back as a real empty list, so the branch still works for the
right reason.

The one thing that *is* different is speed. `mcp_client.call_tool` starts the
server, asks, and shuts it down again on every single call, so a run that used to
be instant now has a visible pause at the search step.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** one filter, in one tool, in `tools.py::search_listings`.
A size written as a plain number is now also allowed to match a waist token.

```python
# before
if size is not None:
    size_tokens = listing["size"].lower().replace("/", " ").split()
    if size.strip().lower() not in size_tokens:
        continue

# after
if size is not None:
    size_tokens = listing["size"].lower().replace("/", " ").split()
    wanted = size.strip().lower()
    matches_size = wanted in size_tokens

    if not matches_size and wanted.isdigit():
        matches_size = ("w" + wanted) in size_tokens

    if not matches_size:
        continue
```

That is the whole change. Four lines. Nothing else in the repo moved:
`agent.py`, `mcp_server.py`, `trace.py`, the prompts, the scenarios and the
criteria are all byte for byte what they were for the before run.

Two things I decided on purpose while writing it.

I match the `w` token only, never `l`. A listing sized `W28 L30` is a 28 waist
with a 30 inseam, so letting a `30` match the `L` token would hand someone
trousers that do not fit and would look like the search working.

I kept the whole token rule as the first test rather than replacing it. It is
the right rule, and it is the thing standing between me and the substring trap
the starter warned about. The number rule only runs when the whole token test
has already failed and the request is all digits, so it can only ever add
listings that the old rule rejected. It cannot loosen anything else.

**Which failure it was meant to fix:** mechanism A from my diagnosis, the one
that cost me try 1 of criterion 1. `levis jeans size 30` returned an empty list
because `lst_001` is sized `W30 L30`, which tokenises to `['w30', 'l30']`, and
`'30'` is equal to neither. Every pair of bottoms in the data is sized that
way, so the filter was discarding all of them for any numeric size.

**Which failure it was not meant to fix:** mechanism B, the scoring ties that
cost me tries 3 and 4. I am allowed one change and I picked the one that
produces the worse experience. Being told nothing exists when it does is a
dead end for a user. Being handed the wrong item at least gives them something
to react to. Mechanism B is untouched and I expect tries 3 and 4 to fail again,
which is the point of saying so before the run rather than after.

### Run Log — Before

Repeated here so the two are side by side. Full file:
`results/run_2026-10-11_1825_before.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | **MISSED (2/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Run Log — After

`python run_eval.py --label after`, same ten scenarios, five tries each,
caching off. Full file: `results/run_2026-10-11_2000_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools *(revised)* | 4 of 5 | **PASS** | PASS | FAIL | FAIL | PASS | **MISSED (3/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item found is the item that gets styled | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card names the price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never crossed | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 1 try by try, before against after:

| Try | Query | Before | After | Selected after the change |
|---|---|---|---|---|
| 1 | `levis jeans size 30` | FAIL, nothing found | **PASS** | lst_001 Vintage Levi's 501 Jeans, $38.0 |
| 2 | `black bomber jacket` | PASS | PASS | lst_022 90s Leather Bomber |
| 3 | `a green silk shirt` | FAIL, wrong item | FAIL, wrong item | lst_024 Vintage Polo Shirt, still not lst_029 |
| 4 | `small tan purse` | FAIL, wrong item | FAIL, wrong item | lst_002 Y2K Baby Tee, still not lst_039 |
| 5 | `chunky knit cardigan` | PASS | PASS | lst_008 Knit Cardigan |

**Did it help, and how do I know:**

Yes, and only as much as I said it would. Criterion 1 went from 2 of 5 to 3 of
5. It is still MISSED, because the target is 4 of 5 and the target does not
move.

The try it was aimed at is the try that changed. Here is try 1 after the
change, from `agent.py::run_agent` via `run_eval.py::run_once`:

```
- stopped early: no
- selected_item: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
- search_results: 1

Fit card:
Scored these dreamy medium wash Vintage Levi's 501 Jeans and I'm obsessed! Grab this absolute steal for just $38.0 over on my depop before someone else snatches them up. Go build your dream fit and tag me in your pics!

Trace:
[1] parse_query
      in:  levis jeans size 30
      out: description='levis jeans', size='30', max_price=None
[2] search_listings (via MCP)
      in:  description='levis jeans', size='30', max_price=None
      out: 1 items: Vintage Levi's 501 Jeans — Medium Wash
      →    branch: 1 results, carrying on
[3] select_item
      in:  1 results, taking index 0
      out: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
      →    selected_item id is lst_001
[4] suggest_outfit
      in:  item lst_001, wardrobe with 10 items
      out: Hey friend! Those medium wash Vintage Levi's 501 Jeans are an incredible find.   Try pairing your new jeans wi…
[5] create_fit_card
      in:  item lst_001, outfit of 353 chars
      out: Scored these dreamy medium wash Vintage Levi's 501 Jeans and I'm obsessed! Grab this absolute steal for just $…
[6] done
      →    all three tools ran, returning the session
```

Two steps became six. The same query that returned an empty list five times in
a row now finds `lst_001`, which is the exact listing my revised criterion
named, and takes it all the way through to a fit card. All five tries did it.

Tries 3 and 4 failed again, with the same two wrong items as before, which is
what I predicted above and is the correct outcome. Mechanism B is a scoring
tie, this change touched the size filter, and a change that had somehow fixed
tries 3 and 4 as well would mean I had not understood either problem.

**What I checked that could have gone wrong.** A size filter that lets more
through can let the wrong things through, and the rule I loosened is the one
guarding the substring trap. So I tested the edges directly against
`tools.py::search_listings` before running the eval:

```
  size='s'   on 'jeans'    ->  0 results, sizes []
  size='l'   on 'hoodie'   ->  1 results, sizes ['L']
  size='32'  on 'jeans'    ->  1 results, sizes ['W32']
  size='28'  on 'jeans'    ->  1 results, sizes ['W28']
  size='8'   on 'sneakers' ->  1 results, sizes ['US 8']
  size='m'   on 'tee'      ->  2 results, sizes ['S/M']
```

A small still does not match `US 9` or any waist. An `L` still does not match
`XL`. A 32 returns `W32` and not `W30`, so the number rule is matching the
whole waist token and not a prefix. Shoes and tops behave exactly as they did
before.

The other four criteria were all 5 of 5 before and are all 5 of 5 after, which
is the result I wanted from them. Criterion 5 in particular I measured again the
same way, printing every returned price rather than just the selected one:

```
try 1: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 2: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 3: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 4: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
try 5: 10 results, prices [12.0, 15.0, 18.0, 19.0, 20.0, 22.0, 24.0, 26.0, 27.0, 30.0]
         max=30.0  over: none
```

Identical to before, which is what a change confined to the size filter should
do to a query that has no size in it.

**One honest limit on this result.** Three of five is a better number than two
of five, but the fix is narrower than the diagnosis. I taught the filter one
convention, `W` for waist, because that is the only one in these 40 listings.
A real catalogue would also have `30x32`, `UK 10`, `EU 38` and sizes written as
words, and none of those would work. What I fixed is this data's spelling of a
waist size, not the general problem of reading a size written a different way
from the one the seller typed.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

### Criterion 1, still MISSED at 3 of 5

Tries 3 and 4 still fail, for the reason my diagnosis named and my improvement
deliberately did not touch: `search_listings` scores a listing by counting how
many query keywords appear in it, one point each, nothing weighted. Ties are
common and the sort is stable, so a tie is settled by whichever listing happens
to sit earlier in `listings.json`.

```
'a green silk shirt'  picked lst_024 score=2 ['green','shirt']  / wanted lst_029 score=2 ['green','silk']
'small tan purse'     picked lst_002 score=1 ['small']          / wanted lst_039 score=1 ['tan']
```

**What I would do, and what I found out about it.** The obvious fix is to stop
treating every word as equally informative and score rarer words higher, so
`silk` outranks `green`. Before writing it in here as the answer I measured it
against the data, counting how many of the 40 listings contain each word and
scoring a match as `1 / that count`:

```
   'green'     3 listings
   'silk'      2 listings
   'shirt'     4 listings
   'small'     1 listings
   'tan'       4 listings
   'purse'     0 listings

  a green silk shirt
     lst_024 rarity score 0.583  from ['green(1/3)', 'shirt(1/4)']
     lst_029 rarity score 0.833  from ['green(1/3)', 'silk(1/2)']   <- now wins, correct
  small tan purse
     lst_002 rarity score 1.000  from ['small(1/1)']                <- still wins, still wrong
     lst_039 rarity score 0.250  from ['tan(1/4)']
```

It fixes try 3 and it makes try 4 **worse**. The word `small` appears in
exactly one listing in the whole catalogue, which makes it the rarest word in
that query and hands the baby tee an even bigger lead. Rarity is a good proxy
for "informative" right up until the rare word is rare by accident. Here it is
rare because one seller happened to write "tag says medium but fits like a
small" in a description.

So I am not shipping it. It would have moved criterion 1 from 3 of 5 to 4 of 5
and turned the row MET, and it would have done that while making one of the two
broken cases worse. That is a number improving for a reason I do not endorse,
and it is the kind of thing this unit is about not doing.

**What try 4 actually needs is not a scoring change at all.** The word `purse`
appears in **zero** of the 40 listings. The item exists, it is `lst_039 Mini
Shoulder Bag, Tan Leather`, and the data simply never uses the shopper's word
for it. No amount of reweighting a keyword count will find a bag by searching
for `purse`, because there is nothing to match. That needs either a synonym
layer, or the model doing the query understanding instead of a substring count,
and either one is a new tool rather than a tweak to this one.

**Why I stopped here.** The unit allows one change and I spent it on mechanism
A, which I still think was right: being told nothing exists when it does is a
dead end for a user, and being handed the wrong item at least gives them
something to push back on. The second reason is the paragraph above. I found
out the easy fix was wrong by testing it, which is better than finding out
after submitting, but it means the real fix is a bigger piece of work than I
have left.

### Things that are not failing yet but will

**The brand word does not match when it has an apostrophe.** `levis` appears in
0 listings. `levi's` appears in 2. A shopper typing the brand the natural way,
without the apostrophe, gets nothing from that word. Try 1 passes anyway
because `jeans` carries it, so this never shows up as a failure in my run log.
It would the moment someone searches for a brand by name alone. Stripping
punctuation from the haystack the same way I already strip it from the query
would fix it, and I did not do it because it was not what my diagnosis named.

**My size fix only knows one convention.** I taught the filter that a plain
number can match a `W` token, because `W30` is how these 40 listings write a
waist. A real catalogue would also have `30x32`, `UK 10`, `EU 38` and sizes
spelled out as words, and none of those work. What I fixed is this data's
spelling of a waist size, not the general problem.

### A criterion I would change, and did not

Criterion 3 is too loose, and I said so in my diagnosis rather than quietly
rewriting it. As written it compares `session["selected_item"]["id"]` against
the id going into `suggest_outfit`, which are the same value set by one
assignment a few lines apart. It passes 5 of 5 and it passed 5 of 5 on the run
where the agent styled a butterfly baby tee for someone shopping for a tan
purse, because it never asks whether the selected item was the right one.

The version worth having would say the selected id is the id of the best
matching listing for the query, which is a claim that can fail and which would
have caught tries 3 and 4 on its own. I have not made that change, because
tightening a criterion I passed is not one of the two moves allowed this unit,
and doing it quietly after seeing the results is worse than leaving it and
saying what is wrong with it.

The honest summary of my five criteria as a set: four of them check that the
machinery holds together, and it does. Only criterion 1 checks whether the
answer is any good, and that is the one still missing its target.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [x] mcp_server.py exists with one tool registered
           (search_listings, with its description and typed inputs)
       [x] Run Log — Before, five criteria, five tries each
           (results/run_2026-10-11_1825_before.md)
       [x] Real output pasted underneath, naming file and function
       [x] A verdict on every criterion
       [x] A diagnosis for every miss, naming a place AND a mechanism
           (tools.py::search_listings; mechanism A the size filter,
            mechanism B the unweighted score and its tie order)
       [x] Loop Trace, with the MCP call visible in it
           (step 2, "search_listings (via MCP)")
       [x] All three failure modes triggered and handled
           (empty search, empty wardrobe, model unavailable)
       [x] One improvement, with Run Log — After in the same format
           (results/run_2026-10-11_2000_after.md)
       [x] What's Still Broken
       [x] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

## Capstone

**What This Extends**

I'm extending FitFindr, my project from units 3 and 4. It's the thrift
shopping agent where you type something like 'vintage graphic tee under $30',
it searches the 40 listings, picks one, suggests an outfit from your wardrobe
and writes a fit card. I picked this one because it's the system I know the
weak spots of best (the keyword score ties and the size filter from unit 4),
and because it already has a `serve.py` that runs the agent over HTTP but
doesn't record anything about what happened.

What's new this unit: every request to `serve.py` now leaves a record behind
in a log file, so I can go back and see what came in, what went out, how long
it took and what it cost.

**The Shape**

Shape A, deploy and instrument. Right now if FitFindr is running as a server
and something goes wrong, the only evidence is whatever got printed in the
terminal, and that's gone as soon as I close it. I'm adding structured logging
to `serve.py` so every call to `/ask` writes one JSON line to
`logs/requests.jsonl` with the time, the query, what came back (the item it
picked, or the error), how long it took in milliseconds, and how many model
calls and tokens it used. Requests that fail (an empty query, a search with no
matches, the model not being reachable) get a line too, not just the ones that
work. I'm taking Path B, running it locally with logs, because the free host
asks for a card and the brief says Path B is worth the same.

What's out of scope:

1. I'm not fixing the search scoring. Criterion 1 from unit 4 is still broken
   (ties go to whichever listing comes first in the file), and it stays in
   What's Still Broken where I already wrote it up.
2. I'm not changing any of the three tools or their prompts. If the log shows
   a bad answer I'll write it down, not go fix the tool.
3. I'm not hosting it anywhere (no Path A), and I'm not turning the one
   request at a time lock in `serve.py` into a real queue.

**Running It**

Path B, local with logs. Everything is in [RUNNING.md](RUNNING.md) under
"Capstone: how I run it". The short version is one command:

```bash
python serve.py
```

and then you send it requests on `http://localhost:5000/ask`. Every request
gets one line in `logs/requests.jsonl`, and `python request_log.py` reads them
back.

How I checked the instructions: I cloned the repo into a brand new folder,
made a new venv, installed `requirements.txt` with pip, copied `.env.example`
to `.env`, put my key in plus `AI201_CACHE=0`, and followed RUNNING.md from
the top. `python test.py` said 10 passed, the server started, and both the
curl command and the PowerShell `Invoke-RestMethod` command got an answer
back. Nothing was missing, which honestly surprised me a bit.

One thing I did differently for the real session below: my own `.env` didn't
have the `AI201_CACHE=0` line in it, so I started the server with
`AI201_CACHE=0` set in the terminal instead. Same effect, and every line in
the log says `"cache_enabled": false` so you can see it was off.

**Instrumentation**

Every call to `/ask` writes one JSON object on one line to
`logs/requests.jsonl`. The code that writes it is `request_log.py::log_request`
and it gets called from `serve.py::ask`. A line gets written for every
outcome, including the ones that fail, before the response goes back.

What each record holds:

1. `timestamp`, in UTC, and a `request_id` (8 characters). The same id comes
   back to the caller in an `X-Request-Id` header, so you can find the line
   for a request you sent.
2. `query`, what came in. For a bad request this is `null` and `raw_body`
   holds the first 200 characters of what was actually sent instead.
3. What went out: `outcome` (`ok`, `stopped`, `bad_request` or `crash`),
   `status_code`, `selected_item_id`, `selected_price`, `fit_card` and
   `error`.
4. How long it took: `duration_ms` for the whole request, and `agent_ms` for
   just the `run_agent` part.
5. What it cost: `model_calls`, `prompt_tokens` and `output_tokens`, for this
   request only.
6. Things specific to FitFindr that I wanted to be able to look up later:
   `parsed` (what `parse_query` pulled out of the query), `num_results` (how
   many listings the search found), `used_example_wardrobe`,
   `waited_for_lock` and `cache_enabled`.

`outcome` is there because the agent answers 200 even when it stopped early
(no matches, or the model couldn't be reached). Without it those would look
like normal successes in the log.

This is the whole log from my real session on November 15, 2026, all 17 requests.
The first 10 are the ones I measured cost from. After those: a search with no
match, four bad requests (empty object, empty query, a list instead of an
object, a number as the query), one with a wardrobe that was a string, and
then the last one is a real model failure, where I restarted the server with
a wrong API key on purpose.

Summary from `python request_log.py 0`:

```
17 requests in logs\requests.jsonl
  outcomes: ok 11, stopped 2, bad_request 4
  ok requests: 11
    avg duration 7626 ms, slowest 21439 ms
    avg model calls 2.0
    avg tokens 355 prompt + 132 output
```

The raw lines from `logs/requests.jsonl`:

```
{"timestamp": "2026-11-15T23:19:03+00:00", "request_id": "709cbc31", "route": "/ask", "query": "vintage graphic tee under $30", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 360, "output_tokens": 147, "agent_ms": 5733, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "num_results": 10, "selected_item_id": "lst_002", "selected_price": 18.0, "fit_card": "Look at this absolute dream of a Y2K baby tee with the cutest butterfly print I just scored! It’s only $18.00 over on my Depop shop, so you definitely need to grab it before it's gone. Head over to my profile to snag it and start styling it with all your fave baggy jeans! ✨🦋", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 5734}
{"timestamp": "2026-11-15T23:19:06+00:00", "request_id": "4bcf006c", "route": "/ask", "query": "90s track jacket in size M", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 357, "output_tokens": 123, "agent_ms": 3358, "parsed": {"description": "90s track jacket in", "size": "M", "max_price": null}, "num_results": 4, "selected_item_id": "lst_004", "selected_price": 45.0, "fit_card": "Scored this ultra-cool 90s Track Jacket on Poshmark for just $45! Layer it over a white ribbed tank with baggy jeans and chunky sneakers for the ultimate effortless sporty look. Such a fun piece to style for everyday streetwear! ✨👟", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 3359}
{"timestamp": "2026-11-15T23:19:09+00:00", "request_id": "3f007384", "route": "/ask", "query": "silk slip dress in midi length under $40", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 354, "output_tokens": 137, "agent_ms": 2856, "parsed": {"description": "silk slip dress in midi length", "size": null, "max_price": 40.0}, "num_results": 7, "selected_item_id": "lst_013", "selected_price": 30.0, "fit_card": "Obsessed with this 90s floral silk slip dress I just scored for only $30! I'm already planning to layer it over a white tee with chunky sneakers, or throw on an oversized crewneck and combat boots for that effortless vintage grunge vibe. Head over to my Depop to grab this gorgeous midi before I change my mind and keep it for myself! 🌸✨", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 2857}
{"timestamp": "2026-11-15T23:19:15+00:00", "request_id": "766655f9", "route": "/ask", "query": "platform sneakers size 8", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 356, "output_tokens": 135, "agent_ms": 5718, "parsed": {"description": "platform sneakers", "size": "8", "max_price": null}, "num_results": 1, "selected_item_id": "lst_019", "selected_price": 48.0, "fit_card": "Look at these white chunky sole platform sneakers I just scored! They were a steal at only $48.0 on Poshmark, and I am already obsessed with them. I can't wait to style them with baggy jeans and a vintage jacket for the ultimate off-duty look!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 5719}
{"timestamp": "2026-11-15T23:19:26+00:00", "request_id": "3f3511de", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 337, "output_tokens": 131, "agent_ms": 10835, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": "Scored this dreamy light wash, cropped Denim Jacket for just $42.0 on Poshmark! Throw it over a ribbed tank and wide-leg trousers for the ultimate off-duty look, or layer it with a black hoodie and combat boots for instant streetwear edge. Run, don't walk, because this piece is too good to miss!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 10836}
{"timestamp": "2026-11-15T23:19:42+00:00", "request_id": "d2882c0a", "route": "/ask", "query": "black leather jacket under $80", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 360, "output_tokens": 129, "agent_ms": 15596, "parsed": {"description": "black leather jacket", "size": null, "max_price": 80.0}, "num_results": 10, "selected_item_id": "lst_022", "selected_price": 75.0, "fit_card": "Obsessed is an understatement! Just scored this ultimate 90s Leather Bomber for only $75.0 on Depop, and I am already planning every outfit. Grab it from my shop before I change my mind and keep it for myself!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 15597}
{"timestamp": "2026-11-15T23:20:03+00:00", "request_id": "3e876afe", "route": "/ask", "query": "baggy jeans size 32", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 370, "output_tokens": 134, "agent_ms": 21438, "parsed": {"description": "baggy jeans", "size": "32", "max_price": null}, "num_results": 1, "selected_item_id": "lst_031", "selected_price": 36.0, "fit_card": "Obsessed with these dark wash baggy carpenter jeans I just scored! Snag them on my Depop for just $36.00 to instantly level up your 90s streetwear game. Trust me, your rotation needs these!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 21439}
{"timestamp": "2026-11-15T23:20:08+00:00", "request_id": "2f7dcb4f", "route": "/ask", "query": "cozy oversized hoodie", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 359, "output_tokens": 131, "agent_ms": 4549, "parsed": {"description": "cozy oversized hoodie", "size": null, "max_price": null}, "num_results": 6, "selected_item_id": "lst_008", "selected_price": 35.0, "fit_card": "Found my ultimate fall staple with this gorgeous chunky brown knit cardigan! Grab it over on my Depop for just $35.00 before I change my mind and keep it. It's giving major cozy vibes and is ready for all your best transitional layering!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 4549}
{"timestamp": "2026-11-15T23:20:16+00:00", "request_id": "16657509", "route": "/ask", "query": "chunky knit sweater under $45", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 358, "output_tokens": 141, "agent_ms": 7626, "parsed": {"description": "chunky knit sweater", "size": null, "max_price": 45.0}, "num_results": 2, "selected_item_id": "lst_008", "selected_price": 35.0, "fit_card": "Obsessed with this cozy chunky brown knit cardigan I just manifested for $35! Throw it over a ribbed tank and baggy jeans for the ultimate earthy vibe, or style it with khaki trousers for pure cottagecore magic. Snag this beauty now over on my Depop before I change my mind and keep it! ✨🤎", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 7626}
{"timestamp": "2026-11-15T23:20:19+00:00", "request_id": "f2567b23", "route": "/ask", "query": "brown leather belt", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 316, "output_tokens": 96, "agent_ms": 3651, "parsed": {"description": "brown leather belt", "size": null, "max_price": null}, "num_results": 7, "selected_item_id": "lst_014", "selected_price": 12.0, "fit_card": "Scored this gorgeous brown, braided leather belt on thredUp for just $12.0! I'm already planning to wear it with wide-leg khaki trousers, a white ribbed tank, and chunky sneakers for the ultimate earthy, casual fit. Thrift magic is real!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 3652}
{"timestamp": "2026-11-15T23:20:20+00:00", "request_id": "47ba1883", "route": "/ask", "query": "designer ballgown size XXS under $5", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 1039, "parsed": {"description": "designer ballgown", "size": "XXS", "max_price": 5.0}, "num_results": 0, "selected_item_id": null, "selected_price": null, "fit_card": null, "error": "I couldn't find anything for \"designer ballgown size XXS under $5\". Try removing the price limit, using a different size, or simpler keywords.", "status_code": 200, "outcome": "stopped", "duration_ms": 1040}
{"timestamp": "2026-11-15T23:20:20+00:00", "request_id": "8ac74683", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:20:21+00:00", "request_id": "80a07960", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{\"query\": \"\"}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:20:21+00:00", "request_id": "76c5cc31", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "[\"vintage\", \"tee\"]", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:20:21+00:00", "request_id": "77858638", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{\"query\": 42}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:20:23+00:00", "request_id": "77f42c13", "route": "/ask", "query": "red beanie", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 373, "output_tokens": 143, "agent_ms": 2515, "parsed": {"description": "red beanie", "size": null, "max_price": null}, "num_results": 9, "selected_item_id": "lst_003", "selected_price": 22.0, "fit_card": "Scored this amazing oversized flannel shirt on thredUp for just $22.0! It’s giving total 90s grunge vibes, and I can't wait to layer it over a white tank with chunky combat boots. Thrift gods definitely blessed me with this one!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 2516}
{"timestamp": "2026-11-15T23:20:48+00:00", "request_id": "d20e3e62", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 3291, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": null, "error": "I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.", "status_code": 200, "outcome": "stopped", "duration_ms": 3292}
```

What the log already showed me that I didn't know before:

1. Some requests are really slow. `baggy jeans size 32` took 21.4 seconds and
   `black leather jacket under $80` took 15.6, while others took under 3. The
   server printed no rate limit waits, so it was the model calls themselves.
   The log only has the total time though, so I can't tell from it whether it
   was `suggest_outfit` or `create_fit_card` that was slow.
2. A wrong API key comes back as status 200, not an error code. The log
   catches it as `"outcome": "stopped"` with `model_calls` 1 and 0 tokens, but
   anything that only looked at status codes would think it worked.
3. It picks wrong items and still says `ok`. `cozy oversized hoodie` got a
   knit cardigan (`lst_008`) and `red beanie` got a flannel shirt
   (`lst_003`). That's the same keyword scoring problem from unit 4 and it's
   out of scope, but now I can see it in the log instead of only in a test.

**What It Costs**

Measured from the first 10 requests in the log above. They're all `ok` and
all have `cache_enabled` false, so every one was a real model call.

1. **Model calls:** 2 per run, every single time (`suggest_outfit` and
   `create_fit_card`). `search_listings` doesn't use the model.
2. **Tokens:** 3527 prompt and 1304 output across the 10 runs, so on average
   **352.7 prompt + 130.4 output = 483.1 tokens per run**. The smallest run
   was 316 + 96 (`brown leather belt`) and the biggest was 370 + 134
   (`baggy jeans size 32`).
3. **Time:** 81,368 ms across the 10 runs, so **8.1 seconds per run on
   average**. The median is 5.7 seconds, because three slow ones pull the
   average up. The fastest was 2.9 seconds and the slowest 21.4.
4. Runs that stop early cost almost nothing. No match was 0 model calls, a
   bad request was 0, and the wrong key run was 1 call that got rejected with
   0 tokens.

How I measured it: Gemini reports token counts on every response
(`usage_metadata.prompt_token_count` and `candidates_token_count`), and
`generate.py` adds them to a running total for the whole process.
`serve.py::ask` reads that total right before `run_agent` and right after,
and logs the difference, so it's exactly what that one request used. The
averages are the log numbers added up and divided by 10. None of it comes
from a pricing page.

In money it's $0 right now, because I'm on the Gemini free tier. Here's what
it would be on the paid tier.

After Milestones 5 and 6 I had a lot more real runs in the same log, so I
redid the average over all of them: every line with `"outcome": "ok"` and
`"cache_enabled": false`, which is 71 runs (the 10 above, the red beanie one,
and 60 from the six trials). That came out to **347.5 prompt + 122.5 output =
470.0 tokens per run**, always 2 model calls, between 405 and 556 tokens. So
the first ten runs were a little high but close.

Google's pricing page for Gemini 3.5 Flash Lite on the paid tier says $0.30
per 1M input tokens and $2.50 per 1M output tokens, and that output includes
"thinking" tokens. My counter in `generate.py` only adds up
`prompt_token_count` and `candidates_token_count`, so I checked whether I was
missing thinking tokens. I made one real call and printed the whole
`usage_metadata`: `prompt 10 candidates 17 thoughts None total 27`. No
thinking tokens, and prompt plus candidates equals the total, so the log
isn't leaving anything out.

One run:

```
input:   347.5 tokens x $0.30 / 1,000,000 = $0.0001042
output:  122.5 tokens x $2.50 / 1,000,000 = $0.0003063
total                                      = $0.0004105 per run
```

**If a hundred people used it a day, each doing one search, it would cost
about 4 cents a day, or about $1.23 a month:**

```
100 runs x $0.0004105 = $0.041 a day
$0.041 x 30 days      = $1.23 a month
100 runs x 470 tokens = 47,000 tokens a day, and 200 model calls a day
```

Output is only about a quarter of the tokens but it's three quarters of the
money, because it's over eight times the price per token. So if I ever had to
make this cheaper, a shorter outfit suggestion or fit card would save more
than a shorter prompt.

The money isn't really the limit though. The rate limit is. The free tier
lets 15 model calls through a minute, which is 7 answers a minute, and my
criterion 2 runs showed the eighth one in a minute waits about 27 seconds. A
hundred people spread over a day is fine. A hundred people arriving in the
same few minutes would mean most of them waiting. I also didn't check how
many requests a day the free tier allows, so I don't know if 200 calls a day
fits in it.

**Run Log and Verdicts**

The test is `run_capstone.py`. For each trial it starts `python serve.py`
fresh with `AI201_CACHE=0`, sends the requests from `criteria.md`, stops it,
starts it again with a wrong API key for criterion 4, and then scores
everything from the new lines in `logs/requests.jsonl`. I ran it with
`python run_capstone.py before` on November 15, 2026, three trials in a row
with 60 seconds between them and nothing changed in between. The full results
are in `results/capstone_2026-11-15_1634_before.md` and what the server
printed is in `results/capstone_2026-11-15_1634_before_server.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one complete log line | 16 of 16 | 16/16 | 16/16 | 16/16 | MET |
| 2. A matching query answers in under 8 seconds | 8 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 3. 2 model calls and 1 to 600 tokens per matching query | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Wrong API key gets 500 or higher, not 200 | 3 of 3 | 0/3 | 0/3 | 0/3 | MISSED |
| 5. Bad input gets a 400 and uses no model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

The diagnosis for the miss comes in the next part. Below is the real output
for each criterion from trial 1. Every log line was written by
`serve.py::ask` through `request_log.py::log_request`, and scored by
`run_capstone.py::run_trial`.

Criterion 1, every request leaves exactly one complete log line. What
`run_capstone.py` printed while it sent the 16 requests (status, the request
id from the response header, what was sent), and the check at the end:

```
200 464bbe5f  vintage graphic tee under $30
  200 58f169ae  90s track jacket in size M
  200 3f76a418  silk slip dress in midi length under $40
  200 33fddec7  platform sneakers size 8
  200 c48093a3  denim jacket under $50
  200 e048de05  black leather jacket under $80
  200 1e9f8088  baggy jeans size 32
  200 ec2edeed  cozy oversized hoodie
  200 670422bf  chunky knit sweater under $45
  200 8ce77754  brown leather belt
  200 fc5e75a2  designer ballgown size XXS under $5
  400 889848b1  bad body {}
  400 0a7d4151  bad body {"query": ""}
  400 c75a6c89  bad body ["vintage", "tee"]
  400 73347b10  bad body {"query": 42}
  400 b2e7b889  bad body hello

16 log lines for these 16 requests
criterion 1: 16/16 MET
```

Criterion 2, under 8 seconds. The `duration_ms` of the ten test queries, in
order:

```
duration_ms: [4318, 3067, 2287, 2842, 2472, 2355, 2142, 30209, 2409, 2952]
```

Nine were under 3.1 seconds. The eighth one, `cozy oversized hoodie`, took 30
seconds, and it was the eighth one in all three trials (30209, 29653 and 28790
ms). Its log line:

```
{"timestamp": "2026-11-15T23:35:32+00:00", "request_id": "ec2edeed", "route": "/ask", "query": "cozy oversized hoodie", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 351, "output_tokens": 129, "agent_ms": 30208, "parsed": {"description": "cozy oversized hoodie", "size": null, "max_price": null}, "num_results": 6, "selected_item_id": "lst_008", "selected_price": 35.0, "fit_card": "Obsessed with this chunky brown knit cardigan! Grab this thrifted gem on my Depop for just $35. Style it with a ribbed tank, baggy jeans, and combat boots for the ultimate cozy fit, or switch to wide-leg trousers for an effortless earth-toned look. ✨🤎", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 30209}
```

and what the server printed around it. The rate limit line comes right after
the seventh request:

```
Press CTRL+C to quit
127.0.0.1 - - [15/Nov/2026 16:34:26] "GET /health HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:32] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:37] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:42] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:47] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:51] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:34:56] "POST /ask HTTP/1.1" 200 -
127.0.0.1 - - [15/Nov/2026 16:35:00] "POST /ask HTTP/1.1" 200 -
  [rate limit] 15 requests used this minute. Waiting 27s. This is normal.
127.0.0.1 - - [15/Nov/2026 16:35:32] "POST /ask HTTP/1.1" 200 -
```

Criterion 3, model calls and tokens for the ten test queries:

```
2 calls / 472 tok; 2 calls / 518 tok; 2 calls / 513 tok; 2 calls / 419 tok; 2 calls / 477 tok; 2 calls / 467 tok; 2 calls / 456 tok; 2 calls / 480 tok; 2 calls / 496 tok; 2 calls / 412 tok
```

One of those lines in full:

```
{"timestamp": "2026-11-15T23:34:32+00:00", "request_id": "464bbe5f", "route": "/ask", "query": "vintage graphic tee under $30", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 2, "prompt_tokens": 353, "output_tokens": 119, "agent_ms": 4318, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "num_results": 10, "selected_item_id": "lst_002", "selected_price": 18.0, "fit_card": "Obsessed with this Y2K baby tee with the cutest butterfly print! Score it for just $18.0 on depop before I change my mind and keep it. Go check out my page for all the details on how to style it!", "error": null, "status_code": 200, "outcome": "ok", "duration_ms": 4318}
```

Criterion 4, wrong API key. All three came back 200, so 0 of 3. The three log
lines:

```
{"timestamp": "2026-11-15T23:36:02+00:00", "request_id": "9bc89b37", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 3336, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": null, "error": "I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.", "status_code": 200, "outcome": "stopped", "duration_ms": 3337}
{"timestamp": "2026-11-15T23:36:05+00:00", "request_id": "93915b68", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 1148, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": null, "error": "I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.", "status_code": 200, "outcome": "stopped", "duration_ms": 1149}
{"timestamp": "2026-11-15T23:36:09+00:00", "request_id": "5a2e1a13", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 1187, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": null, "error": "I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.", "status_code": 200, "outcome": "stopped", "duration_ms": 1188}
```

Criterion 5, bad input. The five log lines, in the same order as the list in
`criteria.md`:

```
{"timestamp": "2026-11-15T23:35:47+00:00", "request_id": "889848b1", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:35:49+00:00", "request_id": "0a7d4151", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{\"query\": \"\"}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:35:51+00:00", "request_id": "c75a6c89", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "[\"vintage\", \"tee\"]", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:35:53+00:00", "request_id": "73347b10", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "{\"query\": 42}", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
{"timestamp": "2026-11-15T23:35:55+00:00", "request_id": "b2e7b889", "route": "/ask", "status_code": 400, "outcome": "bad_request", "query": null, "raw_body": "hello", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0}
```

Every response to those five was a 400 with `"Send JSON with a 'query' field"`
in the error, which `run_capstone.py` checked from the response body.

The verdicts, against the targets I set in `criteria.md`:

1. Criterion 1, one complete log line per request: **MET**, 16 of 16 in all
   three trials.
2. Criterion 2, under 8 seconds: **MET**, 9 of 10 in all three trials. It
   passed, but only because I allowed two slow ones. More on that below.
3. Criterion 3, 2 model calls and 1 to 600 tokens: **MET**, 10 of 10 in all
   three trials. Tokens ran from 412 to 518.
4. Criterion 4, wrong API key gets 500 or higher: **MISSED**, 0 of 3 in all
   three trials. Every one came back 200.
5. Criterion 5, bad input gets a 400 with no model calls: **MET**, 5 of 5 in
   all three trials.

**The miss, criterion 4.** All 9 wrong key requests (3 per trial) came back
200, and their log lines all say `"outcome": "stopped"`, `"model_calls": 1`
and 0 tokens. So the first model call got rejected and nothing after it ran.

Where: the hand off between `agent.py::run_agent` and `serve.py::ask`.

How: in the outfit stage, `run_agent` catches `ModelUnavailable` from
`suggest_outfit`, writes a sentence into `session["error"]` ("I found Denim
Jacket ... but I couldn't reach the model to style it ...") and returns the
session like normal. `serve.py::ask` only gives a 500 when `run_agent` raises,
and it never raises here, so it hands out a 200. The bigger problem is that
"no matches" and "the model is down" reach `serve.py` exactly the same way, as
an English sentence in the same `error` field. "No matches" is a correct
answer and should be a 200. "The model is down" means the server is broken.
`serve.py` has no way to tell which one it got without reading the sentence,
so it treats them both the same and calls both of them `stopped` in the log.

**Not a miss, but worth saying, criterion 2.** The slow request was the eighth
test query (`cozy oversized hoodie`) in all three trials, at 30209, 29653 and
28790 ms, while the other nine were all between 2.1 and 5.2 seconds. Where:
`generate.py::_wait_for_slot`. How: it lets 15 model calls through per minute,
which is the free tier limit, and every FitFindr answer needs 2 calls. The
first seven queries use 14 calls in about 30 seconds, the eighth query's first
call is number 15, and its second call has to wait about 27 seconds for the
minute to roll over. The server printed
`[rate limit] 15 requests used this minute. Waiting 27s.` right before it each
time. So it isn't Gemini being slow, it's my own pacing, and it would happen to
every eighth shopper if requests came in as fast as my test sends them.

**Is it one problem or several?** The two things above aren't connected.
Criterion 4 is about how a failure gets reported, and criterion 2 is about the
free tier only fitting about 7 answers a minute.

**Were my targets too low?** Three of them, yes, honestly:

1. Criterion 2 only passed because I allowed 2 of 10 to be slow. If I tightened
   it to 10 of 10 under 8 seconds it would miss in every trial, and it would
   miss because of the rate limit, which is the real thing to know about this
   system. That's the one I'd tighten.
2. Criterion 3's 600 tokens was loose. The highest run was 518. 550 would
   still pass every run I have and would catch something growing sooner.
3. Criteria 1 and 5 can't really vary between trials, because there's no model
   involved in either check. They passed the same way every time, which is
   what they were supposed to show, but they were never likely to miss.

I'm not changing any of these in `criteria.md`. They weren't broken, they
were just easy, and the brief says only an unmeasurable criterion gets revised.

**The Improvement**

What I changed: when the model can't be reached, `serve.py` now answers 503
instead of 200, and logs it as `"outcome": "model_error"` instead of
`stopped`. It's one change in two places:

1. `agent.py::run_agent` now says *why* it stopped. I added an `error_kind`
   field to the session in `agent.py::new_session`. The empty search branch
   sets it to `"no_results"`, and both `except ModelUnavailable` handlers
   (the outfit one and the fit card one) set it to `"model_unavailable"`. The
   sentence in `error` is exactly the same as before.
2. `serve.py::ask` looks at `error_kind` instead of guessing from the
   sentence. `"model_unavailable"` gets a 503 and the outcome `model_error`.
   Any other stop (no matches) is still a 200 and `stopped`. The body is still
   the whole session, so the caller still gets the sentence about the API key.
   `error_kind` goes in the log line too.

Why this and not something else: the diagnosis said the problem is that "no
matches" and "model is down" arrive at `serve.py` looking exactly the same. So
the fix is to make them look different at the source, in the agent, where the
exception is actually caught, instead of having `serve.py` search the English
sentence for "couldn't reach the model", which would break the first time
someone reworded that message. I picked 503 (Service Unavailable) over a plain
500 because nothing crashed. The server is up, it just can't get to the thing
it depends on.

I ran exactly the same test again with `python run_capstone.py after`, three
trials, nothing else changed. Results are in
`results/capstone_2026-11-15_1650_after.md` and
`results/capstone_2026-11-15_1650_after_server.txt`.

Before (`results/capstone_2026-11-15_1634_before.md`):

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one complete log line | 16 of 16 | 16/16 | 16/16 | 16/16 | MET |
| 2. A matching query answers in under 8 seconds | 8 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 3. 2 model calls and 1 to 600 tokens per matching query | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Wrong API key gets 500 or higher, not 200 | 3 of 3 | 0/3 | 0/3 | 0/3 | MISSED |
| 5. Bad input gets a 400 and uses no model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

After (`results/capstone_2026-11-15_1650_after.md`):

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one complete log line | 16 of 16 | 16/16 | 16/16 | 16/16 | MET |
| 2. A matching query answers in under 8 seconds | 8 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 3. 2 model calls and 1 to 600 tokens per matching query | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Wrong API key gets 500 or higher, not 200 | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 5. Bad input gets a 400 and uses no model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Did it help: yes, for the thing it was aimed at. Criterion 4 went from 0 of 3
to 3 of 3 in every trial. One of the after log lines for a wrong key:

```
{"timestamp": "2026-11-15T23:52:11+00:00", "request_id": "07aab18a", "route": "/ask", "query": "denim jacket under $50", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 3510, "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "num_results": 7, "selected_item_id": "lst_007", "selected_price": 42.0, "fit_card": null, "error": "I found Denim Jacket — Light Wash, Cropped for $42.0 on poshmark, but I couldn't reach the model to style it, so there is no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that is sorted, run the same query again.", "error_kind": "model_unavailable", "outcome": "model_error", "status_code": 503, "duration_ms": 3510}
```

And the no match query in the same trial still came back as a normal 200,
which is what I wanted to keep:

```
{"timestamp": "2026-11-15T23:51:53+00:00", "request_id": "0d5d6ce1", "route": "/ask", "query": "designer ballgown size XXS under $5", "used_example_wardrobe": true, "waited_for_lock": false, "cache_enabled": false, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "agent_ms": 1121, "parsed": {"description": "designer ballgown", "size": "XXS", "max_price": 5.0}, "num_results": 0, "selected_item_id": null, "selected_price": null, "fit_card": null, "error": "I couldn't find anything for \"designer ballgown size XXS under $5\". Try removing the price limit, using a different size, or simpler keywords.", "error_kind": "no_results", "outcome": "stopped", "status_code": 200, "duration_ms": 1122}
```

Nothing else moved. Criteria 1, 3 and 5 are the same. Criterion 2 is 9 of 10
again in all three trials, and it's the eighth query again every time (29175,
29662 and 30154 ms), with the same rate limit wait printed 3 times in the
server output. That's expected, since I didn't touch the rate limit. I also
ran `python agent.py` and `python test.py` afterwards and both still work the
same as before (10 passed), so the CLI didn't break.

What it costs: anything that was treating every 200 as fine and reading
`error` to find problems still works, because the body didn't change. But
anything that was treating every non 200 as "the request was bad" will now
see a 503 for a broken key. I think that's the right trade, because it was
wrong before.

One thing the after run showed me that I got wrong earlier: in the diagnosis I
said a criterion 3 target of 550 tokens "would still pass every run I have".
The highest before run was 518, but in the after run one query used 556 tokens
(`silk slip dress in midi length under $40`, trial 2). So 550 would have been
too tight. The token count moves more between runs than my first ten runs
showed, because the model's outfit text goes into the fit card prompt and that
text is different every time.

**What's Still Broken**

After the improvement all five criteria are met, so there's no criterion
still missing. That doesn't mean nothing is broken. It mostly means some of my
targets were easy.

The target I'd tighten is criterion 2. It says 8 of 10 under 8 seconds and I
got 9 of 10 every time, but the one slow request was slow for a reason that
will always happen: every eighth answer in a minute waits about 27 seconds on
the rate limit. I'd tighten it to **10 of 10 under 8 seconds, with the ten
queries sent one after another**. That would have missed in all six trials,
which is the honest result, because a shopper who lands on the slow one waits
30 seconds no matter how fast the other nine were. What I'd do about it: have
`serve.py` say "busy, try again in a moment" with a 429 when the next model
call would have to wait, instead of holding the request open for half a
minute. I stopped before doing that because the brief allows one improvement,
and I used it on criterion 4, which was an actual miss.

Other things I know are still wrong, that none of my criteria catch:

1. **The log can't tell me which step was slow.** It has `duration_ms` and
   `agent_ms`, but not how long `search_listings`, `suggest_outfit` and
   `create_fit_card` each took. I only found out the 30 second request was
   the rate limit because I went and read the server's terminal output,
   which is exactly what the log was supposed to save me from doing.
2. **It still picks the wrong item sometimes and logs it as `ok`.** `cozy
   oversized hoodie` gets a knit cardigan and `red beanie` gets a flannel
   shirt. That's the keyword scoring problem from unit 4, and I said in The
   Shape that fixing it was out of scope.
3. **The log grows forever.** `logs/requests.jsonl` is append only and
   nothing ever rotates or trims it. It's 131 lines now, which is fine, but a
   real server running for months would need something.
4. **A crash still only shows up as a 500 with the exception name.** The
   `crash` outcome works (I tested it in Milestone 2 by making `run_agent`
   raise), but none of my five criteria ran it, so it isn't part of the
   measured results.

I didn't cut anything from what I planned in The Shape. Everything in it got
built.

**What I'd do next, with another unit:** I'd add a time for each step to the
log line, like `search_ms`, `outfit_ms` and `fit_card_ms`. Every other problem
on this list is easier to find and fix once the log can tell me where the time
went, and the 30 second request showed that it's the first question I end up
asking.

**How I Used AI**

I used Claude (the AI assistant in Claude Code) for this whole capstone. It
read the brief, wrote the code (`request_log.py`, the logging and the 503 in
`serve.py`, the `error_kind` field in `agent.py`, and `run_capstone.py`), ran
the tests, and drafted every section under this Capstone heading and the
Capstone part of RUNNING.md. I went one milestone at a time: it stopped after
each one, I read what it had done, and I made every commit myself.

**Moment 1: picking the system and the repo.** I gave Claude the brief and
asked it to help me do the capstone, and I had already made a new empty repo
for it. What I got back was a question instead of code. It pointed out the
brief says to use the same repo as the system you're extending ("not a copy,
not a fresh repo"), and it recommended FitFindr with shape A, because
`serve.py` was already there with the logging deliberately left out. What I
changed: I dropped my new repo and did everything in this FitFindr repo
instead, so the capstone sits on top of my unit 3 and 4 commits like the brief
wants.

**Moment 2: the five criteria.** The brief says not to have a model write
your criteria. When I got to Milestone 4, Claude didn't write them at first.
It gave me a table of what the log could measure and the numbers from my
Milestone 3 session, and told me to write them myself. I asked it to write
them anyway, so **the wording of the five capstone criteria in `criteria.md`
is Claude's, not mine.** The targets come from my own log (the 5.7 second
median, the 412 to 504 tokens per run, the wrong key coming back as a 200).
Then it ran them through the brief's three self check questions, and that
changed one: criterion 2 didn't say whether time spent waiting on the rate
limiter counts, so it got a sentence saying it does and that trials are 60
seconds apart. That sentence ended up mattering, because the rate limit is
exactly what made the eighth query slow in every trial.

One more thing about the order, since that's what the commit history is
supposed to show. My criteria commit is `fb9afb7` and my first results commit
is `9f753a6`. Their messages just say "unit 9 milestone 4" and "unit 9
milestone 5" and don't name what's in them, which I should have done. I
didn't reword them after pushing, because the brief says not to rewrite
history.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

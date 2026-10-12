"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    # ── Criterion 1, revised in unit 4 ───────────────────────────────────────
    #
    # The original criterion was one query run five times. search_listings is
    # plain Python, so that was the same search five times and it could only
    # ever measure determinism. The revised criterion names five different
    # phrasings instead, so here they are as five scenarios. Each one is a
    # wording a shopper would plausibly type for an item I checked is really in
    # data/listings.json, and I chose all five before running any of them.
    #
    # The five tries of criterion 1 are these five rows, not five repeats of
    # one row. run_eval.py still runs each one five times, which is a free
    # extra: it tells me whether a given phrasing is stable as well as whether
    # it works.
    {
        "name": "c1 phrasing 1: levis jeans",
        "query": "levis jeans size 30",          # lst_001, W30 L30
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "c1 phrasing 2: black bomber jacket",
        "query": "black bomber jacket",          # lst_022
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "c1 phrasing 3: green silk shirt",
        "query": "a green silk shirt",           # lst_029, titled "Silk Button-Down"
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "c1 phrasing 4: small tan purse",
        "query": "small tan purse",              # lst_039, titled "Mini Shoulder Bag"
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "c1 phrasing 5: chunky knit cardigan",
        "query": "chunky knit cardigan",         # lst_008
        "wardrobe": "example",
        "criterion": 1,
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        # A query nothing can match. Criterion 2, the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 is about the session, not about what the user typed, so
        # any query that finds something will do. I picked a different one from
        # criterion 1 so a bug that only shows up on one query cannot hide. What
        # I read is the trace: step 3 prints "selected_item id is lst_XXX" and
        # step 4 prints "item lst_XXX" going into suggest_outfit. The two ids
        # have to be the same string.
        "name": "selected item is the item styled",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 is about the fit card naming the price. run_eval.py runs
        # every scenario five times, so this is the same item written up five
        # separate times, which is what the criterion needs. Caching is off for
        # the run, so these are five real captions and not one answer repeated.
        # The top result here is lst_013 at $30.0, so I am looking for 30 in
        # the caption text.
        "name": "fit card names the price",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 names this exact query, so this is the query I run. The
        # ceiling is $30 and the data has an item priced at exactly $30.00,
        # which is the inclusive edge my Tool Inventory promised, so this is a
        # real test of the filter and not a soft one.
        "name": "price ceiling is never crossed",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes. Not
        # one of my five criteria, so it stays a diagnostic run.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems

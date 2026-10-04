"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()

    # Turn the description into a list of lowercase keywords. I strip out
    # punctuation (so "tee," still matches "tee") and skip very short words
    # like "a" or "in" so they don't match almost everything.
    cleaned = "".join(c if c.isalnum() else " " for c in description.lower())
    keywords = [word for word in cleaned.split() if len(word) >= 3]

    matches = []
    for listing in listings:
        # 1) price filter: skip anything above the ceiling
        if max_price is not None and listing["price"] > max_price:
            continue

        # 2) size filter: compare whole tokens, not substrings, so "M" matches
        # "S/M" but not "XL". "S/M" becomes ["s", "m"], "US 8" -> ["us", "8"].
        if size is not None:
            size_tokens = listing["size"].lower().replace("/", " ").split()
            if size.strip().lower() not in size_tokens:
                continue

        # 3) score by how many keywords appear in the title, description, or tags
        haystack = (
            listing["title"] + " "
            + listing["description"] + " "
            + " ".join(listing["style_tags"])
        ).lower()
        score = 0
        for word in keywords:
            if word in haystack:
                score += 1

        # 4) drop anything that matched no keywords at all
        if score == 0:
            continue

        matches.append((score, listing))

    # 5) best score first, then hand back just the listings (not the scores),
    # capped at the limit in config.py
    matches.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for score, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items", [])

    # A short description of the item we're trying to style.
    item_text = (
        f"{new_item['title']} "
        f"(category: {new_item['category']}, "
        f"colors: {', '.join(new_item['colors'])}, "
        f"style: {', '.join(new_item['style_tags'])})"
    )

    if not items:
        # Empty wardrobe: we have nothing of theirs to name, so ask for general
        # styling ideas instead of specific combinations. This is the empty case
        # from my Tool Inventory, and it still returns a real (non-empty) string.
        prompt = (
            f"I just found this secondhand item: {item_text}.\n"
            f"I don't have any wardrobe saved yet. Suggest one or two general "
            f"outfit ideas that would go with it. Keep it short."
        )
    else:
        # Build a simple list of what the user already owns, then ask for
        # combinations that name those pieces.
        owned = "\n".join(
            f"- {item['name']} ({', '.join(item['colors'])})" for item in items
        )
        prompt = (
            f"I just found this secondhand item: {item_text}.\n\n"
            f"Here is what I already own:\n{owned}\n\n"
            f"Suggest one or two outfits that combine the new item with pieces "
            f"from my wardrobe. Name the specific pieces you use. Keep it short."
        )

    system = (
        "You are a friendly thrift stylist. Give practical outfit ideas in a "
        "few short sentences. Only name wardrobe pieces that were listed."
    )
    return generate(prompt, system=system)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # 1) Guard: with no outfit text there is nothing to caption, so say so
    # instead of calling the model or crashing.
    if not outfit or not outfit.strip():
        return "No outfit suggestion was given, so there's nothing to write a fit card about."

    # 2) Build the prompt with the item details and the outfit.
    prompt = (
        f"Write a short, upbeat caption of 2 to 4 sentences for a thrift find.\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit idea: {outfit}\n\n"
        f"Mention the item, its price, and the platform once each. Make it sound "
        f"like a real post someone would share, not a product description."
    )

    # 3) Call the model and return whatever it writes.
    return generate(prompt)

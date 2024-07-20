import random
from collections import Counter


def enhance_prompt(prompt):
    tone = detect_tone(prompt)
    category = descriptors.get(tone, descriptors["neutral"])
    artist = category["artist"]
    style = random.choice(category["styles"])
    lighting = random.choice(category["lighting"])
    composition = random.choice(category["composition"])
    additional_tags = ", ".join(random.sample(category["additional_tags"], 2))

    sampling_method = category["sampling_method"]
    step_count = random.randint(category["step_count_range"][0], category["step_count_range"][1])

    enhanced_prompt = (
        f"{prompt}, in the style of {artist}, {style}, {lighting} lighting, "
        f"{additional_tags}, {composition}"
    )
    return enhanced_prompt, sampling_method, step_count


def detect_tone(prompt):
    tones = {
        "dark and spooky": [
            "dark", "haunted", "ghost", "creepy", "eerie", "mysterious",
            "sinister", "ominous", "shadowy", "macabre", "foreboding", "grisly",
            "horror", "dreadful", "chilling", "gothic", "nightmare", "haunting",
            "unsettling", "wicked", "deathly", "phantom", "horrific", "terror",
            "satanic", "ominous", "supernatural", "spectral", "ghastly"
        ],
        "cozy and autumnal": [
            "cozy", "autumn", "warm", "fall", "pumpkin", "harvest", "leaves",
            "fireplace", "cinnamon", "comfortable", "snug", "homely", "inviting",
            "rustic", "pleasant", "toasty", "comfortable", "quaint", "rustling",
            "amber", "crisp", "golden", "mellow", "thanksgiving", "foliage",
            "charming", "scenic", "autumnal", "hearth", "homey", "bountiful",
            "festive"
        ],
        "bright and fun": [
            "bright", "fun", "happy", "joyful", "colorful", "cheerful", "vibrant",
            "lively", "exciting", "playful", "upbeat", "radiant", "jolly",
            "spirited", "energetic", "gleeful", "dynamic", "festive", "zestful",
            "sunny", "vivacious", "exuberant", "sparkling", "animated", "chipper",
            "dazzling", "breezy", "blissful", "whimsical", "silly", "bouncy",
            "flamboyant"
        ],
        "romantic and dreamy": [
            "romantic", "dreamy", "love", "soft", "gentle", "ethereal", "passionate",
            "amorous", "enchanting", "blissful", "whimsical", "charming", "fantasy",
            "delicate", "tender", "serene", "adoring", "affectionate", "beautiful",
            "wistful", "rosy", "heartfelt", "sentimental", "idyllic", "moonlit",
            "flirtatious", "mesmerizing", "sultry", "yearning", "poetic", "intimate"
        ],
        "vintage and nostalgic": [
            "vintage", "nostalgic", "old", "retro", "classic", "timeless", "antique",
            "historical", "old-fashioned", "sentimental", "throwback", "yesteryear",
            "reminiscent", "past", "bygone", "rustic", "retrograde", "retroactive",
            "period", "archival", "timeless", "weathered", "patina", "sepia",
            "memorable", "heritage", "relic", "antiquated", "heirloom", "venerable",
            "evocative"
        ],
        "urban and modern": [
            "urban", "modern", "city", "contemporary", "sleek", "stylish", "industrial",
            "trendy", "cosmopolitan", "chic", "metropolitan", "sophisticated", "edgy",
            "up-to-date", "avant-garde", "current", "state-of-the-art", "cutting-edge",
            "innovative", "fashionable", "dynamic", "high-tech", "progressive",
            "futuristic", "minimalist", "refined", "upscale", "high-rise", "bustling",
            "urbane", "suburban"
        ],
        "fantasy and magical": [
            "fantasy", "magical", "fairy", "enchanting", "mythical", "wizard",
            "sorcery", "spellbinding", "otherworldly", "fantastical", "mystical",
            "legendary", "dreamlike", "supernatural", "wonder", "mystical", "charmed",
            "bewitched", "fabled", "arcane", "mythic", "epic", "phantasmagoric",
            "occult", "ethereal", "extraordinary", "transcendent", "magnetizing",
            "fantasmic", "sorcerous", "spectacular", "captivating"
        ],
        "nature and tranquil": [
            "nature", "tranquil", "peaceful", "serene", "calm", "natural", "soothing",
            "pastoral", "idyllic", "bucolic", "relaxing", "rejuvenating", "harmonious",
            "balmy", "refreshing", "quiet", "still", "zen", "picturesque", "meditative",
            "lush", "verdant", "organic", "restful", "gentle", "untamed", "wild",
            "breezy", "floral", "fertile", "arboreal", "unspoiled"
        ],
        "abstract and surreal": [
            "abstract", "surreal", "dream", "bizarre", "weird", "unusual", "imaginative",
            "fantastical", "psychedelic", "whimsical", "unconventional", "eccentric",
            "avant-garde", "peculiar", "outlandish", "hallucinatory", "conceptual",
            "irrational", "metaphysical", "esoteric", "ethereal", "unreal", "fanciful",
            "trippy", "dada", "cubist", "dadaist", "philosophical", "experimental",
            "fluid", "kaleidoscopic", "visionary", "chimerical"
        ],
        "sexy and glamorous": [
            "sexy", "glamorous", "seductive", "alluring", "provocative", "enticing",
            "captivating", "tempting", "voluptuous", "sensual", "sultry", "fashionable",
            "luxurious", "stylish", "glitzy", "elegant", "opulent", "posh", "voguish",
            "radiant", "exquisite", "sophisticated", "lush", "lavish", "chic",
            "allure", "fabulous", "beguiling", "fascinating", "enchanting", "desirable"
        ],
        "fun and spooky": [
            "fun", "spooky", "whimsical", "quirky", "creepy", "eerie", "mysterious",
            "ghostly", "haunted", "chilling", "gothic", "cartoony", "fantastical",
            "unsettling", "playful", "macabre", "weird", "bizarre", "whimsical",
            "spine-chilling", "haunting", "eerie", "odd", "peculiar", "quirky",
            "Tim Burton"
        ]
    }

    keyword_count = Counter()
    prompt_tokens = prompt.lower().split()

    for tone, keywords in tones.items():
        for keyword in keywords:
            if keyword in prompt_tokens:
                keyword_count[tone] += 1

    if keyword_count:
        return keyword_count.most_common(1)[0][0]
    else:
        return "neutral"


descriptors = {
    "dark and spooky": {
        "artist": "H.R. Giger",
        "styles": ["gothic", "surreal"],
        "lighting": ["dark", "shadowy"],
        "additional_tags": [
            "eerie", "mysterious", "ominous", "macabre", "foreboding",
            "trending on deviantart", "popular on ArtStation"
        ],
        "composition": ["rule of thirds", "leading lines", "frame within a frame"],
        "sampling_method": "ddim",
        "step_count_range": (80, 100)
    },
    "cozy and autumnal": {
        "artist": "Norman Rockwell",
        "styles": ["realism", "illustrative"],
        "lighting": ["warm", "golden"],
        "additional_tags": [
            "cozy", "autumnal", "inviting", "rustic", "pleasant",
            "featured on Pinterest", "popular on Instagram"
        ],
        "composition": ["rule of thirds", "symmetry", "leading lines"],
        "sampling_method": "euler",
        "step_count_range": (70, 90)
    },
    "bright and fun": {
        "artist": "Keith Haring",
        "styles": ["pop art", "modern"],
        "lighting": ["bright", "vivid"],
        "additional_tags": [
            "fun", "playful", "cheerful", "dynamic", "exciting",
            "trending on TikTok", "viral on Twitter"
        ],
        "composition": ["dynamic composition", "rule of thirds", "asymmetry"],
        "sampling_method": "ddim",
        "step_count_range": (64, 80)
    },
    "romantic and dreamy": {
        "artist": "John William Waterhouse",
        "styles": ["romanticism", "pre-raphaelite"],
        "lighting": ["soft", "diffused"],
        "additional_tags": [
            "gentle", "ethereal", "lovely", "charming", "serene",
            "trending on Tumblr", "popular on Behance"
        ],
        "composition": ["golden ratio", "leading lines", "soft focus"],
        "sampling_method": "euler",
        "step_count_range": (70, 90)
    },
    "vintage and nostalgic": {
        "artist": "Edward Hopper",
        "styles": ["realism", "vintage"],
        "lighting": ["sepia", "muted"],
        "additional_tags": [
            "retro", "classic", "timeless", "antique", "sentimental",
            "featured on Pinterest", "nostalgic on Instagram"
        ],
        "composition": ["rule of thirds", "framing", "central focus"],
        "sampling_method": "euler",
        "step_count_range": (70, 90)
    },
    "urban and modern": {
        "artist": "Jean-Michel Basquiat",
        "styles": ["street art", "contemporary"],
        "lighting": ["neon", "sharp"],
        "additional_tags": [
            "cityscape", "edgy", "trendy", "sleek", "industrial",
            "trending on DeviantArt", "popular on ArtStation"
        ],
        "composition": ["leading lines", "dynamic angles", "rule of thirds"],
        "sampling_method": "ddim",
        "step_count_range": (80, 100)
    },
    "fantasy and magical": {
        "artist": "Brian Froud",
        "styles": ["fantasy", "illustrative"],
        "lighting": ["glowing", "sparkling"],
        "additional_tags": [
            "mythical", "enchanted", "fairytale", "wizardry", "dreamlike",
            "trending on Tumblr", "popular on DeviantArt"
        ],
        "composition": ["center composition", "rule of thirds", "golden ratio"],
        "sampling_method": "ddim",
        "step_count_range": (80, 100)
    },
    "nature and tranquil": {
        "artist": "Claude Monet",
        "styles": ["impressionism", "landscape"],
        "lighting": ["natural", "soft"],
        "additional_tags": [
            "serene", "peaceful", "calm", "idyllic", "harmonious",
            "featured on Pinterest", "trending on Instagram"
        ],
        "composition": ["rule of thirds", "leading lines", "symmetry"],
        "sampling_method": "euler",
        "step_count_range": (70, 90)
    },
    "abstract and surreal": {
        "artist": "Salvador Dali",
        "styles": ["abstract", "surreal"],
        "lighting": ["dramatic", "contrasting"],
        "additional_tags": [
            "dreamlike", "bizarre", "whimsical", "unreal", "imaginative",
            "trending on Behance", "popular on ArtStation"
        ],
        "composition": ["dynamic composition", "asymmetry", "free form"],
        "sampling_method": "ddim",
        "step_count_range": (80, 100)
    },
    "sexy and glamorous": {
        "artist": "Helmut Newton",
        "styles": ["photography", "fashion"],
        "lighting": ["dramatic", "studio"],
        "additional_tags": [
            "alluring", "provocative", "seductive", "enticing", "opulent",
            "trending on TikTok", "popular on Instagram"
        ],
        "composition": ["rule of thirds", "central focus", "dynamic angles"],
        "sampling_method": "ddim",
        "step_count_range": (80, 100)
    },
    "fun and spooky": {
        "artist": "Tim Burton",
        "styles": ["gothic", "fantastical"],
        "lighting": ["dark", "whimsical"],
        "additional_tags": [
            "quirky", "creepy", "eerie", "mysterious", "playful",
            "trending on DeviantArt", "popular on ArtStation"
        ],
        "composition": ["rule of thirds", "leading lines", "asymmetry"],
        "sampling_method": "ddim",
        "step_count_range": (64, 80)
    },
    "neutral": {
        "artist": "Greg Rutkowski",
        "styles": ["concept art", "digital painting"],
        "lighting": ["natural", "balanced"],
        "additional_tags": [
            "beautiful", "stunning", "elegant", "timeless", "classic",
            "trending on DeviantArt", "popular on ArtStation"
        ],
        "composition": ["rule of thirds", "golden ratio", "balanced"],
        "sampling_method": "euler",
        "step_count_range": (70, 90)
    }
}

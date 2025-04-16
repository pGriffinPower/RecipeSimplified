import requests
from bs4 import BeautifulSoup

def recipe_to_text(url, output_txt):
    # 1. Fetch
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    
    # 2. Parse & Clean
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
        tag.decompose()
    
    # 3. Locate the recipe block
    recipe = soup.select_one(".wprm-recipe")  # adjust selector for your site
    if not recipe:
        # fallback: use readability
        from readability import Document
        doc = Document(resp.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        recipe = soup  # assume the main content is all we need
    
    # 4. Extract pieces
    lines = []
    # Title
    title = recipe.find(["h1", "h2"])
    if title:
        lines.append(title.get_text(strip=True))
        lines.append("")  # blank line
    
    # Ingredients
    ing_list = recipe.select(".wprm-recipe-ingredients-container li")
    if ing_list:
        lines.append("Ingredients:")
        for li in ing_list:
            lines.append(" - " + li.get_text(separator=" ", strip=True))
        lines.append("")
    
    # Instructions
    instrs = recipe.select(".wprm-recipe-instructions-container li")
    if instrs:
        lines.append("Instructions:")
        for i, step in enumerate(instrs, 1):
            lines.append(f" {i}. {step.get_text(strip=True)}")
        lines.append("")
    
    # Notes / Nutrition etc. (optional)
    notes = recipe.select(".wprm-recipe-notes li, .wprm-nutrition-label-container")
    if notes:
        lines.append("Notes:")
        for n in notes:
            lines.append(" * " + n.get_text(strip=True))
    
    # 5. Write out
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote text to {output_txt}")

# Example usage:
if __name__ == "__main__":
    recipe_to_text("https://www.spendwithpennies.com/coconut-curry-soup/", "coconut_curry_soup.txt")

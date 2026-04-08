def update():
    with open("data.py", "r", encoding="utf-8") as f:
        text = f.read()
    new_text = text.replace('            "domain":', '            "hint": "Hint retrieved: take extra time to analyze the formatting, ambiguity, and logic of all candidates.",\n            "domain":')
    with open("data.py", "w", encoding="utf-8") as f:
        f.write(new_text)

update()

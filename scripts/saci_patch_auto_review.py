import os

def patch_code_refactor():
    path = "agents/code_refactor.py"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    insert_after = "send_patch_with_buttons(filename)"
    insert_code = [
        "    generate_all_reviews_markdown(filename)\n",
        "    send_review_markdown_to_telegram(filename.replace(\".patch\", \"\").replace(\".diff\", \"\"))\n"
    ]

    new_lines = []
    for line in lines:
        new_lines.append(line)
        if insert_after in line:
            new_lines.extend(insert_code)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("✅ code_refactor.py обновлён.")

def patch_telegram_bot():
    path = "telegram_bot.py"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Удалим вызовы generate_all_reviews_markdown/send_review_markdown_to_telegram внутри apply:
    new_lines = []
    skip = False
    for line in lines:
        if "generate_all_reviews_markdown" in line or "send_review_markdown_to_telegram" in line:
            continue
        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("✅ telegram_bot.py очищен от дублирующего ревью.")

if __name__ == "__main__":
    patch_code_refactor()
    patch_telegram_bot()

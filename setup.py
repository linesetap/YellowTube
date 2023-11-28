#-------------------------------------
def format_number(num):
    if num >= 1000000000:
        return f"{num/1000000000:.2f}B"
    elif num >= 1000000:
        return f"{num/1000000:.2f}M"
    elif num >= 1000:
        return f"{num/1000:.2f}K"
    else:
        return f"{num:.0f}"

#-------------------------------------
def format_duration(sec):
    min, sec = divmod(sec, 60)
    hour, min = divmod(min, 60)
    if hour > 0:
        return f"{hour:02d}:{min:02d}:{sec:02d}"
    else:
        return f"{min:02d}:{sec:02d}"

#-------------------------------------
def load_json_file(filename):
    with open(filename, "r") as f:
        return eval(f.read())

#-------------------------------------
def count_users_by_language(users, translations):
    counts = {}
    for user in users.values():
        language = user["language"]
        if language in counts:
            counts[language] += 1
        else:
            counts[language] = 1

    # Add languages with 0 users
    for language_code, translation_info in translations.items():
        if language_code not in counts:
            counts[language_code] = 0

    return counts

#-------------------------------------
def format_counts(counts, translations):
    lines = []
    total_users = sum(counts.values())
    lines.append(f"<b>Total User: {total_users}</b>\n")
    # Sort languages by count and name
    languages = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    for language, count in languages:
        translation_info = translations[language]
        language_flag = translation_info["flag"]
        # Calculate percentage of users
        percentage = round(count / total_users * 100, 2)
        lines.append(f"{language_flag} | {count} - {percentage}%")
    return "\n".join(lines)

#-------------------------------------

import re
import httpx
import os

# Настройки
URL_SOURCE = os.getenv("SUB_URL")
TG_TAG = "@obwhitel"
MODE = os.getenv("FILTER_MODE") # "vless_only" или "except_vless"

def extract_flag(text):
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    return flags[0] if flags else ""

def main():
    if not URL_SOURCE:
        print("URL не задан")
        return

    # 1. Скачивание
    with httpx.Client(timeout=10.0) as client:
        r = client.get(URL_SOURCE)
        lines = r.text.splitlines()

    to_save = []
    seen = set()
    idx = 1

    for line in lines:
        line = line.strip()
        if not line or "://" not in line: continue
        
        protocol = line.split("://")[0].lower()
        content = line.split("#")[0]

        # Фильтрация
        if MODE == "vless_only":
            keep = (protocol == "vless")
        else:
            keep = (protocol != "vless")

        if keep and content not in seen:
            flag = extract_flag(line)
            country = re.search(r'([A-Z][a-z]+)', line)
            c_name = country.group(1) if country else "Server"
            
            # Формат: №1 | 🇷🇺 Russia | @obwhitel
            new_line = f"{content}#№{idx} | {flag} {c_name} | {TG_TAG}"
            to_save.append(new_line)
            seen.add(content)
            idx += 1

    # Запись в файл
    with open("subscription.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(to_save))
    print(f"Сохранено {len(to_save)} конфигов")

if __name__ == "__main__":
    main()

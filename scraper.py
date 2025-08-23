import webbrowser
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time



key_word = ""
sections = [
    "https://www.9news.com.au/",
    "https://www.theguardian.com/world",
    "https://www.abc.net.au/news",
    "https://www.skynews.com.au/"

]


filename = "news_headlines.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    html = page.content()


    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Section", "Headline", "Link"])

        for section_url in sections:
            print(f"Hacking {section_url}...")
            page.goto(section_url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(3)  # wait for JavaScript content
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            if "9news" in section_url:
                linker = soup.select("a.story__link")
                for l in linker:
                    link = l.get("href")
                    title = l.get_text(strip=True)
                    title = title.replace("‘",'"')
                    title = title.replace("’",'"')
                    title = title.replace("–",'"')
                    if "https" not in link:
                        link = "https://www.9news.com.au" + link
                    if key_word != "":
                        if key_word.lower() in title.lower():
                            writer.writerow(["9 News", title, link])
                    else:
                        writer.writerow(["9 News", title, link])
                print("SUCCESS!")
            elif "guardian" in section_url:
                linker = soup.select("a.dcr-2yd10d")
                for l in linker:
                    link = "https://www.theguardian.com" + l.get("href")
                    title = l.get("aria-label")
                    title = title.replace("‘",'"')
                    title = title.replace("’",'"')
                    title = title.replace("–",'"')
                    if key_word != "":
                        if key_word.lower() in title.lower():
                            writer.writerow(["Guardian", title, link])
                    else:
                        writer.writerow(["Guardian", title, link])
                print("SUCCESS!")
            elif "abc" in section_url:
                linker = soup.select("a.TopStoriesCard_link__D0AfC")
                for l in linker:
                    link = "https://www.abc.net.au" + l.get("href")
                    title = l.get_text(strip = True)
                    title = title.replace("‘",'"')
                    title = title.replace("’",'"')
                    title = title.replace("–",'"')
                    if key_word != "":
                        if key_word.lower() in title.lower():
                            writer.writerow(["ABC", title, link])
                    else:
                        writer.writerow(["ABC", title, link])
                print("SUCCESS!")
            elif "sky" in section_url:
                linker = soup.select("a.storyblock_title_link")
                for l in linker:
                    link = l.get("href")
                    title = l.get_text(strip = True)
                    title = title.replace("‘",'"')
                    title = title.replace("’","'")
                    title = title.replace("–","'")
                    if key_word != "":
                        if key_word.lower() in title.lower():
                            writer.writerow(["Sky News", title, link])
                    else:
                        writer.writerow(["Sky News", title, link])
                print("SUCCESS!")


    browser.close()


print(f"Done. Headlines saved to {filename}")

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
data = rows[1:]
try:
    title_idx = header.index("Headline")
    link_idx = header.index("Link")
except ValueError:
    print("CSV must have 'title' and 'link' columns.")
    exit()
html = """
<html>
<head>
<title>Scraped News</title>
<style>
table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
th, td { border: 1px solid #999; padding: 8px; text-align: left; }
th { background-color: #333; color: white; }
tr:nth-child(even) { background-color: #f2f2f2; }
a { color: #0645AD; text-decoration: none; }
a:hover { text-decoration: underline; }
</style>
</head>
<body>
<h1>Scraped News</h1>
<input type="text" id="searchBox" placeholder="Search headlines...">
<script>
    document.getElementById("searchBox").addEventListener("keyup", function() {
        let filter = this.value.toLowerCase();
        let rows = document.querySelectorAll("#newsTable tr");

        for (let i = 1; i < rows.length; i++) { // skip header row
            let text = rows[i].innerText.toLowerCase();
            rows[i].style.display = text.includes(filter) ? "" : "none";
        }
    });
</script>
<table>
"""

for i, col in enumerate(header):
    if i != link_idx:
        html += f"<th>{col}</th>"
html += "</tr>"


for row in data:
    row_html = ""
    for i, col in enumerate(row):
        if i == title_idx:  # replace title with clickable link
            url = row[link_idx]
            row_html += f'<td><a href="{url}" target="_blank">{col}</a></td>'
        elif i == link_idx:
            continue  # skip raw URL column
        else:
            row_html += f"<td>{col}</td>"
    html += f"<tr>{row_html}</tr>"

html += "</table></body></html>"

with open("DISPLAY.html", "w", encoding="utf-8") as f:
    f.write(html)



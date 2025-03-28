import re

# Read the input document
with open('new_compact.txt', 'r', encoding='utf-8') as file:
    content = file.read().replace('\ufeff', '')  # Remove BOM explicitly

# Split content into amendment blocks (title through next title or end)
amendment_blocks = re.split(r'\n(?=\d+\.\s+[^0-9\n])', content)
print(f"Total blocks after split: {len(amendment_blocks)}")
for i, block in enumerate(amendment_blocks[:3]):
    print(f"Block {i}: {repr(block[:100])}...")

# Filter blocks (handle BOM and ensure all amendments)
amendment_blocks = [block.strip() for block in amendment_blocks if re.match(r'\d+\.\s+', block.strip())]
print(f"Filtered blocks: {len(amendment_blocks)}")
for i, block in enumerate(amendment_blocks[:3]):
    print(f"Filtered Block {i}: {repr(block[:100])}...")

amendment_data = []

for block in amendment_blocks:
    # Extract amendment number and title
    title_match = re.match(r'(\d+)\.\s+(.+)', block)
    if not title_match:
        print(f"Skipping block due to no title match: {repr(block[:50])}...")
        continue
    number = title_match.group(1)
    title = title_match.group(2).strip()
    
    # Extract sections
    section_pattern = r'Section (\d+)\.\s+(.+?)(?=\nSection \d+\.|$|\nPurpose:|\n\d+\.\s+)'
    sections = []
    section_matches = re.finditer(section_pattern, block, re.DOTALL)
    
    for match in section_matches:
        section_num = match.group(1)
        section_text = match.group(2).strip()
        
        # Step 1: Break between subpoints in a list
        section_text = re.sub(r'([.:;\s])\s*(\([a-z]+\)|\([ivxlcdm]+\))\s+', r'\1<br>\2 ', section_text)
        
        # Step 2: Break after a subpoint list only if followed by a sentence
        # Look for last subpoint in a sequence, followed by a period and more text
        section_text = re.sub(r'(\([a-z]+\)|\([ivxlcdm]+\))\s*\.\s*([A-Z][^\(]*)$', r'\1<br>.\2', section_text)
        
        # Step 3: Remove <br> if it's the first thing
        if section_text.startswith('<br>'):
            section_text = section_text[4:]
        
        # Clean up: flatten remaining newlines
        section_text = section_text.replace('\n', ' ').strip()
        sections.append((section_num, section_text))
    
    if sections:
        amendment_data.append((number, title, sections))
        print(f"Amendment {number}: {title} - {len(sections)} sections")
    else:
        print(f"No sections found for Amendment {number}: {title} - Block: {repr(block[:200])}...")

print(f"Total amendments parsed: {len(amendment_data)}")

# HTML template (unchanged)
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amendments - The New Compact</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header id="top">
        <h1>The New Compact - Amendments</h1>
    </header>
    <nav>
        <a href="index.html">Home</a>
        <a href="amendments.html">Amendments</a>
        <a href="faq.html">FAQ</a>
        <a href="implementation.html">Implementation</a>
    </nav>
    
    <div class="container">
        <div class="toc">
            <h3>Table of Contents</h3>
            <ul>
{TOC}
            </ul>
        </div>
        <main>
{MAIN}
        </main>
    </div>
    
    <footer>
        © 2025 Harry Hinderson. This work is openly licensed via CC BY-NC-SA 4.0.<br>
        Contact: <a href="mailto:contact@newcompact.org" style="color: white;">contact@newcompact.org</a>
    </footer>
    <script>
        window.addEventListener('scroll', function() {{
            const toc = document.querySelector('.toc');
            const header = document.querySelector('header');
            const nav = document.querySelector('nav');
            const triggerPoint = header.offsetHeight + nav.offsetHeight;
            if (window.scrollY >= triggerPoint) {{
                toc.classList.add('fixed');
            }} else {{
                toc.classList.remove('fixed');
            }}
        }});
    </script>
</body>
</html>"""

# Generate TOC and Main content
toc_entries = []
main_entries = []

for number, title, sections in amendment_data:
    toc_subsections = '\n'.join(
        f'                        <li class="toc-subsection"><a href="#amendment{number}-section{s_num}">Section {s_num}</a></li>'
        for s_num, _ in sections
    )
    toc_entry = f"""            <li class="toc-section">
                <div class="amendment-title"><a href="#amendment{number}">{number}. {title}</a></div>
                <details>
                    <summary>View Sections</summary>
                    <ul>
{toc_subsections}
                    </ul>
                </details>
            </li>"""
    toc_entries.append(toc_entry)
    
    main_sections = '\n'.join(
        f"""        <h3 id="amendment{number}-section{s_num}">Section {s_num}</h3>
        <p>{s_text}</p>"""
        for s_num, s_text in sections
    )
    main_entry = f"""        <h2 class="amendment" id="amendment{number}">{number}. {title}</h2>
{main_sections}
        <a href="#top" class="back-to-top">Back to Top</a>"""
    main_entries.append(main_entry)

# Combine into full HTML
toc_content = '\n'.join(toc_entries)
main_content = '\n'.join(main_entries)
final_html = html_template.format(TOC=toc_content, MAIN=main_content)

# Write to file
with open('amendments.html', 'w', encoding='utf-8') as file:
    file.write(final_html)

print("Generated amendments.html successfully!")
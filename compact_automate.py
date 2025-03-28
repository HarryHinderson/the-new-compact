import re

# Read the input document
with open('new_compact.txt', 'r', encoding='utf-8') as file:
    content = file.read().replace('\ufeff', '')  # Remove BOM explicitly

# Split content into amendment blocks
amendment_blocks = re.split(r'\n(?=\d+\.\s+[^0-9\n])', content)
amendment_blocks = [block.strip() for block in amendment_blocks if re.match(r'\d+\.\s+', block.strip())]

amendment_data = []

for block in amendment_blocks:
    # Extract amendment number and title
    title_match = re.match(r'(\d+)\.\s+(.+)', block)
    if not title_match:
        continue
    number = title_match.group(1)
    title = title_match.group(2).strip()
    
    # Extract Purpose
    purpose_match = re.search(r'Purpose:\s*(.+?)(?=\nSection \d+\.|$)', block, re.DOTALL)
    purpose = purpose_match.group(1).strip().replace('\n', ' ') if purpose_match else "No purpose specified."
    
    # Extract sections
    section_pattern = r'Section (\d+)\.\s+(.+?)(?=\nSection \d+\.|$|\nPurpose:|\n\d+\.\s+)'
    sections = []
    section_matches = re.finditer(section_pattern, block, re.DOTALL)
    
    for match in section_matches:
        section_num = match.group(1)
        section_text = match.group(2).strip()
        
        # Protect citations by temporarily replacing them with a placeholder
        citation_pattern = r'Section \d+\([a-z]+\)'
        citations = {}
        def protect_citation(match):
            placeholder = f"__CITATION_{len(citations)}__"
            citations[placeholder] = match.group(0)
            return placeholder
        
        protected_text = re.sub(citation_pattern, protect_citation, section_text)
        
        subclause_text = ""
        continuation_text = ""
        
        # Define pattern for subclause labels (e.g., (a), (b), (i), etc.)
        label_pattern = r'\([a-z]+\)|\([ivxlcdm]+\)'
        labels = list(re.finditer(label_pattern, protected_text))
        
        if labels:
            # Check if this is a list: multiple labels or intro ends with list delimiter
            intro_end = labels[0].start()
            intro_text = protected_text[:intro_end].strip()
            is_list = len(labels) > 1 or (intro_text and intro_text[-1] in '.:;')
            
            if is_list:
                # Introductory text for a list
                if intro_text and intro_text[-1] in '.:;':
                    subclause_text += intro_text + '<br>'
                else:
                    subclause_text += intro_text + ' '
                
                # Process all subclauses except the last one
                for i in range(len(labels) - 1):
                    label = labels[i].group()
                    start = labels[i].end()
                    end = labels[i + 1].start()
                    text = protected_text[start:end].strip()
                    
                    # Check for conjunctions
                    conjunction_match = re.match(r'(.*)\b(or|and)\s*$', text, re.DOTALL)
                    if conjunction_match:
                        text_before, conj = conjunction_match.groups()
                        subclause_text += f"{label} {text_before.strip()} {conj}<br>"
                    else:
                        subclause_text += f"{label} {text}<br>"
                
                # Handle the last subclause
                last_label = labels[-1].group()
                last_start = labels[-1].end()
                last_text = protected_text[last_start:].strip()
                
                # Check for continuation text
                continuation_match = re.match(r'([^.;:]+[.;:]\s*)(.*)', last_text, re.DOTALL)
                if continuation_match:
                    subclause_part, continuation_part = continuation_match.groups()
                    subclause_text += f"{last_label} {subclause_part.strip()}"
                    if continuation_part.strip():
                        continuation_text = continuation_part.strip()
                else:
                    subclause_text += f"{last_label} {last_text}"
            else:
                # Not a list, treat as plain text
                subclause_text = protected_text
        else:
            # No labels, treat as plain text
            subclause_text = protected_text
        
        # Restore citations
        for placeholder, citation in citations.items():
            subclause_text = subclause_text.replace(placeholder, citation)
            if continuation_text:
                continuation_text = continuation_text.replace(placeholder, citation)
        
        # Replace newlines with spaces for consistency within paragraphs
        subclause_text = subclause_text.replace('\n', ' ').strip()
        continuation_text = continuation_text.replace('\n', ' ').strip() if continuation_text else ""
        
        # Combine into section content
        section_content = []
        if subclause_text:
            section_content.append(subclause_text)
        if continuation_text:
            section_content.append(continuation_text)
        
        sections.append((section_num, section_content if section_content else [section_text]))
    
    if sections:
        amendment_data.append((number, title, purpose, sections))

# HTML template
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
        <a href="/">Home</a>
        <a href="/amendments">Amendments</a>
        <a href="/faq">FAQ</a>
        <a href="/implementation">Implementation</a>
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
        Contact: <a href="mailto:thedankmlgmemes@gmail.com" style="color: white;">thedankmlgmemes@gmail.com</a>
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

for number, title, purpose, sections in amendment_data:
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
        {"".join(f"<p>{s_text}</p>" for s_text in s_content)}"""
        for s_num, s_content in sections
    )
    main_entry = f"""        <h2 class="amendment" id="amendment{number}">{number}. {title}</h2>
        <p class="purpose">{purpose}</p>
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
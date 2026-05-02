"""
Common filter logic for MathJax processing using BeautifulSoup.
This handles block math elements - inline math is left untouched as it
already renders correctly with the original server's MathJax configuration.
"""

from bs4 import BeautifulSoup


def extract_latex_from_alt(alt_text: str) -> str:
    """Extract the LaTeX formula from the alt text, cleaning it up."""
    formula = alt_text.strip()

    # Handle various prefixes
    if formula.startswith(r"{\displaystyle"):
        formula = formula[len(r"{\displaystyle"):].strip()
    elif formula.startswith(r"\displaystyle"):
        formula = formula[len(r"\displaystyle"):].strip()
    elif formula.startswith(r"{\textstyle"):
        formula = formula[len(r"{\textstyle"):].strip()
    elif formula.startswith(r"\textstyle"):
        formula = formula[len(r"\textstyle"):].strip()

    # Remove surrounding braces if they wrap the entire formula
    if formula.startswith("{") and formula.endswith("}"):
        # Find the matching closing brace
        depth = 0
        end_pos = len(formula)
        for i, c in enumerate(formula):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end_pos = i
                    break
        formula = formula[1:end_pos]

    # Clean up any extra trailing } that don't have matching {
    while formula.endswith("}"):
        test_formula = formula[:-1]
        open_count = test_formula.count('{')
        close_count = test_formula.count('}')
        if close_count >= open_count:
            formula = test_formula
        else:
            break

    return formula.strip()


def process_math_elements(html_content: str) -> str:
    """
    Process HTML content to replace BLOCK math elements with MathJax-compatible spans.
    Inline math is LEFT UNTOUCHED as it already renders correctly with the
    original server's MathJax configuration.

    Uses BeautifulSoup for reliable parsing regardless of whitespace/formatting.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Process ONLY block math elements
    # Structure: <span class="mwe-math-element mwe-math-element-block">
    #              <span class="mwe-math-mathml-display...">
    #                <math alttext="...">...</math>
    #              </span>
    #              <img alt="...">
    #            </span>
    block_math_spans = soup.find_all(
        'span',
        class_='mwe-math-element mwe-math-element-block'
    )

    for span in block_math_spans:
        # Try to get alttext from the <math> tag inside
        math_tag = span.find('math')
        img_tag = span.find('img')

        if math_tag and math_tag.get('alttext'):
            alttext = math_tag.get('alttext')
        elif img_tag and img_tag.get('alt'):
            alttext = img_tag.get('alt')
        else:
            # Skip if no alt text found
            continue

        formula = extract_latex_from_alt(alttext)

        # Replace the entire span - convert block math to inline format
        # MediaWiki.js processes 'mwe-math-element-inline' but not 'mwe-math-element-block'
        # So we change the class to trigger MathJax processing, then use CSS for block display
        span['class'] = ['mwe-math-element', 'mwe-math-element-inline']
        span['style'] = 'display: block; text-align: center; margin: 1em 0;'

        # Find or create the inner span with mwe-math-mathml-display
        inner_span = span.find('span', class_='mwe-math-mathml-display')
        if not inner_span:
            inner_span = soup.new_tag('span', **{'class': 'mwe-math-mathml-display mwe-math-mathml-a11y'})
            # Insert at the beginning
            for child in list(span.children):
                if child != inner_span:
                    child.decompose()
            span.insert(0, inner_span)
        else:
            # Remove other children except inner_span and img
            for child in list(span.children):
                if child != inner_span and not (child.name == 'img'):
                    child.decompose()

        # Update style - make it inline (not block)
        inner_span['style'] = ''

        # Find or create the <math> tag
        math_tag = inner_span.find('math')
        if not math_tag:
            math_tag = soup.new_tag('math')
            inner_span.insert(0, math_tag)

        # Set the alttext attribute (MediaWiki.js uses this to render)
        math_tag['alttext'] = formula

        # IMPORTANT: Do NOT set text content - MediaWiki.js reads alttext and renders
        # If we leave text content, it shows both the raw LaTeX AND the rendered math
        # Just clear any existing text
        math_tag.string = ''

        # Update the <img> to match inline format
        img_tag = span.find('img')
        if not img_tag:
            img_tag = soup.new_tag('img')
            span.append(img_tag)
        img_tag['class'] = ['mwe-math-fallback-image-inline', 'mw-invert', 'skin-invert']
        img_tag['alt'] = formula
        img_tag['aria-hidden'] = 'true'

    # NOTE: Inline math (mwe-math-element-inline) is left untouched.
    # The original server's MathJax configuration (MediaWiki.js) already
    # handles inline math rendering correctly via the img tags with alt attributes.

    return str(soup)


def process_html_response(html_content: str) -> str:
    """Process HTML content to enable MathJax rendering.

    NOTE: The original server already has MathJax loaded with MediaWiki.js,
    so we only need to convert block math elements to inline format.
    """
    return process_math_elements(html_content)

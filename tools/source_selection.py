"""Choose Montana source alternatives by their stated effective date, without assuming a contingency occurred."""
import datetime as dt
import re


class HeldSource(ValueError):
    """An official page cannot yet be represented as an established current section."""


def _heading(node):
    catches = node.xpath('.//span[contains(concat(" ", normalize-space(@class), " "), " catchline ")]')
    return re.sub(r'\s+', ' ', catches[0].text_content()).strip() if catches else ''


def _effective_label(node):
    """Read publisher markup, not ordinary subject words in a section catchline."""
    catches = node.xpath('.//span[contains(concat(" ", normalize-space(@class), " "), " catchline ")]')
    if not catches:
        return ''
    labels = catches[0].xpath('.//span[contains(concat(" ", normalize-space(@class), " "), " effective-clause ")]')
    return ' '.join(re.sub(r'\s+', ' ', label.text_content()).strip() for label in labels)


def choose_sections(nodes, as_of):
    """Return (selected indexes, audit). Unlabelled continuation blocks are kept together.

    A dated alternative takes precedence once its date is reached. Future alternatives are excluded.
    Contingent and unrecognised alternatives are held, including their preceding temporary wording.
    """
    if not nodes:
        raise HeldSource('no official section-content block')
    cutoff = dt.date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    choices, continuations, labels = [], [], []
    for i, node in enumerate(nodes):
        heading = _heading(node)
        effective_label = _effective_label(node)
        labels.append(heading)
        if re.search(r'effective\s+on\s+occurrence\s+of\s+contingency', effective_label, re.I):
            raise HeldSource('official contingency occurrence has not been established')
        effective = re.search(r'\beffective\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})', effective_label, re.I)
        if effective:
            if cutoff is None:
                raise HeldSource('an explicit as-of date is required for dated source alternatives')
            try:
                start = dt.datetime.strptime(re.sub(r'\s+', ' ', effective[1]), '%B %d, %Y').date()
            except ValueError as exc:
                raise HeldSource('unrecognised official effective date: ' + effective[1]) from exc
            choices.append((start, i))
        elif re.search(r'\beffective\b', effective_label, re.I):
            raise HeldSource('unrecognised or unresolved official effective condition: ' + heading)
        elif heading:
            choices.append((None, i))
        else:
            continuations.append(i)
    undated = [i for day, i in choices if day is None]
    if len(undated) > 1:
        raise HeldSource('multiple undated alternatives lack an established selection rule')
    applicable = [(day, i) for day, i in choices if day is not None and day <= cutoff]
    if applicable:
        newest = max(day for day, _ in applicable)
        matching = [i for day, i in applicable if day == newest]
        if len(matching) != 1:
            raise HeldSource('multiple alternatives have the same effective date')
        selected = matching + continuations
    elif undated:
        selected = undated + continuations
    elif not choices:
        selected = continuations
    else:
        raise HeldSource('the source gives only future wording for the requested date')
    return selected, {'as_of': cutoff.isoformat() if cutoff else None, 'selected_indexes': selected,
                      'effective_dates': {str(i): day.isoformat() if day else None for day, i in choices},
                      'source_block_count': len(nodes), 'headings': labels}


def require_date_plan(path, slugs):
    """New corpus dates require an explicit source-backed plan; a retrieval date is never supplied here."""
    import json
    if not path:
        raise HeldSource('edition date is only "Updated August 2026"; an approved source-backed date plan is required')
    with open(path, encoding='utf8') as f:
        plan = json.load(f)
    for slug in slugs:
        row = plan.get(slug, {})
        if not row.get('source_quote') or not row.get('source_url') or row.get('basis') == 'retrieval':
            raise HeldSource(slug + ': no source-backed date basis')
        try:
            day = dt.date.fromisoformat(row['in_force'])
        except (KeyError, ValueError) as exc:
            raise HeldSource(slug + ': no exact ISO source-backed date; month precision needs coordinator representation') from exc
        english = rf'{day.strftime("%B")}\s+0?{day.day},\s*{day.year}'
        if not re.search(rf'(?:{re.escape(day.isoformat())}|{english})', row['source_quote'], re.I):
            raise HeldSource(slug + ': the quoted source does not state the proposed exact date')
    return plan

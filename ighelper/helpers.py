import re


# Mainly taken from https://gist.github.com/davidtheclark/5521432
def _dumb_to_smart_quotes(string):
    """
    Take a string and return it with dumb quotes, single and double, replaced by smart quotes.

    Accounts for the possibility of HTML tags within the string.
    """

    # Find dumb double quotes coming directly after letters or punctuation,
    # and replace them with right double quotes.
    string = re.sub(r'([a-zA-Z0-9.,?!;:\'\"])"', r'\1”', string)
    # Find any remaining dumb double quotes and replace them with
    # left double quotes.
    string = string.replace('"', '“')
    # Reverse: Find any SMART quotes that have been (mistakenly) placed around HTML
    # attributes (following =) and replace them with dumb quotes.
    string = re.sub(r'=“(.*?)”', r'="\1"', string)
    # Follow the same process with dumb/smart single quotes
    string = re.sub(r"([a-zA-Z0-9.,?!;:\"\'])'", r'\1’', string)
    string = string.replace("'", '‘')
    string = re.sub(r'=‘(.*?)’', r"='\1'", string)
    return string


def get_name(name, username):
    if name:
        return _dumb_to_smart_quotes(name)
    return username

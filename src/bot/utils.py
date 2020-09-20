import re
import asyncio


def log_msg(data):
    """
    Accepts a list of data elements, removes the  u'\u241e'character
    from each element, and then joins the elements using u'\u241e'.

    Messages should be constructed in the format:

        {message_type}\u241e{data}

    where {data} should be a \u241e delimited row.
    """
    tmp = [str(d).replace(u'\u241e', ' ') for d in data]
    return u'\u241e'.join(tmp)

# Format a message as a block quotes.
def block_format(message):
    """
    Formats a given message as a Markdown block quote
    """

    # Find new line positions
    insert_idx = [pos for pos, char in enumerate(message) if char == "\n"]
    insert_idx.insert(0, -1)

    # Insert "> " for block quote formatting
    for offset, i in enumerate(insert_idx):

        message = (message[:i + (2 * offset) + 1] + 
                  "> " + 
                  message[i + (2 * offset) + 1:])

    return(message)

def parse_msg_url(url):
    """
    Parses out the message id from a discord message url
    """

    if not re.match(r'^https:\/\/discord(app)*\.com\/channels\/', url):
        raise ValueError("Provided URL is not a Discord Message URL")

    url_template = re.compile(
        r"https:\/\/discord[a-z]*\.com\/channels\/([0-9]*)\/([0-9]*)\/([0-9]*)"
    )

    server, channel, message = re.search(url_template, url).groups()

    return int(server), int(channel), int(message)

def parse_request(request, norm_text=False):
    '''
    This parses an incoming message for the request and the reply
    Functionally separates the first string from any subsequent strings
    '''
    # Parse out message target and reply (if it exists)
    msg_target = request.split(' ')[0]
    extra = request.split(' ')[1:]

    if '\r' in msg_target or '\n' in msg_target:
      # If weird users decide to separate the msg_id from the reply using a line return
      # clean it up.
      if '\r' in msg_target:
        _temp = msg_target.split('\r')
      else:
        _temp = msg_target.split('\n')

      msg_target = _temp[0].strip()
      extra = [_temp[1].strip()] + request.split(' ')[1:]
      
    if norm_text:
        msg_target = msg_target.strip().lower()
        extra = extra.strip().lower()

    return msg_target, extra

async def clean_up_request(ctx, msg_target):
    try:
        await ctx.message.delete()
        log.info(log_msg(['deleted_request', msg_target]))
    except Exception as e:
        log.warning(log_msg(['delete_request_failed', msg_target, e]))

    return
# Splits a string into several sub-2000 char strings
def splitLongStrings(str, chars=950, preferred_char=" "):
    messages = []
    if preferred_char not in str:  # If there are no spaces, don't respect spaces
        message = ""
        for c in str:
            if len(message) >= chars:  # >= is equivalent to adding 1 to len(message)
                messages.append(message)
                message = ""
            message = message + c
        messages.append(message)
        return messages
    # If there are spaces, respect them
    words = str.split(preferred_char)
    message = ""
    for word in words:
        if len(message) + len(word) > chars:
            messages.append(message[1:])  # delete leading space
            message = ""
        message = message + preferred_char + word
    if len(message) > 1:
        messages.append(message[1:])
    return messages


def gen_invis(i: int = 1):
    if i < 0:
        i = 0
    return str(chr(0xFFA0)) * (i + 1) + " " + str(chr(0x1CBC)) * 4
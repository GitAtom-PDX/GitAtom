# https://www.educative.io/answers/how-to-escape-unescape-html-characters-in-string-in-javascript
replacements = [
    (r"&", r"&amp;"),
    (r"<", r"&lt;"),
    (r">", r"&gt;"),
]

def escape(text):
    for r in replacements:
        text = text.replace(r[0], r[1])
    return text

def unescape(text):
    for r in reversed(replacements):
        text = text.replace(r[1], r[0])
    return text

if __name__ == "__main__":
    t = "<span>a</span> &lt;b&gt; &c &amp;d;"
    if False:
        print(t)
        print(escape(t))
        print(unescape(escape(t)))
    assert t == unescape(escape(t))

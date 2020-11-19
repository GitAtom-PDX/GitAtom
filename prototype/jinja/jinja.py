from jinja2 import Template

header = "GitAtomProject"
blog = "This is an example of genating a simple html page using jinja2"

with open("example.html","w") as f:
    message = """
    <html>
        <head>
        <title>{{Title}}</title>
        </head>
        <body>
            <h1>{{Header}}</h1>
            <p> {{Blog}} </p>
        </body>
    </html>
    """

    template = Template(message)
    out = template.render(Title="Capstone project",
                          Header=header,
                          Blog=blog)
    f.write(out)

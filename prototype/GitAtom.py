
import cmarkgfm     #used to convert markdown to html in mdtohtml()
import os           #used to get file name of markdown to match in html file in mdtohtml()

#funtion to convert markdown file into html 
#called by mdtohtml('filename.md')
#either returns a html file on success or None on failure
def mdtohtml(md_file):
    #make sure there is a valid os path
    if os.path.exists(md_file):
        html_name= os.path.basename(md_file)
        title = len(html_name)

        #make sure file is a .md markdown file
        if html_name[title-3:title] == '.md':
            html_name = html_name[:title-3]
            md_file = open(md_file, "r")
            md_text = md_file.read()
            md_file.close()

            html_text = cmarkgfm.markdown_to_html(md_text)
            #TODO need to change naming convention of new html files
            html_file = open('{0}.html'.format(html_name), "w")
            html_file.write(html_text)
            html_file.close()
            return html_file #success
    return None #failure


#!/usr/bin/python
import cgi, json, datetime, docx, re, subprocess, os, sys, traceback

classesFile = "edit/classes.json"

def readClasses():
  return json.load(open(classesFile, 'r'))

def writeClasses(classes):
  json.dump(classes, open(classesFile, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def getNote(subject):
  note = subject[2]
  if note != "": note = ", " + note
  s = ""
  if subject[1] > 1: s = "s"
  return "\n({} credit{} required{})".format(subject[1], s, note)

#replace quotes
def rq(s):
  return cgi.escape(s).replace("'", "&apos;").replace('"', '&quot;')

#format
def f(s, *args):
  return s.format(*[rq(str(arg)) for arg in args])

CURRENT_YEAR = datetime.date.today().year
DOCUMENT_TIMEOUT = 60 #seconds

form = cgi.FieldStorage()

INPUT = 0
PRINT = 1
VIEW = 2
EDIT = 3

try:
  action = int(form['action'].value)
except:
  action = INPUT


print '''Content-type: text/html

<!DOCTYPE html>'''

classes = readClasses()

if action == VIEW:
  print '''<html>
<head>
<meta charset="UTF-8">
<title>Class Lists</title>
</head>
<body>
<h2>Class Lists</h2>'''
  for subject in classes:
    print f("<br><br><b>{}</b>{}<br><br>", subject[0], getNote(subject))
    for item in subject[3]:
      print f('{}<br>', item)
  print '''</body>
</html>'''

if action == INPUT:
  try:
    years = int(form['years'].value)
    html5 = not 'html4' in form
  except:
    print '''<html>
<head>
<meta charset="UTF-8">
<title>Options</title>
</head>
<body>
<h2>
Options
</h2>
<form>
Enter the number of years:
<input type="text" name="years" value="4">
<br><br><input type="checkbox" name="html4"> Disable HTML5? (Use this if the dropdown menus are not working properly)
<br><br><input type="submit" value="Continue">
</form>
</body>
</html>'''
    quit()
  print '''<html>
<head>
<meta charset="UTF-8">
<title>Generate Document</title>
<style>
table, th, td {
    border: 1px solid black;
}
</style>
</head>
<body>
<h2>Generate Document</h2>

<form target="_blank">

Student Name: <input required type="text" name="name" value=""><br><br>
Start Year: <input required type="text" name="year" value="'''+str(CURRENT_YEAR)+'''">
<br><br>

<table><thead>
<tr><td><b>COURSE</b></td>'''

  for i in range(years):
    print f('<th>Year {}</th>', i+1)
  print '</tr></thead><tbody>'
  for subject in classes:
    print f('<tr><td><b>{}</b><br>{}</td>', subject[0], getNote(subject))
    for i in range(years):
      name = rq(subject[0]+str(i))
      print "<td>"
      for ab in ("a", "b"):
        id = name.replace(" ", "_")+ab
        if html5:
          print f('<input type="text" name="{}" list="{}">', name+ab, id)
          print f('<datalist id="{}">', id)
          for option in subject[3]:
            print f('<option value="{}">{}</option>', option, option)
          print '</datalist>'
        else:
          print f('<select name="{}"><option value="">--------</option>', name+ab)
          for option in subject[3]:
            print f('<option value="{}">{}</option>"', option, option)
          print '</select>'
      print '</td>'
    print '</tr>'
  print '''</tbody></table>
<br/><br/>'''
  print f('<input type="hidden" name="action" value="{}">', PRINT)
  print f('<input type="hidden" name="years" value="{}">', years)
  print '''<input type="submit" value="Export">
<br><br>
<a target="_blank" href="classes.py?action=2">View the class lists</a>
<br><a href="index.html">Go Back</a>
</form>
</body>
</html>
'''

def add_hyperlink(paragraph, url, text):
    """
    A function that places a hyperlink within a paragraph object.

    :param paragraph: The paragraph we are adding the hyperlink to.
    :param url: A string containing the required url
    :param text: The text displayed for the url
    :return: The hyperlink object
    """

    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a w:r element
    new_run = docx.oxml.shared.OxmlElement('w:r')

    # Create a new w:rPr element
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    # Join all the xml elements together add add the required text to the w:r element
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    paragraph._p.append(hyperlink)

    return hyperlink


def urlify(s):

     # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"[^\w\s]", '', s)

     # Replace all runs of whitespace with a single dash
     s = re.sub(r"\s+", '_', s)

     return s

def generate(contents):
  studentName = contents['name']
  startYear = contents['startYear']
  years = contents['years']
  chosen = contents['selected']
  
  document = docx.Document()

  document.add_heading('ESOL Student Graduation Plan', 0)

  """table = document.add_table(rows=3, cols=3)
  table.cell(0,0).text = "Name: " + studentName
  table.cell(0,1).text = "ID#:"
  table.cell(0,2).text = "School:"
  table.cell(1,0).text = "Date of Birth:"
  table.cell(1,1).text = "Last Year Eligible in MCPS:"
  table.cell(2,0).text = "Credits from ISAO? Yes/No"
  table.cell(2,1).text = "Expected Date of Graduation:"
  table.cell(1,1).merge(table.cell(1,2))
  table.cell(2,1).merge(table.cell(2,2))"""

  table = document.add_table(rows=1, cols=3)
  table.cell(0,0).text = "Name: " + studentName
  table.cell(0,1).text = "ID#:"
  table.cell(0,2).text = "School:"

  table = document.add_table(rows=2, cols=2)
  table.cell(0,0).text = "Date of Birth:"
  table.cell(0,1).text = "Last Year Eligible in MCPS:"
  table.cell(1,0).text = "Credits from ISAO? Yes/No"
  table.cell(1,1).text = "Expected Date of Graduation:"

  p = document.add_paragraph()
  add_hyperlink(p, 'http://www.montgomeryschoolsmd.org/curriculum/graduation-requirements.aspx', 'Montgomery County Public Schools Graduation Requirements')
  p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

  credits = [[0 for _ in range(years)] for _ in range(len(chosen))]

  totalCreditsReqd = 0
  table = document.add_table(rows=len(chosen)+4, cols=years+1)
  #  table.style = 'LightShading-Accent1'
  table.cell(0,0).paragraphs[0].add_run("COURSE").bold = True
  for x in range(years):
    table.cell(0, x+1).paragraphs[0].add_run("Year: " + str(startYear + x)).bold = True
  for y, item in enumerate(chosen):
    table.cell(y+1, 0).paragraphs[0].add_run(item[0]).bold = True
    totalCreditsReqd += item[1]
    note = getNote(item)
    table.cell(y+1, 0).paragraphs[0].add_run(note).font.size = docx.shared.Pt(8)
    for x in range(years):
      s1 = item[3][2*x]
      s2 = item[3][2*x+1]
      credits[y][x] += 0.5 * (int(len(s1)>0) + int(len(s2)>0))
      table.cell(y+1, x+1).text = s1 + "\n" + s2
  h = len(chosen)
  table.cell(h+1, 0).paragraphs[0].add_run("SSL Hours: ____").bold = True
  table.cell(h+2, 0).paragraphs[0].add_run("Exams:").bold = True
  table.cell(h+3, 0).paragraphs[0].add_run("Total: {} required".format(totalCreditsReqd)).bold = True
  for x in range(years):
    total = 0
    tmp = "\n"
    for y in range(h):
      total += credits[y][x]
#      tmp+= str(len(table.cell(y, x+1).paragraphs[0].runs[0].text)) + "|"
    table.cell(h+3, x+1).text = "Total Credits: " + str(total)

  document.add_paragraph('* See Course Bulletin specific to each high school for course offerings and details')

  outBasename = "documents/"+urlify(studentName)
  outputFile = outBasename + ".docx"
  i = 0
  while os.path.exists(outputFile):
    i += 1
    outputFile = '{}-{}.docx'.format(outBasename, i)

  document.save(outputFile)
  return outputFile

if action == PRINT:
  try:
    name = form['name'].value
    startYear = int(form['year'].value)
    years = int(form['years'].value)

    selected = []
    for c in classes:
      names = []
      for i in range(years):
        try:
          names.append(form[c[0] + str(i)+'a'].value)
        except:
          names.append("")
        try:
          names.append(form[c[0] + str(i)+'b'].value)
        except:
          names.append("")
      selected.append([c[0], c[1], c[2], names])

    contents = {
    	'name': name,
    	'startYear': startYear,
    	'years': years,
    	'selected': selected
    }
    docFile = generate(contents)
    subprocess.Popen([f('sleep {}; rm {}', DOCUMENT_TIMEOUT+2, docFile)],
      stdout=open('/dev/null', 'w'),
      stderr=open('error.log', 'a'),
      preexec_fn=os.setpgrp,
      shell=True
    )
    print '''<html>
<head>
<meta charset="UTF-8">
<title>Download Page</title>
<script>
setTimeout(function () {
  alert('The document has expired. Press "Export" to re-create it.');
  close();
}, '''+str(DOCUMENT_TIMEOUT*1000)+''');
</script>
</head>
<body>
<h2>Download for "'''+rq(name)+'''"</h2>
<a href="'''+docFile+'''">Click here to download the document.</a><br>
<p>The document will only be available for '''+str(DOCUMENT_TIMEOUT)+''' seconds before it is deleted. Press "Export" again if you need to re-create it.<p>
<button onclick="window.close();">Go Back</button><br>
<br><b>Raw document contents:</b><br>
<div style="border:1px solid">
<pre>'''+cgi.escape(json.dumps(contents, sort_keys=True, indent=4, separators=(',', ': ')))+'''</pre>
</div>
</body>
</html>'''
  except Exception as e:
    print '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Document Error</title>
</head>
<body>
<h2>Error Generating Document</h2>
<button onclick="window.close();">Go Back</button><br><br>
<b>Details:</b><br>
<div style="border:1px solid">
<pre>'''+`e`+'\n' + '\n'.join([tb for tb in traceback.format_tb(sys.exc_info()[2])])+'''</pre>
</div>
</body>
</html>'''

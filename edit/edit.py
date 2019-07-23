#!/usr/bin/python
import cgi, json, time

EXTRA_SLOTS = 15

classesFile = "classes.json"

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

def rq(s):
  return cgi.escape(s).replace("'", "&apos;").replace('"', '&quot;')

def f(s, *args):
  return s.format(*[rq(str(arg)) for arg in args])

form = cgi.FieldStorage()

CATEGORIES = 0
SAVE = 1
SAVE_RETURN = 2
ITEM = 3
DELETE = 4
DELETE_CONFIRM = 5
MOVE_UP = 6
MOVE_DOWN = 7

try:
  action = int(form['action'].value)
except:
  action = CATEGORIES

print '''Content-type: text/html

<!DOCTYPE html>'''

classes = readClasses()

if action == SAVE or action == SAVE_RETURN:
  if action == SAVE_RETURN:
    action = CATEGORIES
  else:
    action = ITEM
  category = None
  catIdx = None
  try:
    catIdx = int(form['category'].value)
    category = classes[catIdx]
  except:
    try:
      catIdx = len(classes)
      if 'cat2' in form:
        cat2 = form['cat2'].value
      else:
        cat2 = ""
      category = [
        form['cat0'].value,
        int(form['cat1'].value),
        cat2,
        []
      ]
      classes.append(category)
    except:
      pass
  if category is not None:
    if 'cat0' in form:
      category[0] = form['cat0'].value
    if 'cat1' in form:
      try:
        category[1] = int(form['cat1'].value)
      except ValueError:
        pass
    if 'cat2' in form:
      category[2] = form['cat2'].value

    #get the class list
    classList = category[3]
    classList = []
    for i in range(int(form['length'].value)):
      checkboxKey = 'c{}'.format(i)
      nameKey = 't{}'.format(i)
      if nameKey in form and not checkboxKey in form:
        name = form[nameKey].value
        classList.append(name)
    category[3] = classList
#    classes[catIdx] = category
    writeClasses(classes)

if action == DELETE:
  try:
    catIdx = int(form['category'].value)
    category = classes[catIdx]
    print '''<html>
<head>
<title>Delete Subject</title>
</head>
<body>
<h2>Delete Subject "'''+category[0]+'''"?</h2>
<form>
<input type="hidden" name="category" value="'''+str(catIdx)+'''">
<button name="action" type="submit" value="'''+str(DELETE_CONFIRM)+'''">Delete</button><br><br>
<button name="action" type="submit" value="'''+str(CATEGORIES)+'''">Cancel</button>
</form>
</body>
</html>'''
  except:
    action = CATEGORIES
if action == DELETE_CONFIRM:
  action = CATEGORIES
  try:
    catIdx = int(form['category'].value)
    del classes[catIdx]
    writeClasses(classes)
  except:
    pass

if action == MOVE_UP or action == MOVE_DOWN:
  direction = 1
  if action == MOVE_UP:
    direction = -1
  action = CATEGORIES
  try:
    a = int(form['category'].value)
    b = a + direction
    if a >= 0 and b >= 0 and a < len(classes) and b < len(classes):
      classes[b], classes[a] = classes[a], classes[b]
      writeClasses(classes)
  except:
    pass

if action == CATEGORIES:
  print '''<html>
<head>
<title>Edit Subjects</title>
<style>
table, th, td {
  border: 1px solid black
}
table {
  cellpadding: 5
}
</style>
</head>
<body>
<h2>Edit Subjects</h2>
<table><thead><tr>
<th>Move Up</th><th>Move Down</th><th>Edit</th><th>Delete</th><th>Subject</th><th>Credits Required</th><th>Classes</th>
</tr></thead><tbody>'''
  for i, cat in enumerate(classes):
    print '<form><tr>'
    print '<th><input type="hidden" name="category" value="'+str(i)+'">'
    print '<input type="hidden" name="time" value="'+str(time.time() * 1000)+'">' #this line is to fixe move up/down
    print '<button name="action" type="submit" value="'+str(MOVE_UP)+'">/\</button></th>'
    print '<th><button name="action" type="submit" value="'+str(MOVE_DOWN)+'">\/</button></th>'
    print '<th><button name="action" type="submit" value="'+str(ITEM)+'">Edit</button></th>'
    print '<th><button name="action" type="submit" value="'+str(DELETE)+'">Delete</button></th>'
    print '<td>'+cat[0]+'</td>'
    print '<td>'+getNote(cat)+'</td>'
    print '<td>'+', '.join(cat[3])+'</td>'
    print '</tr></form>'
  print '''</tbody></table>
<br>
<form>
<input type="hidden" name="category" value="'''+str(len(classes))+'''">
<button name="action" type="submit" value="'''+str(ITEM)+'''">Add New Subject</button>
</form>
<br>
<a href="..">Go Back</a>
</body>
</html>'''

if action == ITEM:
  try:
    catIdx = int(form['category'].value)
  except:
    catIdx = len(classes)
  print """<html>
<head>
<title>Edit Subject</title>
<style>
table, th, td {
  border: 1px solid black
}
table {
  cellpadding: 3
}
</style>
</head>
<body>
<h2>Edit Subject</h2>"""
  try:
    category = classes[catIdx]
  except:
    category = ["New Subject", 1, "", []]
    classes.append(category)
  print """<form>
Subject Name: <input type="text" name="cat0" value='"""+rq(category[0])+"""'><br>
Credits required: <input type="text" name="cat1" value='"""+str(category[1])+"""'><br>
Credits comment: <input type="text" name="cat2" value='"""+rq(category[2])+"""'><br>
<button name="action" type="submit" value='"""+str(SAVE)+"""'>Save</button><br><br>"""
  if len(category[3]) > 0:
    print '<table><thead><tr><th>Delete</th><th>Class Name</th></tr></thead><tbody>'
  for i, c in enumerate(category[3]):
    print '<tr><th><input type="checkbox" name="c'+str(i)+'"></th>'
    print '<td><input type="text" name="t'+str(i)+'" value="'+rq(c)+'"></td></tr>'
  print '''</tbody></table>
<button name="action" type="submit" value="'''+str(SAVE)+'''">Delete Selected</button>
<br><br><b>Add more classes to this subject:</b><br>'''
  for i in range(len(category[3]), len(category[3])+EXTRA_SLOTS):
    print '<input type="text" name="t'+str(i)+'" value=""><br>'
  print """<input type="hidden" name="length" value='"""+str(EXTRA_SLOTS+len(category[3]))+"""'>
<input type="hidden" name="category" value='"""+str(catIdx)+"""'>
<button name="action" type="submit" value='"""+str(SAVE)+"""'>Add</button><br><br>
<button name="action" type="submit" value='"""+str(SAVE_RETURN)+"""'>Save and Quit</button>
</form>
<form>
<input type="submit" value="Discard Changes and Quit">
<input type="hidden" name="action" value='"""+str(CATEGORIES)+"""'>
</form>
</body>
</html>"""

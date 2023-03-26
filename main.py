# k190235 Merub Shaikh

import tkinter as tk
import re
from nltk.stem import PorterStemmer
from collections import OrderedDict

punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
stopwordsdoc = open('Stopword-List.txt', 'r')
stopwords = stopwordsdoc.read()
stopwordslist = stopwords.split()

# Utility function to perform stemming on words
def stemming(word):
  word_stemmer = PorterStemmer()
  return word_stemmer.stem(word)

#Function to find the intersection between documents of words in query
def intersection (word1 , word2, operator):
  mydict = {}
  intersect = set()
  word1 = stemming(word1)                                          # Stem the query word
  if (word2 is None):                                              # Search the documents only if a word is entered
    with open("inverted_index.txt", 'r') as file:                 
      for line in file:
        start = line.split()[0]                                    # Compare only start word of line with query word 
        if start == word1:
         parts = line.strip().split()
         key = parts[0]
         value = list(map(int, parts[1:]))                         # Get the values of the word
         mydict[key] = value                                        
         return value
  else:
    word2 = stemming(word2)                                        # If 2 words find the stem of second word
    with open("inverted_index.txt", 'r') as file:
        for line in file:                                          # Find document list for both the words
            start = line.split()[0]
            if start == word1 or start == word2:
                parts = line.strip().split()
                key = parts[0]
                value = list(map(int, parts[1:]))
                mydict[key] = value
    if (operator.lower() == 'and'):                                    # Compare the operator between the words and perform intersection accordingly
        if word1 in mydict and word2 in mydict:
            intersect = set(mydict[word1]).intersection(mydict[word2])
    elif (operator.lower() == 'or'):
        if word1 in mydict and word2 in mydict:
            intersect = set(mydict[word1]).union(mydict[word2])
        elif (word1 in mydict):
                return set(mydict[word1])
        elif (word2 in mydict):
            return set(mydict[word2])
    return intersect

# Function to cater boolean query received from the UI
def search_booleanquery(query):
  tokens = query.split()                                                  # Tokenizing the received query  
  finalintersect = set()
  x = 0
  if len(tokens) == 1:                                                    # Query to send if one word is received
     finalintersect = intersection(tokens[0],None,'')
  else:
    while x+2 <= len(tokens):                                             # Query to send if more than one word is received
        intersect = intersection(tokens[x], tokens[x+2], tokens[x+1])
        x = x+2
        if (bool(finalintersect)):
            finalintersect = finalintersect.intersection(intersect)        # Intersection of intermediate results with new result
        else:
            finalintersect = intersect
  return finalintersect

# Utility function to remove duplicates from inverted index document list
def remove_duplicates(docs):
   for i in range(0,len(docs)):
      docs[i] = list(set(docs[i]))
   return docs

# Function to cater proximity query received from the UI            
def search_proximityquery(query , k):
  query = query.split()                                                      # Tokenize the query received
  fresult = []
  fdocs = []
  for i in range(0,len(query)):                                              # Perform stemming on each query word 
     query[i] = stemming(query[i])
  with open("positional_index.txt", 'r') as file:
    for line in file:                                                        # Find positional listing of all the words in the query
        start = line.split()[0]
        if start in query:
         list_strings = re.findall(r'\[(.*?)\]', line)
         result = []
         for lst in list_strings:
           int_list = [int(num) for num in lst.split(', ')]
           result.append(int_list)
         fresult.append(result)
  with open("inverted_index.txt", "r") as file:                             # Find document list of all the words in query
     for line in file:
        start = line.split()[0]
        if start in query:
           int_list = [int(s) for s in line.split() if s.isdigit()]
           fdocs.append(int_list)
  fdocs = remove_duplicates(fdocs)                                            # Remove duplicates from document list
  intersect = []
  for i in range(0,len(fdocs),2):                                             # Find the intersecting documents along with positions that are <= k
     p1 = 0
     p2 = 0
     while p1 < len(fdocs[0])  and p2 < len(fdocs[1]) :
        if fdocs[0][p1] == fdocs[1][p2]:
           positional1 = fresult[0][p1]
           positional2 = fresult[1][p2]
           j1 = 0
           j2 = 0
           while j1 < len(positional1) and j2 < len(positional2):
              diff = positional1[j1] - positional2[j2]
              if diff < 0 :
                 diff = diff * -1
              if diff <= k:
                 intersect.append(fdocs[0][p1])
                 j1 += 1
                 j2 += 1
              elif positional1[j1] < positional2[j2]:
                 j1 += 1
              else:
                 j2 += 1
           p1 += 1
           p2 += 1
        elif fdocs[0][p1] < fdocs[1][p2]:
           p1 += 1
        else:
           p2 += 1
  intersect = list(set(intersect))                                                        # Remove duplicate documents
  return intersect

  

# Utility function to remove stopwords from the list of words
def remove_elements (currlist , wordstoremove):
  newlist = []
  currlist = set(currlist)
  wordstoremove = set(wordstoremove) 
  newlist = currlist - wordstoremove
  newlist = list(newlist)
  return newlist

#Utility function to remove punctuation
def remove_punctuation (puntuation, text):
   no_punct = ""
   for char in text:
      if char not in punctuation:
        no_punct = no_punct + char
   return no_punct

# Utility function to remove encoding issues , tokenize , strip and split the words in the document befire indexing
def preprocessing(text):
  text = text.replace('/', ' ')
  text = text.replace('•', ' ')
  text = text.replace('&nbsp', ' ')
  text = text.replace('&bull', ' ')
  text = text.lower()
  text = remove_punctuation(punctuation,text)
  words = text.split()
  words = [word.strip('.,!;()[]/') for word in words]
  words = [word.replace("'s", '') for word in words]
  words = numeric_char_normalization(words)
  words = remove_elements(words,stopwordslist)
  return words

# Utility function to seperate and tokenize alphanumeric words before indexing
def numeric_char_normalization (text):
  res = []
  temp = []
  for idx in text:
    if any(chr.isalpha() for chr in idx) and any(chr.isdigit() for chr in idx):
        res.append(idx)
        temp.append(re.split('(\d+)', idx))
  text = remove_elements(text,res)
  for row in range(len(temp)):
    for col in range(len(temp[row])):
      if temp[row][col].isnumeric():
        text.append(temp[row][col])
      elif temp[row][col].isalpha() and len(temp[row][col]) > 1:
        text.append(temp[row][col])
  return text

# Utility function to find all the indexes on which the word occurs for positional indexing
def find_positions(contents):
   mydict = {}
   for word in contents:
    indexes = []
    if word in mydict:
       continue
    else:
        for i in range(len(contents)):
            if contents[i] == word:
              indexes.append(i+1)
        word = stemming(word)
        mydict[word]= [indexes]
   return mydict

# Function to create positional index
def create_positional_index(nofiles):
  count = 1
  mydict = {}
  for files in range(0,nofiles):
    filename = r'C:\Users\Merub Shaikh\Desktop\IR assignment\Dataset\{}.txt'.format(count)
    docfile = open(filename, 'r')
    contents = docfile.read()
    contents = contents.replace('/', ' ')
    contents = contents.replace('•', ' ')
    contents = contents.replace('&nbsp', ' ')
    contents = contents.replace('&bull', ' ')
    contents = contents.lower()
    contents = contents.split()
    contents = [word.strip('.,:!;()[]@-*/"') for word in contents]
    temp_dict = find_positions(contents)
    for key, value in temp_dict.items():                                      # To combine new dictionary words with the main dictionary
      mydict.setdefault(key, []).extend(value)
    count =  count + 1
    dict1 = OrderedDict(sorted(mydict.items()))                               # Order dictionary before writing to file
    with open('positional_index.txt', 'w') as f:                              # Write to file named positional_index.txt
      for key, value in dict1.items(): 
            line = key + ' ' + ' '.join(map(str, value)) + '\n'
            f.write(line)


# Function to create inverted index (same as positional indexing)
def create_inverted_index (nofiles):
  count = 1
  mydict = {}
  for files in range (0,nofiles):
    filename = r'C:\Users\Merub Shaikh\Desktop\IR assignment\Dataset\{}.txt'.format(count)
    docfile = open(filename, 'r')
    words = docfile.read()
    words = preprocessing(words)
    for word in words:
      word = stemming(word)
      if word in mydict:
        mydict[word].append(count)
      else:
        mydict.setdefault(word,[])
        mydict[word].append(count)
    count = count + 1

  dict1 = OrderedDict(sorted(mydict.items()))
  with open('inverted_index.txt', 'w') as f:                                      # Write to file name inverted_index.txt
      for key, value in dict1.items(): 
           line = key + ' ' + ' '.join(map(str, value)) + '\n'
           f.write(line)

create_inverted_index(30)                                      # Call to functions to create inverted and positional index
create_positional_index(30)

#Function to trigger boolean query when button is clicked
def get_bquery():
    listbox.delete(0, tk.END)
    text = textbox.get() 
    filename = search_booleanquery(text)
    writetolist(filename)
    
# Function to trigger proximity query when button is clicked
def get_pquery():
  text = textbox2.get()
  text = text.split("/")
  filename = search_proximityquery(text[0] , int(text[1]))
  writetolist(filename)

# Function to write name of files in the listbox when result is received
def writetolist(text):
    if text:
        for x in text:
            listbox.insert(tk.END, "   " + str(x) + ".txt")
    else:
      listbox.insert(tk.END, "No document" )
  
# GUI code (uses Tkinter)
root = tk.Tk()
width = 600
height = 300
root.geometry(f"{width}x{height}")
root.title("Boolean Retrieval Model")
root.configure(bg="#DB804E")

label = tk.Label(root, text=" Boolean Query:" , bg="#DB804E" , font=("Arial", 11, "bold"), fg="white")
textbox = tk.Entry(root , width='30')
button = tk.Button(root, text="Search" ,  bg="#4EA9DB" , font=("Arial", 10, "bold"), fg="white" , command=get_bquery)
label3 = tk.Label(root, text=" Proximity Query:" , bg="#DB804E" , font=("Arial", 11, "bold"), fg="white")
textbox2 = tk.Entry(root , width='30')
button2 = tk.Button(root, text="Search" ,  bg="#4EA9DB" , font=("Arial", 10, "bold"), fg="white" , command=get_pquery)
label2 = tk.Label(root , text="Results" , bg="#DB804E" , font=("Arial", 11, "bold"), fg="white")
listbox = tk.Listbox(root , width='50'  ,  bg="#4EA9DB" , font=("Arial", 8), fg="white")

label.grid(row=0, column=1 , pady=5)
textbox.grid(row=0, column=2 , padx=5 , pady=5)
button.grid(row=0 , column =3 , padx=5 )
label3.grid(row=1, column=1 , pady=5)
textbox2.grid(row=1, column=2 , pady=5)
button2.grid(row=1 , column =3  )
label2.grid(row=2 ,column=1 , padx=10 )
listbox.grid (row=2, column=2 , padx=10 , pady=20)
root.mainloop()
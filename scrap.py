import requests                             # requests to get the data from url
from bs4 import BeautifulSoup               # beautifulsoup to get accessing the content in html
import mysql.connector                      # importing mysql connector

# getting the user name and password and database name
user = input("user name: ")
password = input("password: ")
database = input("database name: ")
# actual connection

mydb = mysql.connector.connect(host="localhost", user=user, password=password, database=database)
#cursor.execute("CREATE TABLE web_scrap_data (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), title_link VARCHAR(255), pdf_links VARCHAR(1000))")
# at initially we have to create a database for inserting data un comment this for the first time


cursor = mydb.cursor()
URL = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&s"
r = requests.get(URL)
soup = BeautifulSoup(r.content, 'html.parser')

o = {}    # to store the values in the dictionary with the title followed by links

print("started scrapping the links...")

table = soup.find_all('a')

for i in table:
    a = str(i.get('href'))
    if 'https://www.sebi.gov.in/filings/' in a:
        b = str(i.get('title'))
        o[b] = [a]

print("started scrapping the innner links..")

for i in o.values():
    last = []
    link = requests.get(i[0])
    link = BeautifulSoup(link.content, 'html.parser')
    soup1 = link.find('iframe')
    if soup1:
        link1 = str(soup1.get('src'))
        if "https" in link1:
            last.append(link1[link1.index("https"):])
    else:
        for j in link.find_all('a'):
            if "https://www.sebi.gov.in/sebi_data/" in str(j):
                fin = str(j.get('href')).strip()
                fin = fin.replace(" ", "%20")         # to fill the white space in the collected links
                last.append(fin)
    i.append(last)

# changing data into tuples for insert it into db

final = []

for k, l in o.items():
    final.append(tuple([k, l[0], l[1][0]]))
    for i in range(1, len(l[1])):
        final.append(tuple([k, "", l[1][1]]))


# inserting data int data base...

print("started inserting data...")

cnt = len(final) # for counting the datas

for i in final:
    sql = "INSERT INTO web_scrap_data (title, title_link, pdf_links) VALUES (%s, %s, %s)"
    val = i
    cursor.execute(sql, val)
    #print(cursor.lastrowid) # uncomment this to check whether the data is added or not

print("inserted datacount:", cnt)

mydb.commit() # commiting the database

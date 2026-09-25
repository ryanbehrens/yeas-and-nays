# Political backbone: presidents, statehood, elections (pre-1900 & 2016+), min wage, state min wage
PRESIDENTS = [
 # name, party, start, end
 ("George Washington","Unaffiliated (Federalist-aligned)","1789-04-30","1797-03-04"),
 ("John Adams","Federalist","1797-03-04","1801-03-04"),
 ("Thomas Jefferson","Democratic-Republican","1801-03-04","1809-03-04"),
 ("James Madison","Democratic-Republican","1809-03-04","1817-03-04"),
 ("James Monroe","Democratic-Republican","1817-03-04","1825-03-04"),
 ("John Quincy Adams","Democratic-Republican / National Republican","1825-03-04","1829-03-04"),
 ("Andrew Jackson","Democratic","1829-03-04","1837-03-04"),
 ("Martin Van Buren","Democratic","1837-03-04","1841-03-04"),
 ("William Henry Harrison","Whig","1841-03-04","1841-04-04"),
 ("John Tyler","Whig (expelled) / Unaffiliated","1841-04-04","1845-03-04"),
 ("James K. Polk","Democratic","1845-03-04","1849-03-04"),
 ("Zachary Taylor","Whig","1849-03-04","1850-07-09"),
 ("Millard Fillmore","Whig","1850-07-09","1853-03-04"),
 ("Franklin Pierce","Democratic","1853-03-04","1857-03-04"),
 ("James Buchanan","Democratic","1857-03-04","1861-03-04"),
 ("Abraham Lincoln","Republican","1861-03-04","1865-04-15"),
 ("Andrew Johnson","National Union / Democratic","1865-04-15","1869-03-04"),
 ("Ulysses S. Grant","Republican","1869-03-04","1877-03-04"),
 ("Rutherford B. Hayes","Republican","1877-03-04","1881-03-04"),
 ("James A. Garfield","Republican","1881-03-04","1881-09-19"),
 ("Chester A. Arthur","Republican","1881-09-19","1885-03-04"),
 ("Grover Cleveland","Democratic","1885-03-04","1889-03-04"),
 ("Benjamin Harrison","Republican","1889-03-04","1893-03-04"),
 ("Grover Cleveland","Democratic","1893-03-04","1897-03-04"),
 ("William McKinley","Republican","1897-03-04","1901-09-14"),
 ("Theodore Roosevelt","Republican","1901-09-14","1909-03-04"),
 ("William Howard Taft","Republican","1909-03-04","1913-03-04"),
 ("Woodrow Wilson","Democratic","1913-03-04","1921-03-04"),
 ("Warren G. Harding","Republican","1921-03-04","1923-08-02"),
 ("Calvin Coolidge","Republican","1923-08-02","1929-03-04"),
 ("Herbert Hoover","Republican","1929-03-04","1933-03-04"),
 ("Franklin D. Roosevelt","Democratic","1933-03-04","1945-04-12"),
 ("Harry S. Truman","Democratic","1945-04-12","1953-01-20"),
 ("Dwight D. Eisenhower","Republican","1953-01-20","1961-01-20"),
 ("John F. Kennedy","Democratic","1961-01-20","1963-11-22"),
 ("Lyndon B. Johnson","Democratic","1963-11-22","1969-01-20"),
 ("Richard Nixon","Republican","1969-01-20","1974-08-09"),
 ("Gerald Ford","Republican","1974-08-09","1977-01-20"),
 ("Jimmy Carter","Democratic","1977-01-20","1981-01-20"),
 ("Ronald Reagan","Republican","1981-01-20","1989-01-20"),
 ("George H. W. Bush","Republican","1989-01-20","1993-01-20"),
 ("Bill Clinton","Democratic","1993-01-20","2001-01-20"),
 ("George W. Bush","Republican","2001-01-20","2009-01-20"),
 ("Barack Obama","Democratic","2009-01-20","2017-01-20"),
 ("Donald Trump","Republican","2017-01-20","2021-01-20"),
 ("Joe Biden","Democratic","2021-01-20","2025-01-20"),
 ("Donald Trump","Republican","2025-01-20",None),
]

NAMES = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}

FIPS = {"01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI","56":"WY"}

# Date each state ratified the Constitution / was admitted
STATEHOOD = {"DE":"1787-12-07","PA":"1787-12-12","NJ":"1787-12-18","GA":"1788-01-02","CT":"1788-01-09","MA":"1788-02-06","MD":"1788-04-28","SC":"1788-05-23","NH":"1788-06-21","VA":"1788-06-25","NY":"1788-07-26","NC":"1789-11-21","RI":"1790-05-29","VT":"1791-03-04","KY":"1792-06-01","TN":"1796-06-01","OH":"1803-03-01","LA":"1812-04-30","IN":"1816-12-11","MS":"1817-12-10","IL":"1818-12-03","AL":"1819-12-14","ME":"1820-03-15","MO":"1821-08-10","AR":"1836-06-15","MI":"1837-01-26","FL":"1845-03-03","TX":"1845-12-29","IA":"1846-12-28","WI":"1848-05-29","CA":"1850-09-09","MN":"1858-05-11","OR":"1859-02-14","KS":"1861-01-29","WV":"1863-06-20","NV":"1864-10-31","NE":"1867-03-01","CO":"1876-08-01","ND":"1889-11-02","SD":"1889-11-02","MT":"1889-11-08","WA":"1889-11-11","ID":"1890-07-03","WY":"1890-07-10","UT":"1896-01-04","OK":"1907-11-16","NM":"1912-01-06","AZ":"1912-02-14","AK":"1959-01-03","HI":"1959-08-21"}
ORIGINAL13 = ["DE","PA","NJ","GA","CT","MA","MD","SC","NH","VA","NY","NC","RI"]

# Pre-1900 elections, compiled state-by-state (winner of the state's electoral votes / majority of them).
# Party keys: IND=Washington (unopposed), F, DR, JAX/ADAMS/CRAW/CLAY (1824 factions), NR, D, W, AM, NUL (Nullifier),
# R, KN, SD (Southern Democrat), CU, POP, SPLIT (evenly split), NV (did not vote), DISP (votes disputed/rejected)
def s(txt):
    return txt.split()
PRE1900 = {
 1789: {"IND": s("CT DE GA MD MA NH NJ PA SC VA")},
 1792: {"IND": s("CT DE GA KY MD MA NH NJ NY NC PA RI SC VT VA")},
 1796: {"F": s("CT DE MD MA NH NJ NY RI VT"), "DR": s("GA KY NC PA SC TN VA")},
 1800: {"DR": s("GA KY NY NC PA SC TN VA"), "F": s("CT DE MA NH NJ RI VT"), "SPLIT": s("MD")},
 1804: {"DR": s("GA KY MD MA NH NJ NY NC OH PA RI SC TN VT VA"), "F": s("CT DE")},
 1808: {"DR": s("GA KY MD NJ NY NC OH PA SC TN VT VA"), "F": s("CT DE MA NH RI")},
 1812: {"DR": s("GA KY LA MD NC OH PA SC TN VT VA"), "F": s("CT DE MA NH NJ NY RI")},
 1816: {"DR": s("GA IN KY LA MD NH NJ NY NC OH PA RI SC TN VT VA"), "F": s("CT DE MA")},
 1820: {"DR": s("AL CT DE GA IL IN KY LA ME MD MA MS MO NH NJ NY NC OH PA RI SC TN VT VA")},
 1824: {"JAX": s("AL IL IN LA MD MS NJ NC PA SC TN"), "ADAMS": s("CT ME MA NH NY RI VT"), "CRAW": s("DE GA VA"), "CLAY": s("KY MO OH")},
 1828: {"D": s("AL GA IL IN KY LA MS MO NY NC OH PA SC TN VA"), "NR": s("CT DE ME MD MA NH NJ RI VT")},
 1832: {"D": s("AL GA IL IN LA ME MS MO NH NJ NY NC OH PA TN VA"), "NR": s("CT DE KY MD MA RI"), "AM": s("VT"), "NUL": s("SC")},
 1836: {"D": s("AL AR CT IL LA ME MI MS MO NH NY NC PA RI VA"), "W": s("DE GA IN KY MD MA NJ OH TN VT"), "NUL": s("SC")},
 1840: {"W": s("CT DE GA IN KY LA ME MD MA MI MS NJ NY NC OH PA RI TN VT"), "D": s("AL AR IL MO NH SC VA")},
 1844: {"D": s("AL AR GA IL IN LA ME MI MS MO NH NY PA SC VA"), "W": s("CT DE KY MD MA NJ NC OH RI TN VT")},
 1848: {"W": s("CT DE FL GA KY LA MD MA NJ NY NC PA RI TN VT"), "D": s("AL AR IL IN IA ME MI MS MO NH OH SC TX VA WI")},
 1852: {"D": s("AL AR CA CT DE FL GA IL IN IA LA ME MD MI MS MO NH NJ NY NC OH PA RI SC TX VA WI"), "W": s("KY MA TN VT")},
 1856: {"D": s("AL AR CA DE FL GA IL IN KY LA MS MO NJ NC PA SC TN TX VA"), "R": s("CT IA ME MA MI NH NY OH RI VT WI"), "KN": s("MD")},
 1860: {"R": s("CA CT IL IN IA ME MA MI MN NH NJ NY OH OR PA RI VT WI"), "SD": s("AL AR DE FL GA LA MD MS NC SC TX"), "CU": s("KY TN VA"), "D": s("MO")},
 1864: {"R": s("CA CT IL IN IA KS ME MD MA MI MN MO NV NH NY OH OR PA RI VT WV WI"), "D": s("DE KY NJ"), "NV": s("AL AR FL GA LA MS NC SC TN TX VA")},
 1868: {"R": s("AL AR CA CT FL IL IN IA KS ME MA MI MN MO NE NV NH NC OH PA RI SC TN VT WV WI"), "D": s("DE GA KY LA MD NJ NY OR"), "NV": s("MS TX VA")},
 1872: {"R": s("AL CA CT DE FL IL IN IA KS ME MA MI MN MS NE NV NH NJ NY NC OH OR PA RI SC VT VA WV WI"), "D": s("GA KY MD MO TN TX"), "DISP": s("AR LA")},
 1876: {"R": s("CA CO FL IL IA KS LA ME MA MI MN NE NV NH OH OR PA RI SC VT WI"), "D": s("AL AR CT DE GA IN KY MD MS MO NJ NY NC TN TX VA WV")},
 1880: {"R": s("CO CT IL IN IA KS ME MA MI MN NE NH NY OH OR PA RI VT WI"), "D": s("AL AR CA DE FL GA KY LA MD MS MO NV NJ NC SC TN TX VA WV")},
 1884: {"D": s("AL AR CT DE FL GA IN KY LA MD MS MO NJ NY NC SC TN TX VA WV"), "R": s("CA CO IL IA KS ME MA MI MN NE NV NH OH OR PA RI VT WI")},
 1888: {"R": s("CA CO IL IN IA KS ME MA MI MN NE NV NH NY OH OR PA RI VT WI"), "D": s("AL AR CT DE FL GA KY LA MD MS MO NJ NC SC TN TX VA WV")},
 1892: {"D": s("AL AR CA CT DE FL GA IL IN KY LA MD MS MO NJ NY NC SC TN TX VA WV WI"), "POP": s("CO ID KS NV"), "SPLIT": s("ND"), "R": s("IA ME MA MI MN MT NE NH OH OR PA RI SD VT WA WY")},
 1896: {"R": s("CA CT DE IL IN IA KY ME MD MA MI MN NH NJ NY ND OH OR PA RI VT WV WI"), "D": s("AL AR CO FL GA ID KS LA MS MO MT NE NV NC SC SD TN TX UT VA WA WY")},
}
_DEM16 = s("CA CO CT DE DC HI IL ME MD MA MN NV NH NJ NM NY OR RI VT VA WA")
_REP16 = s("AL AK AZ AR FL GA ID IN IA KS KY LA MI MS MO MT NE NC ND OH OK PA SC SD TN TX UT WV WI WY")
_flip20 = s("AZ GA MI PA WI")
_flip24 = s("AZ GA MI NV PA WI")
_DEM20 = _DEM16 + _flip20
_REP20 = [x for x in _REP16 if x not in _flip20]
POST2012 = {
 2016: {"D": _DEM16, "R": _REP16},
 2020: {"D": _DEM20, "R": _REP20},
 2024: {"D": [x for x in _DEM20 if x not in _flip24], "R": _REP20 + _flip24},
}
# Winning candidates by election year (national winner)
WINNERS = {1789:"George Washington",1792:"George Washington",1796:"John Adams",1800:"Thomas Jefferson",1804:"Thomas Jefferson",1808:"James Madison",1812:"James Madison",1816:"James Monroe",1820:"James Monroe",1824:"John Quincy Adams (chosen by the House)",1828:"Andrew Jackson",1832:"Andrew Jackson",1836:"Martin Van Buren",1840:"William Henry Harrison",1844:"James K. Polk",1848:"Zachary Taylor",1852:"Franklin Pierce",1856:"James Buchanan",1860:"Abraham Lincoln",1864:"Abraham Lincoln",1868:"Ulysses S. Grant",1872:"Ulysses S. Grant",1876:"Rutherford B. Hayes",1880:"James A. Garfield",1884:"Grover Cleveland",1888:"Benjamin Harrison",1892:"Grover Cleveland",1896:"William McKinley",1900:"William McKinley",1904:"Theodore Roosevelt",1908:"William Howard Taft",1912:"Woodrow Wilson",1916:"Woodrow Wilson",1920:"Warren G. Harding",1924:"Calvin Coolidge",1928:"Herbert Hoover",1932:"Franklin D. Roosevelt",1936:"Franklin D. Roosevelt",1940:"Franklin D. Roosevelt",1944:"Franklin D. Roosevelt",1948:"Harry S. Truman",1952:"Dwight D. Eisenhower",1956:"Dwight D. Eisenhower",1960:"John F. Kennedy",1964:"Lyndon B. Johnson",1968:"Richard Nixon",1972:"Richard Nixon",1976:"Jimmy Carter",1980:"Ronald Reagan",1984:"Ronald Reagan",1988:"George H. W. Bush",1992:"Bill Clinton",1996:"Bill Clinton",2000:"George W. Bush",2004:"George W. Bush",2008:"Barack Obama",2012:"Barack Obama",2016:"Donald Trump",2020:"Joe Biden",2024:"Donald Trump"}

PARTIES = {
 "IND":{"name":"Washington (no party)","color":"#8a8f98"},
 "F":{"name":"Federalist","color":"#c9a227"},
 "DR":{"name":"Democratic-Republican","color":"#2f9e8f"},
 "JAX":{"name":"Jackson (Dem.-Rep. faction)","color":"#3b6fd8"},
 "ADAMS":{"name":"J.Q. Adams (Dem.-Rep. faction)","color":"#c9a227"},
 "CRAW":{"name":"Crawford (Dem.-Rep. faction)","color":"#2f9e8f"},
 "CLAY":{"name":"Clay (Dem.-Rep. faction)","color":"#9b6bd3"},
 "NR":{"name":"National Republican","color":"#d4803a"},
 "D":{"name":"Democratic","color":"#2e62d9"},
 "W":{"name":"Whig","color":"#e0a33a"},
 "AM":{"name":"Anti-Masonic","color":"#9b6bd3"},
 "NUL":{"name":"Nullifier / independent","color":"#7a7f88"},
 "R":{"name":"Republican","color":"#d63a3a"},
 "KN":{"name":"Know-Nothing (American)","color":"#b08f5a"},
 "SD":{"name":"Southern Democrat","color":"#6d8fd6"},
 "CU":{"name":"Constitutional Union","color":"#3fa66b"},
 "POP":{"name":"Populist","color":"#3fa66b"},
 "P":{"name":"Progressive (Bull Moose)","color":"#3fa66b"},
 "SR":{"name":"States' Rights / Dixiecrat","color":"#8c7a5b"},
 "AI":{"name":"American Independent (Wallace)","color":"#8c7a5b"},
 "UNP":{"name":"Unpledged electors","color":"#7a7f88"},
 "SPLIT":{"name":"Electoral votes split","color":"#a7a9ae"},
 "NV":{"name":"Did not vote (seceded)","color":"#55504a"},
 "DISP":{"name":"Votes rejected by Congress","color":"#a7a9ae"},
}

FED_MINWAGE = [ # effective date, rate
 ("1938-10-24",0.25),("1939-10-24",0.30),("1945-10-24",0.40),("1950-01-25",0.75),("1956-03-01",1.00),
 ("1961-09-03",1.15),("1963-09-03",1.25),("1967-02-01",1.40),("1968-02-01",1.60),("1974-05-01",2.00),
 ("1975-01-01",2.10),("1976-01-01",2.30),("1978-01-01",2.65),("1979-01-01",2.90),("1980-01-01",3.10),
 ("1981-01-01",3.35),("1990-04-01",3.80),("1991-04-01",4.25),("1996-10-01",4.75),("1997-09-01",5.15),
 ("2007-07-24",5.85),("2008-07-24",6.55),("2009-07-24",7.25)]

# U.S. Dept. of Labor, basic state minimum wage as of July 1, 2026 (None = no state law above federal; federal $7.25 applies)
STATE_MINWAGE_2026 = {"AL":None,"AK":14.00,"AZ":15.15,"AR":11.00,"CA":16.90,"CO":15.16,"CT":16.94,"DE":15.00,"DC":18.40,"FL":14.00,"GA":7.25,"HI":16.00,"ID":7.25,"IL":15.00,"IN":7.25,"IA":7.25,"KS":7.25,"KY":7.25,"LA":None,"ME":15.10,"MD":15.00,"MA":15.00,"MI":13.73,"MN":11.41,"MS":None,"MO":15.00,"MT":10.85,"NE":15.00,"NV":12.00,"NH":7.25,"NJ":15.92,"NM":12.00,"NY":16.00,"NC":7.25,"ND":7.25,"OH":11.00,"OK":7.25,"OR":15.55,"PA":7.25,"RI":16.00,"SC":None,"SD":11.85,"TN":None,"TX":7.25,"UT":7.25,"VT":14.42,"VA":12.77,"WA":17.13,"WV":8.75,"WI":7.25,"WY":7.25}
STATE_MINWAGE_NOTES = {"GA":"State rate is $5.15; federal $7.25 applies to most workers","WY":"State rate is $5.15; federal $7.25 applies to most workers","NY":"$17.00 in NYC, Long Island & Westchester; $16.00 elsewhere","OR":"$16.80 Portland metro; $15.55 standard; $14.55 non-urban","OH":"$11.00 for larger employers","MI":"Scheduled to rise to $15.00 on Jan 1, 2027","DC":"Adjusted each July 1"}

HOUSE = """1|Pro-Administration|37-28
2|Pro-Administration|39-30
3|Anti-Administration|54-51
4|Democratic-Republican|59-47
5|Federalist|57-49
6|Federalist|60-46
7|Democratic-Republican|68-38
8|Democratic-Republican|103-39
9|Democratic-Republican|114-28
10|Democratic-Republican|116-26
11|Democratic-Republican|92-50
12|Democratic-Republican|107-36
13|Democratic-Republican|114-68
14|Democratic-Republican|119-64
15|Democratic-Republican|146-39
16|Democratic-Republican|160-26
17|Democratic-Republican|155-32
18|Adams-Clay Republican|72-64
19|Adams|109-104
20|Jacksonian|113-100
21|Jacksonian|136-72
22|Jacksonian|126-66
23|Jacksonian|143-63
24|Jacksonian|143-75
25|Democratic|128-100
26|Democratic|125-109
27|Whig|142-98
28|Democratic|147-72
29|Democratic|142-79
30|Whig|116-110
31|Democratic|113-108
32|Democratic|127-85
33|Democratic|157-71
34|Opposition|100-83
35|Democratic|132-90
36|Republican|116-83
37|Republican|108-44
38|Republican|85-72
39|Republican|136-38
40|Republican|173-47
41|Republican|171-67
42|Republican|136-104
43|Republican|199-88
44|Democratic|182-103
45|Democratic|155-136
46|Democratic|141-132
47|Republican|151-128
48|Democratic|196-117
49|Democratic|182-141
50|Democratic|167-152
51|Republican|179-152
52|Democratic|238-86
53|Democratic|218-124
54|Republican|254-93
55|Republican|206-124
56|Republican|187-161
57|Republican|200-151
58|Republican|207-176
59|Republican|251-135
60|Republican|223-167
61|Republican|219-172
62|Democratic|230-162
63|Democratic|291-134
64|Democratic|230-196
65|Republican|215-214
66|Republican|240-192
67|Republican|302-132
68|Republican|225-207
69|Republican|247-183
70|Republican|238-194
71|Republican|270-164
72|Republican|218-216
73|Democratic|313-117
74|Democratic|322-103
75|Democratic|334-88
76|Democratic|262-169
77|Democratic|267-162
78|Democratic|222-209
79|Democratic|244-189
80|Republican|246-188
81|Democratic|263-171
82|Democratic|235-199
83|Republican|221-213
84|Democratic|232-203
85|Democratic|232-203
86|Democratic|282-153
87|Democratic|264-173
88|Democratic|258-176
89|Democratic|295-140
90|Democratic|248-187
91|Democratic|243-192
92|Democratic|255-180
93|Democratic|243-192
94|Democratic|291-144
95|Democratic|292-143
96|Democratic|278-157
97|Democratic|243-192
98|Democratic|269-166
99|Democratic|254-181
100|Democratic|258-177
101|Democratic|260-175
102|Democratic|267-167
103|Democratic|258-176
104|Republican|230-204
105|Republican|226-207
106|Republican|223-211
107|Republican|221-212
108|Republican|229-205
109|Republican|232-202
110|Democratic|233-202
111|Democratic|257-178
112|Republican|242-193
113|Republican|234-201
114|Republican|247-188
115|Republican|241-194
116|Democratic|235-199
117|Democratic|222-213
118|Republican|222-213
119|Republican|220-215"""
SENATE = """1|Pro-Administration|18-8
2|Pro-Administration|16-13
3|Pro-Administration|16-14
4|Federalist|21-11
5|Federalist|22-10
6|Federalist|22-10
7|Democratic-Republican|17-15
8|Democratic-Republican|25-9
9|Democratic-Republican|27-7
10|Democratic-Republican|28-6
11|Democratic-Republican|27-7
12|Democratic-Republican|30-6
13|Democratic-Republican|28-8
14|Democratic-Republican|26-12
15|Democratic-Republican|30-12
16|Democratic-Republican|37-9
17|Democratic-Republican|44-4
18|Jackson & Crawford Republican|31-17
19|Jacksonian|26-22
20|Jacksonian|27-21
21|Jacksonian|25-23
22|Jacksonian|24-22
23|Anti-Jackson|26-20
24|Jacksonian|26-24
25|Democratic|35-17
26|Democratic|30-22
27|Whig|29-22
28|Whig|29-23
29|Democratic|34-22
30|Democratic|38-21
31|Democratic|35-25
32|Democratic|36-23
33|Democratic|38-22
34|Democratic|39-21
35|Democratic|41-20
36|Democratic|38-26
37|Republican|31-15
38|Republican|33-10
39|Republican|39-11
40|Republican|57-9
41|Republican|62-12
42|Republican|56-17
43|Republican|47-19
44|Republican|46-28
45|Republican|40-35
46|Democratic|42-33
47|Republican|37-37
48|Republican|38-36
49|Republican|42-34
50|Republican|39-37
51|Republican|51-37
52|Republican|47-39
53|Democratic|44-40
54|Republican|44-40
55|Republican|44-34
56|Republican|53-26
57|Republican|56-32
58|Republican|57-33
59|Republican|58-32
60|Republican|61-31
61|Republican|60-32
62|Republican|52-44
63|Democratic|51-44
64|Democratic|56-40
65|Democratic|54-42
66|Republican|49-47
67|Republican|59-37
68|Republican|53-42
69|Republican|54-41
70|Republican|48-46
71|Republican|56-39
72|Republican|48-47
73|Democratic|59-36
74|Democratic|69-25
75|Democratic|76-16
76|Democratic|69-23
77|Democratic|66-28
78|Democratic|57-38
79|Democratic|57-38
80|Republican|51-45
81|Democratic|54-42
82|Democratic|49-47
83|Republican|48-47
84|Democratic|48-47
85|Democratic|49-47
86|Democratic|65-35
87|Democratic|64-36
88|Democratic|66-34
89|Democratic|68-32
90|Democratic|64-36
91|Democratic|57-43
92|Democratic|54-44
93|Democratic|56-42
94|Democratic|61-37
95|Democratic|61-38
96|Democratic|58-41
97|Republican|53-46
98|Republican|55-45
99|Republican|53-47
100|Democratic|55-45
101|Democratic|55-45
102|Democratic|56-44
103|Democratic|57-43
104|Republican|52-48
105|Republican|55-45
106|Republican|55-45
107|Shifted (50-50, then Democratic)|50-50
108|Republican|51-48
109|Republican|55-44
110|Democratic (with independents)|51-49
111|Democratic|57-41
112|Democratic|51-47
113|Democratic|53-45
114|Republican|54-44
115|Republican|51-47
116|Republican|53-45
117|Democratic (VP tie-break)|50-50
118|Democratic (with independents)|51-49
119|Republican|53-47"""

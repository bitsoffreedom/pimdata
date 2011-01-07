import json
import os
import sys
import sqlite3

def insert_doelen(melding_id, doelen, cursor):
	for doel in doelen:
		cursor.execute("INSERT INTO web_doel (melding_id, naam) " \
				" VALUES (?, ?)", (melding_id, doel))

def insert_verantwoordelijken(melding_id, verantwoordelijken, cursor):
	for verantwoordelijke in verantwoordelijken:
		naam = None
		bezoekadres = None
		postadres = None
		for key, value in verantwoordelijke.iteritems():
			if key == "Naam":
				if naam != None:
					raise Exception("Field Naam found twice")
				naam = value
			elif key == "Bezoekadres":
				if bezoekadres != None:
					raise Exception("Field Bezoekadres found twice")
				bezoekadres = value
			elif key == "Postadres":
				if postadres != None:
					raise Exception("Field Postadres found twice")
				postadres = value
			else:
				raise Exception('Unknown field found');
        cursor.execute("INSERT INTO company_part2 (bezoekadres, naam, " \
                        "postadres) VALUES (?, ?, ?)", ( bezoekadres, naam,
                        postadres))

def insert_ontvangers(melding_id, ontvangers, cursor):
	for ontvanger in ontvangers:
		cursor.execute("INSERT INTO web_ontvanger (melding_id, naam) " \
				" VALUES (?, ?)", (melding_id, ontvanger));

def insert_betrokkene_data(betrokkene_id, betrokkene, cursor):
	for name, value in betrokkene.iteritems():
		cursor.execute("INSERT INTO web_betrokkenedata (betrokkene_id," \
				"name, value) VALUES (?, ?, ?)", (betrokkene_id,
				name, value))

def insert_betrokkenen(melding_id, betrokkenen, cursor):
	for name in betrokkenen.keys():
		betrokkene = betrokkenen[name]
		cursor.execute("INSERT INTO web_betrokkene (melding_id, naam)" \
				"VALUES (?, ?)", (melding_id, name)) 
		betrokkene_id = cursor.lastrowid
		insert_betrokkene_data(betrokkene_id, betrokkene, cursor)

def insert_meldingen(company_url, meldingen, cursor):
	for id in meldingen.keys():
		melding = meldingen[id]
		cursor.execute("INSERT INTO melding_sloppy (company_url, id," \
				"description, doorgifte_passend, url," \
				"doorgifte_buiten_eu, naam_verwerking) VALUES " \
				"(?, ?, ?, ?, ?, ?, ?)", (company_url, id,
				melding['description'],
				melding['doorgifte_passend'], melding['url'],
				melding['doorgifte_buiten_eu'],
				melding['naam_verwerking']))
#		melding_id = cursor.lastrowid
		melding_id = id;
		if "betrokkenen" in melding.keys():
			insert_betrokkenen(melding_id, melding["betrokkenen"], cursor)
		if "ontvangers" in melding.keys():
			insert_ontvangers(melding_id, melding["ontvangers"], cursor)
		if "verantwoordelijken" in melding.keys():
			insert_verantwoordelijken(melding_id, melding["verantwoordelijken"], cursor)
		if "doelen" in melding.keys():
			insert_doelen(melding_id, melding["doelen"], cursor)

def insert_companies(fp, cursor):
	j = json.load(fp)
	i = 0

	for company in j:
		cursor.execute("INSERT INTO company_part1 (url, name) VALUES (?, ?)",
			(company["url"], company["name"]))

		insert_meldingen(company["url"], company["meldingen"], cursor)

		i += 1

	return i

# XXX: a race exists between this and sqlite3.connect. I couldn't find how to
# do it correct in the docs and too lazy to read the code.
if os.path.exists('cbp-new.sqlite'):
    print "File cbp-new.sqlite already exists"
    sys.exit(1)

connection = sqlite3.connect("cbp-new.sqlite")
c = connection.cursor()

c.executescript(
"""
CREATE TABLE web_betrokkene (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER NOT NULL,
	naam TEXT
);
CREATE TABLE web_betrokkenedata (
	id INTEGER PRIMARY KEY NOT NULL,
	betrokkene_id INTEGER NOT NULL,
	name TEXT,
	value TEXT
);
CREATE TEMP TABLE company_part1 (
	url text,
	name text
);
CREATE TEMP TABLE company_part2 (
	bezoekadres TEXT,
	naam TEXT,
	postadres TEXT
);
CREATE TABLE web_doel (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER NOT NULL,
	naam TEXT
);
CREATE TEMP TABLE melding_sloppy (
	id INTEGER,
    company_url TEXT, -- used as foreign key
	description TEXT,
	doorgifte_passend INTEGER,
	url TEXT,
	doorgifte_buiten_eu INTEGER,
	naam_verwerking TEXT
);
CREATE TABLE web_ontvanger (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER,
	naam TEXT
);
"""
);

ncompanies = 0
for dirname, dirnames, filenames, in os.walk('.'):
	for filename in filenames:
		if filename.endswith(".json"):
			path = os.path.join(dirname, filename)
			fp = open(path, 'r')
			ncompanies += insert_companies(fp, c)

print "Inserted %d companies" % (ncompanies, )

# Merge verantwoordelijke and company tables
# XXX: This assumes that the company name uniquely identifies the company.
# Which might not be true. There is more information hidden in the URL of the
# company which can be used to join the two tables.
c.execute("CREATE TEMP TABLE company_merged as select c.url as url, v.bezoekadres as " \
            " bezoekadres, v.naam as naam, v.postadres as postadres from" \
            " company_part1 as c INNER JOIN company_part2 as v ON v.naam " \
            "= c.name;")

# Remove the duplicates.
c.execute("CREATE TEMP TABLE company_distinct as select DISTINCT * from company_merged")

# For some reason when doing an inner join sqlite doesn't generate a _rowid_
c.execute("CREATE TABLE web_company as select _rowid_ as id, * from company_distinct")

c.execute("CREATE TABLE melding_duplicates as SELECT m.id, m.description, c.id as company_id, " \
            " m.doorgifte_passend, m.url, m.doorgifte_buiten_eu, m.naam_verwerking FROM" \
            " melding_sloppy as m INNER JOIN web_company as c ON c.url = "
            " m.company_url;")

# Create in between table.
c.execute("CREATE TABLE company_melding as SELECT DISTINCT company_id, id as " \
            " melding_id from melding_duplicates")

# Create distinct meldingen table
c.execute("CREATE TABLE melding as SELECT DISTINCT id, description, " \
           " doorgifte_passend, url, doorgifte_buiten_eu, naam_verwerking FROM " \
           " melding_duplicates")

connection.commit()

c.close()

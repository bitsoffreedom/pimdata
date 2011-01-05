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
		cursor.execute("INSERT INTO web_verantwoordelijke (melding_id," \
				"bezoekadres, naam, postadres) VALUES " \
				"(?, ?, ?, ?)", (melding_id, bezoekadres, naam,
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

def insert_meldingen(company_id, meldingen, cursor):
	for id in meldingen.keys():
		melding = meldingen[id]
		cursor.execute("INSERT INTO web_melding (company_id, id," \
				"description, doorgifte_passend, url," \
				"doorgifte_buiten_eu, naam_verwerking) VALUES " \
				"(?, ?, ?, ?, ?, ?, ?)", (company_id, id,
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
		cursor.execute("INSERT INTO web_company (url, name) VALUES (?, ?)",
			(company["url"], company["name"]))
		company_id = cursor.lastrowid

		insert_meldingen(company_id, company["meldingen"], cursor)

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
CREATE TABLE web_company (
	id INTEGER PRIMARY KEY NOT NULL,
	url text,
	name text
);
CREATE TABLE web_doel (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER NOT NULL,
	naam TEXT
);
CREATE TABLE web_melding (
	id INTEGER,
	company_id INTEGER,
    -- used as foreign key
    -- company_url TEXT,
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
CREATE TABLE web_verantwoordelijke (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER,
	bezoekadres TEXT,
	naam TEXT,
	postadres TEXT
);
"""
);

ncompanies = 0
for dirname, dirnames, filenames, in os.walk('data'):
	for filename in filenames:
		if filename.endswith(".json"):
			path = os.path.join(dirname, filename)
			fp = open(path, 'r')
			ncompanies += insert_companies(fp, c)

print "Inserted %d companies" % (ncompanies, )
connection.commit()
c.close()

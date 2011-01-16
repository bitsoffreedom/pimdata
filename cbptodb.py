import psycopg2
import sys
import os
import json

def insert_doelen(melding_id, doelen, cursor):
    for doel in doelen:
    	cursor.execute("INSERT INTO scrape_doel (melding_id, naam) " \
    			" VALUES (%s, %s)", (melding_id, doel))

def insert_verantwoordelijken(melding_id, verantwoordelijken, cursor):
    for verantwoordelijke in verantwoordelijken:
    	naam = None
    	bezoekadres = None

	bezoekadres_straat = None
	bezoekadres_stad = None
	bezoekadres_land = None

    	postadres = None

	postadres_straat = None
	postadres_stad = None
	postadres_land = None

    	for key, value in verantwoordelijke.iteritems():
    		if key == "Naam":
    			if naam != None:
    				raise Exception("Field Naam found twice")
    			naam = value
    		elif key == "Bezoekadres":
    			if bezoekadres != None:
    				raise Exception("Field Bezoekadres found twice")
    			bezoekadres = value

			if bezoekadres.count("\n") == 2:
				bezoekadres_straat, bezoekadres_stad, bezoekadres_land = bezoekadres.split("\n")
    		elif key == "Postadres":
    			if postadres != None:
    				raise Exception("Field Postadres found twice")
    			postadres = value

			if postadres.count("\n") == 2:
				postadres_straat, postadres_stad, postadres_land = postadres.split("\n")
    		else:
    			raise Exception('Unknown field found');
        adres = None
        if (bezoekadres):
            adres = postadres
        else:
            adres = bezoekadres
        cursor.execute("INSERT INTO scrape_verantwoordelijke (bezoekadres, naam, " \
                        "postadres) VALUES (%s, %s, %s)", ( bezoekadres, naam,
                        adres))

def insert_ontvangers(melding_id, ontvangers, cursor):
    for ontvanger in ontvangers:
    	cursor.execute("INSERT INTO scrape_ontvanger (melding_id, naam) " \
    			" VALUES (%s, %s)", (melding_id, ontvanger));

def insert_betrokkene_data(betrokkene_id, betrokkene, cursor):
    for name, value in betrokkene.iteritems():
    	cursor.execute("INSERT INTO scrape_data (betrokkene_id," \
    			"name, value) VALUES (%s, %s, %s)", (betrokkene_id,
    			name, value))

def insert_betrokkenen(melding_id, betrokkenen, cursor):
    for name in betrokkenen.keys():
    	betrokkene = betrokkenen[name]
    	cursor.execute("INSERT INTO scrape_betrokkene (melding_id, naam)" \
    			"VALUES (%s, %s)", (melding_id, name)) 
    	betrokkene_id = cursor.lastrowid
    	insert_betrokkene_data(betrokkene_id, betrokkene, cursor)

def insert_meldingen(company_url, meldingen, cursor):
    for id in meldingen.keys():
    	melding = meldingen[id]
        try:
            melding_id = int(id)
        except TypeError:
            sys.exit(0)
        if melding_id == 0:
            print("skipping:\n")
            print "description %s\n" % (melding['description'], )
            continue

	SCRAPE_UNASSIGNED = 0
	SCRAPE_TRUE = 1
	SCRAPE_FALSE = 2

	doorgifte_passend_state = SCRAPE_UNASSIGNED
	if melding['doorgifte_passend'] == True:
		doorgifte_passend_state = SCRAPE_TRUE
	if melding['doorgifte_passend'] == False:
		doorgifte_passend_state = SCRAPE_FALSE

	doorgifte_buiten_eu_state = SCRAPE_UNASSIGNED
	if melding['doorgifte_buiten_eu'] == True:
		doorgifte_buiten_eu_state = SCRAPE_TRUE
	if melding['doorgifte_buiten_eu'] == False:
		doorgifte_buiten_eu_state = SCRAPE_FALSE

        cursor.execute("INSERT INTO scrape_melding (company_url, id," \
    			"description, doorgifte_passend, url," \
    			"doorgifte_buiten_eu, naam_verwerking) VALUES " \
    			"(%s, %s, %s, %s, %s, %s, %s)", (company_url, melding_id,
			melding['description'], doorgifte_passend_state,
			melding['url'], doorgifte_buiten_eu_state,
			melding['naam_verwerking']))
    	if "betrokkenen" in melding.keys():
    		insert_betrokkenen(melding_id, melding["betrokkenen"], cursor)
    	if "ontvangers" in melding.keys():
    		insert_ontvangers(melding_id, melding["ontvangers"], cursor)
    	if "verantwoordelijken" in melding.keys():
    		insert_verantwoordelijken(melding_id, melding["verantwoordelijken"], cursor)
    	if "doelen" in melding.keys():
    		insert_doelen(melding_id, melding["doelen"], cursor)

def insert_bedrijven(json, cursor):
    i = 0

    for company in json:
    	cursor.execute("INSERT INTO scrape_bedrijf (url, name) VALUES (%s, %s)",
    		(company["url"], company["name"]))

    	insert_meldingen(company["url"], company["meldingen"], cursor)

    	i += 1

    return i

connection = psycopg2.connect("dbname=pim user=alex")
c = connection.cursor()

c.execute(
"""
CREATE TABLE scrape_bedrijf (
    url text,
    name text
);
CREATE TABLE scrape_melding (
    id INTEGER,
    company_url TEXT, -- used as foreign key
    description TEXT,
    doorgifte_passend INTEGER,
    url TEXT,
    doorgifte_buiten_eu INTEGER,
    naam_verwerking TEXT
);
CREATE TABLE scrape_betrokkene (
    id SERIAL PRIMARY KEY NOT NULL,
    melding_id INTEGER, -- NOT NULL,
    naam TEXT
);
CREATE TABLE scrape_data (
    id SERIAL PRIMARY KEY NOT NULL,
    betrokkene_id INTEGER NOT NULL,
    name TEXT,
    value TEXT
);
CREATE TABLE scrape_ontvanger (
    id SERIAL PRIMARY KEY NOT NULL,
    melding_id INTEGER,
    naam TEXT
);
CREATE TABLE scrape_verantwoordelijke (
    bezoekadres TEXT,
    naam TEXT,
    postadres TEXT
);
CREATE TABLE scrape_doel (
    id SERIAL PRIMARY KEY NOT NULL,
    melding_id INTEGER NOT NULL,
    naam TEXT
);
""")

ncompanies = 0
for dirname, dirnames, filenames, in os.walk('.'):
    for filename in filenames:
    	if filename.endswith(".json"):

    		path = os.path.join(dirname, filename)
    		fp = open(path, 'r')
		j = json.load(fp)
    		ncompanies += insert_bedrijven(j, c)

connection.commit()
c.close()

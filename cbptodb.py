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
        adres = None
        if (bezoekadres):
            adres = postadres
        else:
            adres = bezoekadres
        cursor.execute("INSERT INTO company_part2 (bezoekadres, naam, " \
                        "postadres) VALUES (?, ?, ?)", ( bezoekadres, naam,
                        adres))

def insert_ontvangers(melding_id, ontvangers, cursor):
	for ontvanger in ontvangers:
		cursor.execute("INSERT INTO web_ontvanger (melding_id, naam) " \
				" VALUES (?, ?)", (melding_id, ontvanger));

def insert_betrokkene_data(betrokkene_id, betrokkene, cursor):
	for name, value in betrokkene.iteritems():
		cursor.execute("INSERT INTO data_undis (betrokkene_id," \
				"name, value) VALUES (?, ?, ?)", (betrokkene_id,
				name, value))

def insert_betrokkenen(melding_id, betrokkenen, cursor):
	for name in betrokkenen.keys():
		betrokkene = betrokkenen[name]
		cursor.execute("INSERT INTO betrokkene_undis (melding_id, naam)" \
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
CREATE TEMP TABLE betrokkene_undis (
	id INTEGER PRIMARY KEY NOT NULL,
	melding_id INTEGER NOT NULL,
	naam TEXT
);
CREATE temp TABLE data_undis (
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
)

ncompanies = 0
for dirname, dirnames, filenames, in os.walk('.'):
	for filename in filenames:
		if filename.endswith(".json"):
			path = os.path.join(dirname, filename)
			fp = open(path, 'r')
			ncompanies += insert_companies(fp, c)

for dirname, dirnames, filenames, in os.walk('../cbp-data/'):
	for filename in filenames:
		if filename.endswith(".json"):
			path = os.path.join(dirname, filename)
			fp = open(path, 'r')
			ncompanies += insert_companies(fp, c)

print "Inserted %d companies" % (ncompanies, )

c.executescript(
"""
-- Merge verantwoordelijke and company tables
-- XXX: This assumes that the company name uniquely identifies the company.
-- Which might not be true. There is more information hidden in the URL of the
-- company which can be used to join the two tables.

CREATE TEMP TABLE company_merged as select c.url as url, v.bezoekadres as
bezoekadres, v.naam as naam, v.postadres as postadres from company_part1 as c
INNER JOIN company_part2 as v ON v.naam = c.name;

-- Remove the duplicates.
CREATE TEMP TABLE company_distinct as select DISTINCT * from company_merged;

-- For some reason when doing an inner join sqlite doesn't generate a _rowid_
CREATE TABLE web_company as select _rowid_ as id, * from company_distinct;

-- Make a proper relation between melding and company
CREATE TEMP TABLE melding_duplicates as SELECT m.id, m.description, c.id as
company_id, m.doorgifte_passend, m.url, m.doorgifte_buiten_eu,
m.naam_verwerking FROM melding_sloppy as m INNER JOIN web_company as c ON c.url
= m.company_url;

-- Create in between table.
CREATE TABLE web_company_meldingen as SELECT DISTINCT company_id, id as
melding_id from melding_duplicates;

-- Create distinct meldingen table
CREATE TABLE web_melding as SELECT DISTINCT id, description, doorgifte_passend,
url, doorgifte_buiten_eu, naam_verwerking FROM melding_duplicates;

-- Create a tables with all the types of betrokkene
CREATE TEMP TABLE betrokkene_type_no_id AS SELECT DISTINCT naam FROM betrokkene_undis;
CREATE TABLE web_betrokkenetype AS SELECT _rowid_ as id, naam FROM betrokkene_type_no_id;

CREATE TABLE web_betrokkene AS SELECT b.id as id, b.melding_id, t.id as
betrokkene_type_id FROM betrokkene_undis as b INNER JOIN web_betrokkenetype as
t ON b.naam=t.naam;

-- Create data and data types
CREATE TEMP TABLE datatype_no_id AS SELECT DISTINCT name FROM data_undis;
CREATE TABLE web_datatype AS SELECT DISTINCT _rowid_ as id, name FROM datatype_no_id;
CREATE TABLE web_data AS SELECT betrokkene_id, t.id as datatype_id, value FROM
data_undis as d INNER JOIN web_datatype as t ON t.name = d.name;

-- Create table to easily copy data.
CREATE TABLE pimbase_organisation AS SELECT id, naam as name, '' as shortname, '' as kvknumber, postadres as address, '' as postcode, 0 as organisationtype_id, 0 as
city_id, 0 as country_id, 0 as sector_id, url as website from web_company;

CREATE TEMP TABLE pimbase_organisation_citizenrole_no_id AS
SELECT DISTINCT cm.company_id as organisation_id,
    b.betrokkene_type_id as citizenrole_id
 FROM web_company_meldingen as cm
 INNER JOIN web_melding as m ON cm.melding_id = m.id
 INNER JOIN web_betrokkene as b ON m.id = b.melding_id;

CREATE TABLE pimbase_organisation_citizenrole AS
SELECT _rowid_ as id, * FROM pimbase_organisation_citizenrole_no_id;

CREATE TABLE pimbase_citizenrole AS
SELECT id, name, name as label FROM web_datatype;

"""
)

connection.commit()
c.close()

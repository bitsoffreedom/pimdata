from django.db import models

class Betrokkene(models.Model):
    naam = models.CharField(max_length=255)

    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

class BetrokkeneData(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    betrokkene = models.ForeignKey('Betrokkene')

    def __unicode__(self):
        return self.name

#class Company(models.Model):
#    url = models.CharField(max_length=255)
#    name = models.CharField(max_length=255)
#
#    def __unicode__(self):
#        return self.name

class Doel(models.Model):
    naam = models.CharField(max_length=255)

    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

class Melding(models.Model):
#    cbp_id = models.BigIntegerField()
    description = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

#    company = models.ForeignKey('Company')

    def __unicode__(self):
        return "%d" % (self.id, )

class Ontvanger(models.Model):
    naam = models.CharField(max_length=255)

    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

#class Verantwoordelijke(models.Model):
#    bezoekadres = models.CharField(max_length=255)
#    naam = models.CharField(max_length=255)
#    postadres = models.CharField(max_length=255)
#
#    melding = models.ForeignKey('Melding')

class Company(models.Model):
    bezoekadres = models.CharField(max_length=255)
    naam = models.CharField(max_length=255)
    postadres = models.CharField(max_length=255)
    melding = models.ForeignKey('Melding')
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.naam

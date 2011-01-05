from django.db import models

class Betrokkene(models.Model):
    naam = models.CharField(max_length=255)
    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name=('Betrokkene')
        verbose_name_plural=('Betrokkenen')


class BetrokkeneData(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    betrokkene = models.ForeignKey('Betrokkene')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name=('Betrokkene data')
        verbose_name_plural=('Betrokkenen data')

class Doel(models.Model):
    naam = models.CharField(max_length=255)
    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name=('Doel')
        verbose_name_plural=('Doelen')

class Melding(models.Model):
    description = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return "%d" % (self.id, )

    class Meta:
        verbose_name=('Melding')
        verbose_name_plural=('Meldingen')

class Ontvanger(models.Model):
    naam = models.CharField(max_length=255)
    melding = models.ForeignKey('Melding')

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name=('Ontvanger')
        verbose_name_plural=('Ontvangers')

class Company(models.Model):
    bezoekadres = models.CharField(max_length=255)
    naam = models.CharField(max_length=255)
    postadres = models.CharField(max_length=255)
    melding = models.ForeignKey('Melding')
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name=('Organisatie')
        verbose_name_plural=('Organisaties')

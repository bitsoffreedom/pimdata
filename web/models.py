from django.db import models

class Betrokkene(models.Model):
    betrokkene_type = models.ForeignKey('BetrokkeneType')
    melding = models.ForeignKey('Melding')

    class Meta:
        verbose_name=('Betrokkene')
        verbose_name_plural=('Betrokkenen')

class BetrokkeneType(models.Model):
    naam = models.CharField(max_length=255)

    def __unicode__(self):
        return self.naam

class DataType(models.Model):
    name = models.CharField(max_length=255)

class Data(models.Model):
    betrokkene = models.ForeignKey('Betrokkene')
    datatype = models.ForeignKey('DataType')
    value = models.CharField(max_length=255)

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
#    doorgifte_passend = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
#    doorgifte_buiten_eu = models.CharField(max_length=255)
    naam_verwerking = models.CharField(max_length=255)

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
    meldingen = models.ManyToManyField(Melding)
    url = models.CharField(max_length=255)

    def html_link(self):
        return "<a href=\"%s\">website</a>" % (self.url, )
    html_link.allow_tags = True

    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name=('Organisatie')
        verbose_name_plural=('Organisaties')

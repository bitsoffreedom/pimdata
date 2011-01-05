from web.models import *
from django.contrib import admin

class BetrokkeneDataInline(admin.StackedInline):
    model = BetrokkeneData
    extra = 1

class BetrokkeneInline(admin.TabularInline):
    model = Betrokkene
    extra = 1

class DoelInline(admin.TabularInline):
    model = Doel
    extra = 1

class OntvangerInline(admin.TabularInline):
    model = Ontvanger
    extra = 1

class CompanyInline(admin.TabularInline):
    model = Company
    extra = 1

class BetrokkeneAdmin(admin.ModelAdmin):
    inlines = [BetrokkeneDataInline, ]

class MeldingAdmin(admin.ModelAdmin):
    inlines = [CompanyInline, OntvangerInline, DoelInline, ]

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('naam', 'postadres', 'bezoekadres', 'html_link')
    readonly_fields = ('melding', )

admin.site.register(Betrokkene, BetrokkeneAdmin)
admin.site.register(BetrokkeneData)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Doel)
admin.site.register(Melding, MeldingAdmin)
admin.site.register(Ontvanger)

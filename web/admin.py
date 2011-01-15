from web.models import *
from django.contrib import admin


class MeldingAdmin(admin.ModelAdmin):
    pass

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('naam', 'postadres', 'bezoekadres', 'html_link')

admin.site.register(Betrokkene)
admin.site.register(BetrokkeneType)
admin.site.register(BetrokkeneData)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Doel)
admin.site.register(Melding, MeldingAdmin)
admin.site.register(Ontvanger)

from datetime import date
from django import forms
from django.http import HttpResponse
from django.contrib import admin
from django.utils.translation import ugettext as _
from models import DynamicFieldValue, DynamicField, DynamicFormFieldRelation, DynamicForm, DynamicFormData
from StringIO import StringIO
from zipfile import ZipFile
import csv


class DynamicFieldValue_Inline(admin.TabularInline):
    model = DynamicFieldValue
    extra = 0


class DynamicFieldAdminForm(forms.ModelForm):
    class Meta:
        model = DynamicField

    def __init__(self, *args, **kwargs):
        super(DynamicFieldAdminForm, self).__init__(*args, **kwargs)
        self.fields['default'].queryset = self.instance.values.all() if self.instance else DynamicFieldValue.objects.none()


class DynamicFieldAdmin(admin.ModelAdmin):
    model = DynamicField
    inlines = [DynamicFieldValue_Inline]
    form = DynamicFieldAdminForm
    list_display = ['label', 'type', 'required', 'default', 'help_text']
    list_editable = ['type', 'required', 'help_text']
    list_filter  = ['dynamicform__name']


class DynamicFormFieldRelation_Inline(admin.TabularInline):
    model = DynamicFormFieldRelation
    extra = 0


class DynamicFormAdmin(admin.ModelAdmin):
    model = DynamicForm
    fieldsets = (
        (None, {'fields': ['name', 'slug', 'type', 'success_url', 'notification_emails']}),
        ('Confirmation e-mail', {'classes': ['collapse'], 'fields': ['send_confirmation', 'email_recipients', 'email_subject', 'email_content']}),
    )
    inlines = [DynamicFormFieldRelation_Inline]
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'slug', 'type', 'success_url']
    list_editable = ['type', 'success_url']
    actions = ['export_data_as_csv']

    def export_form_data_as_csv(self, dynamicform, output):
        writer = csv.DictWriter(output, fieldnames=dynamicform.field_names)
        writer.writerow(dict((f, f) for f in dynamicform.field_names))
        for row in dynamicform.data_as_dicts():
            writer.writerow(row)

    def export_data_as_csv(self, request, queryset):
        output = StringIO()
        if queryset.count() == 1:
            self.export_form_data_as_csv(queryset.get(), output)
            mimetype = 'text/csv'
            filename = '%s.%s.csv' % (queryset.get().name, date.today())
        else:
            zipfile = ZipFile(output, 'w')
            for dynamicform in queryset:
                csv_output = StringIO()
                self.export_form_data_as_csv(dynamicform, csv_output)
                filename = '%s.%s.csv' % (dynamicform.name, date.today())
                zipfile.writestr(filename, csv_output.getvalue())
            zipfile.close()
            mimetype = 'application/zip'
            filename = 'dynamicforms-data.%s.zip' % date.today()
        response = HttpResponse(output.getvalue(), mimetype=mimetype)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class DynamicFormDataAdmin(admin.ModelAdmin):
    model = DynamicFormData
    list_display = ['dynamicform', 'timestamp']
    list_filter  = ['dynamicform__name']


admin.site.register(DynamicField, DynamicFieldAdmin)
admin.site.register(DynamicForm, DynamicFormAdmin)
admin.site.register(DynamicFormData, DynamicFormDataAdmin)


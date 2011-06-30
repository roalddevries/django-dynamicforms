from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.http import QueryDict
from django.utils.translation import ugettext_lazy as _
from forms import BaseDynamicForm, DynamicFormMetaclass
import re


# the default dynamic field types
DEFAULT_DYNAMICFIELD_TYPE = {
    'VERBOSE_NAME': _('text'),
    'FIELD':        'django.forms.CharField',
    'HAS_CHOICES':  False,
    'DEFAULT':      '',
    'WIDGET':       'django.forms.TextInput',
}
DYNAMICFIELD_TYPES = {
    'text':     {'VERBOSE_NAME': _('text'),          'FIELD': 'django.forms.CharField',    'HAS_CHOICES': False, 'DEFAULT': '',    'WIDGET': 'django.forms.TextInput'},
    'integer':  {'VERBOSE_NAME': _('integer'),       'FIELD': 'django.forms.IntegerField', 'HAS_CHOICES': False, 'DEFAULT': '',    'WIDGET': 'django.forms.TextInput'},
    'email':    {'VERBOSE_NAME': _('e-mail'),        'FIELD': 'django.forms.EmailField',   'HAS_CHOICES': False, 'DEFAULT': '',    'WIDGET': 'django.forms.TextInput'},
    'select':   {'VERBOSE_NAME': _('dropdown list'), 'FIELD': 'django.forms.ChoiceField',  'HAS_CHOICES': True,  'DEFAULT': '',    'WIDGET': 'django.forms.Select'},
    'radio':    {'VERBOSE_NAME': _('radio buttons'), 'FIELD': 'django.forms.ChoiceField',  'HAS_CHOICES': True,  'DEFAULT': '',    'WIDGET': 'django.forms.RadioSelect'},
    'checkbox': {'VERBOSE_NAME': _('checkbox'),      'FIELD': 'django.forms.BooleanField', 'HAS_CHOICES': False, 'DEFAULT': False, 'WIDGET': 'django.forms.CheckboxInput'},
    'textarea': {'VERBOSE_NAME': _('large textbox'), 'FIELD': 'django.forms.CharField',    'HAS_CHOICES': False, 'DEFAULT': '',    'WIDGET': 'django.forms.Textarea'},
}
for k, v in getattr(settings, 'DYNAMICFIELD_TYPES', {}).iteritems():
    DYNAMICFIELD_TYPES[k] = dict(DEFAULT_DYNAMICFIELD_TYPE, **v)


DEFAULT_DYNAMICFORM_TYPE = {
    'VERBOSE_NAME':   _('default form'),
    'BASE_FORM':      'dynamicforms.forms.BaseDynamicForm',
    'REDIRECT_URL':   '',
    'TEMPLATE':       'dynamicforms/form.html',
    'TAG_TEMPLATE':   'dynamicforms/_form.html',
    'EMAIL_TEMPLATE': 'dynamicforms/notification.eml',
}
DYNAMICFORM_TYPES = {'default': DEFAULT_DYNAMICFORM_TYPE}
for k, v in getattr(settings, 'DYNAMICFORM_TYPES', {}).iteritems():
    DYNAMICFORM_TYPES[k] = dict(DEFAULT_DYNAMICFORM_TYPE, **v)


HTTP_HEADERS = [
    'CONTENT_LENGTH', 'CONTENT_TYPE', 'HTTP_ACCEPT_ENCODING', 'HTTP_ACCEPT_LANGUAGE',
    'HTTP_HOST', 'HTTP_REFERER', 'HTTP_USER_AGENT', 'QUERY_STRING', 'REMOTE_ADDR',
    'REMOTE_HOST', 'REMOTE_USER', 'REQUEST_METHOD', 'SERVER_NAME', 'SERVER_PORT',
]


class DynamicFieldValue(models.Model):
    '''Used for allowed and default values'''
    value = models.CharField(blank=True, unique=True, max_length=200)
    field = models.ForeignKey('DynamicField', related_name='values', help_text=_('This is used for e.g. dropdown lists and radio buttons.'))

    def __unicode__(self):
        return self.value

    def clean(self):
        if DYNAMICFIELD_TYPES[self.field.type]['HAS_CHOICES'] == False:
            raise ValidationError(_("The chosen field type doesn't support choices"))


class DynamicField(models.Model):

    TYPES = DYNAMICFIELD_TYPES
    TYPE_CHOICES = [(key, value['VERBOSE_NAME']) for key, value in DYNAMICFIELD_TYPES.iteritems()]

    label       = models.CharField      (max_length=200)
    type        = models.CharField      (choices=TYPE_CHOICES, max_length=50)
    required    = models.BooleanField   (default=True)
    default     = models.ForeignKey     (DynamicFieldValue, related_name='default_for', null=True, blank=True, max_length=200)
    help_text   = models.CharField      (max_length=200, blank=True, help_text=_('The help text will be displayed just below the form field.'))

    class Meta:
        verbose_name        = _('dynamic form field')
        verbose_name_plural = _('dynamic form fields')

    def __unicode__(self):
        return self.label

    @property
    def choices(self):
        return self.values.values_list('id', 'value')

    @property
    def field_class(self):
        if not hasattr(self, '_field'):
            field_path   = DYNAMICFIELD_TYPES[self.type].get('FIELD', 'django.forms.CharField').split('.')
            field_module = __import__('.'.join(field_path[:-1]), {}, {}, field_path[-1])
            Field        = getattr(field_module, field_path[-1])

            widget_path   = DYNAMICFIELD_TYPES[self.type].get('WIDGET', 'django.forms.TextInput').split('.')
            widget_module = __import__('.'.join(widget_path[:-1]), {}, {}, widget_path[-1])
            Widget        = getattr(widget_module, widget_path[-1])

            kwargs = {
                'label':      self.label,
                'required':   self.required,
                'initial':    self.default,
                'help_text':  self.help_text,
                'widget':     Widget,
            }
            if DYNAMICFIELD_TYPES[self.type]['HAS_CHOICES']:
                kwargs.update({'choices': self.values.values_list('value', 'value')})
            self._field = Field(**kwargs)

        return self._field


class DynamicFormFieldRelation(models.Model):
    dynamicform  = models.ForeignKey          ('DynamicForm')
    field_name   = models.CharField           (max_length=200) # should be a python indentifier
    dynamicfield = models.ForeignKey          ('DynamicField', blank=True, null=True)
    sort_weight  = models.PositiveIntegerField(default=1000, help_text=_('Higher numbers get a lower position in the form.'))

    class Meta:
        ordering = ['dynamicform__name', 'sort_weight', 'field_name']

    def clean_fields(self, exclude=None):
        errors = {}

        if 'field_name' not in exclude:
            if not re.match('\w[\w\d_]*$', self.field_name):
                errors['field_name'] = [_('This is no valid name')]

        if 'dynamicfield' not in exclude:
            if self.field_name in self.dynamicform.base_form_class.base_fields and self.dynamicfield is not None:
                errors['dynamicfield'] = [_("This field can not be overridden; leave the field empty")]
            elif self.field_name not in self.dynamicform.base_form_class.base_fields and self.dynamicfield is None:
                errors['dynamicfield'] = [_("This field is not predefined; don't leave the field empty")]

        if errors:
            raise ValidationError(errors)

class DynamicForm(models.Model):

    TYPES = DYNAMICFORM_TYPES
    TYPE_CHOICES = [(key, value['VERBOSE_NAME']) for key, value in TYPES.iteritems()]

    name                = models.CharField(max_length=200)
    slug                = models.SlugField(max_length=200)
    type                = models.CharField(choices=TYPE_CHOICES, max_length=50)
    fields              = models.ManyToManyField(DynamicField, through=DynamicFormFieldRelation)
    success_url         = models.CharField(blank=True, max_length=255)
    notification_emails = models.CharField(_('notification e-mail recipients'), blank=True, max_length=255, help_text=_("separated by comma's"))

    send_confirmation = models.BooleanField(_('send confirmation'), default=False, help_text=_('Confirm completion of the form by sending an email to registrar. Make sure the form contains an email field.'))
    email_recipients  = models.CharField(_('confirmation e-mail recipients'), max_length=502, blank=True, help_text=("separated by comma's"))
    email_subject     = models.CharField(_('confirmation e-mail subject'), max_length=200, blank=True)
    email_content     = models.TextField(_('confirmation e-mail content'), help_text=_('This is the text shown in the confirmation e-mail'), blank=True)

    class Meta:
        verbose_name        = _('dynamic form')
        verbose_name_plural = _('dynamic forms')
        ordering            = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('process_dynamicform', kwargs={'slug': self.slug})

    # @property
    # def settings(self):
    #     if not hasattr(type(self), '_types'):
    #         type(self)._types = dict(DEFAULT_DYNAMICFORM_TYPES)
    #         for k, v in getattr(settings, 'DYNAMICFORM_TYPES', {}).iteritems():
    #             DYNAMICFORM_TYPE = dict(DEFAULT_DYNAMICFORM_TYPE)
    #             DYNAMICFORM_TYPE.update(v)
    #             DYNAMICFORM_TYPES[k] = DYNAMICFORM_TYPE
    #     return self._types[self.type]

    def get_success_url(self):
        success_url = self.success_url or DYNAMICFORM_TYPES[self.type]['SUCCESS_URL']
        # success_url = self.success_url or self.settings['SUCCESS_URL']
        if success_url == '':
            return ''
        if success_url.startswith('/'):
            return '%s/' % success_url.rstrip('/')
        elif success_url.startswith('http://') or success_url.startswith('https://'):
            return success_url
        else:
            # check if it's a named url
            if success_url.startswith('"') and quoted_url.endswith('"'):
                return reverse(success_url.strip('"'))
            else:
                # relative url
                return '%s/%s/' % (self.get_absolute_url().rstrip('/'), success_url.strip('/'))

    @property
    def field_names(self):
        return self.dynamicformfieldrelation_set.order_by('sort_weight').values_list('field_name', flat=True)

    @property
    def template(self):
        return DYNAMICFORM_TYPES[self.type]['TEMPLATE']
        # return self.settings['TEMPLATE']

    @property
    def tag_template(self):
        return DYNAMICFORM_TYPES[self.type]['TAG_TEMPLATE']
        # return self.settings['TAG_TEMPLATE']

    @property
    def email_template(self):
        return DYNAMICFORM_TYPES[self.type]['EMAIL_TEMPLATE']
        # return self.settings['EMAIL_TEMPLATE']

    @property
    def base_form_class(self):
        if not hasattr(self, '_base_form'):
            base_form_path   = DYNAMICFORM_TYPES[self.type]['BASE_FORM'].split('.')
            # base_form_path   = self.settings['BASE_FORM'].split('.')
            base_form_module = __import__('.'.join(base_form_path[:-1]), {}, {}, base_form_path[-1])
            self._base_form  = getattr(base_form_module, base_form_path[-1])
        return self._base_form

    @property
    def form_class(self):
        if not hasattr(self, '_form'):

            class CustomForm(self.base_form_class):
                __metaclass__ = DynamicFormMetaclass
                _dynamicform  = self # where self refers to the dynamic form, the first parameter of 'def form_class(...)'

            self._form = CustomForm

        return self._form

    def data_as_dicts(self, fields=None):
        return [d.as_dict(fields) for d in DynamicFormData.objects.filter(dynamicform=self)]

    def data_as_lists(self, fields=None):
        return [d.as_list(fields) for d in DynamicFormData.objects.filter(dynamicform=self)]


class DynamicFormData(models.Model):
    dynamicform   = models.ForeignKey(DynamicForm)
    raw_post_data = models.TextField(help_text=_('The submitted form data as a query string'))
    timestamp     = models.DateTimeField(auto_now_add=True)
    headers       = models.TextField(help_text=_('The headers of the submitted post request as "HEADER: value"-lines'))

    @property
    def POST(self):
        if not hasattr(self, '_POST'):
            self._POST = QueryDict(self.raw_post_data)
        return self._POST

    @property
    def bound_form(self):
        if not hasattr(self, '_bound_form'):
            self._bound_form = self.dynamicform.form_class(self.POST)
        return self._bound_form

    def as_dict(self, fields=None):
        # contains all specified fields, or all fields in the dynamic form
        if self.bound_form.is_valid():
            actual_fields = fields if fields is not None else self.dynamicform.field_names
            return dict((f, self.bound_form.cleaned_data.get(f, None)) for f in actual_fields)
        else:
            return {}

    def as_list(self, fields=None):
        actual_fields = fields if fields is not None else self.dynamicform.field_names
        return dict(self.bound_form.cleaned_data.get(f, None) for f in actual_fields)

    def get_headers(self):
        return dict(
                tuple(x.strip() for x in line.split(':'))
                for line in self.headers.split('\n')
                )

    class Meta:
        verbose_name        = _('data posted from dynamic forms')
        verbose_name_plural = _('data posted from dynamic forms')
        ordering            = ['dynamicform', '-timestamp']


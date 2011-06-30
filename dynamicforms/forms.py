from django import forms
from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils.translation import ugettext_lazy as _


class DynamicFormMetaclass(DeclarativeFieldsMetaclass):
    '''Metaclass for forms created from DynamicForm'''

    def __new__(cls, name, bases, attrs):
        # add dynamicfields to attrs
        dynamic_field_weight = {}
        for relation in attrs['_dynamicform'].dynamicformfieldrelation_set.order_by('sort_weight').all():
            dynamic_field_weight[relation.field_name] = relation.sort_weight
            if relation.dynamicfield:
                attrs[relation.field_name] = relation.dynamicfield.field_class
        # construct the form class
        result = DeclarativeFieldsMetaclass.__new__(cls, name, bases, attrs)
        # customize order of fields
        field_weight = dict((field_name, -1000 + i) for base in bases for i, field_name in enumerate(base.base_fields))
        field_weight.update(dynamic_field_weight)
        result.base_fields.keyOrder = [field for (field, i) in sorted(field_weight.items(), key=lambda (f, i): i)]
        return result


class BaseDynamicForm(forms.Form):
    '''Base class for forms created from DynamicForm'''

    required_css_class = 'required'

    @property
    def super(custom_form):
        return super(custom_form._dynamicform.form(), custom_form)


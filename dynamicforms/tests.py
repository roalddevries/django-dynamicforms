from django import forms
from django.utils.unittest import TestCase
from django.utils.translation import ugettext_lazy as _
from forms import BaseDynamicForm
from models import DynamicField, DynamicFormFieldRelation, DynamicForm


class BaseForm(BaseDynamicForm):
    email = forms.EmailField()
    phone = forms.CharField()


class Test(TestCase):
    def setUp(self):
        # fields
        self.name_field = DynamicField.objects.create(
            label = 'Name',
            type  = 'text',
        )
        self.email_field = DynamicField.objects.create(
            label = 'E-mail',
            type  = 'email',
        )
        self.phone_field = DynamicField.objects.create(
            label = 'Phone',
            type  = 'text',
        )

        # default form
        self.default_form = DynamicForm.objects.create(
            name = 'Default test form',
            slug = 'default-test-form',
            type = 'default',
        )
        self.default_name_relation = DynamicFormFieldRelation.objects.create(
            dynamicform  = self.default_form,
            field_name   = 'name',
            dynamicfield = self.name_field,
            sort_weight  = 1000,
        )
        self.default_email_relation = DynamicFormFieldRelation.objects.create(
            dynamicform  = self.default_form,
            field_name   = 'email',
            dynamicfield = self.name_field,
            sort_weight  = 2000,
        )

        # mailphone form
        form_types = [k for k, v in DynamicForm.TYPES.iteritems() if v['BASE_FORM'] == 'dynamicforms.tests.BaseForm']
        self.form_type = form_types[0] if form_types else None
        if self.form_type:
            self.mailphone_form = DynamicForm.objects.create(
                name = 'Mail and phone test form',
                slug = 'mail-phone-test-form',
                type = self.form_type,
            )
            self.mailphone_name_relation = DynamicFormFieldRelation.objects.create(
                dynamicform  = self.mailphone_form,
                field_name   = 'name',
                dynamicfield = self.name_field,
                sort_weight  = 1000,
            )

            # mailphone form with overriden email field
            self.override_form = DynamicForm.objects.create(
                name = 'Overriding test form',
                slug = 'overriding-test-form',
                type = self.form_type,
            )
            self.override_name_relation = DynamicFormFieldRelation.objects.create(
                dynamicform  = self.override_form,
                field_name   = 'name',
                dynamicfield = self.name_field,
                sort_weight  = 1000,
            )
            self.override_email_relation = DynamicFormFieldRelation.objects.create(
                dynamicform  = self.override_form,
                field_name   = 'email',
                sort_weight  = 2000,
            )
            self.override_phone_relation = DynamicFormFieldRelation.objects.create(
                dynamicform  = self.override_form,
                field_name   = 'phone',
                sort_weight  = 3000,
            )

    def tearDown(self):
        if self.form_type:
            self.override_phone_relation.delete()
            self.override_email_relation.delete()
            self.override_name_relation.delete()
            self.override_form.delete()
            self.mailphone_name_relation.delete()
            self.mailphone_form.delete()
        self.default_email_relation.delete()
        self.default_name_relation.delete()
        self.default_form.delete()
        self.phone_field.delete()
        self.email_field.delete()
        self.name_field.delete()

    def test_default_form(self):
        form_class = self.default_form.form_class
        self.assertEqual(len(form_class.base_fields), 2)

    def test_mailphone_form(self):
        if self.form_type:
            form_class = self.mailphone_form.form_class
            self.assertEqual(len(form_class.base_fields), 3)

    def test_override_form(self):
        if self.form_type:
            form_class = self.override_form.form_class
            self.assertEqual(len(form_class.base_fields), 3)


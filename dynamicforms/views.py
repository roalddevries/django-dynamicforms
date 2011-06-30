from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template import Context, RequestContext, Template
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from html2text import html2text
from models import DynamicForm, DynamicFormData, HTTP_HEADERS
import rfc822


class ProcessDynamicFormView(FormView):
    @property
    def dynamicform(self):
        if not hasattr(self, '_dynamicform'):
            # NOTE: if the specified slug doesn't exist, its url doesn't exist
            self._dynamicform = get_object_or_404(DynamicForm, slug=self.kwargs['slug'])
        return self._dynamicform

    def get_template_names(self):
        return [self.dynamicform.template]

    def get_form_class(self):
        return self.dynamicform.form_class

    def get_success_url(self):
        return self.dynamicform.get_success_url() or self.dynamicform.get_absolute_url()

    def form_valid(self, form):
        # save the result
        data = DynamicFormData.objects.create(
                dynamicform   = self.dynamicform,
                raw_post_data = self.request.raw_post_data,
                headers       = '\n'.join(
                    '%s: %s' % (h, self.request.META[h])
                    for h in HTTP_HEADERS if h in self.request.META
                    )
                )

        # create confirmation e-mail
        if self.dynamicform.send_confirmation:
            recipients_template = Template(self.dynamicform.email_recipients)
            subject_template    = Template(self.dynamicform.email_subject)
            content_template    = Template(self.dynamicform.email_content)
            context = Context(form.cleaned_data)
            recipients = recipients_template.render(context)
            subject    = subject_template.render(context)
            content    = content_template.render(context)
            msg = EmailMultiAlternatives(
                    force_unicode(subject),
                    html2text(content),
                    settings.DEFAULT_FROM_EMAIL,
                    [address for name, address in rfc822.AddressList(recipients).addresslist],
                    )
            msg.attach_alternative(content, "text/html")
            msg.send()

        # create e-mail for dynamicform manager
        if self.dynamicform.notification_emails:
            recipients = self.dynamicform.notification_emails.split(u',')
            subject = _(u'Form "%s" was posted') % self.dynamicform.name
            context = RequestContext(self.request, {'form': form, 'dynamicform': self.dynamicform, 'dynamicformdata': data})
            content = render_to_string(self.dynamicform.email_template, context_instance=context)
            msg = EmailMultiAlternatives(
                    force_unicode(subject),
                    html2text(content),
                    settings.SERVER_EMAIL,
                    [address for name, address in rfc822.AddressList(recipients).addresslist],
                    )
            msg.attach_alternative(content, "text/html")
            msg.send()

        return super(ProcessDynamicFormView, self).form_valid(form)


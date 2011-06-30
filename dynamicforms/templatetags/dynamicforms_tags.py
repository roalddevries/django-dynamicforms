from django import template
from django.template import Variable
from django.template.loader import get_template
from dynamicforms import models
from dynamicforms.models import DynamicForm


register = template.Library()


class DynamicFormNode(template.Node):
    def __init__(self, dynamicform_slug):
        super(DynamicFormNode, self).__init__()
        self.dynamicform_slug = Variable(dynamicform_slug)

    def render(self, context):
        slug = self.dynamicform_slug.resolve(context)
        dynamicform = DynamicForm.objects.get(slug=slug)
        template = get_template(dynamicform.tag_template)
        context['dynamicform'] = dynamicform
        context['form']        = dynamicform.form_class()
        return template.render(context)


@register.tag
def show_dynamicform(parser, token):
    args = token.split_contents()
    return DynamicFormNode(*args[1:])


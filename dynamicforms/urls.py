from django.conf.urls.defaults import *
from views import ProcessDynamicFormView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/$', ProcessDynamicFormView.as_view(), name='process_dynamicform'),
)

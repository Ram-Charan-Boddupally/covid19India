from django.urls import re_path,path
from . import views 
app_name = 'covidVisulizer'

urlpatterns = [
    path(r'',views.mainVisualizer,name="mainVisualizer"),
    re_path(r'^subLoc/(?P<locName>[\w+]+)/$',views.subLoc,name="subLocVisualizer"),
    re_path(r'^catageory/(?P<catageory>[\w-]+)/$',views.catageoryVisulizer,name='catageoryVisulizer'),
]
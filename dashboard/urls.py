# dag_viewer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dag/', views.dag_view, name='dag_view'),
    path('', views.index, name='dashboard-index'),
    path('refined_edge_matrix/', views.refined_edge_matrix, name='refined_edge_matrix'),
    path('evaluate-bias/', views.evaluate_bias, name='evaluate_bias'),

]

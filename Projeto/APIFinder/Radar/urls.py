from django.urls import path
from . import views

urlpatterns = [
    path('buscar_vaga/<str:pk>',views.buscarvaga),
    path('inserir_vaga',views.insert_vaga),
    path('atualizar_vaga/<str:pk>',views.updatevaga),
    path('excluir_vaga/<str:pk>',views.delete_vaga),
    path('buscar_curriculo/<str:pk>', views.buscarCurriculo),
    path('inserir_curriculo',views.cadastrarCurriculo),
    path('atualizar_curriculo/<str:pk>',views.atualizarCurriculo),
    path('excluir_curriculo/<str:pk>',views.deletarCurriculo),
    path('buscaPorVaga/<str:VagaID>',views.buscarPorVaga),
]


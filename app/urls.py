"""
URLs da aplicação - Rede Acadêmica
Todas as rotas integradas e funcionais
"""

from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    # AUTENTICAÇÃO
    path('', views.logando, name='logando'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logando'), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci_senha'),
    path('admin/', admin.site.urls),
    
    # DASHBOARD 
    path('', views.dashboard, name='dashboard'),  # Página principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # PERFIL 
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('perfil/cargo/<int:cargo_id>/toggle/', views.toggle_cargo, name='toggle_cargo'),
    
    # BUSCA DE USUÁRIOS
    path('busca/', views.busca_usuarios, name='busca_usuarios'),
    path('pesquisa/<int:pk>/remover/', views.remover_pesquisa, name='remover_pesquisa'),
    path('pesquisa/limpar/', views.limpar_pesquisas, name='limpar_pesquisas'),
    
    # CANAIS E CHAT 
    path('canal/criar/', views.criar_canal, name='criar_canal'),
    path('chat/<int:canal_id>/', views.chat, name='chat'),
    path('chat/<int:canal_id>/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    
    # ADMIN 
    path('cargo/criar/', views.criar_cargo, name='criar_cargo'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/chat-request/<int:request_id>/aceitar/', views.aceitar_chat_request, name='aceitar_chat_request'),
    path('admin-panel/chat-request/<int:request_id>/recusar/', views.recusar_chat_request, name='recusar_chat_request'),
    path('admin-panel/cargo-request/<int:request_id>/aceitar/', views.aceitar_cargo_request, name='aceitar_cargo_request'),
    path('admin-panel/cargo-request/<int:request_id>/recusar/', views.recusar_cargo_request, name='recusar_cargo_request'),
    path('admin-panel/usuario/<int:usuario_id>/deletar/', views.deletar_usuario, name='deletar_usuario'),
    path('admin-panel/canal/<int:canal_id>/deletar/', views.deletar_canal, name='deletar_canal'),
    path('admin-panel/cargo/<int:cargo_id>/deletar/', views.deletar_cargo, name='deletar_cargo'),
]
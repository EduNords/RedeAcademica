from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Cargo, UsuarioCargo, Canal, 
    MembroCanal, Mensagem, Reacao, Notificacao,
    Novidade, Evento, Seguidor, PesquisaRecente, ChatRequest, CargoRequest
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'fullname', 'matricula', 'email', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'fullname', 'matricula', 'email')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('fullname', 'matricula', 'bio', 'foto_url', 'created_at')
        }),
    )
    
    readonly_fields = ('created_at',)
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('fullname', 'matricula', 'email', 'bio', 'foto_url')
        }),
    )


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'criado_por', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informações do Cargo', {
            'fields': ('nome', 'descricao', 'cor')
        }),
        ('Metadata', {
            'fields': ('criado_por', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsuarioCargo)
class UsuarioCargoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'ativo', 'atribuido_em')
    list_filter = ('cargo', 'ativo', 'atribuido_em')
    search_fields = ('usuario__username', 'usuario__fullname', 'cargo__nome')
    ordering = ('-atribuido_em',)
    readonly_fields = ('atribuido_em',)


@admin.register(Canal)
class CanalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ativo', 'criado_por', 'total_membros', 'created_at')
    list_filter = ('tipo', 'ativo', 'created_at')
    search_fields = ('nome', 'descricao')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('cargos_permitidos',)
    
    fieldsets = (
        ('Informações do Canal', {
            'fields': ('nome', 'descricao', 'tipo', 'avatar', 'cor_avatar', 'ativo')
        }),
        ('Permissões', {
            'fields': ('cargos_permitidos',),
            'description': 'Cargos que podem acessar este canal (apenas para canais restritos)'
        }),
        ('Metadata', {
            'fields': ('criado_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_membros(self, obj):
        return obj.membros.count()
    total_membros.short_description = 'Membros'


@admin.register(MembroCanal)
class MembroCanalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'canal', 'papel', 'entrou_em', 'ultima_leitura')
    list_filter = ('papel', 'entrou_em', 'canal__tipo')
    search_fields = ('usuario__username', 'usuario__fullname', 'canal__nome')
    ordering = ('-entrou_em',)
    readonly_fields = ('entrou_em',)
    
    fieldsets = (
        ('Informações', {
            'fields': ('usuario', 'canal', 'papel')
        }),
        ('Atividade', {
            'fields': ('entrou_em', 'ultima_leitura')
        }),
    )


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('autor', 'canal', 'conteudo_resumido', 'editada', 'created_at')
    list_filter = ('editada', 'created_at', 'canal')
    search_fields = ('conteudo', 'autor__username', 'canal__nome')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações da Mensagem', {
            'fields': ('canal', 'autor', 'conteudo', 'arquivo')
        }),
        ('Resposta', {
            'fields': ('responde_a',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('editada', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def conteudo_resumido(self, obj):
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_resumido.short_description = 'Conteúdo'


@admin.register(Reacao)
class ReacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensagem_info', 'emoji', 'created_at')
    list_filter = ('emoji', 'created_at')
    search_fields = ('usuario__username', 'mensagem__conteudo')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def mensagem_info(self, obj):
        return f"{obj.mensagem.autor.username} em {obj.mensagem.canal.nome}"
    mensagem_info.short_description = 'Mensagem'


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'lida', 'created_at')
    list_filter = ('tipo', 'lida', 'created_at')
    search_fields = ('usuario__username', 'titulo', 'mensagem')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informações da Notificação', {
            'fields': ('usuario', 'tipo', 'titulo', 'mensagem', 'link')
        }),
        ('Status', {
            'fields': ('lida', 'created_at')
        }),
    )
    
    actions = ['marcar_como_lida', 'marcar_como_nao_lida']
    
    def marcar_como_lida(self, request, queryset):
        updated = queryset.update(lida=True)
        self.message_user(request, f'{updated} notificação(ões) marcada(s) como lida(s).')
    marcar_como_lida.short_description = 'Marcar como lida'
    
    def marcar_como_nao_lida(self, request, queryset):
        updated = queryset.update(lida=False)
        self.message_user(request, f'{updated} notificação(ões) marcada(s) como não lida(s).')
    marcar_como_nao_lida.short_description = 'Marcar como não lida'


# ADMIN PARA DASHBOARD 

@admin.register(Novidade)
class NovidadeAdmin(admin.ModelAdmin):
    list_display = ['fonte', 'titulo', 'data_publicacao', 'ativo']
    list_filter = ['ativo', 'data_publicacao', 'fonte']
    search_fields = ['fonte', 'titulo', 'texto']
    date_hierarchy = 'data_publicacao'
    
    fieldsets = (
        ('Informações da Fonte', {
            'fields': ('fonte', 'avatar', 'cor_avatar')
        }),
        ('Conteúdo', {
            'fields': ('titulo', 'texto', 'ativo')
        }),
        ('Data', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['data_publicacao']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data', 'horario_formatado', 'cor', 'ativo']
    list_filter = ['ativo', 'data', 'cor']
    search_fields = ['titulo', 'descricao']
    date_hierarchy = 'data'
    
    fieldsets = (
        ('Informações do Evento', {
            'fields': ('titulo', 'descricao', 'cor')
        }),
        ('Data e Horário', {
            'fields': ('data', 'horario_inicio', 'horario_fim')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )


# ADMIN PARA BUSCA DE PERFIL

@admin.register(Seguidor)
class SeguidorAdmin(admin.ModelAdmin):
    list_display = ['seguidor', 'seguido', 'data_inicio']
    list_filter = ['data_inicio']
    search_fields = ['seguidor__username', 'seguido__username']
    date_hierarchy = 'data_inicio'
    
    fieldsets = (
        ('Relacionamento', {
            'fields': ('seguidor', 'seguido')
        }),
        ('Data', {
            'fields': ('data_inicio',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['data_inicio']


@admin.register(PesquisaRecente)
class PesquisaRecenteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'usuario_pesquisado', 'data_pesquisa']
    list_filter = ['data_pesquisa']
    search_fields = ['usuario__username', 'usuario_pesquisado__username']
    date_hierarchy = 'data_pesquisa'
    
    readonly_fields = ['data_pesquisa']


@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ('nome', 'solicitado_por', 'status', 'created_at', 'aprovado_por')
    list_filter = ('status', 'tipo', 'created_at')
    search_fields = ('nome', 'descricao', 'solicitado_por__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('cargos_permitidos',)
    
    fieldsets = (
        ('Informações do Canal Solicitado', {
            'fields': ('nome', 'descricao', 'tipo', 'avatar', 'cor_avatar')
        }),
        ('Permissões', {
            'fields': ('cargos_permitidos',),
        }),
        ('Status', {
            'fields': ('status', 'solicitado_por', 'aprovado_por', 'motivo_recusa')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CargoRequest)
class CargoRequestAdmin(admin.ModelAdmin):
    list_display = ('nome', 'solicitado_por', 'status', 'created_at', 'aprovado_por')
    list_filter = ('status', 'created_at')
    search_fields = ('nome', 'descricao', 'solicitado_por__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Cargo Solicitado', {
            'fields': ('nome', 'descricao', 'cor')
        }),
        ('Status', {
            'fields': ('status', 'solicitado_por', 'aprovado_por', 'motivo_recusa')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Configurações globais do Admin
admin.site.site_header = "Rede Acadêmica - Administração"
admin.site.site_title = "Rede Acadêmica Admin"
admin.site.index_title = "Painel de Controle"
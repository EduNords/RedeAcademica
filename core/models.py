from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone


class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=50, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biografia")
    foto_url = models.URLField(
        default='https://images.icon-icons.com/2483/PNG/512/user_icon_149851.png',
        verbose_name="URL da Foto"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
    def __str__(self):
        return self.username


class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo")
    descricao = models.TextField(max_length=300, blank=True, verbose_name="Descrição")
    cor = models.CharField(max_length=7, default="#808080", verbose_name="Cor (hex)")
    criado_por = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cargos_criados',
        verbose_name="Criado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class UsuarioCargo(models.Model):
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='usuario_cargos',
        verbose_name="Usuário"
    )
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name='cargo_usuarios',
        verbose_name="Cargo"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    atribuido_em = models.DateTimeField(auto_now_add=True, verbose_name="Atribuído em")
    
    class Meta:
        verbose_name = "Cargo do Usuário"
        verbose_name_plural = "Cargos dos Usuários"
        unique_together = ('usuario', 'cargo')
        ordering = ['usuario', 'cargo']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.cargo.nome}"


class Canal(models.Model):
    TIPO_CHOICES = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
        ('restrito', 'Restrito por Cargo'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name="Nome do Canal")
    descricao = models.TextField(max_length=500, blank=True, verbose_name="Descrição")
    tipo = models.CharField(
        max_length=10, 
        choices=TIPO_CHOICES, 
        default='publico',
        verbose_name="Tipo de Canal"
    )
    avatar = models.CharField(max_length=10, default='💬', verbose_name="Avatar (emoji)")
    cor_avatar = models.CharField(max_length=20, default='blue', verbose_name="Cor do Avatar")
    criado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='canais_criados',
        verbose_name="Criado por"
    )
    cargos_permitidos = models.ManyToManyField(
        Cargo,
        blank=True,
        related_name='canais',
        verbose_name="Cargos Permitidos",
        help_text="Cargos que podem acessar este canal (apenas para canais restritos)"
    )
    membros = models.ManyToManyField(
        CustomUser,
        through='MembroCanal',
        related_name='canais_membro',
        verbose_name="Membros"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Canal"
        verbose_name_plural = "Canais"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
    def usuario_pode_acessar(self, usuario):
        if self.tipo == 'publico':
            return True
        
        if self.tipo == 'privado':
            return self.membros.filter(id=usuario.id).exists()
        
        if self.tipo == 'restrito':
            cargos_usuario = usuario.usuario_cargos.filter(ativo=True).values_list('cargo_id', flat=True)
            return self.cargos_permitidos.filter(id__in=cargos_usuario).exists()
        
        return False


class MembroCanal(models.Model):
    PAPEL_CHOICES = [
        ('admin', 'Administrador'),
        ('moderador', 'Moderador'),
        ('membro', 'Membro'),
    ]
    
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='membros_canal',
        verbose_name="Usuário"
    )
    canal = models.ForeignKey(
        Canal,
        on_delete=models.CASCADE,
        related_name='canal_membros',
        verbose_name="Canal"
    )
    papel = models.CharField(
        max_length=10,
        choices=PAPEL_CHOICES,
        default='membro',
        verbose_name="Papel no Canal"
    )
    entrou_em = models.DateTimeField(auto_now_add=True, verbose_name="Entrou em")
    ultima_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Última leitura")
    
    class Meta:
        verbose_name = "Membro do Canal"
        verbose_name_plural = "Membros dos Canais"
        unique_together = ('usuario', 'canal')
        ordering = ['canal', '-entrou_em']
    
    def __str__(self):
        return f"{self.usuario.username} em {self.canal.nome} ({self.get_papel_display()})"


class Mensagem(models.Model):
    canal = models.ForeignKey(
        Canal,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name="Canal"
    )
    autor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name="Autor"
    )
    conteudo = models.TextField(verbose_name="Conteúdo")
    arquivo = models.FileField(
        upload_to='mensagens/arquivos/',
        blank=True,
        null=True,
        verbose_name="Arquivo anexo"
    )
    responde_a = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respostas',
        verbose_name="Responde a"
    )
    editada = models.BooleanField(default=False, verbose_name="Editada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviada em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.autor.username} em {self.canal.nome} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Verifica se o usuário pode enviar mensagem no canal
        if not self.canal.usuario_pode_acessar(self.autor):
            raise ValidationError("Você não tem permissão para enviar mensagens neste canal.")
        super().save(*args, **kwargs)


class Reacao(models.Model):
    mensagem = models.ForeignKey(
        Mensagem,
        on_delete=models.CASCADE,
        related_name='reacoes',
        verbose_name="Mensagem"
    )
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reacoes',
        verbose_name="Usuário"
    )
    emoji = models.CharField(max_length=10, verbose_name="Emoji")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    
    class Meta:
        verbose_name = "Reação"
        verbose_name_plural = "Reações"
        unique_together = ('mensagem', 'usuario', 'emoji')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.usuario.username} reagiu com {self.emoji}"


class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('mensagem', 'Nova Mensagem'),
        ('mencao', 'Menção'),
        ('canal', 'Novo Canal'),
        ('cargo', 'Novo Cargo'),
        ('sistema', 'Sistema'),
    ]
    
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name="Usuário"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    lida = models.BooleanField(default=False, verbose_name="Lida")
    link = models.CharField(max_length=500, blank=True, verbose_name="Link")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"


# ============ MODELS PARA DASHBOARD ============

class Novidade(models.Model):
    fonte = models.CharField(max_length=200)
    avatar = models.CharField(max_length=10, default='📢')
    cor_avatar = models.CharField(max_length=20, default='blue')
    titulo = models.CharField(max_length=300)
    texto = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.fonte} - {self.titulo}"
    
    def tempo_decorrido(self):
        from django.utils import timezone
        diff = timezone.now() - self.data_publicacao
        
        if diff.days > 0:
            return f"{diff.days} {'dia' if diff.days == 1 else 'dias'} atrás"
        elif diff.seconds >= 3600:
            horas = diff.seconds // 3600
            return f"{horas} {'hora' if horas == 1 else 'horas'} atrás"
        elif diff.seconds >= 60:
            minutos = diff.seconds // 60
            return f"{minutos} {'minuto' if minutos == 1 else 'minutos'} atrás"
        else:
            return "agora"
    
    class Meta:
        verbose_name = 'Novidade'
        verbose_name_plural = 'Novidades'
        ordering = ['-data_publicacao']


class Evento(models.Model):
    titulo = models.CharField(max_length=300)
    descricao = models.TextField(blank=True, null=True)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    data = models.DateField()
    cor = models.CharField(max_length=20, default='green')
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.data}"
    
    def horario_formatado(self):
        return f"{self.horario_inicio.strftime('%H:%M')} - {self.horario_fim.strftime('%H:%M')}"
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['data', 'horario_inicio']


class Seguidor(models.Model):
    seguidor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='seguindo')
    seguido = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='seguidores_list')
    data_inicio = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.seguidor.username} segue {self.seguido.username}"
    
    class Meta:
        verbose_name = 'Seguidor'
        verbose_name_plural = 'Seguidores'
        unique_together = ['seguidor', 'seguido']


class PesquisaRecente(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pesquisas')
    usuario_pesquisado = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='foi_pesquisado_por')
    data_pesquisa = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} pesquisou {self.usuario_pesquisado.username}"
    
    class Meta:
        verbose_name = 'Pesquisa Recente'
        verbose_name_plural = 'Pesquisas Recentes'
        ordering = ['-data_pesquisa']


class ChatRequest(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]
    
    # Dados do canal solicitado
    nome = models.CharField(max_length=100, verbose_name="Nome do Canal")
    descricao = models.TextField(max_length=500, blank=True, verbose_name="Descrição")
    tipo = models.CharField(
        max_length=10, 
        choices=Canal.TIPO_CHOICES, 
        default='publico',
        verbose_name="Tipo de Canal"
    )
    avatar = models.CharField(max_length=10, default='💬', verbose_name="Avatar (emoji)")
    cor_avatar = models.CharField(max_length=20, default='blue', verbose_name="Cor do Avatar")
    
    # Relacionamentos
    solicitado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='chat_requests',
        verbose_name="Solicitado por"
    )
    cargos_permitidos = models.ManyToManyField(
        Cargo,
        blank=True,
        related_name='chat_requests',
        verbose_name="Cargos Permitidos"
    )
    
    # Status e aprovação
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    aprovado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_requests_aprovadas',
        verbose_name="Aprovado por"
    )
    motivo_recusa = models.TextField(max_length=500, blank=True, verbose_name="Motivo da Recusa")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Solicitação de Chat"
        verbose_name_plural = "Solicitações de Chat"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome} - {self.get_status_display()} ({self.solicitado_por.username})"


class CargoRequest(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]
    
    # Dados do cargo solicitado
    nome = models.CharField(max_length=100, verbose_name="Nome do Cargo")
    descricao = models.TextField(max_length=300, blank=True, verbose_name="Descrição")
    cor = models.CharField(max_length=7, default="#808080", verbose_name="Cor (hex)")
    
    # Relacionamentos
    solicitado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='cargo_requests',
        verbose_name="Solicitado por"
    )
    
    # Status e aprovação
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    aprovado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cargo_requests_aprovadas',
        verbose_name="Aprovado por"
    )
    motivo_recusa = models.TextField(max_length=500, blank=True, verbose_name="Motivo da Recusa")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Solicitação de Cargo"
        verbose_name_plural = "Solicitações de Cargo"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome} - {self.get_status_display()} ({self.solicitado_por.username})"

class Disciplinas(models.Model):
    nome = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class AvaliacaoDisciplina(models.Model):
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)

    contribuicao = models.IntegerField()
    equilibrio = models.IntegerField()
    aplicacao = models.IntegerField()
    material = models.IntegerField()
    distribuicao = models.IntegerField()

    comentario = models.TextField(blank=True, null=True)

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.disciplina.codigo} por {self.usuario}"

class Professores(models.Model):
    nome = models.CharField(max_length=100)
    disciplinas = models.ManyToManyField(Disciplinas, related_name='professores')

    def __str__(self):
        return self.nome


class Avaliacao(models.Model):
    professor = models.ForeignKey(Professores, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)

    dominio = models.IntegerField(null=True, blank=True)
    metodos = models.IntegerField(null=True, blank=True)
    relacionamento = models.IntegerField(null=True, blank=True)
    compatibilidade = models.IntegerField(null=True, blank=True)
    clareza = models.IntegerField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
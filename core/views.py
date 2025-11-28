from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime, timedelta
from random import randint
import calendar

from .forms import (
    CustomUserCreationForm, EditarPerfilForm, 
    CriarCanalForm, EnviarMensagemForm,
    BuscarUsuarioForm, CriarCargoForm, AlterarSenhaForm
)

from .models import (
    CustomUser, Cargo, UsuarioCargo, Canal, MembroCanal, 
    Mensagem, Notificacao, Novidade, Evento, Seguidor, PesquisaRecente, ChatRequest, CargoRequest
)


# AUTENTICAÇÃO 

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 
                f'Bem-vindo(a), {user.fullname}! Sua conta foi criada com sucesso.'
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registro.html', {'form': form})


def logando(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.fullname or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário ou senha incorretos.")
    
    return render(request, 'login.html')


def esqueci_senha(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_token':
            email = request.POST.get('email')

            try:
                user = CustomUser.objects.get(email=email)
                code = str(randint(100000, 999999))

                request.session['reset_email'] = email
                request.session['reset_code'] = code
                request.session['reset_expiration'] = (
                    datetime.now() + timedelta(minutes=15)
                ).isoformat()

                subject = 'Recuperação de Senha - Rede Acadêmica'
                message = f"""
Olá {user.username},

Recebemos uma solicitação de redefinição de senha para sua conta na Rede Acadêmica.

- Seu código de verificação é: {code}
- Ele expira em 15 minutos.  

Caso você não tenha solicitado, basta ignorar este e-mail.

Atenciosamente,
Equipe Rede Acadêmica
"""
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@redeacademica.com'),
                    recipient_list=[email],
                    fail_silently=False,
                )

                messages.success(request, 'Código enviado! Verifique seu e-mail.')
                return render(request, 'esqueci_senha.html', {'email': email})

            except CustomUser.DoesNotExist:
                messages.error(request, 'E-mail não encontrado.')
                return render(request, 'esqueci_senha.html')

        if action == 'reset_password':
            email = request.session.get('reset_email')
            real_code = request.session.get('reset_code')
            expiration = request.session.get('reset_expiration')

            inserted_code = request.POST.get('token')
            new_pass = request.POST.get('password')
            confirm_pass = request.POST.get('confirm_password')

            if not (email and real_code and expiration):
                messages.error(request, '⚠ Envie o código primeiro.')
                return redirect('esqueci_senha')

            if inserted_code != real_code:
                messages.error(request, '❌ Código incorreto.')
                return render(request, 'esqueci_senha.html', {'email': email})

            if datetime.now() > datetime.fromisoformat(expiration):
                messages.error(request, '⏳ Código expirado! Solicite novamente.')
                return redirect('esqueci_senha')

            if new_pass != confirm_pass:
                messages.error(request, 'As senhas não coincidem.')
                return render(request, 'esqueci_senha.html', {'email': email})

            try:
                user = CustomUser.objects.get(email=email)
                user.password = make_password(new_pass)
                user.save()

                request.session.pop('reset_email', None)
                request.session.pop('reset_code', None)
                request.session.pop('reset_expiration', None)

                messages.success(request, 'Senha redefinida com sucesso! Faça o login.')
                return redirect('logando')

            except Exception:
                messages.error(request, 'Erro ao redefinir senha. Tente novamente.')
                return render(request, 'esqueci_senha.html', {'email': email})

    return render(request, 'esqueci_senha.html')


# DASHBOARD 

@login_required
def dashboard(request):
    user = request.user
    hoje = datetime.now()
    
    # Data formatada
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                   'Sexta-feira', 'Sábado', 'Domingo']
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    dia_semana = dias_semana[hoje.weekday()]
    mes_nome = meses[hoje.month - 1]
    data_formatada = f"{dia_semana}, {hoje.day} de {mes_nome} de {hoje.year}"
    
    # Dados do usuário
    usuario = {
        'nome': user.fullname or user.username,
        'foto_url': user.foto_url,
        'notificacoes': True,
    }
    
    # Cargos do usuário
    meus_cargos = UsuarioCargo.objects.filter(
        usuario=user, 
        ativo=True
    ).select_related('cargo')
    cargos_ids = meus_cargos.values_list('cargo_id', flat=True)
    
    # Canais disponíveis
    canais_ids = set()
    
    # Canais públicos
    canais_publicos_ids = Canal.objects.filter(
        tipo='publico', 
        ativo=True
    ).values_list('id', flat=True)
    canais_ids.update(canais_publicos_ids)
    
    # Canais privados (membro)
    canais_privados_ids = Canal.objects.filter(
        tipo='privado',
        ativo=True,
        membros=user
    ).values_list('id', flat=True)
    canais_ids.update(canais_privados_ids)
    
    # Canais restritos (por cargo)
    if cargos_ids:
        canais_restritos_ids = Canal.objects.filter(
            tipo='restrito',
            ativo=True,
            cargos_permitidos__in=cargos_ids
        ).distinct().values_list('id', flat=True)
        canais_ids.update(canais_restritos_ids)
    
    # Buscar canais com dados extras
    canais_disponiveis = Canal.objects.filter(
        id__in=canais_ids
    ).prefetch_related('membros', 'cargos_permitidos')
    
    for canal in canais_disponiveis:
        # Mensagens não lidas
        try:
            membro_canal = canal.canal_membros.get(usuario=user)
            ultima_leitura = membro_canal.ultima_leitura
            
            if ultima_leitura:
                canal.mensagens_nao_lidas = canal.mensagens.filter(
                    created_at__gt=ultima_leitura
                ).count()
            else:
                canal.mensagens_nao_lidas = canal.mensagens.count()
        except:
            canal.mensagens_nao_lidas = 0
        
        # Última mensagem
        canal.ultima_mensagem = canal.mensagens.order_by('-created_at').first()
    
    # Ordenar por última atividade
    canais_disponiveis = sorted(
        canais_disponiveis,
        key=lambda x: x.ultima_mensagem.created_at if x.ultima_mensagem else timezone.make_aware(datetime.min),
        reverse=True
    )
    
    # Novidades
    novidades_db = Novidade.objects.filter(ativo=True)[:10]
    novidades = [{
        'avatar': nov.avatar,
        'avatar_class': nov.cor_avatar,
        'fonte': nov.fonte,
        'tempo': nov.tempo_decorrido(),
        'titulo': nov.titulo,
        'texto': nov.texto
    } for nov in novidades_db]
    
    # Notificações
    notificacoes_nao_lidas = Notificacao.objects.filter(
        usuario=user,
        lida=False
    ).count()
    
    # Calendário
    dia_selecionado = request.GET.get('dia')
    
    if dia_selecionado:
        try:
            data_selecionada = datetime.strptime(dia_selecionado, '%Y-%m-%d').date()
        except:
            data_selecionada = hoje.date()
    else:
        data_selecionada = hoje.date()
    
    cal = calendar.monthcalendar(hoje.year, hoje.month)
    dias_semana_cal = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    
    dias_calendario = []
    for semana in cal:
        for dia in semana:
            dias_calendario.append(dia if dia != 0 else None)
    
    calendario = {
        'mes': f'{mes_nome} {hoje.year}',
        'dias_semana': dias_semana_cal,
        'dias': dias_calendario,
        'dia_atual': hoje.day,
        'dia_selecionado': data_selecionada.day if data_selecionada.month == hoje.month else None,
        'mes_atual': hoje.month,
        'ano_atual': hoje.year,
    }
    
    # Eventos
    eventos_db = Evento.objects.filter(
        data=data_selecionada,
        ativo=True
    ).order_by('horario_inicio')
    
    eventos = [{
        'titulo': evt.titulo,
        'horario': evt.horario_formatado(),
        'cor': evt.cor
    } for evt in eventos_db]
    
    context = {
        'usuario': usuario,
        'user': user,
        'data_formatada': data_formatada,
        'data_eventos': f"{data_selecionada.day:02d}/{data_selecionada.month:02d}/{data_selecionada.year}",
        'novidades': novidades,
        'canais_disponiveis': canais_disponiveis,
        'meus_cargos': meus_cargos,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'calendario': calendario,
        'eventos': eventos,
    }
    
    return render(request, 'dashboard.html', context)


# PERFIL 

@login_required
def perfil(request):
    user = request.user
    
    # Cargos do usuário
    meus_cargos = UsuarioCargo.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('cargo')
    
    cargos = [uc.cargo.nome for uc in meus_cargos]
    cargos_usuario_ids = [uc.cargo.id for uc in meus_cargos]
    
    # Todos os cargos disponíveis
    todos_cargos = Cargo.objects.all()
    
    context = {
        'username': user.username,
        'nome_completo': user.fullname or user.get_full_name() or user.username,
        'matricula': user.matricula,
        'email': user.email,
        'foto_url': user.foto_url,
        'bio': user.bio,
        'cargos': cargos,
        'meus_cargos': meus_cargos,
        'cargos_usuario_ids': cargos_usuario_ids,
        'todos_cargos': todos_cargos,
    }
    
    return render(request, 'perfil.html', context)


@login_required
def toggle_cargo(request, cargo_id):
    user = request.user
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    try:
        usuario_cargo = UsuarioCargo.objects.get(
            usuario=user,
            cargo=cargo
        )
        usuario_cargo.ativo = not usuario_cargo.ativo
        usuario_cargo.save()
        
        if usuario_cargo.ativo:
            messages.success(request, f'Cargo "{cargo.nome}" adicionado!')
        else:
            messages.success(request, f'Cargo "{cargo.nome}" removido!')
            
    except UsuarioCargo.DoesNotExist:
        UsuarioCargo.objects.create(
            usuario=user,
            cargo=cargo,
            ativo=True
        )
        messages.success(request, f'Cargo "{cargo.nome}" adicionado!')
    
    return HttpResponseRedirect(reverse('perfil') + '#modalCargos')


@login_required
def editar_perfil(request):
    user = request.user
    
    if request.method == 'POST':
        # Verifica se está usando o formulário ou POST simples
        if 'form_type' in request.POST and request.POST['form_type'] == 'simple':
            # POST simples (do template antigo)
            novo_email = request.POST.get('email', '').strip()
            nova_foto_url = request.POST.get('foto_url', '').strip()
            nova_bio = request.POST.get('bio', '').strip()
            
            if novo_email:
                user.email = novo_email
                messages.success(request, 'Email atualizado com sucesso!')
            
            if nova_foto_url:
                user.foto_url = nova_foto_url
                messages.success(request, 'Foto atualizada com sucesso!')
            
            if nova_bio:
                user.bio = nova_bio
                messages.success(request, 'Biografia atualizada com sucesso!')
            
            user.save()
            return HttpResponseRedirect(reverse('perfil') + '#modalEditarPerfil')
        
        else:
            # Usando formulário completo
            form = EditarPerfilForm(request.POST, instance=user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('perfil')
            else:
                messages.error(request, 'Por favor, corrija os erros abaixo.')
                
                context = {
                    'form': form,
                    'user': user
                }
                return render(request, 'editar_perfil.html', context)
    
    # GET - renderiza formulário se existir template específico
    form = EditarPerfilForm(instance=user)
    context = {
        'form': form,
        'user': user
    }
    
    return render(request, 'editar_perfil.html', context)


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = AlterarSenhaForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            nova_senha = form.cleaned_data['nova_senha']
            request.user.set_password(nova_senha)
            request.user.save()
            
            # Importante: atualizar a sessão para não deslogar o usuário
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AlterarSenhaForm(user=request.user)
    
    context = {
        'form': form
    }
    
    return render(request, 'alterar_senha.html', context)


# BUSCA DE USUÁRIOS 

@login_required
def busca_usuarios(request):
    user = request.user
    query = request.GET.get('q', '').strip()

    # Busca
    if query:
        perfis = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(fullname__icontains=query) |
            Q(email__icontains=query) |
            Q(matricula__icontains=query)
        )[:10]
    else:
        perfis = []

    # Pesquisas recentes
    pesquisas_db = PesquisaRecente.objects.filter(
        usuario=user
    ).select_related('usuario_pesquisado')[:5]

    # Usuário selecionado
    usuario_selecionado = None

    if query and perfis:
        perfil_selecionado = perfis[0]

        # Salva pesquisa recente
        PesquisaRecente.objects.get_or_create(
            usuario=user,
            usuario_pesquisado=perfil_selecionado
        )

        # Dados do usuário selecionado
        usuario_selecionado = {
            'username': perfil_selecionado.username,
            'fullname': perfil_selecionado.fullname or perfil_selecionado.get_full_name(),
            'foto_url': perfil_selecionado.foto_url,
            'seguidores': Seguidor.objects.filter(seguido=perfil_selecionado).count(),
            'seguindo': Seguidor.objects.filter(seguidor=perfil_selecionado).count(),
            'cargos': [
                uc.cargo.nome for uc in
                UsuarioCargo.objects.filter(
                    usuario=perfil_selecionado, 
                    ativo=True
                ).select_related('cargo')
            ],
            'descricao': perfil_selecionado.bio or f"Matrícula: {perfil_selecionado.matricula}",
        }

    # Dados do usuário logado
    usuario_logado = {
        'foto_url': user.foto_url,
        'notificacoes': Notificacao.objects.filter(usuario=user, lida=False).count(),
    }

    context = {
        'usuario_selecionado': usuario_selecionado,
        'pesquisas_db': pesquisas_db,
        'resultados': perfis,
        'query': query,
        'usuario_logado': usuario_logado,
    }

    return render(request, 'pesquisa.html', context)


@login_required
def remover_pesquisa(request, pk):
    user = request.user
    pesquisa = get_object_or_404(PesquisaRecente, id=pk, usuario=user)
    pesquisa.delete()
    messages.success(request, 'Pesquisa removida.')
    return redirect('busca_usuarios')


@login_required
def limpar_pesquisas(request):
    user = request.user
    count = PesquisaRecente.objects.filter(usuario=user).count()
    PesquisaRecente.objects.filter(usuario=user).delete()
    messages.success(request, f'{count} pesquisa(s) removida(s).')
    return redirect('busca_usuarios')


# CANAIS E CHAT 

@login_required
def chat(request, canal_id):
    canal = get_object_or_404(Canal, id=canal_id)
    
    # Verificar acesso
    if not canal.usuario_pode_acessar(request.user):
        messages.error(request, 'Você não tem permissão para acessar este canal.')
        return redirect('dashboard')
    
    # Processar envio de mensagem
    if request.method == 'POST':
        form = EnviarMensagemForm(request.POST, request.FILES)
        
        if form.is_valid():
            mensagem = Mensagem.objects.create(
                canal=canal,
                autor=request.user,
                conteudo=form.cleaned_data['conteudo'],
                arquivo=form.cleaned_data.get('arquivo')
            )
            
            # Se for resposta a outra mensagem
            responde_a_id = form.cleaned_data.get('responde_a')
            if responde_a_id:
                try:
                    mensagem.responde_a = Mensagem.objects.get(id=responde_a_id)
                    mensagem.save()
                except Mensagem.DoesNotExist:
                    pass
            
            messages.success(request, 'Mensagem enviada!')
            return redirect('chat', canal_id=canal.id)
    else:
        form = EnviarMensagemForm()
    
    # Buscar mensagens
    mensagens = Mensagem.objects.filter(
        canal=canal
    ).select_related('autor').order_by('created_at')
    
    # Atualizar última leitura
    try:
        membro_canal = canal.canal_membros.get(usuario=request.user)
        membro_canal.ultima_leitura = timezone.now()
        membro_canal.save()
    except:
        pass
    
    context = {
        'canal': canal,
        'mensagens': mensagens,
        'form': form,
    }
    
    return render(request, 'chat.html', context)


@login_required
def criar_canal(request):
    if request.method == 'POST':
        form = CriarCanalForm(request.POST)
        
        if form.is_valid():
            # Criar ChatRequest ao invés de Canal diretamente
            chat_request = ChatRequest.objects.create(
                nome=form.cleaned_data['nome'],
                descricao=form.cleaned_data.get('descricao', ''),
                tipo=form.cleaned_data['tipo'],
                avatar=form.cleaned_data.get('avatar', '💬'),
                cor_avatar=form.cleaned_data.get('cor_avatar', 'blue'),
                solicitado_por=request.user,
                status='pendente'
            )
            
            # Adicionar cargos permitidos se houver
            if form.cleaned_data.get('cargos_permitidos'):
                chat_request.cargos_permitidos.set(form.cleaned_data['cargos_permitidos'])
            
            messages.success(
                request, 
                f'Solicitação de canal "{chat_request.nome}" criada com sucesso! Aguarde a aprovação de um administrador.'
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CriarCanalForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'criar_canal.html', context)


@login_required
def enviar_mensagem(request, canal_id):
    canal = get_object_or_404(Canal, id=canal_id)
    
    if not canal.usuario_pode_acessar(request.user):
        messages.error(request, 'Você não tem permissão para enviar mensagens neste canal.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EnviarMensagemForm(request.POST, request.FILES)
        
        if form.is_valid():
            mensagem = Mensagem.objects.create(
                canal=canal,
                autor=request.user,
                conteudo=form.cleaned_data['conteudo'],
                arquivo=form.cleaned_data.get('arquivo')
            )
            
            responde_a_id = form.cleaned_data.get('responde_a')
            if responde_a_id:
                try:
                    mensagem.responde_a = Mensagem.objects.get(id=responde_a_id)
                    mensagem.save()
                except Mensagem.DoesNotExist:
                    pass
            
            messages.success(request, 'Mensagem enviada!')
        else:
            messages.error(request, 'Erro ao enviar mensagem.')
    
    return redirect('chat', canal_id=canal.id)


# ADMIN - CRIAR CARGO 

@login_required
def criar_cargo(request):
    if request.method == 'POST':
        form = CriarCargoForm(request.POST)
        
        if form.is_valid():
            # Criar CargoRequest ao invés de Cargo diretamente
            cargo_request = CargoRequest.objects.create(
                nome=form.cleaned_data['nome'],
                descricao=form.cleaned_data.get('descricao', ''),
                cor=form.cleaned_data.get('cor', '#808080'),
                solicitado_por=request.user,
                status='pendente'
            )
            
            messages.success(
                request, 
                f'Solicitação de cargo "{cargo_request.nome}" criada com sucesso! Aguarde a aprovação de um administrador.'
            )
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CriarCargoForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'criar_cargo.html', context)


# ADMIN PANEL

@login_required
def admin_panel(request):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para acessar o painel de administração.')
        return redirect('dashboard')
    
    # Chat Requests pendentes
    chat_requests = ChatRequest.objects.filter(status='pendente').select_related('solicitado_por').prefetch_related('cargos_permitidos')
    
    # Cargo Requests pendentes
    cargo_requests = CargoRequest.objects.filter(status='pendente').select_related('solicitado_por')
    
    # Estatísticas
    total_usuarios = CustomUser.objects.count()
    total_canais = Canal.objects.count()
    total_cargos = Cargo.objects.count()
    total_chat_requests = ChatRequest.objects.filter(status='pendente').count()
    total_cargo_requests = CargoRequest.objects.filter(status='pendente').count()
    
    # Listas para edição
    usuarios = CustomUser.objects.all().order_by('-created_at')[:50]
    canais = Canal.objects.all().order_by('-created_at')[:50]
    cargos = Cargo.objects.all().order_by('nome')
    
    context = {
        'chat_requests': chat_requests,
        'cargo_requests': cargo_requests,
        'total_usuarios': total_usuarios,
        'total_canais': total_canais,
        'total_cargos': total_cargos,
        'total_chat_requests': total_chat_requests,
        'total_cargo_requests': total_cargo_requests,
        'usuarios': usuarios,
        'canais': canais,
        'cargos': cargos,
    }
    
    return render(request, 'admin_panel.html', context)


@login_required
def aceitar_chat_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    chat_request = get_object_or_404(ChatRequest, id=request_id, status='pendente')
    
    # Criar o canal
    canal = Canal.objects.create(
        nome=chat_request.nome,
        descricao=chat_request.descricao,
        tipo=chat_request.tipo,
        avatar=chat_request.avatar,
        cor_avatar=chat_request.cor_avatar,
        criado_por=chat_request.solicitado_por,
        ativo=True
    )
    
    # Adicionar cargos permitidos
    if chat_request.cargos_permitidos.exists():
        canal.cargos_permitidos.set(chat_request.cargos_permitidos.all())
    
    # Adicionar o criador como admin do canal
    MembroCanal.objects.create(
        usuario=chat_request.solicitado_por,
        canal=canal,
        papel='admin'
    )
    
    # Atualizar status da solicitação
    chat_request.status = 'aprovado'
    chat_request.aprovado_por = request.user
    chat_request.save()
    
    messages.success(request, f'Chat "{canal.nome}" aprovado e criado com sucesso!')
    return redirect('admin_panel')


@login_required
def recusar_chat_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    chat_request = get_object_or_404(ChatRequest, id=request_id, status='pendente')
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        chat_request.status = 'recusado'
        chat_request.aprovado_por = request.user
        chat_request.motivo_recusa = motivo
        chat_request.save()
        
        messages.success(request, f'Solicitação de chat "{chat_request.nome}" recusada.')
        return redirect('admin_panel')
    
    # Se GET, mostrar formulário de recusa
    context = {
        'chat_request': chat_request
    }
    return render(request, 'recusar_chat_request.html', context)


@login_required
def deletar_usuario(request, usuario_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    usuario = get_object_or_404(CustomUser, id=usuario_id)
    
    if usuario == request.user:
        messages.error(request, 'Você não pode deletar seu próprio usuário.')
        return redirect('admin_panel')
    
    username = usuario.username
    usuario.delete()
    messages.success(request, f'Usuário "{username}" deletado com sucesso.')
    return redirect('admin_panel')


@login_required
def deletar_canal(request, canal_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    canal = get_object_or_404(Canal, id=canal_id)
    nome = canal.nome
    canal.delete()
    messages.success(request, f'Canal "{nome}" deletado com sucesso.')
    return redirect('admin_panel')


@login_required
def deletar_cargo(request, cargo_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    cargo = get_object_or_404(Cargo, id=cargo_id)
    nome = cargo.nome
    cargo.delete()
    messages.success(request, f'Cargo "{nome}" deletado com sucesso.')
    return redirect('admin_panel')


@login_required
def aceitar_cargo_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    cargo_request = get_object_or_404(CargoRequest, id=request_id, status='pendente')
    
    # Criar o cargo
    cargo = Cargo.objects.create(
        nome=cargo_request.nome,
        descricao=cargo_request.descricao,
        cor=cargo_request.cor,
        criado_por=cargo_request.solicitado_por
    )
    
    # Atualizar status da solicitação
    cargo_request.status = 'aprovado'
    cargo_request.aprovado_por = request.user
    cargo_request.save()
    
    messages.success(request, f'Cargo "{cargo.nome}" aprovado e criado com sucesso!')
    return redirect('admin_panel')


@login_required
def recusar_cargo_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('dashboard')
    
    cargo_request = get_object_or_404(CargoRequest, id=request_id, status='pendente')
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        cargo_request.status = 'recusado'
        cargo_request.aprovado_por = request.user
        cargo_request.motivo_recusa = motivo
        cargo_request.save()
        
        messages.success(request, f'Solicitação de cargo "{cargo_request.nome}" recusada.')
        return redirect('admin_panel')
    
    # Se GET, mostrar formulário de recusa
    context = {
        'cargo_request': cargo_request
    }
    return render(request, 'recusar_cargo_request.html', context)
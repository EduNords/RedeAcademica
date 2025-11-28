from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Canal, Cargo


class CustomUserCreationForm(UserCreationForm):
    fullname = forms.CharField(
        max_length=255,
        required=True,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome completo',
            'id': 'id_fullname',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'O nome completo é obrigatório.',
        }
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Crie um username',
            'id': 'id_username',
            'class': 'form-control'
        }),
        help_text='Letras, números e @/./+/-/_ apenas.',
        error_messages={
            'required': 'O username é obrigatório.',
        }
    )
    
    matricula = forms.CharField(
        max_length=20,
        required=True,
        label='Matrícula',
        widget=forms.TextInput(attrs={
            'placeholder': '2510934',
            'id': 'id_matricula',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'A matrícula é obrigatória.',
        }
    )
    
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Insira seu e-mail',
            'id': 'id_email',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'O e-mail é obrigatório.',
            'invalid': 'Digite um e-mail válido.',
        }
    )
    
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Crie uma senha segura',
            'id': 'id_password1',
            'class': 'form-control'
        }),
        help_text='Sua senha deve ter pelo menos 8 caracteres.',
        error_messages={
            'required': 'A senha é obrigatória.',
        }
    )
    
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme sua senha',
            'id': 'id_password2',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'A confirmação de senha é obrigatória.',
        }
    )
    
    terms = forms.BooleanField(
        required=True,
        label='Aceito os termos de uso',
        error_messages={
            'required': 'Você deve aceitar os termos de uso para continuar.'
        },
        widget=forms.CheckboxInput(attrs={
            'id': 'id_terms',
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('fullname', 'username', 'matricula', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email.lower()  # Salva em minúsculas para consistência
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if CustomUser.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError("Esta matrícula já está cadastrada.")
        return matricula
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este username já está em uso.")
        return username.lower()  # Salva em minúsculas para consistência
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.fullname = self.cleaned_data['fullname']
        user.matricula = self.cleaned_data['matricula']
        if commit:
            user.save()
        return user


class EditarPerfilForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com'
        })
    )
    
    foto_url = forms.URLField(
        required=False,
        label='URL da Foto de Perfil',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://exemplo.com/minha-foto.jpg'
        }),
        help_text='Cole o link direto da imagem'
    )
    
    bio = forms.CharField(
        required=False,
        label='Biografia',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Conte um pouco sobre você...',
            'rows': 4
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'foto_url', 'bio')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso por outro usuário.")
        return email


class CriarCanalForm(forms.ModelForm):
    nome = forms.CharField(
        max_length=100,
        required=True,
        label='Nome do Canal',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Discussões Gerais'
        })
    )
    
    descricao = forms.CharField(
        required=False,
        label='Descrição',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Descreva o propósito deste canal...',
            'rows': 3
        })
    )
    
    tipo = forms.ChoiceField(
        choices=Canal.TIPO_CHOICES,
        required=True,
        label='Tipo de Canal',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Público: todos podem acessar | Privado: apenas membros | Restrito: apenas cargos específicos'
    )
    
    avatar = forms.CharField(
        max_length=10,
        required=False,
        initial='💬',
        label='Avatar (Emoji)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '💬'
        })
    )
    
    cor_avatar = forms.ChoiceField(
        choices=[
            ('blue', 'Azul'),
            ('green', 'Verde'),
            ('red', 'Vermelho'),
            ('yellow', 'Amarelo'),
            ('purple', 'Roxo'),
            ('gray', 'Cinza'),
        ],
        required=False,
        initial='blue',
        label='Cor do Avatar',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    cargos_permitidos = forms.ModelMultipleChoiceField(
        queryset=Cargo.objects.all(),
        required=False,
        label='Cargos Permitidos',
        widget=forms.CheckboxSelectMultiple(),
        help_text='Selecione os cargos que podem acessar (apenas para canais restritos)'
    )
    
    class Meta:
        model = Canal
        fields = ('nome', 'descricao', 'tipo', 'avatar', 'cor_avatar', 'cargos_permitidos')
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        cargos = cleaned_data.get('cargos_permitidos')
        
        # Se for canal restrito, deve ter pelo menos um cargo
        if tipo == 'restrito' and not cargos:
            raise forms.ValidationError(
                'Canais restritos devem ter pelo menos um cargo permitido.'
            )
        
        return cleaned_data


class EnviarMensagemForm(forms.Form):
    conteudo = forms.CharField(
        required=True,
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua mensagem...',
            'rows': 3
        }),
        error_messages={
            'required': 'A mensagem não pode estar vazia.'
        }
    )
    
    arquivo = forms.FileField(
        required=False,
        label='Anexar arquivo',
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
    
    responde_a = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )


class BuscarUsuarioForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Pesquisar por pessoas',
            'autofocus': True
        })
    )


class CriarCargoForm(forms.ModelForm):
    nome = forms.CharField(
        max_length=100,
        required=True,
        label='Nome do Cargo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Líder da Atlética'
        })
    )
    
    descricao = forms.CharField(
        required=False,
        label='Descrição',
        max_length=300,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Descreva o cargo...',
            'rows': 3
        })
    )
    
    cor = forms.CharField(
        max_length=7,
        required=False,
        initial='#808080',
        label='Cor (Hexadecimal)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'color',
            'value': '#808080'
        })
    )
    
    class Meta:
        model = Cargo
        fields = ('nome', 'descricao', 'cor')
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        # Verificar se já existe um cargo aprovado com este nome
        if Cargo.objects.filter(nome=nome).exists():
            raise forms.ValidationError("Já existe um cargo com este nome.")
        # Verificar se já existe uma solicitação pendente com este nome
        from .models import CargoRequest
        if CargoRequest.objects.filter(nome=nome, status='pendente').exists():
            raise forms.ValidationError("Já existe uma solicitação pendente para um cargo com este nome.")
        return nome


class AlterarSenhaForm(forms.Form):
    
    senha_atual = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        }),
        error_messages={
            'required': 'A senha atual é obrigatória.'
        }
    )
    
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        }),
        help_text='Mínimo de 8 caracteres',
        error_messages={
            'required': 'A nova senha é obrigatória.'
        }
    )
    
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        }),
        error_messages={
            'required': 'A confirmação é obrigatória.'
        }
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_senha_atual(self):
        senha = self.cleaned_data.get('senha_atual')
        if not self.user.check_password(senha):
            raise forms.ValidationError("Senha atual incorreta.")
        return senha
    
    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError("As senhas não coincidem.")
            
            if len(nova_senha) < 8:
                raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        
        return cleaned_data
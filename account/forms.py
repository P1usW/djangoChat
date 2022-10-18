from django import forms
from .models import Account
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm


class UserRegister(UserCreationForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                help_text='')
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(UserRegister, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError('Логин "{}" уже используется.'.format(username))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Почта "{}" уже используется.'.format(email))

    class Meta:
        model = Account
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Почта',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserLogin(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}),
                               help_text='')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               help_text='')

    def clean_username(self):
        return self.cleaned_data['username'].lower()


class ProfileEdit(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_image', 'about_me', 'facebook', 'twitter', 'instagram')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control'}),
            'facebook': forms.TextInput(attrs={'class': 'form-control'}),
            'twitter': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.exclude(username=self.instance.username).get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError('Логин "{}" уже используется.'.format(username))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(email=self.instance.email).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Почта "{}" уже используется.'.format(email))

    def save(self, commit=True):
        account = super(ProfileEdit, self).save(commit=True)
        account.username = self.cleaned_data['username'].lower()
        account.email = self.cleaned_data['email'].lower()
        account.first_name = self.cleaned_data['first_name']
        account.last_name = self.cleaned_data['last_name']
        account.about_me = self.cleaned_data['about_me']
        account.facebook = self.cleaned_data['facebook']
        account.twitter = self.cleaned_data['twitter']
        account.instagram = self.cleaned_data['instagram']
        if commit:
            account.save()
        return account


class PasswordEdit(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='Новый пароль',
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Повторите пароль',
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))


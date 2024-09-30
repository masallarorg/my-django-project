from django import forms  # forms modülünü ekleyin
from .models import Comment  , Reply# Comment modelini de ekleyin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # Comment modeline bağlı bir form oluşturuyoruz
        fields = ['content']  # Yalnızca yorum içeriği alanını alıyoruz
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Yorumunuzu buraya yazın...'})
        }
        labels = {
            'content': 'Yorum'
        }



class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Yanıtınızı buraya yazın...'})
        }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Zorunlu. Geçerli bir email adresi girin.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserDeletionForm(forms.Form):
    confirm = forms.BooleanField(label="Üyeliğimi silmeyi onaylıyorum.")

class ContactForm(forms.Form):
    ad_soyad = forms.CharField(label="Adınız ve Soyadınız", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-posta Adresiniz", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mesaj = forms.CharField(label="Mesajınız", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
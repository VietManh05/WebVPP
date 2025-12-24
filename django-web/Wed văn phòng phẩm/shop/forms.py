"""
Form Django cho Cửa hàng Văn Phòng Phẩm
Các Form: Đăng ký, Đăng nhập, Hồ sơ người dùng
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


# ========== AUTHENTICATION FORMS ==========
class RegisterForm(UserCreationForm):
    """Form đăng ký tài khoản"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên'
        })
    )
    password1 = forms.CharField(
        label='Mật khẩu',
        help_text='Tối thiểu 8 ký tự, không được quá giống tên hoặc tên dùng chung',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu (tối thiểu 8 ký tự)'
        })
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        help_texts = {
            'username': 'Tối đa 150 ký tự. Chỉ chữ, số và @/./+/-/_',
            'email': 'Nhập email hợp lệ',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được đăng ký!')
        return email

    def clean_password1(self):
        """Kiểm tra mật khẩu với các thông báo tùy chỉnh"""
        password1 = self.cleaned_data.get('password1')
        
        if not password1:
            raise forms.ValidationError('Vui lòng nhập mật khẩu!')
        
        if len(password1) < 8:
            raise forms.ValidationError('Mật khẩu phải có tối thiểu 8 ký tự!')
        
        # Kiểm tra mật khẩu không được quá giống tên đăng nhập
        username = self.cleaned_data.get('username', '')
        if username and username.lower() in password1.lower():
            raise forms.ValidationError('Mật khẩu không được quá giống tên đăng nhập!')
        
        # Kiểm tra mật khẩu không được quá giống họ tên
        last_name = self.cleaned_data.get('last_name', '')
        if last_name and last_name.lower() in password1.lower():
            raise forms.ValidationError('Mật khẩu không được quá giống tên!')
        
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Tự động tạo UserProfile
            UserProfile.objects.get_or_create(user=user)
        return user


class LoginForm(forms.Form):
    """Form đăng nhập"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập hoặc Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Nhớ mật khẩu'
    )


class UserProfileForm(forms.ModelForm):
    """Form cập nhật thông tin hồ sơ"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'avatar')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Địa chỉ',
                'rows': 3
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Cập nhật thông tin user
        profile.user.first_name = self.cleaned_data.get('first_name', '')
        profile.user.last_name = self.cleaned_data.get('last_name', '')
        profile.user.email = self.cleaned_data.get('email', '')
        
        if commit:
            profile.user.save()
            profile.save()
        return profile

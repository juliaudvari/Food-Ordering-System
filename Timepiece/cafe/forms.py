from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerProfile, SupportRequest, SupportMessage

class UserRegistrationForm(UserCreationForm):
    # User registration form - implements account creation requirement
    # Collects essential user information for profile creation
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        # Apply Bootstrap styling to all form fields - enhances user experience requirement
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        # Extended user save method that handles profile creation
        # Implements the user account management requirement
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Automatically create customer profile - implements user profile requirement
            CustomerProfile.objects.create(user=user)
        
        return user

class CustomerProfileForm(forms.ModelForm):
    # Customer profile edit form - implements profile management requirement
    # Allows users to provide additional contact information
    class Meta:
        model = CustomerProfile
        fields = ('phone_number', 'address')
        
class SupportRequestForm(forms.ModelForm):
    # Support request form - implements customer service requirement
    # Allows customers to submit help tickets with issues
    class Meta:
        model = SupportRequest
        fields = ('subject', 'description')
        
class SupportMessageForm(forms.ModelForm):
    # Support message form for ongoing communication - part of customer service requirement
    # Enables threaded conversations between staff and customers
    class Meta:
        model = SupportMessage
        fields = ('message',) 
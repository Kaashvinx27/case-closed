from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import DetectiveProfile, Suspect, Evidence


class DetectiveRegistrationForm(forms.ModelForm):
    """
    Registration form for new detectives with password confirmation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Choose a secure passphrase (min 6 characters)',
            'autocomplete': 'new-password'
        }),
        min_length=6,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Confirm your passphrase',
            'autocomplete': 'new-password'
        }),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'e.g. AgentVance or DetectiveMorse',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'bureau.operative@investigations.net',
                'autocomplete': 'email'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This callsign/username is already registered in the Bureau files.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passphrases do not match. Please verify your credentials.")
        return cleaned_data


class DetectiveProfileSettingsForm(forms.ModelForm):
    """
    Form to adjust gameplay preferences (audio, motion, timer).
    """
    class Meta:
        model = DetectiveProfile
        fields = ['sound_enabled', 'reduced_motion', 'show_timer']
        widgets = {
            'sound_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reduced_motion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_timer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AccusationForm(forms.Form):
    """
    Backend-validated formal accusation submission form.
    """
    suspect_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    motive = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Enter the underlying motive...'
        })
    )
    supporting_evidence_ids = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    reasoning = forms.CharField(
        required=True,
        min_length=15,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'rows': 4,
            'placeholder': 'Detail your chronological deduction and why the evidence invalidates the suspect alibi...'
        })
    )

import datetime

from django import forms
from django.forms import widgets
from app import models


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=255)
    telephone_number = forms.CharField(max_length=20)
    type_of_company_id = forms.IntegerField()
    amount_of_staff = forms.IntegerField(max_value=1000)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput())

    def save(self):
        username = self.cleaned_data['username']
        telephone_number = self.cleaned_data['telephone_number']
        company_name = self.cleaned_data['company_name']
        type_of_company_id = self.cleaned_data['type_of_company_id']
        amount_of_staff = self.cleaned_data['amount_of_staff']
        password = self.cleaned_data['password']
        type_of_company = models.TypeCompany.objects.filter(id=type_of_company_id).first()
        company = models.Company.objects.create(phone=telephone_number, type=type_of_company,
                                                amount_of_staff=amount_of_staff, name=company_name)
        models.User.objects.create_user(username=username, password=password, company=company, is_staff=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            models.User.objects.get(username=username)
        except:
            pass
        else:
            raise forms.ValidationError("Bunday username mavjud.")
        return username

    def clean_type_of_company_id(self):
        typy_of = self.cleaned_data['type_of_company_id']
        if not typy_of:
            raise forms.ValidationError('Kompaniya turini tanlang.')
        return typy_of

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput())


class PositionModelForm(forms.ModelForm):
    class Meta:
        model = models.Position
        exclude = ('company',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'info': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StaffORGSystemModelForm(forms.ModelForm):
    class Meta:
        model = models.StaffORGSystem
        exclude = ('company',)


class StaffModelForm(forms.ModelForm):
    race = forms.ModelChoiceField(queryset=models.StaffRace.objects.all(), empty_label='Millati')
    group_name = forms.ModelChoiceField(queryset=models.CompanyScheduleName.objects.all(), empty_label='Ish rejimini')

    class Meta:
        model = models.Staff
        exclude = ('company',)
        widgets = {
            'race': forms.TextInput(attrs={'id': "staff-race"})
        }

    def clean_usernmae(self):
        username = self.cleaned_data['username']

        if models.Staff.objects.filter(username=username):
            raise forms.ValidationError('Bu username oldin kiritilgan')
        
        return username


class DepartmentsModelForm(forms.ModelForm):
    class Meta:
        model = models.Department
        exclude = ('company',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'info': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SalaryModelForm(forms.ModelForm):
    class Meta:
        model = models.Salary
        exclude = ('staff',)

        widgets = {
            'type_of_work': forms.TextInput(attrs={'class': 'form-control', 'id': 'type_of_work'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'attached_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class VacationModelForm(forms.ModelForm):
    class Meta:
        model = models.Vacation
        exclude = ('staff',)


class VacationTypeModelForm(forms.ModelForm):
    class Meta:
        model = models.VacationType
        exclude = ('company',)


class AdditionalPaymentsModelForm(forms.ModelForm):
    class Meta:
        model = models.AdditionalPayments
        exclude = ('staff',)


class AdditionalPaymentTypeModelForm(forms.ModelForm):
    class Meta:
        model = models.AdditionalPaymentType
        exclude = ('company',)


class DocumentModelForm(forms.ModelForm):
    class Meta:
        model = models.Document
        exclude = ('staff',)


class BotModelForm(forms.ModelForm):
    class Meta:
        model = models.Bot
        exclude = ('company',)


class AdminModelForm(forms.ModelForm):
    class Meta:
        model = models.Admin
        exclude = ('company',)


class EntryTextModelForm(forms.ModelForm):
    # content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = models.EntryText
        exclude = ('company',)


class FinishTextModelForm(forms.ModelForm):
    class Meta:
        model = models.FinishText
        exclude = ('company',)


# class TrainingInfoModelForm(forms.ModelForm):
#     class Meta:
#         model = models.TrainingInfo
#         exclude = ('company',)
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#         }


class AdoptationModelForm(forms.ModelForm):
    class Meta:
        model = models.AdoptationModel
        exclude = ['videos', 'files', 'company', 'urls']

        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trening titlini kiriting'}),
            'text': forms.Textarea(attrs={'placeholder': 'Matn kiriting'}),
        }

class TrainingModelForm(forms.ModelForm):
    class Meta:
        model = models.TrainingModel
        exclude = ['videos', 'files', 'company', 'urls']

        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trening titlini kiriting'}),
            'text': forms.Textarea(attrs={'placeholder': 'Matn kiriting'}),
        }

class CompanyModelForm(forms.ModelForm):
    class Meta:
        model = models.Company
        exclude = ('company', 'payment_status', 'payment_paid')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomi'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Telefon raqami"}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manzili'}),
            'creator': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asoschisi'}),
            'info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ma\'lumot'}),
            'amount_of_staff': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ishchilar soni'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Video'}),
            'logo': forms.ClearableFileInput(attrs={'label': None, 'class': 'form-control', 'placeholder': 'logo'}),
        }


class CompanyCultureModelForm(forms.ModelForm):
    class Meta:
        model = models.CompanyCulture
        exclude = ('company',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CompanyScheduleNameForm(forms.ModelForm):
    class Meta:
        model = models.CompanyScheduleName
        fields = '__all__'
        widgets = {
            'name': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'text', 'placeholder': "Ish rejimi nomini kiriting"}),
        }


class CompanyScheduleModelForm(forms.ModelForm):
    class Meta:
        model = models.CompanySchedule
        exclude = ('company', 'name')
        widgets = {
            'start_work': forms.TimeInput(
                attrs={'class': 'form-control col-md-4', 'type': 'time'}),
            'lunch_start': forms.TimeInput(attrs={'class': 'form-control col-md-4', 'type': 'time'}),
            'lunch_end': forms.TimeInput(attrs={'class': 'form-control col-md-4', 'type': 'time'}),
            'end_work': forms.TimeInput(attrs={'class': 'form-control col-md-4', 'type': 'time'}),
        }


class SuperStaffsModelForm(forms.ModelForm):
    class Meta:
        model = models.SuperStaffs
        exclude = ('company',)
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'style': 'height:100px'}),
        }

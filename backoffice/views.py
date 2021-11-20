import json
import os
from datetime import datetime, timedelta
from io import BytesIO
from django import http
from django import urls

import pendulum
import qrcode
from PIL import Image, ImageDraw
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files import File
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, QueryDict, request
from django.shortcuts import render, redirect
from django.template.defaulttags import csrf_token
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.db.models import Q
from app import models
from . import forms
from django.conf import settings


def calculation_the_date_of_late(that_date, start_work_time, work_time):
    company_staffs = work_time.staff_set.all()
    # TODO: came ni create_at ga o'zgartir!!!
    flows = models.Flow.objects.filter(staff__in=company_staffs, came__date=that_date)
    flows_all = flows.filter(came__time__gt=start_work_time)
    ll = flows_all.values_list('staff__pk', flat=True)
    return set(ll)


def find_birthdays(request) -> list:
    start_date = pendulum.now().subtract(days=2)
    end_date = pendulum.now().add(days=7)
    birth_day = []

    while start_date <= end_date:
        birth_day.extend(request.user.company.staff_set.filter(birth_date__month=start_date.month,
                                                               birth_date__day=start_date.day))
        start_date += timedelta(days=1)

    return birth_day


class MainTemplate(LoginRequiredMixin, generic.ListView):
    queryset = models.Staff.objects.all()
    template_name = 'backoffice/pages/index.html'

    DAYS_OF_WEEK = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(MainTemplate, self).get_context_data(object_list=None, **kwargs)
        k_day = pendulum.now().day_of_week

        # user count by date
        result = [0, 0, 0, 0, 0, 0, 0]
        try:
            schedule_name = self.request.user.company.companyschedulename_set.all()
            for i in schedule_name:
                schedules = i.companyschedule_set.all()
                if schedules:
                    for j in range(k_day, 0, -1):
                        that_day = pendulum.now().subtract(days=k_day - j).strftime('%Y-%m-%d')
                        start_work_time = schedules.get(day=self.DAYS_OF_WEEK.get(j - 1)).start_work
                        if start_work_time:
                            late_count = len(calculation_the_date_of_late(that_day, start_work_time, i))
                        else:
                            late_count = 0
                        result[j - 1] += late_count
                print(result)
            today = datetime.today().date()

            schedules = self.request.user.company.companyschedulename_set.all()
            late_today = list()
            for i in schedules:
                start_work = i.companyschedule_set.get(day=self.DAYS_OF_WEEK[today.weekday()]).start_work
                if start_work:
                    staff_id = calculation_the_date_of_late(today, start_work, i)
                    late_today.extend(models.Staff.objects.filter(id__in=staff_id))

            ctx['late_today'] = late_today
            came_today = [i for i in self.request.user.company.staff_set.all() for j in
                          models.Flow.objects.filter(came__date=datetime.today()) if i.id == j.staff.id]
            ctx['absent_today'] = [i for i in self.request.user.company.staff_set.all() if i not in came_today]
        except:
            ctx['late_today'] = ""
            ctx['absent_today'] = ""

        ctx['late_came_person_count_per_day'] = result

        ctx['birth_day'] = find_birthdays(self.request)

        all_stafs = self.request.user.company.staff_set.all().count()
        ctx['male_count'] = self.request.user.company.staff_set.filter(gender='male').count()
        ctx['width_male'] = int(ctx['male_count'] * 100 / all_stafs)
        ctx['female_count'] = self.request.user.company.staff_set.filter(gender='female').count()
        ctx['width_female'] = 100 - ctx['width_male']
        return ctx


class TableTemplate(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backoffice/pages/table/table.html'


# Staff
class StaffListTemplate(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/staff/list.html'
    model = models.Staff

    def get_context_data(self, *, object_list=None, **kwargs):
        staff = super(StaffListTemplate, self).get_context_data(**kwargs)
        company = self.request.user.company
        staff['staffs'] = models.Staff.objects.filter(company=company).order_by('-created_at')
        return staff


class StaffUpdate(LoginRequiredMixin, generic.UpdateView, generic.DetailView):
    template_name = 'backoffice/pages/staff/detail.html'
    form_class = forms.StaffModelForm
    model = models.Staff
    context_object_name = 'staff'
    queryset = models.Staff.objects.all()

    def get_form(self, form_class=None):
        form = super(StaffUpdate, self).get_form(form_class)
        form.fields['group_name'].queryset = models.CompanyScheduleName.objects.filter(
            company=self.request.user.company)
        return form

    def get_success_url(self):
        staff_id = self.kwargs['pk']
        return reverse_lazy('staff-detail', kwargs={'pk': staff_id})

    def form_valid(self, form):
        form.save()
        return super(StaffUpdate, self).form_valid(form)

    def form_invalid(self, form):
        return super(StaffUpdate, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self.request.user.company
        ctx['positions'] = models.Position.objects.filter(company=company).order_by('-created_at')
        ctx['departments'] = models.Department.objects.filter(company=company).order_by('-created_at')
        staff_id = self.kwargs.get('pk')
        salary = models.Salary.objects.filter(staff_id=staff_id).last()
        ctx['salary'] = salary
        additional_payment = models.AdditionalPayments.objects.filter(staff_id=staff_id).last()

        return ctx


class StaffCreate(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/staff/create.html'
    model = models.Staff
    form_class = forms.StaffModelForm
    success_url = reverse_lazy('staff')

    def get_form(self, form_class=None):
        form = super(StaffCreate, self).get_form(form_class)
        form.fields['group_name'].queryset = models.CompanyScheduleName.objects.filter(
            company=self.request.user.company)
        return form

    def get_context_data(self, **kwargs):
        ctx = super(StaffCreate, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['departments'] = models.Department.objects.filter(company=company).order_by('-created_at')
        ctx['positions'] = models.Position.objects.filter(company=company).order_by('-created_at')
        return ctx

    def form_valid(self, form):
        staff = form.save(commit=False)
        company = self.request.user.company
        staff.company = company
        staff.save()
        # ******************************** Qr code generate *****************************
        qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        user_data = {
            'id': staff.id,
        }
        qr_code_image = qrcode.make(user_data)
        canvas = Image.new('RGB', (300, 300), 'white')
        ImageDraw.Draw(canvas)
        canvas.paste(qr_code_image)
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        staff.qr_code.save(f"{staff.first_name}_{staff.last_name}.png", File(buffer), save=False)
        staff.save()
        canvas.close()
        # *****************************************
        messages.success(self.request, 'Xodim yaratildi !!!')
        return HttpResponseRedirect(reverse_lazy('staff'))

    def form_invalid(self, form):
        return super(StaffCreate, self).form_invalid(form)


class StaffDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Staff
    form_class = forms.StaffModelForm
    success_url = reverse_lazy('staff')

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.warning(self.request, "Xodim o'chirildi!!!")
            return HttpResponseRedirect(reverse_lazy('staff'))
        except:
            print("asd")


# Authentication
class LoginPage(LoginView):
    template_name = 'backoffice/regist/login.html'
    success_url = reverse_lazy('backoffice-main')


class Registration(generic.FormView):
    template_name = 'backoffice/regist/registartion.html'
    form_class = forms.RegistrationForm
    success_url = reverse_lazy('backoffice-main')

    def get_context_data(self, **kwargs):
        response = super(Registration, self).get_context_data(**kwargs)
        response['types'] = models.TypeCompany.objects.all()
        return response

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


# Position
class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/department/create.html'
    form_class = forms.PositionModelForm
    success_url = reverse_lazy('position')

    def get_form(self, form_class=None):
        f = super().get_form(form_class)
        f.fields['parent'].queryset = self.request.user.company.position_set.all()
        return f

    def form_valid(self, form):
        from django.contrib import messages
        self.position = form.save(commit=False)
        company = self.request.user.company
        self.position.company = company
        self.position.save()
        messages.success(self.request, 'Xodim lavozimi yaratildi')
        return HttpResponseRedirect(reverse_lazy('position'))


class PositionListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/department/list.html'
    queryset = models.Position.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        position = super(PositionListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        position['positions'] = models.Position.objects.filter(company=company)
        return position


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'backoffice/pages/department/update.html'
    form_class = forms.PositionModelForm
    model = models.Position
    success_url = reverse_lazy('position')

    def form_valid(self, form):
        self.position = form.save(commit=False)
        company = self.request.user.company
        self.position.company = company
        self.position.save()
        messages.success(self.request, "Xodim lavozimi o'zgartirildi")
        return HttpResponseRedirect(reverse_lazy('position'))


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    # template_name = 'backoffice/pages/department/delete.html'
    queryset = models.Position.objects.all()
    form_class = forms.PositionModelForm
    success_message = "deleted..."
    success_url = '/backoffice/position'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.warning(self.request, "Xodim lavozimi o'chirildi!!!")
            return HttpResponseRedirect(reverse_lazy('position'))
        except:
            print("asd")


# StaffORGSystem
class StaffORGSystemListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/staff_org/list.html'
    queryset = models.StaffORGSystem.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        position = super(StaffORGSystemListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        position['items'] = models.StaffORGSystem.objects.filter(company=company)
        return position


class StaffORGSystemCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/staff_org/create.html'
    form_class = forms.StaffORGSystemModelForm
    success_url = reverse_lazy('staff_org_system')

    def get_form(self, form_class=None):
        f = super().get_form(form_class)
        f.fields['staff'].queryset = self.request.user.company.staff_set.all()
        f.fields['parent'].queryset = models.StaffORGSystem.objects.filter(company=self.request.user.company)
        return f

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)


class StaffORGSystemUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'backoffice/pages/staff_org/update.html'
    form_class = forms.StaffORGSystemModelForm
    model = models.StaffORGSystem
    context_object_name = "staff_org_system"
    success_url = reverse_lazy('staff_org_system')

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)


class StaffORGSystemDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.StaffORGSystem.objects.all()
    form_class = forms.StaffORGSystemModelForm
    success_url = reverse_lazy('staff_org_system')


# Departments
class DepartmentListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/departments/list.html'
    queryset = models.Department.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(DepartmentListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['departments'] = models.Department.objects.filter(company=company).order_by('-created_at')
        return ctx


class DepartmentDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.Department.objects.all()
    form_class = forms.DepartmentsModelForm
    success_url = reverse_lazy('department')

    def delete(self, request, *args, **kwargs):
        super(DepartmentDeleteView, self).delete(request, *args, **kwargs)
        messages.warning(self.request, "Bo'lim o'chirildi !!!")
        return HttpResponseRedirect(reverse_lazy('department'))


class DepartmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'backoffice/pages/departments/update.html'
    form_class = forms.DepartmentsModelForm
    model = models.Department
    context_object_name = 'department'
    success_url = reverse_lazy('department')

    def get_context_data(self, **kwargs):
        ctx = super(DepartmentUpdateView, self).get_context_data(**kwargs)
        questions = models.Question.objects.filter(department_id=self.kwargs.get('pk'))
        ctx['questions'] = questions
        return ctx

    def form_valid(self, form):
        self.department = form.save(commit=False)
        post_questions = self.request.POST.getlist('field_name')
        company = self.request.user.company
        self.department.company = company
        self.department.save()
        questions_a = models.Question.objects.filter(department_id=self.kwargs.get('pk'))
        for pk, question in enumerate(questions_a):
            question.question = post_questions[pk - 1]
            question.save()
        super(DepartmentUpdateView, self).form_valid(form)
        messages.success(self.request, "Bo'lim o'zgartirildi !!!")
        return HttpResponseRedirect(reverse_lazy('department'))

    def form_invalid(self, form):
        return super(DepartmentUpdateView, self).form_invalid(form)


class DepartmentCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/departments/create.html'
    form_class = forms.DepartmentsModelForm
    success_url = reverse_lazy('department')

    def form_valid(self, form):
        self.department = form.save(commit=False)
        questions = self.request.POST.getlist('field_name')
        company = self.request.user.company
        self.department.company = company
        self.department.save()
        for question in questions:
            models.Question.objects.create(question=question, department=self.department)
        messages.success(self.request, "Bo'lim yaratildi !!!")
        return HttpResponseRedirect(reverse_lazy('department'))


# Salary
class SalaryListView(LoginRequiredMixin, generic.CreateView):
    model = models.Salary
    template_name = 'backoffice/pages/salary/list.html'
    form_class = forms.SalaryModelForm

    def get_success_url(self):
        staff_id = self.kwargs.get('pk')
        return reverse_lazy('salary', kwargs={'pk': staff_id})

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(SalaryListView, self).get_context_data(**kwargs)
        staff_id = self.kwargs.get('pk')
        ctx['staff'] = models.Staff.objects.get(id=staff_id)
        ctx['salaries'] = models.Salary.objects.filter(staff=staff_id).order_by('-id')
        return ctx

    def form_valid(self, form):
        staff_id = self.kwargs['pk']
        self.object = form.save(commit=False)
        staff = models.Staff.objects.get(pk=staff_id)
        self.object.staff = staff
        self.object.save()
        messages.success(self.request, 'Xodim ish haqqi biriktirildi')
        return HttpResponseRedirect(reverse_lazy('salary', kwargs={'pk': staff_id}))

    def form_invalid(self, form):
        return super(SalaryListView, self).form_invalid(form)


# @login_required
# def salary_update_view(request, pk):
#     salary = models.Salary.objects.get(id=pk)
#     if request.method == 'POST':
#         form = forms.SalaryModelForm(request.POST)
#         if form.is_valid():
#             salary.type_of_work = form.cleaned_data['type_of_work']
#             salary.work_type = form.cleaned_data['work_type']
#             salary.amount = form.cleaned_data['amount']
#             salary.attached_date = form.cleaned_data['attached_date']
#             salary.completion_date = form.cleaned_data['completion_date']
#             salary.save()
#             return redirect('salary', pk=salary.staff.id)
#         else:
#             return redirect('salary', pk=salary.staff.id)

class SalaryDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Staff
    template_name = 'backoffice/pages/staff/list.html'


class SalaryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Salary
    form_class = forms.SalaryModelForm
    template_name = 'backoffice/pages/salary/list.html'

    def get_success_url(self):
        staff_id = models.Salary.objects.get(id=self.object.id).staff.id
        return reverse_lazy('salary', kwargs={'pk': staff_id})

    def get_context_data(self, **kwargs):
        ctx = super(SalaryUpdateView, self).get_context_data(**kwargs)
        print(self.get_form_kwargs())

        staff = models.Salary.objects.get(id=self.object.id).staff
        ctx['update'] = True
        ctx['update_form'] = self.get_form()
        ctx['staff'] = staff
        ctx['salaries'] = staff.salary_set.order_by('-id')
        return ctx


@login_required
def salary_delete_view(request, pk):
    id = models.Salary.objects.get(id=pk).staff.id
    if request.method == "POST":
        models.Salary.objects.filter(id=pk).delete()

        return redirect('salary', pk=id)
    return redirect('backoffice-main')


# Vacation
class VacationCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/vacation/list.html'
    form_class = forms.VacationModelForm
    model = models.Vacation

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(VacationCreateView, self).get_context_data(**kwargs)
        staff_id = self.kwargs.get('pk')
        company = self.request.user.company
        ctx['staff'] = models.Staff.objects.get(id=staff_id)
        ctx['vacations'] = models.Vacation.objects.filter(staff_id=staff_id)
        ctx['vacation_types'] = models.VacationType.objects.filter(company=company)
        ctx['staff_id'] = staff_id
        return ctx

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('vacation', kwargs={'pk': staff_id})

    def form_valid(self, form):
        print("123")
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        self.object = form.save(commit=False)
        staff = models.Staff.objects.get(pk=staff_id)
        self.object.staff = staff
        self.object.save()
        messages.warning(self.request, "Qo'shimcha dam olish biriktirildi !!!")
        return reverse_lazy('vacation', kwargs={'pk': staff_id})

    def form_invalid(self, form):
        return super(VacationCreateView, self).form_invalid(form)


class VacationDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.Vacation.objects.all()
    form_class = forms.VacationModelForm

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('vacation', kwargs={'pk': staff_id})

    def delete(self, request, *args, **kwargs):
        super(VacationDeleteView, self).delete(request, *args, **kwargs)
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        messages.warning(self.request, "Qo'shimcha dam olish o'chirildi !!!")
        return reverse_lazy('vacation', kwargs={'pk': staff_id})


class VacationUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.VacationModelForm
    model = models.Vacation

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('vacation', kwargs={'pk': staff_id})

    def form_valid(self, form):
        super(VacationUpdateView, self).form_valid(form)
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        messages.warning(self.request, "Qo'shimcha dam olish biriktirildi !!!")
        return reverse_lazy('vacation', kwargs={'pk': staff_id})


# VacationType
class VacationTypeTypeListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/vacation/vacation_type/list.html'
    model = models.VacationType

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(VacationTypeTypeListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        # staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        # ctx['staff'] = models.Staff.objects.get(id=staff_id)
        prev_page = self.request.META['HTTP_REFERER']
        ctx['prev_page'] = prev_page
        ctx['vacation_types'] = models.VacationType.objects.filter(company=company)
        return ctx


class VacationTypeCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = forms.VacationTypeModelForm
    model = models.VacationType
    success_url = reverse_lazy('vacation_type')

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(VacationTypeCreateView, self).form_invalid(form)


class VacationTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.VacationType
    form_class = forms.VacationTypeModelForm
    success_url = reverse_lazy('vacation_type')


class VacationTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.VacationType
    form_class = forms.VacationTypeModelForm
    success_url = reverse_lazy('vacation_type')


# AdditionalPayments
class AdditionalPaymentsCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/additional_payments/list.html'
    form_class = forms.AdditionalPaymentsModelForm
    model = models.AdditionalPayments

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(AdditionalPaymentsCreateView, self).get_context_data(**kwargs)
        staff_id = self.kwargs.get('pk')
        company = self.request.user.company
        ctx['staff'] = models.Staff.objects.get(id=staff_id)
        ctx['additional_payments'] = models.AdditionalPayments.objects.filter(staff_id=staff_id)
        ctx['additional_payments_type'] = models.AdditionalPaymentType.objects.filter(company=company)
        ctx['staff_id'] = staff_id
        return ctx

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('additional_payment', kwargs={'pk': staff_id})

    def form_valid(self, form):
        print("123")
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        self.object = form.save(commit=False)
        staff = models.Staff.objects.get(pk=staff_id)
        self.object.staff = staff
        self.object.save()
        return super(AdditionalPaymentsCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(AdditionalPaymentsCreateView, self).form_invalid(form)


class AdditionalPaymentsDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.AdditionalPayments.objects.all()
    form_class = forms.AdditionalPaymentsModelForm
    success_message = "deleted..."

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('additional_payment', kwargs={'pk': staff_id})


class AdditionalPaymentsUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.AdditionalPaymentsModelForm
    model = models.AdditionalPayments

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('additional_payment', kwargs={'pk': staff_id})


# AdditionalPaymentsType
class AdditionalPaymentsTypeListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/additional_payments/additional_peyments_type/list.html'
    model = models.AdditionalPayments

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(AdditionalPaymentsTypeListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['additional_payments_types'] = models.AdditionalPaymentType.objects.filter(company=company)
        return ctx


class AdditionalPaymentsTypeCreateView(LoginRequiredMixin, generic.CreateView):
    # template_name = 'backoffice/pages/additional_payments/additional_peyments_type/list.html'
    form_class = forms.AdditionalPaymentTypeModelForm
    model = models.AdditionalPayments
    success_url = reverse_lazy('additional_payment_type')

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        messages.success(self.request, "Ushlab qolish yoki qo’shimcha to’lovlar nomini yaratildi")
        return HttpResponseRedirect(reverse_lazy('additional_payment_type'))

    def form_invalid(self, form):
        return super(AdditionalPaymentsTypeCreateView, self).form_invalid(form)


class AdditionalPaymentsTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.AdditionalPaymentType
    form_class = forms.AdditionalPaymentTypeModelForm
    success_url = reverse_lazy('additional_payment_type')

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.warning(self.request, "Ushlab qolish yoki qo’shimcha to’lovlar nomi o'chirildi!!!")
            return HttpResponseRedirect(reverse_lazy('additional_payment_type'))
        except:
            print("asd")


class AdditionalPaymentsTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.AdditionalPaymentType
    form_class = forms.AdditionalPaymentTypeModelForm
    success_url = reverse_lazy('additional_payment_type')

    def form_valid(self, form):
        super(AdditionalPaymentsTypeUpdateView, self).form_valid(form)
        messages.warning(self.request, "Ushlab qolish yoki qo’shimcha to’lovlar nomi o'zgartirildi!!!")
        return HttpResponseRedirect(reverse_lazy('additional_payment_type'))


# Document
class DocumentListCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/document/list.html'
    form_class = forms.DocumentModelForm
    model = models.Document

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(DocumentListCreateView, self).get_context_data(**kwargs)
        staff_id = self.kwargs.get('pk')
        ctx['documents'] = models.Document.objects.filter(staff_id=staff_id)
        ctx['staff_id'] = staff_id
        return ctx

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('document', kwargs={'pk': staff_id})

    def form_valid(self, form):
        print("123")
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        self.object = form.save(commit=False)
        staff = models.Staff.objects.get(pk=staff_id)
        self.object.staff = staff
        self.object.save()
        messages.success(self.request, 'Xujjat biriktirildi')
        return HttpResponseRedirect(reverse_lazy('document', kwargs={'pk': staff_id}))

    def form_invalid(self, form):
        return super(DocumentListCreateView, self).form_invalid(form)


class DocumentDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.Document.objects.all()
    form_class = forms.DocumentModelForm

    def delete(self, request, *args, **kwargs):
        super(DocumentDeleteView, self).delete(*args, **kwargs)
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        messages.success(self.request, "Xujjat o'chirildi")
        return HttpResponseRedirect(reverse_lazy('document', kwargs={'pk': staff_id}))

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('document', kwargs={'pk': staff_id})


class DocumentUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.DocumentModelForm
    model = models.Document

    def get_success_url(self):
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        return reverse_lazy('document', kwargs={'pk': staff_id})

    def form_valid(self, form):
        super(DocumentUpdateView, self).form_valid(form)
        staff_id = self.request.META['HTTP_REFERER'].split("/")[-1]
        messages.success(self.request, "Xujjat o'zgartirildi")
        return HttpResponseRedirect(reverse_lazy('document', kwargs={'pk': staff_id}))


# NewTelegramStaff
class NewTelegramStaffListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/new-telegram-staff/list.html'
    queryset = models.NewStaff.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(NewTelegramStaffListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['new_staffs'] = models.NewStaff.objects.filter(company=company)
        return ctx


class NewTelegramStaffDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'backoffice/pages/new-telegram-staff/detail.html'
    queryset = models.NewStaff.objects.all()
    context_object_name = 'new_staff'

    def get_context_data(self, **kwargs):
        ctx = super(NewTelegramStaffDetailView, self).get_context_data(**kwargs)
        company = self.request.user.company
        new_staff = models.NewStaff.objects.filter(company=self.request.user.company)
        ctx['answers'] = models.Answer.objects.filter(candidate__company=self.request.user.company)
        return ctx


# -----------------------------------------------------------------------------------------


# Settings
class Settings(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backoffice/pages/settings/index.html'


# Bot
class BotListView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/bot/list.html'
    queryset = models.Bot.objects.all()
    form_class = forms.BotModelForm
    model = models.Bot
    success_url = reverse_lazy('bot_c_l')

    def generate_bot(self, token, company_id):
        bot_path = str(settings.BASE_DIR) + '/app/sample_bot.py'
        with open(bot_path) as f:
            new_bot = f.read().replace('TOKEN = None', f'TOKEN = "{token}"')

        # bot_conf = str(settings.BASE_DIR) + "/bot/conf/bot_conf.conf"
        # bot_conf_new = "/etc/supervisor/conf.d/bot_conf_{}.conf".format(user_id)

        new_bot_path = str(settings.BASE_DIR) + f'/app/bot/bot_{company_id}.py'
        with open(new_bot_path, "w") as f:
            f.write(new_bot)
        service_config = f"""
[Unit]
Description=uWSGI Emperor service

[Service]
WorkingDirectory=/var/www/hr_project/project
#ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown ubuntu:www-data /run/uwsgi'
ExecStart=/var/www/hr_project/venv/bin/python /var/www/hr_project/project/app/bot/bot_{company_id}.py --serve-in-foreground
Restart=always
KillSignal=SIGQUIT
Type=idle

[Install]
WantedBy=multi-user.target
        """
        with open(f'/etc/systemd/system/bot_{company_id}.service', 'w') as f:
            f.write(service_config)

        # with open(bot_conf) as f:
        #     newText = f.read().replace('[program:bot]', '[program:bot_{}]'.format(user_id))
        #     newText = newText.replace('command=/bot/venv/bin/python /bot/bots/bot_father.py', 'command=/bot/venv/bin/python /bot/bots/bot_{}.py'.format(user_id))
        os.system(f"systemctl daemon-reload")
        os.system(f"systemctl restart bot_{company_id}.service")
        # with open(bot_conf_new, "w") as f:
        #     f.write(newText)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(BotListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['bot_list'] = models.Bot.objects.filter(company=company).first()
        return ctx

    def form_valid(self, form):
        self.bot = form.save(commit=False)
        company = self.request.user.company
        self.bot.company = company
        self.bot.save()
        token = form.data.get('token')
        self.generate_bot(token, self.bot.company.id)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(BotListView, self).form_invalid(form)


class BotUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.BotModelForm
    model = models.Bot
    success_url = reverse_lazy('bot_c_l')


# Admin
class AdminCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/bot_admin/list.html'
    form_class = forms.AdminModelForm
    model = models.Admin
    success_url = reverse_lazy('admin_bot')

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(AdminCreateView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['admin_lists'] = models.Admin.objects.filter(company=company)
        return ctx

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(AdminCreateView, self).form_invalid(form)


class AdminDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.Admin.objects.all()
    form_class = forms.AdminModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('admin_bot')


class AdminUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.AdminModelForm
    model = models.Admin
    success_url = reverse_lazy('admin_bot')


# Admin
class EntryTextCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/entry/list.html'
    form_class = forms.EntryTextModelForm
    model = models.EntryText
    success_url = reverse_lazy('entry_text')

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(EntryTextCreateView, self).get_context_data(**kwargs)
        company = self.request.user.company
        entry_text = models.EntryText.objects.filter(company=company).last()
        ctx['item'] = entry_text
        return ctx

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(EntryTextCreateView, self).form_invalid(form)


class EntryTextDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    queryset = models.EntryText.objects.all()
    form_class = forms.EntryTextModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('entry_text')


class EntryTextUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.EntryTextModelForm
    model = models.EntryText
    success_url = reverse_lazy('entry_text')


# Company
class CompanyTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backoffice/pages/company/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(CompanyTemplateView, self).get_context_data(**kwargs)
        ctx['company'] = models.User.objects.get(company=self.request.user.company)
        ctx['item'] = models.Company.objects.get(id=self.request.user.company.id)
        return ctx


class CompanyUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'backoffice/pages/company/update.html'
    form_class = forms.CompanyModelForm
    model = models.Company
    success_url = reverse_lazy('info')


class SearchingStaffListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/staff_search/list.html'
    model = models.Staff

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(SearchingStaffListView, self).get_context_data(**kwargs)
        ctx['searching_staffs'] = models.Staff.objects.filter(company=self.request.user.company)
        return ctx


# FinishText
class FinishTextCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/finish/list.html'
    form_class = forms.FinishTextModelForm
    model = models.FinishText
    success_url = reverse_lazy('finish_text')

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(FinishTextCreateView, self).get_context_data(**kwargs)
        company = self.request.user.company
        finish_text = models.FinishText.objects.filter(company=company).last()
        ctx['item'] = finish_text
        return ctx

    def form_valid(self, form):
        self.company = form.save(commit=False)
        company = self.request.user.company
        self.company.company = company
        self.company.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(FinishTextCreateView, self).form_invalid(form)


class FinishTextDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    queryset = models.FinishText.objects.all()
    form_class = forms.FinishTextModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('finish_text')


class FinishTexttUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.FinishTextModelForm
    model = models.FinishText
    success_url = reverse_lazy('finish_text')


# Control the flowing staff
class ControlFlowingStaffTemplateView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/control_flowing_staffs/index.html'
    model = models.Flow

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(ControlFlowingStaffTemplateView, self).get_context_data(**kwargs)
        import datetime
        staff_flows = self.request.user.company.staff_set.filter(
            flow__created_at__date=datetime.datetime.today().date()).values(
            'pk').annotate(count=Count('pk'))
        flows_list = []
        for staff_flow in staff_flows:
            flows_list.append(staff_flow.get('pk'))
        ctx['staff_flows'] = models.Staff.objects.filter(id__in=flows_list)
        return ctx


# TrainingInfo
class TrainingInfoTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backoffice/pages/trainig-info/index.html'
    # model = models.TrainingInfo

    def get_context_data(self, **kwargs):
        ctx = super(TrainingInfoTemplateView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['items'] = company.adoptationmodel_set.all()
        ctx['staffs'] = company.staff_set.all()
        return ctx

@login_required
def adoptation_create_view(request):
    form = forms.AdoptationModelForm()
    form.fields['position'].queryset = request.user.company.position_set.all()

    if request.method == 'POST':
        form = forms.AdoptationModelForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company

            instance.save()

            for i in request.FILES.getlist('videos'):
                v = models.AdoptationVideos.objects.create(video=i)
                instance.videos.add(v)
            
            for i in request.FILES.getlist('files'):
                v = models.AdoptationFiles.objects.create(file=i)
                instance.files.add(v)

            import re
            for i in request.POST.getlist('urls'):
                print('/embed/'.join(i.split('/watch?v=')))
                v = models.AdoptationUrls.objects.create(url='/embed/'.join(i.split('/watch?v=')))
                instance.urls.add(v)

            instance.save()

            if request.POST.getlist('question')[0]:
                a = [models.AdoptationQuestions(question=i, adopt=instance) for i in request.POST.getlist('question')]
                models.AdoptationQuestions.objects.bulk_create(a)


            return redirect('training_info')
        else:
            form.fields['position'].queryset = request.user.company.position_set.all()
    
    return render(request, 'backoffice/pages/trainig-info/create.html', {'form': form})


class TrainingInfoDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'backoffice/pages/trainig-info/index.html'
    model = models.AdoptationModel
    form_class = forms.AdoptationModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('training_info')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.request.user.company.adoptationmodel_set.all()
        ctx['staffs'] = self.request.user.company.staff_set.all()
        ctx['delete'] = True
        return ctx


class TrainingInfoUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.TrainingInfoModelForm
    model = models.TrainingInfo
    success_url = reverse_lazy('training_info')

    def form_valid(self, form):
        super(TrainingInfoUpdateView, self).form_valid(form)
        messages.success(self.request, "Xodim adaptatsiyasi o'zgartirildi !!!")
        return HttpResponseRedirect(reverse_lazy('training_info'))


# TrainingAnswerListView
class TrainingAnswerListView(LoginRequiredMixin, generic.ListView):
    template_name = 'backoffice/pages/trainig-info/answer.html'
    model = models.Staff

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(TrainingAnswerListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        ctx['staffs'] = models.Staff.objects.filter(company=company)
        ctx['answers'] = models.TrainingAnswer.objects.filter(staff__company=company)
        return ctx


# CompanyCulture
class CompanyCultureCreateViewListView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/company-culture/index.html'
    form_class = forms.CompanyCultureModelForm
    success_url = reverse_lazy('company_culture')
    model = models.CompanyCulture

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CompanyCultureCreateViewListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        training_info = models.CompanyCulture.objects.filter(company=company)
        ctx['items'] = training_info
        return ctx

    def form_valid(self, form):
        self.company = form.save(commit=False)
        self.company.company = self.request.user.company
        self.company.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return super(CompanyCultureCreateViewListView, self).form_invalid(form)


class CompanyCultureDeleteView(LoginRequiredMixin, generic.DeleteView):
    queryset = models.CompanyCulture.objects.all()
    form_class = forms.CompanyCultureModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('company_culture')


class CompanyCultureUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.CompanyCultureModelForm
    model = models.CompanyCulture
    success_url = reverse_lazy('company_culture')

    def form_valid(self, form):
        super(CompanyCultureUpdateView, self).form_valid(form)
        messages.success(self.request, "Kompaniya madaniyati o'zgartirildi !!!")
        return HttpResponseRedirect(reverse_lazy('company_culture'))


# CompanySchadule
@login_required
def clear_schedule_time(request, t_id, name_id):
    models.CompanySchedule.objects.filter(id=t_id).update(start_work=None, end_work=None, lunch_start=None,
                                                          lunch_end=None)
    return redirect('company_schedule_detail', pk=name_id)


@login_required
def create_company_schedule_name(request):
    form_name = forms.CompanyScheduleNameForm
    form_time = forms.CompanyScheduleModelForm
    my_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule_name_list = request.user.company.companyschedulename_set.all()

    ctx = {
        'form_name': form_name,
        'form_time': form_time,
        'list': my_list,
        'form_error': False,
        'schedule_name_list': schedule_name_list
    }

    if request.method == 'POST':
        company = request.user.company
        form_name = forms.CompanyScheduleNameForm(
            {'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken'), 'name': request.POST.get('name'),
             'company': company})
        if form_name.is_valid():
            # models.CompanyScheduleName.objects.create(name=form_name.cleaned_data['name'], company=company)
            form_name.save()
            instance = request.user.company.companyschedulename_set.get(name=form_name.cleaned_data['name'])
            for i in range(len(my_list)):
                form_time = forms.CompanyScheduleModelForm(
                    {'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken'), 'day': my_list[i].lower(),
                     'name': instance, 'start_work': dict(request.POST).get('start_work')[i],
                     'end_work': dict(request.POST).get('end_work')[i],
                     'lunch_start': dict(request.POST).get('lunch_start')[i],
                     'lunch_end': dict(request.POST).get('lunch_end')[i], 'company': company})

                # models.CompanySchedule.objects.create(**form_time.cleaned_data)
                if form_time.is_valid():
                    models.CompanySchedule.objects.create(
                        name=instance,
                        day=form_time.cleaned_data['day'],
                        company=request.user.company,
                        start_work=form_time.cleaned_data['start_work'],
                        end_work=form_time.cleaned_data['end_work'],
                        lunch_start=form_time.cleaned_data['lunch_start'],
                        lunch_end=form_time.cleaned_data['lunch_end'],
                    )
                    # form_time.save()

                    ctx['messages'] = ['Kompaniya ish rejimi yaratildi!!!']
                else:
                    ctx['form_error'] = True
        else:
            ctx['form_error'] = True

    return render(request, 'backoffice/pages/company-schedule/schedule_name.html', ctx)


class DeleteCompanyScheduleName(LoginRequiredMixin, generic.DeleteView):
    template_name = 'backoffice/pages/company-schedule/schedule_name.html'
    model = models.CompanyScheduleName

    def get_success_url(self):
        return reverse_lazy('company_schedule')

    def get_context_data(self, **kwargs):
        ctx = super(DeleteCompanyScheduleName, self).get_context_data(**kwargs)
        ctx['delete_schedule_name'] = True
        ctx['schedule_name_list'] = self.request.user.company.companyschedulename_set.all()
        return ctx


@login_required
def update_company_schedule_name(request, pk):
    object = request.user.company.companyschedulename_set.all().get(id=pk)
    time_list = object.companyschedule_set.all()
    name_list = request.user.company.companyschedulename_set.all()

    if request.method == 'POST':
        company = models.Company.objects.get(id=request.user.company.id)
        my_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        if request.POST.get('name'):
            request.user.company.companyschedulename_set.filter(id=pk).update(name=request.POST.get('name'),
                                                                              company=company)
            # form_name.save()
            instance = request.user.company.companyschedulename_set.get(name=request.POST.get('name'))
            for i in range(len(my_list)):
                form_time = forms.CompanyScheduleModelForm(
                    {'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken'), 'day': my_list[i].lower(),
                     'name': instance, 'start_work': dict(request.POST).get('start_work')[i],
                     'end_work': dict(request.POST).get('end_work')[i],
                     'lunch_start': dict(request.POST).get('lunch_start')[i],
                     'lunch_end': dict(request.POST).get('lunch_end')[i], 'company': company})

                # models.CompanySchedule.objects.create(**form_time.cleaned_data)
                if form_time.is_valid():
                    print('validate')
                    models.CompanySchedule.objects.filter(name=object, day=my_list[i].lower()).update(
                        name=instance,
                        day=form_time.cleaned_data['day'],
                        company=request.user.company,
                        start_work=form_time.cleaned_data['start_work'],
                        end_work=form_time.cleaned_data['end_work'],
                        lunch_start=form_time.cleaned_data['lunch_start'],
                        lunch_end=form_time.cleaned_data['lunch_end'],
                    )
            return redirect('company_schedule')

    ctx = {
        'form': object,
        'update_list': time_list,
        'schedule_name_list': name_list
    }
    return render(request, 'backoffice/pages/company-schedule/schedule_name.html', ctx)


class UpdateCompanyScheduleTime(LoginRequiredMixin, generic.UpdateView):
    template_name = 'backoffice/pages/company-schedule/index.html'
    model = models.CompanySchedule
    form_class = forms.CompanyScheduleModelForm

    def get_success_url(self):
        return reverse('company_schedule_detail', kwargs={'pk': self.object.name.id})

    def get_context_data(self, **kwargs):
        ctx = super(UpdateCompanyScheduleTime, self).get_context_data(**kwargs)
        ctx['update_time'] = True
        ctx['time_list'] = models.CompanySchedule.objects.filter(name__pk=self.object.name.id)
        return ctx


class DetailCompanyScheduleName(LoginRequiredMixin, generic.DetailView):
    template_name = 'backoffice/pages/company-schedule/index.html'
    model = models.CompanyScheduleName

    def get_queryset(self):
        return self.request.user.company.companyschedulename_set.all()

    def get_context_data(self, **kwargs):
        ctx = super(DetailCompanyScheduleName, self).get_context_data(**kwargs)
        ctx['time_list'] = self.object.companyschedule_set.all()
        return ctx


# Super Staff
class SuperStaffCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'backoffice/pages/super-staff/index.html'
    form_class = forms.SuperStaffsModelForm
    success_url = reverse_lazy('super_staff')
    model = models.SuperStaffs

    def get_form(self, form_class=None):
        f = super().get_form(form_class)
        f.fields['staff'].queryset = self.request.user.company.staff_set.all()
        return f

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(SuperStaffCreateView, self).get_context_data(**kwargs)
        company = self.request.user.company
        company_super_staff = models.SuperStaffs.objects.filter(company=company)
        ctx['items'] = company_super_staff
        return ctx

    def form_valid(self, form):
        self.company = form.save(commit=False)
        self.company.company = self.request.user.company
        self.company.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(SuperStaffCreateView, self).form_invalid(form)


class SuperStaffDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.SuperStaffs
    form_class = forms.SuperStaffsModelForm
    success_message = "deleted..."
    success_url = reverse_lazy('super_staff')


class SuperStaffUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.SuperStaffsModelForm
    model = models.SuperStaffs
    success_url = reverse_lazy('super_staff')

    def form_valid(self, form):
        super(SuperStaffUpdateView, self).form_valid(form)
        messages.success(self.request, "Shuxrat burchagi o'zgartirildi !!!")
        return HttpResponseRedirect(reverse_lazy('super_staff'))

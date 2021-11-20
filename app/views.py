from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from app import forms
from app import models
import uuid

from .models import Company


# Staff Login
class StaffLoginTemplateView(generic.FormView):
    template_name = 'app/staff/login.html'
    form_class = forms.StaffLoginForm
    success_url = 'staff-training'

    def form_valid(self, form):
        print(form)
        staff = models.Staff.objects.filter(username=form.data.get('username')).first()
        staff.training_url = uuid.uuid4()
        self.success_url = reverse('staff_training', kwargs={'staff_uuid': staff.training_url})
        staff.save()
        return super().form_valid(form)


class StaffFormView(generic.FormView):
    template_name = 'app/staff/treining/index.html'
    form_class = forms.StaffTrainingQuestionForm
    success_url = 'staff-login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_uuid = self.kwargs.get('staff_uuid')
        staff = models.Staff.objects.get(training_url=staff_uuid)
        salary = models.Salary.objects.filter(staff=staff).last()
        staff_company = staff.company
        staff_position = staff.position
        test = models.AdoptationModel.objects.filter(company=staff_company, position=staff_position)
        print(test)
        context['staff'] = staff
        context['salary'] = salary
        context['test'] = test
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # return redirect('staff_login')
        return response

    def form_valid(self, form):
        super().form_valid(form)
        staff_uuid = self.kwargs.get('staff_uuid')
        staff = models.Staff.objects.get(training_url=staff_uuid)
        training_answers = models.TrainingAnswer.objects.filter(staff=staff)
        for training_answer in training_answers:
            training_answer.answer = form.data.get(f'{training_answer.id}')
            training_answer.save()
        return redirect('staff_login')

    def form_invalid(self, form):
        return super().form_invalid(form)


def select_test_view(request):
    if request.method == 'GET':
        test = models.AdoptationModel.objects.filter(id=request.GET.get('id')).first()
        videos = list(test.videos.all().values())
        url_videos = list(test.urls.all().values())
        files = list(test.files.all().values())
        questions = list(test.adoptationquestions_set.all().values())
        return JsonResponse({'videos': videos, 'url_videos': url_videos, 'files': files, 'questions': questions})
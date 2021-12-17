from django.http.response import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views import generic
from app import forms
from app import models
from django.utils import timezone
import uuid


from .models import Company
from payments.models import FreeTrial

# Staff Login
class StaffLoginTemplateView(generic.FormView):
    template_name = 'app/staff/login.html'
    form_class = forms.StaffLoginForm
    success_url = 'staff-training'

    def form_valid(self, form):
        print(form)
        staff = models.Staff.objects.filter(username=form.data.get('username')).first()
        staff.training_url = uuid.uuid4()
        company = staff.company
        free_trial_days = FreeTrial.objects.last().days
        if not company.payment_expire_date:                
                    if company.created_at + timezone.timedelta(days=free_trial_days) < timezone.localtime(timezone.now()):
                        messages.error(self.request, 'Kompaniya aktiv holatda emas')
                        return redirect('staff_login') 
        else:
            if company.created_at + timezone.timedelta(days=free_trial_days) < timezone.localtime(timezone.now()) and company.payment_expire_date  < timezone.localtime(timezone.now()):
                messages.error(self.request, 'Kompaniya aktiv holatda emas')
                return redirect('staff_login')
        self.success_url = reverse('staff_training', kwargs={'staff_uuid': staff.training_url})
        staff.save()
        return super().form_valid(form)


class StaffFormView(generic.TemplateView):
    template_name = 'app/staff/treining/index.html'
    form_class = forms.StaffTrainingQuestionForm
    success_url = reverse_lazy('staff_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_uuid = self.kwargs.get('staff_uuid')
        self.staff = models.Staff.objects.get(training_url=staff_uuid)
        salary = models.Salary.objects.filter(staff=self.staff).last()
        staff_company = self.staff.company
        staff_position = self.staff.position
        test = models.AdoptationModel.objects.filter(company=staff_company, position=staff_position)
        print(test)
        context['staff'] = self.staff
        context['salary'] = salary
        context['test'] = test
        return context

    def dispatch(self, request, *args, **kwargs) -> HttpResponseBadRequest:

        staff_uuid = self.kwargs.get('staff_uuid')
        self.staff = models.Staff.objects.get(training_url=staff_uuid)

        if request.method == 'POST':
            ids = request.POST.getlist('question')
            answers = request.POST.getlist('answer')

            print(ids, answers)

            for i in answers:
                index = answers.index(i)
                try:
                    question = models.AdoptationQuestions.objects.get(id=ids[index])
                    models.StaffAnswers.objects.create(question=question, staff=self.staff, answer=i)
                except:
                    continue
            
        
            return redirect('staff_login')

        return super().dispatch(request, *args, **kwargs)


def select_test_view(request):
    if request.method == 'GET':
        test = models.AdoptationModel.objects.filter(id=request.GET.get('id')).first()
        videos = list(test.videos.all().values())
        url_videos = list(test.urls.all().values())
        files = list(test.files.all().values())
        questions = list(test.adoptationquestions_set.all().values())
        print(questions)
        return JsonResponse({'videos': videos, 'url_videos': url_videos, 'files': files, 'questions': questions})
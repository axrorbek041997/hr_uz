from django.contrib import admin
from app import models
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html


@admin.register(models.Company)
class CompanyModelAdmin(admin.ModelAdmin):
    pass


class QuestionStackedInline(admin.StackedInline):
    extra = 0
    min_num = 1
    model = models.Question


@admin.register(models.Department)
class DepartmentModelAdmin(admin.ModelAdmin):
    inlines = [QuestionStackedInline]
    exclude = ()


@admin.register(models.Position)
class PositionModelAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 50


@admin.register(models.StaffORGSystem)
class StaffORGSystemDraggableMPTTAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 50


@admin.register(models.Staff)
class StaffModelAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'second_name', 'last_name', 'mobile_phone']
    search_fields = ['first_name', 'second_name', 'last_name']


class AnswerStackedInline(admin.StackedInline):
    model = models.Answer
    readonly_fields = ['question', 'answer']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.NewStaff)
class NewCandidateModelAdmin(admin.ModelAdmin):
    inlines = [AnswerStackedInline]
    exclude = ()
    readonly_fields = ('department', 'position')


@admin.register(models.Vacancy)
class VacationVacancy(admin.ModelAdmin):
    pass


@admin.register(models.Promotion)
class PromotionModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.VacationType)
class VacationTypeModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SuperStaffs)
class SuperStaffsModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Vacation)
class VacationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AdditionalPaymentType)
class AdditionalPaymentTypeModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AdditionalPayments)
class AdditionalPaymentsModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Flow)
class FlowModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TypeCompany)
class CurrencyModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Document)
class DocumentModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Salary)
class SalaryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Bot)
class BotModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EntryText)
class EntryTextModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.FinishText)
class FinishTextModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Admin)
class AdminModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CompanyScheduleName)
class CompanyScheduleNameModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CompanySchedule)
class CompanyScheduleModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.AdoptationVideos)
admin.site.register(models.AdoptationFiles)
admin.site.register(models.AdoptationUrls)
admin.site.register(models.AdoptationModel)
admin.site.register(models.AdoptationQuestions)


@admin.register(models.User)
class UserModelAdmin(admin.ModelAdmin):
    exclude = (
        'last_login',
        'is_staff',
        'is_active',
        'date_joined',
        'groups',
        'user_permissions',
        'is_superuser',
    )


admin.site.register(models.Branch)

admin.site.register(models.RaceCountry)
admin.site.register(models.StaffRace)


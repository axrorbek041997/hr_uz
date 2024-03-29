import datetime
from ckeditor import fields
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver

def get_directory(instance, filename):
    return 'files/{0}/{1}'.format(f'{instance.first_name} {instance.second_name} {instance.last_name}', filename)


class TypeCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kompaniya turini nomi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Kompaniya turi"

    def __str__(self):
        return self.name


# class Qurilma(models.Model):
#     name = models.CharField(max_length=100)
#     company = models.ForeignKey('Company', on_delete=models.CASCADE)


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kompaniya nomi")
    phone = models.CharField(max_length=25, null=True, blank=True, verbose_name="Kompaniya telefon raqami")
    type = models.ForeignKey(TypeCompany, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="Kompaniya turi")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Kompaniya manzili")
    #
    creator = models.CharField(max_length=255, null=True, blank=True, verbose_name="Kompaniya asoschisi")
    text = RichTextUploadingField(null=True, blank=True, verbose_name="Kompaniya haqida qisqacha ma'lumot")
    video = models.FileField(upload_to='company/video/', null=True, blank=True,
                             verbose_name="Kompaniya haqida qisqacha video")
    info = models.TextField(null=True, blank=True, verbose_name="Bot uchun qisqacha ma'lumot")
    logo = models.ImageField(upload_to='company/image/', null=True, blank=True, verbose_name="Kompaniya logotipi")
    amount_of_staff = models.IntegerField(verbose_name="Hodimlar soni", default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_expire_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name="To'lov tugash muddati")
    
    def __str__(self):
        return f'#{self.id}  {self.name}'

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Kompaniya ma'lumotini qo'shish"


class CompanyScheduleName(models.Model):
    name = models.CharField(max_length=100, unique=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        unique_together = ['name', 'company']


class CompanySchedule(models.Model):
    DAYS_OF_THE_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.ForeignKey(CompanyScheduleName, on_delete=models.CASCADE, default=None, null=True)
    day = models.CharField(choices=DAYS_OF_THE_WEEK, max_length=15)
    start_work = models.TimeField(verbose_name="Ish boshlanishi", default=None, blank=True, null=True)
    lunch_start = models.TimeField(verbose_name="Tushlik vaqti", default=None, blank=True, null=True)
    lunch_end = models.TimeField(verbose_name="Tushlik tugash vaqti", default=None, blank=True,
                                 null=True)
    end_work = models.TimeField(verbose_name="Ish Tugash vaqti", default=None, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.day} - {self.name}'


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Filial")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Filial"

    def __str__(self):
        return self.name


class User(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Filial")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Kompaniya')
    is_director = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "HR"

    def save(self, *args, **kwargs):
        if not 'sha256' in self.password:
            self.set_password(self.password)
        super().save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="Bo'lim nomi")
    info = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bo'lim haqida")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Kompaniya')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bo'limlar"


class Position(MPTTModel):
    name = models.CharField(max_length=255, verbose_name="Lavozim nomi")
    info = models.CharField(max_length=255, null=True, blank=True, verbose_name='Lavozim haqida')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Kompaniya')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        ordering = ['-created_at']
        verbose_name_plural = "Lavozim"


class Promotion(models.Model):
    surcharge = models.BooleanField(default=False, verbose_name="Jarima")
    reward = models.BooleanField(default=False, verbose_name="Mukofot")
    note = models.CharField(max_length=512, null=True, blank=True, verbose_name="Izoh")
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name="Xodim")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Xodimlarga jarima mukofot e'lon qilish"

    def __str__(self):
        return f'{self.staff.first_name} {self.staff.second_name} {self.staff.last_name}'


class VacationType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    create_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kompaniya")

    class Meta:
        verbose_name_plural = "Xodimlaring qo'shimcha dam olish turi"

    def __str__(self):
        return self.name


class Vacation(models.Model):
    vocation_period_type = (
        ('per_hour', 'Soatbay'),
        ('per_day', 'Kunbay')
    )
    vocation_period_types = models.CharField(choices=vocation_period_type, null=True, blank=True, max_length=255,
                                             verbose_name="Turi")
    start_at = models.DateField(verbose_name="Boshlash vaqti")
    end_at = models.DateField(verbose_name="Tugash vaqti")
    vacation_type = models.ForeignKey(VacationType, on_delete=models.CASCADE, verbose_name="Qo'shimcha dam olish turi")
    note = models.CharField(max_length=512, null=True, blank=True, verbose_name="Izoh")
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name="Xodim")

    class Meta:
        verbose_name_plural = "Xodimlaring qo'shimcha dam olish bo'limi"

    def __str__(self):
        return f'{self.staff.first_name} {self.staff.second_name} {self.staff.last_name}'


class AdditionalPaymentType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kompaniya")
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Ushlab qolish yoki qo'shimcha to'lovlar nomi"

    def __str__(self):
        return self.name


class AdditionalPayments(models.Model):
    additional_payment = (
        ('find', "Ushlab qolish"),
        ('additional_payment', "Qo'shimcha to'lov")
    )
    apt = models.ForeignKey(AdditionalPaymentType, on_delete=models.CASCADE, verbose_name="Turi")
    attached_date = models.DateField(null=True, blank=True, verbose_name="Biriktirilgan sana")
    type_of_additional_payment = models.CharField(choices=additional_payment, max_length=225)
    amount = models.DecimalField(decimal_places=2, max_digits=16, verbose_name="Summasi")
    note = models.TextField(verbose_name="Ta'rifi")
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name="Xodim")

    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Ushlab qolish yoki to'lov qo'shish"

    def __str__(self):
        return f'{self.staff.first_name} {self.staff.second_name}'


class Flow(models.Model):
    came = models.DateTimeField(verbose_name="Kelishi", null=True, blank=True)
    went = models.DateTimeField(verbose_name="Ketishi", null=True, blank=True)
    went_lunch = models.DateTimeField(verbose_name="Ovqatga ketish", default=None,
                                      null=True, blank=True)
    came_lunch = models.DateTimeField(verbose_name="Ovqatdan kelish", default=None, null=True, blank=True)
    staff = models.ForeignKey("Staff", on_delete=models.CASCADE, verbose_name="Xodim")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Hodimlarning kelib ketishi"

    def __str__(self):
        return f'{self.staff.first_name} {self.staff.second_name}'


class Document(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    date_of_issue = models.DateField(verbose_name="Berilgan sana")
    validity_period = models.DateField(verbose_name="Amal qilish mudati")
    document = models.FileField(upload_to='documents/', verbose_name="Hujjat(file)")
    note = models.CharField(max_length=255)
    staff = models.ForeignKey("Staff", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Hodim hujjatlari"

    def __str__(self):
        return self.name


class Salary(models.Model):
    work_type = [
        ('full time', 'Full Time'),
        ('part time', 'Part Time'),
        ('intern', 'Intern')
    ]

    type_of_work = models.CharField(default='kunbay', max_length=255,
                                    verbose_name="Ishlash turi(soatbay, kunbay, ishbay ...)")
    work_type = models.CharField(choices=work_type, default='full time', max_length=50)
    amount = models.FloatField(verbose_name="Miqdori")
    attached_date = models.DateField(default=None, null=True, blank=True, verbose_name="Biriktirilgan sana")
    completion_date = models.DateField(default=None, null=True, blank=True, verbose_name="Yankunlangan sana")
    staff = models.ForeignKey("Staff", on_delete=models.CASCADE, verbose_name="Xodim")

    class Meta:
        verbose_name_plural = "Ish haqqi"

    def __str__(self):
        return self.type_of_work


class RaceCountry(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class StaffRace(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(RaceCountry, related_name='race_country', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class Staff(models.Model):
    GENDER = (
        ('', 'Jinsi'),
        ('male', 'Erkak'),
        ('female', 'Ayol')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    first_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ism")
    second_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Familiya")
    last_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Otasining ismi")
    username = models.CharField(null=True, blank=True, max_length=255, verbose_name="Username")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")
    gender = models.CharField(choices=GENDER, max_length=10, verbose_name="Jinsi")
    password = models.CharField(null=True, blank=True, max_length=255, verbose_name="parol")
    training_url = models.UUIDField(max_length=200, unique=True, null=True, blank=True)
    tabel_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tabel raqami")
    start_work_at = models.DateField(null=True, blank=True, verbose_name="Ish boshlagan sana")
    account_number = models.BigIntegerField(null=True, blank=True, verbose_name="Xisob raqami")

    group_name = models.ForeignKey(CompanyScheduleName, on_delete=models.SET_NULL, default=None, null=True)
    is_outsource = models.BooleanField(default=False)

    email = models.EmailField(unique=True, verbose_name="Elektron manzil")
    mobile_phone = models.CharField(null=True, blank=True, max_length=15, verbose_name="Mobil telefon")
    home_phone = models.CharField(null=True, blank=True, max_length=15, verbose_name="Uy telefoni")
    work_phone = models.CharField(null=True, blank=True, max_length=15, verbose_name="Ish telefoni")

    race = models.ForeignKey(StaffRace, related_name='staff_race', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    address = models.CharField(null=True, blank=True, max_length=255, verbose_name="Uy manzili")
    image = models.ImageField(upload_to='company/staff/image/', null=True, blank=True, verbose_name="Xodimning rasmi")
    qr_code = models.ImageField(upload_to='company/staff/qr_code/', null=True, blank=True,
                                verbose_name="Xodimning qr code")

    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Bo'lim")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Lavozim")

    note = models.CharField(max_length=255, null=True, blank=True, verbose_name="Eslatma")
    # work_plan = models.ForeignKey(WorkPlan, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ish jadvali")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(f'{self.first_name} {self.second_name} {self.last_name}')

    @property
    def get_today_flow(self):
        from django.utils.timezone import datetime
        today = datetime.today()
        flows = self.flow_set.filter(created_at__day=today.day)
        return flows

    @property
    def get_today_flow_count(self):
        from django.utils.timezone import datetime

        today = datetime.today()
        flow_count = self.flow_set.filter(created_at__day=today.day).count()
        return flow_count + 1

    @property
    def position_name(self):
        return self.position.name


    class Meta:
        unique_together = ['company', 'username']
        ordering = ['-created_at']
        verbose_name_plural = "Xodimlar"


# Vacancy&Answer&Question


class Question(models.Model):
    question = models.CharField(max_length=500, blank=True, null=True, verbose_name="Savol")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bo'lim savoli"


class NewStaff(models.Model):
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Kompaniya")
    full_name = models.CharField(max_length=255, verbose_name="Xodimning to'liq ism sharifi")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Xodimning tug'ilgan sanasi")
    image = models.ImageField(upload_to='company/staff/image/', null=True, blank=True, verbose_name="Xodimning rasmi")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                   verbose_name="Xodim ishlaydigan bo'lim")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Xodimning lavozimi")
    period_time = models.DateField(null=True, blank=True, verbose_name="Stajirovka mudati")
    phone_number = models.CharField(null=True, blank=True, max_length=50)
    address = models.CharField(null=True, blank=True, max_length=255)
    tg_user_id = models.IntegerField(null=True, blank=True)
    question_step = models.IntegerField(null=True, blank=True)
    tg_answer_id = models.IntegerField(null=True, blank=True)
    tg_username = models.CharField(null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Yangi xodimlar"


# answer + new conditae

class Answer(models.Model):
    candidate = models.ForeignKey(NewStaff, on_delete=models.CASCADE, verbose_name="Yangi Xodim")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Bo'lim savoli")
    answer = models.CharField(max_length=512, verbose_name="Javob")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Javoblar"


class Vacancy(models.Model):
    staff_position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Lavozimga vakansiya")
    description = fields.RichTextField(null=True, blank=True,
                                       verbose_name="Lavozimga qo'yiladigan talablar haqida ma'lumot")
    is_active = models.BooleanField(default=False, verbose_name="Vakansiya aktiv")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.staff_position.name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Vakansiya"


class Bot(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Kompaniya")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bot nomi")
    token = models.CharField(max_length=512, null=True, blank=True, verbose_name="Token")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bot"


class Admin(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Kompaniya")
    name = models.CharField(blank=True, null=True, max_length=255)
    chat_id = models.BigIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.chat_id)


class EntryText(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Kompaniya")
    name = models.CharField(blank=True, null=True, max_length=1024)

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class FinishText(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Kompaniya")
    name = models.CharField(blank=True, null=True, max_length=1024)

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class AdoptationVideos(models.Model):
    video = models.FileField(upload_to='company/video')

class AdoptationUrls(models.Model):
    url = models.URLField()

class AdoptationFiles(models.Model):
    file = models.FileField(upload_to='company/files')


# Todo: delete, if have any other training model 
class AdoptationModel(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE,
                                 verbose_name="Xodimning lavozimi")
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    videos = models.ManyToManyField(AdoptationVideos, default=None, blank=True)
    urls = models.ManyToManyField(AdoptationUrls, default=None, blank=True)
    files = models.ManyToManyField(AdoptationFiles, default=None, blank=True)
    text = models.TextField(default=None, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(pre_delete, sender=AdoptationModel)
def cascade_delete_branch(sender, instance, **kwargs):
   if instance.urls:
       instance.urls.all().delete()
   if instance.files:
       instance.files.all().delete()
   if instance.videos:
       instance.videos.all().delete()

class AdoptationQuestions(models.Model):
    question = models.CharField(max_length=1024)
    adopt = models.ForeignKey(AdoptationModel, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.question

class TrainingVideos(models.Model):
    video = models.FileField(upload_to='company/video')

class TrainingUrls(models.Model):
    url = models.URLField()

class TrainingFiles(models.Model):
    file = models.FileField(upload_to='company/files')


# Todo: delete, if have any other training model 
class TrainingModel(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE,
                                 verbose_name="Xodimning lavozimi")
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Kompaniya")
    videos = models.ManyToManyField(AdoptationVideos, default=None, blank=True)
    urls = models.ManyToManyField(AdoptationUrls, default=None, blank=True)
    files = models.ManyToManyField(AdoptationFiles, default=None, blank=True)
    text = models.TextField(default=None, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(pre_delete, sender=TrainingModel)
def cascade_delete_branch(sender, instance, **kwargs):
   if instance.urls:
       instance.urls.all().delete()
   if instance.files:
       instance.files.all().delete()
   if instance.videos:
       instance.videos.all().delete()

class TrainingQuestions(models.Model):
    question = models.CharField(max_length=1024)
    adopt = models.ForeignKey(AdoptationModel, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.question

class StaffAnswers(models.Model):
    question = models.ForeignKey(AdoptationQuestions, on_delete=models.CASCADE)
    answer = models.TextField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.answer

    class Meta:
        unique_together = ['question', 'staff']

# class TrainingInfo(models.Model):
#     position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True,
#                                  verbose_name="Xodimning lavozimi")
#     title = models.CharField(null=True, blank=True, max_length=255)
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Kompaniya")
#     info = RichTextUploadingField(null=True, blank=True)
#     create_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.title)


# class TrainingQuestion(models.Model):
#     question = models.CharField(max_length=500, blank=True, null=True, verbose_name="Savol")
#     position = models.ForeignKey(Position, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.question if self.question else "None"

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name_plural = "Training savollar"


# class TrainingAnswer(models.Model):
    # staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Xodim")
    # question = models.ForeignKey(TrainingQuestion, null=True, blank=True, on_delete=models.CASCADE,
    #                              verbose_name="Savol")
    # answer = models.CharField(max_length=512, null=True, blank=True, verbose_name="Javob")
    # created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.answer if self.answer else "..."

    # class Meta:
    #     ordering = ['-created_at']
    #     verbose_name_plural = "Training Javoblar"


class CompanyCulture(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    text = RichTextUploadingField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Company Culture"


class SuperStaffs(models.Model):
    TYPE_OF_GRADE = (
        ('weekly', 'Haftalik'),
        ('monthly', 'Oylik')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    type = models.CharField(choices=TYPE_OF_GRADE, max_length=20)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.staff.first_name


class StaffORGSystem(MPTTModel):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.staff.first_name} {self.staff.second_name} {self.staff.last_name}'

    class Meta:
        verbose_name_plural = "Xodimlarning ORG sistemasi"

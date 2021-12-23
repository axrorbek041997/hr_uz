# Generated by Django 3.2.9 on 2021-12-19 12:19

import ckeditor.fields
import ckeditor_uploader.fields
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdoptationFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='company/files')),
            ],
        ),
        migrations.CreateModel(
            name='AdoptationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('text', models.TextField(blank=True, default=None)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdoptationQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1024)),
                ('adopt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.adoptationmodel')),
            ],
        ),
        migrations.CreateModel(
            name='AdoptationUrls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='AdoptationVideos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='company/video')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kompaniya nomi')),
                ('phone', models.CharField(blank=True, max_length=25, null=True, verbose_name='Kompaniya telefon raqami')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Kompaniya manzili')),
                ('creator', models.CharField(blank=True, max_length=255, null=True, verbose_name='Kompaniya asoschisi')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name="Kompaniya haqida qisqacha ma'lumot")),
                ('video', models.FileField(blank=True, null=True, upload_to='company/video/', verbose_name='Kompaniya haqida qisqacha video')),
                ('info', models.TextField(blank=True, null=True, verbose_name="Bot uchun qisqacha ma'lumot")),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company/image/', verbose_name='Kompaniya logotipi')),
                ('amount_of_staff', models.IntegerField(default=1, verbose_name='Hodimlar soni')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_expire_date', models.DateTimeField(blank=True, null=True, verbose_name="To'lov tugash muddati")),
            ],
            options={
                'verbose_name_plural': "Kompaniya ma'lumotini qo'shish",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CompanyScheduleName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('company', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company')),
            ],
            options={
                'unique_together': {('name', 'company')},
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name="Bo'lim nomi")),
                ('info', models.CharField(blank=True, max_length=255, null=True, verbose_name="Bo'lim haqida")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
            options={
                'verbose_name_plural': "Bo'limlar",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Lavozim nomi')),
                ('info', models.CharField(blank=True, max_length=255, null=True, verbose_name='Lavozim haqida')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app.position')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ism')),
                ('second_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Familiya')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Otasining ismi')),
                ('username', models.CharField(blank=True, max_length=255, null=True, verbose_name='Username')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name="Tug'ilgan sana")),
                ('gender', models.CharField(choices=[('male', 'Erkak'), ('female', 'Ayol')], max_length=10, verbose_name='Jinsi')),
                ('password', models.CharField(blank=True, max_length=255, null=True, verbose_name='parol')),
                ('training_url', models.UUIDField(blank=True, null=True, unique=True)),
                ('tabel_number', models.PositiveIntegerField(blank=True, null=True, verbose_name='Tabel raqami')),
                ('start_work_at', models.DateField(blank=True, null=True, verbose_name='Ish boshlagan sana')),
                ('account_number', models.BigIntegerField(blank=True, null=True, verbose_name='Xisob raqami')),
                ('is_outsource', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Elektron manzil')),
                ('mobile_phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Mobil telefon')),
                ('home_phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Uy telefoni')),
                ('work_phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Ish telefoni')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Uy manzili')),
                ('image', models.ImageField(blank=True, null=True, upload_to='company/staff/image/', verbose_name='Xodimning rasmi')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='company/staff/qr_code/', verbose_name='Xodimning qr code')),
                ('note', models.CharField(blank=True, max_length=255, null=True, verbose_name='Eslatma')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.department', verbose_name="Bo'lim")),
                ('group_name', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.companyschedulename')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.position', verbose_name='Lavozim')),
            ],
            options={
                'verbose_name_plural': 'Xodimlar',
                'ordering': ['-created_at'],
                'unique_together': {('company', 'username')},
            },
        ),
        migrations.CreateModel(
            name='TrainingFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='company/files')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingUrls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='TrainingVideos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='company/video')),
            ],
        ),
        migrations.CreateModel(
            name='TypeCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kompaniya turini nomi')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Kompaniya turi',
            },
        ),
        migrations.CreateModel(
            name='VacationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nomi')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
            options={
                'verbose_name_plural': "Xodimlaring qo'shimcha dam olish turi",
            },
        ),
        migrations.CreateModel(
            name='Vacation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vocation_period_types', models.CharField(blank=True, choices=[('per_hour', 'Soatbay'), ('per_day', 'Kunbay')], max_length=255, null=True, verbose_name='Turi')),
                ('start_at', models.DateField(verbose_name='Boshlash vaqti')),
                ('end_at', models.DateField(verbose_name='Tugash vaqti')),
                ('note', models.CharField(blank=True, max_length=512, null=True, verbose_name='Izoh')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff', verbose_name='Xodim')),
                ('vacation_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.vacationtype', verbose_name="Qo'shimcha dam olish turi")),
            ],
            options={
                'verbose_name_plural': "Xodimlaring qo'shimcha dam olish bo'limi",
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name="Lavozimga qo'yiladigan talablar haqida ma'lumot")),
                ('is_active', models.BooleanField(default=False, verbose_name='Vakansiya aktiv')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.position', verbose_name='Lavozimga vakansiya')),
            ],
            options={
                'verbose_name_plural': 'Vakansiya',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TrainingQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1024)),
                ('adopt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.adoptationmodel')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('text', models.TextField(blank=True, default=None)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
                ('files', models.ManyToManyField(blank=True, default=None, to='app.AdoptationFiles')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.position', verbose_name='Xodimning lavozimi')),
                ('urls', models.ManyToManyField(blank=True, default=None, to='app.AdoptationUrls')),
                ('videos', models.ManyToManyField(blank=True, default=None, to='app.AdoptationVideos')),
            ],
        ),
        migrations.CreateModel(
            name='SuperStaffs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('weekly', 'Haftalik'), ('monthly', 'Oylik')], max_length=20)),
                ('text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff')),
            ],
        ),
        migrations.CreateModel(
            name='StaffORGSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app.stafforgsystem')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff')),
            ],
            options={
                'verbose_name_plural': 'Xodimlarning ORG sistemasi',
            },
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_work', models.CharField(default='kunbay', max_length=255, verbose_name='Ishlash turi(soatbay, kunbay, ishbay ...)')),
                ('work_type', models.CharField(choices=[('full time', 'Full Time'), ('part time', 'Part Time'), ('intern', 'Intern')], default='full time', max_length=50)),
                ('amount', models.FloatField(verbose_name='Miqdori')),
                ('attached_date', models.DateField(blank=True, default=None, null=True, verbose_name='Biriktirilgan sana')),
                ('completion_date', models.DateField(blank=True, default=None, null=True, verbose_name='Yankunlangan sana')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff', verbose_name='Xodim')),
            ],
            options={
                'verbose_name_plural': 'Ish haqqi',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=500, null=True, verbose_name='Savol')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.department')),
            ],
            options={
                'verbose_name_plural': "Bo'lim savoli",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surcharge', models.BooleanField(default=False, verbose_name='Jarima')),
                ('reward', models.BooleanField(default=False, verbose_name='Mukofot')),
                ('note', models.CharField(blank=True, max_length=512, null=True, verbose_name='Izoh')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff', verbose_name='Xodim')),
            ],
            options={
                'verbose_name_plural': "Xodimlarga jarima mukofot e'lon qilish",
            },
        ),
        migrations.CreateModel(
            name='NewStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name="Xodimning to'liq ism sharifi")),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name="Xodimning tug'ilgan sanasi")),
                ('image', models.ImageField(blank=True, null=True, upload_to='company/staff/image/', verbose_name='Xodimning rasmi')),
                ('period_time', models.DateField(blank=True, null=True, verbose_name='Stajirovka mudati')),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('tg_user_id', models.IntegerField(blank=True, null=True)),
                ('question_step', models.IntegerField(blank=True, null=True)),
                ('tg_answer_id', models.IntegerField(blank=True, null=True)),
                ('tg_username', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.department', verbose_name="Xodim ishlaydigan bo'lim")),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.position', verbose_name='Xodimning lavozimi')),
            ],
            options={
                'verbose_name_plural': 'Yangi xodimlar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('came', models.DateTimeField(blank=True, null=True, verbose_name='Kelishi')),
                ('went', models.DateTimeField(blank=True, null=True, verbose_name='Ketishi')),
                ('went_lunch', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Ovqatga ketish')),
                ('came_lunch', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Ovqatdan kelish')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff', verbose_name='Xodim')),
            ],
            options={
                'verbose_name_plural': 'Hodimlarning kelib ketishi',
            },
        ),
        migrations.CreateModel(
            name='FinishText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=1024, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
        ),
        migrations.CreateModel(
            name='EntryText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=1024, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nomi')),
                ('date_of_issue', models.DateField(verbose_name='Berilgan sana')),
                ('validity_period', models.DateField(verbose_name='Amal qilish mudati')),
                ('document', models.FileField(upload_to='documents/', verbose_name='Hujjat(file)')),
                ('note', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff')),
            ],
            options={
                'verbose_name_plural': 'Hodim hujjatlari',
            },
        ),
        migrations.CreateModel(
            name='CompanySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=15)),
                ('start_work', models.TimeField(blank=True, default=None, null=True, verbose_name='Ish boshlanishi')),
                ('lunch_start', models.TimeField(blank=True, default=None, null=True, verbose_name='Tushlik vaqti')),
                ('lunch_end', models.TimeField(blank=True, default=None, null=True, verbose_name='Tushlik tugash vaqti')),
                ('end_work', models.TimeField(blank=True, default=None, null=True, verbose_name='Ish Tugash vaqti')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company')),
                ('name', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.companyschedulename')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyCulture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company')),
            ],
            options={
                'verbose_name_plural': 'Company Culture',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='company',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.typecompany', verbose_name='Kompaniya turi'),
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nomi')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Filial')),
            ],
            options={
                'verbose_name_plural': 'Filial',
            },
        ),
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bot nomi')),
                ('token', models.CharField(blank=True, max_length=512, null=True, verbose_name='Token')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
            options={
                'verbose_name_plural': 'Bot',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=512, verbose_name='Javob')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.newstaff', verbose_name='Yangi Xodim')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.question', verbose_name="Bo'lim savoli")),
            ],
            options={
                'verbose_name_plural': 'Javoblar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='adoptationmodel',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya'),
        ),
        migrations.AddField(
            model_name='adoptationmodel',
            name='files',
            field=models.ManyToManyField(blank=True, default=None, to='app.AdoptationFiles'),
        ),
        migrations.AddField(
            model_name='adoptationmodel',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.position', verbose_name='Xodimning lavozimi'),
        ),
        migrations.AddField(
            model_name='adoptationmodel',
            name='urls',
            field=models.ManyToManyField(blank=True, default=None, to='app.AdoptationUrls'),
        ),
        migrations.AddField(
            model_name='adoptationmodel',
            name='videos',
            field=models.ManyToManyField(blank=True, default=None, to='app.AdoptationVideos'),
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('chat_id', models.BigIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalPaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nomi')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
            ],
            options={
                'verbose_name_plural': "Ushlab qolish yoki qo'shimcha to'lovlar nomi",
            },
        ),
        migrations.CreateModel(
            name='AdditionalPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attached_date', models.DateField(blank=True, null=True, verbose_name='Biriktirilgan sana')),
                ('type_of_additional_payment', models.CharField(choices=[('find', 'Ushlab qolish'), ('additional_payment', "Qo'shimcha to'lov")], max_length=225)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16, verbose_name='Summasi')),
                ('note', models.TextField(verbose_name="Ta'rifi")),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('apt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.additionalpaymenttype', verbose_name='Turi')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff', verbose_name='Xodim')),
            ],
            options={
                'verbose_name_plural': "Ushlab qolish yoki to'lov qo'shish",
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_director', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.branch', verbose_name='Filial')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.company', verbose_name='Kompaniya')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'HR',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='StaffAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.adoptationquestions')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.staff')),
            ],
            options={
                'unique_together': {('question', 'staff')},
            },
        ),
    ]

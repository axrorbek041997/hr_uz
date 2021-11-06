from django import template
from app import models

register = template.Library()


@register.filter
def fill_fields(form, model_instance):
    f = form.__class__(instance=model_instance, auto_id=f'%s_{model_instance.id}_instance_field')

    return f


@register.filter
def late_delta(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day__exact=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.start_work), "%H:%M:%S")

            if coming_time > schedule:
                # late
                return coming_time - schedule
            elif coming_time < schedule:
                return schedule - coming_time
        except:
            pass


@register.filter
def late_delta_bool(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day__exact=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.start_work), "%H:%M:%S")
            if coming_time > schedule:
                return True
            elif coming_time < schedule:
                return False
        except:
            pass


@register.filter
def earlier_delta(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day__exact=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.end_work), "%H:%M:%S")

            if coming_time > schedule:
                # late
                return coming_time - schedule
            else:
                return schedule - coming_time
        except:
            print("Asd")


@register.filter
def earlier_delta_bool(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day__exact=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.end_work), "%H:%M:%S")
            if coming_time < schedule:
                return True
            else:
                return False
        except:
            pass


@register.filter
def lunch_late_delta(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.came_lunch), "%H:%M:%S")

            if coming_time > schedule:
                # late
                return coming_time - schedule
            else:
                return schedule - coming_time
        except:
            pass


@register.filter
def lunch_late_delta_bool(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.came_lunch), "%H:%M:%S")
            if coming_time > schedule:
                return True
            else:
                return False
        except:
            pass


@register.filter(name='lunch_earlier_delta')
def lunch_earlier_delta(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day=today_name.lower()).first()
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.went_lunch), "%H:%M:%S")

            if coming_time > schedule:
                return coming_time - schedule
            else:
                return schedule - coming_time
        except:
            pass


@register.filter(name='lunch_earlier_delta_bool')
def lunch_earlier_delta_bool(action_time, staff):
    import datetime
    today_name = datetime.datetime.today().strftime('%A')
    company_schedule = staff.group_name.companyschedule_set.filter(day=today_name.lower()).first()
    print(staff.group_name.companyschedule_set.filter(day=today_name.lower()).values())
    if action_time == "":
        coming_time = action_time
    else:
        coming_time = datetime.datetime.strptime(action_time, "%H:%M")
        try:
            schedule = datetime.datetime.strptime(str(company_schedule.went_lunch), "%H:%M:%S")
            return bool(coming_time < schedule)
        except:
            pass

# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

from core import models


def set_default_child(kwargs):
    """
    Sets the default Child for an instance based on the `child` parameter or
    if only one Child instance exists.

    :param kwargs: Form arguments.
    :return: Form arguments with updated initial values.
    """
    instance = kwargs.get('instance', None)
    child_slug = kwargs.get('child', None)
    if not kwargs.get('initial'):
        kwargs.update(initial={})

    # Do not update initial values for an existing instance (edit operation).
    if instance is None:
        if child_slug:
            kwargs['initial'].update({
                'child': models.Child.objects.filter(slug=child_slug).first(),
            })
        elif models.Child.count() == 1:
            kwargs['initial'].update({'child': models.Child.objects.first()})

    try:
        kwargs.pop('child')
    except KeyError:
        pass
    return kwargs


# Sets default values (start/end date, child) from a timer.
def set_defaults_from_timer(kwargs):
    instance = kwargs.get('instance', None)
    timer_id = kwargs.get('timer', None)
    if not kwargs.get('initial'):
        kwargs.update(initial={})

    # Do not update initial values for an existing instance (edit operation).
    if not instance and timer_id:
        timer = models.Timer.objects.get(id=timer_id)
        kwargs['initial'].update({
            'timer': timer,
            'start': timer.start,
            'end': timer.end or timezone.now()
        })

    try:
        kwargs.pop('timer')
    except KeyError:
        pass
    return kwargs


# Sets the default Feeding type to the one used in the most recent entry.
def set_default_feeding_type(kwargs):
    instance = kwargs.get('instance', None)
    initial = kwargs.get('initial', None)
    if not kwargs.get('initial'):
        kwargs.update(initial={})
    if instance is None and initial and 'child' in initial:
        if models.Feeding.objects.filter(child=initial['child']).count() > 0:
            kwargs['initial'].update({
                'type': models.Feeding.objects.filter(
                    child=initial['child']).latest('end').type
            })
    return kwargs


class ChildForm(forms.ModelForm):
    class Meta:
        model = models.Child
        fields = [
            'first_name',
            'last_name',
            'birth_date'
        ]
        if settings.BABY_BUDDY['ALLOW_UPLOADS']:
            fields.append('picture')
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_date',
            }),
        }


class ChildDeleteForm(forms.ModelForm):
    confirm_name = forms.CharField(max_length=511)

    class Meta:
        model = models.Child
        fields = []

    def clean_confirm_name(self):
        confirm_name = self.cleaned_data['confirm_name']
        if confirm_name != str(self.instance):
            raise forms.ValidationError(
                _('Name does not match child name.'), code='confirm_mismatch')
        return confirm_name

    def save(self, commit=True):
        instance = self.instance
        self.instance.delete()
        return instance


class DiaperChangeForm(forms.ModelForm):
    class Meta:
        model = models.DiaperChange
        fields = ['child', 'time', 'wet', 'solid', 'color', 'amount']
        widgets = {
            'time': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_time',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        super(DiaperChangeForm, self).__init__(*args, **kwargs)


class FeedingForm(forms.ModelForm):
    class Meta:
        model = models.Feeding
        fields = ['child', 'start', 'end', 'type', 'method', 'amount']
        widgets = {
            'start': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_start',
            }),
            'end': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_end',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        self.timer_id = kwargs.get('timer', None)
        kwargs = set_defaults_from_timer(kwargs)
        kwargs = set_default_feeding_type(kwargs)
        super(FeedingForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(FeedingForm, self).save(commit=False)
        if self.timer_id:
            timer = models.Timer.objects.get(id=self.timer_id)
            timer.stop(instance.end)
        instance.save()
        return instance


class NoteForm(forms.ModelForm):
    class Meta:
        model = models.Note
        fields = ['child', 'note']

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        super(NoteForm, self).__init__(*args, **kwargs)


class SleepForm(forms.ModelForm):
    class Meta:
        model = models.Sleep
        fields = ['child', 'start', 'end']
        widgets = {
            'start': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_start',
            }),
            'end': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_end',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        self.timer_id = kwargs.get('timer', None)
        kwargs = set_defaults_from_timer(kwargs)
        super(SleepForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(SleepForm, self).save(commit=False)
        if self.timer_id:
            timer = models.Timer.objects.get(id=self.timer_id)
            timer.stop(instance.end)
        instance.save()
        return instance


class TemperatureForm(forms.ModelForm):
    class Meta:
        model = models.Temperature
        fields = ['child', 'temperature', 'time']
        widgets = {
            'time': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_time',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        super(TemperatureForm, self).__init__(*args, **kwargs)


class TimerForm(forms.ModelForm):
    class Meta:
        model = models.Timer
        fields = ['child', 'name', 'start']
        widgets = {
            'start': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_start',
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        kwargs = set_default_child(kwargs)
        super(TimerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(TimerForm, self).save(commit=False)
        instance.user = self.user
        instance.save()
        return instance


class TummyTimeForm(forms.ModelForm):
    class Meta:
        model = models.TummyTime
        fields = ['child', 'start', 'end', 'milestone']
        widgets = {
            'start': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_start',
            }),
            'end': forms.DateTimeInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_end',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        self.timer_id = kwargs.get('timer', None)
        kwargs = set_defaults_from_timer(kwargs)
        super(TummyTimeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(TummyTimeForm, self).save(commit=False)
        if self.timer_id:
            timer = models.Timer.objects.get(id=self.timer_id)
            timer.stop(instance.end)
        instance.save()
        return instance


class WeightForm(forms.ModelForm):
    class Meta:
        model = models.Weight
        fields = ['child', 'weight', 'date']
        widgets = {
            'date': forms.DateInput(attrs={
                'readonly': 'readonly',
                'data-target': '#datetimepicker_date',
            }),
        }

    def __init__(self, *args, **kwargs):
        kwargs = set_default_child(kwargs)
        super(WeightForm, self).__init__(*args, **kwargs)

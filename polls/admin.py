"""Configuration for admin site."""

from django.contrib import admin
from .models import Choice, Question, Vote


class ChoiceInline(admin.TabularInline):
    """Edit the configuration of the admin site."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Edit the configuration of the admin site."""

    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date', 'end_date'],
                              'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date',
                    'was_published_recently', 'end_date')

    list_filter = ['pub_date', 'end_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
admin.site.register(Choice)


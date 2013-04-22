from django import forms
from django.contrib.comments import Comment
from news.models import NewsPost
from ckeditor.widgets import CKEditorWidget

class NewPostForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = NewsPost
        exclude = ('author')

class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Comment
        exclude = ('content_type', 'object_pk', 'user', 'body', 'site', 'user_name', 'user_url', 'user_email', 'submit_date', 'ip_address', 'is_public', 'is_removed')

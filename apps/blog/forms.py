from django import forms

from apps.blog.models import Comment, Post, Category

# from ckeditor.widgets import CKEditorWidget

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text":forms.Textarea(attrs={"class":"form-control"})
        }

class ReplayCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text":forms.Textarea(attrs={"class":"form-control"})
        }

from django_select2 import forms as s2forms

class CategorySelectWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains"
    ]




class PostCreationForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Post
        fields = ['title', 'description', 'media', 'category', 'is_active']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'media': 'Медия',
            'category': 'Категория',
            'is_active': 'Активный',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'media': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', "is_active", "category"]

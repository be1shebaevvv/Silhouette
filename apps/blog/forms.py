from django import forms

from apps.blog.models import Category, Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "maxlength": 5000,
                    "placeholder": "Напишите комментарий…",
                }
            )
        }


class ReplayCommentForm(CommentForm):
    """Compatibility alias for templates that still import the old form name."""


class PostCreationForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )

    class Meta:
        model = Post
        fields = ["title", "description", "media", "category", "is_active"]
        labels = {
            "title": "Заголовок",
            "description": "Текст публикации",
            "media": "Медиафайл (необязательно)",
            "category": "Категория",
            "is_active": "Опубликовать",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 100, "placeholder": "Заголовок"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 6, "placeholder": "Чем хотите поделиться?"}
            ),
            "media": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "is_active", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

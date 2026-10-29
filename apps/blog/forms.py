from pathlib import Path

from django import forms

from apps.blog.models import Category, Comment, Post, Report


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

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError("Комментарий не может быть пустым.")
        if len(text) > 5000:
            raise forms.ValidationError("Комментарий не должен превышать 5000 символов.")
        return text


class ReplayCommentForm(CommentForm):
    """Compatibility alias for templates that still import the old form name."""


class PostCreationForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 6, "maxlength": 10000, "placeholder": "Чем хотите поделиться?"}
        ),
    )
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
                attrs={"class": "form-control", "rows": 6, "maxlength": 10000, "placeholder": "Чем хотите поделиться?"}
            ),
            "media": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.gif,.webp,.mp4,.webm,.mov,.m4v"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Добавьте заголовок.")
        return title

    def clean_description(self):
        description = self.cleaned_data["description"].strip()
        if len(description) > 10000:
            raise forms.ValidationError("Текст не должен превышать 10000 символов.")
        return description

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("description") and not cleaned_data.get("media"):
            self.add_error("description", "Добавьте текст или медиафайл.")
        return cleaned_data

    def clean_media(self):
        media = self.cleaned_data.get("media")
        if not media or not hasattr(media, "name"):
            return media

        extension = Path(media.name).suffix.lower()
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        video_extensions = {".mp4", ".webm", ".mov", ".m4v"}
        allowed_extensions = image_extensions | video_extensions

        if extension not in allowed_extensions:
            raise forms.ValidationError("Разрешены только изображения JPG, PNG, GIF, WebP и видео MP4, WebM, MOV.")
        max_size = 15 * 1024 * 1024 if extension in image_extensions else 50 * 1024 * 1024
        if media.size > max_size:
            limit_mb = max_size // (1024 * 1024)
            raise forms.ValidationError(f"Размер этого файла не должен превышать {limit_mb} МБ.")
        return media


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "is_active", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6, "maxlength": 10000}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Добавьте заголовок.")
        return title

    def clean_description(self):
        description = self.cleaned_data["description"].strip()
        if len(description) > 10000:
            raise forms.ValidationError("Текст не должен превышать 10000 символов.")
        return description



class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "maxlength": 2000, "placeholder": "Дополнительные сведения (необязательно)"}
            ),
        }

    def clean_details(self):
        details = self.cleaned_data.get("details", "").strip()
        if len(details) > 2000:
            raise forms.ValidationError("Подробности не должны превышать 2000 символов.")
        return details

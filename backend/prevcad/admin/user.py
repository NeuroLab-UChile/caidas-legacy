from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import Permission
from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.decorators import update_wrapper
from django.contrib.contenttypes.models import ContentType

from prevcad.models.user_profile import UserProfile


class PermissionSelectWidget(forms.SelectMultiple):
    template_name = "admin/widgets/permission_select.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Agrupar permisos por app
        grouped_choices = {}
        content_types = ContentType.objects.all()

        for ct in content_types:
            app_perms = Permission.objects.filter(content_type=ct)
            if app_perms.exists():
                app_label = ct.app_label.title()
                if app_label not in grouped_choices:
                    grouped_choices[app_label] = []
                for perm in app_perms:
                    grouped_choices[app_label].append((perm.id, perm.name))

        context["widget"]["grouped_choices"] = grouped_choices
        context["widget"]["value"] = value or []
        return context


class CustomUserForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=PermissionSelectWidget,
        required=False,
        help_text="Selecciona los permisos específicos para este usuario",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class CustomUserAdmin(UserAdmin):
    actions = ["delete_users_safely"]
    list_display = (
        "get_avatar_display",
        "get_full_name_display",
        "is_staff_icon",
        "get_permissions_display",
        "get_last_login_display",
    )
    list_filter = ("groups", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name")
    ordering = ("username",)

    # Configuración para añadir usuarios
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
        (
            "Información Personal",
            {
                "fields": ("first_name", "last_name", "email"),
            },
        ),
        (
            "Permisos",
            {
                "classes": ("permissions-fieldset",),
                "fields": ("is_staff", "is_superuser", "groups"),
                "description": "Selecciona los roles y permisos para este usuario",
            },
        ),
    )

    # Actualizar fieldsets para el formulario de edición - usando la configuración estándar de Django
    fieldsets = (
        (None, {"fields": ("username",)}),
        ("Información Personal", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permisos",
            {
                "classes": ("permissions-fieldset",),
                "fields": ("is_staff", "is_superuser", "groups"),
                "description": "Gestiona los roles y permisos del usuario",
            },
        ),
    )

    form = CustomUserForm
    formfield_overrides = {
        User._meta.get_field("user_permissions"): {"widget": PermissionSelectWidget},
    }

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        return urls  # Usamos las URLs por defecto de UserAdmin

    def get_readonly_fields(self, request, obj=None):
        if not obj:  # Si es un nuevo usuario, no hay campos de solo lectura
            return []
        
        # Si es superusuario, no tiene campos de solo lectura
        if request.user.is_superuser:
            return []

        # Si es doctor, no tiene campos de solo lectura
        if request.user.groups.filter(name="DOCTOR").exists():
            return []

        # Si es staff editando a otro usuario
        if request.user.is_staff:
            if obj == request.user:
                # No puede cambiar sus propios permisos
                return ["is_staff", "is_superuser", "groups", "user_permissions"]
            elif obj.groups.filter(name="DOCTOR").exists():
                # No puede editar doctores
                return [f.name for f in self.model._meta.fields]
            else:
                # Puede editar otros usuarios normales
                return []

        # Si es usuario normal
        if obj == request.user:
            # Solo puede cambiar datos básicos
            return [
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "username",
            ]

        # No puede editar otros usuarios
        return [f.name for f in self.model._meta.fields]

    def _get_user_info_html(self, request):
        """Helper para generar el HTML con la información del usuario"""
        if request.user.is_authenticated:
            groups = [g.name for g in request.user.groups.all()]
            roles = []
            if request.user.is_superuser:
                roles.append("Superusuario")
            if request.user.is_staff:
                roles.append("Staff")
            roles.extend(groups)

            return format_html(
                '<div class="user-info" style="margin: 10px 0; padding: 10px; '
                "background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; "
                'font-size: 14px; color: #333;">'
                '<strong style="margin-right: 5px;">👤 Usuario actual:</strong>'
                '<span style="font-weight: 500;">{}</span>'
                '<span style="margin-left: 10px; color: #666;">Roles: {}</span>'
                "</div>",
                request.user.username,
                ", ".join(roles),
            )
        return ""

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["current_user_info"] = self._get_user_info_html(request)
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["current_user_info"] = self._get_user_info_html(request)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["current_user_info"] = self._get_user_info_html(request)
        return super().add_view(request, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        # Hacer doctor automáticamente staff y superuser
        if not change and "groups" in form.cleaned_data:
            if any(group.name == "DOCTOR" for group in form.cleaned_data["groups"]):
                obj.is_staff = True
                obj.is_superuser = True
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Si es doctor, puede cambiar cualquier cosa
        if request.user.groups.filter(name="DOCTOR").exists():
            return True
        # Si es staff, puede cambiar todo excepto doctores
        if request.user.is_staff:
            if obj and obj.groups.filter(name="DOCTOR").exists():
                return False
            return True
        # Si es usuario normal, solo puede cambiar su propio perfil
        return obj is None or obj == request.user

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name="DOCTOR").exists()

    def delete_users_safely(self, request, queryset):
        if not self.has_delete_permission(request):
            print("No tienes permiso para eliminar usuarios.")
            return

        for user in queryset:
            try:
                # Eliminar imagen de perfil si existe
                if hasattr(user, "profile") and user.profile.profile_image:
                    try:
                        image_path = os.path.join(
                            settings.MEDIA_ROOT, str(user.profile.profile_image)
                        )
                        if os.path.exists(image_path):
                            os.remove(image_path)

                        # Eliminar directorio si está vacío
                        user_dir = os.path.dirname(image_path)
                        if os.path.exists(user_dir) and not os.listdir(user_dir):
                            os.rmdir(user_dir)
                    except Exception as e:
                        print(f"Error eliminando imagen de perfil: {str(e)}")

                user.delete()
            except Exception as e:
                print(f"Error eliminando usuario {user.username}: {str(e)}")

    delete_users_safely.short_description = (
        "Eliminar usuarios seleccionados de forma segura"
    )

    def get_avatar_display(self, obj):
        try:
            if hasattr(obj, "profile") and obj.profile.profile_image:
                return format_html(
                    '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; '
                    'object-fit: cover; border: 2px solid #e5e7eb;" />',
                    obj.profile.profile_image.url,
                )
        except Exception:
            pass

        # Avatar por defecto si no hay imagen
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; '
            "background-color: #e5e7eb; display: flex; align-items: center; "
            'justify-content: center; font-size: 16px; color: #6b7280;">'
            "{}</div>",
            obj.username[0].upper(),
        )

    get_avatar_display.short_description = ""

    def get_full_name_display(self, obj):
        full_name = obj.get_full_name()
        username = obj.username

        if full_name:
            return format_html(
                '<div style="display: flex; flex-direction: column;">'
                '<span style="font-weight: 500;">{}</span>'
                '<span style="color: #6b7280; font-size: 0.875rem;">@{}</span>'
                "</div>",
                full_name,
                username,
            )
        return format_html('<span style="font-weight: 500;">@{}</span>', username)

    get_full_name_display.short_description = "Usuario"

    def is_staff_icon(self, obj):
        if obj.groups.filter(name="DOCTOR").exists():
            return format_html(
                '<span style="color: #059669; background: #d1fae5; padding: 4px 8px; '
                'border-radius: 9999px; font-size: 0.75rem;">👨‍⚕️ Doctor</span>'
            )
        return format_html(
            '<span style="color: #6b7280; background: #f3f4f6; padding: 4px 8px; '
            'border-radius: 9999px; font-size: 0.75rem;">👤 Usuario</span>'
        )

    is_staff_icon.short_description = "Rol"

    def get_permissions_display(self, obj):
        permissions = []

        if obj.is_superuser:
            permissions.append(
                '<span style="color: #2563eb; background: #dbeafe; padding: 4px 8px; '
                'border-radius: 9999px; font-size: 0.75rem;">👑 Superusuario</span>'
            )
        if obj.is_staff:
            permissions.append(
                '<span style="color: #0891b2; background: #cffafe; padding: 4px 8px; '
                'border-radius: 9999px; font-size: 0.75rem;">⚙️ Staff</span>'
            )
        if not permissions:
            return format_html(
                '<span style="color: #6b7280; background: #f3f4f6; padding: 4px 8px; '
                'border-radius: 9999px; font-size: 0.75rem;">-</span>'
            )

        return format_html(
            '<div style="display: flex; gap: 4px;">{}</div>',
            format_html("".join(permissions)),
        )

    get_permissions_display.short_description = "Permisos"

    def get_last_login_display(self, obj):
        if obj.last_login:
            return format_html(
                '<span style="color: #6b7280; font-size: 0.875rem;">'
                "Último acceso:<br>{}</span>",
                obj.last_login.strftime("%d/%m/%Y %H:%M"),
            )
        return format_html(
            '<span style="color: #ef4444; font-size: 0.875rem;">Nunca</span>'
        )

    get_last_login_display.short_description = "Último Acceso"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "groups" in form.base_fields:
            form.base_fields["groups"].widget.attrs.update(
                {
                    "class": "select2-roles",
                    "style": "width: 100%; max-height: 200px; overflow-y: auto;",
                }
            )
        return form

    class Media:
        css = {"all": ("admin/css/user_admin.css",)}
        js = (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",
            "admin/js/custom_user_admin.js",
        )


# Registrar el admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# For UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    ordering = ["-pk"]
    list_display = (
        "id",
        "user",
        "phone",
        "birth_date",
        "specialty",
        "profile_image",
        "role",
        "role_label",
        "is_professional",
        "is_staff_member",
    )
    list_filter = ["birth_date"]
    search_fields = ["phone"]


admin.site.register(UserProfile, UserProfileAdmin)

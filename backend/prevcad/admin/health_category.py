from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import path, reverse
import json
from ..models import HealthCategory, Recommendation
from .filters import HealthStatusFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.loader import TemplateDoesNotExist
from urllib.parse import unquote
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.utils.timesince import timesince
from django.core.handlers.wsgi import WSGIRequest
from threading import current_thread
from django.db import transaction
from ..models.user_types import UserTypes
from django.db.models import Q
from django.db import connection
import time
from django.db.models import Case, When, Value, IntegerField
from django.db.utils import OperationalError


class UserProfileFilter(admin.SimpleListFilter):
    title = _("Paciente")  # Cambiado de 'Usuario' a 'Paciente'
    parameter_name = "user_filter"

    def lookups(self, request, model_admin):
        """
        Retorna lista de tuplas (valor, texto) para las opciones del filtro
        """
        users = set()
        for obj in model_admin.model.objects.select_related(
            "user__user", "template"
        ).all():
            if obj.user and obj.user.user:
                user = obj.user.user
                # Obtener el nombre completo o username si no hay nombre completo
                display_name = user.get_full_name() or user.username
                # Obtener la categoría del template
                category = obj.template.name if obj.template else "Sin categoría"

                # Crear la tupla con (id, "Nombre (Categoría)")
                users.add((str(obj.user.id), f"{display_name} - {category}"))
        return sorted(users, key=lambda x: x[1].lower())

    def queryset(self, request, queryset):
        """
        Retorna el queryset filtrado basado en el valor seleccionado
        """
        if not self.value():
            return queryset
        return queryset.filter(user_id=self.value())


@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    # Definir el orden específico de los campos

    recommendation_editor_template = "admin/healthcategory/recommendation_editor.html"
    fields = (
        "get_completion_date",
        "get_user_info",
        "get_template_name",
        "get_recommendation_status",
        "get_evaluation_type",
        "get_user_permissions",
        "get_professional_evaluation",
        "get_recommendation_editor",
        "get_detailed_responses",
    )

    list_display = [
        "get_completion_date",
        "get_user_info",
        "get_template_name",
        "get_recommendation_status",
        "get_evaluation_type",
        "get_user_permissions",
        "get_actions_display",  # Nueva columna
    ]

    list_filter = (
        "user__user__username",
        UserProfileFilter,
        "template",
    )

    search_fields = (
        "user__user__username",
        "user__user__first_name",
        "user__user__last_name",
        "template__name",
    )

    # Definir los campos base del modelo
    base_fields = ["template"]

    # Definir los campos de solo lectura
    readonly_fields = (
        "user",
        "template",
        "get_user_info",
        "get_template_name",
        "get_completion_status",
        "get_completion_date",
        "get_detailed_responses",
        "get_recommendation_editor",
        "get_professional_evaluation",
        "get_user_permissions",
        "get_evaluation_type",
        "get_recommendation_status",
    )

    def get_evaluation_type(self, obj):
        return obj.template.evaluation_type if obj.template else "Sin template"

    get_evaluation_type.short_description = "Tipo de Evaluación"

    def format_datetime(self, date):
        """Función auxiliar para formatear fechas de manera consistente"""
        if not date:
            return None

        # Asegurar que la fecha está en UTC
        if timezone.is_naive(date):
            date = timezone.make_aware(date)

        # Convertir a hora local
        local_date = timezone.localtime(date)

        return {
            "iso": date.isoformat(),
            "formatted": date_format(local_date, "j \d\e F \d\e Y, H:i"),
            "timesince": timesince(local_date),
        }

    def get_professional_evaluation(self, obj):
        """Renderiza el formulario de evaluación profesional"""
        if (
            not hasattr(obj, "template")
            or obj.template.evaluation_type != "PROFESSIONAL"
        ):
            return None

        request = getattr(self, "request", None)
        if not request:
            return "Error: No se pudo obtener el contexto de la solicitud"

        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            professional_responses = evaluation_form.professional_responses or {}

            # Verificar si el usuario tiene permisos de edición
            can_edit = self._check_permission(request.user, "change")

            context = {
                "health_category": obj,
                "evaluation_form": evaluation_form,
                "professional_responses": professional_responses,
                "completed_date": evaluation_form.completed_date,
                "is_completed": bool(evaluation_form.completed_date),
                "evaluation_tags": obj.template.evaluation_tags if obj.template else [],
                "can_edit": can_edit,  # Solo permitir edición si tiene permisos
                "user_is_authorized": can_edit,
            }

            template_path = "admin/healthcategory/professional_evaluation.html"
            try:
                return mark_safe(render_to_string(template_path, context))
            except TemplateDoesNotExist:
                return format_html(
                    '<div class="text-red-500">Template no encontrado: {}</div>',
                    template_path,
                )
        except Exception as e:
            return format_html(
                '<div class="text-red-500">Error al cargar evaluación profesional: {}</div>',
                str(e),
            )
        
    get_professional_evaluation.short_description = "Evaluación Profesional"

    def get_recommendation_editor(self, obj):
        """Renderiza el editor de recomendaciones"""
        try:
            request = getattr(self, "request", None)
            if not request:
                return "Error: No se pudo obtener el contexto de la solicitud"

            # Verificar si el usuario tiene permisos de edición
            can_edit = self._check_permission(request.user, "change")

            recommendation = obj.get_or_create_recommendation()

            context = {
                "health_category": obj,
                "recommendation": recommendation,
                "can_edit": can_edit,  # Solo permitir edición si tiene permisos
                "user_is_authorized": can_edit,
                "user_name": request.user.get_full_name() or request.user.username,
                "user_role": (
                    "Doctor"
                    if request.user.groups.filter(name="DOCTOR").exists()
                    else "Superusuario"
                ),
                "default_recommendations": obj.template.default_recommendations,
            }

            template_path = "admin/healthcategory/recommendation_editor.html"
            return mark_safe(render_to_string(template_path, context))

        except Exception as e:
            return format_html(
                '<div class="text-red-500">Error al cargar editor de recomendación: {}</div>',
                str(e),
            )

    def get_template_context(self, request, obj=None):
        """Método helper para obtener el contexto común de los templates"""
        context = (
            super().get_template_context(request, obj)
            if hasattr(super(), "get_template_context")
            else {}
        )
        context.update(
            {
                "can_edit": True,  # Permitir edición si es doctor o superuser
                "user_is_authorized": True,  # Indicar que el usuario está autorizado
                "user_name": request.user.get_full_name() or request.user.username,
                "user_role": (
                    "Doctor"
                    if request.user.groups.filter(name="DOCTOR").exists()
                    else "Superusuario"
                ),
            }
        )
        return context

    def get_user_info(self, obj):
        if obj.user and obj.user.user:
            user = obj.user.user
            display_name = user.get_full_name() or user.username
            category = obj.template.name if obj.template else "Sin categoría"
            return f"{display_name} - {category}"
        return "-"

    get_user_info.short_description = (
        "Paciente"  # Cambiado de "Información de Usuario" a "Paciente"
    )

    def get_template_name(self, obj):
        return obj.template.name

    get_template_name.short_description = "Plantilla"

    def get_completion_status(self, obj):
        status = obj.get_status()
        if status["is_completed"]:
            return "Completado"
        elif status["is_draft"]:
            return "Pendiente"
        else:
            return "Pendiente"

    get_completion_status.short_description = "Estado"

    def get_completion_date(self, obj):
        """Muestra la fecha de completado según el tipo de evaluación"""
        try:
            if not obj.template:
                return "-"

            evaluation_type = obj.template.evaluation_type

            # Intentar obtener o crear el form si no existe
            from prevcad.models import EvaluationForm

            evaluation_form, created = EvaluationForm.objects.get_or_create(
                health_category=obj,
                defaults={
                    "responses": {},
                    "professional_responses": {},
                    "question_nodes": (
                        obj.template.evaluation_form.get("question_nodes", [])
                        if obj.template.evaluation_form
                        else []
                    ),
                },
            )

            def format_date(date):
                """Formatea la fecha de manera más legible"""
                if not date:
                    return None
                from django.utils import formats

                return formats.date_format(date, "d/m/Y H:i")

            # Para evaluaciones normales
            if evaluation_type == "SELF":
                if evaluation_form.responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return f"✅ {date_info}" if date_info else "✅ Completado"
                return "⏳ Pendiente"

            # Para evaluaciones profesionales
            else:
                if evaluation_form.professional_responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return f"✅ {date_info}" if date_info else "✅ Completado"
                elif evaluation_form.responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return (
                        f"⏳ Evaluado el {date_info}" if date_info else "⏳ Por evaluar"
                    )
                return "⏳ Pendiente"

        except Exception as e:
            print(
                f"Error en get_completion_date para HealthCategory {obj.id}: {str(e)}"
            )
            import traceback

            traceback.print_exc()
            return f"❌ Error: {str(e)}"

    get_completion_date.short_description = "Estado"

    def get_recommendation_status(self, obj):
        """Muestra el estado de la recomendación con mejor formato"""
        try:
            recommendation = obj.get_or_create_recommendation()

            if recommendation.status_color:
                color_map = {
                    "rojo": ("#DC2626", "#FEF2F2", "🔴"),
                    "amarillo": ("#D97706", "#FEF3C7", "🟡"),
                    "verde": ("#059669", "#D1FAE5", "🟢"),
                }
                print(recommendation.status_color)
                bg_color, text_color, emoji = color_map.get(
                    recommendation.status_color, ("#6B7280", "#F3F4F6", "⚪")
                )

                return format_html(
                    '<span style="color: {}; background: {}; padding: 4px 8px; '
                    'border-radius: 9999px; font-size: 0.75rem;">{} {}</span>',
                    bg_color,
                    text_color,
                    emoji,
                    recommendation.is_draft and "Borrador" or "Completado",
                )

            return format_html(
                '<span style="color: #6B7280; background: #F3F4F6; padding: 4px 8px; '
                'border-radius: 9999px; font-size: 0.75rem;">⚪ Sin estado</span>'
            )

        except Exception as e:
            return format_html('<span style="color: #DC2626;">Error: {}</span>', str(e))

    get_recommendation_status.short_description = "Estado"
    get_recommendation_status.allow_tags = True

    def get_detailed_responses(self, obj):
        responses = obj.evaluation_form.responses or {}
        processed_responses = {}

        for node_id, response in responses.items():
            processed_response = response.copy()
            if response.get("type") == "SINGLE_CHOICE_QUESTION":
                options = response["answer"].get("options", [])
                selected = response["answer"].get("selectedOption")
                if selected is not None and selected < len(options):
                    processed_response["answer"]["selected_text"] = options[selected]
            elif response.get("type") == "MULTIPLE_CHOICE_QUESTION":
                options = response["answer"].get("options", [])
                selected = response["answer"].get("selectedOptions", [])
                processed_response["answer"]["selected_texts"] = [
                    options[idx] for idx in selected if idx < len(options)
                ]
            processed_responses[node_id] = processed_response

        context = {"responses": processed_responses}
        return mark_safe(
            render_to_string("admin/healthcategory/detailed_responses.html", context)
        )

    get_detailed_responses.short_description = "Detalle de Respuestas"

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Recommendation):
                instance.updated_by = request.user.username
                if not instance.is_draft and instance.is_signed:
                    instance.signed_by = request.user.username
                    instance.signed_at = timezone.now()
            instance.save()
        formset.save_m2m()

    def get_default_recommendation(self, obj):
        """Retorna la recomendación por defecto basada en el tipo de evaluación"""
        return obj.template.get_default_recommendation()

    def response_change(self, request, obj):
        """Personaliza la respuesta después de intentar guardar"""
        if "_save" in request.POST and hasattr(request, "_permission_denied"):
            # Si hubo un error de permisos, redirigir de vuelta al formulario
            url = reverse(
                "admin:prevcad_healthcategory_change",
                args=[obj.pk],
            )
            return HttpResponseRedirect(url)
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        from django.db import connection
        import time

        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            try:
                with transaction.atomic():
                    # Guardar objeto principal
                    super().save_model(request, obj, form, change)

                    # Obtener o crear recomendación
                    recommendation = obj.get_or_create_recommendation()

                    # Manejar archivo de video
                    if "video" in request.FILES:
                        if recommendation.video:
                            recommendation.video.delete(save=False)
                        recommendation.video = request.FILES["video"]

                    # Guardar otros campos
                    recommendation.text = request.POST.get("text", "")
                    recommendation.status_color = request.POST.get(
                        "status_color", "gris"
                    )
                    recommendation.is_draft = request.POST.get("is_draft") == "true"
                    recommendation.updated_by = request.user.username
                    recommendation.updated_at = timezone.now()

                    # Guardar cambios
                    recommendation.save()
                    # Añadir un mensaje según el estado de la recomendación

                    return JsonResponse(
                        {"success": True, "message": "Cambios guardados correctamente"}
                    )

                break  # Si llegamos aquí, todo salió bien

            except OperationalError as e:
                attempt += 1
                if attempt == max_attempts:
                    messages.error(request, "Error al guardar: Base de datos ocupada")
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "Error al guardar: Base de datos ocupada",
                        },
                        status=503,
                    )
                time.sleep(0.5)  # Esperar antes de reintentar
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Error al guardar: Base de datos ocupada",
                    },
                    status=503,
                )

            except Exception as e:
                print("Error al guardar:", str(e))
                messages.error(request, f"Error al guardar: {str(e)}")
                return JsonResponse({"success": False, "error": str(e)}, status=500)

    def save_professional_evaluation(self, request, object_id):
        """Vista para guardar la evaluación profesional"""
        if request.method != "POST":
            return JsonResponse({"error": "Método no permitido"}, status=405)

        try:
            # Debug
            print(f"Buscando objeto con ID: {object_id}")

            # Obtener el objeto
            obj = self.get_object(request, unquote(object_id))
            if not obj:
                print(f"No se encontró el objeto con ID: {object_id}")
                return JsonResponse({"error": "Objeto no encontrado"}, status=404)

            print(f"Objeto encontrado: {obj}")  # Debug

            data = json.loads(request.body)
            evaluation_form = obj.get_or_create_evaluation_form()

            # Obtener las respuestas profesionales
            professional_responses = data.get("professional_responses", {})

            # Actualizar las respuestas
            if evaluation_form.professional_responses is None:
                evaluation_form.professional_responses = {}
            evaluation_form.professional_responses.update(professional_responses)

            # Manejar el estado de completado
            if data.get("complete", False):
                now = timezone.now()
                evaluation_form.is_draft = False
                evaluation_form.completed_date = now

                # Actualizar la recomendación
                recommendation = obj.get_or_create_recommendation()
                if recommendation:
                    recommendation.is_draft = False
                    recommendation.updated_by = request.user.username
                    recommendation.updated_at = now
                    recommendation.save()

            evaluation_form.save()

            date_info = self.format_datetime(evaluation_form.completed_date)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Evaluación guardada correctamente",
                    "is_draft": evaluation_form.is_draft,
                    "completed_date": date_info["iso"] if date_info else None,
                    "formatted_date": date_info["formatted"] if date_info else None,
                }
            )

        except Exception as e:
            import traceback

            print("Error completo:")
            print(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)

    def update_recommendation_view(self, request, category_id):
        try:
            category = HealthCategory.objects.get(id=category_id)

            if request.method == "POST":
                data = json.loads(request.body)
                now = timezone.now()

                recommendation = category.get_or_create_recommendation()
                recommendation.text = data.get("recommendation_text", "").strip()
                recommendation.status_color = data.get("status_color", "").strip()
                recommendation.is_draft = data.get("is_draft", False)
                recommendation.updated_by = request.user.username
                recommendation.updated_at = now
                recommendation.professional_name = (
                    request.user.get_full_name() or request.user.username
                )
                recommendation.professional_role = " • ".join(
                    [group.name for group in request.user.groups.all()]
                    or ["Profesional de la salud"]
                )

                if not recommendation.is_draft:
                    recommendation.signed_by = request.user.username
                    recommendation.signed_at = now

                recommendation.save()

                date_info = self.format_datetime(now)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Recomendación actualizada correctamente",
                        "recommendation": {
                            "updated_at": date_info["iso"],
                            "formatted_date": date_info["formatted"],
                            "timesince": date_info["timesince"],
                            "professional": {
                                "name": recommendation.professional_name,
                                "role": recommendation.professional_role,
                            },
                        },
                    }
                )

        except HealthCategory.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Categoría no encontrada"}, status=404
            )

        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Error: {str(e)}"}, status=500
            )

    def get_readonly_fields(self, request, obj=None):
        """Define campos de solo lectura basados en permisos"""
        readonly = list(self.readonly_fields)

        if obj:  # Solo para objetos existentes
            user_profile = getattr(request.user, "profile", None)

            # Si el usuario no puede editar o el template está en readonly
            if not obj.template.can_user_edit(user_profile) or obj.template.is_readonly:
                # Hacer todos los campos readonly excepto los que ya lo son
                all_fields = [f.name for f in self.model._meta.fields]
                readonly.extend([f for f in all_fields if f not in readonly])

                # Mantener campos base siempre readonly
                readonly.extend(self.base_fields)

            # Campos que siempre son readonly
            readonly.extend(obj.READONLY_FIELDS)

        return list(set(readonly))  # Eliminar duplicados

    def changelist_view(self, request, extra_context=None):
        """Guarda la request en el admin"""
        self.request = request  # Guardamos la request directamente en self
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Guarda la request en el admin"""
        self.request = request  # Guardamos la request directamente en self
        return super().changeform_view(request, object_id, form_url, extra_context)

    def _check_permission(self, user, perm_type):
        """Verifica permisos incluyendo grupos y permisos directos"""
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Verificar tanto permisos directos como de grupo
        perm_name = f"prevcad.{perm_type}_healthcategory"
        return user.has_perm(perm_name) or any(
            group.permissions.filter(codename=f"{perm_type}_healthcategory").exists()
            for group in user.groups.all()
        )

    def has_view_permission(self, request, obj=None):
        return self._check_permission(request.user, "view")

    def has_change_permission(self, request, obj=None):
        return self._check_permission(request.user, "change")

    def has_add_permission(self, request):
        return self._check_permission(request.user, "add")

    def has_delete_permission(self, request, obj=None):
        return self._check_permission(request.user, "delete")

    def has_module_permission(self, request):
        return any(
            [
                self._check_permission(request.user, perm)
                for perm in ["view", "change", "add", "delete"]
            ]
        )

    def get_user_permissions(self, obj):
        """Muestra los permisos del usuario actual"""
        try:
            request = getattr(self, "request", None)
            if not request or not request.user.is_authenticated:
                return format_html(
                    '<span style="color: #DC2626; background: #FEF2F2; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">🚫 Sin acceso</span>'
                )

            user = request.user

            # Superusuario
            if user.is_superuser:
                return format_html(
                    '<div style="display: flex; gap: 4px; flex-direction: column;">'
                    '<span style="color: #059669; background: #ECFDF5; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">✏️ Acceso completo</span>'
                    '<span style="color: #4F46E5; background: #EEF2FF; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">👑 Superusuario</span>'
                    "</div>"
                )

            # Verificar permisos
            perms = []
            if self._check_permission(user, "view"):
                perms.append("Ver")
            if self._check_permission(user, "change"):
                perms.append("Editar")
            if self._check_permission(user, "add"):
                perms.append("Añadir")
            if self._check_permission(user, "delete"):
                perms.append("Eliminar")

            if perms:
                groups = [g.name for g in user.groups.all()]
                role = "Staff" if user.is_staff else "Usuario"

                return format_html(
                    '<div style="display: flex; gap: 4px; flex-direction: column;">'
                    '<span style="color: #0891b2; background: #CFFAFE; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">⚙️ {} ({})</span>'
                    '<span style="color: #4F46E5; background: #EEF2FF; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">🔑 {}</span>'
                    "</div>",
                    role,
                    " • ".join(groups) if groups else "Sin grupos",
                    ", ".join(perms),
                )

            return format_html(
                '<span style="color: #DC2626; background: #FEF2F2; padding: 2px 8px; '
                'border-radius: 4px; font-size: 0.75rem;">🚫 Sin acceso</span>'
            )

        except Exception as e:
            return format_html('<span style="color: #DC2626;">Error: {}</span>', str(e))

    get_user_permissions.short_description = "Permisos"
    get_user_permissions.allow_tags = True

    def get_fieldsets(self, request, obj=None):
        """Define el orden específico de los campos en el formulario"""
        return [
            (
                None,
                {
                    "fields": (
                        "get_completion_date",
                        "get_user_info",
                        "get_template_name",
                        "get_recommendation_status",
                        "get_evaluation_type",
                        "get_user_permissions",
                        "get_professional_evaluation",
                        "get_recommendation_editor",
                        "get_detailed_responses",
                    )
                },
            ),
        ]

    def get_actions_display(self, obj):
        """Muestra botones de acción basados en permisos"""
        try:
            request = getattr(self, "request", None)
            if not request:
                return "-"

            # Solo mostrar botones si tiene permisos de edición
            if self._check_permission(request.user, "change"):
                actions = []

                # Botón de editar evaluación
                if obj.template.evaluation_type == "PROFESSIONAL":
                    actions.append(
                        '<a href="{}" class="button" style="'
                        "background: #059669; color: white; padding: 4px 8px; "
                        "border-radius: 4px; text-decoration: none; font-size: 0.75rem; "
                        'margin-right: 4px;">📝 Evaluar</a>'.format(
                            f"/admin/prevcad/healthcategory/{obj.id}/change/#professional-evaluation"
                        )
                    )

                # Botón de editar recomendación
                actions.append(
                    '<a href="{}" class="button" style="'
                    "background: #2563eb; color: white; padding: 4px 8px; "
                    "border-radius: 4px; text-decoration: none; font-size: 0.75rem; "
                    'margin-right: 4px;">✏️ Recomendar</a>'.format(
                        f"/admin/prevcad/healthcategory/{obj.id}/change/#recommendation-editor"
                    )
                )

                return format_html(
                    '<div style="display: flex; gap: 4px;">{}</div>',
                    mark_safe("".join(actions)),
                )

            # Si solo tiene permisos de lectura, mostrar mensaje
            return format_html(
                '<span style="color: #6B7280; background: #F3F4F6; padding: 2px 8px; '
                'border-radius: 4px; font-size: 0.75rem;">👁️ Solo lectura</span>'
            )

        except Exception as e:
            return format_html('<span style="color: #DC2626;">Error: {}</span>', str(e))

    get_actions_display.short_description = "Acciones"
    get_actions_display.allow_tags = True

    class Media:
        css = {
            "all": (
                "https://cdn.tailwindcss.com",
                "admin/css/forms.css",
                "admin/css/widgets.css",
            )
        }

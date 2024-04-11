import json
from django.db import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template
from django.db.models import Q, Count, Prefetch, Case, When, IntegerField, Avg, F
from weasyprint import HTML

from accounts.services import get_teacher_request_gpt_analyze

from .models import Material, MaterialRejection, Room, RoomMessage, TeacherRequest, Theme, User, MaterialInfo, FavoriteMaterial
from .forms import CommentForm, CustomUserCreationForm, MaterialForm, MaterialRejectionForm, MaterialSearchForm, TeacherRequestContentForm, TeacherRequestForm

@login_required
def my_materials(request):
    form, materials = None, None

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            if form.is_valid():
                material = form.save(commit=False)
                material.author = request.user
                material.save()
                return redirect('my_materials')
        else:
            form = MaterialForm()

        materials = Material.objects.filter(
            author=request.user
        ).annotate(
            views=Count('infos'),
        ).select_related('author').order_by('-pk')

    context = {
        'form': form,
        'materials': materials
    }

    return render(request, 'my_materials.html', context=context)


def home(request):
    search_form = MaterialSearchForm(request.GET)
    materials = None
    if request.user.is_authenticated:

        materials = Material.objects.annotate(
            views=Count('infos')
        ).select_related('author').order_by('-status', '-pk')
        user = request.user

        if user.role == User.Role.CUSTOMER:
            materials = materials.filter(
                status=Material.Status.VERIFIED,
                rating__gte=settings.MATERIAL_MIN_RATING,
                views__gte=settings.MATERIAL_MIN_VIEWS
            )
        elif user.role == User.Role.EXPERT:
            materials = materials.filter(status=Material.Status.NEW)

        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            selected_subject = search_form.cleaned_data.get('subject')
            selected_grade = search_form.cleaned_data.get('grade')
            selected_rating = search_form.cleaned_data.get('rating')

            if selected_subject:
                if selected_subject != '':
                    materials = materials.filter(subject=selected_subject)

            if selected_grade:
                if selected_grade != '':
                    materials = materials.filter(grade=selected_grade)

            if selected_rating:
                if selected_rating != '':
                    materials = materials.filter(rating=selected_rating)

            if search_query:
                materials = materials.filter(title__icontains=search_query)

    context = {
        'search_form': search_form,
        'materials': materials,
        'customer_role': User.Role.CUSTOMER,
        'expert_role': User.Role.EXPERT
    }

    return render(request, 'home.html', context=context)


def green_page(request):
    materials = None
    search_form = MaterialSearchForm(request.GET)

    if request.user.is_authenticated:

        materials = Material.objects.filter(
            status=Material.Status.VERIFIED
        ).annotate(
            views=Count('infos')
        ).select_related('author').order_by('-status', '-pk')

        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            selected_subject = search_form.cleaned_data.get('subject')
            selected_grade = search_form.cleaned_data.get('grade')
            selected_rating = search_form.cleaned_data.get('rating')

            if selected_subject:
                if selected_subject != '':
                    materials = materials.filter(subject=selected_subject)

            if selected_grade:
                if selected_grade != '':
                    materials = materials.filter(grade=selected_grade)

            if selected_rating:
                if selected_rating != '':
                    materials = materials.filter(rating=selected_rating)

            if search_query:
                materials = materials.filter(title__icontains=search_query)

    context = {
        'search_form': search_form,
        'materials': materials,
    }

    return render(request, 'green_page.html', context=context)


@login_required
def verify_material(request, material_pk):
    if request.user.role == User.Role.EXPERT:
        material = get_object_or_404(Material, pk=material_pk)
        material.status = Material.Status.VERIFIED
        material.save()
    return redirect('home')


@login_required
def reject_material(request, material_pk):
    if request.user.role != User.Role.EXPERT:
        return JsonResponse({'error': 'User is not authorized to reject materials.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        form = MaterialRejectionForm(data)
        if form.is_valid():
            material = get_object_or_404(Material, pk=material_pk)
            rejection_reason = form.cleaned_data['reason']
            rejection, created = MaterialRejection.objects.get_or_create(
                material=material, expert=request.user)
            rejection.description = rejection_reason
            rejection.save()
            material.status = Material.Status.REJECTED
            material.save(update_fields=['status'])
            return JsonResponse({'message': 'Material rejected successfully.'})
        else:
            return JsonResponse({'error': 'Invalid form data.'}, status=400)
    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)


class CustomUserCreateView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@login_required
def material_detail(request, pk):
    try:
        material = Material.objects.annotate(
            views=Count('infos'),
            rating_1_star=Count(
                Case(When(infos__user_rating=1, then=1), output_field=IntegerField())),
            rating_2_star=Count(
                Case(When(infos__user_rating=2, then=1), output_field=IntegerField())),
            rating_3_star=Count(
                Case(When(infos__user_rating=3, then=1), output_field=IntegerField())),
            rating_4_star=Count(
                Case(When(infos__user_rating=4, then=1), output_field=IntegerField())),
            rating_5_star=Count(
                Case(When(infos__user_rating=5, then=1), output_field=IntegerField())),
        ).prefetch_related(
            Prefetch('infos', MaterialInfo.objects.select_related('user'))
        ).get(pk=pk)
    except Material.DoesNotExist:
        raise Http404

    is_favorite = request.user.favorite_materials.filter(material=material).exists()

    if material.author_id != request.user.pk and request.user.role != User.Role.EXPERT:
        material_info, _ = MaterialInfo.objects.get_or_create(
            material=material, user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            material_info.user_comment = form.cleaned_data['user_comment']
            material_info.user_rating = form.cleaned_data['user_rating']
            material_info.commented_at = timezone.now()
            material_info.save(
                update_fields=['user_comment', 'user_rating', 'commented_at'])

            infos = MaterialInfo.objects.filter(material=material).exclude(commented_at__isnull=True).aggregate(
                avg_rating=Avg('user_rating')
            )
            material.rating = infos['avg_rating']
            material.save(update_fields=['rating'])
    else:
        form = None
        if material.author_id != request.user.pk and request.user.role != User.Role.EXPERT and material_info.commented_at is None:
            form = CommentForm(instance=material_info)

    context = {
        'material': material,
        'form': form,
        'is_favorite': is_favorite,
    }
    return render(request, 'material_detail.html', context)


@login_required
def rejections(request):
    materials = Material.objects.annotate(
        views=Count('infos')
    ).prefetch_related(
        'rejections'
    ).filter(
        author=request.user, status=Material.Status.REJECTED
    ).all()

    context = {
        'materials': materials,
    }
    return render(request, 'rejections.html', context)

@login_required
def add_to_favorites(request, pk):
    material = get_object_or_404(Material, pk=pk)
    
    # Check if the material is already in favorites
    if request.user.favorite_materials.filter(material=material).exists():
        messages.warning(request, "This material is already in your favorites.")
    else:
        # Add material to favorites
        favorite_material = FavoriteMaterial.objects.create(user=request.user, material=material)
        messages.success(request, f"{material.title} has been added to your favorites.")
    
    # Redirect back to the material detail page
    return redirect('material_detail', pk=pk)

@login_required
def favorite_materials(request):
    favorite_materials = request.user.favorite_materials.all()
    context = {
        'favorite_materials': favorite_materials
    }
    return render(request, 'favorite_materials.html', context)

@login_required
def remove_from_favorites(request, favorite_material_id):
    favorite_material = get_object_or_404(FavoriteMaterial, pk=favorite_material_id)
    
    # Check if the favorite material belongs to the current user
    if favorite_material.user != request.user:
        # If not, display an error message
        messages.error(request, "You are not authorized to remove this material from favorites.")
    else:
        # Delete the favorite material
        favorite_material.delete()
        messages.success(request, "Material removed from favorites successfully.")
    
    # Redirect back to the favorite materials page
    return redirect('favorite_materials')


@login_required
def room(request):
    try:
        room, _ = Room.objects.select_related(
            'customer'
        ).get_or_create(customer_id=request.user.pk)

        room_messages = RoomMessage.objects.order_by('-created_at').annotate(
            author_username = F('author__username')
        ).filter(room_id=room.pk).order_by('-created_at')[:settings.LAST_N_MESSAGE][::-1]

    except IntegrityError as e:
        raise Http404
    return render(request, 'room.html', {'room': room, 'room_messages': room_messages})


@login_required
def teacher_requests(request):
    if request.method == 'POST':
        form = TeacherRequestForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data.pop('language')
            teacher_request: TeacherRequest = form.save(commit=False)
            teacher_request.author = request.user
            teacher_request.content = get_teacher_request_gpt_analyze(
                grade=teacher_request.grade, subject=teacher_request.subject.name_en,
                theme=teacher_request.theme.name_en, requirements=teacher_request.template.prompt,
                language=language
            )
            teacher_request.save()
            return redirect('teacher_request_detail', pk=teacher_request.pk)
    else:
        form = TeacherRequestForm()

    teacher_requests = TeacherRequest.objects.filter(
        author=request.user
    ).select_related('author', 'subject', 'theme').order_by('-pk')

    context = {
        'form': form,
        'teacher_requests': teacher_requests
    }

    return render(request, 'teacher_requests.html', context=context)


@login_required
def teacher_request_detail(request, pk):
    try:
        teacher_request = TeacherRequest.objects.filter(
            author=request.user
        ).select_related('author', 'subject', 'theme').order_by('-pk').get(pk=pk)
    except TeacherRequest.DoesNotExist:
        raise Http404
    
    if request.method == 'POST':
        form = TeacherRequestContentForm(request.POST, instance=teacher_request)
        if form.is_valid():
            form.save()
    else:
        form = TeacherRequestContentForm(instance=teacher_request)

    context = {
        'teacher_request': teacher_request,
        'form': form
    }
    return render(request, 'teacher_request_detail.html', context)


def get_themes(request):
    subject_id = request.GET.get('subject_id')
    themes = [{
        'id': theme.pk,
        'name': str(theme)
    } for theme in Theme.objects.filter(subject_id=subject_id).all()]
    return JsonResponse({'themes': list(themes)})


@login_required
def teacher_request_detail_generate_pdf(request, pk):
    try:
        teacher_request = TeacherRequest.objects.filter(
            author=request.user
        ).select_related('author', 'subject', 'theme').order_by('-pk').get(pk=pk)
    except TeacherRequest.DoesNotExist:
        raise Http404
    
    context = {
        'content': teacher_request.content
    }
    template = get_template('teacher_request_detail_generate_pdf.html')
    html_content = template.render(context)

    # Generate PDF
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # Return PDF as a download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
    return response
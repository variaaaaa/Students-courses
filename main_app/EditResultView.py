from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, StudentResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        context = {
            'form': resultForm,
            'page_title': "Результаты"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Результаты"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                exam = form.cleaned_data.get('exam')
                result = StudentResult.objects.get(student=student, subject=subject)
                result.exam = exam

                result.save()
                messages.success(request, "Баллы обновлены!")
                return redirect(reverse('edit_student_result'))
            except Exception as e:
                messages.warning(request, "Ошибка обновления данных.")
        else:
            messages.warning(request, "Ошибка обновления данных")
        return render(request, "staff_template/edit_student_result.html", context)

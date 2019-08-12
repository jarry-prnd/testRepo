from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.http import HttpResponse
from django.db.models import F, Sum
from django.forms import formset_factory
from django.views import generic
from rest_framework import generics, permissions
from .models import Question, Choice, Responser, ResponseRecord
from .forms import QuestionForm, ChoiceForm, ResponserForm, ResponseRecordForm, ResponseForm, ResponseFormSet

import csv


def get_DB_info():
    DB_info = []
    question_list = Question.objects.prefetch_related('choices').all()
    for question in question_list:
        data = {
            'question_id': question.id,
            'question_type': question.question_type,
            'question_text': question.question_text,
            'limit': question.limit,
            'choice_list': list(question.choices.values_list('id', 'choice_text'))
        }
        DB_info.append(data)
    return DB_info


def test(request):
    # GET : 현재 존재하는 Question/Choice 모델 객체들의 정보 회수
    # POST : 응답이 POST된 순간에 존재하는 Question/Choice 모델 객체들의 정보 회수
    # 이를 바탕으로 설문 문항 정보 구성
    question_cnt = Question.objects.count()
    DB_info = get_DB_info()

    if (request.method == "GET"):
        # 현재 존재하는 Question 객체의 갯수만큼 Form을 담을 FormSet을 만들어내는 객체 생성
        ResponseFormSetFactory = formset_factory(form=ResponseForm, formset=ResponseFormSet, extra=question_cnt)

        # 설문 문항 정보를 바탕으로 FormSet 생성 및 렌더링
        forms = ResponseFormSetFactory(DB_info=DB_info)
        return render(request, 'survey/test.html', {'forms': forms})

    elif (request.method == "POST"):
        # 응답이 POST된 순간에 존재하는 Question 객체의 갯수만큼 Form을 담을 FormSet을 만들어내는 객체 생성
        # 그 갯수만큼 응답하지 않았다면 모든 문항에 응답하지 않은 것이므로 validation check에 걸림
        ResponseFormSetFactory = formset_factory(form=ResponseForm, formset=ResponseFormSet, extra=0, min_num=question_cnt, validate_min=True)

        # POST된 응답 내용을 가지고 Form들을 생성, validation check (FormSet, Form)
        # validation check에 걸리면 이미 응답한 Form은 그대로 보여주도록 함
        forms = ResponseFormSetFactory(request.POST, request.FILES, DB_info=DB_info)

        # validation check
        if (forms.is_valid()):
            print("@@@ validation check:", True)
            return redirect(reverse('submit-complete'))
        else:
            print("@@@ validation check:", False)
            print("@@@ validation error messages:", forms.errors)
            return render(request, 'survey/test.html', {'forms': forms})


def index_view(request):
    if (request.method == 'GET'):
        question_list = Question.objects.prefetch_related('choices').all()
        return render(request, 'survey/index.html', {'question_list': question_list, 'user': request.user})

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def submit_view(request):
    if (request.method == 'POST'):
        # check if all questions are responsed
        questions_num_responsed = len(list(filter(lambda x: x.isdigit(), list(request.POST.keys()))))
        questions_num_all = Question.objects.count()
        if (questions_num_responsed < questions_num_all):
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('index'))           # VALIDATION ERROR

        # record the responser
        responser_form = ResponserForm({'phone_number': request.POST['phone_number']})
        responser = None
        if responser_form.is_valid():
            responser = responser_form.save()
        else:
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('index'))           # VALIDATION ERROR

        # obtail the set of choices that user selected
        choice_set = set()
        choice_rank = dict()
        for key in request.POST.keys():
            if (key.isdigit()):
                for choice_id in request.POST.getlist(key):
                    choice_set.add(int(choice_id))
            elif ("_sorted" in key):
                checkbox_list = [ int(choice_id) for choice_id in request.POST[key].split(",")]
                for idx, choice_id in enumerate(checkbox_list):
                    choice_rank[choice_id] = idx+1

        # get the queryset of the choices together with the related Question objects
        choice_list = Choice.objects.select_related('question').filter(pk__in=choice_set)

        # record all the responses
        response_record_list = []
        for choice in choice_list:
            if (choice.id in choice_rank.keys()):
                response_record = ResponseRecord(responser=responser, choice=choice, rank=choice_rank[choice.id])
            else:
                response_record = ResponseRecord(responser=responser, choice=choice)
            response_record_list.append(response_record)
        ResponseRecord.objects.bulk_create(response_record_list)

        # increase # responses of each choice
        choice_list.update(response_num=F('response_num')+1)

        return redirect(reverse('submit-complete'))

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def submit_complete_view(request):
    if (request.method == 'GET'):
        return render(request, 'survey/submit-complete.html')

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def survey_admin_view(request):
    if (request.user.is_anonymous):
        return redirect(reverse('index'))

    if (request.method == 'GET'):
        question_list = Question.objects.prefetch_related('choices').annotate(response_num_total=Sum('choices__response_num'))
        return render(request, 'survey/survey-admin.html', {'question_list': question_list})


def login_view(request):
    if (request.user.is_authenticated):
        return redirect(reverse('index'))

    if (request.method == 'GET'):
        return render(request, 'survey/login.html')

    elif (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if (user is not None):
            auth.login(request, user)
            return redirect(reverse('index'))
        else:
            messages.error(request, '존재하지 않는 관리자 계정입니다.')
            return redirect(reverse('login'))

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def logout_view(request):
    if (request.user.is_anonymous):
        return redirect(reverse('index'))

    if (request.method == 'GET'):
        auth.logout(request)
        return redirect(reverse('index'))

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def signup_view(request):
    if (request.user.is_authenticated):
        return redirect(reverse('index'))

    if (request.method == 'GET'):
        return render(request, 'survey/signup.html')

    elif (request.method == 'POST'):
        if (request.POST['password1'] == request.POST['password2']):
            user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'], is_superuser=True, is_staff=True)
            auth.login(request, user)
            messages.success(request, '회원가입 성공')
            return redirect(reverse('index'))
        else:
            messages.error(request, '비밀번호를 확인해주세요.')
            return redirect('signup')

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def csv_download(request):
    if (request.user.is_anonymous):
        return redirect(reverse('index'))

    if (request.method == 'GET'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey-results.csv"'
        writer = csv.writer(response)
        response.write(u'\ufeff'.encode('utf8'))
        question_list = Question.objects.annotate(response_num_total=Sum('choices__response_num'))

        for idx, question in enumerate(question_list):
            writer.writerow(['Q'+str(idx+1), question.question_text])
            writer.writerow(['type', question.question_type])
            if (question.limit == 0):
                writer.writerow(['limit', '1'])
            else:
                writer.writerow(['limit', str(question.limit)])
            for choice in question.choices.all():
                ratio = (choice.response_num * 100) / question.response_num_total
                writer.writerow(['', choice.choice_text, str(choice.response_num) + '표', str(ratio) + '%'])
            writer.writerow([''])
        return response

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def question_post(request):
    # POST
    if (request.method == "POST"):
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('survey-admin'))
        else:
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('survey-admin'))    # VALIDATION ERROR

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def question_detail(request, pk):
    # DELETE
    if (request.method == "GET"):
        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return redirect(reverse('survey-admin'))

    # PUT
    elif (request.method == "POST"):
        question = get_object_or_404(Question, pk=pk)
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect(reverse('survey-admin'))
        else:
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('survey-admin'))    # VALIDATION ERROR

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def choice_post(request):
    # POST
    if (request.method == "POST"):
        form = ChoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('survey-admin'))
        else:
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('survey-admin'))    # VALIDATION ERROR

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def choice_detail(request, pk):
    # DELETE
    if (request.method == "GET"):
        choice = get_object_or_404(Choice, pk=pk)
        choice.delete()
        return redirect(reverse('survey-admin'))

    # PUT
    elif (request.method == "POST"):
        choice = get_object_or_404(Choice, pk=pk)
        form = ChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            return redirect(reverse('survey-admin'))
        else:
            messages.error(request, 'VALIDATION ERROR') # VALIDATION ERROR
            return redirect(reverse('survey-admin'))    # VALIDATION ERROR

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def responser_list(request):
    # GET
    if (request.method == "GET"):
        responser_list = Responser.objects.all()
        return render(request, 'survey/responser-list.html', {'responser_list': responser_list})

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))


def responser_detail(request, pk):
    # GET
    if (request.method == "GET"):
        responser = get_object_or_404(Responser, pk=pk)
        response_record_list = ResponseRecord.objects.prefetch_related('responser', 'choice').filter(responser=responser).order_by('rank').all()
        return render(request, 'survey/responser-detail.html', {'responser': responser, 'response_record_list': response_record_list})

    else:
        messages.error(request, '잘못된 METHOD 요청입니다.')
        return redirect(reverse('index'))

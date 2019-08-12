from django import forms
from django.forms import BaseFormSet
from .models import Question, Choice, Responser, ResponseRecord


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'limit')


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('id', 'question', 'choice_text')


class ResponserForm(forms.ModelForm):
    class Meta:
        model = Responser
        fields = ('id', 'phone_number')


class ResponseRecordForm(forms.ModelForm):
    class Meta:
        model = ResponseRecord
        fields = ('id', 'responser', 'choice', 'rank')


class ResponseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.DB_info = kwargs.pop('DB_info') # 설문 문항 정보 (DB 모델 객체들 정보)
        super(ResponseFormSet, self).__init__(*args, **kwargs)

    # index번째 Form을 만들 때 넘겨주는 kwargs 인자 값 결정
    def get_form_kwargs(self, index):
        kwargs = super(ResponseFormSet, self).get_form_kwargs(index)
        if (index < len(self.DB_info)):
            kwargs['question_id'] = self.DB_info[index]['question_id']
            kwargs['question_text'] = self.DB_info[index]['question_text']
            kwargs['question_type'] = self.DB_info[index]['question_type']
            kwargs['limit'] = self.DB_info[index]['limit']
            kwargs['choice_list'] = self.DB_info[index]['choice_list']
        return kwargs

    # FormSet validation check
    def clean(self):
        cleaned_data = super(ResponseFormSet, self).clean()
        print('@@@ cleaned_data (FormSet) :', cleaned_data)
        # customize validation check here (compare two sets : POST data vs DB data)
        return cleaned_data


class ResponseForm(forms.Form):
    # 문항 ID, 문항 타입, 문항 제목, 선택지 최대 체크 갯수, 선택지
    question_id = forms.IntegerField(widget=forms.HiddenInput)
    question_type = forms.CharField(widget=forms.HiddenInput)
    question_text = forms.CharField(widget=forms.HiddenInput)
    limit = forms.IntegerField(widget=forms.HiddenInput)
    choice_list = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        if ('question_id' in kwargs) :
            # 설문 문항 정보 (DB 모델 객체들 정보) 회수
            question_id = kwargs.pop('question_id')
            question_type = kwargs.pop('question_type')
            question_text = kwargs.pop('question_text')
            limit = kwargs.pop('limit')
            choice_list = kwargs.pop('choice_list')

            # kwargs를 원래대로 복구한 뒤 상위 클래스의 생성자 호출
            super(ResponseForm, self).__init__(*args, **kwargs)

            # 모델 객체들 정보를 바탕으로 Form의 필드들을 적절히 설정해줌 (그래야 다시 렌더링 가능)
            self.fields['question_id'] = forms.IntegerField(widget=forms.HiddenInput, initial=question_id)
            self.fields['question_type'] = forms.CharField(widget=forms.HiddenInput, initial=question_type)
            self.fields['question_text'] = forms.CharField(widget=forms.HiddenInput, initial=question_text)
            if (question_type == "select"):
                self.fields['limit'] = forms.IntegerField(widget=forms.HiddenInput, initial=1)
                self.fields['choice_list'] = forms.ChoiceField(widget=forms.Select, choices=choice_list)
            elif (question_type == "radio"):
                self.fields['limit'] = forms.IntegerField(widget=forms.HiddenInput, initial=1)
                self.fields['choice_list'] = forms.ChoiceField(widget=forms.RadioSelect, choices=choice_list)
            elif (question_type == "checkbox"):
                self.fields['limit'] = forms.IntegerField(widget=forms.HiddenInput, initial=limit)
                self.fields['choice_list'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choice_list)

        else:
            super(ResponseForm, self).__init__(*args, **kwargs)

    # Form validation check
    def clean(self):
        cleaned_data = super(ResponseForm, self).clean()
        print('@@@ cleaned_data (Form) :', cleaned_data)
        # customize validation check here
        if (cleaned_data['question_type'] == "checkbox" and 'choice_list' in cleaned_data):
            if (len(cleaned_data['choice_list']) > cleaned_data['limit']):
                raise forms.ValidationError("You can check up to "+str(cleaned_data['limit'])+' choice(s).')
        return cleaned_data

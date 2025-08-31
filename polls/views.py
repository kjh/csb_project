from urllib.parse import urlparse
from django.forms import ValidationError
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import requests

from .models import Choice, Question

from django.db import connection 

# load_url allowed urls
# allowed_url_list = [''] # FLAW 2 FIX

# Utility fuction that is used to load external poll data
def load_url(data_url):
    #parsed_url = urlparse(poll_url)
    #if parsed_url.netloc in allowed_url_list: 
    res = requests.get(data_url) # FLAW 2     
    #else:
    #    return "url not in allowed list"  

    return res.text

# Seach questions 
def search_question(request):
    hide_latest = True
    question_text = request.GET.get('question_text', '')
    #search_result = Question.objects.filter(question_text__icontains=question_text) # FLAW 1 FIX (changes needed in index.html)
    sql_query = f"SELECT * FROM polls_question WHERE question_text = '{question_text}'" # FLAW 1 start
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        search_result = cursor.fetchall() # FLAW 1 end
    context = { 'search_result': search_result, 'hide_latest': hide_latest}
    return render(request, 'polls/index.html', context)

# Question “index” page – displays the latest few questions.
def index(request):
    hide_search = True
    username = request.user.username

    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list, 'username': username, 'hide_search': hide_search}
    return render(request, 'polls/index.html', context)

# Question “detail” page – displays a question text, with no results but with a form to vote.
# Show edit question link if admin user
def detail(request, question_id):
    admin_user = False
    if request.user.username == 'admin':
        admin_user = True
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question, 'admin_user': admin_user})

# Question “results” page – displays results for a particular question.
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

# Vote action – handles voting for a particular choice in a particular question.
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
# Edit question
def edit_question(request, question_id):
    
    # FLAW 3 anyone can edit question
    #if not request.user.username == 'admin': # Flaw 3 fix
    #    return HttpResponseForbidden('fordidden')
        
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    
    if request.method == 'POST':
        question.additional_data = request.POST.get('additional_data') 
    
        if question.additional_data.startswith(('http://', 'https://')):
            question.additional_data = load_url(question.additional_data)  

        question.question_text = request.POST.get('question_text')
        if question.question_text:
            try:
                question.full_clean() # Flaw 5 fix requires also max_length=200 to work
            except ValidationError:
                return HttpResponseBadRequest("Invalid input")

            
        question.pub_date = request.POST.get('pub_date')
        question.save()
        return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

    return render(request, 'polls/edit_question.html', {'question': question})
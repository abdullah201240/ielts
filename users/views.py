from users.models import History
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
#CNN
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
#SVM
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
#end

from django.http import HttpResponse
import math


# Create your views here.

def Signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken.')
            return redirect('signup')

        # Use create_user with the correct arguments
        new_user = User.objects.create_user(username=email, email=email, password=password)
        new_user.first_name = fname
        new_user.last_name = lname
        new_user.save()

        messages.success(request, 'User registered successfully.')
        return redirect('login')

    return render(request, 'signup.html')

def Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

def Home(request):
    user = request.user
    context = {'user': user}

    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')

        #svm start
        loaded_model = joblib.load('Ml_part/svm_model.joblib')
        new_input = pd.DataFrame({'Question': [question], 'Essay': [answer]})
        vectorizer = joblib.load('Ml_part/tfidf_vectorizer.joblib')
        new_input_tfidf = vectorizer.transform(new_input['Question'] + ' ' + new_input['Essay'])
        predicted_mark = loaded_model.predict(new_input_tfidf)
        print(f'Predicted Marks for New Input: {predicted_mark[0]}')
        #svmend
        #cnn start

        # # Load the model
        # model_path = '/Users/abdullahalsakib/Downloads/Trimester12/ielts/ieltsscore.h5'
        # loaded_model = load_model(model_path)

        # # Set the maximum sequence length for questions and answers
        # max_sequence_length = 100  # Adjust based on your model's input layer

        # # Tokenize and pad sequences
        # tokenizer = Tokenizer(num_words=10000)
        # tokenizer.fit_on_texts([question, answer])

        # # Tokenize and pad sequences for the input data
        # new_question_seq = tokenizer.texts_to_sequences([question])
        # new_answer_seq = tokenizer.texts_to_sequences([answer])
        # new_question_padded = pad_sequences(new_question_seq, maxlen=max_sequence_length)
        # new_answer_padded = pad_sequences(new_answer_seq, maxlen=max_sequence_length)

        # # Debugging: Print tokenized sequences and shapes
        # print("Tokenized Question:", new_question_seq)
        # print("Tokenized Answer:", new_answer_seq)
        # print("Shape of new_question_padded:", new_question_padded.shape)
        # print("Shape of new_answer_padded:", new_answer_padded.shape)

        # # Predict the mark
        # predicted_mark = loaded_model.predict([new_question_padded, new_answer_padded])[0][0]
        #cnn end 

        # print(f"Predicted Mark: {predicted_mark:.2f}")
        rounded_mark = math.ceil(predicted_mark * 2) / 2

        loaded_model = joblib.load('Ml_part/Structure_your_answers_in_logical_paragraphs_svm_model_Coherence_and_Cohesion.pkl')
        Structure = question + ' ' + answer

        # Make a prediction using the loaded model
        prediction1 = loaded_model.predict([Structure])
        context['Structure']=prediction1
        loaded_model = joblib.load('Ml_part/svm_model_Coherence_and_Cohesion_regression.pkl')
        

        # Make a prediction using the loaded model
        prediction0 = loaded_model.predict([Structure])
        mark0 = math.ceil(prediction0 * 2) / 2

        context['Coherence']=mark0
        words = len(answer.split())
        paragraphs = len([p for p in answer.split('\n') if p.strip()]) 

        context['words'] = words
        context['paragraphs'] = paragraphs
        loaded_model = joblib.load('Ml_part/svm_model_Introduction_and_Conclusion_regression.pkl')
        prediction2 = loaded_model.predict([Structure])
        context['Introduction']=prediction2
        loaded_model = joblib.load('Ml_part/Support_main_points_with_an_explanation_and_then_an_example_svm_model_Coherence_and_Cohesion.pkl')
        prediction3 = loaded_model.predict([Structure])
        context['Support']=prediction3
        loaded_model = joblib.load('Ml_part/Use_cohesive_linking_words_accurately_and_appropriately_svm_model_Coherence_and_Cohesion.pkl')
        prediction4 = loaded_model.predict([Structure])
        context['Use']=prediction4

        loaded_model = joblib.load('Ml_part/Vary_your_linking_phrases_using_synonyms_svm_model_Coherence_and_Cohesion.pkl')
        prediction5 = loaded_model.predict([Structure])
        context['Vary']=prediction5

        loaded_model = joblib.load('Ml_part/Lexical_Resource_score.joblib')
        new_input = question + ' ' + answer

        loaded_vectorizer = joblib.load('Ml_part/Lexical_Resource_score_tfidf_vectorizer.joblib')
        new_input_tfidf = loaded_vectorizer.transform([new_input])
        Lexical_mark = loaded_model.predict(new_input_tfidf)
        print(f'Lexical Marks for New Input: {Lexical_mark[0]}')
        rounded_Lexical_mark = math.ceil(Lexical_mark * 2) / 2
        context['Lexical_mark'] = rounded_Lexical_mark

        loaded_model = joblib.load('Ml_part/Try_to_vary_your_vocabulary_using_accurate_synonyms.pkl')
        Try = question + ' ' + answer

        prediction1 = loaded_model.predict([Try])
        context['Try']=prediction1

        loaded_model = joblib.load('Ml_part/Use_less_common_question_specific_words_that_accurately_convey_meaning.pkl')
        Use = question + ' ' + answer

        prediction1 = loaded_model.predict([Use])
        if prediction1==0:
            context['Use_less']='NO'
            print(context['Use_less'])

        elif prediction1==1:
            context['Use_less']='YES'
            print(context['Use_less'])


        

        loaded_model = joblib.load('Ml_part/Check_your_work_for_spelling_and_word_formation_mistakes.pkl')
        Check = question + ' ' + answer

        # Make a prediction using the loaded model
        prediction1 = loaded_model.predict([Check])
        context['Check']=prediction1
        if prediction1==0:
            context['Check']='NO'
            print(context['Check'])

        elif prediction1==1:
            context['Check']='YES'
            print(context['Check'])

        loaded_model = joblib.load('Ml_part/Grammatical_Range_score.joblib')
        new_input = question + ' ' + answer

        loaded_vectorizer = joblib.load('Ml_part/Grammatical_Range_score_tfidf_vectorizer.joblib')
        new_input_tfidf = loaded_vectorizer.transform([new_input])
        Grammatica_mark = loaded_model.predict(new_input_tfidf)
        print(f'Lexical Marks for New Input: {Grammatica_mark[0]}')
        rounded_Grammatica_mark = math.ceil(Grammatica_mark * 2) / 2
        context['Grammatica_mark'] = rounded_Grammatica_mark

        loaded_model = joblib.load('Ml_part/Use_a_variety_of_complex_and_simple_sentences.pkl')
        Use_a = question + ' ' + answer
        prediction1 = loaded_model.predict([Use_a])
        context['Use_a']=prediction1
        if prediction1==0:
            context['Use_a']='NO'

        elif prediction1==1:
            context['Use_a']='YES'
        


        loaded_model = joblib.load('Ml_part/Check_your_writing_for_errors.pkl')

        Check_your = question + ' ' + answer

        prediction1 = loaded_model.predict([Check_your])

        context['Check_your'] = 'YES' if prediction1 == 1 else 'NO'
        

        loaded_model = joblib.load('Ml_part/Task_score.joblib')
        new_input = question + ' ' + answer

        loaded_vectorizer = joblib.load('Ml_part/Task_score_tfidf_vectorizer.joblib')
        new_input_tfidf = loaded_vectorizer.transform([new_input])
        Task_mark = loaded_model.predict(new_input_tfidf)
        rounded_Task_mark = math.ceil(Task_mark * 2) / 2
        context['Task_mark'] = rounded_Task_mark
        
        loaded_model = joblib.load('Ml_part/Answer_all_parts_of_the_question.pkl')

        Present = question + ' ' + answer

        prediction1 = loaded_model.predict([Present])

        context['Answer_all'] = 'YES' if prediction1 == 1 else 'NO'


        loaded_model = joblib.load('Ml_part/Present_relevant_ideas.pkl')

        Present = question + ' ' + answer

        prediction1 = loaded_model.predict([Present])

        context['Present'] = 'YES' if prediction1 == 1 else 'NO'









        loaded_model = joblib.load('Ml_part/Fully_explain_these_ideas.pkl')

        Present = question + ' ' + answer

        prediction1 = loaded_model.predict([Present])

        context['Fully'] = 'YES' if prediction1 == 1 else 'NO'

        
        loaded_model = joblib.load('Ml_part/specific_examples.pkl')

        Present = question + ' ' + answer

        prediction1 = loaded_model.predict([Present])

        context['specific_examples'] = 'YES' if prediction1 == 1 else 'NO'











        # Add the predicted mark to the context
        context['predicted_mark'] = rounded_mark
        insert=History(
             uid=user.id,
             question=question,
             answer=answer,
             marks=rounded_mark

        )
        insert.save()



    return render(request, 'home.html', context)

def Logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

def Profile(request):
    if request.user.is_authenticated:
        user = request.user
        data = History.objects.filter(uid=user.id)  
        context = {'user': user, 'data': data}
        return render(request, 'profile.html', context)
    else:
        return redirect('/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Your profile was successfully updated!')
        return redirect('profile')
    else:
        return redirect('/')
    

def Historys(request):
    if request.user.is_authenticated:
        user = request.user
        data = History.objects.filter(uid=user.id)  
        context = {'user': user, 'data': data}
        return render(request, 'history.html', context)
    else:
        return redirect('/')


def Index(request):
    return render(request, 'index.html')


    






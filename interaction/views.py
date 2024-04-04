# views.py
from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Complaint

# In your Django view function where you handle audio recordings
from django.http import JsonResponse
import speech_recognition as sr

class AudioTranscription(models.Model):
    text = models.TextField()


def index(request):
    return render(request, 'index.html')

def process_complaint_text(request):
    print(request.POST)
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint_text', '')
        if complaint_text:
            # Save the text complaint to the database
            Complaint.objects.create(text=complaint_text)
            return HttpResponse('Complaint text submitted successfully!')
        else:
            return HttpResponse('Text complaint is empty!')
    else:
        return HttpResponse('Invalid request method!')

@csrf_exempt
def process_complaint_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')  # Assuming audio is sent as a file
        if audio_file:
            # Initialize speech recognition
            recognizer = sr.Recognizer()

            # Process audio file
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            # Convert audio to text
            try:
                transcription = recognizer.recognize_google(audio_data)
                # Save text transcription to database
                AudioTranscription.objects.create(text=transcription)
                return JsonResponse({'status': 'success', 'message': 'Audio transcription saved successfully'})
            except sr.UnknownValueError:
                return JsonResponse({'status': 'error', 'message': 'Could not understand audio'})
            except sr.RequestError as e:
                return JsonResponse({'status': 'error', 'message': f"Could not request results: {e}"})
        else:
            return JsonResponse({'status': 'error', 'message': 'Audio file not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

import speech_recognition as sr
import webbrowser
import time

r = sr.Recognizer()
text = ""
sr.Microphone.list_microphone_names()
with sr.Microphone(sample_rate=48000) as source:
    r.adjust_for_ambient_noise(source, duration = 1)
    r.energy_threshold = 50
    while text != "exit":
        print("Speak Anything :")
        #audio = r.listen(source)
        audio = r.record(source, duration = 1)
        try:
            text = r.recognize_google(audio)
            print("You said : {}".format(text))
        except:
            print("Sorry could not recognize what you said")

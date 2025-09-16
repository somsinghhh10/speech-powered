import pyttsx3
import wikipedia
import speech_recognition as sr

def speak(text):
    """Speak the given text using pyttsx3"""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to the microphone and return recognized text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
        speak("Sorry, I could not understand your speech.")
        return ""
    except sr.RequestError:
        print("Speech Recognition service is down")
        speak("Speech Recognition service is down")
        return ""

def search_and_speak(query):
    """Search Wikipedia and speak the first 2 sentences"""
    if query.startswith("search "):
        query = query[7:]
    try:
        result = wikipedia.summary(query, sentences=2)
        print("Result:\n", result)
        speak(result)
    except wikipedia.exceptions.DisambiguationError as e:
        print("Your query is ambiguous. Options:", e.options[:5])
        speak("Your query is ambiguous. Please be more specific.")
    except wikipedia.exceptions.PageError:
        print("No page found for:", query)
        speak("I could not find anything about " + query)

if __name__ == "__main__":
    speak("Hello! I am your assistant. Say exit anytime to quit.")
    while True:
        command = listen()
        if command:
            if "exit" in command:
                speak("Goodbye!")
                break
            elif "search" in command:
                search_and_speak(command)
            else:
                speak("Please say a command starting with search or say exit to quit.")

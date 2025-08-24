import speech_recognition as sr
import webbrowser

def listen_and_search():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Listening... Say 'search' followed by your query or say 'exit' to quit.")
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")

                if command.lower() == "exit":
                    print("Exiting... Goodbye!")
                    break

                if command.lower().startswith("search"):
                    query = command[7:]  
                    if query:
                        print(f"Searching for: {query}")
                        webbrowser.open(f"https://www.google.com/search?q={query}")
                    else:
                        print("Please specify what to search for.")
                else:
                    print("Command not recognized. Please start with 'search' or say 'exit' to quit.")
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

listen_and_search()

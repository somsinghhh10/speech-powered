import re
import time
import speech_recognition as sr
import pyttsx3

NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALE_WORDS = {"hundred": 100, "thousand": 1000, "million": 1000000}

def words_to_number(tokens):
    total = 0
    current = 0
    for t in tokens:
        if t in NUM_WORDS:
            current += NUM_WORDS[t]
        elif t in SCALE_WORDS:
            if current == 0:
                current = 1
            current *= SCALE_WORDS[t]
            total += current
            current = 0
        elif re.match(r"\d+(\.\d+)?", t):
            current += float(t) if '.' in t else int(t)
        else:
            break
    total += current
    return total

def extract_numbers_from_text(text):
    digit_matches = re.findall(r"[-+]?\d*\.?\d+", text)
    if digit_matches and any(m.strip() != "" for m in digit_matches):
        nums = []
        for m in digit_matches:
            if m.strip() == "":
                continue
            if '.' in m:
                nums.append(float(m))
            else:
                nums.append(int(m))
        return nums
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    if not tokens:
        return []
    groups = []
    current = []
    for tok in tokens:
        if tok in NUM_WORDS or tok in SCALE_WORDS:
            current.append(tok)
        else:
            if current:
                groups.append(current)
                current = []
    if current:
        groups.append(current)
    nums = []
    for g in groups:
        nums.append(words_to_number(g))
    return nums

def handle_math_command(text):
    t = text.lower()
    nums = extract_numbers_from_text(t)
    if t.startswith("add") or " plus " in t or "add " in t:
        if len(nums) >= 2:
            result = sum(nums)
            return f"{nums} -> {result}", result
        elif len(nums) == 1 and '+' in t:
            try:
                expr = re.search(r"add\s+(.+)", t)
                if expr:
                    val = eval_expr(expr.group(1))
                    return f"{expr.group(1)} -> {val}", val
            except Exception:
                pass
        return None, None
    if "subtract" in t or "minus" in t:
        m = re.search(r"subtract\s+(.+)\s+from\s+(.+)", t)
        if m:
            a_text, b_text = m.group(1), m.group(2)
            a = extract_numbers_from_text(a_text)
            b = extract_numbers_from_text(b_text)
            if a and b:
                result = b[0] - a[0]
                return f"{b[0]} - {a[0]} = {result}", result
        if len(nums) >= 2:
            result = nums[0] - nums[1]
            return f"{nums[0]} - {nums[1]} = {result}", result
        return None, None
    if "multiply" in t or "times" in t or "x " in t:
        m = re.search(r"(multiply|times)\s+(.+)\s+by\s+(.+)", t)
        if m:
            a_text, b_text = m.group(2), m.group(3)
            a = extract_numbers_from_text(a_text)
            b = extract_numbers_from_text(b_text)
            if a and b:
                result = a[0] * b[0]
                return f"{a[0]} * {b[0]} = {result}", result
        if len(nums) >= 2:
            result = nums[0] * nums[1]
            return f"{nums[0]} * {nums[1]} = {result}", result
        return None, None
    if "divide" in t or "over" in t or " by " in t:
        m = re.search(r"(divide)\s+(.+)\s+by\s+(.+)", t)
        if m:
            a_text, b_text = m.group(2), m.group(3)
            a = extract_numbers_from_text(a_text)
            b = extract_numbers_from_text(b_text)
            if a and b:
                if b[0] == 0:
                    return f"Cannot divide by zero", None
                result = a[0] / b[0]
                return f"{a[0]} / {b[0]} = {result}", result
        if len(nums) >= 2:
            if nums[1] == 0:
                return "Cannot divide by zero", None
            result = nums[0] / nums[1]
            return f"{nums[0]} / {nums[1]} = {result}", result
        return None, None
    m = re.search(r"what is (.+)", t)
    if m:
        expr = m.group(1)
        if "plus" in expr or "add" in expr:
            nums = extract_numbers_from_text(expr)
            if len(nums) >= 2:
                return f"{nums[0]} + {nums[1]} = {nums[0] + nums[1]}", nums[0] + nums[1]
        if "minus" in expr or "subtract" in expr:
            nums = extract_numbers_from_text(expr)
            if len(nums) >= 2:
                return f"{nums[0]} - {nums[1]} = {nums[0] - nums[1]}", nums[0] - nums[1]
        if "times" in expr or "multiply" in expr or "x" in expr:
            nums = extract_numbers_from_text(expr)
            if len(nums) >= 2:
                return f"{nums[0]} * {nums[1]} = {nums[0] * nums[1]}", nums[0] * nums[1]
        if "divide" in expr or "over" in expr:
            nums = extract_numbers_from_text(expr)
            if len(nums) >= 2:
                if nums[1] == 0:
                    return "Cannot divide by zero", None
                return f"{nums[0]} / {nums[1]} = {nums[0] / nums[1]}", nums[0] / nums[1]
    return None, None

def eval_expr(expr):
    if not re.fullmatch(r"[0-9\.\+\-\*\/\s\(\)]+", expr):
        raise ValueError("Unsafe expression")
    return eval(expr)

recognizer = sr.Recognizer()
tts = pyttsx3.init()
tts.setProperty("rate", 160)
voices = tts.getProperty("voices")


for voice in voices:
    if "zira" in voice.name.lower(): 
        tts.setProperty("voice", voice.id)
        break

WAKE_WORD = "calculator"
SHUTDOWN_CMD = "calculator shutdown"

def speak(text):
    print("SAY:", text)
    try:
        tts.say(text)
        tts.runAndWait()
    except Exception as e:
        print("TTS error:", e)

def recognize_from_mic(timeout=None, phrase_time_limit=None):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.7)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return None
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print("Speech recognition request failed:", e)
        return None

def main_loop():
    active = False
    print("Voice calculator ready. Say 'Calculator' to activate.")
    speak("Voice calculator ready. Say calculator to activate.")
    try:
        while True:
            if not active:
                heard = recognize_from_mic(timeout=3, phrase_time_limit=3)
                if heard:
                    print("Heard (standby):", heard)
                    if WAKE_WORD in heard.lower().split():
                        active = True
                        speak("Calculator activated. Listening for math commands.")
                        print("Activated")
                    else:
                        pass
            else:
                heard = recognize_from_mic(timeout=5, phrase_time_limit=6)
                if not heard:
                    continue
                heard_l = heard.lower().strip()
                print("Heard (active):", heard_l)
                if heard_l == SHUTDOWN_CMD or heard_l == "shutdown" or heard_l == "calculator shut down":
                    active = False
                    speak("Calculator deactivated. Say calculator to reactivate.")
                    print("Deactivated")
                    continue
                message, result = handle_math_command(heard_l)
                if message is None:
                    print("Not a math command or couldn't parse numbers. Ignoring.")
                    continue
                else:
                    if result is None:
                        speak(str(message))
                    else:
                        if isinstance(result, float) and result.is_integer():
                            result = int(result)
                        speak(message)
    except KeyboardInterrupt:
        print("\nExiting.")
        speak("Goodbye")

if __name__ == "__main__":
    main_loop()

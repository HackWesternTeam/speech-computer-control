import time
import re
import sys
import os
import webbrowser
import keyboard
import mouse
import pyaudio

credential_path = r"C:\Users\Simon\Desktop\python1\voice-python-cf6446c5f010.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import enums
from six.moves import queue
# Audio recording parameters
STREAMING_LIMIT = 10000
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):

        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round((self.final_request_end_time -
                                            self.bridging_offset) / chunk_time)

                    self.bridging_offset = (round((
                        len(self.last_audio_input) - chunks_from_ms)
                                                  * chunk_time))

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b''.join(data)
def volume_output(num):
    mouse.move(1360, 900, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')
    scale = 1242 + ((1472 - 1242)/100)*num
    time.sleep(0.5)
    mouse.move(scale, 797, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')
    time.sleep(0.05)
    mouse.move(1360, 900, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')

def keyboard_up():
    for i in range(0,15):
        keyboard.press_and_release('up')
def keyboard_down():
    for i in range(0,15):
        keyboard.press_and_release('down')
def move_mouse(direction, num):
    if direction == "r":
        mouse.move(25*num, 0, absolute=False, duration=0)
    elif direction == "l":
        mouse.move(-25*num, 0, absolute=False, duration=0)
    elif direction == "u":
        mouse.move(0, -25*num, absolute=False, duration=0)
    elif direction == "d":
        mouse.move(0, 25*num, absolute=False, duration=0)


def processInput(transcript):
    parse = transcript.replace(" ","").lower()
    if "reopen" in parse:
        keyboard.press_and_release("ctrl+shift+t")
    elif "setvolumeto" in parse:
        word = parse[parse.find("setvolumeto")+len("setvolumeto"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            volume_output(number)
    elif "clear" in parse:
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.05)
        keyboard.press_and_release("backspace")
    elif "back" in parse:
        keyboard.press_and_release("alt+left")
    elif "forward" in parse:
        keyboard.press_and_release("alt+right")
    elif "switch" in parse:
        keyboard.press_and_release("alt+tab")
    elif "type" in parse:
        send_message = transcript[transcript.lower().find("type ")+len("type "):]
        keyboard.write(send_message)
    elif "open" in parse:
        parse = parse[parse.lower().find("open")+len("open"):]
        test = "www." + parse + ".com"
        webbrowser.open(test)
    elif "closetab" in parse:
        num_tab = parse[parse.find("closetab")+len("closetab"):]
        close_tab = "ctrl+" + num_tab
        try:
            keyboard.press_and_release(close_tab)
            time.sleep(0.05)
            keyboard.press_and_release('ctrl+w')
        except:
            print("Not Recognized")
    elif "searchyoutubefor" in parse:
        query = parse[parse.find("youtubefor")+len("youtubefor"):]
        webbrowser.open("http://www.youtube.com/results?search_query="+query)
    elif "searchgooglefor" in parse:
        query = parse[parse.find("googlefor")+len("googlefor"):]
        webbrowser.open("https://www.google.com/search?q="+query)
    elif "scrollup" in parse:
        keyboard_up()
    elif "scrolldown" in parse:
        keyboard_down()
    elif "gototab" in parse:
        num_tab = parse[parse.find("gototab")+len("gototab"):]
        go_to_tab = "ctrl+" + num_tab
        try:
            keyboard.press_and_release(go_to_tab)
        except:
            print("Not Recognized")
    elif "send" in parse:
        send_message = transcript[transcript.lower().find("send ")+len("send "):]
        keyboard.write(send_message)
        time.sleep(0.05)
        keyboard.press_and_release("enter")
    elif "click" in parse:
        mouse.click(button='left')
    elif "copy" in parse:
        mouse.click(button='left')
        time.sleep(0.05)
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.05)
        keyboard.press_and_release("ctrl+c")
    elif "paste" in parse:
        mouse.click(button='left')
        time.sleep(0.05)
        keyboard.press_and_release("ctrl+v")
    elif "r" in parse:
        word = parse[parse.find("r")+len("r"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            move_mouse("r",number)
    elif "l" in parse:
        word = parse[parse.find("l")+len("l"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            move_mouse("l",number)
    elif "u" in parse:
        word = parse[parse.find("u")+len("u"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            move_mouse("u",number)
    elif "d" in parse:
        word = parse[parse.find("d")+len("d"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            move_mouse("d",number)
    


def listen_print_loop(responses, stream):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    for response in responses:

        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_nanos = 0
        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.nanos:
            result_nanos = result.result_end_time.nanos

        stream.result_end_time = int((result_seconds * 1000)
                                     + (result_nanos / 1000000))
        corrected_time = (stream.result_end_time - stream.bridging_offset
                          + (STREAMING_LIMIT * stream.restart_counter))
        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.

        if result.is_final:

            sys.stdout.write(GREEN)
            sys.stdout.write('\033[K')
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\n')

            processInput(transcript)

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                sys.stdout.write(YELLOW)
                sys.stdout.write('Exiting...\n')
                stream.closed = True
                break


        else:
            sys.stdout.write(RED)
            sys.stdout.write('\033[K')
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\r')
            stream.last_transcript_was_final = False


def main():
    client = speech.SpeechClient()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code='en-US',
        speech_contexts=[speech.types.SpeechContext(
        phrases=["click", "close tab", "copy", "clear","paste","go to tab", "scroll up", "scroll down", "back","switch","forward","u1","u2","u3","u4","u5","u6","u7","u8","u9","u10","l1","l2","l3","l4","l5","l6","l7","l8","l9","l10","d1","d2","d3","d4","d5","d6","d7","d8","d9","d10",
"r1","r2","r3","r4","r5","r6","r7","r8","r9","r10", "set volume to"])],
        max_alternatives=1)
    streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
    print(mic_manager.chunk_size)
    sys.stdout.write(YELLOW)
    sys.stdout.write('\nListening, say "Quit" or "Exit" to stop.\n\n')
    sys.stdout.write('End (ms)       Transcript Results/Status\n')
    sys.stdout.write('=====================================================\n')

    with mic_manager as stream:

        while not stream.closed:
            sys.stdout.write(YELLOW)
            sys.stdout.write('\n' + str(
                STREAMING_LIMIT * stream.restart_counter) + ': NEW REQUEST\n')

            stream.audio_input = []
            audio_generator = stream.generator()

            requests = (speech.types.StreamingRecognizeRequest(
                audio_content=content)for content in audio_generator)

            responses = client.streaming_recognize(streaming_config,
                                                   requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses, stream)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write('\n')
            stream.new_stream = True


if __name__ == '__main__':
    main()

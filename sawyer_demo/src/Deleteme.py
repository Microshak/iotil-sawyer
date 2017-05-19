import speech_recognition as sr
r = sr.Recognizer()
m = sr.Microphone()
#set threhold level
with m as source: r.adjust_for_ambient_noise(source)
print "Set minimum energy threshold to {}".format(r.energy_threshold)
# obtain audio from the microphone

with sr.Microphone() as source:
    print "Say something!"
    audio = r.listen(source)


# recognize speech using Microsoft Bing Voice Recognition
BING_KEY = "4b1323765f834841b16daee7894783c3"  
print r.recognize_sphinx(audio)

#try:
print "Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=BING_KEY)
#except sr.UnknownValueError:
#    print "Microsoft Bing Voice Recognition could not understand audio"
#except sr.RequestError as e:
#    print "Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e)

#print 'e'
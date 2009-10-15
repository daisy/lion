echo building executable
call c:\python25\python setup.py py2exe

echo copying files to the dist directory
copy pronunciation.txt dist\pronunciation.txt
copy prompts.html  dist\prompts.html
copy sapi2wav.exe dist\sapi2wav.exe

echo Zip up the dist directory and distribute!  users may replace prompts.html and edit pronunciation.txt

rem uncomment to test
rem cd dist
rem call lion_audio_helper.exe
rem cd ../
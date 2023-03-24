./yas-lock.exe --window 云·原神 --speed 5 --default-stop 100
cp good.json artifacts-Filter/good.json
# #rm -r artifacts-Filter/config/expend_build.pkl
python artifacts-Filter/main.py
cp artifacts-Filter/result/lock.json lock.json
# #cp artifacts-Filter/result/now_lock.json lock.json
./yas-lock.exe --window 云·原神 --speed 5 --default-stop 100

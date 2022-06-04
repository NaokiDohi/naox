# TCP Server

## Description

You can get server_recv.txt which includes HTTP Headers when you run tcpserver.py and send request from chrome.

X  →aiueo→ Y

あるデータをインターネットで送り出す時、データは細切れのパケットという単位に分割され、ばらばらに配送されます。</br>

TCPではこの完全性と順序性（=漏れなく順序良く）を担保するために、データを送る側はパケットに番号を割り振って、データを受け取る側はパケットを受け取るたびに受け取った番号を返事する、という協調動作を行います。</br>

例）</br>
マシンX: 1:あ 2:い 3:う 4:え 5(最後):お を送るよ！</br>
マシンY: 1を受け取ったよ！ 2を受け取ったよ！ 5(最後)を受け取ったよ！ 3と4が届いてないか<ら、もう一度おくってくれる？</br>
マシンX: 3:う 4:え を送るよ！</br>
マシンY: 3を受け取ったよ！ 4を受け取ったよ!</br>
~ Fin ~</br>

漏れなく順序よく送らないプロトコルのことを UDP(User Datagram Protocol) と呼ぶ。動画ストリーミングで使用される。
あいえおや、えあういおと届く可能性があります

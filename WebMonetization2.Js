# testnet
moneyd xrp:start --testnet
# local network
moneyd local

http GET ilpsurvey.localtunnel.me/23a9c6ea-c5ee-4f68-83e4-ef1360c8f2f2 Accept:"application/spsp4+json"
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 386
Content-Type: application/spsp4+json
Date: Thu, 10 Jan 2019 22:44:59 GMT
Server: nginx/1.10.1
{
  "destination_account": "private.moneyd.local.zQqGsK6bg6q4J1TL00XvAdyL8v93VurOWLpnMgSzNb8.63swBEGQNvnn52vMRvBq-uag~23a9c6ea-c5ee-4f68-83e4-ef1360c8f2f2",
  "shared_secret": "dXGYytLMt8xCFh3a7tpfSbgmRuol4Y5ZHgVdrXGj67U="
  "balance": {
    "available": "0",
    "current": "0",
    "maximum": "28000000"
  },
  "receiver_info": {
    "name": "My Sample Survey"
  }
}


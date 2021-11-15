import asyncio
import websockets
import json
import datetime
import uuid
import os

#Numero de clientes conectados!!!

mensagens = []
connected = set()


usersonline = []

def organizaclientid():
    ##nao esta finalizado aqui
    ##preciso separar em um json somente os ids dos usuarios conectados e enviar isso separado
    clientsid = []
    #,"uuids":usersonline
    #print(usersonline)
    for i in usersonline:
        clientsid.append(i['id'])
    #print(clientsid)
    return clientsid

async def users_event():
    return json.dumps({"type": "users", "count": len(connected), "uuids": organizaclientid()})

def user_saiu(id_user_que_saiu):
    return json.dumps({"type": "user_saiu", "id":id_user_que_saiu})
    
async def my_id(meuid):
    return json.dumps({"type": "my_id", "id":meuid})

async def conn2id(conn):
    print("&"*20)
    print(usersonline)
    print("&"*20)
    #return usersonline[conn]

async def server(websocket, path):
    global mensagens,usersonline
    # Register.
    
    print("adding")
    temp = dict()
    ultimouserconectado = set()
    
    temp['id'] = str(uuid.uuid4())
    temp['time_conected'] = datetime.datetime.utcnow().isoformat() + "Z"
    temp['conection'] = websocket
    temp[str(websocket)] = temp['id']
    usersonline.append(temp)
    connected.add(websocket)
    ultimouserconectado.add(websocket)
    #print("esse cara conectou "+str(ultimouserconectado))
    #await websocket.send("seu id aqui")
    #print("co ======= "+str(connected))
    #print("usuagora ======= "+str(ultimouserconectado))
    websockets.broadcast(ultimouserconectado,await my_id(temp['id']))
    websockets.broadcast(connected, await users_event())
    #print(temp['id'])
    try:
        async for message in websocket:
            msss = json.loads(message)

            if msss['type'] == "msg-post":
                mensagens.append(msss)
                print(msss)
                for conn in connected:
                    #print(help(conn))
                    if conn != websocket:
                        #conn2id(conn)
                        #print(f"enviando para o {conn2id(conn)}")
                        await conn.send(str(msss))
                    else:
                        
                        print(f"Dar retorno")
            elif msss['type'] == "erro":
                print("some error ocorreu")
            elif msss['type'] == "autentificacao":
                print(msss)
                print(f"seu username para o servidor == {msss['token']}")
            else:
                print("typo nao suportado")
                print(msss)
                        
    finally:
        # Unregister.
        for index,user in enumerate(usersonline):
            if user['conection'] == websocket:
                print(f"{user['id']} saiu ...")
                usersonline.pop(index)
                print(f"Restam apenas {len(usersonline)} conectados")
                websockets.broadcast(connected, user_saiu(user['id']))
                
                
        print("Conneccao interrompida")
        connected.remove(websocket)
    

start_server = websockets.serve(server, host="",port=int(os.environ["PORT"]))
print("Running...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

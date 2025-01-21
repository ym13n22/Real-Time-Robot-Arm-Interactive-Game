using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using PimDeWitte.UnityMainThreadDispatcher;

public class SocketClient : MonoBehaviour
{
   
    private TcpListener server;
    private Thread serverThread;

    private armmove armm;

    private handMove handmove;

    private baseMove basemove;

    private fingerMove fingermove;

    private forearmMove forearMove;

    private catchedBall catchBall;

   

    void Start()
    {
     armm = FindObjectOfType<armmove>();
        if (armm == null)
        {
            Debug.LogError("armmove component not found in the scene.");
            return;
        }
    basemove = FindObjectOfType<baseMove>();
        if (basemove == null)
        {
            Debug.LogError("baseMove component not found in the scene.");
            return;
        }
    handmove =FindObjectOfType<handMove>();
         if (handmove == null)
        {
            Debug.LogError("handMove component not found in the scene.");
            return;
        }
    fingermove =FindObjectOfType<fingerMove>();
        if (fingermove == null)
        {
            Debug.LogError("fingerMove component not found in the scene.");
            return;
        }
    forearMove=FindObjectOfType<forearmMove>();
        if (forearMove == null)
        {
            Debug.LogError("forearMove component not found in the scene.");
            return;
        }
    catchBall=FindObjectOfType<catchedBall>();
        if (catchBall == null)
        {
            Debug.LogError("catchBall component not found in the scene.");
            return;
        }

        serverThread = new Thread(new ThreadStart(StartServer));
        serverThread.IsBackground = true;
        serverThread.Start();
    }

    void StartServer()
{
    server = new TcpListener(IPAddress.Parse("127.0.0.1"), 65432);
    server.Start();
    Debug.Log("Server started");

    try
    {
        while (true)
        {
            TcpClient client = server.AcceptTcpClient();
            
            // Use ThreadPool to handle each client connection
            ThreadPool.QueueUserWorkItem(HandleClient, client);
        }
    }
    catch (SocketException e)
    {
        Debug.Log("SocketException: " + e);
    }
    finally
    {
        server.Stop();
    }
}

void HandleClient(object obj)
{
    TcpClient client = (TcpClient)obj;
    
    
    using (NetworkStream stream = client.GetStream())
    {
        byte[] buffer = new byte[1024];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string receivedCommand = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        //Debug.Log("Received command: " + receivedCommand);

        // Send a response back to the Python client
        byte[] response = Encoding.UTF8.GetBytes("Command received "+receivedCommand);
        stream.Write(response, 0, response.Length);
      //  Debug.Log("FeedBack Seccessfully");
        string[] command = receivedCommand.Split(':');
       // Debug.Log("command[0] "+command[0]);
        if(command[0]=="Command"){
         //    Debug.Log("is in command ");
        }
        if(command[0]=="Command "){
          //  Debug.Log("is in command");
            string[] commands = command[1].Split(' ');
            if(commands.Length>1){
              //  Debug.Log("into split "+commands[1]);
                if(commands[1]=="down"){
                float rotateAngle;
                if(float.TryParse(commands[2],out rotateAngle)){
                 //   Debug.Log("rotationAngle is"+ rotateAngle);
                     UnityMainThreadDispatcher.Instance().Enqueue(() => armm.rotateArmZ(rotateAngle));
                        //Debug.Log("down");
                }
                }
                if(commands[1]=="up"){
                float rotateAngle;
                if(float.TryParse(commands[2],out rotateAngle)){
                 //   Debug.Log("rotationAngle is"+ rotateAngle);
                     UnityMainThreadDispatcher.Instance().Enqueue(() => armm.armmoveUp(rotateAngle));
                        //Debug.Log("up");
                }
                }
                if(commands[1]=="roll"){
                float rotateAngle;
                if(float.TryParse(commands[2],out rotateAngle)){
                   // Debug.Log("rotationAngle is"+ rotateAngle);
                     UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.rotateY(rotateAngle));
                        //Debug.Log("down");
                }
                }
                if(commands[1]=="back"){
                float rotateAngle;
                if(float.TryParse(commands[2],out rotateAngle)){
                  //  Debug.Log("rotationAngle is"+ rotateAngle);
                     UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.baseRollBack(rotateAngle));
                        //Debug.Log("down");
                }
                }
               
                
               
            }
            if(command[1]==" roll"){
            UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.rotateY(0));
            Debug.Log("roll");
            }
            if(command[1]==" up"){
            Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => armm.armmoveUp(45));
            Debug.Log("armmoveUp");
            }
            if(command[1]==" back"){
            Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.baseRollBack(0));
            Debug.Log("rollBack");
            }
        }
        if(command[0]=="Hand "){
            if (command[1]=="Hand Close"){
               // if(checkCatchable()==true){
                   UnityMainThreadDispatcher.Instance().Enqueue(() => fingermove.moveAction());
              //  }
            
            }
            if (command[1]=="Hand Open"){
              //  if(checkCatchable()==true){
                  UnityMainThreadDispatcher.Instance().Enqueue(() => fingermove.returnTogether());
              //  }
            
            }
        }
        if(receivedCommand=="d pressed"){
            Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => armm.rotateArmZ(45));
            Debug.Log("rotateArmZ");
        }
        if(receivedCommand=="u pressed"){
            Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => armm.armmoveUp(45));
            Debug.Log("armmoveUp");
        }
         if(receivedCommand=="r pressed"){
               Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.rotateY(0));
            Debug.Log("rotateArmZ");
        }
        if(receivedCommand=="b pressed"){
               Debug.Log("command received");
            UnityMainThreadDispatcher.Instance().Enqueue(() => basemove.baseRollBack(0));
            Debug.Log("rotateArmZ");
        }

    }

    client.Close();
}

    void OnApplicationQuit()
    {
        if (serverThread != null)
        {
            serverThread.Abort();
        }

        if (server != null)
        {
            server.Stop();
        }
    }
}



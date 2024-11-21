// See https://aka.ms/new-console-template for more information
using InTheHand.Net.Bluetooth;
using InTheHand.Net.Sockets;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;

var fromBoat = new BlockingCollection<byte>();
var toBoat = new BlockingCollection<byte>();
var name = args.Length > 0 ? args[0] : "Yngves";
var port = args.Length > 1 ? int.Parse(args[1]) : 10110;
var btTask = Task.Run(bt);
var tcpTask = Task.Run(tcp);

Task.WaitAll(btTask, tcpTask);
//Console.WriteLine("Hello, World!");
void bt()
{
    Console.WriteLine("bt!");
    BluetoothClient client = new();
    var device = client.DiscoverDevices()
        .First(d => d.DeviceName == name);
    client.Connect(device.DeviceAddress, BluetoothService.SerialPort);
    var btStream = client.GetStream();
    var readTask = Task.Run(() =>
    {
        var buf = new byte[1024];
        while (btStream.CanRead)
        {
            var b = (byte)btStream.ReadByte();
            fromBoat.Add(b);
        }
    }
);
    var writeTask = Task.Run(() =>
    {
        while (true)
        {
            var b = toBoat.Take();
            btStream.WriteByte(b);
            Console.Write(Convert.ToChar(b));
        }
    }
    );
    Task.WaitAll(readTask, writeTask);

}

void tcp()
{
    Console.WriteLine("tcp!");

    TcpListener server = new TcpListener(IPAddress.Any, port);
    server.Start();
    Console.WriteLine("Server started...");

    while (true)
    {
        TcpClient client = server.AcceptTcpClient();
        Console.WriteLine("Client connected!");
        NetworkStream tcpStream = client.GetStream();
        var readTask = Task.Run(() =>
        {
            while (true)
            {
                var b = fromBoat.Take();
                tcpStream.WriteByte(b);
            }
        }
        );
        var writeTask = Task.Run(() =>
        {
            while (true)
            {
                var b = tcpStream.ReadByte();
                toBoat.Add((byte)b);
            }
        }
        ); 
        Task.WaitAll(readTask, writeTask);
        client.Close();
    }
}
Console.ReadKey();
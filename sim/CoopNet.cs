// Two players in one process (co-op readiness, Phase 6 groundwork). The host's game runs here as the host; the
// second seat is a client that does not exist as a process. This service stands in for the network: the game registers
// its message handlers with it, messages the host sends are kept in an outbox (nobody receives them), and the second
// seat's actions can be delivered to the registered handlers as if a client had sent them (Deliver), the way the game's
// own replay service feeds recorded messages. Nothing leaves the process.
using MegaCrit.Sts2.Core.Multiplayer;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;

public sealed class InProcessHostService : INetHostGameService
{
    readonly Dictionary<Type, List<Delegate>> _handlers = new();
    public readonly List<(string Type, ulong? To)> Outbox = new();
    readonly List<object> _sentMessages = new();

    public ulong NetId { get; set; } = 1;
    public bool IsConnected => true;
    public bool IsGameLoading { get; private set; }
    public NetGameType Type => NetGameType.Host;
    public MegaCrit.Sts2.Core.Platform.PlatformType Platform => MegaCrit.Sts2.Core.Platform.PlatformType.None;
    public PeerVersionInfo LocalVersion => default;
    public event Action<MegaCrit.Sts2.Core.Entities.Multiplayer.NetErrorInfo> Disconnected { add { } remove { } }

    public void SendMessage<T>(T message, ulong playerId) where T : INetMessage { Outbox.Add((typeof(T).Name, playerId)); _sentMessages.Add(message); }
    public void SendMessage<T>(T message) where T : INetMessage { Outbox.Add((typeof(T).Name, null)); _sentMessages.Add(message); }

    public void RegisterMessageHandler<T>(MessageHandlerDelegate<T> handler) where T : INetMessage
    {
        if (!_handlers.TryGetValue(typeof(T), out var list)) _handlers[typeof(T)] = list = new List<Delegate>();
        list.Add(handler);
    }

    public void UnregisterMessageHandler<T>(MessageHandlerDelegate<T> handler) where T : INetMessage
    {
        if (_handlers.TryGetValue(typeof(T), out var list)) list.Remove(handler);
    }

    // A message from the second seat, delivered to every handler the game registered for its type.
    public int Deliver<T>(T message, ulong fromPlayer) where T : INetMessage
    {
        if (!_handlers.TryGetValue(typeof(T), out var list)) return 0;
        foreach (var h in list.ToList()) ((MessageHandlerDelegate<T>)h)(message, fromPlayer);
        return list.Count;
    }

    // The second seat acting like the host just did: a copy of the host's last message of that type, with some fields
    // changed (for example another option index), delivered as if the other seat had sent it. Returns handlers reached.
    public int DeliverLike(string typeName, IDictionary<string, object> fields, ulong fromPlayer)
    {
        var last = _sentMessages.LastOrDefault(m => m.GetType().Name == typeName)
                   ?? throw new InvalidOperationException($"the host has not sent a {typeName} yet");
        var copy = last.GetType().IsValueType ? last : System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(last.GetType());
        if (!last.GetType().IsValueType)
            foreach (var f in last.GetType().GetFields(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic))
                f.SetValue(copy, f.GetValue(last));
        foreach (var (name, value) in fields)
        {
            var f = copy.GetType().GetField(name) ?? throw new ArgumentException($"{typeName} has no field {name}");
            f.SetValue(copy, Convert.ChangeType(value, f.FieldType));
        }
        var deliver = typeof(InProcessHostService).GetMethod(nameof(Deliver))!.MakeGenericMethod(copy.GetType());
        return (int)deliver.Invoke(this, new[] { copy, (object)fromPlayer })!;
    }

    public IEnumerable<string> HandledTypes => _handlers.Where(kv => kv.Value.Count > 0).Select(kv => kv.Key.Name);

    public void Update() { }
    public void Disconnect(MegaCrit.Sts2.Core.Entities.Multiplayer.NetError reason, bool now) { }
    public MegaCrit.Sts2.Core.Multiplayer.Quality.ConnectionStats GetStatsForPeer(ulong peerId) => null;
    public void SetGameLoading(bool isLoading) => IsGameLoading = isLoading;
    public void SetBufferMessages(bool bufferMessages) { }
    public string GetRawLobbyIdentifier() => "in-process";

    // host side
    public MegaCrit.Sts2.Core.Multiplayer.Transport.NetHost NetHost => null;
    public event Action<ulong> ClientConnected { add { } remove { } }
    public event Action<ulong, MegaCrit.Sts2.Core.Entities.Multiplayer.NetErrorInfo> ClientDisconnected { add { } remove { } }
    public event Action<ulong, MegaCrit.Sts2.Core.Entities.Multiplayer.NetErrorInfo> ClientConnectionFailed { add { } remove { } }
    public void DisconnectClient(ulong peerId, MegaCrit.Sts2.Core.Entities.Multiplayer.NetError reason, bool now) { }
    public void SetPeerReadyForBroadcasting(ulong peerId) { }
    public PeerVersionInfo? GetVersionInfoForPeer(ulong peerId) => default(PeerVersionInfo);
}

// The lobby reports changes to its screen through this listener; the host has no lobby screen, so it ignores them.
public sealed class SilentLobbyListener : MegaCrit.Sts2.Core.Multiplayer.Game.Lobby.IStartRunLobbyListener
{
    public void PlayerConnected(MegaCrit.Sts2.Core.Entities.Multiplayer.StartRunLobbyPlayer player) { }
    public void PlayerChanged(MegaCrit.Sts2.Core.Entities.Multiplayer.StartRunLobbyPlayer player, bool isRandomCharacterResolution) { }
    public void AscensionChanged() { }
    public void SeedChanged() { }
    public void ModifiersChanged() { }
    public void MaxAscensionChanged() { }
    public void RemotePlayerDisconnected(MegaCrit.Sts2.Core.Entities.Multiplayer.StartRunLobbyPlayer player) { }
    public void BeginRun(string seed, List<MegaCrit.Sts2.Core.Models.ActModel> acts, IReadOnlyList<MegaCrit.Sts2.Core.Models.ModifierModel> modifiers) { }
    public void LocalPlayerDisconnected(MegaCrit.Sts2.Core.Entities.Multiplayer.NetErrorInfo info) { }
}

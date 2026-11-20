// Single-threaded scheduler for the game's async code (docs/simulator-integrity.md FI-8): every continuation the game
// posts runs on the host's one thread, in the order posted. Nothing runs on the thread pool.
public sealed class SimContext : SynchronizationContext
{
    readonly Queue<(SendOrPostCallback, object)> _queue = new();
    public long Posted;

    public override void Post(SendOrPostCallback d, object state) { lock (_queue) { _queue.Enqueue((d, state)); Posted++; } }
    public override void Send(SendOrPostCallback d, object state) => d(state);
    public override SynchronizationContext CreateCopy() => this;

    public bool PumpOne()
    {
        (SendOrPostCallback, object) item;
        lock (_queue) { if (_queue.Count == 0) return false; item = _queue.Dequeue(); }
        item.Item1(item.Item2);
        return true;
    }

    public int Drain() { var n = 0; while (PumpOne()) n++; return n; }

    // Runs queued work until the task completes. A task that cannot complete (it waits for an engine signal that never
    // comes) is reported instead of hanging.
    public void RunUntil(Task t, string what)
    {
        var idle = System.Diagnostics.Stopwatch.StartNew();
        while (!t.IsCompleted)
        {
            if (PumpOne()) { idle.Restart(); continue; }
            if (idle.ElapsedMilliseconds > 3000) throw new TimeoutException($"stuck: '{what}' is waiting for something that never completes (status {t.Status})");
            Thread.Yield();
        }
        t.GetAwaiter().GetResult();
    }
}

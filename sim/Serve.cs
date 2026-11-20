// JSON-lines server for tools/sim.py (P7.E4.S5). One request per line on stdin; one reply per line on stdout, prefixed
// with "@@" so it cannot be confused with anything the game prints. Errors come back as {"ok": false, "error": ...};
// the process keeps running (EN-5).
//
// Requests: {"cmd":"load","path":..} · {"cmd":"reset","events":k,"seed":n|null} · {"cmd":"observe"} · {"cmd":"legal"}
//           {"cmd":"step","action":{..}} · {"cmd":"hidden"} (tests only) · {"cmd":"rollout","policy":"first"|"random","seed":n,"max_steps":m}
//           {"cmd":"stats"} · {"cmd":"quit"}
using System.Text.Json;
using System.Text.Json.Nodes;

public static class Serve
{
    static void Reply(JsonObject o) { Console.Out.WriteLine("@@" + o.ToJsonString()); Console.Out.Flush(); }

    public static int Run(string[] args)
    {
        try { Stages.Boot(false); Choices.Install(); Host.InstallStubs(); } catch (Stages.StageFailed) { return 1; }
        if (!args.Contains("log")) Stubs.CaptureLog();
        var s = new Session();
        SynchronizationContext.SetSynchronizationContext(s.Ctx);
        var info = Path.Combine(Path.GetDirectoryName(Program.GameDir.TrimEnd('/'))!, "release_info.json");
        var build = File.Exists(info) ? JsonNode.Parse(File.ReadAllText(info)) : null;
        Reply(new JsonObject { ["ok"] = true, ["ready"] = true, ["game_version"] = (string)build?["version"], ["game_commit"] = (string)build?["commit"],
                               ["model_id_hash"] = MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash });
        string line;
        long steps = 0, resets = 0;
        while ((line = Console.In.ReadLine()) != null)
        {
            if (line.Trim().Length == 0) continue;
            var reply = new JsonObject { ["ok"] = true };
            try
            {
                var req = JsonNode.Parse(line)!;
                switch ((string)req["cmd"])
                {
                    case "load":
                        s.Load((string)req["path"]);
                        // FI-3: refuse a recording from another build or with another model list
                        if (s.Replay.modelIdHash != MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash)
                            throw new InvalidOperationException($"model-id hash differs: replay {s.Replay.modelIdHash}, host {MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash}");
                        if (build != null && s.Replay.gitCommit != (string)build["commit"])
                            throw new InvalidOperationException($"game build differs: replay {s.Replay.gitCommit}, installed {(string)build["commit"]}");
                        reply["events"] = s.Replay.events.Count;
                        reply["version"] = s.Replay.version;
                        reply["commit"] = s.Replay.gitCommit;
                        break;
                    case "points":
                        if (s.Run == null) s.Reset(0, null);
                        reply["decision_points"] = new JsonArray(s.DecisionPoints().Select(i => (JsonNode)i).ToArray());
                        break;
                    case "reset":
                        s.Reset((int)req["events"], req["seed"] == null ? null : (ulong)req["seed"]);
                        resets++;
                        reply["obs"] = s.Observe();
                        reply["generators_reseeded"] = req["seed"] == null ? 0 : Sanitizer.LastCount;
                        break;
                    case "new_fight":
                        s.NewFight(req["spec"]!, (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L));
                        resets++;
                        reply["obs"] = s.Observe();
                        reply["generators_reseeded"] = Sanitizer.LastCount;
                        break;
                    case "new_run":
                        s.NewRun(req["spec"]!, (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L));
                        resets++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "run_legal": reply["actions"] = s.RunLegal(); break;
                    case "run_step":
                        s.RunStep(req["action"]!);
                        s.AfterRewardTaken();
                        steps++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "run_observe": reply["obs"] = s.RunObserve(); break;
                    case "map": reply["map"] = s.MapView(); break;
                    case "debug_rng": reply["counters"] = s.DebugRngCounters(); break;   // fidelity tests only (FP-2)
                    case "move_to":
                        s.MoveTo((int)req["col"], (int)req["row"]);
                        steps++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "encounters":
                        reply["encounters"] = new JsonArray(MegaCrit.Sts2.Core.Models.ModelDb.AllEncounters
                            .Select(e => (JsonNode)new JsonObject { ["id"] = e.Id.Entry, ["room_type"] = e.RoomType.ToString(), ["weak"] = e.IsWeak }).ToArray());
                        break;
                    case "observe": reply["obs"] = s.Observe(); break;
                    case "legal": reply["actions"] = s.Legal(); break;
                    case "step":
                        s.Step(req["action"]!);
                        steps++;
                        reply["obs"] = s.Observe();
                        break;
                    case "hidden": reply["hidden"] = s.Hidden(); break;
                    case "selfcheck": reply["result"] = s.OwnActionsReplay(); break;
                    case "rollout":
                    {
                        var rng = new Random((int)(req["seed"] ?? 0));
                        var max = (int)(req["max_steps"] ?? 400);
                        var n = 0;
                        while (n < max && s.Status() == "in_progress" && !s.Blocked)
                        {
                            var acts = s.Legal();
                            if (acts.Count == 0) break;
                            var pick = (string)req["policy"] == "random" ? acts[rng.Next(acts.Count)]! : acts[0]!;
                            s.Step(pick);
                            n++; steps++;
                        }
                        reply["steps"] = n;
                        reply["obs"] = s.Observe();
                        break;
                    }
                    case "diag":
                        reply["problems"] = new JsonArray(Stubs.Problems.TakeLast((int)(req["last"] ?? 6)).Select(x => (JsonNode)x).ToArray());
                        reply["last_action"] = s.LastAction();
                        if (req["clear"] != null) Stubs.Problems.Clear();
                        break;
                    case "stats":
                        reply["steps"] = steps; reply["resets"] = resets; reply["engine_calls"] = Stubs.TotalCalls;
                        reply["managed_mb"] = GC.GetTotalMemory(false) / 1048576; reply["sanitize_ms"] = Sanitizer.LastMs;
                        break;
                    case "quit": Reply(reply); return 0;
                    default: throw new ArgumentException("unknown cmd");
                }
            }
            catch (Exception e)
            {
                var inner = e; while (inner.InnerException != null) inner = inner.InnerException;
                reply = new JsonObject { ["ok"] = false, ["error"] = inner.GetType().Name + ": " + inner.Message.Split('\n')[0],
                                         ["where"] = string.Join(" <- ", (inner.StackTrace ?? "").Split('\n').Take(4).Select(x => x.Trim())) };
            }
            Reply(reply);
        }
        return 0;
    }
}

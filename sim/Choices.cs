// Card choices in decision mode (P7.E4.S3). Cards such as Headbutt, Armaments or True Grit ask the player to pick
// cards. In the game that opens a selection screen; in a recorded fight the answer comes from the recording. In
// decision mode the host intercepts the selection commands, exposes the options, and waits for the policy's answer.
// The interception is off while recorded events are applied, so the past is replayed exactly as recorded.
using System.Reflection;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

public static class Choices
{
    public sealed class Pending
    {
        public List<CardModel> Options = new();
        public int Min, Max;
        public bool Single;
        public object Tcs;
        public string Kind = "";
    }

    public static bool Intercept;
    public static Pending Current;
    static bool _installed;

    public static void Install()
    {
        if (_installed) return;
        _installed = true;
        var prefix = new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(Prefix), BindingFlags.Static | BindingFlags.NonPublic));
        foreach (var name in new[] { "FromCombatPile", "FromHand", "FromHandForDiscard", "FromHandForUpgrade", "FromSimpleGrid", "FromChooseACardScreen" })
            foreach (var m in typeof(CardSelectCmd).GetMethods(BindingFlags.Static | BindingFlags.Public).Where(m => m.Name == name))
                Stubs.H.Patch(m, prefix: prefix);
    }

    static bool Prefix(MethodBase __originalMethod, object[] __args, ref object __result)
    {
        if (!Intercept) return true;
        var m = (MethodInfo)__originalMethod;
        var player = __args.OfType<Player>().FirstOrDefault();
        var cards = __args.OfType<CardPile>().FirstOrDefault()?.Cards
                    ?? __args.OfType<IReadOnlyList<CardModel>>().FirstOrDefault()
                    ?? (IEnumerable<CardModel>)player!.PlayerCombatState.Hand.Cards;
        var filter = __args.OfType<Func<CardModel, bool>>().FirstOrDefault();
        var options = cards.Where(c => filter == null || filter(c)).ToList();
        if (m.Name == "FromHandForUpgrade") options = options.Where(c => c.IsUpgradable).ToList();
        var single = m.ReturnType == typeof(Task<CardModel>);
        int min = 1, max = 1;
        if (__args.FirstOrDefault(a => a is CardSelectorPrefs) is CardSelectorPrefs prefs) { min = prefs.MinSelect; max = prefs.MaxSelect; }
        if (m.Name == "FromChooseACardScreen" && __args.OfType<bool>().FirstOrDefault()) min = 0;
        max = Math.Min(max, options.Count);
        min = Math.Min(min, max);
        if (single)
        {
            var tcs = new TaskCompletionSource<CardModel>();
            __result = tcs.Task;
            if (options.Count == 0) tcs.SetResult(null);
            else if (options.Count == 1 && min >= 1) tcs.SetResult(options[0]);       // a forced pick needs no decision
            else Current = new Pending { Options = options, Min = min, Max = 1, Single = true, Tcs = tcs, Kind = m.Name };
        }
        else
        {
            var tcs = new TaskCompletionSource<IEnumerable<CardModel>>();
            __result = tcs.Task;
            if (options.Count <= min) tcs.SetResult(options);                          // forced: every option is taken
            else Current = new Pending { Options = options, Min = min, Max = max, Tcs = tcs, Kind = m.Name };
        }
        return false;
    }

    public static void Answer(IReadOnlyList<int> picks)
    {
        var p = Current ?? throw new InvalidOperationException("no choice is pending");
        if (picks.Count < p.Min || picks.Count > p.Max || picks.Distinct().Count() != picks.Count || picks.Any(i => i < 0 || i >= p.Options.Count))
            throw new ArgumentException($"choose between {p.Min} and {p.Max} of {p.Options.Count} options");
        var chosen = picks.Select(i => p.Options[i]).ToList();
        Current = null;
        if (p.Single) ((TaskCompletionSource<CardModel>)p.Tcs).SetResult(chosen.FirstOrDefault());
        else ((TaskCompletionSource<IEnumerable<CardModel>>)p.Tcs).SetResult(chosen);
    }
}
